"""
Audit the per-section CD276 stratification BEFORE interpreting any neighbourhood
effect. CD276 is detected in only ~17% of spots, so the value-based quartile rule
can have ties at the boundary and fall back to a deterministic rank split. This
script records, per section, the zero fraction, quartiles, group sizes, whether
the fallback was required, edge/isolated spots, and the depth confounding of the
split (CD276 vs total_counts / n_genes; depth of high vs low groups).

This uses only the spot metadata, so it is independent of the abundance values
and can run while the mapping re-run is in progress.

Output
------
results/tables/visium_c2l_cd276_stratification_audit.csv
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run, checked_frame  # noqa: E402

TAB = f"{WORK}/results/tables"
RADIUS = 2.05

df = pd.read_parquet(f"{TAB}/visium_c2l_spot_abundances.parquet",
                     columns=["section", "patient", "histology", "array_row",
                              "array_col", "total_counts", "n_genes_by_counts",
                              "CD276_counts", "CD276_lognorm"])
rows = []
for sec, sub in df.groupby("section", observed=True):
    cd = sub["CD276_lognorm"].to_numpy(float)
    q25, q50, q75 = np.percentile(cd, [25, 50, 75])
    gt75 = np.where(cd > q75)[0]
    lt25 = np.where(cd < q25)[0]
    fallback = len(gt75) == 0 or len(lt25) == 0
    if fallback:
        order = np.argsort(cd, kind="stable")
        n = len(order)
        low = order[: n // 4]
        high = order[-(n // 4):]
    else:
        low, high = lt25, gt75
    xy = sub[["array_row", "array_col"]].to_numpy(float)
    nb = cKDTree(xy).query_ball_point(xy, r=RADIUS)
    n_nb = np.array([len(x) - 1 for x in nb])
    rho_depth = spearmanr(cd, sub["total_counts"].to_numpy(float)).statistic
    rho_genes = spearmanr(cd, sub["n_genes_by_counts"].to_numpy(float)).statistic
    rows.append({
        "section": sec, "patient": sub["patient"].iloc[0],
        "histology": sub["histology"].iloc[0], "n_spots": len(sub),
        "pct_cd276_zero": float((sub["CD276_counts"] == 0).mean() * 100),
        "q25": q25, "q50": q50, "q75": q75,
        "n_cd276_gt_q75": len(gt75), "n_cd276_lt_q25": len(lt25),
        "rank_fallback_required": bool(fallback),
        "n_high_used": len(high), "n_low_used": len(low),
        "cd276_lognorm_mean_high": float(cd[high].mean()),
        "cd276_lognorm_mean_low": float(cd[low].mean()),
        "pct_cd276_positive_high": float((cd[high] > 0).mean() * 100),
        "pct_cd276_positive_low": float((cd[low] > 0).mean() * 100),
        # These are group MEANS. The earlier column names said "median_*" but
        # the values were computed with .mean(); rename to what they are, and
        # additionally store true per-section medians.
        "mean_total_counts_high": float(sub["total_counts"].to_numpy()[high].mean()),
        "mean_total_counts_low": float(sub["total_counts"].to_numpy()[low].mean()),
        "median_total_counts_high": float(np.median(sub["total_counts"].to_numpy()[high])),
        "median_total_counts_low": float(np.median(sub["total_counts"].to_numpy()[low])),
        "spearman_cd276_vs_total_counts": float(rho_depth),
        "spearman_cd276_vs_n_genes": float(rho_genes),
        "n_isolated_spots": int((n_nb == 0).sum()),
        "n_spots_with_1_to_5_neighbours": int(((n_nb > 0) & (n_nb < 6)).sum()),
    })
AUD_COLS = ["section", "patient", "histology", "n_spots", "pct_cd276_zero",
            "q25", "q50", "q75", "n_cd276_gt_q75", "n_cd276_lt_q25",
            "rank_fallback_required", "n_high_used", "n_low_used",
            "cd276_lognorm_mean_high", "cd276_lognorm_mean_low",
            "pct_cd276_positive_high", "pct_cd276_positive_low",
            "mean_total_counts_high", "mean_total_counts_low",
            "median_total_counts_high", "median_total_counts_low",
            "spearman_cd276_vs_total_counts", "spearman_cd276_vs_n_genes",
            "n_isolated_spots", "n_spots_with_1_to_5_neighbours"]
aud = checked_frame(rows, AUD_COLS, "visium_c2l_cd276_stratification_audit")
assert len(aud) == 22, f"expected 22 sections, got {len(aud)}"
aud.to_csv(f"{TAB}/visium_c2l_cd276_stratification_audit.csv", index=False)
print(aud[["section", "histology", "n_spots", "pct_cd276_zero", "q75",
           "rank_fallback_required", "n_high_used", "n_low_used",
           "spearman_cd276_vs_total_counts"]].to_string(index=False), flush=True)
print("\nfallback required:", int(aud.rank_fallback_required.sum()),
      "/", len(aud), flush=True)
print("median rho(CD276, depth) by histology:", flush=True)
print(aud.groupby("histology")["spearman_cd276_vs_total_counts"].median().to_string(), flush=True)
log_run(step="cd276_stratification_audit", status="ok", n_cells=len(df),
        detail=(f"{len(aud)} sections; rank fallback required in "
                f"{int(aud.rank_fallback_required.sum())}; median Spearman CD276 vs depth "
                f"tumour={aud[aud.histology=='tumor'].spearman_cd276_vs_total_counts.median():.3f}, "
                f"adjacent-normal={aud[aud.histology=='adjacent-normal'].spearman_cd276_vs_total_counts.median():.3f}"))
print("DONE", flush=True)
