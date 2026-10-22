"""
POST-HOC sensitivity for Panel 4E/S5B (NOT the pre-specified primary analysis).

Motivation: the primary endpoint is the absolute neighbour cell abundance, which
is sensitive to capture depth / local cell density. CD276 log1p(CP10K) still
correlates with total counts (Spearman ~0.31 in tumour), and total abundance
correlates with total counts (~0.40). A high-CD276 neighbourhood could therefore
show higher absolute immune abundance simply because it is a deeper, cell-denser
neighbourhood rather than because its immune composition differs.

This script repeats the same graph, the same per-section rank quartile split and
the same section bootstrap / within-section label-shuffle permutation, but asks
two different questions:
  1. relative_composition: neighbour cell-type fraction (ct / total abundance),
     then the high-vs-low percent change. This removes the cell-density scale.
     Rows are emitted for ALL 14 compartments (including `malignant cell` and
     `stromal/other`); the denominator is the sum over those same 14.
  2. total_abundance: neighbour total abundance (all 14 cell types summed).
     A large positive value means high-CD276 neighbourhoods are simply denser.

Two spatial variants are reported: all spots with >=1 neighbour, and only spots
with exactly 6 neighbours (interior), because the primary edge-spot sensitivity
showed sign changes in tumour.

Output
------
results/tables/visium_neighborhood_composition_sensitivity.csv
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
N_PERM = 1000
N_BOOT = 1000
RADIUS = 2.05
TAB = f"{WORK}/results/tables"

IMMUNE = ["T cell", "B cell", "NK cell", "macrophage", "monocyte/myeloid",
          "dendritic cell", "mast cell", "neutrophil", "plasma cell"]
CONTEXT = ["fibroblast", "epithelial cell", "endothelial cell"]
MALIGNANT_STROMAL = ["malignant cell", "stromal/other"]

rng = np.random.default_rng(SEED)
t0 = time.time()
df = pd.read_parquet(f"{TAB}/visium_c2l_spot_abundances.parquet")
avail = [c.replace("mean_", "") for c in df.columns if c.startswith("mean_")]
ALL14 = avail
# Report ALL 14 compartments. The earlier version reported 12 and silently
# dropped `malignant cell` and `stromal/other`, so the percentage-point
# differences could not reconcile to the composition denominator.
TYPES = [c for c in IMMUNE + CONTEXT + MALIGNANT_STROMAL if c in avail]
assert sorted(TYPES) == sorted(ALL14), (
    f"composition must cover all {len(ALL14)} compartments; missing "
    f"{sorted(set(ALL14) - set(TYPES))}")

store = {}
for sec, sub in df.groupby("section", observed=True):
    xy = sub[["array_row", "array_col"]].to_numpy(float)
    nb = cKDTree(xy).query_ball_point(xy, r=RADIUS)
    n_nb = np.array([len(x) - 1 for x in nb])
    ab = sub[[f"mean_{c}" for c in ALL14]].to_numpy(float)
    tot = ab.sum(1)
    rel = np.divide(ab, tot[:, None], out=np.full_like(ab, np.nan),
                    where=tot[:, None] > 0)
    cd = sub["CD276_lognorm"].to_numpy(float)
    q25, q75 = np.percentile(cd, [25, 75])
    high = np.where(cd > q75)[0]
    low = np.where(cd < q25)[0]
    if len(high) == 0 or len(low) == 0:
        order = np.argsort(cd, kind="stable")
        n = len(order)
        low, high = order[: n // 4], order[-(n // 4):]
    valid = n_nb > 0
    high, low = high[valid[high]], low[valid[low]]

    def nb_mean(mat):
        out = np.full((len(nb), mat.shape[1]), np.nan)
        for i, inds in enumerate(nb):
            others = [j for j in inds if j != i]
            if others:
                out[i] = mat[others].mean(0)
        return out

    # nb_rel must have exactly one column per entry of TYPES; ALL14 contains
    # extra compartments (malignant/stromal), so subset and assert alignment.
    nb_rel = nb_mean(rel)[:, [ALL14.index(c) for c in TYPES]]
    assert nb_rel.shape[1] == len(TYPES), (nb_rel.shape, len(TYPES))
    store[sec] = {
        "hist": sub["histology"].iloc[0], "patient": sub["patient"].iloc[0],
        "nb_rel": nb_rel, "nb_total": nb_mean(tot[:, None])[:, 0],
        "high": high, "low": low, "n_nb": n_nb,
    }
print("sections prepared", flush=True)
print("TYPES (column order):", TYPES, flush=True)


def groups(d, variant):
    hi, lo = d["high"], d["low"]
    if variant == "six_neighbour_only":
        hi = hi[d["n_nb"][hi] == 6]
        lo = lo[d["n_nb"][lo] == 6]
    return hi, lo


def pooled(sec_list, endpoint, j, variant):
    num = den = 0.0
    for sec in sec_list:
        d = store[sec]
        hi, lo = groups(d, variant)
        if len(hi) < 3 or len(lo) < 3:
            continue
        mat = d["nb_rel"][:, j] if endpoint == "relative_composition" else d["nb_total"]
        num += mat[hi].sum() - mat[lo].sum()
        den += mat[lo].sum()
    return num / den * 100 if den > 0 else np.nan


def boot(sec_list, endpoint, j, variant):
    if len(sec_list) < 3:
        return np.nan, np.nan
    vals = []
    for _ in range(N_BOOT):
        samp = rng.choice(sec_list, size=len(sec_list), replace=True)
        v = pooled(samp, endpoint, j, variant)
        if np.isfinite(v):
            vals.append(v)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))
            if len(vals) >= 10 else (np.nan, np.nan))


def perm_p(sec_list, endpoint, j, variant):
    obs = pooled(sec_list, endpoint, j, variant)
    if not np.isfinite(obs):
        return np.nan
    null = np.zeros(N_PERM)
    for b in range(N_PERM):
        num = den = 0.0
        for sec in sec_list:
            d = store[sec]
            hi, lo = groups(d, variant)
            mat = d["nb_rel"][:, j] if endpoint == "relative_composition" else d["nb_total"]
            allidx = np.concatenate([hi, lo])
            if len(allidx) == 0:
                continue
            p = rng.permutation(len(allidx))
            h, l = allidx[p[:len(hi)]], allidx[p[len(hi):]]
            num += mat[h].sum() - mat[l].sum()
            den += mat[l].sum()
        null[b] = num / den * 100 if den > 0 else np.nan
    return (np.sum(np.abs(null) >= abs(obs)) + 1) / (N_PERM + 1)


rows = []
for hist in ["tumor", "adjacent-normal"]:
    sec_list = [s for s, d in store.items() if d["hist"] == hist]
    for variant in ["all_spots", "six_neighbour_only"]:
        endpoints = [("total_abundance", [None]),
                     ("relative_composition", list(range(len(TYPES))))]
        for endpoint, js in endpoints:
            for j in js:
                ct = "ALL_CELL_TYPES" if j is None else TYPES[j]
                v = pooled(sec_list, endpoint, j, variant)
                lo, hi = boot(sec_list, endpoint, j, variant)
                p = perm_p(sec_list, endpoint, j, variant)
                secpos = 0
                nsec = 0
                for sec in sec_list:
                    d = store[sec]
                    h, l = groups(d, variant)
                    if len(h) < 3 or len(l) < 3:
                        continue
                    mat = d["nb_rel"][:, j] if endpoint == "relative_composition" else d["nb_total"]
                    sv = ((mat[h].mean() - mat[l].mean()) / mat[l].mean() * 100
                          if mat[l].mean() > 0 else np.nan)
                    if np.isfinite(sv):
                        nsec += 1
                        secpos += int(sv > 0)
                dpos = 0
                nd = 0
                for pat in sorted({d["patient"] for s, d in store.items()
                                   if d["hist"] == hist}):
                    plist = [s for s in sec_list if store[s]["patient"] == pat]
                    dv = pooled(plist, endpoint, j, variant)
                    if np.isfinite(dv):
                        nd += 1
                        dpos += int(dv > 0)
                rows.append({
                    "histology": hist, "variant": variant, "endpoint": endpoint,
                    "cell_type": ct,
                    "pooled_pct_change": v,
                    "bootstrap_ci_low": lo, "bootstrap_ci_high": hi,
                    "permutation_p": p, "n_sections": nsec,
                    "n_sections_positive": secpos,
                    "n_donors": nd, "n_donors_positive": dpos,
                })
        print(f"done {hist} {variant}", flush=True)

OUT_COLS = ["histology", "variant", "endpoint", "cell_type", "pooled_pct_change",
            "bootstrap_ci_low", "bootstrap_ci_high", "permutation_p",
            "n_sections", "n_sections_positive", "n_donors", "n_donors_positive"]
out = checked_frame(rows, OUT_COLS, "visium_neighborhood_composition_sensitivity")
assert len(out) == 2 * 2 * (1 + len(TYPES)), (
    f"expected 2 histologies x 2 variants x (1 total + {len(TYPES)} types) rows, "
    f"got {len(out)}")
out.to_csv(f"{TAB}/visium_neighborhood_composition_sensitivity.csv", index=False)
print(out[out.endpoint == "total_abundance"].to_string(index=False), flush=True)
print(out[(out.endpoint == "relative_composition")
          & (out.variant == "all_spots")].to_string(index=False), flush=True)
log_run(step="neighborhood_composition_sensitivity", status="ok",
        wall_time_s=round(time.time() - t0, 1), n_cells=len(df),
        detail=("POST-HOC: relative neighbour composition and total neighbour abundance; "
                f"same graph/stratification; {N_PERM} permutations/{N_BOOT} bootstraps; "
                "all spots and 6-neighbour-only variants"))
print("DONE", flush=True)
