"""Panel 4C figure: pseudobulk DE summary and volcano plots.

The volcano grid adapts to the cell types that were actually testable (>=3
donors in each group). Cell types that could not be tested are listed with
their reason in a side panel, so the gap is visible in the figure rather than
silently omitted.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
TAB = BASE / "results/tables"
FIG = BASE / "results/figures"

res = pd.read_csv(TAB / "scrna_pseudobulk_de_luad_sclc.csv")
res = res[res.analysis == "primary_all_donors"].copy()
summ = pd.read_csv(TAB / "scrna_pseudobulk_de_sample_summary.csv")
summ = summ[summ.analysis == "primary_all_donors"].copy()

FDR, LFC = 0.05, 0.5
res["neglog10p"] = -np.log10(res["padj"].clip(lower=1e-300))

HISTS = ["LUAD", "SCLC"]
PRIORITY = ["epithelial cell", "macrophage", "T cell", "dendritic cell",
            "B cell", "endothelial cell", "fibroblast", "mast cell", "plasma cell"]
tested = set(res.cell_type.unique())
CELLS = [c for c in PRIORITY if c in tested][:6]
ntest = len(CELLS)
print("tested cell types:", sorted(tested), "| plotting:", CELLS)

fig = plt.figure(figsize=(4.2 + 2.8 * ntest, 12.0))
gs = fig.add_gridspec(2, ntest + 1, width_ratios=[1.35] + [1] * ntest,
                      hspace=0.55, wspace=0.38, top=0.90, bottom=0.23,
                      left=0.06, right=0.99)

# --- summary bars ---
ax0 = fig.add_subplot(gs[:, 0])
tested_summ = summ[summ.status == "tested"]
piv = tested_summ.pivot_table(index="cell_type", columns="histology",
                              values="n_significant", aggfunc="first")
piv = piv.reindex(index=[c for c in PRIORITY if c in piv.index],
                  columns=[h for h in HISTS if h in piv.columns]).fillna(0)
y = np.arange(len(piv))
w = 0.38
for i, h in enumerate(piv.columns):
    ax0.barh(y + (i - (len(piv.columns) - 1) / 2) * w, piv[h], height=w, label=h)
ax0.set_yticks(y)
ax0.set_yticklabels(piv.index, fontsize=9)
ax0.invert_yaxis()
ax0.set_xlabel("Significant genes\n(FDR<0.05, |log2FC|>0.5)", fontsize=10)
ax0.set_title("A  Pseudobulk DE: disease vs normal", fontsize=12, loc="left")
ax0.legend(frameon=False, fontsize=9)
ax0.spines[["top", "right"]].set_visible(False)

# --- volcano plots ---
for r, hist in enumerate(HISTS):
    for c, ct in enumerate(CELLS):
        ax = fig.add_subplot(gs[r, c + 1])
        d = res[(res.histology == hist) & (res.cell_type == ct)].copy()
        if d.empty:
            ax.text(0.5, 0.5, "not tested", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title(f"{hist} | {ct}", fontsize=10)
            ax.set_xticks([])
            ax.set_yticks([])
            continue
        sig = d.significant.fillna(False).astype(bool)
        ax.scatter(d.loc[~sig, "log2FoldChange"], d.loc[~sig, "neglog10p"], s=2,
                   c="lightgrey", rasterized=True)
        up = sig & (d.log2FoldChange > 0)
        dn = sig & (d.log2FoldChange < 0)
        ax.scatter(d.loc[up, "log2FoldChange"], d.loc[up, "neglog10p"], s=3,
                   c="#c0392b", rasterized=True, label=f"up ({int(up.sum())})")
        ax.scatter(d.loc[dn, "log2FoldChange"], d.loc[dn, "neglog10p"], s=3,
                   c="#2471a3", rasterized=True, label=f"down ({int(dn.sum())})")
        ax.axvline(LFC, ls="--", lw=0.6, c="k")
        ax.axvline(-LFC, ls="--", lw=0.6, c="k")
        ax.axhline(-np.log10(FDR), ls="--", lw=0.6, c="k")
        if "CD276" in set(d.gene):
            g = d[d.gene == "CD276"].iloc[0]
            ax.annotate("CD276", (g.log2FoldChange, g.neglog10p), fontsize=8,
                        xytext=(4, 4), textcoords="offset points", color="black")
            ax.scatter([g.log2FoldChange], [g.neglog10p], s=35, facecolors="none",
                       edgecolors="k", linewidths=1.0)
        ax.set_title(f"{hist} | {ct}\n"
                     f"{int(d.n_disease_donors.iloc[0])} disease vs "
                     f"{int(d.n_normal_donors.iloc[0])} normal donors", fontsize=9)
        ax.set_xlabel("log2FC (disease / normal)", fontsize=9)
        ax.set_ylabel("-log10 FDR", fontsize=9)
        ax.legend(frameon=False, fontsize=7, loc="upper left")
        ax.spines[["top", "right"]].set_visible(False)

# --- untested cell types, with reasons ---
skipped = summ[summ.status != "tested"].copy()
lines = []
for hist in HISTS:
    parts = []
    for _, s in skipped[skipped.histology == hist].drop_duplicates("cell_type").iterrows():
        parts.append(f"{s.cell_type} ({int(s.n_disease_donors)} vs "
                     f"{int(s.n_normal_donors)} donors)")
    if parts:
        lines.append(f"{hist} not tested: " + ", ".join(parts))
lines.append("A contrast requires >=3 donors with >=10 cells in BOTH groups.")
if lines:
    fig.text(0.06, 0.185, "\n".join(lines), fontsize=7.4, va="top", ha="left",
             linespacing=1.5, color="0.25")

fig.suptitle("Panel 4C  Pseudobulk DE in LUAD and SCLC (dataset 576f193c; all genes tested)",
             fontsize=14, x=0.01, y=0.985, ha="left")
fig.text(0.01, 0.955, "FDR<0.05 (Benjamini-Hochberg) and |log2FC|>0.5; "
         "PyDESeq2 0.5.4; raw-count pseudobulk per donor x cell type x condition",
         fontsize=9, color="0.35", ha="left")
fig.savefig(FIG / "fig4c_pseudobulk_de_luad_sclc.png", dpi=300, bbox_inches="tight")
fig.savefig(FIG / "fig4c_pseudobulk_de_luad_sclc.pdf", bbox_inches="tight")
plt.close(fig)
print("wrote fig4c_pseudobulk_de_luad_sclc.png/.pdf")
