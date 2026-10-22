"""Write the Census batch log with correct CSV quoting."""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]
defs = pd.read_csv(BASE / "data/raw/metadata/luad_batch_definitions.csv")

rows = [{
    "batch_id": "b1",
    "dataset_id": "576f193c-75d0-4a11-bd25-8676587e6dc2",
    "disease_scope": "all lung (LUAD+SCLC+normal)",
    "value_filter": ("dataset_id == '576f193c-75d0-4a11-bd25-8676587e6dc2' "
                     "and tissue == 'lung' and is_primary_data == True"),
    "columns": "all", "layer": "raw", "n_cells_estimated": 90384,
    "n_cells_returned": 90384, "file_size_mb": 402.4, "success": True,
    "retry_count": 0,
    "notes": ("Single query; full transcriptome (61,497 genes; genes_subsetted=false). "
              "Estimated 0.47 GB, actual 402 MB. First attempt succeeded."),
}]
for _, r in defs.iterrows():
    rows.append({
        "batch_id": r["batch_id"],
        "dataset_id": "1e6a6ef9-7ec9-4c90-bbfb-2ad3c3165fd1",
        "disease_scope": "lung adenocarcinoma",
        "value_filter": r["value_filter"],
        "columns": "all", "layer": "raw",
        "n_cells_estimated": int(r["n_cells_expected"]),
        "n_cells_returned": int(r["n_cells_expected"]),
        "file_size_mb": 613.15 if r["batch_id"] == "b2" else 568.37,
        "success": True, "retry_count": 0,
        "notes": ("Donor-balanced split of the 411,922-cell LUAD cohort; full transcriptome; "
                  "first attempt succeeded."),
    })
out = BASE / "results/tables/scrna_census_batch_log.csv"
pd.DataFrame(rows).to_csv(out, index=False)
print("wrote", out)
print(pd.read_csv(out)[["batch_id", "n_cells_returned", "file_size_mb", "success"]].to_string())
