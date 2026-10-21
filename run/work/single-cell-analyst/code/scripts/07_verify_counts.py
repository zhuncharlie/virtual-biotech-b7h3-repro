"""Verify cell/donor counts and paired ratios from saved tables (no re-analysis)."""
import pandas as pd

BASE = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/single-cell-analyst"
TAB = f"{BASE}/results/tables"

b = pd.read_csv(f"{TAB}/cd276_luad_sclc_by_dataset_celltype.csv")
print("rows", len(b))
print("\nLUAD totals by dataset:")
print(b[b.indication == "LUAD"].groupby("dataset_id").agg(
    n_cells=("n_cells", "sum"), max_donors=("n_donors", "max"),
    n_ct=("cell_type", "nunique")).to_string())
print("\nSCLC totals by dataset:")
print(b[b.indication == "SCLC"].groupby("dataset_id").agg(
    n_cells=("n_cells", "sum"), max_donors=("n_donors", "max"),
    n_ct=("cell_type", "nunique")).to_string())

keys = ["malignant cell", "epithelial cell", "epithelial cell of lung",
        "fibroblast", "bronchus fibroblast of lung", "fibroblast of lung",
        "macrophage", "alveolar macrophage"]
print("\nKey cell types per dataset:")
print(b[b.cell_type.isin(keys)][
    ["indication", "dataset_id", "cell_type", "n_cells", "n_donors",
     "n_datasets", "mean_cpm", "pct_expressing"]
].sort_values(["indication", "n_cells"], ascending=[True, False]).to_string(index=False))

print("\nmax n_donors per row overall:", b.n_donors.max())
print("Sum LUAD cells:", b[b.indication == "LUAD"].n_cells.sum())
print("Sum SCLC cells:", b[b.indication == "SCLC"].n_cells.sum())

print("\n--- lineage summary ---")
l = pd.read_csv(f"{TAB}/cd276_luad_sclc_lineage_expression.csv")
print(l.to_string(index=False))

print("\n--- compartment summary ---")
c = pd.read_csv(f"{TAB}/cd276_luad_sclc_compartment_summary.csv")
print(c.to_string(index=False))

print("\n--- paired ratios ---")
p = pd.read_csv(f"{TAB}/cd276_epithelial_tumor_vs_normal_donor_paired.csv")
piv = p.pivot(index="donor_id", columns="condition", values="mean_cpm")
piv["ratio_tumour_over_normal"] = piv["LUAD"] / piv["Normal"]
print(piv.round(4).to_string())
print("mean of donor means ratio:", round(piv["LUAD"].mean() / piv["Normal"].mean(), 4))
print("ratios >= 2:", int((piv["ratio_tumour_over_normal"] >= 2).sum()), "of", len(piv))
