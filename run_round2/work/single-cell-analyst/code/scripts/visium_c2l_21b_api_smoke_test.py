"""API smoke test for the cell2location mapping step on a 300-spot subset.

Uses a placeholder signature (positive random values shaped like the real one)
purely to validate that Cell2location.setup_anndata / model init / train /
export_posterior work with scvi-tools 1.4.2 on this installation. It does NOT
produce biological results.
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import anndata as ad
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK  # noqa: E402

np.random.seed(0)
torch.manual_seed(0)
from cell2location.models import Cell2location  # noqa: E402

VIS = f"{WORK}/data/processed/visium_sections_qc.h5ad"
start = time.time()
adata = ad.read_h5ad(VIS)
print("loaded", adata.shape, f"{time.time()-start:.0f}s", flush=True)

# 300 spots from one section to keep it fast
sec = "P10_T1"
adata = adata[adata.obs["section"] == sec].copy()
adata = adata[np.random.choice(adata.n_obs, size=min(300, adata.n_obs), replace=False)].copy()

# placeholder gene set: first 2000 genes with any counts
genes = adata.var_names[:2000]
adata = adata[:, genes].copy()
adata.X = adata.X.astype(np.float32)

rng = np.random.default_rng(0)
fake_sig = pd.DataFrame(
    rng.gamma(shape=2.0, scale=0.5, size=(2000, 14)).astype(np.float32),
    index=adata.var_names,
    columns=[f"type_{i}" for i in range(14)],
)

Cell2location.setup_anndata(adata, batch_key="section")
mod = Cell2location(adata, cell_state_df=fake_sig, N_cells_per_location=8, detection_alpha=20)
print("model ok; n_factors", mod.n_factors_, flush=True)

t = time.time()
mod.train(max_epochs=5, batch_size=256, train_size=1, lr=0.002,
          accelerator="cpu", enable_progress_bar=False,
          enable_checkpointing=False, logger=False)
print(f"train 5 epochs {time.time()-t:.1f}s", flush=True)

t = time.time()
adata = mod.export_posterior(adata, sample_kwargs={"num_samples": 20, "batch_size": 300, "accelerator": "cpu"},
                             use_quantiles=False)
print(f"export {time.time()-t:.1f}s", flush=True)
print("obsm keys:", [k for k in adata.obsm.keys()], flush=True)
print("mean_abundance shape:", adata.obsm["means_cell_abundance_w_sf"].shape, flush=True)
print("q05 shape:", adata.obsm["q05_cell_abundance_w_sf"].shape, flush=True)
print("SMOKE TEST OK", flush=True)
