"""
Panel 4E / S5B step 1: build the cell2location single-cell reference from the
integrated LUAD/SCLC atlas.

Rules (pre-specified):
  - keep LUAD + normal lung cells only; EXCLUDE small cell lung carcinoma (SCLC)
    because the Visium cohort is lung adenocarcinoma.
  - keep cell types with >= 50 cells in the retained reference.
  - EXCLUDE CD276 (B7-H3) from every gene used for training / mapping
    (circularity guard: CD276 is the stratification variable downstream).
  - select 2,000 highly variable genes (seurat_v3 on raw counts, batch-aware).
  - optional per-cell-type subsample, fixed seed, documented.

Outputs:
  data/processed/c2l_reference_luad_normal_hvg2000.h5ad
  results/tables/visium_c2l_reference_preparation.csv
  results/tables/visium_c2l_reference_gene_selection.csv
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import RUN, LOG, log_run, ensure_dirs  # noqa: E402

SCRNA = f"{RUN}/work/single-cell-analyst/data/processed/scrna_luad_sclc_integrated.h5ad"
OUT_H5AD = f"{RUN}/work/single-cell-analyst/data/processed/c2l_reference_luad_normal_hvg2000.h5ad"
TAB_DIR = f"{RUN}/work/single-cell-analyst/results/tables"
N_HVG = 2000
MIN_CELLS_PER_TYPE = 50
SEED = 42

t0 = time.time()
np.random.seed(SEED)

print("Reading reference (backed) ...", flush=True)
ref = ad.read_h5ad(SCRNA)
print("Loaded:", ref.shape, flush=True)

# ---------------------------------------------------------------- provenance
record = {"step": "reference_ingest", "n_cells_input": int(ref.n_obs),
          "n_genes_input": int(ref.n_vars)}

# raw counts live in .layers['counts']; .X is the log-normalised matrix
X_counts = ref.layers["counts"]
print("counts layer dtype:", X_counts.dtype, "min:", X_counts.min(),
      "max:", X_counts.max(), flush=True)

# ------------------------------------------------------------------ disease
before_disease = ref.obs["disease"].value_counts().to_dict()
keep_disease = ref.obs["disease"].isin(["lung adenocarcinoma", "normal"]).values
ref = ref[keep_disease].copy()
print("After excluding SCLC:", ref.shape, flush=True)

# --------------------------------------------------------- cell-type filter
ct_counts_before = ref.obs["cell_type"].value_counts()
keep_ct = ct_counts_before[ct_counts_before >= MIN_CELLS_PER_TYPE].index
dropped_ct = ct_counts_before[ct_counts_before < MIN_CELLS_PER_TYPE]
ref = ref[ref.obs["cell_type"].isin(keep_ct)].copy()
print("Cell types kept:", len(keep_ct), "dropped:", dropped_ct.to_dict(), flush=True)

# ensure counts layer is the only thing we need, and make sparse float32
ref.X = ref.layers["counts"].astype(np.float32)
del ref.layers["counts"]

# ------------------------------------------------------------ gene handling
n_genes_pre = ref.n_vars
cd276_present = "CD276" in ref.var_names
print("CD276 present in reference before exclusion:", cd276_present, flush=True)

# drop CD276 BEFORE HVG selection so it can never enter the model
if cd276_present:
    ref = ref[:, ref.var_names != "CD276"].copy()

# drop genes with zero counts anywhere (cell2location requires non-degenerate)
sc.pp.filter_genes(ref, min_cells=1)
n_genes_after_filter = ref.n_vars
print("Genes after min_cells=1 filter:", n_genes_after_filter, flush=True)

# HVG selection, batch-aware (dataset_id captures study/batch)
sc.pp.highly_variable_genes(
    ref, n_top_genes=N_HVG, batch_key="dataset_id", flavor="seurat_v3",
    layer=None, subset=True,
)
print("After HVG subset:", ref.shape, flush=True)

assert "CD276" not in ref.var_names, "CD276 leaked into reference genes"

# ------------------------------------------------------------- subsampling
# controlled by env var so the same script documents both the full run and a
# CPU-tractability run
SUBSAMPLE_PER_TYPE = int(os.environ.get("C2L_SUBSAMPLE_PER_TYPE", "0"))
subsample_rule = "none (all cells)"
if SUBSAMPLE_PER_TYPE > 0:
    rng = np.random.default_rng(SEED)
    keep_idx = []
    for ct, idx in ref.obs.groupby("cell_type", observed=True).indices.items():
        if len(idx) > SUBSAMPLE_PER_TYPE:
            keep_idx.extend(rng.choice(idx, SUBSAMPLE_PER_TYPE, replace=False))
        else:
            keep_idx.extend(idx)
    keep_idx = np.sort(np.asarray(keep_idx))
    ref = ref[keep_idx].copy()
    subsample_rule = (f"max {SUBSAMPLE_PER_TYPE} cells per cell type, "
                      f"numpy default_rng(seed={SEED}), replace=False")
print("After subsampling:", ref.shape, "rule:", subsample_rule, flush=True)

# ---------------------------------------------- reference preparation table
ct_final = ref.obs["cell_type"].value_counts()
ct_disease = pd.crosstab(ref.obs["cell_type"], ref.obs["disease"])
prep = pd.DataFrame({
    "cell_type": ct_final.index.astype(str),
    "n_cells_reference": ct_final.values,
})
prep["n_luad"] = prep["cell_type"].map(ct_disease.get("lung adenocarcinoma", pd.Series(dtype=int))).fillna(0).astype(int)
prep["n_normal"] = prep["cell_type"].map(ct_disease.get("normal", pd.Series(dtype=int))).fillna(0).astype(int)
prep["n_donors"] = prep["cell_type"].map(ref.obs.groupby("cell_type", observed=True)["donor_id"].nunique())
prep["kept"] = True
prep["drop_reason"] = ""
for ct, n in dropped_ct.items():
    prep.loc[len(prep)] = [ct, 0, 0, 0, 0, False,
                           f"<{MIN_CELLS_PER_TYPE} cells in LUAD+normal reference (n={int(n)})"]
prep["subsample_rule"] = subsample_rule
prep = prep.sort_values("n_cells_reference", ascending=False)
prep.to_csv(f"{TAB_DIR}/visium_c2l_reference_preparation.csv", index=False)

gene_sel = pd.DataFrame({
    "item": ["genes_input", "genes_after_CD276_exclusion", "genes_after_min_cells_filter",
             "genes_after_HVG", "n_hvg_requested", "hvg_flavor", "hvg_batch_key",
             "CD276_in_reference_genes", "n_cell_types_input", "n_cell_types_kept",
             "cell_types_dropped", "n_cells_reference", "subsample_rule"],
    "value": [n_genes_pre, n_genes_pre - int(cd276_present), n_genes_after_filter,
              int(ref.n_vars), N_HVG, "seurat_v3", "dataset_id",
              str("CD276" in ref.var_names), len(ct_counts_before), len(keep_ct),
              "; ".join(f"{k}(n={v})" for k, v in dropped_ct.items()),
              int(ref.n_obs), subsample_rule],
})
gene_sel.to_csv(f"{TAB_DIR}/visium_c2l_reference_gene_selection.csv", index=False)

ref.write_h5ad(OUT_H5AD, compression="gzip")
print("Saved", OUT_H5AD, ref.shape, flush=True)

log_run(step="prep_reference", status="ok", wall_time_s=round(time.time() - t0, 1),
        n_cells=ref.n_obs, n_genes=ref.n_vars,
        detail=f"SCLC excluded; CD276 excluded; {subsample_rule}")
print("DONE", flush=True)
