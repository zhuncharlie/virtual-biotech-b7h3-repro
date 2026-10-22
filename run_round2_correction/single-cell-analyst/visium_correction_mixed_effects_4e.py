"""
Targeted correction, Task A: fit the paper's Figure 4E statistical model.

Paper caption (verbatim ground truth):
  "Bar plot quantifies the percent change in neighbor immune abundance between
   top and bottom quartile of B7-H3-expressing spots across 12 LUAD tumor
   samples. Significance was assessed using a mixed-effects model adjusting for
   total UMI count, fibroblast abundance, and malignant epithelial abundance
   fixed effects, with random effects at the sample-level."

Model fitted here (primary, tumour sections only):
  neighbour_mean_abundance(cell type) ~ cd276_group(high/low)
        + z(log1p(total_counts)) + z(mean_fibroblast)
        + z(mean_malignant cell)
        + (1 | section)
  REML, statsmodels MixedLM, Wald z p-values.

Environment bridge (documented because the two Python envs are split):
  The pandas-2.3.3/statsmodels env has NO parquet reader; pyarrow 19.0 in
  `qlib_real` crashes on this file ("Repetition level histogram size
  mismatch"). pyarrow 20.0 in `vbt` reads it correctly. The parquet was
  therefore exported once, with `conda run -n vbt`, to
  data/processed/visium_c2l_spot_abundances.csv (47,448 rows x 39 cols), and
  this script reads that CSV. No package was installed.

Inputs (read-only source run):
  results/tables/visium_c2l_spot_abundances.parquet (exported above)
  results/tables/visium_spot_qc_metrics.csv (total counts duplicate; not
      needed because total_counts is in the abundance table; verified equal)
  results/tables/visium_c2l_cd276_stratification_audit.csv (per-section
      stratification diagnostics, used only as a cross-check)

Outputs (this run):
  results/tables/visium_correction_mixed_effects_4e.csv
  results/tables/visium_correction_mixed_effects_4e_sensitivity.csv
  results/tables/visium_correction_mixed_effects_4e_group_construction.csv
  results/reports/visium_correction_mixed_effects_4e_fit_log.txt

Reused neighbourhood logic: k=6 hex lattice via cKDTree on (array_row,
array_col), hard radius 2.05, self excluded (identical to
visium_c2l_30_neighborhood_analysis.py).
"""
import json
import os
import sys
import time
import traceback

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
import statsmodels.formula.api as smf

SEED = 42
np.random.seed(SEED)

ROOT = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261022-094819-this-is-a-targeted-correction-pa-d24cb49b/work/"
        "single-cell-analyst")
CSV = f"{ROOT}/data/processed/visium_c2l_spot_abundances.csv"
TAB = f"{ROOT}/results/tables"
REP = f"{ROOT}/results/reports"
LOG = f"{REP}/visium_correction_mixed_effects_4e_fit_log.txt"
os.makedirs(TAB, exist_ok=True)
os.makedirs(REP, exist_ok=True)

RADIUS = 2.05

IMMUNE_TYPES = ["T cell", "B cell", "NK cell", "macrophage",
                "monocyte/myeloid", "dendritic cell", "mast cell",
                "neutrophil", "plasma cell"]
PAPER_NAMED = {"T cell", "macrophage", "monocyte/myeloid", "dendritic cell"}

_t0 = time.time()
_log_lines = []


def log(msg):
    print(msg, flush=True)
    _log_lines.append(str(msg))


# ----------------------------------------------------------------- load
log(f"RUN START {time.strftime('%Y-%m-%d %H:%M:%S')}")
log(f"script={os.path.abspath(__file__)}")
df = pd.read_csv(CSV)
log(f"loaded {df.shape[0]} spots x {df.shape[1]} columns from CSV export")
assert len(df) == 47448, f"row count {len(df)} != 47448"
assert df["spot_barcode"].is_unique
if "qc_pass" in df.columns:
    log(f"qc_pass values: {df['qc_pass'].value_counts().to_dict()}")
df = df[df["qc_pass"].astype(str).str.lower().isin(["true", "1"])].copy()
log(f"after qc_pass filter: {len(df)} spots")

for ct in IMMUNE_TYPES:
    assert f"mean_{ct}" in df.columns, f"missing mean_{ct}"

# ------------------------------------------------------- neighbourhood graph
# Exact logic from visium_c2l_30_neighborhood_analysis.py.
df = df.reset_index(drop=True)
nb_mean = {ct: np.full(len(df), np.nan) for ct in IMMUNE_TYPES + ["fibroblast", "malignant cell"]}
n_nb = np.zeros(len(df), dtype=int)
section_index = {}
for sec, idx in df.groupby("section").groups.items():
    idx = np.asarray(idx)
    section_index[sec] = idx
    sub = df.loc[idx]
    xy = sub[["array_row", "array_col"]].to_numpy(dtype=float)
    tree = cKDTree(xy)
    nbrs = tree.query_ball_point(xy, r=RADIUS)
    n_local_nb = np.array([len(x) - 1 for x in nbrs])
    n_nb[idx] = n_local_nb
    for ct in IMMUNE_TYPES + ["fibroblast", "malignant cell"]:
        mat = sub[f"mean_{ct}"].to_numpy(dtype=np.float64)
        out = np.full(len(sub), np.nan)
        for i, inds in enumerate(nbrs):
            others = [j for j in inds if j != i]
            if others:
                out[i] = mat[others].mean()
        nb_mean[ct][idx] = out

df["n_neighbours"] = n_nb
for ct in IMMUNE_TYPES + ["fibroblast", "malignant cell"]:
    df[f"nb_{ct}"] = nb_mean[ct]

log("neighbour counts: " + json.dumps(
    {k: int(v) for k, v in pd.Series(n_nb).value_counts().sort_index().items()}))

# --------------------------------------------- per-section CD276 high/low
# Reuse the deterministic rank fallback exactly as the source script: strict
# >q75 / <q25 first; if either tail is empty (ties at zero), use the top and
# bottom 25% by CD276 rank.
group_rows = []
g = np.full(len(df), "", dtype=object)
for sec, idx in section_index.items():
    cd = df.loc[idx, "CD276_lognorm"].to_numpy(dtype=float)
    q25, q50, q75 = np.percentile(cd, [25, 50, 75])
    high = np.where(cd > q75)[0]
    low = np.where(cd < q25)[0]
    fallback = False
    if len(high) == 0 or len(low) == 0:
        order = np.argsort(cd, kind="stable")
        n = len(order)
        low = order[: n // 4]
        high = order[-(n // 4):]
        fallback = True
    local = np.array([""] * len(idx), dtype=object)
    local[high] = "high"
    local[low] = "low"
    g[idx] = local
    group_rows.append({
        "section": sec, "patient": df.loc[idx[0], "patient"],
        "histology": df.loc[idx[0], "histology"], "n_spots": len(idx),
        "q25": q25, "q50": q50, "q75": q75,
        "rank_fallback_used": fallback,
        "n_high_all": len(high), "n_low_all": len(low),
        "n_high_with_neighbour": int(((local == "high") & (n_nb[idx] > 0)).sum()),
        "n_low_with_neighbour": int(((local == "low") & (n_nb[idx] > 0)).sum()),
        "cd276_median_high": float(np.median(cd[high])) if len(high) else np.nan,
        "cd276_median_low": float(np.median(cd[low])) if len(low) else np.nan,
        "pct_positive_high": float((cd[high] > 0).mean() * 100) if len(high) else np.nan,
        "pct_positive_low": float((cd[low] > 0).mean() * 100) if len(low) else np.nan,
        "median_depth_high": float(df.loc[idx[high], "total_counts"].median()) if len(high) else np.nan,
        "median_depth_low": float(df.loc[idx[low], "total_counts"].median()) if len(low) else np.nan,
    })
df["cd276_group"] = g
groups_df = pd.DataFrame(group_rows)
groups_df.to_csv(f"{TAB}/visium_correction_mixed_effects_4e_group_construction.csv", index=False)
log(f"group construction: {groups_df[['histology','section','n_high_all','n_low_all','rank_fallback_used']].to_string(index=False)}")

# detection groups (sensitivity): CD276_counts > 0 vs == 0
df["cd276_detected"] = np.where(df["CD276_counts"] > 0, "positive", "zero")

# ------------------------------------------------------------- model fitting
def zscore(x):
    x = np.asarray(x, dtype=float)
    sd = x.std()
    return (x - x.mean()) / sd if sd > 0 else np.zeros_like(x)


def fit_one(data, response, group_col, cov_cols, groups_col, vc_formula=None,
            high_label="high"):
    d = data.dropna(subset=[response] + cov_cols + ["log_depth"] + [group_col, groups_col]).copy()
    # keep only the two modelled levels (drops "" for the quartile split);
    # for the detection split the levels are "positive"/"zero".
    d = d[d[group_col].isin([high_label,
                            "low" if high_label == "high" else "zero"])]
    if d[group_col].nunique() < 2:
        raise ValueError("group has a single level after filtering")
    d["y"] = d[response].astype(float)
    for c in cov_cols:
        d["z_" + c] = zscore(d[c])
    terms = " + ".join("z_" + c for c in cov_cols)
    d["grp"] = (d[group_col] == high_label).astype(int)
    fml = f"y ~ grp + {terms}"
    kw = dict(groups=d[groups_col])
    if vc_formula is not None:
        kw["vc_formula"] = vc_formula
    md = smf.mixedlm(fml, d, re_formula="1", **kw)
    try:
        res = md.fit(reml=True, method="lbfgs", maxiter=300)
    except Exception:
        res = md.fit(reml=True, method="powell", maxiter=300)
    conv = bool(getattr(res, "converged", False))
    beta = float(res.params["grp"])
    se = float(res.bse["grp"])
    p = float(res.pvalues["grp"])
    intercept = float(res.params["Intercept"])
    out = {
        "beta": beta, "se": se, "ci_low": beta - 1.959963984540054 * se,
        "ci_high": beta + 1.959963984540054 * se,
        "z": beta / se if se > 0 else np.nan, "p_value": p,
        "n_spots": len(d), "n_high": int((d["grp"] == 1).sum()),
        "n_low": int((d["grp"] == 0).sum()),
        "n_sections": int(d[groups_col].nunique()) if groups_col != "section" else int(d["section"].nunique()),
        "n_patients": int(d["patient"].nunique()),
        "converged": conv,
        "low_group_mean_response": float(d.loc[d["grp"] == 0, "y"].mean()),
        "high_group_mean_response": float(d.loc[d["grp"] == 1, "y"].mean()),
        "intercept": intercept,
    }
    # random-effect variance / ICC
    re_vars = {}
    if res.cov_re is not None and res.cov_re.size:
        if hasattr(res.model, "cov_re_names"):
            names = res.model.cov_re_names
        else:
            names = [f"re{i}" for i in range(res.cov_re.shape[0])]
        for i, nm in enumerate(names):
            re_vars[str(nm)] = float(res.cov_re.iloc[i, i]) if hasattr(res.cov_re, "iloc") else float(res.cov_re[i, i])
    vcomp = {}
    vcomp_raw = getattr(res, "vcomp", None)
    if vcomp_raw is not None:
        if hasattr(vcomp_raw, "items"):
            for k, v in vcomp_raw.items():
                vcomp[str(k)] = float(np.asarray(v).ravel()[0])
        else:
            arr = np.asarray(vcomp_raw).ravel()
            for i, v in enumerate(arr):
                vcomp[f"vc{i}"] = float(v)
    resid = float(res.scale)
    total_re = sum(re_vars.values()) + sum(vcomp.values())
    out["re_variance"] = json.dumps(re_vars)
    out["vc_variance"] = json.dumps(vcomp)
    out["residual_variance"] = resid
    out["icc_total"] = total_re / (total_re + resid) if (total_re + resid) > 0 else np.nan
    return out


ANALYSES = []
# ---- primary: tumour, neighbour response, own covariates, section RE
ANALYSES.append(dict(
    analysis="primary_tumour_nb_owncov_sectionRE", histology="tumor",
    group_col="cd276_group", response_prefix="nb_", cov_source="own",
    groups_col="section", vc_formula=None, transform="identity", primary=True,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback)",
    random_effect="(1|section)"))
# ---- sensitivity: log1p neighbour response
ANALYSES.append(dict(
    analysis="sens_log1p_nb_tumour", histology="tumor",
    group_col="cd276_group", response_prefix="nb_", cov_source="own",
    groups_col="section", vc_formula=None, transform="log1p", primary=False,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback)",
    random_effect="(1|section)"))
# ---- sensitivity: detection group
ANALYSES.append(dict(
    analysis="sens_detection_group_tumour", histology="tumor",
    group_col="cd276_detected", response_prefix="nb_", cov_source="own",
    groups_col="section", vc_formula=None, transform="identity", primary=False,
    group_definition="CD276_counts > 0 (high) vs == 0 (low)",
    random_effect="(1|section)"))
# ---- sensitivity: neighbour covariates
ANALYSES.append(dict(
    analysis="sens_neighbour_covariates_tumour", histology="tumor",
    group_col="cd276_group", response_prefix="nb_", cov_source="neighbour",
    groups_col="section", vc_formula=None, transform="identity", primary=False,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback)",
    random_effect="(1|section)"))
# ---- sensitivity: spot-own abundance response
ANALYSES.append(dict(
    analysis="sens_spot_own_abundance_tumour", histology="tumor",
    group_col="cd276_group", response_prefix="own_", cov_source="own",
    groups_col="section", vc_formula=None, transform="identity", primary=False,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback)",
    random_effect="(1|section)"))
# ---- sensitivity: patient random effect
ANALYSES.append(dict(
    analysis="sens_patient_random_effect_tumour", histology="tumor",
    group_col="cd276_group", response_prefix="nb_", cov_source="own",
    groups_col="patient", vc_formula=None, transform="identity", primary=False,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback)",
    random_effect="(1|patient), 5 donors"))
# ---- sensitivity: nested patient/section
ANALYSES.append(dict(
    analysis="sens_nested_patient_section_tumour", histology="tumor",
    group_col="cd276_group", response_prefix="nb_", cov_source="own",
    groups_col="patient", vc_formula={"section": "0 + C(section)"},
    transform="identity", primary=False,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback)",
    random_effect="(1|patient) + (1|section within patient)"))
# ---- sensitivity: depth adjustment only (decomposes why the sign flips)
ANALYSES.append(dict(
    analysis="sens_depth_only_tumour", histology="tumor",
    group_col="cd276_group", response_prefix="nb_", cov_source="own",
    cov_set="depth", groups_col="section", vc_formula=None,
    transform="identity", primary=False,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback)",
    random_effect="(1|section)"))
# ---- sensitivity: depth + fibroblast, no malignant covariate
ANALYSES.append(dict(
    analysis="sens_depth_plus_fibroblast_tumour", histology="tumor",
    group_col="cd276_group", response_prefix="nb_", cov_source="own",
    cov_set="depth_fib", groups_col="section", vc_formula=None,
    transform="identity", primary=False,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback)",
    random_effect="(1|section)"))
# ---- sensitivity: complete-ring spots only (8 neighbours within radius 2.05)
# NOTE: on this array_row/array_col table the 2.05 radius returns 8 neighbours
# for full-ring spots (4 at distance 1.414, 4 at distance 2.0), not 6. The
# source script's text called this a "k=6" lattice; the actual degree
# distribution is reported in the fit log. The complete-ring sensitivity uses
# n_neighbours == 8 (the modal value), which is the correct interior set.
ANALYSES.append(dict(
    analysis="sens_full_ring_spots_tumour", histology="tumor",
    group_col="cd276_group", response_prefix="nb_", cov_source="own",
    cov_set="full", subset="full_ring", groups_col="section", vc_formula=None,
    transform="identity", primary=False,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback)",
    random_effect="(1|section)"))
# ---- sensitivity: adjacent-normal primary spec
ANALYSES.append(dict(
    analysis="sens_adjacent_normal_nb_owncov_sectionRE", histology="adjacent-normal",
    group_col="cd276_group", response_prefix="nb_", cov_source="own",
    groups_col="section", vc_formula=None, transform="identity", primary=False,
    group_definition="per-section top vs bottom quartile of CD276_lognorm (rank fallback; degenerate in 8/10 sections: median CD276 of high group = 0)",
    random_effect="(1|section)"))
ANALYSES.append(dict(
    analysis="sens_adjacent_normal_detection_group", histology="adjacent-normal",
    group_col="cd276_detected", response_prefix="nb_", cov_source="own",
    groups_col="section", vc_formula=None, transform="identity", primary=False,
    group_definition="CD276_counts > 0 (high) vs == 0 (low); degenerate / underpowered",
    random_effect="(1|section)"))

rows = []
for spec in ANALYSES:
    hist = spec["histology"]
    datasub = df[(df["histology"] == hist) & (df["n_neighbours"] > 0)].copy()
    if spec.get("subset") == "full_ring":
        datasub = datasub[datasub["n_neighbours"] == 8].copy()
    # own covariates
    datasub["log_depth"] = np.log1p(datasub["total_counts"])
    if spec["cov_source"] == "own":
        datasub["cov_fib"] = datasub["mean_fibroblast"]
        datasub["cov_malig"] = datasub["mean_malignant cell"]
    else:
        datasub["cov_fib"] = datasub["nb_fibroblast"]
        datasub["cov_malig"] = datasub["nb_malignant cell"]
    datasub = datasub.dropna(subset=["cov_fib", "cov_malig", "log_depth"])
    for ct in IMMUNE_TYPES:
        response = f"nb_{ct}" if spec["response_prefix"] == "nb_" else f"mean_{ct}"
        data_ct = datasub.copy()
        if spec["transform"] == "log1p":
            data_ct[response] = np.log1p(data_ct[response].astype(float))
        rec = dict(spec)
        rec.pop("cov_source", None)
        rec.pop("response_prefix", None)
        rec.pop("transform", None)
        rec["response"] = ("neighbour-mean abundance" if spec["response_prefix"] == "nb_"
                           else "spot-own abundance")
        if spec.get("primary"):
            pass
        rec["response_transform"] = spec.get("transform", "identity")
        cov_set = spec.get("cov_set", "full")
        cov_cols = {"full": ["log_depth", "cov_fib", "cov_malig"],
                    "depth": ["log_depth"],
                    "depth_fib": ["log_depth", "cov_fib"]}[cov_set]
        base_cov = ("own spot: log1p(total_counts)"
                    if spec["cov_source"] == "own" else
                    "neighbour means: log1p(total_counts)")
        if cov_set == "full":
            extra = (", mean_fibroblast, mean_malignant cell"
                     if spec["cov_source"] == "own" else
                     ", nb_fibroblast, nb_malignant cell")
        elif cov_set == "depth_fib":
            extra = ", mean_fibroblast"
        else:
            extra = " (depth adjustment only)"
        rec["covariates"] = base_cov + extra
        rec["cell_type"] = ct
        rec["paper_named_compartment"] = ct in PAPER_NAMED
        try:
            fit = fit_one(data_ct, response, spec["group_col"],
                          cov_cols,
                          spec["groups_col"], spec.get("vc_formula"),
                          high_label=("positive" if spec["group_col"] == "cd276_detected"
                                      else "high"))
            rec.update(fit)
            rec["status"] = "ok"
        except Exception as e:
            log(f"FIT FAILED {spec['analysis']} {ct}: {type(e).__name__}: {e}")
            log(traceback.format_exc())
            rec.update({"status": f"failed: {type(e).__name__}: {e}",
                        "beta": np.nan, "se": np.nan, "ci_low": np.nan,
                        "ci_high": np.nan, "z": np.nan, "p_value": np.nan,
                        "n_spots": np.nan, "n_high": np.nan, "n_low": np.nan,
                        "n_sections": np.nan, "n_patients": np.nan,
                        "converged": False, "icc_total": np.nan,
                        "low_group_mean_response": np.nan,
                        "high_group_mean_response": np.nan})
        rows.append(rec)

res_df = pd.DataFrame(rows)
# BH within each analysis x 9 immune types
res_df["q_bh"] = np.nan
for a, sub in res_df.groupby("analysis"):
    ok = sub["p_value"].notna()
    p = sub.loc[ok, "p_value"].to_numpy()
    order = np.argsort(p)
    m = len(p)
    q = np.empty(m)
    ranked = p[order]
    q_sorted = ranked * m / np.arange(1, m + 1)
    q_sorted = np.minimum.accumulate(q_sorted[::-1])[::-1]
    q[order] = np.clip(q_sorted, 0, 1)
    res_df.loc[sub.index[ok], "q_bh"] = q
res_df["direction"] = np.where(res_df["beta"] > 0, "increase",
                               np.where(res_df["beta"] < 0, "decrease", "none"))
res_df["pct_change_vs_low_mean"] = np.where(
    (res_df["response_transform"] == "identity") & (res_df["low_group_mean_response"] > 0),
    res_df["beta"] / res_df["low_group_mean_response"] * 100, np.nan)
# crude, unadjusted high-vs-low contrast (no covariates, no RE), for context:
# shows how much the paper-style adjustment changes the raw group difference.
res_df["unadjusted_diff"] = (res_df["high_group_mean_response"]
                             - res_df["low_group_mean_response"])
res_df["unadjusted_pct_change"] = np.where(
    res_df["low_group_mean_response"] > 0,
    res_df["unadjusted_diff"] / res_df["low_group_mean_response"] * 100, np.nan)
res_df["significant_q05"] = res_df["q_bh"] < 0.05

COLS = ["analysis", "histology", "cell_type", "paper_named_compartment",
        "group_definition", "response", "response_transform", "covariates",
        "random_effect", "beta", "se", "ci_low", "ci_high", "z", "p_value",
        "q_bh", "significant_q05", "direction", "pct_change_vs_low_mean",
        "unadjusted_diff", "unadjusted_pct_change",
        "low_group_mean_response", "high_group_mean_response", "n_spots",
        "n_high", "n_low", "n_sections", "n_patients", "converged",
        "re_variance", "vc_variance", "residual_variance", "icc_total",
        "intercept", "status"]
res_df = res_df.reindex(columns=COLS)

primary = res_df[res_df["analysis"] == "primary_tumour_nb_owncov_sectionRE"].copy()
primary.to_csv(f"{TAB}/visium_correction_mixed_effects_4e.csv", index=False)
res_df.to_csv(f"{TAB}/visium_correction_mixed_effects_4e_sensitivity.csv", index=False)

log("\n=== PRIMARY (tumour, neighbour abundance, own covariates, section RE) ===")
log(primary[["cell_type", "beta", "se", "ci_low", "ci_high", "p_value", "q_bh",
             "direction", "pct_change_vs_low_mean", "n_spots", "n_sections",
             "converged", "icc_total"]].to_string(index=False))
log("\n=== All analyses (compact) ===")
log(res_df[["analysis", "cell_type", "beta", "p_value", "q_bh", "direction",
            "n_spots", "converged", "status"]].to_string(index=False))
log(f"\nRUN END wall={time.time() - _t0:.1f}s")
with open(LOG, "w") as fh:
    fh.write("\n".join(_log_lines) + "\n")
print("DONE")
