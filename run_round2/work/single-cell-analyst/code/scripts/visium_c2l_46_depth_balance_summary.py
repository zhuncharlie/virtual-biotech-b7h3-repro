"""Revision 2.1 (review N2 + N5): recompute-and-store the depth-balance numbers.

No model is re-run. Inputs are two delivered tables:
  * results/tables/visium_c2l_cd276_stratification_audit.csv  (per-section)
  * results/tables/visium_c2l_spot_abundances.parquet         (per-spot)

Output:
  * results/tables/visium_c2l_depth_balance_summary.csv

Aggregation definitions (all unweighted across sections unless stated):
  median_total_counts_group
      np.median over the sections of one histology of the per-section
      `median_total_counts_high` (or `_low`) column. This is a MEDIAN OF
      PER-SECTION MEDIANS, one value per section, NOT a pooled spot-level
      median and NOT a mean of the per-section medians.
  mean_total_counts_group
      np.mean over the sections of one histology of `mean_total_counts_high`
      (or `_low`). This is a MEAN OF PER-SECTION MEANS.
  all_spot_pooled_median
      np.median(total_counts) over all spots of a histology pooled across
      sections (spot-weighted, sections with more spots contribute more).
  all_spot_section_median_of_medians
      per-section np.median(total_counts), then np.median over sections
      (section-weighted, every section contributes one value).

The Revision 2 values quoted in prose were the MEAN of the per-section
medians (7,337.3 / 3,676.5 and 2,325.8 / 1,945.25), mislabelled as medians.
The true medians of those same columns are 7,545.0 / 3,708.5 and
2,388.0 / 2,083.75.
"""
import os
import sys

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TAB = os.path.join(BASE, "results", "tables")
AUDIT = os.path.join(TAB, "visium_c2l_cd276_stratification_audit.csv")
SPOTS = os.path.join(TAB, "visium_c2l_spot_abundances.parquet")
OUT = os.path.join(TAB, "visium_c2l_depth_balance_summary.csv")

audit = pd.read_csv(AUDIT)
spots = pd.read_parquet(SPOTS, columns=["section", "histology", "total_counts"])

rows = []
for hist in ["tumor", "adjacent-normal"]:
    a = audit[audit["histology"] == hist].copy()
    s = spots[spots["histology"] == hist].copy()
    n_sections = int(a["section"].nunique())
    n_spots = int(a["n_spots"].sum())
    assert n_spots == len(s), (hist, n_spots, len(s))

    hi = float(np.median(a["median_total_counts_high"].values))
    lo = float(np.median(a["median_total_counts_low"].values))
    rows.append(dict(
        histology=hist, metric="median_total_counts_group", group="CD276_high",
        value=hi, n_sections=n_sections, n_spots=n_spots,
        ratio_high_to_low=hi / lo,
        aggregation_definition=("median over the "
                               f"{n_sections} {hist} sections of the per-section "
                               "median_total_counts_high column (one value per "
                               "section; unweighted, not pooled)")))
    rows.append(dict(
        histology=hist, metric="median_total_counts_group", group="CD276_low",
        value=lo, n_sections=n_sections, n_spots=n_spots,
        ratio_high_to_low=np.nan,
        aggregation_definition=("median over the "
                               f"{n_sections} {hist} sections of the per-section "
                               "median_total_counts_low column (one value per "
                               "section; unweighted, not pooled)")))

    mhi = float(a["mean_total_counts_high"].mean())
    mlo = float(a["mean_total_counts_low"].mean())
    rows.append(dict(
        histology=hist, metric="mean_total_counts_group", group="CD276_high",
        value=mhi, n_sections=n_sections, n_spots=n_spots,
        ratio_high_to_low=mhi / mlo,
        aggregation_definition=("mean over the "
                               f"{n_sections} {hist} sections of the per-section "
                               "mean_total_counts_high column (mean of section "
                               "means; unweighted)")))
    rows.append(dict(
        histology=hist, metric="mean_total_counts_group", group="CD276_low",
        value=mlo, n_sections=n_sections, n_spots=n_spots,
        ratio_high_to_low=np.nan,
        aggregation_definition=("mean over the "
                               f"{n_sections} {hist} sections of the per-section "
                               "mean_total_counts_low column (mean of section "
                               "means; unweighted)")))

    pooled = float(np.median(s["total_counts"].values))
    rows.append(dict(
        histology=hist, metric="all_spot_pooled_median", group="all_spots",
        value=pooled, n_sections=n_sections, n_spots=n_spots,
        ratio_high_to_low=np.nan,
        aggregation_definition=("median total_counts over all "
                               f"{n_spots:,} {hist} spots pooled across sections "
                               "(spot-weighted; sections with more spots "
                               "contribute proportionally)")))

    per_section = s.groupby("section", observed=True)["total_counts"].median()
    assert per_section.notna().all()
    mom = float(np.median(per_section.values))
    rows.append(dict(
        histology=hist, metric="all_spot_section_median_of_medians",
        group="all_spots", value=mom, n_sections=n_sections, n_spots=n_spots,
        ratio_high_to_low=np.nan,
        aggregation_definition=("per-section median total_counts, then median "
                               f"over the {n_sections} {hist} sections "
                               "(section-weighted; each section contributes one "
                               "value regardless of spot count)")))

out = pd.DataFrame(rows, columns=[
    "histology", "metric", "group", "value", "n_sections", "n_spots",
    "ratio_high_to_low", "aggregation_definition"])
out.to_csv(OUT, index=False)

print(f"wrote {OUT}: {len(out)} rows")
for metric in out["metric"].unique():
    sub = out[out["metric"] == metric]
    print(metric)
    for _, r in sub.iterrows():
        extra = "" if np.isnan(r["ratio_high_to_low"]) else f" ratio={r['ratio_high_to_low']:.4f}"
        print(f"  {r['histology']:16s} {r['group']:12s} {r['value']:12.4f}{extra}")
