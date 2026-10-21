#!/usr/bin/env python3
"""Parse a saved ClinicalTrials.gov v2 JSON record (as returned by the
clinicaltrials MCP tool) into a compact trial summary.

Usage:
    python parse_ctgov_record.py <saved_json> [--copy-raw DIR]

Writes a JSON summary to stdout. If --copy-raw is given, copies the raw
record into that directory under its NCT id.
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def brief(rec: dict) -> dict:
    out = {}
    keys = [
        "nctId", "briefTitle", "officialTitle", "acronym", "overallStatus",
        "whyStopped", "startDate", "primaryCompletionDate", "completionDate",
        "lastUpdatePostDate", "studyType", "phases", "allocation",
        "interventionModel", "masking", "enrollmentCount", "enrollmentType",
        "conditions", "keywords", "leadSponsor", "hasResults", "ipdSharing",
    ]
    for k in keys:
        out[k] = rec.get(k)
    out["interventions"] = [
        {"type": i.get("type"), "name": i.get("name"), "otherNames": i.get("otherNames")}
        for i in rec.get("interventions", [])
    ]
    out["primaryOutcomes"] = [o.get("measure") for o in rec.get("primaryOutcomes", [])]
    elig = rec.get("eligibilityCriteria") or ""
    out["eligibility_excerpt"] = elig[:2500]
    # location countries
    locs = rec.get("locations") or []
    out["countries"] = sorted({l.get("country") for l in locs if l.get("country")})

    # The MCP tool flattens results modules to the top level; accept the
    # nested resultsSection shape too.
    rs = rec.get("resultsSection") or {
        k: rec[k] for k in
        ("participantFlow", "baselineCharacteristics", "outcomeMeasures", "adverseEvents")
        if rec.get(k)
    }
    if rs:
        out["results_keys"] = sorted(rs.keys())
        pf = rs.get("participantFlowModule") or rs.get("participantFlow") or {}
        out["participant_flow_groups"] = [
            g.get("title") for g in (pf.get("groups") or [])
        ]
        oms = rs.get("outcomeMeasuresModule", {}).get("outcomeMeasures", []) or rs.get("outcomeMeasures") or []
        compact_oms = []
        for om in oms:
            item = {
                "type": om.get("type"),
                "title": om.get("title"),
                "description": (om.get("description") or "")[:300],
                "units": (om.get("unitOfMeasure") or {}).get("value") if isinstance(om.get("unitOfMeasure"), dict) else om.get("unitOfMeasure"),
                "groups": [g.get("title") for g in (om.get("groups") or [])],
                "classes": [],
            }
            for cl in (om.get("classes") or []):
                cats = []
                for cat in (cl.get("categories") or []):
                    cats.append({
                        "title": cat.get("title"),
                        "measurements": [
                            {"groupId": m.get("groupId"), "value": m.get("value")}
                            for m in (cat.get("measurements") or [])
                        ],
                    })
                item["classes"].append({"title": cl.get("title"), "categories": cats})
            compact_oms.append(item)
        out["outcomeMeasures"] = compact_oms
        ae = rs.get("adverseEventsModule") or rs.get("adverseEvents") or {}
        out["ae_event_groups"] = [g.get("title") for g in (ae.get("eventGroups") or [])]
        # serious AE summary counts per group
        out["serious_ae_affected"] = [
            {"groupId": g.get("id"), "deaths": g.get("deathsNumAffected"),
             "serious": g.get("seriousNumAffected"), "other": g.get("otherNumAffected")}
            for g in (ae.get("eventGroups") or [])
        ]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--copy-raw", default=None)
    args = ap.parse_args()
    rec = json.load(open(args.json_path))
    if args.copy_raw:
        os.makedirs(args.copy_raw, exist_ok=True)
        dst = Path(args.copy_raw) / f"clinicaltrials_gov_{rec.get('nctId','unknown')}.json"
        shutil.copyfile(args.json_path, dst)
    json.dump(brief(rec), sys.stdout, indent=2)


if __name__ == "__main__":
    main()
