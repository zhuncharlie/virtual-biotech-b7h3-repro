"""Inspect downloaded Census h5ad structure before analysis."""
import scanpy as sc
import numpy as np
import pandas as pd

BASE = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/single-cell-analyst"
files = [
    "luad_ds1e6a_lymphoid_cd276.h5ad", "luad_ds1e6a_myeloid_cd276.h5ad",
    "luad_ds1e6a_epithelial_stromal_cd276.h5ad", "luad_other_datasets_cd276.h5ad",
    "sclc_cd276.h5ad", "normal_lung_matched_cd276.h5ad", "normal_blood_cd276.h5ad",
]
for f in files:
    a = sc.read_h5ad(f"{BASE}/data/raw/{f}")
    print(f"\n=== {f}: {a.shape} ===")
    print("var_names:", list(a.var_names)[:5], "| var cols:", list(a.var.columns))
    print("obs cols:", list(a.obs.columns))
    print("X dtype:", a.X.dtype, "| min/max:", float(a.X.min()), float(a.X.max()))
    print("X type:", type(a.X).__name__)
    for c in ["dataset_id", "disease", "tissue"]:
        if c in a.obs:
            print(f"  {c}:", a.obs[c].astype(str).value_counts().head(5).to_dict())
    print("  cell types:", a.obs.cell_type.astype(str).nunique(), "| donors:", a.obs.donor_id.astype(str).nunique())
    if f.startswith("luad_other") or f.startswith("normal_lung"):
        print("  cell_type counts:", a.obs.cell_type.astype(str).value_counts().to_dict())
    # check X stores log1p CP10K (max ~10) and integer-ness
    vals = a.X[:2000].toarray().ravel() if hasattr(a.X, "toarray") else np.asarray(a.X[:2000]).ravel()
    print("  sample noninteger frac:", float(np.mean(np.mod(vals, 1) != 0)), "| nnz frac:", float(np.mean(vals > 0)))
