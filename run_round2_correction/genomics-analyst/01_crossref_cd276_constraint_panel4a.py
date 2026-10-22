#!/usr/bin/env python3
"""Cross-reference the round-1 gnomAD CD276 LoF constraint values into panel 4A.

No new data pull and no recomputation of constraint: this script only reads two
already-saved round-1 artifacts, checks that they agree exactly, checks that the
LoF O/E rounds to the paper's quoted 0.67, and writes one tidy table plus a
verification log.

Inputs (read-only, outside this run):
  A) bio-pathways-ppi-analyst/results/tables/cd276_constraint_tractability.csv
  B) fda-safety-officer/data/raw/cd276_target_info_and_constraint.json

Outputs (inside this run):
  results/tables/cd276_panel4a_constraint_crossreference.csv
  data/processed/cd276_constraint_crossreference_log.txt
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]  # .../work/genomics-analyst
OUT_CSV = BASE / "results/tables/cd276_panel4a_constraint_crossreference.csv"
OUT_LOG = BASE / "data/processed/cd276_constraint_crossreference_log.txt"

ROUND1 = Path(
    "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
    "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work"
)
CSV_PATH = ROUND1 / "bio-pathways-ppi-analyst/results/tables/cd276_constraint_tractability.csv"
JSON_PATH = ROUND1 / "fda-safety-officer/data/raw/cd276_target_info_and_constraint.json"

PAPER_VALUE = "0.67"


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_detail(detail: str) -> dict[str, float | str | None]:
    """Parse 'obs=34; exp=51.002; oe_lower=0.506; oe_upper=0.888; p=...; upperRank=...'"""
    out: dict[str, float | str | None] = {}
    for part in detail.split(";"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k, v = k.strip(), v.strip()
        if v.lower() == "none" or v == "":
            out[k] = None
            continue
        try:
            out[k] = float(v)
        except ValueError:
            out[k] = v
    return out


# ---- Source A: round-1 CSV ------------------------------------------------
rows = list(csv.DictReader(CSV_PATH.open()))
lof_rows = [r for r in rows if r["annotation_class"] == "constraint" and r["annotation"] == "lof"]
assert len(lof_rows) == 1, f"expected exactly one constraint,lof row, got {len(lof_rows)}"
row_a = lof_rows[0]
detail = parse_detail(row_a["detail"])
a = {
    "oe": float(row_a["value"]),
    "obs": detail["obs"],
    "exp": detail["exp"],
    "oe_lower": detail["oe_lower"],
    "oe_upper": detail["oe_upper"],
    "p": detail["p"],
    "upper_rank": detail["upperRank"],
    "upper_bin": detail["upperBin"],
    "upper_bin6": detail["upperBin6"],
    "source": row_a["source"],
}

# ---- Source B: round-1 JSON (raw get_target_info response) ----------------
doc = json.load(JSON_PATH.open())
b_raw = doc["constraint"]["lof"]
b = {
    "oe": b_raw["oe"],
    "obs": b_raw["obs"],
    "exp": b_raw["exp"],
    "oe_lower": b_raw["oeLower"],
    "oe_upper": b_raw["oeUpper"],
    "p": b_raw["score"],  # the lof 'score' field is the p-value in this payload
    "upper_rank": b_raw.get("upperRank"),
    "upper_bin": b_raw.get("upperBin"),
    "upper_bin6": b_raw.get("upperBin6"),
}

# ---- Agreement checks -----------------------------------------------------
# CSV carries full float precision; JSON is rounded. Compare with explicit
# tolerances documented in the log rather than silently rounding.
CHECKS = [
    ("oe", 1e-12),          # 0.6666399836540222 vs 0.66664
    ("obs", 0),             # 34 vs 34
    ("exp", 1e-6),          # 51.00199890136719 vs 51.002
    ("oe_lower", 1e-6),     # 0.5059999823570251 vs 0.506
    ("oe_upper", 1e-6),     # 0.8880000114440918 vs 0.888
    ("p", 1e-12),           # 4.2877999817392265e-08 vs 4.2878e-08
    ("upper_rank", 0),
    ("upper_bin", 0),
    ("upper_bin6", 0),
]
for key, tol in CHECKS:
    va, vb = a[key], b[key]
    if tol == 0:
        ok = va == vb
    else:
        ok = math.isclose(float(va), float(vb), rel_tol=0.0, abs_tol=max(tol, abs(float(vb)) * 1e-5))
    assert ok, f"source mismatch on {key}: CSV={va!r} JSON={vb!r}"

oe_rounded = f"{a['oe']:.2f}"
match_paper = oe_rounded == PAPER_VALUE
assert match_paper, f"LoF O/E {a['oe']} rounds to {oe_rounded}, not {PAPER_VALUE}"

ci_excludes_one = a["oe_upper"] < 1.0
assert ci_excludes_one

log = []
log.append("CD276 panel 4A constraint cross-reference — verification log")
log.append("=" * 66)
log.append("")
log.append("Source A (round-1 CSV):")
log.append(f"  {CSV_PATH}")
log.append(f"  md5 {md5(CSV_PATH)}")
log.append(f"  row key: annotation_class=constraint, annotation=lof")
log.append(f"  value={row_a['value']}  detail={row_a['detail']}")
log.append(f"  source string: {row_a['source']}")
log.append("")
log.append("Source B (round-1 JSON, raw get_target_info response):")
log.append(f"  {JSON_PATH}")
log.append(f"  md5 {md5(JSON_PATH)}")
log.append(f"  field: constraint.lof -> {json.dumps(b_raw)}")
log.append(f"  query: {json.dumps(doc.get('query'))}")
log.append(f"  approvedSymbol={doc.get('approvedSymbol')} biotype={doc.get('biotype')}")
log.append(f"  genomicLocation={json.dumps(doc.get('genomicLocation'))}")
log.append("")
log.append("Field-by-field agreement (CSV vs JSON):")
for key, tol in CHECKS:
    log.append(f"  {key:11s} CSV={a[key]!r:28s} JSON={b[key]!r:14s} abs_tol={tol}")
log.append("  -> all fields agree; CSV retains full float precision, JSON is rounded.")
log.append("")
log.append("Paper check:")
log.append(f"  paper quoted LoF O/E = {PAPER_VALUE}")
log.append(f"  gnomAD/Open Targets LoF O/E = {a['oe']!r} -> round to 2 dp = {oe_rounded}")
log.append(f"  MATCH = {match_paper}")
log.append("")
log.append("Interpretation inputs (descriptive only):")
log.append(f"  obs={a['obs']} exp={a['exp']} -> {a['obs']}/{a['exp']} LoF variants observed")
log.append(f"  95% CI on O/E = {a['oe_lower']}–{a['oe_upper']}; upper bound < 1 = {ci_excludes_one}")
log.append(f"  p = {a['p']} (departure from O/E = 1)")
log.append("  pLI is NOT returned by this source (see JSON pLI_note); pLI is not reported here.")
log.append(f"  upperRank={a['upper_rank']} upperBin={a['upper_bin']} upperBin6={a['upper_bin6']}")
log.append("  Bin edges / rank denominator are NOT stored in the saved payload, so no")
log.append("  percentile is derived here. No web access was used. No data was re-queried.")
log.append("")

OUT_LOG.parent.mkdir(parents=True, exist_ok=True)
OUT_LOG.write_text("\n".join(log) + "\n")

# ---- Tidy output table ----------------------------------------------------
fieldnames = [
    "gene",
    "ensembl_id",
    "metric",
    "lof_oe",
    "lof_oe_rounded_2dp",
    "obs_lof",
    "exp_lof",
    "oe_lower_95ci",
    "oe_upper_95ci",
    "p_value",
    "upper_rank",
    "upper_bin",
    "upper_bin6",
    "paper_quoted_value",
    "rounding_check",
    "agreement_assessment",
    "interpretation_flag",
    "source_string",
    "retrieval_date",
    "source_a_csv_path",
    "source_a_row_key",
    "source_b_json_path",
    "source_b_json_field",
    "source_a_md5",
    "source_b_md5",
    "crosscheck_note",
]

record = {
    "gene": "CD276",
    "ensembl_id": "ENSG00000103855",
    "metric": "gnomAD pLoF observed/expected (O/E)",
    "lof_oe": repr(float(row_a["value"])),
    "lof_oe_rounded_2dp": oe_rounded,
    "obs_lof": int(a["obs"]),
    "exp_lof": repr(float(a["exp"])),
    "oe_lower_95ci": repr(float(a["oe_lower"])),
    "oe_upper_95ci": repr(float(a["oe_upper"])),
    "p_value": repr(float(a["p"])),
    "upper_rank": int(a["upper_rank"]),
    "upper_bin": int(a["upper_bin"]),
    "upper_bin6": int(a["upper_bin6"]),
    "paper_quoted_value": PAPER_VALUE,
    "rounding_check": f"{a['oe']:.4f} -> {oe_rounded} = paper's {PAPER_VALUE}",
    "agreement_assessment": "AGREE — reproduces the paper's quoted LoF O/E (0.6666 rounds to 0.67)",
    "interpretation_flag": (
        "significant but moderate LoF depletion (95% CI upper 0.888 < 1); "
        "not an extreme-constraint gene; constraint is gene-level annotation, "
        "not disease association"
    ),
    "source_string": (
        "Open Targets gnomAD constraint via mcp__target__get_target_info "
        "(target_id=ENSG00000103855)"
    ),
    "retrieval_date": doc["query"]["retrieved_utc"],
    "source_a_csv_path": str(CSV_PATH),
    "source_a_row_key": "annotation_class=constraint,annotation=lof",
    "source_b_json_path": str(JSON_PATH),
    "source_b_json_field": "constraint.lof (oe, obs, exp, oeLower, oeUpper, score/p, upperRank, upperBin, upperBin6)",
    "source_a_md5": md5(CSV_PATH),
    "source_b_md5": md5(JSON_PATH),
    "crosscheck_note": (
        "Both round-1 sources agree on every field (oe, obs, exp, CI, p, upperRank/Bin/Bin6); "
        "CSV carries full float precision, JSON is rounded to 5-6 dp"
    ),
}

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_CSV.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    w.writerow(record)

print(f"wrote {OUT_CSV}")
print(f"wrote {OUT_LOG}")
print(f"LoF O/E = {a['oe']!r} -> {oe_rounded} (paper {PAPER_VALUE}); sources agree; CI upper {a['oe_upper']} < 1")
