#!/usr/bin/env python
"""
Gene-level expression of the ligands/receptors in the top differential pairs,
in CAF_B7H3_high vs CAF_B7H3_low fibroblasts.

Values are computed from the integrated atlas:
  mean_lognorm  = mean of .X (log-normalised) across cells
  pct_detected  = fraction of cells with raw count > 0
This shows whether the source-side genes differ after normalisation, and hence
whether a differential call is supported by expression rather than only by
rank re-ordering.

Implementation note: the atlas is subset to disease fibroblasts once per
disease and held in memory, then all genes are read from that in-memory object.
The earlier column-by-column backed read was aborted after >3 min without
output because each backed column access scanned the full 414k-cell matrix.

Output
  results/tables/liana_top_pair_gene_expression.csv
"""
import os
import numpy as np
import pandas as pd
import anndata as ad

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
SRC_ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"  # atlas input stays in SOURCE (md5 in report)
WORK = os.path.join(ROOT, "work/single-cell-analyst")
SRC_WORK = os.path.join(SRC_ROOT, "work/single-cell-analyst")
H5AD = os.path.join(SRC_WORK, "data/processed/scrna_luad_sclc_integrated.h5ad")
TAB = os.path.join(WORK, "results/tables")
DISEASE = {"SCLC": "small cell lung carcinoma", "LUAD": "lung adenocarcinoma"}


def genes_in(s):
    return [g for g in str(s).replace("&", "_").split("_") if g]


def main():
    top = pd.read_csv(os.path.join(TAB, "liana_top_differential_pairs.csv"))
    A = ad.read_h5ad(H5AD, backed="r")
    obs = A.obs
    out = []
    for short, label in DISEASE.items():
        genes = set()
        for _, r in top[top.disease == short].iterrows():
            genes |= set(genes_in(r.ligand_complex)) | set(genes_in(r.receptor_complex))
        genes.add("CD276")
        genes = sorted(genes)

        dsel = (obs["disease"] == label).values & (obs["cell_type"].astype(str) == "fibroblast").values
        idx = np.where(dsel)[0]
        D = A[idx, :].to_memory()
        D.var_names = D.var["feature_name"].astype(str).values
        D.var_names_make_unique()
        sub_obs = D.obs
        cd = np.asarray(D[:, "CD276"].layers["counts"].todense()).ravel()
        grp = np.where(cd > 0, "CAF_B7H3_high", "CAF_B7H3_low")
        hi = grp == "CAF_B7H3_high"
        lo = grp == "CAF_B7H3_low"

        for g in genes:
            if g not in D.var_names:
                continue
            x = np.asarray(D[:, g].X.todense()).ravel()
            cnt = np.asarray(D[:, g].layers["counts"].todense()).ravel()
            out.append(dict(
                disease=short, gene=g,
                mean_lognorm_high=round(float(x[hi].mean()), 4),
                mean_lognorm_low=round(float(x[lo].mean()), 4),
                log2FC_lognorm=round(float(np.log2((x[hi].mean() + 1e-6) / (x[lo].mean() + 1e-6))), 4),
                pct_detected_high=round(float((cnt[hi] > 0).mean()), 4),
                pct_detected_low=round(float((cnt[lo] > 0).mean()), 4),
                mean_raw_high=round(float(cnt[hi].mean()), 4),
                mean_raw_low=round(float(cnt[lo].mean()), 4),
            ))
        del D
    df = pd.DataFrame(out)
    df.to_csv(os.path.join(TAB, "liana_top_pair_gene_expression.csv"), index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
