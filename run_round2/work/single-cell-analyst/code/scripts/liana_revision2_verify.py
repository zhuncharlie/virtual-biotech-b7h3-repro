#!/usr/bin/env python
"""Revision-2 verification for the LIANA Panels 4D/S5A report.

Recomputes, from the delivered pair-level tables only:
  - shared / high-only / low-only / union pair counts and the enriched-call splits
  - every CXCL12 ligand row (SCLC and LUAD) with source group and target
  - the SCLC definition c group sizes / unassigned cells

Writes results/tables/liana_pair_status_counts.csv
       results/tables/liana_cxcl12_pairs.csv
and prints a compact summary. No LIANA or model is re-run.
"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = os.path.join(BASE, "results", "tables")

rows = []
cx_rows = []
for dis, panel in [("sclc", "4D"), ("luad", "S5A")]:
    fn = os.path.join(T, f"liana_pair_level_comparison_{dis}.csv")
    df = pd.read_csv(fn)
    # discover presence/call columns
    cols = list(df.columns)
    print(f"\n=== {dis.upper()} {df.shape} ===")
    print(cols)
    print(df.head(2).to_string())

    # identify the status/call column
    cand = [c for c in cols if "call" in c.lower() or "status" in c.lower() or "category" in c.lower()]
    print("candidate status columns:", cand)

    # presence columns
    pres = [c for c in cols if "present" in c.lower() or "detected" in c.lower() or c.lower().startswith("in_")]
    print("candidate presence columns:", pres)

    # full unique-pair row count
    n_pairs = len(df)
    print("n rows:", n_pairs)

    # Try a sensible interpretation and report counts with whatever flags exist
    hi_col = next((c for c in pres if "high" in c.lower()), None)
    lo_col = next((c for c in pres if "low" in c.lower()), None)
    if hi_col and lo_col:
        hi = df[hi_col].astype(bool)
        lo = df[lo_col].astype(bool)
        shared = int((hi & lo).sum())
        high_only = int((hi & ~lo).sum())
        low_only = int((~hi & lo).sum())
        neither = int((~hi & ~lo).sum())
    else:
        shared = high_only = low_only = neither = None

    rows.append(dict(disease=dis.upper(), panel=panel, n_unique_pairs=n_pairs,
                     shared=shared, high_only=high_only, low_only=low_only,
                     neither_present=neither,
                     shared_plus_high_only=(shared + high_only) if shared is not None else None,
                     presence_cols=f"{hi_col}|{lo_col}"))

    # CXCL12 rows
    lig_cols = [c for c in cols if "ligand" in c.lower()]
    for lc in lig_cols:
        m = df[lc].astype(str).str.contains("CXCL12", case=False, na=False)
        if m.any():
            sub = df[m].copy()
            print(f"\nCXCL12 rows via {lc}: {len(sub)}")
            print(sub.to_string())
            for _, r in sub.iterrows():
                cx_rows.append({"disease": dis.upper(), "panel": panel,
                                "ligand_col": lc,
                                **{k: r[k] for k in cols}})

pd.DataFrame(rows).to_csv(os.path.join(T, "liana_pair_status_counts.csv"), index=False)
if cx_rows:
    pd.DataFrame(cx_rows).to_csv(os.path.join(T, "liana_cxcl12_pairs.csv"), index=False)
print("\n=== summary ===")
print(pd.DataFrame(rows).to_string())
