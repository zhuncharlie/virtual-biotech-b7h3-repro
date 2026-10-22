#!/usr/bin/env python
"""Cox proportional hazards models for CD276 expression quartile in TCGA LUAD
PanCancer Atlas.

Primary contrast : Q4 (top quartile) vs Q1 (bottom quartile)
Models           : unadjusted; adjusted for age (per year), sex, AJCC stage
                   group (I ref, II, III, IV)
Endpoints        : OS, DSS (paper-reported); PFS, DFS (computability reported)
PH assumption    : Schoenfeld residual test (rank time transform) for every term
Sensitivity      : continuous log2(RSEM) per doubling; Q4 vs Q1+Q2+Q3
                   (both unadjusted and adjusted)

No model is tuned to reproduce the paper's HRs.
"""
import os
import warnings
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test

warnings.filterwarnings("ignore")

BASE = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/clinical-trialist")
PROC = os.path.join(BASE, "data/processed")
TAB = os.path.join(BASE, "results/tables")
os.makedirs(TAB, exist_ok=True)

co = pd.read_csv(os.path.join(PROC, "tcga_luad_cd276_analysis_cohort.csv"))
co["log2_expr"] = np.log2(co["value"])

ENDPOINTS = ["OS", "DSS", "PFS", "DFS"]

rows = []
fit_objects = {}


def prep(ep, subset):
    d = co.copy()
    d = d[d[f"{ep}_TIME"].notna() & d[f"{ep}_EVENT"].notna() & (d[f"{ep}_TIME"] > 0)]
    if subset == "q1q4":
        d = d[d.expression_quartile.isin(["Q1", "Q4"])].copy()
        d["Q4_vs_Q1"] = (d.expression_quartile == "Q4").astype(int)
    elif subset == "q4vrest":
        d = d.copy()
        d["Q4_vs_Q1"] = (d.expression_quartile == "Q4").astype(int)  # Q4 vs all others
    d = d.rename(columns={f"{ep}_TIME": "T", f"{ep}_EVENT": "E"})
    return d


def run(ep, subset, model, terms, d, label):
    import re
    needed = ["T", "E"] + [re.sub(r"C\((.*)\)", r"\1", t) for t in terms]
    needed = [c for c in needed if c in d.columns]
    dd = d[needed].dropna().copy()
    # drop stage levels with no observations in this endpoint subset (avoids an
    # all-zero design column; e.g. DFS has no stage IV patients with follow-up)
    present = [c for c in ["I", "II", "III", "IV"] if c in set(dd["STAGE"])] if "STAGE" in dd.columns else []
    if "STAGE" in dd.columns:
        dd["STAGE"] = pd.Categorical(dd["STAGE"], categories=present)
    cph = CoxPHFitter()
    formula = " + ".join(terms)
    cph.fit(dd, duration_col="T", event_col="E", formula=formula)
    d = dd
    s = cph.summary
    stage_levels = "/".join(present)
    try:
        ph = proportional_hazard_test(cph, d, time_transform="rank").summary
        ph_p = ph["p"].to_dict()
    except Exception as e:
        print(f"PH test failed for {ep}/{label}: {e}")
        ph_p = {}
    fit_objects[(ep, label)] = cph
    for term in s.index:
        r = s.loc[term]
        rows.append(dict(
            endpoint=ep, model=label, term=term,
            is_primary_contrast=int(term in ("Q4_vs_Q1", "log2_expr")),
            HR=float(r["exp(coef)"]), CI_lower=float(r["exp(coef) lower 95%"]),
            CI_upper=float(r["exp(coef) upper 95%"]), coef=float(r["coef"]),
            se=float(r["se(coef)"]), z=float(r["z"]), p=float(r["p"]),
            n=int(cph._n_examples), events=int(d["E"].sum()),
            ph_test_p=float(ph_p.get(term, np.nan)),
            ph_violation_p05=int((not np.isnan(ph_p.get(term, np.nan))) and ph_p[term] < 0.05),
            n_dropped_covariate_missing=int(len(co[co[f"{ep}_TIME"].notna()]) - len(d)) if model != "unadjusted" else 0,
            stage_levels_used=stage_levels,
            notes=""))

    # global PH note
    return cph


print("=" * 70)
for ep in ENDPOINTS:
    base = prep(ep, "q1q4")
    print(f"\n### {ep}: available n={len(base)}, events={int(base.E.sum())}, "
          f"Q1={int((base.expression_quartile=='Q1').sum())} "
          f"Q4={int((base.expression_quartile=='Q4').sum())}")

    if len(base) == 0 or base.E.sum() < 5:
        rows.append(dict(endpoint=ep, model="NOT_COMPUTABLE", term="", HR=np.nan,
                         CI_lower=np.nan, CI_upper=np.nan, coef=np.nan, se=np.nan,
                         z=np.nan, p=np.nan, n=len(base), events=int(base.E.sum()),
                         ph_test_p=np.nan, ph_violation_p05=np.nan,
                         n_dropped_covariate_missing=np.nan,
                         notes="insufficient events"))
        continue

    # 1. unadjusted Q4 vs Q1
    run(ep, "q1q4", "unadjusted_Q4_vs_Q1", ["Q4_vs_Q1"], base, "unadjusted_Q4_vs_Q1")

    # 2. adjusted Q4 vs Q1
    adj = base.dropna(subset=["AGE", "SEX_M", "STAGE"])
    run(ep, "q1q4", "adjusted_Q4_vs_Q1", ["Q4_vs_Q1", "AGE", "C(STAGE)", "SEX_M"],
        base, "adjusted_Q4_vs_Q1")

    # 3. sensitivity: continuous log2 expression per doubling, adjusted
    run(ep, "q1q4", "adjusted_continuous_log2expr", ["log2_expr", "AGE", "C(STAGE)", "SEX_M"],
        base, "adjusted_continuous_log2expr")
    run(ep, "q1q4", "unadjusted_continuous_log2expr", ["log2_expr"], base,
        "unadjusted_continuous_log2expr")

    # 4. sensitivity: Q4 vs Q1+Q2+Q3 (all patients with endpoint), adjusted
    rest = prep(ep, "q4vrest").dropna(subset=["AGE", "SEX_M", "STAGE"])
    run(ep, "q4vrest", "adjusted_Q4_vs_Q123", ["Q4_vs_Q1", "AGE", "C(STAGE)", "SEX_M"],
        rest, "adjusted_Q4_vs_Q123")

# ---- PH-violation follow-up: PFS truncated at 24 months (labelled sensitivity)
pv = prep("PFS", "q1q4").copy()
pv["T_orig"] = pv["T"]
pv.loc[pv["T"] > 24, "T"] = 24
pv.loc[pv["T_orig"] > 24, "E"] = 0
run("PFS", "q1q4", "sensitivity_PFS_truncated_24mo", ["Q4_vs_Q1"], pv,
    "sensitivity_PFS_truncated_24mo")
print("PFS 24-month truncated sensitivity fitted (PH violation check)")

res = pd.DataFrame(rows)
res.to_csv(os.path.join(TAB, "tcga_luad_cd276_cox_models.csv"), index=False)
print("\n=== PRIMARY RESULTS (focal terms) ===")
show = res[(res.is_primary_contrast == 1)][
    ["endpoint", "model", "term", "HR", "CI_lower", "CI_upper", "p", "n", "events", "ph_test_p"]]
pd.set_option("display.width", 200)
print(show.to_string(index=False))
print("\nwrote", os.path.join(TAB, "tcga_luad_cd276_cox_models.csv"))

# ---- reverse-KM median follow-up (overall and by quartile, OS cohort) -----
from lifelines import KaplanMeierFitter
fu_rows = []
osd = co[co.OS_TIME.notna() & co.OS_EVENT.notna() & (co.OS_TIME > 0)]
for grp, sub in [("overall", osd)] + [(q, osd[osd.expression_quartile == q]) for q in ["Q1", "Q2", "Q3", "Q4"]]:
    km = KaplanMeierFitter().fit(sub["OS_TIME"], event_observed=1 - sub["OS_EVENT"])
    fu_rows.append(dict(group=grp, n=len(sub), median_followup_months=float(km.median_survival_time_),
                        deaths=int(sub.OS_EVENT.sum())))
pd.DataFrame(fu_rows).to_csv(os.path.join(TAB, "tcga_luad_median_followup.csv"), index=False)
print("\nmedian follow-up (reverse KM):")
print(pd.DataFrame(fu_rows).to_string(index=False))

# quartile-level summary table (n and events per quartile per endpoint)
qrows = []
for ep in ENDPOINTS:
    d = co[co[f"{ep}_TIME"].notna() & co[f"{ep}_EVENT"].notna() & (co[f"{ep}_TIME"] > 0)]
    for qq in ["Q1", "Q2", "Q3", "Q4"]:
        s = d[d.expression_quartile == qq]
        qrows.append(dict(endpoint=ep, quartile=qq, n=len(s),
                          events=int(s[f"{ep}_EVENT"].sum()),
                          median_followup_months=float(s[f"{ep}_TIME"].median()),
                          median_CD276_RSEM=float(s["value"].median())))
pd.DataFrame(qrows).to_csv(os.path.join(TAB, "tcga_luad_cd276_quartile_event_counts.csv"), index=False)
print("\nwrote quartile event counts")
