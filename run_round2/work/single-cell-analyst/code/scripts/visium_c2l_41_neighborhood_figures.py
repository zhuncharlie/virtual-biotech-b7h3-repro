"""
Neighbourhood-analysis figures for Panel 4E (tumour) and S5B (adjacent-normal).

A  pooled percent change in neighbourhood immune abundance around B7-H3-high vs
   B7-H3-low spots, with section-bootstrap 95% CI.
B  per-section percent change (dots) with the pooled value (bar); shows
   direction consistency.
C  pooled per-donor percent change (sum of high-minus-low over sum of low),
   matching the `donor_pct_changes` column of visium_neighborhood_robustness.csv.
   (The earlier version plotted the unweighted mean of per-section percent
   changes, a different estimator that did not reconcile with the table.)

Outputs
-------
results/figures/fig4e_neighborhood_immune_change.png/.pdf
results/figures/figs5b_neighborhood_immune_change.png/.pdf
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run  # noqa: E402

T0 = time.time()

TAB = os.environ.get("C2L_TAB_DIR", f"{WORK}/results/tables")
FIG = os.environ.get("C2L_FIG_DIR", f"{WORK}/results/figures")
RUN_STATUS = os.environ.get("C2L_STATUS", "ok")

IMMUNE = ["T cell", "B cell", "NK cell", "macrophage", "monocyte/myeloid",
          "dendritic cell", "mast cell", "neutrophil", "plasma cell"]
CONTEXT = ["fibroblast", "epithelial cell", "endothelial cell"]

per_sec = pd.read_csv(f"{TAB}/visium_neighborhood_immune_change.csv")
robust = pd.read_csv(f"{TAB}/visium_neighborhood_robustness.csv")

REQUIRED_PER_SEC = ["section", "patient", "histology", "cell_type", "n_high",
                    "n_low", "mean_neighbor_high", "mean_neighbor_low",
                    "pct_change"]
REQUIRED_ROBUST = ["histology", "metric", "cell_type", "immune_compartment",
                   "pooled_pct_change", "bootstrap_ci_low", "bootstrap_ci_high",
                   "permutation_p"]
for _name, _df, _cols in [("visium_neighborhood_immune_change", per_sec, REQUIRED_PER_SEC),
                          ("visium_neighborhood_robustness", robust, REQUIRED_ROBUST)]:
    assert _df.notna().any().any(), f"{_name}: all values NaN"
    missing = [c for c in _cols if c not in _df.columns]
    assert not missing, f"{_name}: missing columns {missing}"


def make_figure(histology, outbase, title):
    r = robust[(robust.histology == histology) & (robust.metric == "mean")].copy()
    order = [c for c in IMMUNE + CONTEXT if c in set(r.cell_type)]
    r = r.set_index("cell_type").loc[order].reset_index()
    ps = per_sec[per_sec.histology == histology]

    fig = plt.figure(figsize=(13, 8.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], height_ratios=[1, 1],
                          hspace=0.35, wspace=0.3)

    # A: pooled effect with CI
    ax = fig.add_subplot(gs[:, 0])
    y = np.arange(len(r))[::-1]
    # Two independent visual dimensions so the legend cannot conflate them:
    #   fill colour  = compartment (red immune, blue context)
    #   solid/hatched = CI excludes zero / CI includes zero
    face, edge, hatch = [], [], []
    for _, row in r.iterrows():
        sig = np.isfinite(row["bootstrap_ci_low"]) and (
            row["bootstrap_ci_low"] > 0 or row["bootstrap_ci_high"] < 0)
        base = "#c0392b" if row.immune_compartment == "immune" else "#2471a3"
        face.append(base if sig else "white")
        edge.append(base)
        hatch.append("" if sig else "///")
    ax.barh(y, r["pooled_pct_change"], color=face, edgecolor=edge,
            hatch=hatch, linewidth=0.8, height=0.7)
    ax.errorbar(r["pooled_pct_change"], y,
                xerr=[r["pooled_pct_change"] - r["bootstrap_ci_low"],
                      r["bootstrap_ci_high"] - r["pooled_pct_change"]],
                fmt="none", ecolor="black", elinewidth=1, capsize=2)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{c}  (p={p:.3f})" if np.isfinite(p) else c
                        for c, p in zip(r.cell_type, r.permutation_p)], fontsize=8)
    ax.set_xlabel("% change in mean neighbour abundance\n(B7-H3-high vs B7-H3-low spots)", fontsize=9)
    ax.set_title("A  pooled effect (section-cluster bootstrap 95% CI)", fontsize=10, loc="left")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.legend(handles=[
        Patch(facecolor="#c0392b", edgecolor="#c0392b", label="immune, CI excludes 0"),
        Patch(facecolor="#2471a3", edgecolor="#2471a3", label="context, CI excludes 0"),
        Patch(facecolor="white", edgecolor="#c0392b", hatch="///",
              label="immune, CI includes 0"),
        Patch(facecolor="white", edgecolor="#2471a3", hatch="///",
              label="context, CI includes 0"),
    ], loc="lower right", fontsize=6.5, frameon=False, handlelength=1.6)

    # B: per-section dots
    ax = fig.add_subplot(gs[0, 1])
    x = np.arange(len(order))
    for i, ct in enumerate(order):
        vals = ps[ps.cell_type == ct]["pct_change"].dropna().to_numpy()
        jitter = np.random.default_rng(0).normal(0, 0.06, len(vals))
        ax.scatter(np.full(len(vals), i) + jitter, vals, s=12, alpha=0.7,
                   color="#c0392b" if ct in IMMUNE else "#7f8c8d")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(order, rotation=60, ha="right", fontsize=7)
    ax.set_ylabel("% change per section", fontsize=8)
    ax.set_title("B  per-section direction", fontsize=10, loc="left")
    ax.set_ylim(-100, 100)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

    # C: pooled per-donor ratio, matching robustness.donor_pct_changes.
    #   ratio_d = 100 * sum_sections(mean_hi*n_hi - mean_lo*n_lo)
    #                   / sum_sections(mean_lo*n_lo)
    ax = fig.add_subplot(gs[1, 1])
    dnames = sorted(ps["patient"].unique())
    for i, ct in enumerate(order):
        vals = []
        for d in dnames:
            sub = ps[(ps.cell_type == ct) & (ps.patient == d)]
            if len(sub):
                num = ((sub["mean_neighbor_high"] * sub["n_high"])
                       - (sub["mean_neighbor_low"] * sub["n_low"])).sum()
                den = (sub["mean_neighbor_low"] * sub["n_low"]).sum()
                vals.append(num / den * 100 if den > 0 else np.nan)
            else:
                vals.append(np.nan)
        ax.plot(np.arange(len(dnames)), vals, marker="o", ms=4, lw=1,
                label=ct, color="#c0392b" if ct in IMMUNE else "#2471a3",
                alpha=0.8)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(np.arange(len(dnames)))
    ax.set_xticklabels(dnames, fontsize=8)
    ax.set_ylabel("pooled % change per donor\n(sum high-low / sum low)", fontsize=8)
    ax.set_title("C  per-donor direction (pooled ratio)", fontsize=10, loc="left")
    ax.set_ylim(-100, 100)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

    fig.suptitle(title, fontsize=12, fontweight="bold")
    fig.savefig(f"{FIG}/{outbase}.png", dpi=250, bbox_inches="tight")
    fig.savefig(f"{FIG}/{outbase}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("saved", outbase, flush=True)


make_figure("tumor", "fig4e_neighborhood_immune_change",
            "Figure 4E - immune neighbourhood of B7-H3-high vs B7-H3-low spots (LUAD tumour)")
make_figure("adjacent-normal", "figs5b_neighborhood_immune_change",
            "Figure S5B - immune neighbourhood of B7-H3-high vs B7-H3-low spots (adjacent normal)")

log_run(step=("neighborhood_figures" if RUN_STATUS == "ok"
              else "neighborhood_figures_synthetic_test"),
        status=RUN_STATUS, wall_time_s=round(time.time() - T0, 1),
        detail=("fig4e_neighborhood_immune_change + figs5b_neighborhood_immune_change "
                "(.png/.pdf)"))
print("DONE", flush=True)
