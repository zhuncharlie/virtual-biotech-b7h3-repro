"""
Audit the SDRF age / disease-staging fields for the 22 sections in this panel.

Why this exists
---------------
The Visium ingest report parsed `Characteristics[age]` and
`Characteristics[disease staging]` straight from E-MTAB-13530.sdrf.txt and copied
them into `.obs['age']` and `.obs['stage']`. A reviewer noticed that within a
single patient the age increments by one year per section and the AJCC M
category increments (M0, M1, M2, ...), which is not biologically possible: M2-M5
are not valid AJCC M categories. These fields describe the section, not the
patient, and must not be used as per-section covariates.

This script re-reads the SDRF (read-only), restricts to the 22 sections used in
the panel, and writes a section-level audit table plus a per-patient summary.
No data are modified; `.obs` columns are left as deposited.

Outputs
-------
results/tables/visium_sdrf_age_stage_integrity.csv
results/tables/visium_sdrf_age_stage_patient_summary.csv
"""
import os
import re
import sys

import anndata as ad
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run, checked_frame  # noqa: E402

SDRF = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/"
        "data/visium_raw/E-MTAB-13530.sdrf.txt")
H5AD = f"{WORK}/data/processed/visium_sections_qc.h5ad"
TAB = f"{WORK}/results/tables"

if not os.path.exists(SDRF):
    raise FileNotFoundError(f"SDRF not found (read-only input): {SDRF}")

sec = ad.read_h5ad(H5AD, backed="r").obs[
    ["section", "patient", "histology", "sampling_site", "age", "stage", "sex"]
].drop_duplicates().copy()
# AnnData stores these as categorical; make them plain ordered scalars so
# min/max and string comparison behave as expected.
sec["age"] = sec["age"].astype(int)
for c in ["section", "patient", "histology", "sampling_site", "stage", "sex"]:
    sec[c] = sec[c].astype(str)
sections = sorted(sec["section"].unique())
assert len(sections) == 22, f"expected 22 sections, got {len(sections)}"

sdrf = pd.read_csv(SDRF, sep="\t", dtype=str)
need = ["Source Name", "Characteristics[original source name]",
        "Characteristics[age]", "Characteristics[disease]",
        "Characteristics[disease staging]", "Characteristics[sampling site]"]
missing = [c for c in need if c not in sdrf.columns]
assert not missing, f"SDRF missing columns: {missing}"

sub = sdrf[sdrf["Source Name"].astype(str).isin(sections)].copy()
# Each section has 4 SDRF rows (one per FASTQ read type: index1/index2/read1/
# read2) that differ only in sequencing columns. Collapse to one metadata row.
n_fastq_rows = len(sub)
sub = sub[need].drop_duplicates()
assert len(sub) == 22, f"expected one metadata row per section, got {len(sub)}"
assert n_fastq_rows == 88, f"expected 4 FASTQ rows/section, got {n_fastq_rows}"
sub = sub.set_index("Source Name")
assert set(sub.index) == set(sections), (
    f"SDRF sections != h5ad sections: {set(sub.index) ^ set(sections)}")

# Cross-check the h5ad copy against the SDRF verbatim.
sec = sec.set_index("section")
assert all(str(sec.loc[s, "age"]) == str(sub.loc[s, "Characteristics[age]"])
           for s in sections), "h5ad age disagrees with SDRF"
assert all(str(sec.loc[s, "stage"]) == str(sub.loc[s, "Characteristics[disease staging]"])
           for s in sections), "h5ad stage disagrees with SDRF"
assert all(str(sec.loc[s, "sampling_site"]) == str(sub.loc[s, "Characteristics[sampling site]"])
           for s in sections), "h5ad sampling site disagrees with SDRF"

M_RE = re.compile(r"M(\d+)")
rows = []
for s in sections:
    pat = sec.loc[s, "patient"]
    sib = sec[sec["patient"] == pat]
    age = int(sec.loc[s, "age"])
    stage = str(sec.loc[s, "stage"])
    m = M_RE.search(stage)
    m_cat = int(m.group(1)) if m else None
    rows.append({
        "patient": pat,
        "section": s,
        "histology": sec.loc[s, "histology"],
        "sdrf_original_source_name": sub.loc[s, "Characteristics[original source name]"],
        "sdrf_disease": sub.loc[s, "Characteristics[disease]"],
        "sdrf_sampling_site": sub.loc[s, "Characteristics[sampling site]"],
        "age": age,
        "age_min_in_patient": int(sib["age"].min()),
        "age_max_in_patient": int(sib["age"].max()),
        "age_varies_within_patient": bool(sib["age"].nunique() > 1),
        "stage": stage,
        "stage_n_distinct_in_patient": int(sib["stage"].nunique()),
        "stage_varies_within_patient": bool(sib["stage"].nunique() > 1),
        "stage_M_category": m_cat,
        "stage_M_invalid": bool(m_cat is not None and m_cat > 1),
        "usable_as_patient_level_covariate": False,
        "reason": ("age and stage differ between sections of the same patient; "
                   "M2-M5 are not valid AJCC M categories -> section-index "
                   "artefact, not patient metadata"),
    })
det = pd.DataFrame(rows)
COLS = ["patient", "section", "histology", "sdrf_original_source_name",
        "sdrf_disease", "sdrf_sampling_site", "age", "age_min_in_patient",
        "age_max_in_patient", "age_varies_within_patient", "stage",
        "stage_n_distinct_in_patient", "stage_varies_within_patient",
        "stage_M_category", "stage_M_invalid",
        "usable_as_patient_level_covariate", "reason"]
det = checked_frame(det, COLS, "visium_sdrf_age_stage_integrity")
assert len(det) == 22
assert det["usable_as_patient_level_covariate"].eq(False).all()
det.to_csv(f"{TAB}/visium_sdrf_age_stage_integrity.csv", index=False)

# Per-patient summary: does a single constant age exist anywhere?
summ = []
for pat, g in det.groupby("patient", sort=True):
    const_age = g["age"].nunique() == 1
    summ.append({
        "patient": pat,
        "n_sections": len(g),
        "n_tumor": int((g["histology"] == "tumor").sum()),
        "n_adjacent_normal": int((g["histology"] == "adjacent-normal").sum()),
        "age_min": int(g["age"].min()),
        "age_max": int(g["age"].max()),
        "age_span_years": int(g["age"].max() - g["age"].min()),
        "constant_age_within_patient": bool(const_age),
        "stages": "; ".join(sorted(g["stage"].unique())),
        "n_distinct_stages": int(g["stage"].nunique()),
        "has_invalid_M_category": bool(g["stage_M_invalid"].any()),
        "valid_patient_age_recoverable": bool(const_age),
    })
ps = pd.DataFrame(summ)
PS_COLS = ["patient", "n_sections", "n_tumor", "n_adjacent_normal", "age_min",
           "age_max", "age_span_years", "constant_age_within_patient", "stages",
           "n_distinct_stages", "has_invalid_M_category",
           "valid_patient_age_recoverable"]
ps = checked_frame(ps, PS_COLS, "visium_sdrf_age_stage_patient_summary")
assert len(ps) == 5
assert not ps["valid_patient_age_recoverable"].any(), (
    "a patient has a constant age; re-check the anomaly claim")
ps.to_csv(f"{TAB}/visium_sdrf_age_stage_patient_summary.csv", index=False)

print(ps.to_string(index=False), flush=True)
print("\ninvalid M categories:", int(det["stage_M_invalid"].sum()), "/", len(det),
      flush=True)
print("sections whose stage varies within patient:",
      int(det["stage_varies_within_patient"].sum()), "/", len(det), flush=True)

log_run(step="sdrf_metadata_integrity", status="ok",
        detail=("22/22 sections: age and/or stage vary between sections of the same "
                "patient; M2-M5 invalid AJCC categories; no patient has a constant "
                "age, so no patient-level age is recoverable; both fields flagged "
                "unusable as covariates"))
print("DONE", flush=True)
