#!/usr/bin/env python
"""
Sensitivity LIANA run for pre-specified CAF definition (a):
  CAF_B7H3_high := fibroblast with CD276 raw count > median of CD276-positive
                   fibroblasts (SCLC >1.5 -> >1 count; LUAD >1.0 -> >1 count)
  CAF_B7H3_low  := every other fibroblast (including CD276 == 0 and == 1)

This is definition `sens_a_median_positive` in
results/tables/liana_b7h3_caf_definition.csv.  Definitions b and c are
identical to the primary definition for LUAD (Q75 == 0) and to sens_a for
SCLC, so sens_a is the only informative alternative in both diseases.

All LIANA parameters are identical to the main run:
  consensus resource, expr_prop=0.1, min_cells=5, rank_aggregate/RRA,
  n_perms=1000, seed=1337, 32 jobs.
Cell universe is identical to the main run:
  SCLC: all 29,178 disease cells
  LUAD: all 7,022 disease fibroblasts + fixed-seed (42) sample of max 1,500
        non-fibroblast cells per cell type (25,162 cells)
No universe h5ad is written (disk quota); the universe cell counts are logged
and checked against the main run.

Outputs
  results/tables/liana_raw_sclc_sens_a.parquet
  results/tables/liana_raw_luad_sens_a.parquet
  logs/liana_sensitivity_<disease>.log (stdout redirect)
"""
import os
import sys
import json
import time
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
TAB = os.path.join(WORK, "results/tables")

DISEASE = {"SCLC": "small cell lung carcinoma", "LUAD": "lung adenocarcinoma"}
CHECK_UNIVERSE = {"SCLC": 29178, "LUAD": 25162}
CHECK_FIB = {"SCLC": 244, "LUAD": 7022}
CHECK_HIGH = {"SCLC": 43, "LUAD": 551}
CHECK_LOW = {"SCLC": 201, "LUAD": 6471}


def build_universe(short):
    A = ad.read_h5ad(H5AD, backed="r")
    obs = A.obs
    d_idx = np.where((obs["disease"] == DISEASE[short]).values)[0]
    sub = obs.iloc[d_idx]
    is_fib = (sub["cell_type"] == "fibroblast").values
    fib_pos = np.where(is_fib)[0]
    nonfib_pos = np.where(~is_fib)[0]

    if short == "SCLC":
        keep_nonfib = nonfib_pos
    else:
        rng = np.random.default_rng(42)
        chunks = []
        for ct in sorted(sub["cell_type"].astype(str).unique()):
            if ct == "fibroblast":
                continue
            pos = nonfib_pos[(sub["cell_type"].values[nonfib_pos] == ct)]
            if len(pos) > 1500:
                pos = rng.choice(pos, size=1500, replace=False)
            chunks.append(np.asarray(pos))
        keep_nonfib = np.concatenate(chunks)
    keep_local = np.sort(np.concatenate([fib_pos, keep_nonfib]))
    keep_global = d_idx[keep_local]
    D = A[keep_global, :].to_memory()
    D.obs["cell_type"] = D.obs["cell_type"].astype(str)
    return D


def main(short):
    t0 = time.time()
    print(f"[{short}] building universe", flush=True)
    D = build_universe(short)
    fib = (D.obs["cell_type"] == "fibroblast").values
    cd276 = np.zeros(D.n_obs, dtype=np.int64)
    if fib.sum() > 0:
        c = D[fib, ["CD276"]].layers["counts"]
        c = np.asarray(c.todense()).ravel() if sp.issparse(c) else np.asarray(c).ravel()
        cd276[fib] = c.astype(np.int64)

    grp = D.obs["cell_type"].values.copy()
    grp[fib & (cd276 > 1)] = "CAF_B7H3_high"
    grp[fib & (cd276 <= 1)] = "CAF_B7H3_low"
    D.obs["liana_group"] = pd.Categorical(grp)

    n_high = int((fib & (cd276 > 1)).sum())
    n_low = int((fib & (cd276 <= 1)).sum())
    n_fib = int(fib.sum())
    print(f"[{short}] universe={D.n_obs} fibroblasts={n_fib} sens_a high={n_high} low={n_low}", flush=True)
    assert D.n_obs == CHECK_UNIVERSE[short], f"universe {D.n_obs} != {CHECK_UNIVERSE[short]}"
    assert n_fib == CHECK_FIB[short], f"fib {n_fib} != {CHECK_FIB[short]}"
    assert n_high == CHECK_HIGH[short], f"high {n_high} != {CHECK_HIGH[short]}"
    assert n_low == CHECK_LOW[short], f"low {n_low} != {CHECK_LOW[short]}"

    print(f"[{short}] LIANA rank_aggregate n_perms=1000", flush=True)
    t_l = time.time()
    liana.mt.rank_aggregate(
        D, groupby="liana_group", resource_name="consensus", expr_prop=0.1,
        min_cells=5, aggregate_method="rra", n_perms=1000, seed=1337,
        use_raw=False, layer=None, n_jobs=32, verbose=True, inplace=True,
    )
    res = D.uns["liana_res"].copy()
    out = os.path.join(TAB, f"liana_raw_{short.lower()}_sens_a.parquet")
    res.to_parquet(out, index=False)
    meta = dict(
        disease=short, definition="sens_a_median_positive", n_perms=1000, seed=1337,
        n_cells_universe=int(D.n_obs), n_fibroblasts=n_fib,
        n_caf_high=n_high, n_caf_low=n_low, n_donors_high=int(
            D.obs.loc[grp == "CAF_B7H3_high", "donor_id"].nunique()),
        n_donors_low=int(D.obs.loc[grp == "CAF_B7H3_low", "donor_id"].nunique()),
        n_interactions_raw=int(len(res)),
        n_lr_pairs=int(res[["ligand_complex", "receptor_complex"]].drop_duplicates().shape[0]),
        liana_wall_time_min=round((time.time() - t_l) / 60, 2),
        finished_utc=datetime.now(timezone.utc).isoformat(), output=out,
    )
    with open(os.path.join(TAB, f"liana_sensitivity_{short.lower()}_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2), flush=True)


if __name__ == "__main__":
    for short in sys.argv[1:] or ["SCLC", "LUAD"]:
        try:
            main(short)
        except Exception:
            traceback.print_exc()
            sys.exit(1)
