#!/usr/bin/env python3
"""Audit CD276 coverage in the bundled ChEMBL/Open Targets clinical-trial
mapping and write the drug-MCP known-drug mapping to CSV.

This documents a database-coverage limitation: the bundled ChEMBL mapping
contains only a handful of CD276 rows and no lung-cancer trials, while the
ClinicalTrials.gov registry contains a large current B7-H3 lung landscape.
"""
from pathlib import Path

import pandas as pd

RUN = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
           "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/clinical-trialist")
PARQUET = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/datasets/"
               "clinical_trials/chembl_clinical_nct_data.parquet")
TAB = RUN / "results" / "tables"
PROC = RUN / "data" / "processed"
TAB.mkdir(parents=True, exist_ok=True)

cols = ["nct_id", "drugId", "targetId", "diseaseId", "phase", "status",
        "disease_name", "studyStopReason", "studyStopReasonCategories"]
df = pd.read_parquet(PARQUET, columns=cols)
cd = df[df.targetId == "ENSG00000103855"].copy()
cd.to_csv(PROC / "cd276_chembl_parquet_rows.csv", index=False)

lung_terms = ("lung", "pulmonary", "nsclc", "sclc", "adenocarcinoma")
cd["lung_related"] = cd.disease_name.fillna("").str.lower().apply(
    lambda s: any(t in s for t in lung_terms))
summary = pd.DataFrame([
    dict(metric="total parquet rows", value=len(df)),
    dict(metric="CD276 rows", value=len(cd)),
    dict(metric="distinct CD276 NCTs", value=cd.nct_id.nunique()),
    dict(metric="CD276 lung-related rows", value=int(cd.lung_related.sum())),
    dict(metric="CD276 distinct drugs", value=cd.drugId.nunique()),
    dict(metric="as_of_date", value="2026-10-20"),
])
summary.to_csv(TAB / "cd276_chembl_parquet_coverage.csv", index=False)

# Drug MCP result (search_known_drugs, target ENSG00000103855, min_phase 0,
# limit 50; fetched 2026-10-20). Curated from the tool response.
drug_mcp = pd.DataFrame([
    dict(drug="ENOBLITUZUMAB", chembl_id="CHEMBL3545373", disease="head and neck squamous cell carcinoma",
         phase=2, status="Withdrawn", mechanism="CD276 antigen cross-linking agent", nct="NCT04129320"),
    dict(drug="ENOBLITUZUMAB", chembl_id="CHEMBL3545373", disease="prostate cancer",
         phase=2, status="Recruiting", mechanism="CD276 antigen cross-linking agent", nct="NCT06014255"),
    dict(drug="8H9 131I", chembl_id="CHEMBL2109310", disease="leptomeningeal metastasis",
         phase=2, status="Terminated", mechanism="CD276 antigen binding agent", nct="NCT03275402"),
    dict(drug="ENOBLITUZUMAB", chembl_id="CHEMBL3545373", disease="head and neck malignant neoplasia",
         phase=2, status="Withdrawn", mechanism="CD276 antigen cross-linking agent", nct="NCT04129320"),
    dict(drug="8H9 131I", chembl_id="CHEMBL2109310", disease="neuroblastoma",
         phase=2, status="Terminated", mechanism="CD276 antigen binding agent", nct="NCT03275402"),
    dict(drug="ENOBLITUZUMAB", chembl_id="CHEMBL3545373", disease="prostate cancer",
         phase=2, status="Active, not recruiting", mechanism="CD276 antigen cross-linking agent", nct="NCT02923180"),
    dict(drug="8H9 131I", chembl_id="CHEMBL2109310", disease="diffuse intrinsic pontine glioma",
         phase=1, status="Withdrawn", mechanism="CD276 antigen binding agent", nct="NCT05063357"),
    dict(drug="ENOBLITUZUMAB", chembl_id="CHEMBL3545373", disease="melanoma",
         phase=1, status="Terminated", mechanism="CD276 antigen cross-linking agent", nct="NCT01918930"),
    dict(drug="8H9 131I", chembl_id="CHEMBL2109310", disease="peritoneum cancer",
         phase=1, status="Terminated", mechanism="CD276 antigen binding agent", nct="NCT01099644"),
])
drug_mcp.to_csv(TAB / "cd276_known_drugs_drug_mcp.csv", index=False)

print(summary.to_string(index=False))
print("\nCD276 rows in bundled ChEMBL parquet:")
print(cd[["nct_id", "drugId", "disease_name", "phase", "status"]].to_string(index=False))
print("\nDrug MCP known-drug rows:", len(drug_mcp), "| lung rows:",
      int(drug_mcp.disease.str.contains("lung", case=False).sum()))
