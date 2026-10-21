#!/usr/bin/env python
"""Summarise CD276 single-cell expression in LUAD and SCLC for modality selection.

Input : single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv
Output: results/tables/cd276_key_celltype_expression.csv
        results/tables/cd276_malignant_vs_stromal_ratios.csv
        results/figures/cd276_malignant_vs_stromal_expression.png

The comparison that matters for a cytotoxic modality is malignant/epithelial
signal versus the stromal and myeloid cells that share the same tissue.  These
are transcript (CPM) data, not surface protein density; the report says so.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

WORK = Path(
    "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
    "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work"
)
RUN = WORK / "medchem-pharmacologist"
SRC = WORK / "single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv"

TAB = RUN / "results/tables"
FIG = RUN / "results/figures"
TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SRC)

KEY_CELLS = {
    "LUAD": [
        "malignant cell",
        "fibroblast",
        "macrophage",
        "alveolar macrophage",
        "epithelial cell",
        "pulmonary alveolar type 2 cell",
        "endothelial cell",
        "T cell",
        "natural killer cell",
        "B cell",
    ],
    "SCLC": [
        "epithelial cell",
        "fibroblast",
        "macrophage",
        "endothelial cell",
        "T cell",
        "B cell",
        "dendritic cell",
        "neutrophil",
    ],
}

# The comparator is the malignant/epithelial population present in the same
# single-cell table.  SCLC has no separate 'malignant cell' label.
MALIGNANT_REF = {"LUAD": "malignant cell", "SCLC": "epithelial cell"}

rows = []
ratio_rows = []

for indication, cells in KEY_CELLS.items():
    sub = df[df["indication"] == indication].copy()
    sub = sub[sub["cell_type"].isin(cells)]
    ref_type = MALIGNANT_REF[indication]
    ref = sub.loc[sub["cell_type"] == ref_type]
    if ref.empty:
        raise ValueError(f"reference cell type missing for {indication}: {ref_type}")
    ref_cpm = float(ref["mean_cpm"].iloc[0])
    ref_pct = float(ref["pct_expressing"].iloc[0])

    for _, r in sub.iterrows():
        rows.append(
            {
                "indication": indication,
                "cell_type": r["cell_type"],
                "lineage": r["lineage"],
                "compartment": r["compartment"],
                "n_cells": int(r["n_cells"]),
                "n_donors": int(r["n_donors"]),
                "n_datasets": int(r["n_datasets"]),
                "mean_cpm": round(float(r["mean_cpm"]), 2),
                "mean_cpm_donor_avg": round(float(r["mean_cpm_donor_avg"]), 2),
                "median_cpm": round(float(r["median_cpm"]), 2),
                "pct_expressing": round(float(r["pct_expressing"]), 4),
                "malignant_reference_cell_type": ref_type,
                "malignant_reference_mean_cpm": round(ref_cpm, 2),
                "ratio_to_malignant_reference": round(float(r["mean_cpm"]) / ref_cpm, 2)
                if ref_cpm > 0
                else np.nan,
                "is_malignant_reference": r["cell_type"] == ref_type,
            }
        )

    # Fold-change in the other direction, so the report can quote either form.
    for _, r in sub.iterrows():
        if r["cell_type"] == ref_type:
            continue
        if ref_cpm > 0:
            ratio_rows.append(
                {
                    "indication": indication,
                    "malignant_reference_cell_type": ref_type,
                    "malignant_reference_mean_cpm": round(ref_cpm, 2),
                    "malignant_reference_pct_expressing": round(ref_pct, 4),
                    "comparator_cell_type": r["cell_type"],
                    "comparator_mean_cpm": round(float(r["mean_cpm"]), 2),
                    "comparator_pct_expressing": round(float(r["pct_expressing"]), 4),
                    "malignant_to_comparator_ratio": round(ref_cpm / float(r["mean_cpm"]), 2)
                    if float(r["mean_cpm"]) > 0
                    else np.nan,
                    "comparator_to_malignant_ratio": round(float(r["mean_cpm"]) / ref_cpm, 2),
                }
            )

key = pd.DataFrame(rows).sort_values(
    ["indication", "mean_cpm"], ascending=[True, False]
)
ratios = pd.DataFrame(ratio_rows).sort_values(
    ["indication", "malignant_to_comparator_ratio"], ascending=[True, True]
)

key.to_csv(TAB / "cd276_key_celltype_expression.csv", index=False)
ratios.to_csv(TAB / "cd276_malignant_vs_stromal_ratios.csv", index=False)

# ---- Figure: malignant/epithelial signal against the shared-tissue background ----
plot_cells = {
    "LUAD": [
        "malignant cell",
        "fibroblast",
        "macrophage",
        "alveolar macrophage",
        "pulmonary alveolar type 2 cell",
        "endothelial cell",
        "T cell",
        "natural killer cell",
    ],
    "SCLC": [
        "epithelial cell",
        "fibroblast",
        "macrophage",
        "endothelial cell",
        "dendritic cell",
        "B cell",
        "T cell",
    ],
}
colors = {
    "malignant cell": "#b2182b",
    "epithelial cell": "#b2182b",
    "fibroblast": "#2166ac",
    "macrophage": "#4393c3",
    "alveolar macrophage": "#92c5de",
    "pulmonary alveolar type 2 cell": "#f4a582",
    "endothelial cell": "#7b3294",
    "T cell": "#bababa",
    "natural killer cell": "#878787",
    "B cell": "#d9d9d9",
    "dendritic cell": "#c7eae5",
}

fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), sharey=False)
for ax, indication in zip(axes, ["LUAD", "SCLC"]):
    sub = (
        key[key["indication"] == indication]
        .set_index("cell_type")
        .loc[plot_cells[indication]]
    )
    y = np.arange(len(sub))
    ax.barh(
        y,
        sub["mean_cpm"],
        color=[colors.get(c, "#999999") for c in sub.index],
        edgecolor="black",
        linewidth=0.4,
    )
    ax.set_yticks(y)
    ax.set_yticklabels([c.replace(" cell", "") for c in sub.index], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("CD276 mean CPM (single-cell transcript)")
    ax.set_title(f"{indication}: CD276 is highest in stroma/myeloid, not tumour", fontsize=11)
    ax.grid(axis="x", alpha=0.25)
    for yi, (_, row) in enumerate(sub.iterrows()):
        ax.text(
            row["mean_cpm"] + max(sub["mean_cpm"]) * 0.015,
            yi,
            f"{row['mean_cpm']:.1f} CPM / {row['pct_expressing']*100:.1f}% expressing",
            va="center",
            fontsize=7.5,
        )
    ax.set_xlim(0, max(sub["mean_cpm"]) * 1.55)

fig.suptitle(
    "CD276 transcript in LUAD and SCLC: malignant cells are not the dominant source",
    fontsize=13,
    y=1.00,
)
fig.tight_layout()
fig.savefig(FIG / "cd276_malignant_vs_stromal_expression.png", dpi=300, bbox_inches="tight")
fig.savefig(FIG / "cd276_malignant_vs_stromal_expression.pdf", bbox_inches="tight")
plt.close(fig)

print("Wrote:")
print(TAB / "cd276_key_celltype_expression.csv")
print(TAB / "cd276_malignant_vs_stromal_ratios.csv")
print(FIG / "cd276_malignant_vs_stromal_expression.png")
for indication in ["LUAD", "SCLC"]:
    r = ratios[ratios["indication"] == indication]
    print(f"\n{indication} malignant-to-comparator ratios:")
    print(
        r[
            [
                "comparator_cell_type",
                "comparator_mean_cpm",
                "malignant_to_comparator_ratio",
            ]
        ].to_string(index=False)
    )
