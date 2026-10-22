#!/usr/bin/env python
"""
Audit the depth dependence of the detection-based B7-H3 CAF split.

The primary definition splits fibroblasts by CD276 raw count > 0 vs == 0.
Raw-count detection is library-size dependent, so this script quantifies:
  - n_genes / total_counts in CAF_B7H3_high vs CAF_B7H3_low
  - Spearman correlation of CD276 raw count with n_genes and total_counts
    across all disease fibroblasts
  - donor-level correlation between the fraction of CD276-positive
    fibroblasts and donor sequencing depth (median n_genes)

Outputs
  results/tables/liana_caf_depth_audit.csv
  results/tables/liana_caf_depth_by_donor.csv
  results/figures/caf_b7h3_detection_depth_audit.png
"""
import os
import numpy as np
import pandas as pd
import anndata as ad
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
SRC_ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"  # atlas input stays in SOURCE (md5 in report)
WORK = os.path.join(ROOT, "work/single-cell-analyst")
SRC_WORK = os.path.join(SRC_ROOT, "work/single-cell-analyst")
H5AD = os.path.join(SRC_WORK, "data/processed/scrna_luad_sclc_integrated.h5ad")
TAB = os.path.join(WORK, "results/tables")
FIG = os.path.join(WORK, "results/figures")

DISEASE = {"SCLC": "small cell lung carcinoma", "LUAD": "lung adenocarcinoma"}


def main():
    A = ad.read_h5ad(H5AD, backed="r")
    gi = int(np.where(A.var["feature_name"].astype(str).values == "CD276")[0][0])
    cd_all = np.asarray(A[:, gi].layers["counts"].todense()).ravel()
    obs = A.obs.copy()
    keep = obs["cell_type"].astype(str).values == "fibroblast"
    obs = obs.loc[keep].copy()
    cd = cd_all[keep]

    obs["cd276_raw"] = cd.astype(int)
    obs["caf_group"] = np.where(cd > 0, "CAF_B7H3_high", "CAF_B7H3_low")

    rows, donor_rows = [], []
    panel = {}
    for short, label in DISEASE.items():
        d = obs[obs["disease"] == label].copy()
        hi = d[d.caf_group == "CAF_B7H3_high"]
        lo = d[d.caf_group == "CAF_B7H3_low"]
        rho_g, p_g = spearmanr(d["cd276_raw"], d["n_genes"])
        rho_c, p_c = spearmanr(d["cd276_raw"], d["total_counts"])

        # donor-level depth vs positivity fraction
        dd = (d.groupby("donor_id", observed=True)
                .agg(n_fib=("cd276_raw", "size"),
                     n_high=("cd276_raw", lambda x: int((x > 0).sum())),
                     median_n_genes=("n_genes", "median"),
                     median_total_counts=("total_counts", "median"),
                     median_cd276=("cd276_raw", "median"))
                .reset_index())
        dd["frac_high"] = dd["n_high"] / dd["n_fib"]
        dd.insert(0, "disease", short)
        donor_rows.append(dd)
        rho_d, p_d = spearmanr(dd["frac_high"], dd["median_n_genes"])

        rows.append(dict(
            disease=short,
            n_fibroblasts=len(d), n_high=len(hi), n_low=len(lo),
            frac_high=round(len(hi) / len(d), 4),
            median_n_genes_high=float(hi["n_genes"].median()),
            median_n_genes_low=float(lo["n_genes"].median()),
            median_total_counts_high=float(hi["total_counts"].median()),
            median_total_counts_low=float(lo["total_counts"].median()),
            median_cd276_high=float(hi["cd276_raw"].median()),
            median_cd276_low=float(lo["cd276_raw"].median()),
            frac_cd276_zero=round(float((d["cd276_raw"] == 0).mean()), 4),
            frac_cd276_one=round(float((d["cd276_raw"] == 1).mean()), 4),
            frac_cd276_ge2=round(float((d["cd276_raw"] >= 2).mean()), 4),
            rho_cd276_vs_n_genes=round(float(rho_g), 4),
            p_cd276_vs_n_genes=float(p_g),
            rho_cd276_vs_total_counts=round(float(rho_c), 4),
            p_cd276_vs_total_counts=float(p_c),
            n_donors=int(dd.shape[0]),
            n_donors_high=int((dd["n_high"] > 0).sum()),
            rho_donor_frac_high_vs_median_n_genes=round(float(rho_d), 4),
            p_donor_frac_high_vs_median_n_genes=float(p_d),
        ))
        panel[short] = d

    pd.DataFrame(rows).to_csv(os.path.join(TAB, "liana_caf_depth_audit.csv"), index=False)
    pd.concat(donor_rows, ignore_index=True).to_csv(
        os.path.join(TAB, "liana_caf_depth_by_donor.csv"), index=False)

    # -------- figure: CD276 count distribution + n_genes by group ----------
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5))
    for j, short in enumerate(["SCLC", "LUAD"]):
        d = panel[short]
        ax = axes[0, j]
        vc = d["cd276_raw"].value_counts().sort_index()
        vc = vc[vc.index <= 6]
        ax.bar(vc.index, vc.values, color="#4d7ea8", edgecolor="0.3")
        ax.set_yscale("log")
        ax.set_xlabel("CD276 raw count per fibroblast")
        ax.set_ylabel("cells (log scale)")
        ax.set_title(f"{short}: CD276 count distribution (n={len(d):,})", fontsize=9)

        ax = axes[1, j]
        data = [d.loc[d.caf_group == "CAF_B7H3_low", "n_genes"].values,
                d.loc[d.caf_group == "CAF_B7H3_high", "n_genes"].values]
        bp = ax.boxplot(data, tick_labels=["CD276 = 0", "CD276 > 0"], showfliers=False,
                        patch_artist=True, widths=0.55)
        for patch, col in zip(bp["boxes"], ["#9ecae1", "#de2d26"]):
            patch.set_facecolor(col)
        ax.set_ylabel("genes detected per fibroblast")
        ax.set_title(f"{short}: depth by B7-H3 group", fontsize=9)
    fig.suptitle("Detection-based B7-H3 CAF split is depth-dependent", fontsize=11)
    fig.tight_layout()
    out = os.path.join(FIG, "caf_b7h3_detection_depth_audit.png")
    fig.savefig(out, dpi=250, bbox_inches="tight")
    print("WROTE", out)
    print(pd.DataFrame(rows).T.to_string())


if __name__ == "__main__":
    main()
