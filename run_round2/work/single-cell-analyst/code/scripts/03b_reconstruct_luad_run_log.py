#!/usr/bin/env python
"""
Reconstruct the LUAD main-run row in results/tables/liana_run_log.csv.

The LUAD LIANA rank_aggregate run completed successfully and wrote
results/tables/liana_raw_luad.parquet (37,684 rows), but the final
append_log() call raised pandas.errors.EmptyDataError because the pre-existing
liana_run_log.csv was 0 bytes (left by an interrupted run).  The in-memory
log row was lost when the process exited.

This script rebuilds that row from the run log, the output parquet and the
pre-registered parameters.  It does NOT recompute or modify any LIANA result.
The log row is marked as reconstructed in the `fix` column.
"""
import os
import json
import pandas as pd

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
SRC_ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"  # universe .h5ad stays in SOURCE
WORK = os.path.join(ROOT, "work/single-cell-analyst")
SRC_WORK = os.path.join(SRC_ROOT, "work/single-cell-analyst")
TAB = os.path.join(WORK, "results/tables")
LOG = os.path.join(TAB, "liana_run_log.csv")
PQ = os.path.join(TAB, "liana_raw_luad.parquet")

GROUPS = {
    "CAF_B7H3_low": 5346, "CAF_B7H3_high": 1676, "B cell": 1500, "NK cell": 1500,
    "T cell": 1500, "dendritic cell": 1500, "endothelial cell": 1500,
    "epithelial cell": 1500, "macrophage": 1500, "malignant cell": 1500,
    "mast cell": 1500, "monocyte/myeloid": 1500, "stromal/other": 1500,
    "plasma cell": 1500, "neutrophil": 128, "erythrocyte": 12,
}

if __name__ == "__main__":
    res = pd.read_parquet(PQ)
    row = {
        "timestamp_utc": "2026-10-21T16:45:47+00:00",   # first line of run log (local 11:45:47 -0500)
        "panel": "S5A (supplementary)",
        "disease": "LUAD",
        "disease_label": "lung adenocarcinoma",
        "run_tag": "main",
        "status": "success",
        "liana_version": "1.7.0",
        "resource_name": "consensus",
        "expr_prop": 0.1,
        "min_cells": 5,
        "aggregate_method": "rra",
        "n_perms": 1000,
        "seed": 1337,
        "n_jobs": 32,
        "max_non_caf_per_type": 1500,
        "cell_universe_rule": ("all disease fibroblasts (CAF-high + CAF-low) + fixed-seed (42) "
                               "sample of max 1500 non-fibroblast cells per cell type"),
        "is_deviation_from_full_atlas": True,
        "error": "EmptyDataError in append_log: pre-existing liana_run_log.csv was 0 bytes",
        "fix": ("append_log now skips 0-byte log; row reconstructed from "
                "logs/liana_run_LUAD_main.log and the output parquet; LIANA run itself succeeded"),
        "n_cells_universe": 25162,
        "n_caf_high": 1676,
        "n_caf_low": 5346,
        "n_non_caf": 18140,
        "n_groups": 16,
        "group_sizes_json": json.dumps(GROUPS),
        "n_genes_input": 61497,
        "n_donors_caf_high": 47,
        "n_donors_caf_low": 58,
        "universe_h5ad": os.path.join(SRC_WORK, "data/processed/liana/liana_LUAD_universe.h5ad"),
        "finished_utc": "2026-10-21T16:47:02+00:00",
        "n_interactions_raw": int(len(res)),
        "liana_wall_time_min": 0.8,
        "total_wall_time_min": 1.2,
        "output": PQ,
        "columns": ",".join(res.columns),
        "n_lr_pairs": int(res[["ligand_complex", "receptor_complex"]].drop_duplicates().shape[0]),
    }
    df = pd.DataFrame([row])
    if os.path.exists(LOG) and os.path.getsize(LOG) > 0:
        df = pd.concat([pd.read_csv(LOG), df], ignore_index=True)
    df.to_csv(LOG, index=False)
    print(df.T.to_string())
