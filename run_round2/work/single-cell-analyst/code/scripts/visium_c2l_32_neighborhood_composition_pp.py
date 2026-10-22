"""
POST-HOC additive composition endpoint for Panel 4E/S5B (sensitivity only).

Why this exists
---------------
script 31 reports a pooled *percent change* of relative cell-type fractions.
That estimator divides by the summed low-group fraction, so sections are weighted
differently for each cell type and the values do not sum to zero across a
composition (see the regenerated sums printed by script 31). It is therefore not
a valid composition summary on its own.

This script uses an additive endpoint instead: for every section,
    pp_diff = 100 * ( mean neighbour fraction in high spots
                      - mean neighbour fraction in low spots )
i.e. percentage points. The pooled estimate is the equal-weight mean of the
per-section pp differences (sections with >=3 high and >=3 low spots). Because
every spot's fractions are normalised by the same 14-compartment total, the pp
differences across ALL 14 compartments sum to zero by construction. The sum is
computed over the emitted rows (all 14) and asserted; the earlier version
emitted only 12 types, so the printed "~0" check was invalid.

Same graph, same per-section CD276 quartile split (with the rank fallback),
same section bootstrap and within-section label-shuffle permutation as the
primary analysis. Two variants: all spots with >=1 neighbour, and only spots
with exactly 6 neighbours.

For completeness the same equal-section-weight statistic is also computed for
total neighbour abundance (percent change), which is more robust to a single
section dominating the pooled ratio of script 31.

Output
------
results/tables/visium_neighborhood_composition_pp_difference.csv
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
# ALL 14 compartments, so the additive pp endpoint reconciles to zero.
TYPES = [c for c in IMMUNE + CONTEXT + MALIGNANT_STROMAL if c in avail]
assert sorted(TYPES) == sorted(avail), (
    f"composition must cover all {len(avail)} compartments; missing "
    f"{sorted(set(avail) - set(TYPES))}")

store = {}
for sec, sub in df.groupby("section", observed=True):
    xy = sub[["array_row", "array_col"]].to_numpy(float)
    nb = cKDTree(xy).query_ball_point(xy, r=RADIUS)
    n_nb = np.array([len(x) - 1 for x in nb])
    ab = sub[[f"mean_{c}" for c in avail]].to_numpy(float)
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

    # nb_rel must have exactly one column per entry of TYPES, in TYPES order,
    # so downstream j-indexed lookups are unambiguous.
    nb_rel = nb_mean(rel)[:, [avail.index(c) for c in TYPES]]
    assert nb_rel.shape[1] == len(TYPES), (sec, nb_rel.shape, len(TYPES))
    assert np.isfinite(nb_rel[high]).all() and np.isfinite(nb_rel[low]).all(), (
        f"{sec}: non-finite composition fractions in the contrast groups")
    store[sec] = {
        "hist": sub["histology"].iloc[0], "patient": sub["patient"].iloc[0],
        "nb_rel": nb_rel,
        "nb_total": nb_mean(tot[:, None])[:, 0],
        "high": high, "low": low, "n_nb": n_nb,
    }
print("sections prepared", flush=True)


def groups(d, variant):
    hi, lo = d["high"], d["low"]
    if variant == "six_neighbour_only":
        hi = hi[d["n_nb"][hi] == 6]
        lo = lo[d["n_nb"][lo] == 6]
    return hi, lo


def usable(sec_list, variant):
    out = []
    for s in sec_list:
        hi, lo = groups(store[s], variant)
        if len(hi) >= 3 and len(lo) >= 3:
            out.append(s)
    return out


def section_pp(d, variant):
    """Per-section pp difference for every cell type (vectorised)."""
    hi, lo = groups(d, variant)
    if len(hi) < 3 or len(lo) < 3:
        return None
    return (np.nanmean(d["nb_rel"][hi], axis=0)
            - np.nanmean(d["nb_rel"][lo], axis=0)) * 100


def section_total_pct(d, variant):
    hi, lo = groups(d, variant)
    if len(hi) < 3 or len(lo) < 3:
        return None
    hm, lm = d["nb_total"][hi].mean(), d["nb_total"][lo].mean()
    return (hm - lm) / lm * 100 if lm > 0 else None


def pooled_pp(sec_list, variant):
    vals = [section_pp(store[s], variant) for s in sec_list]
    vals = [v for v in vals if v is not None]
    return np.mean(vals, axis=0) if vals else None


def pooled_total(sec_list, variant):
    vals = [section_total_pct(store[s], variant) for s in sec_list]
    vals = [v for v in vals if v is not None and np.isfinite(v)]
    return float(np.mean(vals)) if vals else np.nan


def boot_ci(sec_list, variant, kind, j=None):
    if len(sec_list) < 3:
        return np.nan, np.nan
    vals = []
    for _ in range(N_BOOT):
        samp = list(rng.choice(sec_list, size=len(sec_list), replace=True))
        if kind == "pp":
            v = pooled_pp(samp, variant)
            v = np.nan if v is None else v[j]
        else:
            v = pooled_total(samp, variant)
        if np.isfinite(v):
            vals.append(v)
    if len(vals) < 10:
        return np.nan, np.nan
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def perm_p(sec_list, variant, kind, j=None):
    if kind == "pp":
        obs = pooled_pp(sec_list, variant)
        if obs is None:
            return np.nan
        obs = obs[j]
    else:
        obs = pooled_total(sec_list, variant)
        if not np.isfinite(obs):
            return np.nan
    null = np.full(N_PERM, np.nan)
    for b in range(N_PERM):
        acc = []
        for s in sec_list:
            d = store[s]
            hi, lo = groups(d, variant)
            allidx = np.concatenate([hi, lo])
            if len(allidx) == 0:
                continue
            p = rng.permutation(len(allidx))
            h, l = allidx[p[:len(hi)]], allidx[p[len(hi):]]
            if kind == "pp":
                acc.append((np.nanmean(d["nb_rel"][h], axis=0)
                            - np.nanmean(d["nb_rel"][l], axis=0)) * 100)
            else:
                hm, lm = d["nb_total"][h].mean(), d["nb_total"][l].mean()
                if lm > 0:
                    acc.append((hm - lm) / lm * 100)
        if acc:
            v = np.mean(acc, axis=0)
            null[b] = v[j] if kind == "pp" else v
    null = null[np.isfinite(null)]
    if len(null) < 10:
        return np.nan
    return (np.sum(np.abs(null) >= abs(obs)) + 1) / (len(null) + 1)


rows = []
for hist in ["tumor", "adjacent-normal"]:
    sec_all = [s for s, d in store.items() if d["hist"] == hist]
    for variant in ["all_spots", "six_neighbour_only"]:
        sec_list = usable(sec_all, variant)
        pp = pooled_pp(sec_list, variant)
        tot = pooled_total(sec_list, variant)
        # section-level values for sign consistency and median
        sec_pp = {}
        sec_tot = {}
        for s in sec_list:
            v = section_pp(store[s], variant)
            if v is not None:
                sec_pp[s] = v
            tv = section_total_pct(store[s], variant)
            if tv is not None and np.isfinite(tv):
                sec_tot[s] = tv
        donors = sorted({store[s]["patient"] for s in sec_list})
        for j, ct in enumerate(TYPES):
            lo, hi = boot_ci(sec_list, variant, "pp", j)
            p = perm_p(sec_list, variant, "pp", j)
            sv = np.array([sec_pp[s][j] for s in sec_list if s in sec_pp])
            dvals = []
            for pat in donors:
                pv = [sec_pp[s][j] for s in sec_list
                      if s in sec_pp and store[s]["patient"] == pat]
                if pv:
                    dvals.append(np.mean(pv))
            rows.append({
                "histology": hist, "variant": variant,
                "statistic": "composition_pp", "cell_type": ct,
                "estimate": float(pp[j]) if pp is not None else np.nan,
                "ci_low": lo, "ci_high": hi, "permutation_p": p,
                "median_section_estimate": float(np.median(sv)) if len(sv) else np.nan,
                "n_sections": len(sv),
                "n_sections_positive": int((sv > 0).sum()),
                "n_donors": len(dvals),
                "n_donors_positive": int(sum(1 for v in dvals if v > 0)),
            })
        lo, hi = boot_ci(sec_list, variant, "total")
        p = perm_p(sec_list, variant, "total")
        tv = np.array(list(sec_tot.values()))
        dvals = []
        for pat in donors:
            pv = [sec_tot[s] for s in sec_list
                  if s in sec_tot and store[s]["patient"] == pat]
            if pv:
                dvals.append(np.mean(pv))
        rows.append({
            "histology": hist, "variant": variant,
            "statistic": "total_abundance_pct", "cell_type": "ALL_CELL_TYPES",
            "estimate": tot, "ci_low": lo, "ci_high": hi, "permutation_p": p,
            "median_section_estimate": float(np.median(tv)) if len(tv) else np.nan,
            "n_sections": len(tv),
            "n_sections_positive": int((tv > 0).sum()),
            "n_donors": len(dvals),
            "n_donors_positive": int(sum(1 for v in dvals if v > 0)),
        })
    print(f"done {hist}", flush=True)

OUT_COLS = ["histology", "variant", "statistic", "cell_type", "estimate",
            "ci_low", "ci_high", "permutation_p", "median_section_estimate",
            "n_sections", "n_sections_positive", "n_donors",
            "n_donors_positive"]
out = checked_frame(rows, OUT_COLS, "visium_neighborhood_composition_pp_difference")
expl = len(TYPES)
assert len(out) == 2 * 2 * (expl + 1), (
    f"expected 2 histologies x 2 variants x ({expl} pp rows + 1 total row), "
    f"got {len(out)}")
out.to_csv(f"{TAB}/visium_neighborhood_composition_pp_difference.csv", index=False)

# With all 14 compartments emitted the pp differences close to zero by
# construction. Assert it rather than merely printing a "should be ~0" note.
for variant in ["all_spots", "six_neighbour_only"]:
    s = out[(out.variant == variant) & (out.statistic == "composition_pp")]
    check = s.groupby("histology")["estimate"].sum()
    counts = s.groupby("histology")["estimate"].count()
    print(f"{variant}: sum of pp differences over all compartments "
          f"(0 by construction)")
    print(check.round(6).to_string(), flush=True)
    print("compartments per histology:", counts.to_dict(), flush=True)
    if not (check.abs() < 1e-6).all():
        raise AssertionError(f"{variant}: pp residual not zero after 14-component "
                             f"sum: {check.to_dict()}")
    if not (counts == expl).all():
        raise AssertionError(f"{variant}: expected {expl} compartments per "
                             f"histology, got {counts.to_dict()}")

print(out.round(3).to_string(index=False), flush=True)
log_run(step="neighborhood_composition_pp", status="ok",
        wall_time_s=round(time.time() - t0, 1), n_cells=len(df),
        detail=("POST-HOC additive composition endpoint: equal-section-weight mean of "
                "per-section high-minus-low neighbour fraction (percentage points); "
                f"{N_PERM} permutations/{N_BOOT} bootstraps; all spots and "
                "6-neighbour-only variants; plus equal-weight total abundance % change"))
print("DONE", flush=True)
