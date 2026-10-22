"""
Panel 4E / S5B step 4: spatial-neighbourhood analysis of immune-cell abundance
around B7-H3 (CD276) high vs low Visium spots.

Definitions (pre-specified)
---------------------------
* Spot B7-H3 level: log1p(CP10K) of CD276 (NOT raw counts; depth-confounded).
* Stratification unit: SECTION. Each Visium section is an independent array
  from a single tissue block; pooling spots across sections before quartiling
  would let section-level depth/composition drive the split. Patients have up
  to 4 sections, so a patient-level split would mix tumour and adjacent-normal
  tissue. Sections are therefore stratified independently, and patient is used
  only to check donor-level consistency.
* high = CD276 lognorm > per-section 75th percentile; low = < 25th percentile;
  the middle 50% is excluded from the high-vs-low contrast (it is still used as
  a neighbour when computing neighbourhood means).
* Neighbourhood: k=6 nearest spots on the Visium hex lattice built from
  (array_row, array_col) with a hard radius of 2.05 coordinate units. On this
  lattice the six physical neighbours sit at 1.414 (diagonal) and 2.0
  (same-row); the next ring is >= 2.828. The radius therefore returns exactly
  the true neighbours and never crosses sections. Spots with 0 true neighbours
  (isolated QC-surviving spots) are excluded from the contrast and counted.
  Spots with 1-5 neighbours use the mean of the neighbours they have.
* Neighbour abundance = unweighted mean posterior cell-type abundance of the
  neighbouring spots, excluding the spot itself.
* Effect = (mean_neighbour_high - mean_neighbour_low) / mean_neighbour_low * 100.

Outputs
-------
results/tables/visium_neighborhood_immune_change.csv
results/tables/visium_neighborhood_robustness.csv
results/tables/visium_neighborhood_stratification.csv
results/figures/fig4e_neighborhood_immune_change.png/.pdf      (tumour)
results/figures/figs5b_neighborhood_immune_change.png/.pdf    (adjacent-normal)
"""
import os
import sys
import time
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run, checked_frame  # noqa: E402

SEED = 42
N_PERM = int(os.environ.get("C2L_NPERM", "1000"))
N_BOOT = int(os.environ.get("C2L_NBOOT", "1000"))
# Probe runs use a suffix so a timed small-N run can never masquerade as the
# final result (the canonical tables are only written by the full run).
OUT_TAG = os.environ.get("C2L_OUT_TAG", "")
RUN_STATUS = os.environ.get("C2L_STATUS", "ok")
RADIUS = 2.05
TAB = f"{WORK}/results/tables"
FIG = f"{WORK}/results/figures"
# Optional overrides exist so the logic can be exercised on synthetic/mock data
# without ever writing a mock table into the canonical results directory.
IN_PARQUET = os.environ.get("C2L_INPUT_PARQUET", f"{TAB}/visium_c2l_spot_abundances.parquet")
OUT_DIR = os.environ.get("C2L_OUT_DIR", TAB)


def outpath(stem):
    return f"{OUT_DIR}/{stem}{OUT_TAG}.csv"



IMMUNE_TYPES = ["T cell", "B cell", "NK cell", "macrophage", "monocyte/myeloid",
                "dendritic cell", "mast cell", "neutrophil", "plasma cell"]
CONTEXT_TYPES = ["fibroblast", "epithelial cell", "endothelial cell"]
ALL_TYPES = IMMUNE_TYPES + CONTEXT_TYPES

rng = np.random.default_rng(SEED)
t0 = time.time()

df = pd.read_parquet(IN_PARQUET)
df.index.name = "spot_barcode"
print("spots:", df.shape, flush=True)
print(f"RUN CONFIG N_PERM={N_PERM} N_BOOT={N_BOOT} OUT_TAG='{OUT_TAG}'", flush=True)

available = [c.replace("mean_", "") for c in df.columns if c.startswith("mean_")]
missing = [c for c in ALL_TYPES if c not in available]
print("requested cell types:", ALL_TYPES, flush=True)
print("missing from output:", missing, flush=True)
CELL_TYPES = [c for c in ALL_TYPES if c in available]

sections = sorted(df["section"].unique())
print(f"sections: {len(sections)}", flush=True)

# ---------------------------------------------------------------- graph + means
records_strat = []
neighbor_store = {}   # section -> (index array, neighbour-mean matrix, high idx, low idx, n_nb)
for sec in sections:
    sub = df[df["section"] == sec]
    hist = sub["histology"].iloc[0]
    patient = sub["patient"].iloc[0]
    xy = sub[["array_row", "array_col"]].to_numpy(dtype=float)
    tree = cKDTree(xy)
    nb = tree.query_ball_point(xy, r=RADIUS)
    n_nb = np.array([len(x) - 1 for x in nb])   # exclude self
    ab = sub[[f"mean_{c}" for c in CELL_TYPES]].to_numpy(dtype=np.float64)
    ab_q05 = sub[[f"q05_{c}" for c in CELL_TYPES]].to_numpy(dtype=np.float64)

    def _neighbour_mean(mat):
        out = np.full((len(nb), mat.shape[1]), np.nan)
        for i, inds in enumerate(nb):
            others = [j for j in inds if j != i]
            if len(others):
                out[i] = mat[others].mean(0)
        return out

    nb_mean = _neighbour_mean(ab)
    nb_q05 = _neighbour_mean(ab_q05)

    cd = sub["CD276_lognorm"].to_numpy(dtype=float)
    q25, q50, q75 = np.percentile(cd, [25, 50, 75])
    high = np.where(cd > q75)[0]
    low = np.where(cd < q25)[0]
    # ties at the percentile boundaries can make a group empty (e.g. >75% zeros)
    if len(high) == 0 or len(low) == 0:
        # deterministic fallback: rank-based split, keep top/bottom quarter
        order = np.argsort(cd, kind="stable")
        n = len(order)
        low = order[: n // 4]
        high = order[-(n // 4):]
        fallback = True
    else:
        fallback = False

    # spots without any neighbour can't contribute to a neighbourhood mean
    valid = n_nb > 0
    high = high[valid[high]]
    low = low[valid[low]]
    n_edge_1_5 = int(((n_nb > 0) & (n_nb < 6)).sum())
    n_isolated = int((~valid).sum())

    for label, idx in [("high", high), ("low", low)]:
        records_strat.append({
            "section": sec, "patient": patient, "histology": hist, "group": label,
            "n_spots": len(idx), "cd276_lognorm_mean": float(cd[idx].mean()) if len(idx) else np.nan,
            "cd276_lognorm_median": float(np.median(cd[idx])) if len(idx) else np.nan,
            "pct_cd276_positive": float((cd[idx] > 0).mean() * 100) if len(idx) else np.nan,
            "q25": q25, "q50": q50, "q75": q75, "rank_fallback": fallback,
            "n_spots_with_1_to_5_neighbours": n_edge_1_5, "n_isolated_spots": n_isolated,
            "n_spots_in_section": len(sub),
        })
    neighbor_store[sec] = dict(hist=hist, patient=patient, nb_mean=nb_mean, nb_q05=nb_q05,
                               high=high, low=low, n_nb=n_nb, n_edge_1_5=n_edge_1_5,
                               n_isolated=n_isolated, cd=cd, fallback=fallback)

STRAT_COLS = ["section", "patient", "histology", "group", "n_spots",
              "cd276_lognorm_mean", "cd276_lognorm_median", "pct_cd276_positive",
              "q25", "q50", "q75", "rank_fallback",
              "n_spots_with_1_to_5_neighbours", "n_isolated_spots",
              "n_spots_in_section"]
strat = checked_frame(records_strat, STRAT_COLS, "visium_neighborhood_stratification")
strat.to_csv(outpath("visium_neighborhood_stratification"), index=False)
print(strat.groupby(["histology", "group"])["n_spots"].describe().to_string(), flush=True)

# --------------------------------------------------------------- effect tables
def effect_table(metric="mean", histology=None, exclude_edge=False):
    rows = []
    for sec, d in neighbor_store.items():
        if histology is not None and d["hist"] != histology:
            continue
        mat = d["nb_mean"] if metric == "mean" else d["nb_q05"]
        hi, lo = d["high"], d["low"]
        if exclude_edge:
            hi = hi[d["n_nb"][hi] == 6]
            lo = lo[d["n_nb"][lo] == 6]
        if len(hi) < 3 or len(lo) < 3:
            continue
        hm = np.nanmean(mat[hi], axis=0)
        lm = np.nanmean(mat[lo], axis=0)
        for j, ct in enumerate(CELL_TYPES):
            rows.append({
                "metric": metric, "section": sec, "patient": d["patient"],
                "histology": d["hist"], "cell_type": ct,
                "n_high": len(hi), "n_low": len(lo),
                "n_edge_spots_1_to_5": d["n_edge_1_5"],
                "n_isolated_spots": d["n_isolated"],
                "mean_neighbor_high": hm[j], "mean_neighbor_low": lm[j],
                "abs_diff": hm[j] - lm[j],
                "pct_change": (hm[j] - lm[j]) / lm[j] * 100 if lm[j] > 0 else np.nan,
            })
    return pd.DataFrame(rows)

EFFECT_COLS = ["metric", "section", "patient", "histology", "cell_type",
               "n_high", "n_low", "n_edge_spots_1_to_5", "n_isolated_spots",
               "mean_neighbor_high", "mean_neighbor_low", "abs_diff", "pct_change"]
per_sec = checked_frame(effect_table("mean"), EFFECT_COLS,
                        "visium_neighborhood_immune_change")
per_sec.to_csv(outpath("visium_neighborhood_immune_change"), index=False)
per_sec_q05 = effect_table("q05")


def pooled_ratio(stat, cell_type, metric="mean", histology=None, exclude_edge=False):
    """Sample-weighted pooled percent change over sections."""
    num = den = 0.0
    for sec, d in neighbor_store.items():
        if histology is not None and d["hist"] != histology:
            continue
        mat = d["nb_mean"] if metric == "mean" else d["nb_q05"]
        j = CELL_TYPES.index(cell_type)
        hi, lo = d["high"], d["low"]
        if exclude_edge:
            hi = hi[d["n_nb"][hi] == 6]
            lo = lo[d["n_nb"][lo] == 6]
        if len(hi) < 3 or len(lo) < 3:
            continue
        num += mat[hi, j].sum() - mat[lo, j].sum()
        den += mat[lo, j].sum()
    return num / den * 100 if den > 0 else np.nan


def pooled_abs_diff(sec_list, cell_type, metric="mean"):
    """Pooled mean neighbour abundance difference (high - low), same weighting."""
    j = CELL_TYPES.index(cell_type)
    num = 0.0
    n = 0
    for sec in sec_list:
        d = neighbor_store[sec]
        mat = d["nb_mean"] if metric == "mean" else d["nb_q05"]
        hi, lo = d["high"], d["low"]
        if len(hi) < 3 or len(lo) < 3:
            continue
        num += mat[hi, j].sum() - mat[lo, j].sum()
        n += len(hi) + len(lo)
    return num / n if n else np.nan


def pooled_ratio_subset(sec_list, cell_type, metric="mean"):
    num = den = 0.0
    j = CELL_TYPES.index(cell_type)
    for sec in sec_list:
        d = neighbor_store[sec]
        mat = d["nb_mean"] if metric == "mean" else d["nb_q05"]
        hi, lo = d["high"], d["low"]
        if len(hi) < 3 or len(lo) < 3:
            continue
        num += mat[hi, j].sum() - mat[lo, j].sum()
        den += mat[lo, j].sum()
    return num / den * 100 if den > 0 else np.nan


# ------------------------------------------------- robustness: bootstrap + perm
def bootstrap_sections(sec_list, cell_type, metric="mean", n_boot=N_BOOT):
    if len(sec_list) < 3:
        return np.nan, np.nan
    vals = []
    for _ in range(n_boot):
        samp = rng.choice(sec_list, size=len(sec_list), replace=True)
        v = pooled_ratio_subset(samp, cell_type, metric=metric)
        if np.isfinite(v):
            vals.append(v)
    if len(vals) < 10:
        return np.nan, np.nan
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def permutation_p(sec_list, cell_type, metric="mean", n_perm=N_PERM):
    """Within-section label shuffle of high/low membership (group sizes fixed)."""
    observed = pooled_ratio_subset(sec_list, cell_type, metric=metric)
    if not np.isfinite(observed):
        return np.nan, np.nan
    j = CELL_TYPES.index(cell_type)
    null = np.zeros(n_perm)
    for b in range(n_perm):
        num = den = 0.0
        for sec in sec_list:
            d = neighbor_store[sec]
            mat = (d["nb_mean"] if metric == "mean" else d["nb_q05"])[:, j]
            allidx = np.concatenate([d["high"], d["low"]])
            if len(allidx) == 0:
                continue
            perm = rng.permutation(len(allidx))
            hi = allidx[perm[: len(d["high"])]]
            lo = allidx[perm[len(d["high"]):]]
            num += mat[hi].sum() - mat[lo].sum()
            den += mat[lo].sum()
        null[b] = num / den * 100 if den > 0 else np.nan
    p = (np.sum(np.abs(null) >= abs(observed)) + 1) / (n_perm + 1)
    return observed, p


robust_rows = []
for histology in ["tumor", "adjacent-normal"]:
    sec_list = [s for s, d in neighbor_store.items() if d["hist"] == histology]
    for metric in ["mean", "q05"]:
        for ct in CELL_TYPES:
            obs = pooled_ratio(None, ct, metric=metric, histology=histology)
            lo, hi = bootstrap_sections(sec_list, ct, metric=metric)
            _, p = permutation_p(sec_list, ct, metric=metric)
            src = per_sec if metric == "mean" else per_sec_q05
            sec_vals = src[(src.histology == histology) & (src.cell_type == ct)]
            n_pos = int((sec_vals["pct_change"] > 0).sum())
            n_sec = int(sec_vals["pct_change"].notna().sum())
            # donor-level direction
            donor_vals = {}
            for pat in sorted({d["patient"] for d in neighbor_store.values() if d["hist"] == histology}):
                plist = [s for s in sec_list if neighbor_store[s]["patient"] == pat]
                donor_vals[pat] = pooled_ratio_subset(plist, ct, metric=metric)
            n_hi_tot = sum(len(neighbor_store[s]["high"]) for s in sec_list
                           if len(neighbor_store[s]["high"]) >= 3
                           and len(neighbor_store[s]["low"]) >= 3)
            n_lo_tot = sum(len(neighbor_store[s]["low"]) for s in sec_list
                           if len(neighbor_store[s]["high"]) >= 3
                           and len(neighbor_store[s]["low"]) >= 3)
            robust_rows.append({
                "histology": histology, "metric": metric, "cell_type": ct,
                "immune_compartment": "immune" if ct in IMMUNE_TYPES else "context",
                "pooled_pct_change": obs,
                "pooled_abs_diff": pooled_abs_diff(sec_list, ct, metric=metric),
                "n_high_spots_total": n_hi_tot, "n_low_spots_total": n_lo_tot,
                "bootstrap_ci_low": lo, "bootstrap_ci_high": hi,
                "permutation_p": p, "n_sections": n_sec,
                "n_sections_positive": n_pos,
                "pct_sections_positive": n_pos / n_sec * 100 if n_sec else np.nan,
                "median_section_pct_change": float(sec_vals["pct_change"].median()) if n_sec else np.nan,
                "n_donors": len(donor_vals),
                "n_donors_positive": int(sum(1 for v in donor_vals.values() if np.isfinite(v) and v > 0)),
                "donor_pct_changes": ";".join(f"{k}:{v:.1f}" for k, v in donor_vals.items() if np.isfinite(v)),
            })

ROBUST_COLS = ["histology", "metric", "cell_type", "immune_compartment",
               "pooled_pct_change", "pooled_abs_diff", "n_high_spots_total",
               "n_low_spots_total", "bootstrap_ci_low", "bootstrap_ci_high",
               "permutation_p", "n_sections", "n_sections_positive",
               "pct_sections_positive", "median_section_pct_change",
               "n_donors", "n_donors_positive", "donor_pct_changes"]
robust = checked_frame(robust_rows, ROBUST_COLS, "visium_neighborhood_robustness")
assert len(robust) == 2 * 2 * len(CELL_TYPES), (
    "robustness table should have histology x metric x cell_type rows: "
    f"{len(robust)} vs {2 * 2 * len(CELL_TYPES)}")
robust.to_csv(outpath("visium_neighborhood_robustness"), index=False)
print(robust[robust.metric == "mean"].to_string(index=False), flush=True)

# ---------------------------------------------------- edge-spot sensitivity row
sens_rows = []
for histology in ["tumor", "adjacent-normal"]:
    sec_list = [s for s, d in neighbor_store.items() if d["hist"] == histology]
    # Full CELL_TYPES (immune + context), not IMMUNE_TYPES only: the earlier
    # version silently dropped fibroblast/epithelial/endothelial, and the report
    # then claimed an endothelial result that was not in the table.
    for ct in CELL_TYPES:
        v_all = pooled_ratio(None, ct, histology=histology)
        v_edge = pooled_ratio(None, ct, histology=histology, exclude_edge=True)
        sens_rows.append({"histology": histology, "cell_type": ct,
                          "pooled_pct_change_all_spots": v_all,
                          "pooled_pct_change_only_6_neighbour_spots": v_edge,
                          "n_isolated_spots": int(sum(d['n_isolated'] for d in neighbor_store.values() if d['hist'] == histology)),
                          "n_spots_with_1_to_5_neighbours": int(sum(d['n_edge_1_5'] for d in neighbor_store.values() if d['hist'] == histology))})
SENS_COLS = ["histology", "cell_type", "pooled_pct_change_all_spots",
             "pooled_pct_change_only_6_neighbour_spots", "n_isolated_spots",
             "n_spots_with_1_to_5_neighbours"]
sens = checked_frame(sens_rows, SENS_COLS, "visium_neighborhood_edge_spot_sensitivity")
assert len(sens) == 2 * len(CELL_TYPES), (
    f"edge table should have 2 histologies x {len(CELL_TYPES)} types = "
    f"{2 * len(CELL_TYPES)} rows, got {len(sens)}")
sens.to_csv(outpath("visium_neighborhood_edge_spot_sensitivity"), index=False)

log_run(step=("neighborhood_analysis_probe" if OUT_TAG else "neighborhood_analysis"), status=RUN_STATUS, wall_time_s=round(time.time() - t0, 1),
        n_cells=len(df), detail=(f"k=6 hex neighbours radius={RADIUS}; per-section CD276 log1p CP10K "
                                 f"top/bottom quartile; {N_PERM} permutations; {N_BOOT} section bootstraps; "
                                 f"tumour+adjacent-normal; mean and q05 abundances; OUT_TAG={OUT_TAG!r}"))
print("DONE", flush=True)
