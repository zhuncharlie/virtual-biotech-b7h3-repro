"""
Panel 4E / S5B step 3: map cell-type abundances onto the 22 Visium sections with
cell2location.

Design
------
* reference signatures: posterior MEAN of per_cluster_mu_fg from the trained
  RegressionModel (c2l_reference_celltype_signatures_mean.csv)
* single joint mapping run over all 22 sections with section as the technical
  batch (batch_key='section'). Rationale: the 22 sections are the same platform
  and protocol but differ in tissue/array; per-section detection efficiency is a
  technical nuisance, while cell abundance is the quantity of interest. Running
  one model keeps abundances comparable across sections. The graph never mixes
  sections (built per section downstream).
* N_cells_per_location = 8 (paper prior; cells per Visium spot).
* detection_alpha = 20 (cell2location default for Visium).
* posterior: num_samples=200 (CPU tractability; documented deviation from 1000),
  exporting both mean and q05 cell abundance.

Bench mode: C2L_MAP_BENCH=1 trains 1 epoch and skips export, to measure
seconds/step before committing to the production epoch count.

Outputs
-------
results/tables/visium_c2l_spot_abundances.parquet   (one row per spot)
results/tables/visium_c2l_mapping_history.csv
results/tables/visium_c2l_run_log.csv               (appended rows)
data/processed/visium_c2l_abundances_small.h5ad     (abundances only, no genes)
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
MAX_EPOCHS = int(os.environ.get("C2L_MAP_EPOCHS", "10000"))
N_SAMPLES = int(os.environ.get("C2L_MAP_SAMPLES", "200"))
BENCH = os.environ.get("C2L_MAP_BENCH", "0") == "1"
LR = 0.002
N_CELLS_PER_LOCATION = 8
DETECTION_ALPHA = 20

VIS = f"{WORK}/data/processed/visium_sections_qc.h5ad"
SIG = f"{WORK}/results/tables/c2l_reference_celltype_signatures_mean.csv"
TAB = f"{WORK}/results/tables"
PROC = f"{WORK}/data/processed"

np.random.seed(SEED)
torch.manual_seed(SEED)

from cell2location.models import Cell2location  # noqa: E402

t0 = time.time()
print(f"device={ACCEL} bench={BENCH} max_epochs={MAX_EPOCHS} batch_size={BATCH_SIZE}", flush=True)

inf_aver = pd.read_csv(SIG, index_col=0)
print("signature:", inf_aver.shape, list(inf_aver.columns), flush=True)

adata = ad.read_h5ad(VIS)
print("visium:", adata.shape, flush=True)

missing = [g for g in inf_aver.index if g not in adata.var_names]
print("signature genes missing from visium:", len(missing), missing[:10], flush=True)
pd.DataFrame({"gene_missing_from_visium": missing}).to_csv(
    f"{TAB}/visium_c2l_signature_genes_missing_from_visium.csv", index=False)
common = [g for g in inf_aver.index if g in adata.var_names]
inf_aver = inf_aver.loc[common]
print("signature genes shared with visium:", len(common), flush=True)

# keep CD276 counts / normalised expression out of the model but carry them for
# downstream stratification (extract before subsetting to the reference genes)
cd276_raw = adata[:, "CD276"].X
cd276_raw = np.asarray(cd276_raw.todense()).ravel() if hasattr(cd276_raw, "todense") else np.asarray(cd276_raw).ravel()
lognorm_cd276 = adata[:, "CD276"].layers["lognorm"]
lognorm_cd276 = np.asarray(lognorm_cd276.todense()).ravel() if hasattr(lognorm_cd276, "todense") else np.asarray(lognorm_cd276).ravel()

adata = adata[:, common].copy()                  # exact order required by cell2location
adata.X = adata.X.astype(np.float32)
adata.obs["CD276_counts"] = cd276_raw
adata.obs["CD276_lognorm"] = lognorm_cd276
print("subset:", adata.shape, flush=True)

Cell2location.setup_anndata(adata, batch_key="section")
mod = Cell2location(
    adata,
    cell_state_df=inf_aver,
    N_cells_per_location=N_CELLS_PER_LOCATION,
    detection_alpha=DETECTION_ALPHA,
)
print(f"model: N_cells_per_location={N_CELLS_PER_LOCATION} detection_alpha={DETECTION_ALPHA} "
      f"n_factors={mod.n_factors_}", flush=True)

steps_per_epoch = int(np.ceil(adata.n_obs / BATCH_SIZE))
try:
    n_epochs = 1 if BENCH else MAX_EPOCHS
    # scvi-tools 1.4 only populates model.history from a Lightning logger, so a
    # CSVLogger is used here (small, under WORK/logs) to retain the ELBO curve.
    import lightning.pytorch as pl
    csv_logger = pl.loggers.CSVLogger(save_dir=f"{WORK}/logs/lightning", name="c2l_mapping",
                                      version=f"bench{int(BENCH)}_{n_epochs}ep",
                                      flush_logs_every_n_steps=50)
    t = time.time()
    mod.train(max_epochs=n_epochs, batch_size=BATCH_SIZE, train_size=1, lr=LR,
              accelerator=ACCEL, enable_progress_bar=False,
              enable_checkpointing=False, logger=csv_logger)
    train_s = time.time() - t
    hist = pd.DataFrame(mod.history)
    hist.index.name = "epoch"
    hist = hist.dropna(how="all")
    # Never write a header-only CSV. mod.history is populated from the
    # Lightning logger and can be empty even when training succeeded; in that
    # case the per-epoch values are in the CSVLogger directory. Remove any
    # stale empty file left by an earlier run.
    hist_path = f"{TAB}/visium_c2l_mapping_history.csv"
    if len(hist):
        hist.to_csv(hist_path)
        print(f"wrote per-epoch history: {len(hist)} rows", flush=True)
    else:
        if os.path.exists(hist_path):
            os.remove(hist_path)
        print("mod.history empty; no history CSV written; see the Lightning "
              "metrics.csv under logs/lightning/c2l_mapping/", flush=True)
    epochs_completed = int(n_epochs) if hist.empty else len(hist)
    print(f"train {train_s:.1f}s for {epochs_completed} epochs; per_step={train_s/(epochs_completed*steps_per_epoch):.3f}s; "
          f"steps/epoch={steps_per_epoch}", flush=True)

    if BENCH:
        log_run(step="mapping_bench", status="ok", wall_time_s=round(time.time() - t0, 1),
                max_epochs=1, epochs_completed=1, batch_size=BATCH_SIZE, device=ACCEL,
                n_cells=adata.n_obs, n_genes=adata.n_vars,
                detail=f"1-epoch mapping benchmark; {train_s/(steps_per_epoch):.2f}s/epoch; "
                       f"{train_s/(epochs_completed*steps_per_epoch):.3f}s/step; section as batch")
        print("BENCH DONE", flush=True)
        sys.exit(0)

    t = time.time()
    adata = mod.export_posterior(
        adata,
        sample_kwargs={"num_samples": N_SAMPLES, "batch_size": 2500, "accelerator": ACCEL},
        use_quantiles=False,
    )
    export_s = time.time() - t
    print(f"posterior export {export_s:.1f}s", flush=True)

    factor_names = list(adata.uns["mod"]["factor_names"])
    mean_ab = pd.DataFrame(adata.obsm["means_cell_abundance_w_sf"], index=adata.obs_names,
                           columns=[f"mean_{c}" for c in factor_names])
    q05_ab = pd.DataFrame(adata.obsm["q05_cell_abundance_w_sf"], index=adata.obs_names,
                          columns=[f"q05_{c}" for c in factor_names])

    meta_cols = ["section", "patient", "histology", "array_row", "array_col",
                 "total_counts", "n_genes_by_counts", "qc_pass", "CD276_counts", "CD276_lognorm"]
    out = pd.concat([adata.obs[meta_cols], mean_ab, q05_ab], axis=1)
    out.index.name = "spot_barcode"
    out.to_parquet(f"{TAB}/visium_c2l_spot_abundances.parquet")
    print("spot abundances:", out.shape, flush=True)

    # compact AnnData: abundances + metadata only (no genes) for the neighbourhood step
    small = ad.AnnData(
        X=np.zeros((adata.n_obs, 1), dtype=np.float32),
        obs=out.copy(),
        var=pd.DataFrame(index=["placeholder"]),
    )
    small.obsm["spatial"] = adata.obsm["spatial"]
    small.write_h5ad(f"{PROC}/visium_c2l_abundances_small.h5ad", compression="gzip")

    log_run(step="mapping", status="ok", wall_time_s=round(time.time() - t0, 1),
            max_epochs=MAX_EPOCHS, epochs_completed=epochs_completed,
            batch_size=BATCH_SIZE, device=ACCEL, n_cells=adata.n_obs, n_genes=adata.n_vars,
            detail=(f"Cell2location section as batch; N_cells_per_location={N_CELLS_PER_LOCATION}; "
                    f"detection_alpha={DETECTION_ALPHA}; lr={LR}; train={train_s:.0f}s; "
                    f"export={export_s:.0f}s; num_samples={N_SAMPLES}; 22 sections; CPU only"))
    print("DONE", flush=True)

except Exception as e:
    import traceback
    traceback.print_exc()
    log_run(step="mapping_bench" if BENCH else "mapping", status="failed",
            wall_time_s=round(time.time() - t0, 1),
            max_epochs=1 if BENCH else MAX_EPOCHS, batch_size=BATCH_SIZE, device=ACCEL,
            n_cells=adata.n_obs, n_genes=adata.n_vars,
            detail=f"{type(e).__name__}: {str(e)[:300]}")
    raise
