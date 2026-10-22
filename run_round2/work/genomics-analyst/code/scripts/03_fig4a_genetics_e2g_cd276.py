#!/usr/bin/env python
"""
Figure 4A: CD276 locus, kept as two separate evidence streams.

  (top-left)   CD276 gene model (GRCh38 chr15:73,683,966-73,714,514; TSS 73,684,383)
  (middle-left) E2G lung regulatory links targeting CD276 (ENCODE rE2G, ENCSR985HNP,
               ENCFF459TXD, DNase-only) - regulatory annotation
  (right)      score distribution and pre-declared thresholds
  (bottom-left) fine-mapped GWAS/QTL credible-set lead variants in TSS +/-500 kb -
               statistical genetic association

The figure deliberately does NOT present E2G links as genetic association.
Outputs: results/figures/fig4a_genetics_e2g_cd276.png and .pdf
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle

from pathlib import Path
# Workspace root = .../work/genomics-analyst (script lives in code/scripts/)
BASE = str(Path(__file__).resolve().parents[2])
TAB = os.path.join(BASE, "results", "tables")
FIG = os.path.join(BASE, "results", "figures")

GENE_START, GENE_END, TSS = 73_683_966, 73_714_514, 73_684_383
WIN_LO, WIN_HI = TSS - 500_000, TSS + 500_000
PRIMARY_THR = 0.02

CLASS_COLORS = {"promoter": "#1f77b4", "genic": "#2ca02c", "intergenic": "#ff7f0e"}
TYPE_COLORS = {"gwas": "#b2182b", "eqtl": "#2166ac", "sqtl": "#762a83",
               "pqtl": "#1b7837", "tuqtl": "#8c6d31", "sceqtl": "#666666"}


def main():
    os.makedirs(FIG, exist_ok=True)
    e2g = pd.read_csv(os.path.join(TAB, "cd276_e2g_regulatory_elements.csv"))
    all_linked = e2g[e2g.is_CD276_target_gene].copy()
    # unique element rows: the gene-linked selection has one row per element
    linked = all_linked[all_linked.overlaps_TSS_500kb].drop_duplicates("name").copy()

    cred = pd.read_parquet(os.path.join(BASE, "data", "raw",
                                        "cd276_tss500kb_region_query_round2.parquet"))
    cred = cred[(cred.position >= WIN_LO) & (cred.position <= WIN_HI)].copy()

    fig = plt.figure(figsize=(14.5, 10.5))
    gs = GridSpec(3, 2, width_ratios=[4.0, 1.25], height_ratios=[0.62, 2.05, 1.55],
                  hspace=0.12, wspace=0.10)
    ax_gene = fig.add_subplot(gs[0, 0])
    ax_e2g = fig.add_subplot(gs[1, 0], sharex=ax_gene)
    ax_cred = fig.add_subplot(gs[2, 0], sharex=ax_gene)
    ax_hist = fig.add_subplot(gs[:, 1])

    xmin, xmax = WIN_LO - 25_000, WIN_HI + 25_000

    # ---------------- A. gene model ----------------
    ax_gene.set_xlim(xmin, xmax)
    ax_gene.set_ylim(-0.8, 0.9)
    for v in [TSS - 250_000, TSS + 250_000]:
        ax_gene.axvline(v, color="0.6", ls=(0, (2, 3)), lw=0.8, zorder=0)
    for v in [WIN_LO, WIN_HI]:
        ax_gene.axvline(v, color="0.4", ls=":", lw=0.8, zorder=0)
    ax_gene.add_patch(Rectangle((GENE_START, -0.22), GENE_END - GENE_START, 0.44,
                                facecolor="#c6dbef", edgecolor="#08519c", lw=1.0, zorder=3))
    ax_gene.plot([GENE_START, GENE_END], [0.0, 0.0], color="#08519c", lw=2.0, zorder=4)
    ax_gene.plot([TSS], [0.42], marker="v", color="#b2182b", ms=8, zorder=5)
    ax_gene.text(TSS, 0.55, "TSS 73,684,383", color="#b2182b", fontsize=8, ha="center")
    ax_gene.text((GENE_START + GENE_END) / 2, -0.52,
                 "CD276 (ENSG00000103855)  chr15:73,683,966-73,714,514",
                 ha="center", va="center", fontsize=9)
    ax_gene.text(TSS - 250_000, 0.73, "TSS -250 kb", fontsize=7, color="0.45", ha="center")
    ax_gene.text(TSS + 250_000, 0.73, "TSS +250 kb", fontsize=7, color="0.45", ha="center")
    ax_gene.text(TSS, -0.72, "gene body", fontsize=7, color="#08519c", ha="center")
    ax_gene.set_yticks([])
    ax_gene.set_ylabel("Gene", rotation=0, ha="right", va="center", fontsize=9)
    ax_gene.set_title("A  CD276 gene model (GRCh38)", loc="left", fontsize=10, fontweight="bold")
    for s in ["top", "right", "bottom"]:
        ax_gene.spines[s].set_visible(False)
    ax_gene.tick_params(labelbottom=False, bottom=False)

    # ---------------- B. E2G links ----------------
    linked = linked.sort_values("Score")
    y = linked["Score"].clip(lower=1e-4)
    for i, r in linked.iterrows():
        ax_e2g.plot([r["element_midpoint"], r["element_midpoint"]], [1e-4, r["Score"]],
                    color=CLASS_COLORS.get(r["class"], "0.5"), lw=0.8, alpha=0.6, zorder=2)
    for cls in ["promoter", "genic", "intergenic"]:
        d = linked[linked["class"] == cls]
        above = d["Score"] >= PRIMARY_THR
        ax_e2g.scatter(d.loc[above, "element_midpoint"], d.loc[above, "Score"],
                       s=42, marker="o", color=CLASS_COLORS[cls], edgecolor="black",
                       linewidth=0.4, zorder=4)
        ax_e2g.scatter(d.loc[~above, "element_midpoint"], d.loc[~above, "Score"].clip(lower=1e-4),
                       s=26, marker="o", facecolor="white", edgecolor=CLASS_COLORS[cls],
                       linewidth=0.9, zorder=3)
    sp = linked[linked.isSelfPromoter]
    ax_e2g.scatter(sp["element_midpoint"], sp["Score"], marker="*", s=260,
                   color="gold", edgecolor="black", linewidth=0.6, zorder=6)
    handles = [Line2D([], [], marker="o", ls="", color=CLASS_COLORS[c], markeredgecolor="black",
                      markersize=7, label=c) for c in ["promoter", "genic", "intergenic"]]
    handles += [
        Line2D([], [], marker="o", ls="", markerfacecolor="white",
               markeredgecolor="0.3", markersize=7, label=f"score < {PRIMARY_THR}"),
        Line2D([], [], marker="*", ls="", markerfacecolor="gold", markeredgecolor="black",
               markersize=12, label="self-promoter"),
    ]
    for thr, lab, ls in [(0.1, "0.10", (0, (4, 2))), (0.05, "0.05", (0, (4, 2))),
                         (PRIMARY_THR, "0.02 (primary)", "-")]:
        ax_e2g.axhline(thr, color="0.25", ls=ls, lw=1.0 if thr == PRIMARY_THR else 0.7, zorder=1)
        n = int((linked["Score"] >= thr).sum())
        ax_e2g.text(xmax - 8_000, thr * 1.08, f"score >= {lab}: n={n}",
                    ha="right", va="bottom", fontsize=7.5, color="0.25")
    for v in [WIN_LO, WIN_HI]:
        ax_e2g.axvline(v, color="0.4", ls=":", lw=0.8, zorder=0)
    ax_e2g.set_yscale("log")
    ax_e2g.set_ylim(1e-4, 2.0)
    ax_e2g.set_ylabel("E2G Score\n(log scale)", fontsize=9)
    ax_e2g.set_title(f"B  Lung E2G links targeting CD276 within TSS +/-500 kb "
                     f"(n={len(linked)} elements; ENCODE rE2G ENCSR985HNP, DNase-only)",
                     loc="left", fontsize=10, fontweight="bold")
    ax_e2g.legend(handles=handles, loc="lower left", fontsize=6.8, frameon=True,
                  ncol=2, framealpha=0.95)
    ax_e2g.grid(axis="y", color="0.9", lw=0.4)
    ax_e2g.tick_params(labelbottom=False)
    ax_e2g.text(0.005, 0.975, "REGULATORY ANNOTATION — not a genetic association",
                transform=ax_e2g.transAxes, ha="left", va="top", fontsize=8,
                style="italic", color="#1f4e79",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.85))

    # ---------------- D. credible sets ----------------
    order = [t for t in ["gwas", "eqtl", "sqtl", "pqtl", "tuqtl", "sceqtl"]
             if t in set(cred.studyType)]
    rng = np.random.default_rng(7)
    for i, t in enumerate(order):
        d = cred[cred.studyType == t]
        jitter = rng.uniform(-0.22, 0.22, len(d))
        ax_cred.scatter(d["position"], i + jitter, s=9, color=TYPE_COLORS[t],
                        alpha=0.65, edgecolor="none", zorder=3)
        ax_cred.text(xmax - 8_000, i + 0.30, f"{t}: {len(d)} sets / {d.studyId.nunique()} studies",
                     ha="right", va="bottom", fontsize=7.5, color=TYPE_COLORS[t])
    ax_cred.axvspan(GENE_START, GENE_END, color="#c6dbef", alpha=0.55, zorder=0)
    for v in [TSS - 250_000, TSS + 250_000]:
        ax_cred.axvline(v, color="0.6", ls=(0, (2, 3)), lw=0.8, zorder=0)
    for v in [WIN_LO, WIN_HI]:
        ax_cred.axvline(v, color="0.4", ls=":", lw=0.8, zorder=0)
    ax_cred.set_yticks(range(len(order)))
    ax_cred.set_yticklabels(order, fontsize=8)
    ax_cred.set_ylim(-0.7, len(order) - 0.2)
    ax_cred.set_xlabel("chr15 position (GRCh38, Mb)")
    ax_cred.set_title(f"C  Fine-mapped credible-set lead variants within TSS +/-500 kb "
                      f"(n={len(cred)} credible sets, {cred.studyId.nunique()} studies; no LUAD/SCLC study)",
                      loc="left", fontsize=10, fontweight="bold")
    ax_cred.text(0.005, 0.975,
                 "STATISTICAL GENETIC ASSOCIATION — 0/8 LUAD+SCLC GWAS studies; 0/67 L2G loci",
                 transform=ax_cred.transAxes, ha="left", va="top", fontsize=8,
                 style="italic", color="#b2182b",
                 bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.85))
    ax_cred.set_xlim(xmin, xmax)
    tick_bp = np.arange(73_200_000, 74_200_001, 200_000)
    ax_cred.set_xticks(tick_bp)
    ax_cred.set_xticklabels([f"{v / 1e6:.1f}" for v in tick_bp])
    for s in ["top", "right"]:
        ax_cred.spines[s].set_visible(False)

    # ---------------- E. score distribution ----------------
    bins = np.logspace(np.log10(1e-4), np.log10(1.0), 45)
    ax_hist.hist(all_linked["Score"].clip(lower=1e-4), bins=bins, color="#4c72b0", alpha=0.85)
    ax_hist.set_xscale("log")
    ax_hist.set_xlabel("E2G Score (log scale)", fontsize=9)
    ax_hist.set_ylabel("CD276-linked elements\n(all distances)", fontsize=8.5)
    for thr, lab, ls in [(0.1, "0.10", (0, (4, 2))), (0.05, "0.05", (0, (4, 2))),
                         (PRIMARY_THR, "0.02", "-")]:
        ax_hist.axvline(thr, color="0.2", ls=ls, lw=1.0 if thr == PRIMARY_THR else 0.7)
        n = int((all_linked["Score"] >= thr).sum())
        ax_hist.text(thr, ax_hist.get_ylim()[1] * 0.97, f" {lab}\n n={n}",
                     fontsize=7, va="top", ha="left")
    ax_hist.set_title("D  E2G score distribution\n(n=%d CD276-linked elements)" % len(all_linked),
                      loc="left", fontsize=9.5, fontweight="bold")
    ax_hist.text(0.04, 0.60,
                 "Median %.4g\n95th pct %.4g\n99th pct %.4g\nMax %.4g" % (
                     all_linked["Score"].median(), all_linked["Score"].quantile(0.95),
                     all_linked["Score"].quantile(0.99), all_linked["Score"].max()),
                 transform=ax_hist.transAxes, fontsize=8, va="top",
                 bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="0.7"))
    ax_hist.grid(axis="y", color="0.9", lw=0.4)
    for s in ["top", "right"]:
        ax_hist.spines[s].set_visible(False)

    fig.suptitle("Figure 4A  CD276 genetic credible-set evidence (germline) vs lung regulatory E2G annotation",
                 fontsize=13, fontweight="bold", y=0.997)
    fig.text(0.5, 0.012,
             "Two distinct evidence streams: (i) fine-mapped GWAS/QTL credible sets test statistical genetic association; "
             "(ii) ENCODE-rE2G DNase-only lung predictions annotate candidate enhancer-gene links. "
             "E2G support is regulatory annotation, not LUAD/SCLC genetic association.",
             ha="center", fontsize=8.2, color="0.25")
    fig.subplots_adjust(left=0.07, right=0.985, top=0.935, bottom=0.075)

    png = os.path.join(FIG, "fig4a_genetics_e2g_cd276.png")
    pdf = os.path.join(FIG, "fig4a_genetics_e2g_cd276.pdf")
    fig.savefig(png, dpi=300)
    fig.savefig(pdf)
    print("wrote", png)
    print("wrote", pdf)
    print(f"linked within window: {len(linked)}; all linked: {len(all_linked)}; credible sets: {len(cred)}")


if __name__ == "__main__":
    main()
