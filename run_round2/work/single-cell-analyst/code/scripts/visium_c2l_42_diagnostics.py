"""
Diagnostics for the cell2location panels: training ELBO convergence, deconvolution
sanity checks (abundance vs sequencing depth, abundance range, empty-spot
fraction), and a per-section abundance summary of major compartments.

Provenance of the ELBO traces
-----------------------------
* Spatial mapping: the Lightning CSVLogger wrote a per-epoch metrics file during
  the completed 3,000-epoch run. It was recovered from the interrupted source run
  and copied here as logs/c2l_mapping_elbo_metrics_3000epoch.csv
  (columns elbo_train,epoch,step; 3,000 rows).
* Reference RegressionModel: NO ELBO trace exists. scvi-tools 1.4 populates
  model.history only when a Lightning logger is attached; the reference model was
  trained with logger=False. Lightning reported `max_epochs=250 reached`, and the
  run log records 250/250 epochs / 4,586.9 s, but the loss values were never
  written. We report this as unavailable and do NOT fabricate a curve.

Outputs
-------
results/tables/visium_c2l_training_convergence.csv
results/tables/visium_c2l_abundance_sanity.csv
results/figures/figs5_c2l_training_convergence.png
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run, checked_frame  # noqa: E402

TAB = f"{WORK}/results/tables"
FIG = f"{WORK}/results/figures"
LOGS = f"{WORK}/logs"
METRICS = f"{LOGS}/c2l_mapping_elbo_metrics_3000epoch.csv"
METRICS_RERUN = f"{LOGS}/lightning/c2l_mapping_rerun/3000ep/metrics.csv"

IMMUNE = ["T cell", "B cell", "NK cell", "macrophage", "monocyte/myeloid",
          "dendritic cell", "mast cell", "neutrophil", "plasma cell"]

t0 = time.time()

# ----------------------------------------------------------- ELBO convergence
h = pd.read_csv(METRICS)
assert {"elbo_train", "epoch"}.issubset(h.columns), h.columns
h = h.sort_values("epoch").reset_index(drop=True)
n = len(h)
tail_n = max(1, n // 10)
tail = h.iloc[-tail_n:]
slope = float(np.polyfit(tail["epoch"], tail["elbo_train"], 1)[0])
elbo_first = float(h["elbo_train"].iloc[0])
elbo_last = float(h["elbo_train"].iloc[-1])
elbo_at_90 = float(h["elbo_train"].iloc[n - tail_n])
pct_decrease_by_90 = ((elbo_first - elbo_at_90) / (elbo_first - elbo_last) * 100
                      if elbo_first > elbo_last else np.nan)

def trace_stats(hist):
    hist = hist.sort_values("epoch").reset_index(drop=True)
    n_ = len(hist)
    tn = max(1, n_ // 10)
    t = hist.iloc[-tn:]
    return {
        "epochs": n_,
        "elbo_first": float(hist["elbo_train"].iloc[0]),
        "elbo_last": float(hist["elbo_train"].iloc[-1]),
        "elbo_last10pct_mean": float(t["elbo_train"].mean()),
        "elbo_last10pct_sd": float(t["elbo_train"].std()),
        "rel_change_last10pct_pct": float((t["elbo_train"].iloc[-1] -
                                           t["elbo_train"].iloc[0]) /
                                          abs(t["elbo_train"].iloc[0]) * 100),
        "last10pct_slope_per_epoch": float(
            np.polyfit(t["epoch"], t["elbo_train"], 1)[0]),
        "pct_total_decrease_by_90pct_epoch": float(
            (hist["elbo_train"].iloc[0] - t["elbo_train"].iloc[0]) /
            (hist["elbo_train"].iloc[0] - hist["elbo_train"].iloc[-1]) * 100),
    }


primary = trace_stats(h)
rows = [dict(model="spatial mapping (Cell2location), original run",
             trace_available=True, **primary,
             source_file="logs/c2l_mapping_elbo_metrics_3000epoch.csv",
             note=("Recovered per-epoch Lightning CSVLogger trace from the completed "
                   "3,000-epoch run; logger=False only affected the reference model."))]
if os.path.exists(METRICS_RERUN):
    hr = pd.read_csv(METRICS_RERUN)
    if {"elbo_train", "epoch"}.issubset(hr.columns) and len(hr):
        rr = trace_stats(hr)
        rows.append(dict(
            model="spatial mapping, re-run (corrected export)", trace_available=True,
            **rr, source_file="logs/lightning/c2l_mapping_rerun/3000ep/metrics.csv",
            note=("Re-run with identical configuration after the all-NaN export "
                  f"defect; final ELBO differs from the original by "
                  f"{100*(rr['elbo_last']-primary['elbo_last'])/abs(primary['elbo_last']):+.2f}%.")))
        hrerun = hr.sort_values("epoch").reset_index(drop=True)
    else:
        hrerun = None
else:
    hrerun = None
rows.append({
    "model": "reference (RegressionModel)",
    "trace_available": False,
    "epochs": 250,
    "elbo_first": np.nan,
    "elbo_last": np.nan,
    "elbo_last10pct_mean": np.nan,
    "elbo_last10pct_sd": np.nan,
    "rel_change_last10pct_pct": np.nan,
    "last10pct_slope_per_epoch": np.nan,
    "pct_total_decrease_by_90pct_epoch": np.nan,
    "source_file": "",
    "note": ("UNAVAILABLE. 250/250 epochs completed (Lightning 'max_epochs=250 "
             "reached'; 4,586.9 s, 18.3 s/epoch) but scvi-tools 1.4 populates "
             "model.history only with a Lightning logger attached; logger=False "
             "was used. No loss values were written; no curve is fabricated."),
})
CONV_COLS = ["model", "trace_available", "epochs", "elbo_first", "elbo_last",
             "elbo_last10pct_mean", "elbo_last10pct_sd",
             "rel_change_last10pct_pct", "last10pct_slope_per_epoch",
             "pct_total_decrease_by_90pct_epoch", "source_file", "note"]
conv = checked_frame(rows, CONV_COLS, "visium_c2l_training_convergence")
assert len(conv) >= 2, "convergence table must contain mapping + reference rows"
conv.to_csv(f"{TAB}/visium_c2l_training_convergence.csv", index=False)
print(conv.to_string(index=False), flush=True)

fig, axes = plt.subplots(1, 2, figsize=(11, 3.9))
ax = axes[0]
ax.plot(h["epoch"], h["elbo_train"] / 1e6, color="#d62728", lw=1.2,
        label="original run (recovered)")
if hrerun is not None:
    ax.plot(hrerun["epoch"], hrerun["elbo_train"] / 1e6, color="black", lw=0.7,
            ls="--", alpha=0.8, label="re-run (corrected export)")
    ax.legend(fontsize=6.5, frameon=False, loc="upper right")
ax.set_xlabel("epoch"); ax.set_ylabel("ELBO (train, x1e6)")
ax.set_title(f"spatial mapping (Cell2location), {n:,} epochs", fontsize=9)
ax.annotate(f"start {elbo_first/1e6:,.1f}M\nend {elbo_last/1e6:,.1f}M\n"
            f"total decrease {100*(elbo_first-elbo_last)/abs(elbo_first):.1f}%",
            xy=(0.03, 0.05), xycoords="axes fraction", fontsize=7, va="bottom")

ax = axes[1]
ax.plot(tail["epoch"], tail["elbo_train"] / 1e6, color="#d62728", lw=1, label="ELBO")
xf = tail["epoch"].to_numpy(float)
yf = tail["elbo_train"].to_numpy(float) / 1e6
ax.plot(xf, np.polyval(np.polyfit(xf, yf, 1), xf), color="black", lw=1, ls="--",
        label=f"linear fit: {slope/1e6:+.4f}M/epoch")
ax.set_xlabel("epoch"); ax.set_ylabel("ELBO (train, x1e6)")
ax.set_title("last 10% of mapping epochs (tail flatness)", fontsize=9)
ax.legend(fontsize=7, frameon=False, loc="upper right")
ax.text(0.02, 0.04,
        "Reference RegressionModel ELBO trace: UNAVAILABLE\n"
        "(scvi-tools 1.4 logger=False; history empty; 250/250 epochs done)",
        transform=ax.transAxes, fontsize=6.5, color="#555", va="bottom")
for a in axes:
    for s in ["top", "right"]:
        a.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(f"{FIG}/figs5_c2l_training_convergence.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# --------------------------------------------------------------- sanity table
df = pd.read_parquet(f"{TAB}/visium_c2l_spot_abundances.parquet")
cell_types = [c.replace("mean_", "") for c in df.columns if c.startswith("mean_")]
mean_cols = [f"mean_{c}" for c in cell_types]
tot = df[mean_cols].sum(axis=1)
imm = df[[f"mean_{c}" for c in IMMUNE]].sum(axis=1)
sanity = [
    {"metric": "n_spots", "value": len(df)},
    {"metric": "spearman_total_abundance_vs_total_counts",
     "value": float(tot.corr(df["total_counts"], method="spearman"))},
    {"metric": "spearman_immune_abundance_vs_total_counts",
     "value": float(imm.corr(df["total_counts"], method="spearman"))},
    {"metric": "spearman_total_abundance_vs_n_genes",
     "value": float(tot.corr(df["n_genes_by_counts"], method="spearman"))},
    {"metric": "median_total_abundance_per_spot", "value": float(tot.median())},
    {"metric": "median_immune_abundance_per_spot", "value": float(imm.median())},
    {"metric": "pct_spots_total_abundance_below_1", "value": float((tot < 1).mean() * 100)},
    {"metric": "pct_spots_immune_abundance_below_1", "value": float((imm < 1).mean() * 100)},
    {"metric": "pct_spots_CD276_counts_zero", "value": float((df["CD276_counts"] == 0).mean() * 100)},
    {"metric": "pct_spots_CD276_lognorm_zero", "value": float((df["CD276_lognorm"] == 0).mean() * 100)},
    {"metric": "median_CD276_lognorm_positive_spots",
     "value": float(df.loc[df["CD276_counts"] > 0, "CD276_lognorm"].median())},
    {"metric": "max_CD276_lognorm", "value": float(df["CD276_lognorm"].max())},
]
san = checked_frame(sanity, ["metric", "value"],
                    "visium_c2l_abundance_sanity")
san.to_csv(f"{TAB}/visium_c2l_abundance_sanity.csv", index=False)
print(san.to_string(index=False), flush=True)

log_run(step="diagnostics", status="ok", wall_time_s=round(time.time() - t0, 1),
        n_cells=len(df), detail=(f"mapping ELBO recovered ({n} epochs, "
                                 f"{elbo_first:,.0f}->{elbo_last:,.0f}); reference ELBO "
                                 f"unavailable (logger=False); sanity metrics written"))
print("DONE", flush=True)
