"""Apply requested corrections to the saved CD276 single-cell deliverables.

Reads ONLY previously saved summary tables (no h5ad / Census re-analysis):
  - cd276_epithelial_tumor_vs_normal_donor_paired.csv
  - cd276_luad_sclc_celltype_expression.csv
  - cd276_luad_sclc_lineage_expression.csv
  - cd276_key_comparisons.csv
  - cd276_dataset_inventory.csv

Writes:
  - cd276_epithelial_tumor_vs_normal_donor_paired.csv  (adds per-donor ratio)
  - cd276_epithelial_tumor_vs_normal_donor_paired_summary.csv (clean schema)
  - cd276_luad_paired_donor_stats.csv (new explicit statistical artifact)
  - cd276_key_comparisons.csv (corrected wording, no unsupported p in prose)
  - cd276_stromal_vs_tumor_symmetry.csv (new)
  - figures/cd276_luad_tumor_vs_normal_paired.png (ratio-labelled)
  - figures/cd276_stromal_vs_tumor_symmetry.png (new)
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/single-cell-analyst"
TAB = f"{BASE}/results/tables"
FIG = f"{BASE}/results/figures"
os.makedirs(FIG, exist_ok=True)

# ------------------------------------------------------------------
# 1. Donor-matched paired table: add traceable per-donor ratios
# ------------------------------------------------------------------
pair = pd.read_csv(f"{TAB}/cd276_epithelial_tumor_vs_normal_donor_paired.csv")
wide = pair.pivot(index="donor_id", columns="condition", values="mean_cpm")
wide_pct = pair.pivot(index="donor_id", columns="condition", values="pct_expressing")
nwide = pair.pivot(index="donor_id", columns="condition", values="n_cells")

pair["ratio_tumour_over_normal"] = pair.apply(
    lambda r: (r["mean_cpm"] / wide.loc[r["donor_id"], "Normal"])
    if r["condition"] == "LUAD" else np.nan,
    axis=1,
)
pair = pair[["donor_id", "condition", "n_cells", "mean_cpm", "pct_expressing",
             "mean_epcam_cpm", "mean_ptprc_cpm", "ratio_tumour_over_normal"]]
pair.to_csv(f"{TAB}/cd276_epithelial_tumor_vs_normal_donor_paired.csv", index=False)

ratios = (wide["LUAD"] / wide["Normal"]).sort_index()
summary = pd.DataFrame({
    "donor_id": ratios.index,
    "n_cells_LUAD": nwide.loc[ratios.index, "LUAD"].values.astype(int),
    "n_cells_Normal": nwide.loc[ratios.index, "Normal"].values.astype(int),
    "mean_cpm_LUAD": wide.loc[ratios.index, "LUAD"].values,
    "mean_cpm_Normal": wide.loc[ratios.index, "Normal"].values,
    "pct_expressing_LUAD": wide_pct.loc[ratios.index, "LUAD"].values,
    "pct_expressing_Normal": wide_pct.loc[ratios.index, "Normal"].values,
    "ratio_tumour_over_normal": ratios.values,
})
summary.to_csv(f"{TAB}/cd276_epithelial_tumor_vs_normal_donor_paired_summary.csv", index=False)

# ------------------------------------------------------------------
# 2. Explicit statistical artifact (derived from the saved 3-donor table)
# ------------------------------------------------------------------
t_cpm = stats.ttest_rel(wide["LUAD"], wide["Normal"])
t_pct = stats.ttest_rel(wide_pct["LUAD"], wide_pct["Normal"])
stats_df = pd.DataFrame([{
    "comparison": "CD276 in LUAD epithelial cells vs adjacent normal lung epithelial cells (dataset 576f)",
    "n_pairs": int(len(ratios)),
    "mean_cpm_LUAD": round(float(wide["LUAD"].mean()), 4),
    "mean_cpm_Normal": round(float(wide["Normal"].mean()), 4),
    "ratio_of_donor_means": round(float(wide["LUAD"].mean() / wide["Normal"].mean()), 4),
    "mean_of_donor_ratios": round(float(ratios.mean()), 4),
    "min_donor_ratio": round(float(ratios.min()), 4),
    "max_donor_ratio": round(float(ratios.max()), 4),
    "n_donors_higher_in_tumour": int((ratios > 1).sum()),
    "n_donors_ge_2x": int((ratios >= 2).sum()),
    "paired_t_statistic_mean_cpm": round(float(t_cpm.statistic), 4),
    "paired_t_p_value_mean_cpm": round(float(t_cpm.pvalue), 4),
    "paired_t_statistic_pct_expressing": round(float(t_pct.statistic), 4),
    "paired_t_p_value_pct_expressing": round(float(t_pct.pvalue), 4),
    "test": "two-sided paired t-test on donor means, n=3 pairs",
    "caveat": ("n=3 donors; underpowered. Higher in 3/3 but >=2x in only 2/3; "
               "not statistically significant at n=3."),
}])
stats_df.to_csv(f"{TAB}/cd276_luad_paired_donor_stats.csv", index=False)

# ------------------------------------------------------------------
# 3. Corrected key comparisons table
# ------------------------------------------------------------------
key = pd.read_csv(f"{TAB}/cd276_key_comparisons.csv")
corrected_sentence = ("CD276 was higher in tumour than adjacent normal epithelium in 3/3 "
                      "donor-matched LUAD pairs, but reached >=2x in only 2/3 "
                      "(3.26, 3.40, 1.09) and was not statistically significant at n=3.")
mask = key["comparison"].str.contains("adjacent normal lung epithelial", case=False, na=False)
key.loc[mask, "matched"] = ("donor-matched (3 donors); " + corrected_sentence +
                            " Statistical details: cd276_luad_paired_donor_stats.csv")
key["stats_artifact"] = np.where(mask, "cd276_luad_paired_donor_stats.csv", "")
key.to_csv(f"{TAB}/cd276_key_comparisons.csv", index=False)

# ------------------------------------------------------------------
# 4. Symmetry table: stromal/macrophage > malignant/epithelial in BOTH
# ------------------------------------------------------------------
lin = pd.read_csv(f"{TAB}/cd276_luad_sclc_lineage_expression.csv")


def get(ind, lineage):
    r = lin[(lin.indication == ind) & (lin.lineage == lineage)]
    if len(r) != 1:
        raise ValueError(f"expected one row for {ind}/{lineage}, got {len(r)}")
    return r.iloc[0]


rows = []
for ind, tumour_lineage, tumour_label in [
    ("LUAD", "Malignant", "malignant cell"),
    ("SCLC", "Epithelial", "epithelial cell"),
]:
    tum = get(ind, tumour_lineage)
    fib = get(ind, "Fibroblast/stromal")
    mac = get(ind, "Macrophage")
    for comp_label, comp in [("fibroblast/stromal", fib), ("macrophage", mac)]:
        rows.append({
            "indication": ind,
            "tumour_lineage": tumour_label,
            "tumour_mean_cpm": round(float(tum.mean_cpm_weighted), 2),
            "tumour_n_cells": int(tum.n_cells),
            "tumour_n_donors": int(tum.n_donors),
            "comparator": comp_label,
            "comparator_mean_cpm": round(float(comp.mean_cpm_weighted), 2),
            "comparator_n_cells": int(comp.n_cells),
            "comparator_n_donors": int(comp.n_donors),
            "comparator_over_tumour_ratio": round(float(comp.mean_cpm_weighted / tum.mean_cpm_weighted), 2),
            "interpretation": ("Transcript-level comparison within the same indication. Stromal/myeloid cells "
                               "exceed malignant/epithelial cell CD276 in both LUAD and SCLC. This is a "
                               "transcript-level caveat and a potential stromal antigen sink; it is not a measure "
                               "of tumour-cell surface protein and is not evidence against an ADC."),
        })
sym = pd.DataFrame(rows)
sym.to_csv(f"{TAB}/cd276_stromal_vs_tumor_symmetry.csv", index=False)

# ------------------------------------------------------------------
# 5. Corrected paired figure (per-donor ratios shown)
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 4.6))
colors = plt.cm.tab10(np.linspace(0, 1, len(wide)))
for (don, row), c in zip(wide.iterrows(), colors):
    ax.plot([0, 1], [row["Normal"], row["LUAD"]], "-o", lw=1.6, ms=6, color=c)
    ax.annotate(f"{don} ({ratios.loc[don]:.2f}x)", (1.03, row["LUAD"]), fontsize=8, color=c)
ax.set_xlim(-0.15, 1.55)
ax.set_xticks([0, 1], ["Adjacent normal", "LUAD"])
ax.set_ylabel("mean CD276 (CPM-equivalent), epithelial cells")
ax.set_title("Donor-matched epithelial CD276, dataset 576f\n"
             "3/3 higher in tumour; >=2x in 2/3; not significant at n=3")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(f"{FIG}/cd276_luad_tumor_vs_normal_paired.png", dpi=300)
plt.close(fig)

# ------------------------------------------------------------------
# 6. Symmetry figure
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), sharey=False)
for ax, ind in zip(axes, ["LUAD", "SCLC"]):
    sub = sym[sym.indication == ind]
    first = sub.iloc[0]
    labels = [f"{first.tumour_lineage}\n({first.tumour_n_cells:,} cells)"] + \
             [f"{row.comparator}\n({row.comparator_n_cells:,} cells)" for _, row in sub.iterrows()]
    vals = [sub.iloc[0].tumour_mean_cpm] + sub.comparator_mean_cpm.tolist()
    cols = ["#c0392b", "#27ae60", "#2980b9"][:len(vals)]
    ax.bar(range(len(vals)), vals, color=cols)
    ax.set_xticks(range(len(vals)), labels, fontsize=7)
    ax.set_ylabel("mean CD276 (CPM-equivalent)")
    ax.set_title(f"{ind}: stromal/myeloid vs tumour-cell CD276")
    ax.grid(axis="y", alpha=0.3)
fig.suptitle("Same direction in both indications: transcript-level stromal signal exceeds tumour cells",
             fontsize=9)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(f"{FIG}/cd276_stromal_vs_tumor_symmetry.png", dpi=300)
plt.close(fig)

print("Corrections written.")
print("Ratios:", ", ".join(f"{d}={v:.2f}" for d, v in ratios.items()))
print(f"Paired t-test mean CPM: t={t_cpm.statistic:.3f}, p={t_cpm.pvalue:.3f}, n={len(ratios)}")
print("n >=2x:", int((ratios >= 2).sum()), "of", len(ratios))
print("Key comparison corrected rows:", int(mask.sum()))
