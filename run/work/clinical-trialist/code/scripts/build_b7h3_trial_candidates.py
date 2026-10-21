#!/usr/bin/env python3
"""Deduplicate ClinicalTrials.gov search hits and flag B7-H3-directed trials
with any lung (SCLC / LUAD / NSCLC / pan-tumor-with-lung) relevance.

Writes data/processed/b7h3_ctgov_candidates.csv and a readable dump.
"""
import json
import re
from pathlib import Path

import pandas as pd

RUN = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
           "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/clinical-trialist")
RAW = RUN / "data" / "raw"
PROC = RUN / "data" / "processed"

AGENT_PATTERNS = [
    "b7-h3", "b7h3", "b7 h3", "cd276", "ifinatamab", "ds-7300", "ds7300",
    "vobramitamab", "mgc018", "enoblituzumab", "mga271", "mgd009", "orlotamab",
    "abbv-155", "abbv155", "hs-20093", "hs20093", "ds-5573a", "ds5573",
    "db-1311", "db1311", "bnt324", "mhb088c", "omburtamab", "8h9",
    "b7-h3 car", "b7h3 car", "b7-h3 x cd3", "b7-h3/cd3", "b7-h3 bispecific",
    "b7-h3 adc",
]

trials = {}
provenance = {}
for f in sorted(RAW.glob("ctgov_search_*.json")):
    if f.name.endswith("index.json") or f.name.endswith("counts.json"):
        continue
    d = json.load(open(f))
    for t in d.get("trials", []):
        nct = t.get("nctId")
        if not nct:
            continue
        trials.setdefault(nct, t)
        provenance.setdefault(nct, set()).add(f.stem)


def blob(t):
    parts = [
        t.get("briefTitle") or "", t.get("officialTitle") or "",
        " ".join(t.get("keywords") or []),
        " ".join(i.get("name") or "" for i in (t.get("interventions") or [])),
        " ".join(i.get("description") or "" for i in (t.get("interventions") or [])),
    ]
    return " ".join(parts).lower()


def is_b7h3_directed(t):
    b = blob(t)
    # Require B7-H3 signal in the title/intervention/keyword block. Trials that
    # merely list a prior B7-H3 agent as an exclusion are screened out later by
    # manual review of intervention names.
    return any(p in b for p in AGENT_PATTERNS)


def indication_category(t):
    txt = " ".join([
        " ".join(t.get("conditions") or []),
        " ".join(t.get("keywords") or []),
        t.get("briefTitle") or "", t.get("officialTitle") or "",
    ]).lower()
    norm = txt.replace("-", " ").replace("_", " ")
    sclc = ("small cell" in norm and "non small cell" not in norm) or "sclc" in norm
    luad = "adenocarcinoma" in norm and "lung" in norm
    nsclc = "non small cell lung" in norm or "nsclc" in norm
    lung_other = "lung" in txt or "pulmonary" in txt
    solid = any(p in txt for p in ["solid tumor", "solid tumour", "solid malignant",
                                   "advanced cancer", "advanced malignancy"])
    if sclc:
        return "SCLC"
    if luad:
        return "LUAD"
    if nsclc:
        return "NSCLC (not LUAD-specific)"
    if lung_other:
        return "other lung"
    if solid:
        return "pan-tumor/solid tumor"
    return "non-lung"


rows = []
for nct, t in trials.items():
    if not is_b7h3_directed(t):
        continue
    cat = indication_category(t)
    rows.append({
        "nct_id": nct,
        "brief_title": t.get("briefTitle"),
        "status": t.get("overallStatus"),
        "phase": "/".join(t.get("phases") or []),
        "indication_category": cat,
        "conditions": "; ".join(t.get("conditions") or []),
        "interventions": "; ".join(i.get("name") or "" for i in (t.get("interventions") or [])),
        "enrollment": t.get("enrollmentCount"),
        "enrollment_type": t.get("enrollmentType"),
        "sponsor": t.get("leadSponsor"),
        "start_date": t.get("startDate"),
        "completion_date": t.get("completionDate"),
        "has_results": t.get("hasResults"),
        "why_stopped": t.get("whyStopped"),
        "found_by": ";".join(sorted(provenance[nct])),
    })

df = pd.DataFrame(rows).sort_values(["indication_category", "nct_id"])
df.to_csv(PROC / "b7h3_ctgov_candidates.csv", index=False)
print("candidate B7-H3-directed trials:", len(df))
print(df["indication_category"].value_counts().to_string())
print("\n--- LUNG-RELEVANT CANDIDATES ---")
cols = ["nct_id", "status", "phase", "indication_category", "interventions", "enrollment", "has_results", "brief_title"]
lung = df[df.indication_category.isin(["SCLC", "LUAD", "NSCLC (not LUAD-specific)", "other lung"])]
for _, r in lung.iterrows():
    print(" | ".join(str(r[c])[:90] for c in cols))
print("\n--- PAN-TUMOR CANDIDATES (need lung-cohort check) ---")
pt = df[df.indication_category == "pan-tumor/solid tumor"]
for _, r in pt.iterrows():
    print(" | ".join(str(r[c])[:80] for c in cols))
