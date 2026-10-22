#!/usr/bin/env python
"""Descriptive summary of the CD276 RSEM expression distribution and the
quartile strata used in the survival models."""
import os
import pandas as pd

BASE = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/clinical-trialist")
co = pd.read_csv(os.path.join(BASE, "data/processed/tcga_luad_cd276_analysis_cohort.csv"))
TAB = os.path.join(BASE, "results/tables")

rows = []
v = co["value"]
rows.append(dict(statistic="n_patients_with_CD276_mRNA", value=len(v)))
for name, val in [("mean_RSEM", v.mean()), ("sd_RSEM", v.std()), ("min_RSEM", v.min()),
                  ("q25_RSEM", v.quantile(0.25)), ("median_RSEM", v.median()),
                  ("q75_RSEM", v.quantile(0.75)), ("max_RSEM", v.max()),
                  ("log2_mean", v.apply(lambda x: x).pipe(lambda s: __import__("numpy").log2(s)).mean())]:
    rows.append(dict(statistic=name, value=float(val)))
for q in ["Q1", "Q2", "Q3", "Q4"]:
    s = co[co.expression_quartile == q]
    rows.append(dict(statistic=f"{q}_n", value=int(len(s))))
    rows.append(dict(statistic=f"{q}_RSEM_min", value=float(s.value.min())))
    rows.append(dict(statistic=f"{q}_RSEM_max", value=float(s.value.max())))
    rows.append(dict(statistic=f"{q}_RSEM_median", value=float(s.value.median())))

out = os.path.join(TAB, "tcga_luad_cd276_expression_summary.csv")
pd.DataFrame(rows).to_csv(out, index=False)
print(pd.DataFrame(rows).to_string(index=False))
print("wrote", out)
