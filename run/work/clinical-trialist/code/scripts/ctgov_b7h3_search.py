#!/usr/bin/env python3
"""Search ClinicalTrials.gov for B7-H3/CD276 trials via the configured
clinicaltrials MCP server's own tool implementation.

The MCP server registers search_clinical_trials/count_clinical_trials against
the ClinicalTrials.gov API v2; this script imports those same registered
functions (they were not exposed in this session's tool list) so the searches
use the configured data source rather than ad-hoc scraping.

Outputs raw JSON into data/raw/ and a flat candidate table into
data/processed/.
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech")
sys.path.insert(0, str(PROJECT_ROOT))

from src.mcp_servers.clinicaltrials_mcp.tools import (  # noqa: E402
    count_clinical_trials,
    search_clinical_trials,
)

RUN = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
           "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/clinical-trialist")
RAW = RUN / "data" / "raw"
PROC = RUN / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

TERMS = ["B7-H3", "B7H3", "CD276", "B7-H3 ADC", "B7-H3 CAR", "B7-H3 bispecific"]
CONDITIONS = [None, "small cell lung cancer", "lung adenocarcinoma",
              "non-small cell lung cancer"]
INTERVENTIONS = [
    "ifinatamab deruxtecan", "DS-7300", "vobramitamab duocarmazine", "MGC018",
    "enoblituzumab", "MGA271", "MGD009", "orlotamab", "ABBV-155", "HS-20093",
    "DS-5573a", "DB-1311", "BNT324", "MHB088C", "omburtamab", "8H9",
]

summary = {"counts": [], "searches": []}


def record_count(label, **kw):
    r = count_clinical_trials(country=None, **kw)
    summary["counts"].append({"label": label, "query": kw, "result": r})
    print(f"COUNT {label}: {r.get('total_count', r.get('error'))}")


for t in TERMS:
    record_count(f"term:{t}", term=t)

for c in CONDITIONS[1:]:
    record_count(f"condition:{c}+term:B7-H3", condition=c, term="B7-H3")
    record_count(f"condition:{c}+term:CD276", condition=c, term="CD276")

for iv in INTERVENTIONS:
    record_count(f"intervention:{iv}", intervention=iv)

json.dump(summary, open(RAW / "ctgov_b7h3_search_counts.json", "w"), indent=2)


def run_search(label, **kw):
    r = search_clinical_trials(country=None, **kw)
    n = r.get("total_count", 0) if r.get("success") else None
    print(f"SEARCH {label}: success={r.get('success')} total={n} error={r.get('error')}")
    if r.get("success"):
        out = RAW / f"ctgov_search_{label.replace(':', '_').replace(' ', '_')}.json"
        json.dump(r, open(out, "w"), indent=2)
        summary["searches"].append({"label": label, "query": kw, "total": n,
                                    "file": str(out)})
    return r


# Broad term searches first (all fields, global)
for t in ["B7-H3", "B7H3", "CD276"]:
    run_search(f"term:{t}", term=t)

# Condition-restricted searches
for c in CONDITIONS[1:]:
    run_search(f"term:B7-H3__condition:{c}", condition=c, term="B7-H3")
    run_search(f"term:CD276__condition:{c}", condition=c, term="CD276")

# Agent-specific searches
for iv in INTERVENTIONS:
    run_search(f"intervention:{iv}", intervention=iv)

json.dump(summary, open(RAW / "ctgov_b7h3_search_index.json", "w"), indent=2)
print("DONE")
