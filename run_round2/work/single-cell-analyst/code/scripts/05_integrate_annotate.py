"""Stage 2: normalise, HVG, PCA, Harmony (batch=dataset_id), UMAP, validation.

Input : data/processed/scrna_qc_downsampled_v2.h5ad  (raw counts in X and
        layers['counts']; produced by 03b_merge_qc_downsample_instrumented.py)
Output: data/processed/scrna_luad_sclc_integrated.h5ad
            layers['counts']  raw integer counts
            X                 library-size normalised + log1p
            obsm X_pca, X_harmony, X_umap
            obs  donor_id, dataset_id, cell_type, disease, tissue, assay,
                 n_genes, pct_mito
"""
import time
from pathlib import Path

import anndata as ad
import harmonypy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors

BASE = Path(__file__).resolve().parents[2]
PROC = BASE / "data/processed"
FIG = BASE / "results/figures"
TAB = BASE / "results/tables"
np.random.seed(42)
sc.settings.n_jobs = 48
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


adata = ad.read_h5ad(PROC / "scrna_qc_downsampled_v2.h5ad")
log(f"loaded {adata.shape}; layers={list(adata.layers.keys())}")
assert "counts" in adata.layers
assert adata.layers["counts"].nnz == adata.X.nnz

# ---- library-size normalisation + log1p ----
t = time.time()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
log(f"normalised; X max {float(adata.X.max()):.3f} ({time.time() - t:.1f}s)")

# ---- 3,000 HVGs (batch-aware) ----
t = time.time()
sc.pp.highly_variable_genes(adata, n_top_genes=3000, flavor="seurat",
                            batch_key="dataset_id")
log(f"HVGs: {int(adata.var.highly_variable.sum())} ({time.time() - t:.1f}s)")

# ---- PCA on HVG ----
t = time.time()
sc.tl.pca(adata, n_comps=50, use_highly_variable=True, svd_solver="randomized",
          random_state=42)
log(f"PCA {adata.obsm['X_pca'].shape} ({time.time() - t:.1f}s)")

# ---- Harmony on dataset_id ----
t = time.time()
# harmonypy 0.2.0 returns Z_corr as (n_cells, n_pcs); scanpy's wrapper assumes
# the older (n_pcs, n_cells) layout and would transpose it wrongly, so call
# harmonypy directly and normalise the orientation defensively.
ho = harmonypy.run_harmony(adata.obsm["X_pca"].astype(np.float64), adata.obs,
                           "dataset_id", max_iter_harmony=20, random_state=42,
                           verbose=False)
Z = np.asarray(ho.Z_corr)
if Z.shape == (50, adata.n_obs):
    Z = Z.T
assert Z.shape == (adata.n_obs, 50), Z.shape
adata.obsm["X_harmony"] = Z
log(f"Harmony {adata.obsm['X_harmony'].shape} ({time.time() - t:.1f}s)")
assert not np.isnan(adata.obsm["X_harmony"]).any()

# ---- batch-correction validation (subsampled for speed) ----
t = time.time()
rng = np.random.default_rng(42)
idx = rng.choice(adata.n_obs, size=min(30000, adata.n_obs), replace=False)
labels_batch = adata.obs["dataset_id"].astype(str).values
labels_dis = adata.obs["disease"].astype(str).values


def mix_metrics(emb, labels, k=15):
    nn = NearestNeighbors(n_neighbors=k + 1).fit(emb)
    _, ind = nn.kneighbors(emb)
    neigh = ind[:, 1:]
    return float((labels[neigh] == labels[:, None]).mean())


val = []
for name, emb_name in [("X_pca", "X_pca"), ("X_harmony", "X_harmony")]:
    emb = adata.obsm[emb_name][idx]
    val.append(dict(representation=name,
                    asw_dataset=silhouette_score(emb, labels_batch[idx],
                                                 sample_size=10000, random_state=42),
                    asw_disease=silhouette_score(emb, labels_dis[idx],
                                                 sample_size=10000, random_state=42),
                    knn_same_dataset_frac=mix_metrics(emb, labels_batch[idx])))
val = pd.DataFrame(val)
val.to_csv(TAB / "scrna_harmony_validation.csv", index=False)
log(f"harmony validation ({time.time() - t:.1f}s)\n{val.to_string(index=False)}")

# ---- neighbours + UMAP on Harmony ----
t = time.time()
sc.pp.neighbors(adata, n_neighbors=15, use_rep="X_harmony", random_state=42)
log(f"neighbors ({time.time() - t:.1f}s)")
t = time.time()
sc.tl.umap(adata, min_dist=0.3, spread=1.0, random_state=42)
log(f"UMAP {adata.obsm['X_umap'].shape} ({time.time() - t:.1f}s)")

# ---- marker validation of unified cell types ----
markers = ["EPCAM", "KRT18", "PTPRC", "CD3D", "CD3E", "MS4A1", "MZB1", "CD68",
           "C1QA", "COL1A1", "DCN", "PECAM1", "VWF", "TPSAB1", "CPA3",
           "LYZ", "FCGR3B", "SFTPC", "AGER", "HBB", "CD276"]
markers = [m for m in markers if m in adata.var_names]
mk = sc.get.obs_df(adata, keys=markers + ["cell_type"])
marker_tab = mk.groupby("cell_type", observed=True)[markers].mean()
marker_tab.to_csv(TAB / "scrna_celltype_marker_validation.csv")
log(f"marker validation written; markers found: {markers}")

# ---- save deliverable ----
keep_obs = ["donor_id", "dataset_id", "cell_type", "cell_type_original", "disease",
            "tissue", "assay", "n_genes", "pct_mito", "total_counts", "nnz"]
for c in keep_obs:
    if c not in adata.obs:
        adata.obs[c] = np.nan
adata.obs = adata.obs[keep_obs].copy()
adata.obs.index.name = "cell_id"
adata.var.index.name = "gene_id"
t = time.time()
adata.write_h5ad(PROC / "scrna_luad_sclc_integrated.h5ad", compression="lzf")
log(f"SAVED scrna_luad_sclc_integrated.h5ad {adata.shape} ({time.time() - t:.1f}s)")

# ---- append final stages to the audit table ----
def audit_rows(stage, a):
    df = a.obs
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
    return rows


aud = pd.read_csv(TAB / "scrna_cell_donor_audit_stage1_v2.csv")
aud = pd.concat([aud, pd.DataFrame(audit_rows("final_integrated", adata)),
                 pd.DataFrame(audit_rows("final_plotted", adata))], ignore_index=True)
aud.to_csv(TAB / "scrna_cell_donor_audit.csv", index=False)
log(f"audit {TAB / 'scrna_cell_donor_audit.csv'} {aud.shape}")

# ---- figures ----
t = time.time()
fig, axes = plt.subplots(2, 2, figsize=(16, 13))
for ax, key, title in [(axes[0, 0], "disease", "Disease"),
                       (axes[0, 1], "dataset_id", "Dataset"),
                       (axes[1, 0], "cell_type", "Unified cell type"),
                       (axes[1, 1], "cell_type_original", "Original cell type")]:
    sc.pl.umap(adata, color=key, ax=ax, show=False,
               legend_loc="right margin" if key.startswith("cell_type") else "on data",
               legend_fontsize=6, na_color="lightgrey", title=title, frameon=False)
    ax.set_title(title)
fig.tight_layout()
fig.savefig(FIG / "fig4b_umap_luad_sclc.png", dpi=300, bbox_inches="tight")
fig.savefig(FIG / "fig4b_umap_luad_sclc.pdf", bbox_inches="tight")
plt.close(fig)
log(f"wrote fig4b_umap_luad_sclc.png/.pdf ({time.time() - t:.1f}s)")
