"""Shared constants / helpers for the cell2location Panel 4E steps."""
import os
import csv
import time

import pandas as pd

RUN = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
WORK = f"{RUN}/work/single-cell-analyst"
LOG = f"{WORK}/results/tables/visium_c2l_run_log.csv"

LOG_COLS = ["timestamp", "step", "status", "max_epochs", "epochs_completed",
            "batch_size", "device", "n_cells_or_spots", "n_genes",
            "wall_time_s", "detail"]


def ensure_dirs():
    for d in ["code/scripts", "data/raw", "data/processed",
              "results/figures", "results/tables", "results/reports", "logs"]:
        os.makedirs(f"{WORK}/{d}", exist_ok=True)


def checked_frame(rows, expected_columns, name):
    """Build a DataFrame and fail fast on the two bug classes seen in this run.

    1. Silent all-NaN construction (e.g. pandas `columns=` used as a rename).
    2. Column misalignment (a table whose columns are not what downstream code
       indexes by name).

    Parameters
    ----------
    rows : list[dict]
        Records to construct. A DataFrame may also be passed and is validated
        in place of construction.
    expected_columns : list[str]
        Exact expected column names, in order.
    name : str
        Human-readable artifact name used in the assertion message.
    """
    cols = list(expected_columns)
    df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if list(df.columns) != cols:
        raise AssertionError(
            f"{name}: expected {len(cols)} columns {cols}, "
            f"got {len(df.columns)} {list(df.columns)}")
    if len(df) == 0:
        raise AssertionError(f"{name}: zero rows")
    if not df.notna().any().any():
        raise AssertionError(f"{name}: every value is NaN (silent export failure)")
    return df


def log_run(step, status, wall_time_s=None, detail="", max_epochs=None,
            epochs_completed=None, batch_size=None, device=None,
            n_cells=None, n_genes=None):
    """Append one row to the run log. Every failure/retry is recorded here."""
    ensure_dirs()
    exists = os.path.exists(LOG)
    with open(LOG, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_COLS)
        if not exists:
            w.writeheader()
        w.writerow({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "step": step, "status": status,
            "max_epochs": max_epochs, "epochs_completed": epochs_completed,
            "batch_size": batch_size, "device": device,
            "n_cells_or_spots": n_cells, "n_genes": n_genes,
            "wall_time_s": wall_time_s, "detail": detail,
        })
