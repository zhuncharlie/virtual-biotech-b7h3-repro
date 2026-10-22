#!/usr/bin/env python
"""
Compare the primary detection-based CAF split with pre-specified sensitivity
definition (a) (CD276 > median of CD276-positive cells).

Reads the pair-level comparison tables produced by 04:
  liana_pair_level_comparison_<disease>.csv
  liana_pair_level_comparison_<disease>_sens_a.csv

Outputs
  results/tables/liana_sensitivity_concordance.csv
"""
import os
import pandas as pd

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"
WORK = os.path.join(ROOT, "work/single-cell-analyst")
TAB = os.path.join(WORK, "results/tables")
KEY = ["target", "ligand_complex", "receptor_complex"]


def main():
    rows = []
    for short in ["SCLC", "LUAD"]:
        pri = pd.read_csv(os.path.join(TAB, f"liana_pair_level_comparison_{short.lower()}.csv"))
        sen = pd.read_csv(os.path.join(TAB, f"liana_pair_level_comparison_{short.lower()}_sens_a.csv"))
        for side in ["enriched_high", "enriched_low"]:
            a = set(map(tuple, pri.loc[pri.differential_call == side, KEY].values))
            b = set(map(tuple, sen.loc[sen.differential_call == side, KEY].values))
            inter = a & b
            union = a | b
            rows.append(dict(
                disease=short, direction=side,
                n_primary=len(a), n_sens_a=len(b), n_shared=len(inter),
                jaccard=round(len(inter) / len(union), 4) if union else None,
                shared_pct_of_primary=round(100 * len(inter) / len(a), 2) if a else None,
                shared_examples="; ".join(f"{l}->{r} ({t})" for t, l, r in sorted(inter)[:5]),
            ))
        # overall directional agreement among all pairs called in either run
        m = pri[KEY + ["differential_call"]].merge(
            sen[KEY + ["differential_call"]], on=KEY, how="outer", suffixes=("_primary", "_sens_a"))
        both_called = m.dropna(subset=["differential_call_primary", "differential_call_sens_a"])
        agree = (both_called["differential_call_primary"] == both_called["differential_call_sens_a"]).mean()
        rows.append(dict(disease=short, direction="all_pairs_direction_agreement",
                         n_primary=int(m["differential_call_primary"].notna().sum()),
                         n_sens_a=int(m["differential_call_sens_a"].notna().sum()),
                         n_shared=int(both_called.shape[0]),
                         jaccard=None, shared_pct_of_primary=round(100 * agree, 2),
                         shared_examples="pct of pairs called in both runs with the same call"))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(TAB, "liana_sensitivity_concordance.csv"), index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
