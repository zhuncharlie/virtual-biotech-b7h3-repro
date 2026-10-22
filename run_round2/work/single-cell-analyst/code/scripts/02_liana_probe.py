#!/usr/bin/env python
"""Probe LIANA rank_aggregate output schema + timing on a small SCLC subset."""
import os, time, json
import numpy as np, pandas as pd, anndata as ad
import liana

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
SRC_ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"  # atlas input stays in SOURCE (md5 in report)
WORK = os.path.join(ROOT, "work/single-cell-analyst")
SRC_WORK = os.path.join(SRC_ROOT, "work/single-cell-analyst")
H5AD = os.path.join(SRC_WORK, "data/processed/scrna_luad_sclc_integrated.h5ad")

A = ad.read_h5ad(H5AD, backed="r")
obs = A.obs
mask = (obs["disease"] == "small cell lung carcinoma").values
idx = np.where(mask)[0]
rng = np.random.default_rng(42)
# sample: all fibroblasts + 200 per non-fibro type
fib = obs.iloc[idx][obs.iloc[idx]["cell_type"] == "fibroblast"].index
chosen = list(A.obs_names.get_indexer(fib))
for ct in obs.iloc[idx]["cell_type"].unique():
    if ct == "fibroblast":
        continue
    ii = np.where(mask & (obs["cell_type"] == ct).values)[0]
    chosen += list(rng.choice(ii, size=min(200, len(ii)), replace=False))
chosen = np.array(sorted(set(chosen)))
print("probe cells", len(chosen))
D = A[chosen, :].to_memory()
print(D.shape, type(D.X), D.X[:5, :3])

# group column
ct = D.obs["cell_type"].astype(str).values
is_fib = ct == "fibroblast"
cd276 = np.asarray(D[:, ["CD276"]].layers["counts"].todense()).ravel()
grp = ct.copy()
grp[is_fib & (cd276 > 0)] = "CAF_B7H3_high"
grp[is_fib & (cd276 == 0)] = "CAF_B7H3_low"
D.obs["liana_group"] = pd.Categorical(grp)
print(D.obs["liana_group"].value_counts().to_string())

t0 = time.time()
liana.mt.rank_aggregate(
    D, groupby="liana_group", resource_name="consensus",
    expr_prop=0.1, min_cells=5, n_perms=20, seed=1337,
    use_raw=False, layer=None, n_jobs=8, verbose=True, inplace=True,
)
dt = time.time() - t0
res = D.uns["liana_res"]
print("elapsed for 20 perms: %.1f s" % dt)
print("columns:", res.columns.tolist())
print("shape:", res.shape)
print(res.head(3).to_string())
res.to_csv(os.path.join(WORK, "results/tables/liana_PROBE_sca20_perms.csv"), index=False)
with open(os.path.join(WORK, "results/tables/liana_PROBE_meta.json"), "w") as f:
    json.dump({"n_cells": int(len(chosen)), "n_perms": 20, "elapsed_s": dt,
               "n_rows": int(len(res)), "columns": res.columns.tolist()}, f, indent=2)
