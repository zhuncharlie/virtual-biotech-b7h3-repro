#!/usr/bin/env python
"""Build the TCGA LUAD PanCancer Atlas CD276 survival cohort.

Inputs
  data/raw/cbioportal_luad_tcga_pancancer_clinical.csv          (MCP get_clinical_data, 566 samples)
  data/raw/cbioportal_luad_tcga_pancancer_cd276_mrna_raw.csv    (pybioportal molecular_data, 510 samples)

Outputs
  data/processed/tcga_luad_cd276_analysis_cohort.csv
  results/tables/tcga_luad_cohort_construction.csv
  results/tables/tcga_luad_cd276_expression_quartiles.csv

Handling decisions (documented, not tuned):
  * one sample per patient (verify; keep first primary-tumour aliquot if >1)
  * expression quartiles cut on the full mRNA cohort (n=510) with pandas
    linear-interpolation quantiles -> Q1..Q4
  * stage collapsed to AJCC groups I/II/III/IV (IA/IB -> I etc.)
  * non-positive survival times excluded from that endpoint
  * adjusted models: complete cases on age, sex, stage (missingness reported)
"""
import os
import numpy as np
import pandas as pd

BASE = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/clinical-trialist")
RAW = os.path.join(BASE, "data/raw")
PROC = os.path.join(BASE, "data/processed")
TAB = os.path.join(BASE, "results/tables")
os.makedirs(PROC, exist_ok=True)
os.makedirs(TAB, exist_ok=True)

cli = pd.read_csv(os.path.join(RAW, "cbioportal_luad_tcga_pancancer_clinical.csv"), dtype=str)
expr = pd.read_csv(os.path.join(RAW, "cbioportal_luad_tcga_pancancer_cd276_mrna_raw.csv"), dtype=str)
expr["value"] = pd.to_numeric(expr["value"], errors="coerce")

print("clinical rows/samples/patients:", len(cli), cli.sampleId.nunique(), cli.patientId.nunique())
print("expression rows/samples/patients:", len(expr), expr.sampleId.nunique(), expr.patientId.nunique())
print("expression NaN values:", expr["value"].isna().sum())
dup_expr = expr[expr.duplicated("patientId", keep=False)]
print("expression patients with >1 aliquot:", dup_expr.patientId.nunique())

# ---- 1. one sample per patient -------------------------------------------
expr_sorted = expr.sort_values(["patientId", "sampleId"])
expr_one = expr_sorted.drop_duplicates("patientId", keep="first").copy()
print("kept one expression sample per patient:", len(expr_one))

# ---- 2. presence of non-standard clinical values -------------------------
def audit_field(series):
    s = series.astype(str).str.strip()
    bad = s.isin(["", "nan", "None", "NA", "Not Reported", "not reported",
                  "Not reported", "Unknown", "[Not Available]", "[Not Applicable]"])
    return int(bad.sum()), sorted(s[bad].unique().tolist())

for c in ["AGE", "SEX", "AJCC_PATHOLOGIC_TUMOR_STAGE"]:
    nbad, vals = audit_field(cli[c])
    print(f"{c}: missing/placeholder={nbad} values={vals}")
    print("  raw non-null:", cli[c].notna().sum(), "distinct:", cli[c].nunique())

cli["AGE_NUM"] = pd.to_numeric(cli["AGE"].astype(str).str.strip(), errors="coerce")
print("AGE non-numeric after coercion:", cli["AGE_NUM"].isna().sum())
print("AGE range:", cli["AGE_NUM"].min(), cli["AGE_NUM"].max())

# ---- 3. stage collapse ----------------------------------------------------
def collapse_stage(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip().upper()
    if s in ("", "NAN", "NOT REPORTED", "UNKNOWN", "NA"):
        return np.nan
    for roman, num in [("IV", "IV"), ("III", "III"), ("II", "II"), ("I", "I")]:
        if s.startswith(f"STAGE {roman}"):
            return num
    return np.nan

cli["STAGE_GROUP"] = cli["AJCC_PATHOLOGIC_TUMOR_STAGE"].apply(collapse_stage)
print("\nSTAGE_GROUP counts:\n", cli["STAGE_GROUP"].value_counts(dropna=False))
print("unmapped stage values:",
      sorted(cli.loc[cli.STAGE_GROUP.isna() & cli.AJCC_PATHOLOGIC_TUMOR_STAGE.notna(),
                     "AJCC_PATHOLOGIC_TUMOR_STAGE"].unique().tolist()))

# ---- 4. merge -------------------------------------------------------------
cohort = expr_one.merge(
    cli[["sampleId", "patientId", "AGE_NUM", "SEX", "STAGE_GROUP",
         "SAMPLE_TYPE", "PATH_T_STAGE", "PATH_N_STAGE", "PATH_M_STAGE",
         "OS_MONTHS", "OS_STATUS", "PFS_MONTHS", "PFS_STATUS",
         "DSS_MONTHS", "DSS_STATUS", "DFS_MONTHS", "DFS_STATUS"]],
    on=["sampleId", "patientId"], how="left", validate="one_to_one")
print("\nmerged shape:", cohort.shape, "patients:", cohort.patientId.nunique())

# ---- 5. quartiles on the full expression cohort ---------------------------
q = cohort["value"].quantile([0.25, 0.5, 0.75])
print("\nexpression quartile cutpoints (RSEM):", dict(q))
cohort["expression_quartile"] = pd.cut(
    cohort["value"], bins=[-np.inf, q[0.25], q[0.5], q[0.75], np.inf],
    labels=["Q1", "Q2", "Q3", "Q4"]).astype(str)
print(cohort.expression_quartile.value_counts().sort_index())

# ---- 6. endpoint usability -------------------------------------------------
for ep in ["OS", "PFS", "DSS", "DFS"]:
    t = pd.to_numeric(cohort[f"{ep}_MONTHS"], errors="coerce")
    s = cohort[f"{ep}_STATUS"].astype(str).str.strip()
    valid_s = s.str.match(r"^[01]:")
    ev = s.str.startswith("1:")
    cohort[f"{ep}_TIME"] = t
    cohort[f"{ep}_EVENT"] = np.where(valid_s, ev.astype(int), np.nan)
    print(f"{ep}: time non-null={t.notna().sum()}, valid status={valid_s.sum()}, "
          f"both={int((t.notna() & valid_s).sum())}, events={int((t.notna() & valid_s & ev).sum())}, "
          f"time<=0 (valid status)={int((t.notna() & valid_s & (t <= 0)).sum())}")

# ---- 7. covariates complete-case ------------------------------------------
cohort["SEX_M"] = cohort["SEX"].map({"Male": 1, "Female": 0})
cohort["AGE"] = cohort["AGE_NUM"]
cohort["STAGE"] = cohort["STAGE_GROUP"]
cov_ok = cohort[["AGE", "SEX_M", "STAGE"]].notna().all(axis=1)
print("\ncovariate completeness: AGE", cohort.AGE.notna().sum(),
      "SEX", cohort.SEX_M.notna().sum(), "STAGE", cohort.STAGE.notna().sum(),
      "all three", int(cov_ok.sum()))
print("missingness combos:\n", cohort[["AGE", "SEX_M", "STAGE"]].isna().value_counts())

# ---- 8. cohort construction table -----------------------------------------
rows = []

def add(step, detail, n_remaining, n_excluded, scope):
    rows.append(dict(step=step, detail=detail, n_remaining=int(n_remaining),
                     n_excluded=int(n_excluded), scope=scope))

add(1, "Samples in luad_tcga_pan_can_atlas_2018 (clinical MCP get_clinical_data)", len(cli), 0, "all")
add(2, "Patients with CD276 value in luad_tcga_pan_can_atlas_2018_rna_seq_v2_mrna", len(expr_one),
    len(cli) - len(expr_one), "all")
add(3, "After duplicate-patient sample reduction (one primary aliquot/patient)", len(cohort), 0, "all")
add(4, "Expression quartile assigned (non-missing CD276)", cohort.value.notna().sum(),
    cohort.value.isna().sum(), "all")
add(5, "Covariates complete (age, sex, AJCC stage) -- adjusted-model eligible", cov_ok.sum(),
    int((~cov_ok).sum()), "adjusted")

for ep in ["OS", "PFS", "DSS", "DFS"]:
    t = cohort[f"{ep}_TIME"].notna() & cohort[f"{ep}_EVENT"].notna()
    tpos = t & (cohort[f"{ep}_TIME"] > 0)
    add(6, f"{ep}: endpoint time+status present", t.sum(), len(cohort) - t.sum(), ep)
    add(7, f"{ep}: positive follow-up time only", tpos.sum(), int((t & ~tpos).sum()), ep)
    add(8, f"{ep}: unadjusted Q4-vs-Q1 analysis set",
        int((tpos & cohort.expression_quartile.isin(["Q1", "Q4"])).sum()),
        int((tpos & ~cohort.expression_quartile.isin(["Q1", "Q4"])).sum()), f"{ep}_q4vq1")
    add(9, f"{ep}: adjusted Q4-vs-Q1 analysis set (covariates complete)",
        int((tpos & cov_ok & cohort.expression_quartile.isin(["Q1", "Q4"])).sum()),
        int((tpos & ~(cov_ok & cohort.expression_quartile.isin(["Q1", "Q4"]))).sum()),
        f"{ep}_q4vq1_adjusted")

cc = pd.DataFrame(rows)
cc.to_csv(os.path.join(TAB, "tcga_luad_cohort_construction.csv"), index=False)
print("\n=== COHORT CONSTRUCTION ===")
print(cc.to_string(index=False))

cohort.to_csv(os.path.join(PROC, "tcga_luad_cd276_analysis_cohort.csv"), index=False)

qt = cohort[["patientId", "sampleId", "value", "expression_quartile", "AGE", "SEX",
             "STAGE_GROUP", "OS_TIME", "OS_EVENT", "PFS_TIME", "PFS_EVENT",
             "DSS_TIME", "DSS_EVENT", "DFS_TIME", "DFS_EVENT"]].copy()
qt = qt.rename(columns={"value": "CD276_RSEM_batch_normalized"})
qt.to_csv(os.path.join(TAB, "tcga_luad_cd276_expression_quartiles.csv"), index=False)
print("\nwrote", os.path.join(TAB, "tcga_luad_cd276_expression_quartiles.csv"), qt.shape)
