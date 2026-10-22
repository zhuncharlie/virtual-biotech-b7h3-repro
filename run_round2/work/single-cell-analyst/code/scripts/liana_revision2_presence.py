#!/usr/bin/env python
"""Presence / CXCL12 audit for the LIANA revision-2 report.

Presence is inferred from the pair-level table: a side is present when its
lr_means is non-null. This mirrors how the pair table was built (union of the
high-source and low-source interaction tables).

Writes:
  results/tables/liana_pair_status_counts.csv   (shared/high-only/low-only/union)
  results/tables/liana_cxcl12_pairs.csv         (all CXCL12 rows, both diseases)
"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = os.path.join(BASE, "results", "tables")

rows = []
allcx = []
for dis, panel in [("sclc", "4D"), ("luad", "S5A")]:
    df = pd.read_csv(os.path.join(T, f"liana_pair_level_comparison_{dis}.csv"))
    hi = df["lr_means_high"].notna()
    lo = df["lr_means_low"].notna()
    n = len(df)
    shared = int((hi & lo).sum())
    high_only = int((hi & ~lo).sum())
    low_only = int((~hi & lo).sum())
    neither = int((~hi & ~lo).sum())
    row = dict(disease=dis.upper(), panel=panel, n_unique_pairs=n,
               shared=shared, high_only=high_only, low_only=low_only,
               neither_row=neither,
               shared_plus_high_only=shared + high_only,
               reconciled_sum=shared + high_only + low_only + neither)
    rows.append(row)
    print(f"{dis.upper()}: union={n} shared={shared} high_only={high_only} "
          f"low_only={low_only} neither={neither} SUM={shared+high_only+low_only+neither}")

    # enriched-call splits
    for call in ["enriched_high", "enriched_low", "both_pass", "neither"]:
        sub = df[df["differential_call"] == call]
        print(f"  {call}: {len(sub)} (high_only={int((sub['lr_means_high'].notna() & sub['lr_means_low'].isna()).sum())}, "
              f"low_only={int((sub['lr_means_high'].isna() & sub['lr_means_low'].notna()).sum())})")

    # CXCL12 pairs
    cx = df[df["ligand_complex"].astype(str).str.fullmatch("CXCL12", case=False)]
    print(f"  CXCL12 pairs: {len(cx)}; calls: {cx['differential_call'].value_counts().to_dict()}")
    for _, r in cx.iterrows():
        allcx.append(dict(disease=dis.upper(), panel=panel, target=r["target"],
                          ligand=r["ligand_complex"], receptor=r["receptor_complex"],
                          delta_specificity_rank=r["delta_specificity_rank"],
                          differential_call=r["differential_call"],
                          passes_high=r["passes_high"], passes_low=r["passes_low"],
                          specificity_rank_high=r["specificity_rank_high"],
                          specificity_rank_low=r["specificity_rank_low"],
                          lr_means_high=r["lr_means_high"], lr_means_low=r["lr_means_low"]))

    # all enriched_low ranked (SCLC only, for the report sentence)
    if dis == "sclc":
        low = df[df["differential_call"] == "enriched_low"].sort_values("delta_specificity_rank")
        print("  SCLC enriched_low ranked by delta:")
        print(low[["target", "ligand_complex", "receptor_complex", "delta_specificity_rank"]].to_string(index=False))

pd.DataFrame(rows).to_csv(os.path.join(T, "liana_pair_status_counts.csv"), index=False)
pd.DataFrame(allcx).to_csv(os.path.join(T, "liana_cxcl12_pairs.csv"), index=False)
print("\nWrote liana_pair_status_counts.csv and liana_cxcl12_pairs.csv")
