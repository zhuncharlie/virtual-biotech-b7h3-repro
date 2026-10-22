"""Benchmark one cell2location optimiser step on the available hardware.

Env vars:
  C2L_THREADS   torch CPU threads (default: nproc)
  C2L_BENCH_BS  batch size (default 4096)
  C2L_ACCEL     'cuda' or 'cpu' (default: cuda if available else cpu)
  C2L_STEPS     timed optimiser steps (default 10)
"""
import os
import time
import torch

RUN = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"
WORK = f"{RUN}/work/single-cell-analyst"

print("torch", torch.__version__, "cuda available:", torch.cuda.is_available(),
      "built with cuda:", torch.backends.cuda.is_built(), flush=True)
accel = os.environ.get("C2L_ACCEL", "cuda" if torch.cuda.is_available() else "cpu")
if accel == "cuda" and not torch.cuda.is_available():
    print("CUDA requested but unavailable -> falling back to cpu", flush=True)
    accel = "cpu"
n_threads = int(os.environ.get("C2L_THREADS", str(os.cpu_count())))
torch.set_num_threads(n_threads)
print("device:", accel, "torch threads:", n_threads, "nproc:", os.cpu_count(), flush=True)

import anndata as ad  # noqa: E402
from cell2location.models import RegressionModel  # noqa: E402

ref = ad.read_h5ad(f"{WORK}/data/processed/c2l_reference_luad_normal_hvg2000.h5ad")
print("reference:", ref.shape, flush=True)
RegressionModel.setup_anndata(ref, batch_key="dataset_id", labels_key="cell_type")
t = time.time()
mod = RegressionModel(ref)
print("model init", round(time.time() - t, 1), "s", flush=True)

bs = int(os.environ.get("C2L_BENCH_BS", "4096"))
# scvi-tools 1.4 PyroSviTrainMixin no longer accepts max_steps/devices; time one
# full epoch instead. cell2location 0.1.5's train() signature is unchanged.
t = time.time()
mod.train(max_epochs=1, batch_size=bs, train_size=1, lr=0.002,
          accelerator=accel, enable_progress_bar=False,
          enable_checkpointing=False, logger=False)
dt = time.time() - t
steps_per_epoch = ref.n_obs / bs
per_step = dt / steps_per_epoch
n_steps = int(round(steps_per_epoch))
print("RESULT device=%s bs=%d steps=%d wall=%.1fs per_step=%.2fs steps_per_epoch=%.1f epoch_est=%.1fs"
      % (accel, bs, n_steps, dt, per_step, steps_per_epoch, per_step * steps_per_epoch), flush=True)

for ep in [250, 100, 50, 10000, 3000]:
    print("  projected %5d epochs: %.2f h (reference)" % (ep, per_step * steps_per_epoch * ep / 3600), flush=True)
