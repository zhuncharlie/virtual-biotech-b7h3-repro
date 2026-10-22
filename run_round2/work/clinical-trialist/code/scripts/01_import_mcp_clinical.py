#!/usr/bin/env python
"""Import the raw JSON payload returned by the cBioPortal MCP tool
mcp__clinicaltrials__get_clinical_data (tool_use_id provenance
mcp-clinicaltrials-get_clinical_data-1792588469181) into tabular form.

The MCP result was too large to return inline and was written by the harness to
a tool-results file; this script reads that exact payload and saves it under
data/raw so the cohort is reproducible from a saved artifact.
"""
import json
import os
import pandas as pd

SRC = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/"
       "isolated_claude_config/projects/"
       "-mnt-beegfs-xqinag-projects-TheVirtualBiotech-runs-20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/"
       "5c1a907a-23af-4730-bee7-1171af62cd2d/tool-results/"
       "mcp-clinicaltrials-get_clinical_data-1792588469181.txt")
OUT_DIR = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
           "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/clinical-trialist/data/raw")
os.makedirs(OUT_DIR, exist_ok=True)

with open(SRC) as fh:
    payload = json.load(fh)

print("top-level keys:", list(payload.keys()))
print("success:", payload.get("success"))
print("study_id:", payload.get("study_id"))
print("sample_count:", payload.get("sample_count"))
print("n clinical attributes:", len(payload.get("clinical_attributes", [])))
print("n data records:", len(payload.get("data", [])))

records = payload["data"]
keys = sorted({k for r in records for k in r.keys()})
print("n distinct record fields:", len(keys))
print("fields:", keys)

df = pd.DataFrame(records)
df.to_csv(os.path.join(OUT_DIR, "cbioportal_luad_tcga_pancancer_clinical.csv"), index=False)
with open(os.path.join(OUT_DIR, "cbioportal_luad_tcga_pancancer_clinical_attributes.json"), "w") as fh:
    json.dump(payload.get("clinical_attributes", []), fh, indent=2)
print("shape:", df.shape)
print(df.head(3).to_string()[:2000])
