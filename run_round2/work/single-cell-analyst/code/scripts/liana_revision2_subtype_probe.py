#!/usr/bin/env python
"""Probe the source atlas for fibroblast subtype annotations and markers.

Read-only. Prints obs columns, candidate subtype columns and the CD276/CAF marker
genes available in var. Does not modify the atlas.
"""
import anndata as ad
import h5py
import numpy as np

SRC = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/single-cell-analyst"
ATLAS = f"{SRC}/data/processed/scrna_luad_sclc_integrated.h5ad"

A = ad.read_h5ad(ATLAS, backed="r")
print("shape:", A.shape)
print("obs columns:", list(A.obs.columns))
print("obsm:", list(A.obsm.keys()))
cand = [c for c in A.obs.columns if any(k in c.lower() for k in
        ["subtype", "fibro", "caf", "annot", "cell_type", "celltype", "cluster", "label"])]
print("candidate annotation columns:", cand)
for c in cand:
    print(f"--- {c}: dtype={A.obs[c].dtype}, n_unique={A.obs[c].nunique()}")
    print(A.obs[c].value_counts().head(30).to_string())

fib = A.obs[A.obs["cell_type"].astype(str).str.contains("fibro", case=False, na=False)]
print("\nfibroblast rows:", len(fib))
for c in cand:
    print(f"fibroblast values in {c}:")
    print(fib[c].value_counts().head(20).to_string())

markers = ["CD276", "ACTA2", "TAGLN", "MYL9", "CNN1", "MYH11", "IL6", "CXCL12",
           "HAS1", "PDGFRA", "LIF", "DCN", "COL1A1", "COL1A2", "LUM", "PDGFRB",
           "MMP11", "CTHRC1", "POSTN", "FAP"]
names = A.var["feature_name"].astype(str) if "feature_name" in A.var.columns else A.var_names.astype(str)
present = [m for m in markers if m in set(names)]
print("\nmarkers present:", present)
print("markers absent:", [m for m in markers if m not in set(names)])
A.file.close()

# validate the SCLC universe h5ad (open only; no full read)
for path in [
    f"{SRC}/data/processed/liana/liana_SCLC_universe.h5ad",
    f"{SRC}/data/processed/liana/liana_LUAD_universe.h5ad",
]:
    try:
        with h5py.File(path, "r") as f:
            print(f"\nHDF5 OK: {path}")
            print("  keys:", list(f.keys()))
            if "X" in f and hasattr(f["X"], "attrs"):
                print("  X attrs:", dict(f["X"].attrs))
            if "obs" in f:
                print("  obs keys:", list(f["obs"].keys())[:20])
    except Exception as e:
        print(f"\nHDF5 FAILED: {path}: {type(e).__name__}: {e}")
