"""Assemble final tidy tables: add lineage labels, dataset inventory, key comparisons."""
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

BASE = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/single-cell-analyst"
TAB = f"{BASE}/results/tables"
RAW = f"{BASE}/data/raw"


def lineage(ct):
    s = str(ct).lower()
    if "unknown" in s:
        return "Unknown"
    if "malignant" in s or "tumour" in s or "tumor" in s:
        return "Malignant"
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


# ---- 1. required table + lineage ----
p = pd.read_csv(f"{TAB}/cd276_luad_sclc_celltype_expression.csv")
p = p.drop(columns=[c for c in ["lineage", "dataset_id"] if c in p.columns])
p.insert(3, "lineage", p.cell_type.map(lineage))
cols = ["indication", "dataset_id", "cell_type", "lineage", "compartment", "n_cells", "n_donors", "n_datasets",
        "mean_cpm", "mean_cpm_donor_avg", "median_cpm", "pct_expressing",
        "mean_epcam_cpm", "mean_ptprc_cpm"]
# dataset_id is not in the pooled table; keep schema explicit
if "dataset_id" not in p.columns:
    p["dataset_id"] = "pooled"
p = p[cols].sort_values(["indication", "mean_cpm", "n_cells"], ascending=[True, False, False])
p.to_csv(f"{TAB}/cd276_luad_sclc_celltype_expression.csv", index=False)

# by-dataset table also gets lineage
b = pd.read_csv(f"{TAB}/cd276_luad_sclc_by_dataset_celltype.csv")
b["lineage"] = b.cell_type.map(lineage)
b.to_csv(f"{TAB}/cd276_luad_sclc_by_dataset_celltype.csv", index=False)

# ---- 2. dataset inventory ----
rows = []
for ind, f in [("LUAD", "luad_lung_cell_metadata.parquet"), ("SCLC", "sclc_lung_cell_metadata.parquet")]:
    df = pd.read_parquet(f"{RAW}/{f}")
    df = df[df.is_primary_data == True]
    for ds, g in df.groupby("dataset_id", observed=True):
        rows.append(dict(indication=ind, dataset_id=str(ds), n_cells=len(g), n_donors=g.donor_id.nunique(),
                         n_cell_types=g.cell_type.nunique(),
                         assays="; ".join(f"{k}" for k in g.assay.astype(str).unique()),
                         tissue=str(g.tissue.astype(str).iloc[0]), disease=str(g.disease.astype(str).iloc[0])))
inv = pd.DataFrame(rows).sort_values(["indication", "n_cells"], ascending=[True, False])
inv.to_csv(f"{TAB}/cd276_dataset_inventory.csv", index=False)
print("Dataset inventory:\n", inv.to_string(index=False))

# normal tissue inventory (from assays file)
na = pd.read_csv(f"{TAB}/normal_tissue_dataset_assays.csv")
na.to_csv(f"{TAB}/cd276_normal_dataset_inventory.csv", index=False)

# ---- 3. key comparisons ----
pair = pd.read_csv(f"{TAB}/cd276_epithelial_tumor_vs_normal_donor_paired.csv")
piv = pair.pivot(index="donor_id", columns="condition", values="mean_cpm")
pivp = pair.pivot(index="donor_id", columns="condition", values="pct_expressing")
t = stats.ttest_rel(piv["LUAD"], piv["Normal"])
tp = stats.ttest_rel(pivp["LUAD"], pivp["Normal"])
norm_ep = 17.091188  # normal lung epithelial, pooled (see log)
key = [
    dict(comparison="LUAD malignant cells (annotated) vs LUAD non-malignant epithelial cells",
         grouping="LUAD", tumor_or_test="malignant cell", comparator="epithelial (non-malignant)",
         n_tumor_cells=26179, n_tumor_donors=92, n_comparator_cells=47002, n_comparator_donors=93,
         mean_cpm_tumor=23.58, mean_cpm_comparator=16.40, pct_expressing_tumor=0.1544,
         pct_expressing_comparator=0.0751, matched="same indication, different cell classes"),
    dict(comparison="LUAD epithelial cells vs adjacent normal lung epithelial cells (dataset 576f)",
         grouping="LUAD vs normal", tumor_or_test="LUAD epithelial", comparator="normal lung epithelial",
         n_tumor_cells=int(pair[pair.condition == "LUAD"].n_cells.sum()), n_tumor_donors=3,
         n_comparator_cells=int(pair[pair.condition == "Normal"].n_cells.sum()), n_comparator_donors=3,
         mean_cpm_tumor=round(piv["LUAD"].mean(), 2), mean_cpm_comparator=round(piv["Normal"].mean(), 2),
         pct_expressing_tumor=round(pivp["LUAD"].mean(), 4), pct_expressing_comparator=round(pivp["Normal"].mean(), 4),
         matched=f"donor-matched (3 donors); paired t-test p={t.pvalue:.2f} (mean CPM), p={tp.pvalue:.2f} (pct expressing)"),
    dict(comparison="SCLC epithelial cells vs normal lung epithelial cells (dataset 576f, no shared donors)",
         grouping="SCLC vs normal", tumor_or_test="SCLC epithelial", comparator="normal lung epithelial",
         n_tumor_cells=25988, n_tumor_donors=9, n_comparator_cells=851, n_comparator_donors=4,
         mean_cpm_tumor=28.54, mean_cpm_comparator=norm_ep, pct_expressing_tumor=0.1946,
         pct_expressing_comparator=0.0682, matched="NOT donor-matched (same dataset, disjoint donors)"),
    dict(comparison="LUAD: malignant cells vs tumour-associated macrophages",
         grouping="LUAD", tumor_or_test="malignant cell", comparator="macrophage",
         n_tumor_cells=26179, n_tumor_donors=92, n_comparator_cells=116365, n_comparator_donors=115,
         mean_cpm_tumor=23.58, mean_cpm_comparator=33.49, pct_expressing_tumor=0.1544,
         pct_expressing_comparator=0.2159, matched="same samples"),
    dict(comparison="LUAD: malignant cells vs tumour-associated fibroblasts",
         grouping="LUAD", tumor_or_test="malignant cell", comparator="fibroblast/stromal",
         n_tumor_cells=26179, n_tumor_donors=92, n_comparator_cells=9909, n_comparator_donors=75,
         mean_cpm_tumor=23.58, mean_cpm_comparator=55.45, pct_expressing_tumor=0.1544,
         pct_expressing_comparator=0.2107, matched="same samples"),
    dict(comparison="SCLC: epithelial cells vs tumour-associated fibroblasts",
         grouping="SCLC", tumor_or_test="epithelial cell", comparator="fibroblast/stromal",
         n_tumor_cells=25988, n_tumor_donors=9, n_comparator_cells=328, n_comparator_donors=9,
         mean_cpm_tumor=28.54, mean_cpm_comparator=68.10, pct_expressing_tumor=0.1946,
         pct_expressing_comparator=0.2622, matched="same samples"),
]
keydf = pd.DataFrame(key)
keydf.to_csv(f"{TAB}/cd276_key_comparisons.csv", index=False)
print("\nKey comparisons:\n", keydf.to_string(index=False))

# ---- 4. paired donor figure ----
fig, ax = plt.subplots(figsize=(5.5, 4.5))
for don, row in piv.iterrows():
    ax.plot([0, 1], [row["Normal"], row["LUAD"]], "-o", lw=1.5, ms=6)
    ax.annotate(don, (1.02, row["LUAD"]), fontsize=8)
ax.set_xticks([0, 1], ["Adjacent normal", "LUAD"])
ax.set_ylabel("mean CD276 (CPM-equivalent), epithelial cells")
ax.set_title("Donor-matched epithelial CD276\ndataset 576f, 3 donors")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(f"{BASE}/results/figures/cd276_luad_tumor_vs_normal_paired.png", dpi=300)
plt.close(fig)
print("\nWrote final tables and paired figure.")
