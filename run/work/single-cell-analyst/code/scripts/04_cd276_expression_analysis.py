"""CD276 expression in LUAD and SCLC (CELLxGENE Census), per cell type and tumor vs normal.

Units: Census 'normalized' layer is counts divided by total counts per cell (fraction).
We multiply by 1e6 to report CPM-equivalent units. No log transform applied.
"""
import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as sp

BASE = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/single-cell-analyst"
RAW = f"{BASE}/data/raw"
TAB = f"{BASE}/results/tables"

COMPARTMENT = {
    # malignant / epithelial
    "malignant cell": "Malignant/epithelial", "epithelial cell": "Malignant/epithelial",
    "epithelial cell of lung": "Malignant/epithelial", "epithelial cell of lower respiratory tract": "Malignant/epithelial",
    "pulmonary alveolar type 2 cell": "Malignant/epithelial", "pulmonary alveolar type 1 cell": "Malignant/epithelial",
    "pulmonary alveolar epithelial cell": "Malignant/epithelial", "multiciliated epithelial cell": "Malignant/epithelial",
    "multiciliated columnar cell of tracheobronchial tree": "Malignant/epithelial", "club cell": "Malignant/epithelial",
    "brush cell of tracheobronchial tree": "Malignant/epithelial", "respiratory basal cell": "Malignant/epithelial",
    "ionocyte": "Malignant/epithelial", "respiratory tract hillock cell": "Malignant/epithelial",
    "tracheobronchial goblet cell": "Malignant/epithelial", "nasal mucosa goblet cell": "Malignant/epithelial",
    # immune
    "CD4-positive, alpha-beta T cell": "Immune", "CD8-positive, alpha-beta T cell": "Immune",
    "T cell": "Immune", "regulatory T cell": "Immune", "natural killer cell": "Immune",
    "B cell": "Immune", "plasma cell": "Immune", "alveolar macrophage": "Immune", "macrophage": "Immune",
    "lung macrophage": "Immune", "elicited macrophage": "Immune", "classical monocyte": "Immune",
    "non-classical monocyte": "Immune", "myeloid cell": "Immune", "CD1c-positive myeloid dendritic cell": "Immune",
    "plasmacytoid dendritic cell": "Immune", "conventional dendritic cell": "Immune", "dendritic cell": "Immune",
    "neutrophil": "Immune", "mast cell": "Immune",
    # stromal / endothelial
    "fibroblast": "Stromal/endothelial", "fibroblast of lung": "Stromal/endothelial",
    "bronchus fibroblast of lung": "Stromal/endothelial", "alveolar type 1 fibroblast cell": "Stromal/endothelial",
    "alveolar adventitial fibroblast": "Stromal/endothelial", "myofibroblast cell": "Stromal/endothelial",
    "vein endothelial cell": "Stromal/endothelial", "capillary endothelial cell": "Stromal/endothelial",
    "endothelial cell": "Stromal/endothelial", "endothelial cell of lymphatic vessel": "Stromal/endothelial",
    "pulmonary artery endothelial cell": "Stromal/endothelial", "smooth muscle cell": "Stromal/endothelial",
    "tracheobronchial smooth muscle cell": "Stromal/endothelial", "pericyte": "Stromal/endothelial",
    "lung pericyte": "Stromal/endothelial", "mesothelial cell": "Stromal/endothelial",
    "stromal cell": "Stromal/endothelial", "erythrocyte": "Other", "unknown": "Unknown",
}


def load(path):
    a = sc.read_h5ad(path)
    a.var.index = a.var["feature_name"].astype(str)
    a.var_names_make_unique()
    for c in a.obs.columns:
        if a.obs[c].dtype.name == "category":
            a.obs[c] = a.obs[c].astype(str)
    return a


def expr_vector(a, gene):
    return np.asarray(a[:, gene].X.todense()).ravel()


def summarize(a, group_cols):
    """Cell-level and donor-level summary of CD276 per group."""
    d = a.obs.copy()
    d["cd276"] = expr_vector(a, "CD276")
    d["epcam"] = expr_vector(a, "EPCAM") if "EPCAM" in a.var_names else np.nan
    d["ptprc"] = expr_vector(a, "PTPRC") if "PTPRC" in a.var_names else np.nan
    d["compartment"] = d["cell_type"].map(COMPARTMENT).fillna("Other")

    g = d.groupby(group_cols, observed=True)
    out = g.agg(
        n_cells=("cd276", "size"),
        n_donors=("donor_id", "nunique"),
        n_datasets=("dataset_id", "nunique"),
        mean_fraction=("cd276", "mean"),
        median_fraction=("cd276", "median"),
        pct_expressing=("cd276", lambda s: float(np.mean(s > 0))),
        mean_epcam_fraction=("epcam", "mean"),
        mean_ptprc_fraction=("ptprc", "mean"),
    ).reset_index()
    # donor-level mean (unweighted across donors) for robustness
    dm = (d.groupby(group_cols + ["donor_id"], observed=True)["cd276"].mean()
          .groupby(level=list(range(len(group_cols)))).mean().rename("mean_fraction_donor_avg"))
    out = out.merge(dm.reset_index(), on=group_cols, how="left")
    for c in ["mean_fraction", "median_fraction", "mean_fraction_donor_avg",
              "mean_epcam_fraction", "mean_ptprc_fraction"]:
        out[c.replace("_fraction", "_cpm")] = out[c] * 1e6
    return out


# ---------------- LUAD / SCLC ----------------
luad_parts = [
    load(f"{RAW}/luad_ds1e6a_lymphoid_cd276.h5ad"),
    load(f"{RAW}/luad_ds1e6a_myeloid_cd276.h5ad"),
    load(f"{RAW}/luad_ds1e6a_epithelial_stromal_cd276.h5ad"),
    load(f"{RAW}/luad_other_datasets_cd276.h5ad"),
]
luad = sc.concat(luad_parts, join="outer", merge="same")
luad.obs["indication"] = "LUAD"
sclc = load(f"{RAW}/sclc_cd276.h5ad")
sclc.obs["indication"] = "SCLC"
print("LUAD:", luad.shape, "| cells:", luad.n_obs, "| donors:", luad.obs.donor_id.nunique(),
      "| datasets:", luad.obs.dataset_id.nunique())
print("SCLC:", sclc.shape, "| cells:", sclc.n_obs, "| donors:", sclc.obs.donor_id.nunique(),
      "| datasets:", sclc.obs.dataset_id.nunique())
assert luad.n_obs == 635998, luad.n_obs

# pooled per indication x cell type
pooled = pd.concat([
    summarize(luad, ["indication", "compartment", "cell_type"]),
    summarize(sclc, ["indication", "compartment", "cell_type"]),
], ignore_index=True)
pooled = pooled.sort_values(["indication", "mean_cpm"], ascending=[True, False])
pooled.to_csv(f"{TAB}/cd276_luad_sclc_celltype_expression.csv", index=False)

# per dataset x cell type (shows consistency / annotation differences)
byds = pd.concat([
    summarize(luad, ["indication", "dataset_id", "compartment", "cell_type"]),
    summarize(sclc, ["indication", "dataset_id", "compartment", "cell_type"]),
], ignore_index=True)
byds.to_csv(f"{TAB}/cd276_luad_sclc_by_dataset_celltype.csv", index=False)

# compartment-level summary
comp = pd.concat([
    summarize(luad, ["indication", "compartment"]),
    summarize(sclc, ["indication", "compartment"]),
], ignore_index=True).sort_values(["indication", "mean_cpm"], ascending=[True, False])
comp.to_csv(f"{TAB}/cd276_luad_sclc_compartment_summary.csv", index=False)

# ---------------- Tumor vs normal (dataset 576f; matched donors) ----------------
normal_lung = load(f"{RAW}/normal_lung_matched_cd276.h5ad")
normal_lung.obs["indication"] = "Normal lung"
tvn = []
for cond, ad in [("LUAD", luad[luad.obs.dataset_id == "576f193c-75d0-4a11-bd25-8676587e6dc2"]),
                 ("SCLC", sclc[sclc.obs.dataset_id == "576f193c-75d0-4a11-bd25-8676587e6dc2"]),
                 ("Normal", normal_lung)]:
    t = summarize(ad, ["indication", "cell_type", "donor_id"])
    t["condition"] = cond
    tvn.append(t)
tvn = pd.concat(tvn, ignore_index=True)
tvn.to_csv(f"{TAB}/cd276_tumor_vs_normal_per_donor.csv", index=False)

# paired donor-level epithelial comparison (LUAD vs normal, shared donors)
shared = sorted(set(luad.obs.donor_id) & set(normal_lung.obs.donor_id))
print("Shared LUAD/normal donors in 576f:", shared)
rows = []
for don in shared:
    for cond, ad in [("LUAD", luad), ("Normal", normal_lung)]:
        sub = ad[(ad.obs.donor_id == don) & (ad.obs.cell_type == "epithelial cell")]
        if len(sub) == 0:
            continue
        v = expr_vector(sub, "CD276")
        rows.append(dict(donor_id=don, condition=cond, n_cells=len(v),
                         mean_cpm=v.mean() * 1e6, pct_expressing=float(np.mean(v > 0)),
                         mean_epcam_cpm=expr_vector(sub, "EPCAM").mean() * 1e6 if "EPCAM" in sub.var_names else np.nan,
                         mean_ptprc_cpm=expr_vector(sub, "PTPRC").mean() * 1e6 if "PTPRC" in sub.var_names else np.nan))
pair = pd.DataFrame(rows)
pair.to_csv(f"{TAB}/cd276_epithelial_tumor_vs_normal_donor_paired.csv", index=False)
pair_sum = pair.pivot(index="donor_id", columns="condition", values=["n_cells", "mean_cpm", "pct_expressing"])
pair_sum["mean_cpm", "ratio_LUAD_over_normal"] = pair_sum[("mean_cpm", "LUAD")] / pair_sum[("mean_cpm", "Normal")]
pair_sum.to_csv(f"{TAB}/cd276_epithelial_tumor_vs_normal_donor_paired_summary.csv")
print(pair.to_string())
print("\nPaired summary:\n", pair_sum.to_string())
print("\nMean LUAD vs normal epithelial CPM (donor means):",
      pair[pair.condition == "LUAD"].mean_cpm.mean(), "vs", pair[pair.condition == "Normal"].mean_cpm.mean())

# SCLC epithelial vs normal epithelial (not donor matched)
print("\nSCLC epithelial:", summarize(sclc[sclc.obs.cell_type == "epithelial cell"], ["indication"]).to_string())
print("Normal lung epithelial:", summarize(normal_lung[normal_lung.obs.cell_type == "epithelial cell"], ["indication"]).to_string())

# ---------------- Normal tissues ----------------
files = {
    "blood (progenitor-rich)": "normal_blood_cd276.h5ad",
    "blood (mature PBMC)": "normal_blood_mature_pbmc_cd276.h5ad",
    "bone marrow": "normal_bone_marrow_cd276.h5ad",
    "spleen/lymph node": "normal_spleen_lymphnode_cd276.h5ad", "thymus": "normal_thymus_cd276.h5ad",
    "heart": "normal_heart_cd276.h5ad", "liver": "normal_liver_cd276.h5ad",
    "kidney": "normal_kidney_cd276.h5ad", "brain cortex": "normal_brain_cortex_cd276.h5ad",
    "skin": "normal_skin_cd276.h5ad", "colon": "normal_colon_cd276.h5ad",
    "ileum": "normal_ileum_cd276.h5ad", "pancreas": "normal_pancreas_cd276.h5ad",
    "skeletal muscle": "normal_skeletal_muscle_cd276.h5ad", "esophagus": "normal_esophagus_cd276.h5ad",
    "adrenal gland": "normal_adrenal_cd276.h5ad", "breast": "normal_breast_cd276.h5ad",
    "adipose": "normal_adipose_cd276.h5ad", "lung": "normal_lung_matched_cd276.h5ad",
}
norm_parts = []
for organ, f in files.items():
    a = load(f"{RAW}/{f}")
    a.obs["organ"] = organ
    # for spleen/LN keep the Census tissue label
    if "tissue" in a.obs:
        a.obs["organ_detail"] = a.obs["tissue"].astype(str)
    else:
        a.obs["organ_detail"] = organ
    t = summarize(a, ["organ", "organ_detail", "cell_type"])
    norm_parts.append(t)
norm = pd.concat(norm_parts, ignore_index=True)
norm = norm.sort_values(["organ", "mean_cpm"], ascending=[True, False])
norm.to_csv(f"{TAB}/cd276_normal_tissues_celltype_expression.csv", index=False)

# organ summary (exclude 'unknown' cell-type label)
norm_valid = norm[norm.cell_type.astype(str).str.lower() != "unknown"].copy()
org = norm_valid.groupby("organ", observed=True).apply(lambda x: pd.Series({
    "n_cells": x.n_cells.sum(),
    "n_donors": x.n_donors.max(),
    "weighted_mean_cpm": np.average(x.mean_cpm, weights=x.n_cells),
    "max_celltype_cpm": x.mean_cpm.max(),
    "max_celltype": x.loc[x.mean_cpm.idxmax(), "cell_type"],
    "max_celltype_pct": x.loc[x.mean_cpm.idxmax(), "pct_expressing"],
    "pct_cells_expressing_weighted": np.average(x.pct_expressing, weights=x.n_cells),
}), include_groups=False).reset_index().sort_values("weighted_mean_cpm", ascending=False)
org.to_csv(f"{TAB}/cd276_normal_tissue_organ_summary.csv", index=False)
print("\nOrgan summary:\n", org.to_string())
top_norm = (norm[(norm.n_cells >= 200) & (norm.cell_type.astype(str).str.lower() != "unknown")]
            .sort_values("mean_cpm", ascending=False))
top_norm.to_csv(f"{TAB}/cd276_normal_tissues_top_celltypes.csv", index=False)
print("\nTop 25 normal cell types by mean CD276 CPM (>=200 cells, unknown excluded):")
print(top_norm.head(25)[["organ", "cell_type", "n_cells", "n_donors", "mean_cpm", "pct_expressing"]].to_string())

# ---------------- Figures ----------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pooled_top = pooled[(pooled.cell_type.astype(str).str.lower() != "unknown") & (pooled.n_cells >= 200)]
pooled_top.to_csv(f"{TAB}/cd276_luad_sclc_top_celltypes_min200cells.csv", index=False)
fig, axes = plt.subplots(1, 2, figsize=(16, 10), sharex=False)
for ax, ind in zip(axes, ["LUAD", "SCLC"]):
    sub = pooled_top[pooled_top.indication == ind].head(20).iloc[::-1]
    colors = sub.compartment.map({"Malignant/epithelial": "#c0392b", "Immune": "#2980b9",
                                  "Stromal/endothelial": "#27ae60", "Other": "#7f8c8d",
                                  "Unknown": "#bdc3c7"}).fillna("#7f8c8d")
    ax.barh(sub.cell_type + " (" + sub.n_cells.map(lambda x: f"{x:,}") + ")", sub.mean_cpm, color=colors)
    ax.set_xlabel("mean CD276 expression (CPM-equivalent)")
    ax.set_title(f"{ind}: top cell types by CD276\n(n cells in parentheses; red=malignant/epithelial)")
    ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(f"{BASE}/results/figures/cd276_luad_sclc_celltype_expression.png", dpi=300)
plt.close(fig)

# normal tissue heatmap: top cell types per organ
pivot_rows = []
for organ, g in norm_valid.groupby("organ", observed=True):
    top = g.sort_values("mean_cpm", ascending=False).head(4)
    for _, r in top.iterrows():
        pivot_rows.append((f"{organ}: {r.cell_type}", r.mean_cpm))
labels, vals = zip(*pivot_rows)
order = np.argsort(vals)
fig, ax = plt.subplots(figsize=(8, 12))
ax.barh(np.array(labels)[order], np.array(vals)[order],
        color=["#c0392b" if v >= 50 else ("#e67e22" if v >= 10 else "#95a5a6") for v in np.array(vals)[order]])
ax.set_xlabel("mean CD276 expression (CPM-equivalent)")
ax.set_title("CD276 in normal tissues: top 4 cell types per organ")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(f"{BASE}/results/figures/cd276_normal_tissues_top_celltypes.png", dpi=300)
plt.close(fig)

print("\nSaved tables and figures.")
