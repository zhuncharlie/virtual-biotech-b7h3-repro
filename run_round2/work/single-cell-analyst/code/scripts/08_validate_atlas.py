"""Validate the deliverable atlas and summarise CD276 expression.

Outputs
  results/tables/scrna_atlas_validation.csv        pass/fail checks
  results/tables/scrna_cd276_expression_by_celltype.csv
      CD276 detection and mean log-normalised expression per
      dataset x disease x cell type (B7-H3 target context for the atlas)
"""
import time
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
PROC = BASE / "data/processed"
TAB = BASE / "results/tables"
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.1f}s] {msg}", flush=True)


a = ad.read_h5ad(PROC / "scrna_luad_sclc_integrated.h5ad")
log(f"loaded {a.shape}; layers={list(a.layers.keys())}; obsm={list(a.obsm.keys())}")

required_obs = ["donor_id", "dataset_id", "cell_type", "disease", "tissue", "assay",
                "n_genes", "pct_mito"]
counts = a.layers["counts"]
is_int = bool(np.all(np.equal(np.mod(counts.data, 1), 0))) if hasattr(counts, "data") else False

checks = [
    ("n_cells", a.n_obs, True),
    ("n_genes", a.n_vars, True),
    ("has_counts_layer", "counts" in a.layers, "counts" in a.layers),
    ("counts_integer_valued", is_int, is_int),
    ("counts_nnz_equals_X_nnz", f"{counts.nnz}=={a.X.nnz}", counts.nnz == a.X.nnz),
    ("X_is_lognorm_max<20", round(float(a.X.max()), 3), float(a.X.max()) < 20),
    ("obsm_X_pca", a.obsm["X_pca"].shape if "X_pca" in a.obsm else "MISSING",
     "X_pca" in a.obsm and a.obsm["X_pca"].shape[0] == a.n_obs),
    ("obsm_X_harmony", a.obsm["X_harmony"].shape if "X_harmony" in a.obsm else "MISSING",
     "X_harmony" in a.obsm and a.obsm["X_harmony"].shape[0] == a.n_obs),
    ("obsm_X_umap", a.obsm["X_umap"].shape if "X_umap" in a.obsm else "MISSING",
     "X_umap" in a.obsm and a.obsm["X_umap"].shape[0] == a.n_obs),
    ("obs_columns_present", all(c in a.obs for c in required_obs),
     all(c in a.obs for c in required_obs)),
    ("donors", a.obs.donor_id.astype(str).nunique(), True),
    ("datasets", a.obs.dataset_id.astype(str).nunique(), True),
    ("cell_types", a.obs.cell_type.astype(str).nunique(), True),
    ("no_nan_umap", bool(np.isnan(a.obsm["X_umap"]).any()) is False,
     bool(np.isnan(a.obsm["X_umap"]).any()) is False),
]
v = pd.DataFrame(checks, columns=["check", "value", "pass"])
v.to_csv(TAB / "scrna_atlas_validation.csv", index=False)
log("validation:\n" + v.to_string(index=False))

# ---- CD276 expression per dataset x disease x cell type ----
if "CD276" in a.var_names:
    j = a.var_names.get_loc("CD276")
    expr = np.asarray(a.X[:, j].todense()).ravel() if hasattr(a.X, "todense") else np.asarray(a.X[:, j]).ravel()
    raw = np.asarray(counts[:, j].todense()).ravel() if hasattr(counts, "todense") else np.asarray(counts[:, j]).ravel()
    df = a.obs[["dataset_id", "disease", "cell_type"]].copy()
    df["expr"] = expr
    df["raw"] = raw
    df["detected"] = raw > 0
    out = (df.groupby(["dataset_id", "disease", "cell_type"], observed=True)
             .agg(n_cells=("expr", "size"), pct_detected=("detected", "mean"),
                  mean_log_expr=("expr", "mean"), mean_raw_counts=("raw", "mean"))
             .reset_index())
    out["pct_detected"] = (out["pct_detected"] * 100).round(2)
    out["mean_log_expr"] = out["mean_log_expr"].round(3)
    out["mean_raw_counts"] = out["mean_raw_counts"].round(3)
    out = out.sort_values(["dataset_id", "disease", "mean_log_expr"], ascending=[True, True, False])
    out.to_csv(TAB / "scrna_cd276_expression_by_celltype.csv", index=False)
    log(f"CD276 table rows {len(out)}; top rows:\n{out.head(8).to_string(index=False)}")
else:
    log("CD276 not in var_names -- CD276 table not written")
