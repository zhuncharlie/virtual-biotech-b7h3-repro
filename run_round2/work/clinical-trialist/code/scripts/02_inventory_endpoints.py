#!/usr/bin/env python
"""Inventory survival endpoints and covariates in the TCGA LUAD PanCancer
Atlas clinical table pulled via the cBioPortal MCP tool.

Writes results/tables/tcga_luad_clinical_endpoint_inventory.csv and prints
value-label distributions for every *_STATUS field.
"""
import os
import pandas as pd

BASE = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/clinical-trialist")
IN = os.path.join(BASE, "data/raw/cbioportal_luad_tcga_pancancer_clinical.csv")
OUT = os.path.join(BASE, "results/tables")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(IN, dtype=str)
print("shape:", df.shape)
print("unique sampleId:", df["sampleId"].nunique(),
      "unique patientId:", df["patientId"].nunique())

rows = []
for ep in ["OS", "PFS", "DSS", "DFS"]:
    tcol, scol = f"{ep}_MONTHS", f"{ep}_STATUS"
    if tcol not in df.columns:
        rows.append(dict(endpoint=ep, time_field=tcol, status_field=scol,
                         present=False, n_time_nonnull=0, n_status_nonnull=0,
                         n_both_nonnull=0, n_events=None, status_labels=""))
        continue
    t = pd.to_numeric(df[tcol], errors="coerce")
    s = df[scol].astype(str).str.strip()
    s_null = df[scol].isna() | s.isin(["", "nan", "None", "NA", "Not Reported", "not reported"])
    both = t.notna() & ~s_null
    labels = s[~s_null].value_counts().to_dict()
    # cBioPortal status encoding: "1:DECEASED"/"0:LIVING", "1:RECURRED"/"0:DISEASE FREE"
    event = s.str.startswith("1:")
    n_events = int((both & event).sum())
    rows.append(dict(endpoint=ep, time_field=tcol, status_field=scol,
                     present=True, n_time_nonnull=int(t.notna().sum()),
                     n_status_nonnull=int((~s_null).sum()),
                     n_both_nonnull=int(both.sum()), n_events=n_events,
                     status_labels="; ".join(f"{k}={v}" for k, v in labels.items())))
    print(f"\n--- {ep} ---")
    print("time non-null:", t.notna().sum(), " min/median/max:",
          t.min(), t.median(), t.max())
    print("status labels:", labels)
    print("both non-null:", both.sum(), "events:", n_events)

inv = pd.DataFrame(rows)
inv.to_csv(os.path.join(OUT, "tcga_luad_clinical_endpoint_inventory.csv"), index=False)

# covariate inventory
print("\n=== COVARIATES ===")
for c in ["AGE", "SEX", "AJCC_PATHOLOGIC_TUMOR_STAGE", "AJCC_STAGING_EDITION",
          "PATH_T_STAGE", "PATH_N_STAGE", "PATH_M_STAGE", "GRADE" if "GRADE" in df.columns else "SUBTYPE",
          "SAMPLE_TYPE", "SUBTYPE"]:
    if c in df.columns:
        print(f"{c}: non-null={df[c].notna().sum()}", df[c].value_counts().head(12).to_dict())

print("\nSTAGE x EDITION crosstab:")
print(pd.crosstab(df["AJCC_PATHOLOGIC_TUMOR_STAGE"].fillna("NA"),
                  df["AJCC_STAGING_EDITION"].fillna("NA")))
print("\nSAMPLE_TYPE:", df["SAMPLE_TYPE"].value_counts().to_dict())
print("PERSON_NEOPLASM_CANCER_STATUS:", df["PERSON_NEOPLASM_CANCER_STATUS"].value_counts().to_dict())
print("\nwrote", os.path.join(OUT, "tcga_luad_clinical_endpoint_inventory.csv"))
