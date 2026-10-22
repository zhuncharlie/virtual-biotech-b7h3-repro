#!/usr/bin/env python
"""
Build the citable top-differential-pair tables and a composition summary of
the differential calls.

Outputs
  results/tables/liana_top_differential_pairs.csv
  results/tables/liana_differential_composition.csv
"""
import os
import numpy as np
import pandas as pd

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
WORK = os.path.join(ROOT, "work/single-cell-analyst")
TAB = os.path.join(WORK, "results/tables")
KEY = ["target", "ligand_complex", "receptor_complex"]

TOPN_HIGH, TOPN_LOW = 20, 10


def main():
    tops, comp = [], []
    for short in ["SCLC", "LUAD"]:
        d = pd.read_csv(os.path.join(TAB, f"liana_pair_level_comparison_{short.lower()}.csv"))
        s = pd.read_csv(os.path.join(TAB, f"liana_pair_level_comparison_{short.lower()}_sens_a.csv"))
        s = s[KEY + ["differential_call"]].rename(columns={"differential_call": "call_sens_a"})
        d = d.merge(s, on=KEY, how="left")
        d["low_side_absent"] = d["specificity_rank_low"].isna()
        d["high_side_absent"] = d["specificity_rank_high"].isna()

        for direction, n in (("enriched_high", TOPN_HIGH), ("enriched_low", TOPN_LOW)):
            sub = d[d.differential_call == direction]
            if direction == "enriched_high":
                sub = sub.sort_values("delta_specificity_rank", ascending=False)
            else:
                sub = sub.sort_values("delta_specificity_rank", ascending=True)
            sub = sub.head(n).copy()
            sub["rank_within_direction"] = range(1, len(sub) + 1)
            sub["direction"] = direction
            sub["disease"] = short
            tops.append(sub)

            allsub = d[d.differential_call == direction]
            comp.append(dict(
                disease=short, direction=direction, n_calls=len(allsub),
                n_low_side_absent=int(allsub.specificity_rank_low.isna().sum()),
                n_high_side_absent=int(allsub.specificity_rank_high.isna().sum()),
                pct_low_side_absent=round(100 * allsub.specificity_rank_low.isna().mean(), 2),
                median_delta_specificity_rank=round(float(allsub.delta_specificity_rank.median()), 4),
                median_abs_log2_lr_means=round(float(allsub.log2_lr_means_high_over_low.abs().median()), 4),
                q90_abs_log2_lr_means=round(float(allsub.log2_lr_means_high_over_low.abs().quantile(0.9)), 4),
                n_nominal_sens_a_concordant=int((allsub.call_sens_a == direction).sum()),
                pct_sens_a_concordant=round(100 * (allsub.call_sens_a == direction).mean(), 2),
            ))

    top = pd.concat(tops, ignore_index=True)
    cols = ["disease", "direction", "rank_within_direction", "target",
            "ligand_complex", "receptor_complex", "delta_specificity_rank",
            "specificity_rank_high", "specificity_rank_low",
            "cellphone_pvals_high", "cellphone_pvals_low",
            "lr_means_high", "lr_means_low", "log2_lr_means_high_over_low",
            "low_side_absent", "high_side_absent", "call_sens_a"]
    top[cols].to_csv(os.path.join(TAB, "liana_top_differential_pairs.csv"), index=False)

    comp_df = pd.DataFrame(comp)
    comp_df.to_csv(os.path.join(TAB, "liana_differential_composition.csv"), index=False)
    print(comp_df.to_string(index=False))
    print("\nTop 5 enriched_high per disease:")
    print(top[(top.direction == "enriched_high") & (top.rank_within_direction <= 5)]
          [["disease", "target", "ligand_complex", "receptor_complex", "delta_specificity_rank",
            "lr_means_high", "lr_means_low", "log2_lr_means_high_over_low", "low_side_absent"]]
          .to_string(index=False))


if __name__ == "__main__":
    main()
