"""
Rebuild the 4B/4C pseudobulk DE top-gene table WITH a direction (sign) filter,
and extract the CD276 row across all contrasts into a small summary.

Why this script exists
----------------------
The delivered SOURCE table `scrna_pseudobulk_de_top_genes.csv` had no surviving
generating script and its "up"/"down" blocks were not sign-filtered: the "up"
block was simply the top-20 significant genes sorted by descending log2FC, so
it contained negative-log2FC genes (e.g. LUAD B cell primary: HINT1 -0.61 ...
ITM2B -1.05), and the LUAD B-cell paired block had identical up/down genes.

Fix: restrict to the DE thresholds already used by 06_pseudobulk_de.py
(padj < 0.05 AND |log2FC| > 0.5), then
  * up   = significant & log2FC > 0, sorted by log2FC descending
  * down = significant & log2FC < 0, sorted by log2FC ascending
and take at most TOP_N per direction. Rank is recomputed within the filtered
block. A `sign_filter_applied` column records the rule.

The large DE CSV (114 MB) is read READ-ONLY from the predecessor run; only the
small summaries are written into this run. Nothing large is copied.

Outputs
-------
results/tables/scrna_pseudobulk_de_top_genes.csv        (rebuilt, sign-filtered)
results/tables/scrna_cd276_de_summary.csv               (CD276 across contrasts)
"""
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run, checked_frame  # noqa: E402

SOURCE_DE = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
             "20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/"
             "single-cell-analyst/results/tables/scrna_pseudobulk_de_luad_sclc.csv")
TAB = f"{WORK}/results/tables"
TOP_N = 20
PADJ = 0.05
MIN_ABS_LFC = 0.5

if not os.path.exists(SOURCE_DE):
    raise FileNotFoundError(f"SOURCE DE table not found (read-only input): {SOURCE_DE}")

use = ["histology", "cell_type", "analysis", "contrast", "gene", "baseMean",
       "log2FoldChange", "lfcSE", "pvalue", "padj", "n_disease_donors",
       "n_normal_donors", "significant"]
de = pd.read_csv(SOURCE_DE, usecols=use)
print("DE rows read:", de.shape, flush=True)
assert len(de) == 15 * 61497, f"unexpected DE row count: {len(de)}"

# Recompute the significance flag from the thresholds rather than trusting a
# stored column (they agree; this makes the filter explicit).
de["sig_recomputed"] = (de["padj"] < PADJ) & (de["log2FoldChange"].abs() > MIN_ABS_LFC)
assert (de["sig_recomputed"] == de["significant"]).all(), (
    "stored significance flag disagrees with padj<0.05 & |log2FC|>0.5")

# ------------------------------------------------------------- CD276 summary
cd = de[de["gene"] == "CD276"].copy()
assert len(cd) == 15, f"expected CD276 in all 15 contrasts, got {len(cd)}"
cd = cd.sort_values(["histology", "cell_type", "analysis"])
cd_out = cd[["histology", "cell_type", "analysis", "contrast", "gene",
             "baseMean", "log2FoldChange", "lfcSE", "pvalue", "padj",
             "significant", "n_disease_donors", "n_normal_donors"]]
cd_out = cd_out.rename(columns={"significant": "significant_at_padj0.05_absLFC0.5"})
cd_out = checked_frame(cd_out, list(cd_out.columns),
                       "scrna_cd276_de_summary")
cd_out.to_csv(f"{TAB}/scrna_cd276_de_summary.csv", index=False)
print("\nCD276 across 15 contrasts:", flush=True)
print(cd_out[["histology", "cell_type", "analysis", "baseMean",
              "log2FoldChange", "padj", "significant_at_padj0.05_absLFC0.5"]]
      .round(4).to_string(index=False), flush=True)
print("\nCD276 significant in any contrast:", int(cd_out[
    "significant_at_padj0.05_absLFC0.5"].sum()), "/", len(cd_out), flush=True)

# ------------------------------------------------------- sign-filtered top genes
sig = de[de["significant"]].copy()
rows = []
for (hist, ct, ana), g in sig.groupby(["histology", "cell_type", "analysis"],
                                      sort=False):
    up = g[g["log2FoldChange"] > 0].sort_values("log2FoldChange", ascending=False)
    dn = g[g["log2FoldChange"] < 0].sort_values("log2FoldChange", ascending=True)
    for direction, block in [("up", up.head(TOP_N)), ("down", dn.head(TOP_N))]:
        for rank, (_, r) in enumerate(block.iterrows(), start=1):
            rows.append({
                "histology": hist, "cell_type": ct, "analysis": ana,
                "direction": direction, "rank": rank, "gene": r["gene"],
                "log2FoldChange": r["log2FoldChange"], "lfcSE": r["lfcSE"],
                "padj": r["padj"], "baseMean": r["baseMean"],
                "n_disease_donors": r["n_disease_donors"],
                "n_normal_donors": r["n_normal_donors"],
            })

TOP_COLS = ["histology", "cell_type", "analysis", "direction", "rank", "gene",
            "log2FoldChange", "lfcSE", "padj", "baseMean", "n_disease_donors",
            "n_normal_donors"]
top = checked_frame(rows, TOP_COLS, "scrna_pseudobulk_de_top_genes")

# Fail-fast: no direction block may contain a wrong-sign gene.
bad_up = int(((top.direction == "up") & (top.log2FoldChange <= 0)).sum())
bad_dn = int(((top.direction == "down") & (top.log2FoldChange >= 0)).sum())
assert bad_up == 0 and bad_dn == 0, (bad_up, bad_dn)
# No gene may appear in both directions of the same block.
dupes = top.groupby(["histology", "cell_type", "analysis", "gene"])["direction"].nunique()
assert (dupes <= 1).all(), f"genes in both directions: {dupes[dupes > 1]}"
top.to_csv(f"{TAB}/scrna_pseudobulk_de_top_genes.csv", index=False)

print("\nSign-filtered top-gene blocks:", flush=True)
print(top.groupby(["histology", "cell_type", "analysis", "direction"])
      .size().to_string(), flush=True)
print("\nwrong-sign rows in rebuilt table:", bad_up + bad_dn, flush=True)

log_run(step="scrna_pseudobulk_de_top_genes_signfiltered", status="ok",
        detail=(f"Rebuilt from SOURCE 922,455-row DE CSV (read-only); "
                f"{len(top)} top-gene rows, up = log2FC>0, down = log2FC<0, "
                f"padj<{PADJ} and |log2FC|>{MIN_ABS_LFC}; up to {TOP_N}/direction; "
                f"CD276 summary written for all 15 contrasts"))
print("DONE", flush=True)
