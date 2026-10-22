"""
Panel 4E / S5B step 2: train the cell2location reference (RegressionModel) on
the LUAD + adjacent-normal single-cell reference and export the cell-type
expression signatures needed for spatial mapping.

Paper configuration: 250 epochs. Hardware here is CPU-only (package installation
is blocked by the environment policy), measured throughput 0.24 s/step,
23 s/epoch -> 250 epochs is ~1.6 h, so the paper epoch count is retained.

Outputs (small only; no model checkpoint is written):
  results/tables/c2l_reference_celltype_signatures_mean.csv   (genes x cell types)
  results/tables/c2l_reference_training_history.csv           (ELBO per epoch)
  results/tables/visium_c2l_run_log.csv                       (appended row)
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
MAX_EPOCHS = int(os.environ.get("C2L_REF_EPOCHS", "250"))
BATCH_SIZE = int(os.environ.get("C2L_REF_BS", "4096"))
LR = 0.002
N_SAMPLES = int(os.environ.get("C2L_REF_SAMPLES", "100"))
ACCEL = "cuda" if torch.cuda.is_available() else "cpu"

REF = f"{WORK}/data/processed/c2l_reference_luad_normal_hvg2000.h5ad"
TAB = f"{WORK}/results/tables"

np.random.seed(SEED)
torch.manual_seed(SEED)

from cell2location.models import RegressionModel  # noqa: E402

t0 = time.time()
print(f"device={ACCEL} max_epochs={MAX_EPOCHS} batch_size={BATCH_SIZE}", flush=True)
ref = ad.read_h5ad(REF)
print("reference:", ref.shape, flush=True)

RegressionModel.setup_anndata(ref, batch_key="dataset_id", labels_key="cell_type")
mod = RegressionModel(ref)
n_epochs = MAX_EPOCHS

try:
    t = time.time()
    mod.train(max_epochs=n_epochs, batch_size=BATCH_SIZE, train_size=1, lr=LR,
              accelerator=ACCEL, enable_progress_bar=False,
              enable_checkpointing=False, logger=False)
    train_s = time.time() - t
    print(f"training finished in {train_s:.1f}s", flush=True)

    hist = pd.DataFrame(mod.history)
    hist.index.name = "epoch"
    hist = hist.dropna(how="all")
    # mod.history is empty in scvi-tools 1.4 when the model is trained with
    # logger=False. Never write a header-only CSV that looks like a result:
    # write only when there is at least one non-empty row, and remove any
    # stale empty file left by an earlier run.
    hist_path = f"{TAB}/c2l_reference_training_history.csv"
    if len(hist):
        hist.to_csv(hist_path)
        print(f"wrote per-epoch history: {len(hist)} rows", flush=True)
    else:
        if os.path.exists(hist_path):
            os.remove(hist_path)
        print("mod.history empty; no history CSV written (logger=False; "
              "reference ELBO unavailable)", flush=True)
    epochs_completed = len(hist) if len(hist) else int(n_epochs)
    final_elbo = float(hist["elbo_train"].iloc[-1]) if "elbo_train" in hist else np.nan
    print("epochs completed:", epochs_completed, "final elbo_train:", final_elbo, flush=True)

    t = time.time()
    ref = mod.export_posterior(
        ref,
        sample_kwargs={"num_samples": N_SAMPLES, "batch_size": 2500,
                       "accelerator": ACCEL},
        use_quantiles=False,
    )
    sample_s = time.time() - t
    print(f"posterior export {sample_s:.1f}s", flush=True)

    factor_names = ref.uns["mod"]["factor_names"]
    inf_aver = ref.varm["means_per_cluster_mu_fg"][
        [f"means_per_cluster_mu_fg_{i}" for i in factor_names]
    ].copy()
    inf_aver.columns = factor_names
    inf_aver.index.name = "gene"
    inf_aver.to_csv(f"{TAB}/c2l_reference_celltype_signatures_mean.csv")
    print("signatures:", inf_aver.shape, flush=True)

    # also keep the q05 signature so the mapping sensitivity (q05 vs mean) can be
    # run without retraining
    inf_q05 = ref.varm["q05_per_cluster_mu_fg"][
        [f"q05_per_cluster_mu_fg_{i}" for i in factor_names]
    ].copy()
    inf_q05.columns = factor_names
    inf_q05.index.name = "gene"
    inf_q05.to_csv(f"{TAB}/c2l_reference_celltype_signatures_q05.csv")

    log_run(step="reference_train", status="ok",
            wall_time_s=round(time.time() - t0, 1),
            max_epochs=MAX_EPOCHS, epochs_completed=epochs_completed,
            batch_size=BATCH_SIZE, device=ACCEL,
            n_cells=ref.n_obs, n_genes=ref.n_vars,
            detail=(f"RegressionModel batch_key=dataset_id labels_key=cell_type; "
                    f"lr={LR}; train={train_s:.0f}s; posterior_export={sample_s:.0f}s; "
                    f"num_samples={N_SAMPLES}; final_elbo_train={final_elbo:.1f}; "
                    f"CPU only (pip install blocked)"))
    print("DONE", flush=True)

except Exception as e:
    import traceback
    traceback.print_exc()
    log_run(step="reference_train", status="failed",
            wall_time_s=round(time.time() - t0, 1),
            max_epochs=MAX_EPOCHS, batch_size=BATCH_SIZE, device=ACCEL,
            n_cells=ref.n_obs, n_genes=ref.n_vars,
            detail=f"{type(e).__name__}: {str(e)[:300]}")
    raise
