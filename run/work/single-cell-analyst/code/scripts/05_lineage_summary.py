"""Collapse cell-type labels to broad lineages for clean across-organ comparison."""
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/single-cell-analyst"
TAB = f"{BASE}/results/tables"


def lineage(ct):
    s = str(ct).lower()
    if "unknown" in s:
        return "Unknown"
    if "malignant" in s or "tumour" in s or "tumor" in s:
        return "Malignant"
    # word-boundary match so 'malignant cell' / 'goblet cell' are not called T cells
    if re.search(r"\bt[\s-]?cell\b", s) or "thymocyte" in s or "lymphocyte" in s:
        return "T cell"
    if re.search(r"\bb[\s-]?cell\b", s) or s == "be cell":
        return "B cell"
    if "plasma" in s or "antibody secreting" in s:
        return "Plasma cell"
    if "natural killer" in s:
        return "NK cell"
    if "dendritic" in s:
        return "Dendritic cell"
    if "macrophage" in s or "microglial" in s:
        return "Macrophage"
    if "monocyte" in s:
        return "Monocyte"
    if "neutrophil" in s:
        return "Neutrophil"
    if "mast" in s:
        return "Mast cell"
    if "erythrocyte" in s or "platelet" in s or "megakaryocyte" in s:
        return "Blood other"
    if "fibroblast" in s or "stromal" in s or "mesenchymal" in s or "stellate" in s or "adventitial" in s:
        return "Fibroblast/stromal"
    if "endothelial" in s:
        return "Endothelial"
    if "pericyte" in s or "smooth muscle" in s or "myocyte" in s or "muscle" in s or "cardiomyocyte" in s:
        return "Pericyte/SMC/muscle"
    if "adipocyte" in s:
        return "Adipocyte"
    if "hepatocyte" in s:
        return "Hepatocyte"
    if "chondrocyte" in s or "osteoblast" in s or "osteocyte" in s:
        return "Chondrocyte/bone"
    if "neuron" in s or "glia" in s or "astrocyte" in s or "oligodendrocyte" in s or "cns" in s or "eurydendroid" in s:
        return "Neural/glial"
    if "epithelial" in s or "keratinocyte" in s or "club" in s or "basal" in s or "goblet" in s \
       or "ionocyte" in s or "alveolar" in s or "tubule" in s or "nephron" in s or "enterocyte" in s \
       or "pancreatic" in s or "acinar" in s or "duct" in s or "hillock" in s or "brush" in s:
        return "Epithelial"
    return "Other"


def collapse(df, keys):
    d = df.copy()
    d["lineage"] = d.cell_type.map(lineage)
    g = d.groupby(keys + ["lineage"], observed=True).apply(lambda x: pd.Series({
        "n_cells": x.n_cells.sum(),
        "n_donors": x.n_donors.max(),
        "mean_cpm_weighted": np.average(x.mean_cpm, weights=x.n_cells),
        "mean_cpm_donor_avg": np.average(x.mean_cpm_donor_avg, weights=x.n_cells),
        "pct_expressing_weighted": np.average(x.pct_expressing, weights=x.n_cells),
        "max_celltype_cpm": x.mean_cpm.max(),
        "max_celltype": x.loc[x.mean_cpm.idxmax(), "cell_type"],
    }), include_groups=False).reset_index()
    return g


# ---------- normal tissues ----------
norm = pd.read_csv(f"{TAB}/cd276_normal_tissues_celltype_expression.csv")
assert "mean_cpm_donor_avg" in norm.columns, norm.columns.tolist()
norm_lin = collapse(norm, ["organ"])
norm_lin = norm_lin.sort_values(["organ", "mean_cpm_weighted"], ascending=[True, False])
norm_lin.to_csv(f"{TAB}/cd276_normal_tissues_lineage_expression.csv", index=False)

org_order = (norm_lin.groupby("organ", observed=True)
             .apply(lambda x: np.average(x.mean_cpm_weighted, weights=x.n_cells), include_groups=False)
             .sort_values(ascending=False))
print("Organ ordering by weighted mean CD276:")
print(org_order.to_string())
print("\nTop lineages overall (>=500 cells):")
print(norm_lin[norm_lin.n_cells >= 500].sort_values("mean_cpm_weighted", ascending=False)
      .head(20)[["organ", "lineage", "n_cells", "n_donors", "mean_cpm_weighted", "pct_expressing_weighted"]].to_string())

# ---------- figure: organ x lineage heatmap ----------
lin_order = ["Epithelial", "Fibroblast/stromal", "Endothelial", "Pericyte/SMC/muscle",
             "Macrophage", "Monocyte", "Dendritic cell", "T cell", "B cell", "Plasma cell",
             "Adipocyte", "Hepatocyte", "Neural/glial"]
mat = (norm_lin[norm_lin.lineage.isin(lin_order)]
       .pivot(index="organ", columns="lineage", values="mean_cpm_weighted")
       .reindex(index=org_order.index, columns=lin_order))
fig, ax = plt.subplots(figsize=(11, 8))
im = ax.imshow(mat.values, aspect="auto", cmap="YlOrRd", vmin=0, vmax=np.nanpercentile(mat.values, 95))
ax.set_xticks(range(len(mat.columns)), mat.columns, rotation=45, ha="right")
ax.set_yticks(range(len(mat.index)), mat.index)
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        v = mat.values[i, j]
        if np.isfinite(v):
            ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                    color="black" if v < np.nanpercentile(mat.values, 75) else "white", fontsize=7)
fig.colorbar(im, label="mean CD276 (CPM-equivalent)")
ax.set_title("CD276 expression by organ and lineage (normal human tissues, Census)")
fig.tight_layout()
fig.savefig(f"{BASE}/results/figures/cd276_normal_tissues_organ_by_lineage.png", dpi=300)
plt.close(fig)

# ---------- cancer lineage table ----------
can = pd.read_csv(f"{TAB}/cd276_luad_sclc_celltype_expression.csv")
can_lin = collapse(can, ["indication"])
can_lin = can_lin.sort_values(["indication", "mean_cpm_weighted"], ascending=[True, False])
can_lin.to_csv(f"{TAB}/cd276_luad_sclc_lineage_expression.csv", index=False)
print("\nCancer lineage summary:")
print(can_lin.to_string(index=False))

# ---------- key numbers ----------
p = pd.read_csv(f"{TAB}/cd276_luad_sclc_celltype_expression.csv")
for ind in ["LUAD", "SCLC"]:
    for ct in ["malignant cell", "epithelial cell", "fibroblast", "macrophage", "T cell", "CD8-positive, alpha-beta T cell"]:
        r = p[(p.indication == ind) & (p.cell_type == ct)]
        if len(r):
            r = r.iloc[0]
            print(f"{ind} | {ct}: n={int(r.n_cells):,} donors={int(r.n_donors)} "
                  f"mean={r.mean_cpm:.1f} CPM donor_avg={r.mean_cpm_donor_avg:.1f} pct+={100*r.pct_expressing:.1f}%")
