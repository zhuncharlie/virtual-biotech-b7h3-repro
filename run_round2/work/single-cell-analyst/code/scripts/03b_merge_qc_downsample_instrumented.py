"""Stage 1 (instrumented, unbuffered): merge, QC, harmonise, donor-downsample.

Identical logic and seed to 03_merge_qc_downsample.py, but every step prints a
timestamp so a stall can be localised. QC metrics are computed directly from the
CSR matrix (row nnz / row sum / MT row sum) instead of scanpy's
calculate_qc_metrics, which also computes per-gene statistics that the run does
not need.

Outputs (v2 names so they cannot collide with the concurrently running 03):
  data/processed/scrna_qc_downsampled_v2.h5ad
  results/tables/scrna_cell_donor_audit_stage1_v2.csv
  results/tables/scrna_donor_downsampling_report_v2.csv
"""
import sys
import time
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scipy.sparse as sp

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data/raw/h5ad"
PROC = BASE / "data/processed"
TAB = BASE / "results/tables"
np.random.seed(42)
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


BATCHES = ["batch01_576f193c_all.h5ad", "batch02_1e6a6ef9_luad.h5ad",
           "batch03_1e6a6ef9_luad.h5ad"]

UNIFIED = {
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
    "T cell": "T cell", "epithelial cell": "epithelial cell",
    "fibroblast": "fibroblast", "endothelial cell": "endothelial cell",
}

audit_rows = []


def add_audit(stage, adata):
    df = adata.obs
    rows = [dict(stage=stage, grouping="overall", dataset_id="ALL", disease="ALL",
                 n_cells=len(df), n_donors=df.donor_id.astype(str).nunique(),
                 n_cell_types=df.cell_type.astype(str).nunique())]
    ds = df.dataset_id.astype(str)
    dis = df.disease.astype(str)
    for (d, s), g in df.groupby([ds, dis], observed=True):
        rows.append(dict(stage=stage, grouping="dataset_disease", dataset_id=d, disease=s,
                         n_cells=len(g), n_donors=g.donor_id.astype(str).nunique(),
                         n_cell_types=g.cell_type.astype(str).nunique()))
    for d, g in df.groupby(ds, observed=True):
        rows.append(dict(stage=stage, grouping="dataset", dataset_id=d, disease="ALL",
                         n_cells=len(g), n_donors=g.donor_id.astype(str).nunique(),
                         n_cell_types=g.cell_type.astype(str).nunique()))
    for s, g in df.groupby(dis, observed=True):
        rows.append(dict(stage=stage, grouping="disease", dataset_id="ALL", disease=s,
                         n_cells=len(g), n_donors=g.donor_id.astype(str).nunique(),
                         n_cell_types=g.cell_type.astype(str).nunique()))
    audit_rows.extend(rows)
    log(f"AUDIT {stage}: {len(df)} cells, {df.donor_id.astype(str).nunique()} donors")


# ---- load and merge ----
adatas = []
for b in BATCHES:
    t = time.time()
    a = ad.read_h5ad(RAW / b)
    a.obs_names = "cell_" + a.obs["soma_joinid"].astype(str)
    assert a.obs_names.is_unique, b
    a.X = sp.csr_matrix(a.X)
    adatas.append(a)
    log(f"read {b} {a.shape} nnz={a.X.nnz} ({time.time() - t:.1f}s)")

t = time.time()
adata = ad.concat(adatas, join="inner", merge="same")
del adatas
assert adata.obs_names.is_unique
log(f"concat {adata.shape} nnz={adata.X.nnz} ({time.time() - t:.1f}s)")

t = time.time()
adata.var.index = adata.var["feature_name"].astype(str)
adata.var_names_make_unique()
adata.var_names = adata.var_names.astype(str)
# the var index name must not collide with the still-present feature_name column
adata.var.index.name = "gene_id"
log(f"var_names from feature_name ({time.time() - t:.1f}s)")

t = time.time()
adata.obs["dataset_id"] = adata.obs["dataset_id"].astype(str)
adata.obs["disease"] = adata.obs["disease"].astype(str)
adata.obs["donor_id"] = adata.obs["donor_id"].astype(str)
adata.obs["cell_type_original"] = adata.obs["cell_type"].astype(str)
adata.obs["cell_type"] = adata.obs["cell_type_original"].map(UNIFIED)
missing = adata.obs.loc[adata.obs["cell_type"].isna(), "cell_type_original"].unique()
if len(missing):
    log(f"WARNING unmapped labels: {list(missing)[:20]}")
    adata.obs["cell_type"] = adata.obs["cell_type"].fillna(adata.obs["cell_type_original"])
log(f"obs harmonisation ({time.time() - t:.1f}s); "
    f"{adata.obs.cell_type.nunique()} unified types")

add_audit("raw_pull", adata)

# ---- QC metrics straight from CSR ----
t = time.time()
X = adata.X
if not sp.isspmatrix_csr(X):
    X = X.tocsr()
    adata.X = X
X.eliminate_zeros()
n_genes = np.diff(X.indptr).astype(np.int32)
total_counts = np.asarray(X.sum(axis=1)).ravel().astype(np.float32)
mt_mask = np.asarray(adata.var_names.str.upper().str.startswith("MT-"), dtype=bool)
log(f"MT genes: {int(mt_mask.sum())}")
mt_counts = np.asarray(X[:, mt_mask].sum(axis=1)).ravel()
pct_mito = (mt_counts / np.maximum(total_counts, 1) * 100).astype(np.float32)
adata.obs["n_genes"] = n_genes
adata.obs["total_counts"] = total_counts
adata.obs["mt_counts"] = mt_counts.astype(np.float32)
adata.obs["pct_mito"] = pct_mito
log(f"QC metrics computed ({time.time() - t:.1f}s); median n_genes "
    f"{np.median(n_genes):.0f}, median pct_mito {np.median(pct_mito):.2f}")
log("pct_mito percentiles 50/90/99/max: "
    + ", ".join(f"{np.percentile(pct_mito, q):.2f}" for q in (50, 90, 99, 100)))
log(f"cells with zero MT counts: {int((mt_counts == 0).sum())}/{len(mt_counts)}; "
    f"MT genes present: {list(adata.var_names[mt_mask][:5])}")

# ---- QC filter ----
t = time.time()
ng = adata.obs.n_genes.to_numpy()
pm = adata.obs.pct_mito.to_numpy()
gene_ok = (ng >= 300) & (ng <= 9000)
mito_ok = pm <= 15
keep = gene_ok & mito_ok
log(f"QC breakdown: fail n_genes<300 {int((ng < 300).sum())}, "
    f"fail n_genes>9000 {int((ng > 9000).sum())}, "
    f"fail pct_mito>15 {int((~mito_ok).sum())} "
    f"(mito unavailable -> filter inert)")
log(f"QC pass {int(keep.sum())}/{len(keep)} = {100 * keep.mean():.2f}%")
adata = adata[keep].copy()
log(f"QC subset ({time.time() - t:.1f}s) -> {adata.shape} nnz={adata.X.nnz}")
add_audit("post_qc", adata)

# ---- donor-level downsampling, stratified by cell type ----
t = time.time()
MAX_PER_DONOR, RARE_FLOOR = 10000, 5
rng = np.random.default_rng(42)
keep_names = []
ds_report = []
obs = adata.obs
for donor, g in obs.groupby("donor_id", observed=True):
    n = len(g)
    if n <= MAX_PER_DONOR:
        keep_names.extend(g.index.tolist())
        ds_report.append(dict(donor_id=donor, n_before=n, n_after=n, downsampled=False))
        continue
    sizes = g.groupby("cell_type", observed=True).size()
    raw_alloc = sizes / n * MAX_PER_DONOR
    alloc = pd.Series(np.floor(raw_alloc.values).astype(int), index=sizes.index)
    floor = pd.Series(np.minimum(sizes.values, RARE_FLOOR), index=sizes.index)
    alloc = alloc.clip(lower=floor)
    while alloc.sum() > MAX_PER_DONOR:
        over = int(alloc.sum() - MAX_PER_DONOR)
        for j in alloc.sort_values(ascending=False).index:
            if over == 0:
                break
            reducible = max(0, int(alloc[j] - floor[j]))
            take = min(over, reducible)
            alloc[j] -= take
            over -= take
    if alloc.sum() < MAX_PER_DONOR:
        short = MAX_PER_DONOR - int(alloc.sum())
        remainder = (raw_alloc - np.floor(raw_alloc)).sort_values(ascending=False)
        for j in remainder.index:
            if short == 0:
                break
            take = min(short, int(sizes[j] - alloc[j]))
            alloc[j] += take
            short -= take
    for ct in sizes.index:
        pool = g.index[g["cell_type"] == ct].to_numpy()
        k = int(min(alloc[ct], len(pool)))
        if k > 0:
            keep_names.extend(rng.choice(pool, size=k, replace=False).tolist())
    ds_report.append(dict(donor_id=donor, n_before=n, n_after=int(alloc.sum()),
                          downsampled=True))
log(f"downsampling allocations ({time.time() - t:.1f}s); "
    f"{sum(r['downsampled'] for r in ds_report)} donors downsampled")

t = time.time()
mask = obs.index.isin(keep_names)
adata = adata[mask].copy()
log(f"downsample subset ({time.time() - t:.1f}s) -> {adata.shape} nnz={adata.X.nnz}")
pd.DataFrame(ds_report).to_csv(TAB / "scrna_donor_downsampling_report_v2.csv", index=False)
add_audit("post_downsample", adata)

# ---- save ----
# anndata refuses to write when the obs index name duplicates a column name whose
# values differ (here soma_joinid); give the index an explicit non-column name.
adata.obs.index.name = "cell_id"
assert "cell_id" not in adata.obs.columns
adata.layers["counts"] = adata.X.copy()
log("counts layer copied")
t = time.time()
adata.write_h5ad(PROC / "scrna_qc_downsampled_v2.h5ad", compression="lzf")
log(f"WROTE scrna_qc_downsampled_v2.h5ad ({time.time() - t:.1f}s) {adata.shape}")

pd.DataFrame(audit_rows).to_csv(TAB / "scrna_cell_donor_audit_stage1_v2.csv", index=False)
log("audit written")
log(pd.DataFrame(audit_rows)[["stage", "grouping", "n_cells", "n_donors"]]
    .query("grouping == 'overall'").to_string(index=False))
