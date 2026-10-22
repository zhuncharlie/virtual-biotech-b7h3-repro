"""
Multiple-testing correction for the spatial-neighbourhood endpoints.

The primary neighbourhood analysis (script 30) and the post-hoc composition
endpoints (scripts 31/32) report raw within-section label-shuffle permutation
p-values. No multiplicity correction was applied originally. This script adds
Benjamini-Hochberg FDR columns IN PLACE (same filenames, added columns) and
writes a small summary table.

Families
--------
* visium_neighborhood_robustness.csv: one BH pass per (histology, metric) over
  the 12 cell types; plus one global pass over all 48 primary rows.
* visium_neighborhood_composition_pp_difference.csv: one BH pass per
  (histology, variant, statistic) -- 14 tests for composition_pp, 1 for
  total_abundance_pct.
* visium_neighborhood_composition_sensitivity.csv: one BH pass per
  (histology, variant, endpoint) -- 14 tests for relative_composition,
  1 for total_abundance.

Caveat that no correction can fix: the permutation null shuffles high/low
labels WITHIN a section, destroying spatial autocorrelation, so the p-values
are anticonservative and the 1,000-permutation floor is p = 0.000999.

Output
------
the three tables above (extra columns) +
results/tables/visium_neighborhood_multiple_testing_summary.csv
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run, checked_frame  # noqa: E402

TAB = f"{WORK}/results/tables"
N_PERM = 1000  # permutation floor for every table here is 1/(N_PERM+1)


def bh_fdr(pvals):
    """Benjamini-Hochberg q-values; NaNs are ignored but preserved."""
    p = np.asarray(pvals, dtype=float)
    ok = np.isfinite(p)
    q = np.full_like(p, np.nan)
    n = int(ok.sum())
    if n == 0:
        return q
    idx = np.where(ok)[0]
    order = idx[np.argsort(p[idx], kind="stable")]
    ranked = p[order]
    qvals = ranked * n / np.arange(1, n + 1)
    qvals = np.minimum.accumulate(qvals[::-1])[::-1]
    q[order] = np.clip(qvals, 0, 1)
    return q


def add_bh(df, family_cols, p_col="permutation_p", out_col="permutation_p_bh",
           family_name_col="bh_family"):
    df = df.copy()
    df[family_name_col] = df[family_cols].astype(str).agg("|".join, axis=1)
    df[out_col] = np.nan
    for fam, g in df.groupby(family_name_col, sort=False):
        df.loc[g.index, out_col] = bh_fdr(g[p_col].to_numpy(float))
    return df


summary = []

# ---------------------------------------------------------------- robustness
f = f"{TAB}/visium_neighborhood_robustness.csv"
r = pd.read_csv(f)
assert len(r) == 48, f"expected 48 primary robustness rows, got {len(r)}"
r = add_bh(r, ["histology", "metric"])
# global sensitivity pass across all 48
r["permutation_p_bh_global48"] = bh_fdr(r["permutation_p"].to_numpy(float))
assert r["permutation_p_bh"].notna().all()
assert r.shape[1] == 21, r.shape
r.to_csv(f, index=False)
for fam, g in r.groupby("bh_family"):
    summary.append({
        "table": "visium_neighborhood_robustness.csv", "family": fam,
        "n_tests": len(g),
        "n_p_at_floor": int((g["permutation_p"] <= 1 / (N_PERM + 1) + 1e-12).sum()),
        "n_bh_q_lt_0.05": int((g["permutation_p_bh"] < 0.05).sum()),
        "min_raw_p": float(g["permutation_p"].min()),
        "min_bh_q": float(g["permutation_p_bh"].min()),
    })

# --------------------------------------------------------- composition pp
f = f"{TAB}/visium_neighborhood_composition_pp_difference.csv"
c = pd.read_csv(f)
assert len(c) == 2 * 2 * 15, f"expected 60 pp rows (14 types + total x 4), got {len(c)}"
c = add_bh(c, ["histology", "variant", "statistic"])
assert c["permutation_p_bh"].notna().all()
assert c.shape[1] == 15, c.shape
c.to_csv(f, index=False)
for fam, g in c.groupby("bh_family"):
    summary.append({
        "table": "visium_neighborhood_composition_pp_difference.csv",
        "family": fam, "n_tests": len(g),
        "n_p_at_floor": int((g["permutation_p"] <= 1 / (N_PERM + 1) + 1e-12).sum()),
        "n_bh_q_lt_0.05": int((g["permutation_p_bh"] < 0.05).sum()),
        "min_raw_p": float(g["permutation_p"].min()),
        "min_bh_q": float(g["permutation_p_bh"].min()),
    })

# -------------------------------------------------- composition percent change
f = f"{TAB}/visium_neighborhood_composition_sensitivity.csv"
s = pd.read_csv(f)
assert len(s) == 2 * 2 * 15, f"expected 60 sensitivity rows, got {len(s)}"
s = add_bh(s, ["histology", "variant", "endpoint"])
assert s["permutation_p_bh"].notna().all()
assert s.shape[1] == 14, s.shape
s.to_csv(f, index=False)
for fam, g in s.groupby("bh_family"):
    summary.append({
        "table": "visium_neighborhood_composition_sensitivity.csv",
        "family": fam, "n_tests": len(g),
        "n_p_at_floor": int((g["permutation_p"] <= 1 / (N_PERM + 1) + 1e-12).sum()),
        "n_bh_q_lt_0.05": int((g["permutation_p_bh"] < 0.05).sum()),
        "min_raw_p": float(g["permutation_p"].min()),
        "min_bh_q": float(g["permutation_p_bh"].min()),
    })

SUM_COLS = ["table", "family", "n_tests", "n_p_at_floor", "n_bh_q_lt_0.05",
            "min_raw_p", "min_bh_q"]
out = checked_frame(summary, SUM_COLS,
                    "visium_neighborhood_multiple_testing_summary")
out.to_csv(f"{TAB}/visium_neighborhood_multiple_testing_summary.csv", index=False)
print(out.to_string(index=False), flush=True)

log_run(step="neighborhood_multiple_testing", status="ok",
        detail=(f"BH-FDR added to robustness (48 rows; family=histology x metric), "
                f"composition pp and relative-composition tables (family="
                f"histology x variant x endpoint); {len(out)} families; "
                f"raw permutation p floor = 0.000999"))

# ---------------------------------------------------------- report-side checks
prim = r[r.metric == "mean"]
print("\nTumour mean-block raw p and BH q:", flush=True)
print(prim[prim.histology == "tumor"][
    ["cell_type", "pooled_pct_change", "permutation_p", "permutation_p_bh"]
].round(4).to_string(index=False), flush=True)
print("\nTumour all-spot composition pp raw p and BH q:", flush=True)
print(c[(c.histology == "tumor") & (c.variant == "all_spots")
        & (c.statistic == "composition_pp")][
    ["cell_type", "estimate", "permutation_p", "permutation_p_bh"]
].round(4).to_string(index=False), flush=True)
print("DONE", flush=True)
