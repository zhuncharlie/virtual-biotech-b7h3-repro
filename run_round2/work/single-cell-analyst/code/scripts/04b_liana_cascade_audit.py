#!/usr/bin/env python
"""
Independent audit of the LIANA filter cascade for panels 4D (SCLC) and S5A (LUAD).

Recomputes every step directly from the raw rank_aggregate parquet without
calling the processing functions in 04_liana_extract_compare.py, checks that
each step is a subset of the previous one, and compares the recomputed counts
with results/tables/liana_filter_cascade.csv.

Outputs
  results/tables/liana_cascade_audit.csv
"""
import os
import pandas as pd

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
WORK = os.path.join(ROOT, "work/single-cell-analyst")
TAB = os.path.join(WORK, "results/tables")

SPEC_RANK_CUT = 0.1
PVAL_CUT = 0.01
MIN_METHODS = 3


def audit(short):
    raw = pd.read_parquet(os.path.join(TAB, f"liana_raw_{short.lower()}.parquet"))
    caf = raw[raw["source"].isin(["CAF_B7H3_high", "CAF_B7H3_low"])].copy()

    # The 5-method consensus emits five score columns; a method is "finite" if
    # at least one of its score columns is finite for that row.
    METHOD_COLS = {
        "CellPhoneDB": ["lr_means", "cellphone_pvals"],
        "Connectome": ["expr_prod", "scaled_weight"],
        "log2FC": ["lr_logfc"],
        "NATMI": ["expr_prod", "spec_weight"],
        "SingleCellSignalR": ["lrscore"],
    }
    finite = pd.DataFrame(index=caf.index)
    for m, cols in METHOD_COLS.items():
        finite[m] = caf[cols].apply(pd.to_numeric, errors="coerce").notna().any(axis=1)
    caf["n_methods_finite_rank"] = finite.sum(axis=1)

    s0 = caf
    s1 = s0[s0["specificity_rank"] <= SPEC_RANK_CUT]
    s2 = s1[s1["cellphone_pvals"] < PVAL_CUT]
    s3 = s2[s2["n_methods_finite_rank"] >= MIN_METHODS]

    # subset checks
    sub12 = s2.index.isin(s1.index).all()
    sub23 = s3.index.isin(s2.index).all()
    sub01 = s1.index.isin(s0.index).all()

    rep = pd.read_csv(os.path.join(TAB, "liana_filter_cascade.csv"))
    rep = rep[rep["disease"] == short].set_index("step")["n_interactions"]

    rows = [
        dict(disease=short, step="0_all_CAF_source", n_recomputed=len(s0),
             n_reported=int(rep.get("0_all_CAF_source", -1)),
             is_subset_of_previous=True, n_high=int((s0.source == "CAF_B7H3_high").sum()),
             n_low=int((s0.source == "CAF_B7H3_low").sum())),
        dict(disease=short, step="1_top10pct_specificity_rank", n_recomputed=len(s1),
             n_reported=int(rep.get("1_top10pct_specificity_rank", -1)),
             is_subset_of_previous=bool(sub01), n_high=int((s1.source == "CAF_B7H3_high").sum()),
             n_low=int((s1.source == "CAF_B7H3_low").sum())),
        dict(disease=short, step="2_pval_lt_0.01", n_recomputed=len(s2),
             n_reported=int(rep.get("2_pval_lt_0.01", -1)),
             is_subset_of_previous=bool(sub12), n_high=int((s2.source == "CAF_B7H3_high").sum()),
             n_low=int((s2.source == "CAF_B7H3_low").sum())),
        dict(disease=short, step="3_ge3_methods_finite", n_recomputed=len(s3),
             n_reported=int(rep.get("3_ge3_methods_finite", -1)),
             is_subset_of_previous=bool(sub23), n_high=int((s3.source == "CAF_B7H3_high").sum()),
             n_low=int((s3.source == "CAF_B7H3_low").sum())),
    ]
    out = pd.DataFrame(rows)
    out["counts_match"] = out["n_recomputed"] == out["n_reported"]
    out["n_methods_finite_always_5_in_s1"] = bool((s1["n_methods_finite_rank"] == 5).all())
    out["pval_filter_removes_zero_rows"] = len(s1) - len(s2) == 0
    return out


if __name__ == "__main__":
    frames = []
    for short in ["SCLC", "LUAD"]:
        if os.path.exists(os.path.join(TAB, f"liana_raw_{short.lower()}.parquet")):
            frames.append(audit(short))
    out = pd.concat(frames, ignore_index=True)
    out.to_csv(os.path.join(TAB, "liana_cascade_audit.csv"), index=False)
    print(out.to_string(index=False))
