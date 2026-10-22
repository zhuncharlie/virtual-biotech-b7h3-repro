"""
Panel 4E / S5B step 3 (RE-RUN after an output-formatting defect): map cell-type
abundances onto the 22 Visium sections with cell2location.

Why this file exists
--------------------
The first 3,000-epoch mapping run (2026-10-21 15:08) trained successfully
(ELBO 104,060,600 -> 38,571,652) but its stored abundance tables are 100% NaN.
The cause is NOT the model: the export code built the output with

    pd.DataFrame(adata.obsm["means_cell_abundance_w_sf"],
                 index=adata.obs_names, columns=[f"mean_{c}" for c in factor_names])

The obsm DataFrame's columns are bare cell-type names, so the prefixed names
were interpreted as column SELECTION, not renaming, and every column became NaN.
A 5-epoch probe (visium_c2l_22_export_probe.py) shows obsm values are finite
(NaN fraction 0.0), the buggy construction gives NaN fraction 1.0, and a plain
rename gives 0.0. No checkpoint was saved (`enable_checkpointing=False`), so the
posterior cannot be re-exported; the mapping must be re-run. The configuration
here is identical to the original (3,000 epochs, batch 4096, lr 0.002,
N_cells_per_location=8, detection_alpha=20, section as batch, num_samples=200).
Only the export/validation code is corrected, and the model is saved so this
cannot happen again.

Outputs
-------
results/tables/visium_c2l_spot_abundances.parquet   (validated, overwritten)
data/processed/visium_c2l_abundances_small.h5ad     (validated, overwritten)
data/processed/c2l_mapping_model_rerun/             (saved model, audit)
logs/lightning/c2l_mapping_rerun/.../metrics.csv    (per-epoch ELBO)
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
ACCEL = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = int(os.environ.get("C2L_MAP_BS", "4096"))
MAX_EPOCHS = int(os.environ.get("C2L_MAP_EPOCHS", "3000"))
N_SAMPLES = int(os.environ.get("C2L_MAP_SAMPLES", "200"))
LR = 0.002
N_CELLS_PER_LOCATION = 8
DETECTION_ALPHA = 20

SIG = f"{WORK}/results/tables/c2l_reference_celltype_signatures_mean.csv"
TAB = f"{WORK}/results/tables"
PROC = f"{WORK}/data/processed"
# Self-contained: the QC h5ad is copied into this run (450 MB; byte-identical
# to the SOURCE copy, md5 a9066b064a85bc24cf710d7fba31e5db). No cross-run path.
VIS = f"{PROC}/visium_sections_qc.h5ad"
if not os.path.exists(VIS):
    raise FileNotFoundError(f"Visium QC input missing from LIVE run: {VIS}")
MODEL_DIR = f"{PROC}/c2l_mapping_model_rerun"

np.random.seed(SEED)
torch.manual_seed(SEED)

from cell2location.models import Cell2location  # noqa: E402

t0 = time.time()
print(f"device={ACCEL} max_epochs={MAX_EPOCHS} batch_size={BATCH_SIZE}", flush=True)
log_run(step="mapping_rerun", status="started", max_epochs=MAX_EPOCHS,
        batch_size=BATCH_SIZE, device=ACCEL, n_cells=47448, n_genes=1926,
        detail=("Re-run forced by all-NaN stored abundances: output builder used "
                "prefixed column names as selection labels. Identical model config; "
                "only export fixed; model now saved."))

inf_aver = pd.read_csv(SIG, index_col=0)
adata = ad.read_h5ad(VIS)
missing = [g for g in inf_aver.index if g not in adata.var_names]
print("signature genes missing from visium:", len(missing), flush=True)
pd.DataFrame({"gene_missing_from_visium": missing}).to_csv(
    f"{TAB}/visium_c2l_signature_genes_missing_from_visium.csv", index=False)
common = [g for g in inf_aver.index if g in adata.var_names]
inf_aver = inf_aver.loc[common]
print("signature genes shared with visium:", len(common), flush=True)

cd276_raw = adata[:, "CD276"].X
cd276_raw = (np.asarray(cd276_raw.todense()).ravel()
             if hasattr(cd276_raw, "todense") else np.asarray(cd276_raw).ravel())
lognorm_cd276 = adata[:, "CD276"].layers["lognorm"]
lognorm_cd276 = (np.asarray(lognorm_cd276.todense()).ravel()
                 if hasattr(lognorm_cd276, "todense")
                 else np.asarray(lognorm_cd276).ravel())

adata = adata[:, common].copy()
adata.X = adata.X.astype(np.float32)
adata.obs["CD276_counts"] = cd276_raw
adata.obs["CD276_lognorm"] = lognorm_cd276
print("subset:", adata.shape, flush=True)

Cell2location.setup_anndata(adata, batch_key="section")
mod = Cell2location(adata, cell_state_df=inf_aver,
                    N_cells_per_location=N_CELLS_PER_LOCATION,
                    detection_alpha=DETECTION_ALPHA)
print(f"model: N_cells_per_location={N_CELLS_PER_LOCATION} "
      f"detection_alpha={DETECTION_ALPHA} n_factors={mod.n_factors_}", flush=True)

steps_per_epoch = int(np.ceil(adata.n_obs / BATCH_SIZE))
import lightning.pytorch as pl  # noqa: E402
csv_logger = pl.loggers.CSVLogger(save_dir=f"{WORK}/logs/lightning",
                                  name="c2l_mapping_rerun",
                                  version=f"{MAX_EPOCHS}ep",
                                  flush_logs_every_n_steps=50)
t = time.time()
mod.train(max_epochs=MAX_EPOCHS, batch_size=BATCH_SIZE, train_size=1, lr=LR,
          accelerator=ACCEL, enable_progress_bar=False,
          enable_checkpointing=False, logger=csv_logger)
train_s = time.time() - t
hist = pd.DataFrame(mod.history)
hist.index.name = "epoch"
hist = hist.dropna(how="all")
# mod.history is empty in scvi-tools 1.4 even with a CSVLogger attached (the
# per-epoch values go to the Lightning log). Writing it unconditionally produced
# a 6-byte header-only CSV that looked like an output; only write when there is
# at least one non-empty row, remove any stale empty file, and point at the real
# trace otherwise. See results/tables/visium_c2l_mapping_history_README.md.
hist_path = f"{TAB}/visium_c2l_mapping_history_rerun.csv"
if len(hist):
    hist.to_csv(hist_path)
    print(f"wrote per-epoch history: {len(hist)} rows", flush=True)
else:
    if os.path.exists(hist_path):
        os.remove(hist_path)
    print("mod.history empty; no history CSV written; per-epoch ELBO is in "
          "the Lightning metrics.csv under logs/lightning/c2l_mapping_rerun/",
          flush=True)
epochs_completed = int(MAX_EPOCHS) if hist.empty else len(hist)
print(f"train {train_s:.1f}s for {epochs_completed} epochs; "
      f"per_step={train_s/(epochs_completed*steps_per_epoch):.3f}s; "
      f"steps/epoch={steps_per_epoch}", flush=True)

t = time.time()
adata = mod.export_posterior(
    adata,
    sample_kwargs={"num_samples": N_SAMPLES, "batch_size": 2500,
                   "accelerator": ACCEL},
    use_quantiles=False,
)
export_s = time.time() - t
print(f"posterior export {export_s:.1f}s", flush=True)

factor_names = list(adata.uns["mod"]["factor_names"])
mean_df = adata.obsm["means_cell_abundance_w_sf"].copy()
q05_df = adata.obsm["q05_cell_abundance_w_sf"].copy()
# CORRECT construction: rename existing columns; do NOT pass them as `columns=`.
mean_df.columns = [f"mean_{c}" for c in factor_names]
q05_df.columns = [f"q05_{c}" for c in factor_names]

raw_mean = np.asarray(mean_df, dtype=float)
raw_q05 = np.asarray(q05_df, dtype=float)
print("mean nan frac", float(np.isnan(raw_mean).mean()),
      "min", float(np.nanmin(raw_mean)), "max", float(np.nanmax(raw_mean)), flush=True)
print("q05 nan frac", float(np.isnan(raw_q05).mean()), flush=True)
if not np.isfinite(raw_mean).all() or not np.isfinite(raw_q05).all():
    raise RuntimeError("Posterior export still contains non-finite abundances; refusing to write.")
if raw_mean.max() <= 0:
    raise RuntimeError("Posterior export is all-zero; refusing to write.")

meta_cols = ["section", "patient", "histology", "array_row", "array_col",
             "total_counts", "n_genes_by_counts", "qc_pass", "CD276_counts",
             "CD276_lognorm"]
out = pd.concat([adata.obs[meta_cols], mean_df, q05_df], axis=1)
out.index.name = "spot_barcode"
out.to_parquet(f"{TAB}/visium_c2l_spot_abundances.parquet")
print("spot abundances:", out.shape, flush=True)

small = ad.AnnData(
    X=np.zeros((adata.n_obs, 1), dtype=np.float32),
    obs=out.copy(),
    var=pd.DataFrame(index=["placeholder"]),
)
small.obsm["spatial"] = adata.obsm["spatial"]
small.write_h5ad(f"{PROC}/visium_c2l_abundances_small.h5ad", compression="gzip")

t = time.time()
try:
    mod.save(MODEL_DIR, overwrite=True)
    print(f"model saved to {MODEL_DIR} in {time.time()-t:.1f}s", flush=True)
    model_saved = True
except Exception as e:
    # The validated abundance tables are already written; a save failure is an
    # audit inconvenience, not a reason to discard a completed mapping.
    model_saved = False
    print(f"WARNING: model save failed: {type(e).__name__}: {e}", flush=True)
    log_run(step="mapping_rerun_model_save", status="failed",
            wall_time_s=round(time.time() - t, 1),
            detail=f"{type(e).__name__}: {str(e)[:300]}")

log_run(step="mapping_rerun", status="ok", wall_time_s=round(time.time() - t0, 1),
        max_epochs=MAX_EPOCHS, epochs_completed=epochs_completed,
        batch_size=BATCH_SIZE, device=ACCEL, n_cells=adata.n_obs, n_genes=adata.n_vars,
        detail=(f"Identical configuration to original mapping; FIXED export. "
                f"train={train_s:.0f}s; export={export_s:.0f}s; num_samples={N_SAMPLES}; "
                f"mean abundance min={raw_mean.min():.3f} max={raw_mean.max():.2f} "
                f"nan_frac=0; model_saved={model_saved}"))
print("DONE", flush=True)
