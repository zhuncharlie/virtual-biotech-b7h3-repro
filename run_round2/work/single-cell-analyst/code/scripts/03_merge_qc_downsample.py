"""Stage 1: merge Census batches, QC, harmonise cell types, donor-downsample.

QC spec (paper-matched): 300 <= n_genes <= 9000 and pct_mito <= 15.
Downsampling: max 10,000 cells per donor, stratified by harmonised cell type,
proportional allocation with a rare-type floor (min(5, available) cells) and
largest-remainder adjustment to hit the cap exactly.
"""
import json
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data/raw/h5ad"
PROC = BASE / "data/processed"
TAB = BASE / "results/tables"
PROC.mkdir(parents=True, exist_ok=True)
np.random.seed(42)

BATCHES = ["batch01_576f193c_all.h5ad", "batch02_1e6a6ef9_luad.h5ad",
           "batch03_1e6a6ef9_luad.h5ad"]

# ---- harmonisation map: dataset-specific granular labels -> unified labels ----
UNIFIED = {
    # 1e6a6ef9 granular labels
    "CD4-positive, alpha-beta T cell": "T cell",
    "CD8-positive, alpha-beta T cell": "T cell",
    "regulatory T cell": "T cell",
    "natural killer cell": "NK cell",
    "B cell": "B cell",
    "plasma cell": "plasma cell",
    "alveolar macrophage": "macrophage",
    "macrophage": "macrophage",
    "classical monocyte": "monocyte/myeloid",
    "non-classical monocyte": "monocyte/myeloid",
    "myeloid cell": "monocyte/myeloid",
    "CD1c-positive myeloid dendritic cell": "dendritic cell",
    "plasmacytoid dendritic cell": "dendritic cell",
    "conventional dendritic cell": "dendritic cell",
    "dendritic cell": "dendritic cell",
    "fibroblast of lung": "fibroblast",
    "bronchus fibroblast of lung": "fibroblast",
    "endothelial cell of lymphatic vessel": "endothelial cell",
    "vein endothelial cell": "endothelial cell",
    "capillary endothelial cell": "endothelial cell",
    "pulmonary artery endothelial cell": "endothelial cell",
    "epithelial cell of lung": "epithelial cell",
    "pulmonary alveolar type 2 cell": "epithelial cell",
    "pulmonary alveolar type 1 cell": "epithelial cell",
    "club cell": "epithelial cell",
    "multiciliated epithelial cell": "epithelial cell",
    "malignant cell": "malignant cell",
    "mast cell": "mast cell",
    "neutrophil": "neutrophil",
    "smooth muscle cell": "stromal/other",
    "pericyte": "stromal/other",
    "stromal cell": "stromal/other",
    "mesothelial cell": "stromal/other",
    "erythrocyte": "erythrocyte",
    # 576f coarse labels pass through
    "T cell": "T cell", "epithelial cell": "epithelial cell",
    "fibroblast": "fibroblast", "endothelial cell": "endothelial cell",
}

audit_rows = []


def add_audit(stage, adata, extra=None):
    df = adata.obs
    rows = [dict(stage=stage, grouping="overall", dataset_id="ALL", disease="ALL",
                 n_cells=len(df), n_donors=df.donor_id.astype(str).nunique(),
                 n_cell_types=df.cell_type.astype(str).nunique())]
    for (ds, dis), g in df.groupby([df.dataset_id.astype(str), df.disease.astype(str)], observed=True):
        rows.append(dict(stage=stage, grouping="dataset_disease", dataset_id=ds, disease=dis,
                         n_cells=len(g), n_donors=g.donor_id.astype(str).nunique(),
                         n_cell_types=g.cell_type.astype(str).nunique()))
    for ds, g in df.groupby(df.dataset_id.astype(str), observed=True):
        rows.append(dict(stage=stage, grouping="dataset", dataset_id=ds, disease="ALL",
                         n_cells=len(g), n_donors=g.donor_id.astype(str).nunique(),
                         n_cell_types=g.cell_type.astype(str).nunique()))
    for dis, g in df.groupby(df.disease.astype(str), observed=True):
        rows.append(dict(stage=stage, grouping="disease", dataset_id="ALL", disease=dis,
                         n_cells=len(g), n_donors=g.donor_id.astype(str).nunique(),
                         n_cell_types=g.cell_type.astype(str).nunique()))
    audit_rows.extend(rows)
    print("AUDIT", stage, "| overall", len(df), "cells",
          df.donor_id.astype(str).nunique(), "donors")


# ---- load and merge ----
adatas = []
for b in BATCHES:
    a = ad.read_h5ad(RAW / b)
    # Census MCP returns positional obs_names (0..n-1) per query; use globally
    # unique soma_joinid so cells cannot collide when batches are concatenated.
    a.obs_names = "cell_" + a.obs["soma_joinid"].astype(str)
    assert a.obs_names.is_unique, b
    print(b, a.shape, "obs_names unique:", a.obs_names.is_unique)
    adatas.append(a)
adata = ad.concat(adatas, join="inner", merge="same")
del adatas
assert adata.obs_names.is_unique, "duplicate cell names after concat"
# Census fix: numeric var_names -> gene symbols
adata.var.index = adata.var["feature_name"].astype(str)
adata.var_names_make_unique()
print("MERGED", adata.shape, "| genes unique:", adata.var_names.is_unique)
print("feature_type:\n", adata.var["feature_type"].astype(str).value_counts().to_string())

adata.obs["dataset_id"] = adata.obs["dataset_id"].astype(str)
adata.obs["disease"] = adata.obs["disease"].astype(str)
adata.obs["donor_id"] = adata.obs["donor_id"].astype(str)
adata.obs["cell_type_original"] = adata.obs["cell_type"].astype(str)
adata.obs["cell_type"] = adata.obs["cell_type_original"].map(UNIFIED)
missing = adata.obs.loc[adata.obs["cell_type"].isna(), "cell_type_original"].unique()
if len(missing):
    print("WARNING unmapped labels:", missing)
    adata.obs["cell_type"] = adata.obs["cell_type"].fillna(adata.obs["cell_type_original"])

add_audit("raw_pull", adata)

# ---- QC metrics on raw counts ----
adata.X = adata.X.tocsr()
adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
adata.obs["n_genes"] = adata.obs["n_genes_by_counts"].astype(int)
adata.obs["pct_mito"] = adata.obs["pct_counts_mt"].astype(float)
print("QC metric ranges: n_genes", adata.obs.n_genes.min(), adata.obs.n_genes.max(),
      "| pct_mito", round(adata.obs.pct_mito.min(), 2), round(adata.obs.pct_mito.max(), 2))
print("median n_genes", adata.obs.n_genes.median(), "median pct_mito", adata.obs.pct_mito.median())

# ---- QC filter ----
keep = (adata.obs.n_genes >= 300) & (adata.obs.n_genes <= 9000) & (adata.obs.pct_mito <= 15)
print("QC pass:", int(keep.sum()), "/", len(keep), "=", round(100 * keep.mean(), 2), "%")
adata = adata[keep].copy()
add_audit("post_qc", adata)

# ---- donor-level downsampling, stratified by cell type ----
MAX_PER_DONOR = 10000
RARE_FLOOR = 5
rng = np.random.default_rng(42)
keep_idx = []
ds_report = []
for donor, g in adata.obs.groupby("donor_id", observed=True):
    n = len(g)
    if n <= MAX_PER_DONOR:
        keep_idx.extend(g.index.tolist())
        ds_report.append(dict(donor_id=donor, n_before=n, n_after=n, downsampled=False))
        continue
    sizes = g.groupby("cell_type", observed=True).size()
    frac = sizes / n
    raw_alloc = frac * MAX_PER_DONOR
    order = sizes.index
    alloc = pd.Series(np.floor(raw_alloc.values).astype(int), index=order)
    # rare-type floor: keep min(RARE_FLOOR, available) cells for every present type
    floor = pd.Series(np.minimum(sizes.values, RARE_FLOOR), index=order)
    alloc = alloc.clip(lower=floor)
    # if floors push above cap, trim from the largest types
    while alloc.sum() > MAX_PER_DONOR:
        over = int(alloc.sum() - MAX_PER_DONOR)
        for j in alloc.sort_values(ascending=False).index:
            if over == 0:
                break
            reducible = max(0, int(alloc[j] - floor[j]))
            take = min(over, reducible)
            alloc[j] -= take
            over -= take
    # largest-remainder adjustment upward to exactly MAX_PER_DONOR
    if alloc.sum() < MAX_PER_DONOR:
        short = MAX_PER_DONOR - int(alloc.sum())
        remainder = (raw_alloc - np.floor(raw_alloc)).sort_values(ascending=False)
        for j in remainder.index:
            if short == 0:
                break
            room = int(sizes[j] - alloc[j])
            take = min(short, room)
            alloc[j] += take
            short -= take
    for ct in sizes.index:
        pool = g.index[g["cell_type"] == ct].tolist()
        k = int(min(alloc[ct], len(pool)))
        if k > 0:
            keep_idx.extend(rng.choice(pool, size=k, replace=False).tolist())
    ds_report.append(dict(donor_id=donor, n_before=n, n_after=int(alloc.sum()), downsampled=True))

adata = adata[np.isin(adata.obs_names, keep_idx)].copy()
add_audit("post_downsample", adata)
pd.DataFrame(ds_report).to_csv(TAB / "scrna_donor_downsampling_report.csv", index=False)
print("Downsample: donors", len(ds_report), "downsampled donors",
      sum(r["downsampled"] for r in ds_report))

# ---- save intermediate (raw counts preserved) ----
adata.layers["counts"] = adata.X.copy()
adata.write_h5ad(PROC / "scrna_qc_downsampled.h5ad", compression="lzf")
print("Saved", PROC / "scrna_qc_downsampled.h5ad", adata.shape)

audit = pd.DataFrame(audit_rows)
audit.to_csv(TAB / "scrna_cell_donor_audit_stage1.csv", index=False)
print(audit.to_string())
