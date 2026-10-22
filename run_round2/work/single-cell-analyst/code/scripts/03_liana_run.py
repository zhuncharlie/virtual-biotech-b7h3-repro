#!/usr/bin/env python
"""
Run LIANA rank_aggregate for one disease (SCLC -> panel 4D, LUAD -> panel S5A).

Statistical parameters are fixed and identical for both diseases:
  resource_name='consensus', expr_prop=0.1, min_cells=5,
  aggregate_method='rra', n_perms=1000 (unless --n-perms overridden for a
  timing benchmark ONLY), seed=1337.

Cell universe:
  all fibroblast-labelled cells of that disease, split into
  CAF_B7H3_high (CD276 raw count > 0) and CAF_B7H3_low (== 0)
  + non-fibroblast cells.  If --max-per-type > 0, at most that many
  non-fibroblast cells are sampled per cell type with seed 42; if 0, every
  non-fibroblast cell of the disease is used (full disease atlas).

Groupby column `liana_group` keeps non-CAF cell types separate so that
CAF-high / CAF-low / each non-CAF cell type are distinguishable groups.
`caf_b7h3_group` (high/low/other) is retained for transparency.

Outputs
  data/processed/liana/liana_<DISEASE>_universe.h5ad   (in-memory subset actually analysed)
  results/tables/liana_raw_<disease>.parquet          (raw rank_aggregate output)
  results/tables/liana_run_log.csv                    (appended)
"""
import os
import sys
import json
import time
import argparse
import traceback
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import anndata as ad
import scipy.sparse as sp
import liana

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
SRC_ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"  # atlas input stays in SOURCE (md5 in report)
WORK = os.path.join(ROOT, "work/single-cell-analyst")
SRC_WORK = os.path.join(SRC_ROOT, "work/single-cell-analyst")
H5AD = os.path.join(SRC_WORK, "data/processed/scrna_luad_sclc_integrated.h5ad")
PROC_DIR = os.path.join(WORK, "data/processed/liana")
TAB_DIR = os.path.join(WORK, "results/tables")
LOG = os.path.join(TAB_DIR, "liana_run_log.csv")
os.makedirs(PROC_DIR, exist_ok=True)

DISEASE = {
    "SCLC": "small cell lung carcinoma",
    "LUAD": "lung adenocarcinoma",
}


def append_log(row: dict):
    df = pd.DataFrame([row])
    # a 0-byte log file (left by an interrupted run) makes read_csv raise
    # EmptyDataError, which must not be allowed to fail a completed LIANA run
    if os.path.exists(LOG) and os.path.getsize(LOG) > 0:
        old = pd.read_csv(LOG)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(LOG, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disease", required=True, choices=list(DISEASE))
    ap.add_argument("--n-perms", type=int, default=1000)
    ap.add_argument("--max-per-type", type=int, default=1500,
                    help="max non-fibroblast cells per cell type; 0 = full atlas")
    ap.add_argument("--n-jobs", type=int, default=32)
    ap.add_argument("--tag", default="main")
    a = ap.parse_args()

    short = a.disease
    disease = DISEASE[short]
    t_start = time.time()
    log_row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "panel": {"SCLC": "4D (main)", "LUAD": "S5A (supplementary)"}[short],
        "disease": short,
        "disease_label": disease,
        "run_tag": a.tag,
        "status": "started",
        "liana_version": liana.__version__,
        "resource_name": "consensus",
        "expr_prop": 0.1,
        "min_cells": 5,
        "aggregate_method": "rra",
        "n_perms": a.n_perms,
        "seed": 1337,
        "n_jobs": a.n_jobs,
        "max_non_caf_per_type": a.max_per_type,
        "cell_universe_rule": (
            "all disease fibroblasts (CAF-high + CAF-low) + every non-fibroblast cell of the disease"
            if a.max_per_type == 0 else
            f"all disease fibroblasts (CAF-high + CAF-low) + fixed-seed (42) sample of max {a.max_per_type} non-fibroblast cells per cell type"
        ),
        "is_deviation_from_full_atlas": bool(a.max_per_type != 0),
        "error": "",
        "fix": "",
    }

    try:
        print(f"[{short}] reading backed atlas", flush=True)
        A = ad.read_h5ad(H5AD, backed="r")
        obs = A.obs
        d_mask = (obs["disease"] == disease).values
        d_idx = np.where(d_mask)[0]
        print(f"[{short}] disease cells in atlas: {len(d_idx)}", flush=True)

        sub_obs = obs.iloc[d_idx].copy()
        is_fib = (sub_obs["cell_type"] == "fibroblast").values
        fib_pos = np.where(is_fib)[0]
        nonfib_pos = np.where(~is_fib)[0]

        rng = np.random.default_rng(42)
        if a.max_per_type == 0:
            keep_nonfib = nonfib_pos
        else:
            keep_chunks = []
            for ct in sorted(sub_obs["cell_type"].astype(str).unique()):
                if ct == "fibroblast":
                    continue
                pos = nonfib_pos[(sub_obs["cell_type"].values[nonfib_pos] == ct)]
                if len(pos) > a.max_per_type:
                    pos = rng.choice(pos, size=a.max_per_type, replace=False)
                keep_chunks.append(np.asarray(pos))
            keep_nonfib = np.concatenate(keep_chunks) if keep_chunks else np.array([], dtype=int)
        keep_local = np.concatenate([fib_pos, keep_nonfib])
        keep_local = np.sort(keep_local)
        keep_global = d_idx[keep_local]
        print(f"[{short}] universe cells: {len(keep_global)} "
              f"({len(fib_pos)} fibroblasts, {len(keep_nonfib)} non-fibroblast)", flush=True)

        D = A[keep_global, :].to_memory()
        D.obs["cell_type"] = D.obs["cell_type"].astype(str)

        # CD276 raw counts for fibroblasts in the universe
        fib_mask = (D.obs["cell_type"] == "fibroblast").values
        cd276 = np.zeros(D.n_obs, dtype=np.int64)
        if fib_mask.sum() > 0:
            c = D[fib_mask, ["CD276"]].layers["counts"]
            c = np.asarray(c.todense()).ravel() if sp.issparse(c) else np.asarray(c).ravel()
            cd276[fib_mask] = c.astype(np.int64)

        grp = D.obs["cell_type"].values.copy()
        caf_grp = np.array(["other"] * D.n_obs, dtype=object)
        grp[fib_mask & (cd276 > 0)] = "CAF_B7H3_high"
        grp[fib_mask & (cd276 == 0)] = "CAF_B7H3_low"
        caf_grp[fib_mask & (cd276 > 0)] = "CAF_B7H3_high"
        caf_grp[fib_mask & (cd276 == 0)] = "CAF_B7H3_low"
        D.obs["liana_group"] = pd.Categorical(grp)
        D.obs["caf_b7h3_group"] = pd.Categorical(caf_grp)
        D.obs["cd276_raw_counts"] = cd276

        vc = D.obs["liana_group"].value_counts()
        print(f"[{short}] group sizes:\n{vc.to_string()}", flush=True)
        log_row["n_cells_universe"] = int(D.n_obs)
        log_row["n_caf_high"] = int((caf_grp == "CAF_B7H3_high").sum())
        log_row["n_caf_low"] = int((caf_grp == "CAF_B7H3_low").sum())
        log_row["n_non_caf"] = int((caf_grp == "other").sum())
        log_row["n_groups"] = int(D.obs["liana_group"].nunique())
        log_row["group_sizes_json"] = json.dumps({str(k): int(v) for k, v in vc.items()})
        log_row["n_genes_input"] = int(D.n_vars)
        log_row["n_donors_caf_high"] = int(D.obs.loc[caf_grp == "CAF_B7H3_high", "donor_id"].nunique())
        log_row["n_donors_caf_low"] = int(D.obs.loc[caf_grp == "CAF_B7H3_low", "donor_id"].nunique())

        # persist the exact universe so the run is reproducible/auditable
        universe_path = os.path.join(PROC_DIR, f"liana_{short}_universe.h5ad")
        D.write_h5ad(universe_path)
        log_row["universe_h5ad"] = universe_path
        print(f"[{short}] wrote universe -> {universe_path}", flush=True)

        print(f"[{short}] running LIANA rank_aggregate n_perms={a.n_perms} ...", flush=True)
        t_liana = time.time()
        liana.mt.rank_aggregate(
            D,
            groupby="liana_group",
            resource_name="consensus",
            expr_prop=0.1,
            min_cells=5,
            aggregate_method="rra",
            n_perms=a.n_perms,
            seed=1337,
            use_raw=False,
            layer=None,
            n_jobs=a.n_jobs,
            verbose=True,
            inplace=True,
        )
        elapsed_liana = time.time() - t_liana
        res = D.uns["liana_res"].copy()
        print(f"[{short}] LIANA done in {elapsed_liana/60:.1f} min; rows={len(res)}", flush=True)

        out_pq = os.path.join(TAB_DIR, f"liana_raw_{short.lower()}.parquet")
        res.to_parquet(out_pq, index=False)
        log_row.update({
            "status": "success",
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "n_interactions_raw": int(len(res)),
            "liana_wall_time_min": round(elapsed_liana / 60, 2),
            "total_wall_time_min": round((time.time() - t_start) / 60, 2),
            "output": out_pq,
            "columns": ",".join(res.columns),
            "n_lr_pairs": int(res[["ligand_complex", "receptor_complex"]].drop_duplicates().shape[0]),
        })
        print(f"[{short}] wrote {out_pq}", flush=True)
    except Exception as e:
        log_row.update({
            "status": "FAILED",
            "error": f"{type(e).__name__}: {e}",
            "fix": "see logs/liana_run_" + short + ".log and traceback",
            "total_wall_time_min": round((time.time() - t_start) / 60, 2),
            "finished_utc": datetime.now(timezone.utc).isoformat(),
        })
        append_log(log_row)
        traceback.print_exc()
        sys.exit(1)

    append_log(log_row)
    print(json.dumps({k: v for k, v in log_row.items() if k != "group_sizes_json"}, indent=2, default=str))


if __name__ == "__main__":
    main()
