"""Build donor-balanced batch definitions for the 1e6a6ef9 LUAD cohort.

Splits the 54 donors into two groups of near-equal cell count so each Census
query stays well under the 2.5 GB cap. Writes batch definitions to CSV.
"""
import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]
meta = pd.read_parquet(BASE / "data/raw/metadata/meta_1e6a6ef9_luad10x_primary.parquet")
meta["donor_id"] = meta["donor_id"].astype(str)
meta["disease"] = meta["disease"].astype(str)

counts = meta.groupby("donor_id").size().sort_values(ascending=False)
print("donors:", len(counts), "cells:", int(counts.sum()))

# Greedy balancing: assign each donor (largest first) to the lighter batch.
batch_cells = {"b2": 0, "b3": 0}
assign = {"b2": [], "b3": []}
for donor, n in counts.items():
    key = min(batch_cells, key=batch_cells.get)
    assign[key].append(donor)
    batch_cells[key] += int(n)

rows = []
for key in ("b2", "b3"):
    donors = sorted(assign[key])
    in_clause = ", ".join("'%s'" % d for d in donors)
    vf = (
        "dataset_id == '1e6a6ef9-7ec9-4c90-bbfb-2ad3c3165fd1' and tissue == 'lung' "
        "and is_primary_data == True and disease == 'lung adenocarcinoma' "
        "and assay in ['10x 3\\' v2', '10x 3\\' v3', '10x 3\\' transcription profiling', "
        "'10x 5\\' v1', '10x 3\\' v1', '10x 5\\' v2', '10x 5\\' transcription profiling'] "
        "and donor_id in [%s]" % in_clause
    )
    rows.append({"batch_id": key, "n_donors": len(donors),
                 "n_cells_expected": batch_cells[key], "value_filter": vf,
                 "output": "batch02_1e6a6ef9_luad.h5ad" if key == "b2" else "batch03_1e6a6ef9_luad.h5ad"})

out = pd.DataFrame(rows)
out.to_csv(BASE / "data/raw/metadata/luad_batch_definitions.csv", index=False)
for r in rows:
    print(r["batch_id"], r["n_donors"], r["n_cells_expected"])
print("\nFilters written to data/raw/metadata/luad_batch_definitions.csv")
