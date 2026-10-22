#!/usr/bin/env python
"""
Figures 4D (SCLC) and S5A (LUAD): LIANA differential interactions between
B7-H3-high and B7-H3-low fibroblast-labelled CAFs.

Same layout and scale conventions in both panels.  If no interaction survives
all pre-specified filters, the figure says so explicitly and shows the filter
cascade plus nominal candidates labelled as not significant.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
WORK = os.path.join(ROOT, "work/single-cell-analyst")
TAB = os.path.join(WORK, "results/tables")
FIG = os.path.join(WORK, "results/figures")

SPEC_RANK_CUT = 0.1
PVAL_CUT = 0.01
MIN_METHODS = 3

META = {
    "SCLC": dict(
        table="liana_caf_b7h3_sclc_4d.csv",
        png="fig4d_liana_sclc_caf_b7h3.png",
        pdf="fig4d_liana_sclc_caf_b7h3.pdf",
        panel="Panel 4D",
        disease="SCLC",
        high_n=86, low_n=158, high_d=7, low_d=9,
    ),
    "LUAD": dict(
        table="liana_caf_b7h3_luad_s5a.csv",
        png="figs5a_liana_luad_caf_b7h3.png",
        pdf="figs5a_liana_luad_caf_b7h3.pdf",
        panel="Panel S5A",
        disease="LUAD",
        high_n=1676, low_n=5346, high_d=47, low_d=58,
    ),
}

VMIN, VMAX = -0.5, 0.5


def lr_label(r):
    return f"{r['ligand_complex']} → {r['receptor_complex']}"


def select_rows(df, n_per_dir=12):
    """Rows enriched in high / low; if none, top nominal candidates by |delta|."""
    up = df[df["differential_call"] == "enriched_high"].copy()
    dn = df[df["differential_call"] == "enriched_low"].copy()
    fallback = False
    if len(up) == 0 and len(dn) == 0:
        fallback = True
        cand = df.copy()
        # nominal = at least one side passes the permutation p-value filter
        cand = cand[
            (cand.get("cellphone_pvals_high", np.inf) < PVAL_CUT)
            | (cand.get("cellphone_pvals_low", np.inf) < PVAL_CUT)
        ]
        cand = cand.reindex(cand["delta_specificity_rank"].abs().sort_values(ascending=False).index)
        up = cand[cand["delta_specificity_rank"] > 0].head(n_per_dir)
        dn = cand[cand["delta_specificity_rank"] < 0].head(n_per_dir)
    up = up.sort_values("delta_specificity_rank", ascending=False).head(n_per_dir)
    dn = dn.sort_values("delta_specificity_rank").head(n_per_dir)
    return up, dn, fallback


def make_panel(short, cascade_counts):
    m = META[short]
    df = pd.read_csv(os.path.join(TAB, m["table"]))
    # the per-disease table has one row per source group, so every target/LR
    # pair appears twice (high-source and low-source rows). Collapse to the
    # differential unit (one row per pair) before selecting and counting.
    df = df.drop_duplicates(subset=["target", "ligand_complex", "receptor_complex"]).copy()
    up, dn, fallback = select_rows(df)

    fig = plt.figure(figsize=(13, max(5.5, 0.42 * (len(up) + len(dn)) + 3.0)))
    gs = fig.add_gridspec(1, 2, width_ratios=[4.2, 1.15], wspace=0.28)
    ax = fig.add_subplot(gs[0, 0])
    axc = fig.add_subplot(gs[0, 1])

    # ---------- build dot-plot matrix -------------------------------------
    rows = []
    for direction, sub, pcol in (("up", up, "cellphone_pvals_high"),
                                 ("down", dn, "cellphone_pvals_low")):
        for _, r in sub.iterrows():
            rows.append(dict(direction=direction, label=lr_label(r), target=r["target"],
                             delta=r["delta_specificity_rank"],
                             p=r.get(pcol, np.nan),
                             lfc=r.get("log2_lr_means_high_over_low", np.nan)))
    if not rows:
        ax.text(0.5, 0.5, "No nominal differential candidates\n(even before filtering)",
                ha="center", va="center", fontsize=13, transform=ax.transAxes)
        ax.set_axis_off()
    else:
        d = pd.DataFrame(rows)
        targets = sorted(d["target"].unique())
        labels = list(dict.fromkeys(d["label"]))
        ypos = {}
        y = 0
        yticks, yticklabels = [], []
        for direction in ("up", "down"):
            sub = d[d.direction == direction]
            if sub.empty:
                continue
            if direction == "down":
                y += 0.8  # gap between direction blocks
            for lab in list(dict.fromkeys(sub["label"])):
                ypos[lab] = y
                yticks.append(y)
                yticklabels.append(lab)
                y += 1
            ax.axhline(y - 0.5, color="0.8", lw=0.8, zorder=0)
            y += 0.3

        for _, r in d.iterrows():
            x = targets.index(r["target"])
            yy = ypos[r["label"]]
            p = r["p"] if pd.notna(r["p"]) else 1.0
            size = np.clip(-np.log10(max(p, p if p > 0 else 1.0 / 1001)), 0, 3)
            ax.scatter(x, yy, s=35 + 190 * size, c=[r["delta"]], cmap="coolwarm",
                       vmin=VMIN, vmax=VMAX, edgecolor="0.25", linewidth=0.4, zorder=3)

        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels, fontsize=7.5)
        ax.set_xticks(range(len(targets)))
        ax.set_xticklabels(targets, rotation=45, ha="right", fontsize=8)
        ax.set_ylabel("Ligand → receptor", fontsize=9)
        ax.set_xlabel("Target cell type", fontsize=9)
        ax.set_ylim(-0.8, max(ypos.values()) + 1.0 if ypos else 1)
        ax.invert_yaxis()

        # direction block labels on the right
        if not up.empty:
            ax.text(1.005, 0.985, "higher in B7-H3-high",
                    transform=ax.transAxes, rotation=90, va="top", ha="left",
                    fontsize=8, color="#b2182b", fontweight="bold")
        if not dn.empty:
            lo_frac = 0.0 if up.empty else 0.45
            ax.text(1.005, lo_frac + 0.02,
                    "higher in B7-H3-low", transform=ax.transAxes, rotation=90,
                    va="bottom", ha="left", fontsize=8, color="#2166ac", fontweight="bold")

    cb = fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(VMIN, VMAX), cmap="coolwarm"),
                      ax=ax, orientation="vertical", fraction=0.025, pad=0.02)
    cb.set_label("Δ specificity rank\n(low − high; >0 = higher in B7-H3-high)",
                 fontsize=7.5)

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="0.65",
               markeredgecolor="0.25", markersize=np.sqrt(35 + 190 * v),
               label=lbl) for v, lbl in ((0, "p=1"), (1, "p=0.1"), (2, "p=0.01"), (3, "p≤0.001"))
    ]
    ax.legend(handles=handles, title="dot size:\nCellPhoneDB\n−log10 p",
              loc="upper left", bbox_to_anchor=(0.0, -0.32), fontsize=7, title_fontsize=7,
              frameon=False, ncol=4, handletextpad=0.6, columnspacing=1.2)

    if fallback:
        ax.text(0.01, 0.99, "NONE pass all filters — nominal candidates only",
                transform=ax.transAxes, va="top", ha="left", fontsize=8.5,
                color="#b2182b", fontweight="bold")

    # ---------- filter cascade -------------------------------------------
    c = pd.DataFrame(cascade_counts)
    c = c[c["disease"] == short]
    axc.barh(range(len(c)), c["n_interactions"], color="#8c96c6", edgecolor="0.3")
    axc.set_yticks(range(len(c)))
    axc.set_yticklabels([s.split("_", 1)[1].replace("_", " ") for s in c["step"]], fontsize=7)
    axc.invert_yaxis()
    for i, v in enumerate(c["n_interactions"]):
        axc.text(v + max(c["n_interactions"]) * 0.02, i, f"{v:,}", va="center", fontsize=7)
    axc.set_xlabel("interactions (source = CAF)", fontsize=8)
    axc.set_title("filter cascade", fontsize=9)
    axc.set_xlim(0, max(c["n_interactions"]) * 1.35)
    n_up = int((df["differential_call"] == "enriched_high").sum())
    n_dn = int((df["differential_call"] == "enriched_low").sum())
    axc.text(0.02, -0.35, f"enriched high: {n_up}\nenriched low: {n_dn}",
             transform=axc.transAxes, fontsize=8, va="top",
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7"))

    title = (f"{m['panel']} — {m['disease']}: B7-H3-high vs B7-H3-low "
             f"tumour-associated fibroblast compartment (fibroblast-labelled)")
    sub = (f"CAF_B7H3_high n={m['high_n']} ({m['high_d']} donors)  |  "
           f"CAF_B7H3_low n={m['low_n']} ({m['low_d']} donors)  |  "
           f"LIANA rank_aggregate consensus, 1,000 perms.  Filters: top-decile specificity rank "
           f"(discriminating), p<0.01 and ≥3 methods (both non-discriminating here).\n"
           f"Calls are rank-based differential specificity, not a formal high-vs-low test; "
           f"the split is CD276-detection-based and depth-dependent (see depth audit).")
    if fallback:
        sub += "\nNOTE: no interaction passes all filters; dots show nominal candidates and must not be read as significant."
    fig.suptitle(title, fontsize=11, x=0.02, ha="left", y=0.99)
    fig.text(0.02, 0.945 if not fallback else 0.915, sub, fontsize=7.5, va="top", ha="left")
    fig.subplots_adjust(top=0.83 if not fallback else 0.80, left=0.22, right=0.96, bottom=0.16)

    for ext in ("png", "pdf"):
        out = os.path.join(FIG, m["png"] if ext == "png" else m["pdf"])
        fig.savefig(out, dpi=300, bbox_inches="tight")
        print("WROTE", out)
    plt.close(fig)


if __name__ == "__main__":
    casc = pd.read_csv(os.path.join(TAB, "liana_filter_cascade.csv"))
    for short in ["SCLC", "LUAD"]:
        if os.path.exists(os.path.join(TAB, META[short]["table"])):
            make_panel(short, casc)
