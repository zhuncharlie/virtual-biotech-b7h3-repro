#!/usr/bin/env python
"""myCAF / iCAF marker-score check for the LIANA CAF high-vs-low split.

The integrated atlas has NO myCAF/iCAF subtype labels (cell_type_original only
distinguishes anatomical fibroblast labels). This script therefore computes a
transparent marker-score proxy, not a subtype classification:

  myCAF score = mean log-normalised expression over
                ACTA2, TAGLN, MYL9, CNN1, CTHRC1, POSTN, MMP11, FAP
  iCAF score  = mean log-normalised expression over
                IL6, CXCL12, HAS1, PDGFRA, LIF

Reads the SCLC and LUAD LIANA universe .h5ad files in SOURCE (read-only),
using only the fibroblast rows. Writes one table:
  results/tables/liana_caf_subtype_check.csv

Cell-level Mann-Whitney p-values are descriptive only (cells are not
independent); donor-level paired tests use donors with >=10 cells in both
groups. No LIANA or model is re-run.
"""
import os
import numpy as np
import pandas as pd
import anndata as ad
from scipy.stats import mannwhitneyu, wilcoxon

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = os.path.join(BASE, "results", "tables")
SRC = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
       "20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/single-cell-analyst")

MYCAF = ["ACTA2", "TAGLN", "MYL9", "CNN1", "CTHRC1", "POSTN", "MMP11", "FAP"]
ICAF = ["IL6", "CXCL12", "HAS1", "PDGFRA", "LIF"]

rows = []
summary = []
for dis in ["SCLC", "LUAD"]:
    path = f"{SRC}/data/processed/liana/liana_{dis}_universe.h5ad"
    A = ad.read_h5ad(path, backed="r")
    obs = A.obs
    names = A.var["feature_name"].astype(str).to_numpy()
    name_to_idx = {g: i for i, g in enumerate(names)}

    fib = obs["cell_type"].astype(str).str.contains("fibro", case=False, na=False).to_numpy()
    idx = np.where(fib)[0]
    genes = MYCAF + ICAF
    missing = [g for g in genes if g not in name_to_idx]
    if missing:
        raise RuntimeError(f"{dis}: markers missing from var: {missing}")
    gidx = [name_to_idx[g] for g in genes]

    sub = A[idx, gidx].to_memory()
    X = sub.X
    if hasattr(X, "toarray"):
        X = X.toarray()
    X = np.asarray(X, dtype=float)
    meta = obs.iloc[idx].copy()
    meta["mycaf_score"] = X[:, : len(MYCAF)].mean(axis=1)
    meta["icaf_score"] = X[:, len(MYCAF):].mean(axis=1)
    meta["mycaf_pct"] = (X[:, : len(MYCAF)] > 0).mean(axis=1)
    meta["icaf_pct"] = (X[:, len(MYCAF):] > 0).mean(axis=1)
    A.file.close()

    # anatomical composition fractions per group
    anat = meta["cell_type_original"].astype(str)
    for grp in ["CAF_B7H3_high", "CAF_B7H3_low"]:
        g = meta[meta["caf_b7h3_group"] == grp]
        n = len(g)
        rows.append(dict(
            disease=dis, level="group", group=grp, donor_id="ALL",
            n_cells=n, n_donors=g["donor_id"].nunique(),
            frac_original_fibroblast=float((anat[meta["caf_b7h3_group"] == grp] == "fibroblast").mean()),
            frac_original_fibroblast_of_lung=float((anat[meta["caf_b7h3_group"] == grp] == "fibroblast of lung").mean()),
            frac_original_bronchus_fibroblast=float((anat[meta["caf_b7h3_group"] == grp] == "bronchus fibroblast of lung").mean()),
            mycaf_genes=";".join(MYCAF), icaf_genes=";".join(ICAF),
            mycaf_score_mean=g["mycaf_score"].mean(), mycaf_score_median=g["mycaf_score"].median(),
            mycaf_pct_detected=g["mycaf_pct"].mean(),
            icaf_score_mean=g["icaf_score"].mean(), icaf_score_median=g["icaf_score"].median(),
            icaf_pct_detected=g["icaf_pct"].mean(),
        ))

    hi = meta[meta["caf_b7h3_group"] == "CAF_B7H3_high"]
    lo = meta[meta["caf_b7h3_group"] == "CAF_B7H3_low"]
    p_my = mannwhitneyu(hi["mycaf_score"], lo["mycaf_score"], alternative="two-sided").pvalue
    p_ic = mannwhitneyu(hi["icaf_score"], lo["icaf_score"], alternative="two-sided").pvalue

    # donor-level paired analysis (>=10 cells in each group)
    dg = (meta.groupby(["donor_id", "caf_b7h3_group"], observed=True)[["mycaf_score", "icaf_score"]]
              .agg(["mean", "size"]).reset_index())
    dg.columns = ["donor_id", "group", "mycaf_mean", "mycaf_n", "icaf_mean", "icaf_n"]
    dg = dg[dg["mycaf_n"] > 0].copy()
    piv = dg.pivot(index="donor_id", columns="group")
    paired = piv.dropna(subset=[("mycaf_n", "CAF_B7H3_high"), ("mycaf_n", "CAF_B7H3_low")])
    paired = paired[(paired[("mycaf_n", "CAF_B7H3_high")] >= 10) &
                    (paired[("mycaf_n", "CAF_B7H3_low")] >= 10)]
    n_paired = len(paired)
    if n_paired >= 5:
        p_my_d = wilcoxon(paired[("mycaf_mean", "CAF_B7H3_high")],
                          paired[("mycaf_mean", "CAF_B7H3_low")]).pvalue
        p_ic_d = wilcoxon(paired[("icaf_mean", "CAF_B7H3_high")],
                          paired[("icaf_mean", "CAF_B7H3_low")]).pvalue
    else:
        p_my_d = p_ic_d = np.nan

    # donor-level rows
    for _, r in dg.iterrows():
        rows.append(dict(
            disease=dis, level="donor", group=r["group"], donor_id=r["donor_id"],
            n_cells=int(r["mycaf_n"]), n_donors=np.nan,
            mycaf_genes=";".join(MYCAF), icaf_genes=";".join(ICAF),
            mycaf_score_mean=r["mycaf_mean"], icaf_score_mean=r["icaf_mean"],
        ))

    summary.append(dict(disease=dis, p_mycaf_celllevel=p_my, p_icaf_celllevel=p_ic,
                        n_donors_paired_ge10=n_paired,
                        p_mycaf_donorlevel=p_my_d, p_icaf_donorlevel=p_ic_d))

out = pd.DataFrame(rows)
summ = pd.DataFrame(summary)
print("=== group-level ===")
print(out[out.level == "group"].to_string(index=False))
print("\n=== tests ===")
print(summ.to_string(index=False))
out.to_csv(os.path.join(T, "liana_caf_subtype_check.csv"), index=False)
summ.to_csv(os.path.join(T, "liana_caf_subtype_check_tests.csv"), index=False)
print("\nWrote", os.path.join(T, "liana_caf_subtype_check.csv"))
