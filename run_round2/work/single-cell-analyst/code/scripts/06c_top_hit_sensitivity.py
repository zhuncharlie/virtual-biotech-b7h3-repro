#!/usr/bin/env python
"""
For each disease, list the strongest primary-definition differential pairs and
show whether the pre-specified sensitivity definition (a) reproduces the call.

Output
  results/tables/liana_top_hits_primary_vs_sens_a.csv
"""
import os
import pandas as pd

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"
WORK = os.path.join(ROOT, "work/single-cell-analyst")
TAB = os.path.join(WORK, "results/tables")
KEY = ["target", "ligand_complex", "receptor_complex"]


def main():
    frames = []
    for short in ["SCLC", "LUAD"]:
        pri = pd.read_csv(os.path.join(TAB, f"liana_pair_level_comparison_{short.lower()}.csv"))
        sen = pd.read_csv(os.path.join(TAB, f"liana_pair_level_comparison_{short.lower()}_sens_a.csv"))
        sen = sen.rename(columns={"differential_call": "call_sens_a",
                                  "delta_specificity_rank": "delta_sens_a"})
        keep_cols = KEY + ["call_sens_a", "delta_sens_a", "specificity_rank_high",
                           "specificity_rank_low", "cellphone_pvals_high", "cellphone_pvals_low",
                           "lr_means_high", "lr_means_low"]
        m = pri.merge(sen[keep_cols], on=KEY, how="left", suffixes=("", "_sens_a"))

        up = m[m.differential_call == "enriched_high"].sort_values(
            "delta_specificity_rank", ascending=False).head(15)
        dn = m[m.differential_call == "enriched_low"].sort_values(
            "delta_specificity_rank", ascending=True).head(10)
        for direction, sub in (("enriched_high", up), ("enriched_low", dn)):
            s = sub.copy()
            s["disease"] = short
            s.insert(0, "direction", direction)
            s["rank_primary_within_direction"] = range(1, len(s) + 1)
            frames.append(s)
    out = pd.concat(frames, ignore_index=True)
    cols = ["disease", "direction", "rank_primary_within_direction",
            "target", "ligand_complex", "receptor_complex",
            "delta_specificity_rank", "specificity_rank_high", "specificity_rank_low",
            "lr_means_high", "lr_means_low", "cellphone_pvals_high", "cellphone_pvals_low",
            "differential_call", "delta_sens_a", "call_sens_a"]
    out = out[cols]
    out.to_csv(os.path.join(TAB, "liana_top_hits_primary_vs_sens_a.csv"), index=False)
    print(out.to_string(index=False, max_colwidth=28))


if __name__ == "__main__":
    main()
