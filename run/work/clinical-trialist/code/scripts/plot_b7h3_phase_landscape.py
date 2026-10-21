#!/usr/bin/env python3
"""Plot the B7-H3 trial phase distribution for SCLC-contributing and NSCLC
context trials. LUAD-specific trials = 0 (no bar)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RUN = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
           "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/clinical-trialist")
df = pd.read_csv(RUN / "results" / "tables" / "b7h3_luad_sclc_trials.csv")

phase_map = {
    "PHASE3": "Phase 3",
    "PHASE2/PHASE3": "Phase 2/3",
    "PHASE2": "Phase 2",
    "PHASE1/PHASE2": "Phase 1/2",
    "PHASE1": "Phase 1",
    "EARLY_PHASE1": "Early Phase 1",
}
df["phase_cat"] = df["phase"].map(phase_map)
phase_order = ["Early Phase 1", "Phase 1", "Phase 1/2", "Phase 2", "Phase 2/3", "Phase 3"]

sclc = df[df.scope.isin(["SCLC-specific", "SCLC cohort (pan-tumor)"])].copy()
nsclc = df[df.scope == "NSCLC context (not LUAD-specific)"].copy()

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), sharey=True)
colors = {"SCLC-specific": "#1f4e79", "SCLC cohort (pan-tumor)": "#6fa8dc"}

for ax, sub, title, stacked in [
    (axes[0], sclc, "SCLC-contributing trials (n=26)", True),
    (axes[1], nsclc, "NSCLC context trials (n=16)\nno LUAD-specific trial identified", False),
]:
    if stacked:
        pivot = (sub.groupby(["phase_cat", "scope"]).size()
                 .unstack(fill_value=0).reindex(phase_order, fill_value=0))
        bottom = pd.Series(0, index=pivot.index)
        for scope in ["SCLC-specific", "SCLC cohort (pan-tumor)"]:
            if scope in pivot:
                ax.bar(pivot.index, pivot[scope], bottom=bottom,
                       color=colors[scope], label=scope, edgecolor="white")
                bottom = bottom + pivot[scope]
    else:
        counts = sub.groupby("phase_cat").size().reindex(phase_order, fill_value=0)
        ax.bar(counts.index, counts.values, color="#8c8c8c", edgecolor="white")
    ax.set_title(title, fontsize=10)
    ax.set_ylabel("Number of trials" if ax is axes[0] else "")
    ax.tick_params(axis="x", rotation=35)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

axes[0].legend(frameon=False, fontsize=8, loc="upper left")
fig.suptitle("B7-H3 (CD276) lung-cancer trial landscape by phase (ClinicalTrials.gov, 2026-10-20)",
             fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.93])
for ext in ("png", "pdf"):
    fig.savefig(RUN / "results" / "figures" / f"b7h3_phase_landscape.{ext}", dpi=200)
print("wrote b7h3_phase_landscape.png/pdf")
print("SCLC phase counts:\n", sclc.phase_cat.value_counts().to_string())
print("NSCLC phase counts:\n", nsclc.phase_cat.value_counts().to_string())
