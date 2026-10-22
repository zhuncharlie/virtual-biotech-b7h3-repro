"""Recount lung-line histology buckets from the saved Tahoe lung context table.

Read-only audit of results/tables/tahoe_lung_cell_lines_cd276_context.csv.
Writes a small recount table so the report's prose can cite a checked number.
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]
SRC = BASE / "results" / "tables" / "tahoe_lung_cell_lines_cd276_context.csv"
OUT = BASE / "results" / "tables" / "tahoe_lung_histology_recount.csv"

df = pd.read_csv(SRC)
print("columns:", df.columns.tolist())
print("rows:", len(df))

# Prefer an explicit histology column; fall back to the round-1 group column.
cand = [c for c in df.columns if c.lower() in
        ("histology", "depmap_group", "group", "histology_group", "disease")]
print("candidate columns:", cand)
col = cand[0]
print("\n-- all rows --")
print(df[col].value_counts(dropna=False).to_string())

# The prose quotes buckets for the 22 lines matched to Round-1 DepMap.
matched = df[df["matched_round1_depmap"].astype(str).str.lower().isin(
    ("true", "1", "yes"))]
print(f"\n-- matched to Round-1 DepMap: {len(matched)} of {len(df)} --")
print(matched[col].value_counts(dropna=False).to_string())

counts = (matched[col].value_counts().rename_axis(col).reset_index(name="n_lines"))
counts.insert(0, "scope", "matched_round1_depmap")
counts.to_csv(OUT, index=False)
print("\nwrote", OUT)
for grp in counts[col]:
    names = matched.loc[matched[col] == grp, "cell_name"].tolist()
    print(f"{grp} (n={len(names)}): {', '.join(names)}")
print("\nNaN histology rows (unmatched lung lines):")
print(df.loc[df[col].isna(), ["cell_name", "matched_round1_depmap"]].to_string(index=False))
