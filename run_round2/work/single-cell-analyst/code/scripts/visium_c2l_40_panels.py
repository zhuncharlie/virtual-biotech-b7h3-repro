"""
Panel 4E (tumour) and S5B (adjacent-normal) figures from the cell2location
spot abundances, plus the section-level summary table.

Figure 4E  : 12 LUAD tumour sections. Spatial maps of CD276, total immune,
             T cell, macrophage and fibroblast abundance for a representative
             section; small-multiple total-immune maps for all 12 sections; and
             per-section cell-type composition.
Figure S5B : the same layout for the 10 matched adjacent-normal sections.

Outputs
-------
results/tables/visium_c2l_section_summary.csv
results/figures/fig4e_c2l_tumor.png/.pdf
results/figures/figs5b_c2l_adjacent_normal.png/.pdf
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import anndata as ad

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run, checked_frame  # noqa: E402

T0 = time.time()

# Overridable so the plotting path can be exercised on synthetic data without
# writing mock figures into the canonical results directory.
TAB = os.environ.get("C2L_TAB_DIR", f"{WORK}/results/tables")
FIG = os.environ.get("C2L_FIG_DIR", f"{WORK}/results/figures")
PROC = f"{WORK}/data/processed"
SMALL = os.environ.get("C2L_SMALL_H5AD", f"{PROC}/visium_c2l_abundances_small.h5ad")
RUN_STATUS = os.environ.get("C2L_STATUS", "ok")

IMMUNE = ["T cell", "B cell", "NK cell", "macrophage", "monocyte/myeloid",
          "dendritic cell", "mast cell", "neutrophil", "plasma cell"]
OTHER = ["epithelial cell", "malignant cell", "fibroblast", "endothelial cell", "stromal/other"]

COMP_COLORS = {
    "T cell": "#1f77b4", "B cell": "#aec7e8", "NK cell": "#17becf",
    "macrophage": "#d62728", "monocyte/myeloid": "#ff9896",
    "dendritic cell": "#9467bd", "mast cell": "#8c564b",
    "neutrophil": "#e377c2", "plasma cell": "#bcbd22",
    "epithelial cell": "#2ca02c", "malignant cell": "#98df8a",
    "fibroblast": "#ff7f0e", "endothelial cell": "#c49c94", "stromal/other": "#7f7f7f",
}

small = ad.read_h5ad(SMALL)
obs = small.obs.copy()
xy = small.obsm["spatial"]
cell_types = [c.replace("mean_", "") for c in obs.columns if c.startswith("mean_")]
print("cell types:", cell_types, flush=True)
# Fail fast if the abundance export is empty or has been mis-shaped: the
# figures and the section summary silently become meaningless otherwise.
assert len(cell_types) == 14, (
    f"expected 14 deconvolved compartments in the h5ad, got {len(cell_types)}: "
    f"{cell_types}")
ab_cols = [f"mean_{c}" for c in cell_types]
assert obs[ab_cols].notna().any().any(), "all abundance columns are NaN"
assert np.isfinite(obs[ab_cols].to_numpy(float)).all(), (
    "non-finite values in abundance columns")
assert sorted(cell_types) == sorted(set(cell_types)), "duplicate cell-type columns"
assert obs["section"].nunique() == 22, obs["section"].nunique()

obs["total_abundance"] = obs[[f"mean_{c}" for c in cell_types]].sum(axis=1)
obs["immune_abundance"] = obs[[f"mean_{c}" for c in IMMUNE if f"mean_{c}" in obs]].sum(axis=1)
obs["fibroblast_abundance"] = obs["mean_fibroblast"] if "mean_fibroblast" in obs else 0.0
obs["T_cell_abundance"] = obs["mean_T cell"]
obs["macrophage_abundance"] = obs["mean_macrophage"]
obs = obs.loc[small.obs_names]
obs["x"] = xy[:, 0]
obs["y"] = xy[:, 1]

# ------------------------------------------------------------ section summary
rows = []
for sec, sub in obs.groupby("section"):
    row = {"section": sec, "patient": sub["patient"].iloc[0],
           "histology": sub["histology"].iloc[0], "n_spots": len(sub),
           "mean_total_abundance": sub["total_abundance"].mean(),
           "mean_immune_abundance": sub["immune_abundance"].mean(),
           "mean_CD276_lognorm": sub["CD276_lognorm"].mean(),
           "pct_spots_CD276_positive": (sub["CD276_lognorm"] > 0).mean() * 100,
           "mean_CD276_counts": sub["CD276_counts"].mean()}
    for ct in cell_types:
        row[f"mean_{ct}"] = sub[f"mean_{ct}"].mean()
    rows.append(row)
SEC_BASE = ["section", "patient", "histology", "n_spots", "mean_total_abundance",
            "mean_immune_abundance", "mean_CD276_lognorm",
            "pct_spots_CD276_positive", "mean_CD276_counts"]
SEC_COLS = SEC_BASE + [f"mean_{c}" for c in cell_types]
sec_summary = checked_frame(rows, SEC_COLS, "visium_c2l_section_summary")
sec_summary = sec_summary.sort_values(["histology", "section"])
assert len(sec_summary) == 22, len(sec_summary)
assert sec_summary["n_spots"].sum() == len(obs), (
    sec_summary["n_spots"].sum(), len(obs))
sec_summary.to_csv(f"{TAB}/visium_c2l_section_summary.csv", index=False)
print(sec_summary[["section", "histology", "n_spots", "mean_total_abundance",
                   "mean_immune_abundance", "mean_CD276_lognorm"]].to_string(index=False), flush=True)


# ------------------------------------------------------------------- plotting
def spatial_panel(ax, sub, col, title, cmap="viridis", vmin=None, vmax=None, cbar=True):
    v = sub[col].to_numpy(dtype=float)
    if vmax is None:
        vmax = np.percentile(v, 99) if np.isfinite(v).any() else 1.0
    vmax = max(vmax, 1e-9)
    sca = ax.scatter(sub["x"], sub["y"], c=v, s=2.2, cmap=cmap,
                     norm=Normalize(vmin=0 if vmin is None else vmin, vmax=vmax),
                     linewidths=0, rasterized=True)
    ax.set_title(title, fontsize=8)
    ax.set_xticks([]); ax.set_yticks([]); ax.invert_yaxis(); ax.set_aspect("equal")
    for s in ax.spines.values():
        s.set_visible(False)
    if cbar:
        cb = plt.colorbar(sca, ax=ax, fraction=0.046, pad=0.01)
        cb.ax.tick_params(labelsize=6)
        cb.outline.set_visible(False)
    return sca


def make_panel(histology, outbase, main_title):
    sub_h = obs[obs["histology"] == histology]
    sections = sorted(sub_h["section"].unique())
    # representative section = the one with the most spots
    rep = sub_h.groupby("section").size().idxmax()
    rep_df = sub_h[sub_h["section"] == rep]

    fig = plt.figure(figsize=(15, 11))
    gs = fig.add_gridspec(4, 5, height_ratios=[1.05, 1.05, 1.0, 1.0], hspace=0.35, wspace=0.28)

    # row 0: representative section, 5 maps
    maps = [("CD276_lognorm", "CD276 log1p(CP10K)"), ("immune_abundance", "total immune abundance"),
            ("T_cell_abundance", "T cell abundance"), ("macrophage_abundance", "macrophage abundance"),
            ("fibroblast_abundance", "fibroblast abundance")]
    for j, (col, lab) in enumerate(maps):
        ax = fig.add_subplot(gs[0, j])
        spatial_panel(ax, rep_df, col, f"{lab}\n{rep}", cmap="magma" if j == 0 else "viridis")
    fig.text(0.5, 0.965, main_title, ha="center", fontsize=13, fontweight="bold")
    fig.text(0.5, 0.935, f"representative section: {rep} (n={len(rep_df)} spots)", ha="center", fontsize=9)

    # rows 1-2: small multiples of total immune abundance for all sections
    from matplotlib.gridspec import GridSpecFromSubplotSpec
    sub_gs = GridSpecFromSubplotSpec(3, 4, subplot_spec=gs[1:3, :], hspace=0.18, wspace=0.12)
    vmax_imm = np.percentile(sub_h["immune_abundance"], 99)
    for k, sec in enumerate(sections):
        ax = fig.add_subplot(sub_gs[k // 4, k % 4])
        d = sub_h[sub_h["section"] == sec]
        spatial_panel(ax, d, "immune_abundance", f"{sec} (n={len(d)})", vmax=vmax_imm, cbar=(k == 0))

    # row 3: composition stacked bars
    ax = fig.add_subplot(gs[3, :])
    order = [c for c in IMMUNE + OTHER if c in cell_types]
    comp = sec_summary[sec_summary.histology == histology].set_index("section")[
        [f"mean_{c}" for c in order]].copy()
    comp.columns = order
    comp = comp.div(comp.sum(axis=1), axis=0) * 100
    bottom = np.zeros(len(comp))
    for ct in order:
        ax.bar(comp.index, comp[ct], bottom=bottom, color=COMP_COLORS.get(ct, "#333"),
               label=ct, width=0.75, linewidth=0)
        bottom += comp[ct].to_numpy()
    ax.set_ylabel("% of mean cell abundance", fontsize=8)
    ax.set_title("cell-type composition per section", fontsize=9)
    ax.tick_params(labelsize=7)
    ax.legend(ncol=5, fontsize=6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

    fig.savefig(f"{FIG}/{outbase}.png", dpi=250, bbox_inches="tight")
    fig.savefig(f"{FIG}/{outbase}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("saved", outbase, flush=True)


make_panel("tumor", "fig4e_c2l_tumor",
           "Figure 4E - cell2location deconvolution of 12 LUAD tumour Visium sections")
make_panel("adjacent-normal", "figs5b_c2l_adjacent_normal",
           "Figure S5B - cell2location deconvolution of 10 matched adjacent-normal sections")

log_run(step=("panel_figures" if RUN_STATUS == "ok" else "panel_figures_synthetic_test"),
        status=RUN_STATUS, wall_time_s=round(time.time() - T0, 1),
        n_cells=len(obs), detail=(f"fig4e_c2l_tumor + figs5b_c2l_adjacent_normal (.png/.pdf); "
                                  f"{obs['section'].nunique()} sections "
                                  f"({(obs['histology'] == 'tumor').sum()} tumour spots, "
                                  f"{(obs['histology'] == 'adjacent-normal').sum()} adjacent-normal spots); "
                                  f"section summary table written"))
print("DONE", flush=True)
