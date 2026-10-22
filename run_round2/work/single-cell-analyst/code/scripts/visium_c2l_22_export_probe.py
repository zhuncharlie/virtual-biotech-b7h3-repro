"""
API probe (NOT a biological result): check whether cell2location's posterior
export returns finite abundance values under the installed scvi-tools 1.4 /
cell2location 0.1.5, and confirm the exact cause of the all-NaN production
output.

The production mapping wrote:
    pd.DataFrame(adata.obsm["means_cell_abundance_w_sf"], index=...,
                 columns=[f"mean_{c}" for c in factor_names])
The obsm DataFrame's columns are bare cell-type names, so passing the prefixed
names as `columns=` performs label SELECTION and produces all-NaN columns.
This probe tests (a) raw obsm finiteness and (b) the correct rename path.

Outputs
-------
logs/c2l_export_probe_finiteness.csv
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import anndata as ad
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run  # noqa: E402

SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)
t0 = time.time()

VIS = (f"/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
       f"20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/"
       f"single-cell-analyst/data/processed/visium_sections_qc.h5ad")
SIG = f"{WORK}/results/tables/c2l_reference_celltype_signatures_mean.csv"
LOGS = f"{WORK}/logs"

from cell2location.models import Cell2location  # noqa: E402

inf_aver = pd.read_csv(SIG, index_col=0)
a = ad.read_h5ad(VIS)
a = a[:3000].copy()                       # probe only
common = [g for g in inf_aver.index if g in a.var_names]
a = a[:, common].copy()
a.X = a.X.astype(np.float32)
inf_aver = inf_aver.loc[common]
Cell2location.setup_anndata(a, batch_key="section")
mod = Cell2location(a, cell_state_df=inf_aver, N_cells_per_location=8,
                    detection_alpha=20)
print(f"probe: {a.n_obs} spots x {a.n_vars} genes, {mod.n_factors_} factors", flush=True)
mod.train(max_epochs=5, batch_size=4096, train_size=1, lr=0.002,
          accelerator="cpu", enable_progress_bar=False,
          enable_checkpointing=False, logger=False)
a = mod.export_posterior(a, sample_kwargs={"num_samples": 20, "batch_size": 2500,
                                           "accelerator": "cpu"},
                         use_quantiles=False)

mean_df = a.obsm["means_cell_abundance_w_sf"]
q05_df = a.obsm["q05_cell_abundance_w_sf"]
raw_mean = np.asarray(mean_df, dtype=float)
raw_q05 = np.asarray(q05_df, dtype=float)
buggy = pd.DataFrame(mean_df, index=a.obs_names,
                     columns=[f"mean_{c}" for c in mean_df.columns])
fixed = mean_df.copy()
fixed.columns = [f"mean_{c}" for c in mean_df.columns]

rows = [
    {"check": "obsm_mean_nan_fraction", "value": float(np.isnan(raw_mean).mean())},
    {"check": "obsm_mean_min", "value": float(np.nanmin(raw_mean))},
    {"check": "obsm_mean_max", "value": float(np.nanmax(raw_mean))},
    {"check": "obsm_mean_median", "value": float(np.nanmedian(raw_mean))},
    {"check": "obsm_q05_nan_fraction", "value": float(np.isnan(raw_q05).mean())},
    {"check": "buggy_construction_nan_fraction",
     "value": float(np.isnan(buggy.to_numpy(float)).mean())},
    {"check": "fixed_rename_nan_fraction",
     "value": float(np.isnan(fixed.to_numpy(float)).mean())},
    {"check": "obsm_columns", "value": ";".join(map(str, mean_df.columns))},
]
out = pd.DataFrame(rows)
out.to_csv(f"{LOGS}/c2l_export_probe_finiteness.csv", index=False)
print(out.to_string(index=False), flush=True)
log_run(step="export_probe", status="ok", wall_time_s=round(time.time() - t0, 1),
        n_cells=a.n_obs, n_genes=a.n_vars,
        detail=(f"5-epoch API probe on 3,000 spots; obsm mean NaN frac "
                f"{np.isnan(raw_mean).mean():.4f}; buggy prefixed-column construction "
                f"NaN frac {np.isnan(buggy.to_numpy(float)).mean():.4f}; fixed rename "
                f"NaN frac {np.isnan(fixed.to_numpy(float)).mean():.4f}"))
print("PROBE DONE", flush=True)
