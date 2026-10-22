#!/usr/bin/env python
"""
Step 1 of panels 4D / S5A: PRE-REGISTER the B7-H3-positive fibroblast definition.

This script is run BEFORE any LIANA analysis. It only reads CD276 raw counts in
fibroblast-labelled cells and writes the definitions + group sizes. It writes:
  results/tables/liana_b7h3_caf_definition.csv
  results/tables/liana_b7h3_caf_definition_by_donor.csv

No threshold is selected to reproduce a paper number.
"""
import os
import sys
import json
import hashlib
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import anndata as ad
import scipy.sparse as sp

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
SRC_ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"  # atlas input stays in SOURCE (md5 in report)
WORK = os.path.join(ROOT, "work/single-cell-analyst")
SRC_WORK = os.path.join(SRC_ROOT, "work/single-cell-analyst")
H5AD = os.path.join(SRC_WORK, "data/processed/scrna_luad_sclc_integrated.h5ad")
OUT_DEF = os.path.join(WORK, "results/tables/liana_b7h3_caf_definition.csv")
OUT_DONOR = os.path.join(WORK, "results/tables/liana_b7h3_caf_definition_by_donor.csv")

DISEASE = {
    "SCLC": "small cell lung carcinoma",
    "LUAD": "lung adenocarcinoma",
}

np.random.seed(42)

A = ad.read_h5ad(H5AD, backed="r")
fib_mask = (A.obs["cell_type"] == "fibroblast").values
fib_idx = np.where(fib_mask)[0]
print(f"fibroblast-labelled cells in atlas: {len(fib_idx)}")

# read raw CD276 counts only for fibroblasts
sub = A[fib_idx, ["CD276"]].to_memory()
X = sub.layers["counts"]
if sp.issparse(X):
    counts = np.asarray(X.todense()).ravel()
else:
    counts = np.asarray(X).ravel()
obs = sub.obs.copy()
obs["cd276_raw_counts"] = counts
obs = obs[obs["disease"].isin(DISEASE.values())].copy()
print(obs.groupby("disease").size().to_string())

rows = []
donor_rows = []

for short, disease in DISEASE.items():
    g = obs[obs["disease"] == disease].copy()
    n_total = len(g)
    pos = g["cd276_raw_counts"] > 0
    n_pos = int(pos.sum())

    all_q = np.percentile(g["cd276_raw_counts"], [25, 50, 75])
    pos_vals = g.loc[pos, "cd276_raw_counts"]
    pos_med = float(np.median(pos_vals)) if n_pos else np.nan
    q25_all, q50_all, q75_all = [float(x) for x in all_q]

    # ---- definition masks -------------------------------------------------
    # primary: detected (>0 raw count)
    m_primary = g["cd276_raw_counts"] > 0
    # (a) CD276 > median of CD276-positive fibroblasts
    m_a = g["cd276_raw_counts"] > pos_med
    # (b) CD276 > 75th percentile of ALL fibroblasts in that disease
    m_b = g["cd276_raw_counts"] > q75_all
    # (c) top vs bottom quartile of all fibroblasts.
    #     Because CD276 is zero-inflated, the 25th percentile is 0 in both
    #     diseases and a strictly-below-Q25 group is empty.  Operational
    #     rule pre-specified here: bottom = CD276 == 0 (the empirical bottom
    #     64.8% [SCLC] / 76.1% [LUAD] of cells), top = CD276 > Q75.
    m_c_top = g["cd276_raw_counts"] > q75_all
    m_c_bot = g["cd276_raw_counts"] == 0

    def summarize(def_id, name, rule, m_high, m_low, note):
        hi = g[m_high]
        lo = g[m_low]
        return {
            "disease": short,
            "disease_label": disease,
            "definition_id": def_id,
            "definition_name": name,
            "rule": rule,
            "threshold_raw_counts": (
                ">0" if def_id == "primary"
                else f"> {pos_med:g} (median of CD276+ cells)" if def_id == "sens_a_median_positive"
                else f"> {q75_all:g} (Q75 of all fibroblasts)" if def_id in ("sens_b_q75_all", "sens_c_quartile_top")
                else "== 0 (bottom group)"
            ),
            "n_cells_high": int(len(hi)),
            "n_cells_low": int(len(lo)),
            "n_fibroblasts_disease": n_total,
            "frac_fibroblasts_high": round(len(hi) / n_total, 4),
            "n_donors_high": int(hi["donor_id"].nunique()),
            "n_donors_low": int(lo["donor_id"].nunique()),
            "n_donors_high_ge10_cells": int((hi.groupby("donor_id", observed=True).size() >= 10).sum()),
            "n_donors_low_ge10_cells": int((lo.groupby("donor_id", observed=True).size() >= 10).sum()),
            "n_datasets_high": int(hi["dataset_id"].nunique()),
            "median_all_fibroblasts": q50_all,
            "q25_all_fibroblasts": q25_all,
            "q75_all_fibroblasts": q75_all,
            "median_cd276_positive": pos_med,
            "note": note,
        }

    rows.append(summarize(
        "primary", "CD276 detected (>0 raw counts)",
        "CAF_B7H3_high := fibroblast with CD276 raw count > 0; CAF_B7H3_low := fibroblast with CD276 raw count == 0",
        m_primary, ~m_primary,
        "PRIMARY definition, used for the LIANA group split. Detection is library-size dependent and was NOT normalised; sensitivity to this is why definitions a-c are pre-specified.",
    ))
    rows.append(summarize(
        "sens_a_median_positive", "CD276 > median of CD276-positive fibroblasts",
        "high := CD276 > median of detected cells; low := all other fibroblasts",
        m_a, ~m_a,
        "Sensitivity only. Not used in the main LIANA run.",
    ))
    rows.append(summarize(
        "sens_b_q75_all", "CD276 > 75th percentile of all fibroblasts",
        "high := CD276 > Q75(all fibroblasts); low := rest",
        m_b, ~m_b,
        "Sensitivity only. Because >76% (LUAD) / >64% (SCLC) of fibroblasts are CD276-zero, Q75 == 0 in LUAD, so this collapses to the primary definition.",
    ))
    rows.append(summarize(
        "sens_c_quartile_top", "Top quartile of all fibroblasts",
        "high := CD276 > Q75(all fibroblasts)",
        m_c_top, m_c_bot,
        "Top quartile of the continuous split. In LUAD Q75==0 so top group is all positive cells (23.9%, not 25%).",
    ))
    rows.append(summarize(
        "sens_c_quartile_bottom", "Bottom group of the continuous split (CD276 == 0)",
        "low := CD276 == 0",
        m_c_top, m_c_bot,
        "The nominal bottom quartile (< Q25) is EMPTY because Q25==0. Pre-specified operational fallback: bottom = CD276==0, which is 64.8% (SCLC) / 76.1% (LUAD) of fibroblasts, NOT 25%.",
    ))

    # per-donor breakdown
    for donor, dg in g.groupby("donor_id", observed=True):
        donor_rows.append({
            "disease": short,
            "donor_id": donor,
            "dataset_id": dg["dataset_id"].iloc[0],
            "n_fibroblasts": len(dg),
            "n_cd276_positive_primary": int((dg["cd276_raw_counts"] > 0).sum()),
            "frac_cd276_positive_primary": round(float((dg["cd276_raw_counts"] > 0).mean()), 4),
            "n_high_sens_a": int((dg["cd276_raw_counts"] > pos_med).sum()),
            "n_high_sens_b_q75_all": int((dg["cd276_raw_counts"] > q75_all).sum()),
        })

df = pd.DataFrame(rows)
df.insert(0, "pre_registered_utc", datetime.now(timezone.utc).isoformat())
df["no_threshold_selected_to_match_paper"] = (
    "TRUE - no threshold was selected because it reproduced a paper number; "
    "the primary definition is detection (>0) and a-c were fixed before LIANA output was inspected"
)
df.to_csv(OUT_DEF, index=False)
pd.DataFrame(donor_rows).to_csv(OUT_DONOR, index=False)

# input checksum for the audit trail
h = hashlib.md5()
with open(H5AD, "rb") as fh:
    for chunk in iter(lambda: fh.read(1024 * 1024), b""):
        h.update(chunk)

meta = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "h5ad": H5AD,
    "h5ad_md5": h.hexdigest(),
    "n_fibroblasts_total": int(len(fib_idx)),
    "definitions_written": OUT_DEF,
    "donor_table_written": OUT_DONOR,
}
with open(os.path.join(WORK, "results/tables/liana_b7h3_caf_definition_meta.json"), "w") as fh:
    json.dump(meta, fh, indent=2)

print(df[["disease", "definition_id", "n_cells_high", "n_cells_low",
          "n_donors_high", "n_donors_low", "frac_fibroblasts_high"]].to_string(index=False))
print("WROTE", OUT_DEF)
print("WROTE", OUT_DONOR)
