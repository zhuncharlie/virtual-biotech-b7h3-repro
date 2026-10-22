"""Audit the Tahoe drug_metadata `targets` column: null vs empty-string vs text.

The status report previously described `n_drugs_with_annotated_target` as
`targets.notna().sum()` (264), which is only correct if no annotated value is an
empty string. This script quantifies the distinction on the pinned metadata
parquet so the report can describe the metric exactly.

Input parquet is read from the read-only source run (not re-downloaded).
"""
from pathlib import Path

import pandas as pd

SRC = Path(
    "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
    "20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/"
    "functional-genomics-analyst/data/raw/tahoe_metadata/metadata/drug_metadata.parquet"
)
OUT = Path(__file__).resolve().parents[2] / "results" / "tables" / "tahoe_drug_targets_annotation_audit.csv"

df = pd.read_parquet(SRC)
t = df["targets"]
norm = t.astype("string").str.strip()

audit = pd.DataFrame([
    {"metric": "n_drug_rows", "value": len(df)},
    {"metric": "targets_isna_true", "value": int(t.isna().sum())},
    {"metric": "targets_empty_or_whitespace_string",
     "value": int((norm == "").fillna(False).sum())},
    {"metric": "targets_na_or_blank", "value": int((t.isna() | (norm == "")).sum())},
    {"metric": "targets_nonblank_text", "value": int((~t.isna() & (norm != "")).sum())},
    {"metric": "n_unique_drugs", "value": int(df["drug"].nunique())},
])
audit.to_csv(OUT, index=False)
print(audit.to_string(index=False))

# Show what the blank values look like, without dumping the whole table.
example = df.loc[t.notna() & (norm == ""), "drug"].head(5).tolist()
print("example drugs with blank-string targets:", example)
raw_example = t.loc[t.notna()].head(3).tolist()
print("example non-null targets values:", raw_example)
print("dtype:", t.dtype)
print("wrote", OUT)
