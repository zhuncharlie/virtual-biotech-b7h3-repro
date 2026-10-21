#!/usr/bin/env python3
"""Build the CD276 (B7-H3) pathway / GO / PPI evidence table.

Input : data/raw/cd276_mcp_query_results.json  (transcribed MCP tool responses)
Output: results/tables/cd276_pathways_interactions.csv

Every row is traceable to one MCP tool call recorded in the input file's
provenance block. No values are imputed: unresolved gene symbols are left blank
with symbol_verified = false in the input.
"""

import csv
import json
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parents[2]
RAW = AGENT_DIR / "data" / "raw" / "cd276_mcp_query_results.json"
OUT = AGENT_DIR / "results" / "tables" / "cd276_pathways_interactions.csv"

COLUMNS = [
    "record_type",
    "gene_symbol",
    "ensembl_id",
    "source",
    "score",
    "score_type",
    "detection_method",
    "mi_identifier",
    "evidence_count",
    "go_aspect",
    "go_id",
    "go_term",
    "go_evidence_code",
    "reference",
    "notes",
]


def main() -> None:
    data = json.loads(RAW.read_text())
    names = data["go_term_names"]
    rows = []

    # --- Pathway annotation status -------------------------------------------
    rq = data["reactome_query"]
    rows.append(
        {
            "record_type": "Reactome_pathway",
            "gene_symbol": "CD276",
            "ensembl_id": data["provenance"]["ensembl_id"],
            "source": "Reactome via mcp__pathway__get_gene_pathways",
            "evidence_count": rq["count"],
            "notes": f"count=0; message='{rq['message']}'; search_pathways('CD276') also returned 0",
        }
    )

    for q in data["go_endpoint_queries"]:
        rows.append(
            {
                "record_type": "GO_endpoint_status",
                "gene_symbol": "CD276",
                "ensembl_id": data["provenance"]["ensembl_id"],
                "source": "mcp__pathway__get_gene_ontology",
                "evidence_count": q["count"],
                "go_aspect": q["aspect"],
                "notes": "count=0 from the pathway-MCP GO endpoint; GO terms below come from mcp__target__get_target_info instead",
            }
        )

    # --- GO annotations ------------------------------------------------------
    for g in data["go_annotations_from_target_info"]:
        rows.append(
            {
                "record_type": "GO_annotation",
                "gene_symbol": "CD276",
                "ensembl_id": data["provenance"]["ensembl_id"],
                "source": "Open Targets via mcp__target__get_target_info",
                "go_aspect": g["aspect"],
                "go_id": g["go_id"],
                "go_term": names.get(g["go_id"], ""),
                "go_evidence_code": g["evidence"],
                "reference": g["source"],
                "notes": "",
            }
        )

    # --- STRING interactions -------------------------------------------------
    for s in data["string_interactions"]:
        rows.append(
            {
                "record_type": "PPI_STRING",
                "gene_symbol": s["symbol"] or "",
                "ensembl_id": s["ensembl_id"],
                "source": "STRING v12 via mcp__interaction__get_interactions",
                "score": s["score"],
                "score_type": "STRING combined score (0-1)",
                "evidence_count": s["count"],
                "notes": (
                    "top-scoring partner in the network; textmining-only evidence, pubmedId null"
                    if s["symbol"] == "CD8A"
                    else ("symbol unresolved in this session" if not s["symbol_verified"] else "")
                ),
            }
        )

    # --- IntAct interactions -------------------------------------------------
    for i in data["intact_interactions"]:
        note = "IntAct score 0.35 is the modal floor of this network (single-observation records); low confidence"
        if i["score"] == 0.53:
            note = "highest IntAct score in this network (3 observations); still below the 0.7 high-confidence threshold"
        if not i["symbol_verified"]:
            note += "; symbol unresolved in this session"
        rows.append(
            {
                "record_type": "PPI_IntAct",
                "gene_symbol": i["symbol"] or "",
                "ensembl_id": i["ensembl_id"],
                "source": "IntAct via mcp__interaction__get_interactions",
                "score": i["score"],
                "score_type": "IntAct MI score (0-1)",
                "evidence_count": i["count"],
                "reference": i["uniprot"],
                "notes": note,
            }
        )

    # --- STRING evidence records --------------------------------------------
    for e in data["interaction_evidence_string"]:
        rows.append(
            {
                "record_type": "PPI_evidence",
                "gene_symbol": e["symbol"] or "",
                "ensembl_id": e["ensembl_id"],
                "source": "STRING v12 via mcp__interaction__get_interaction_evidence",
                "score": e["evidenceScore"],
                "score_type": "STRING evidence channel score (0-1)",
                "detection_method": e["method"],
                "mi_identifier": e["mi"],
                "reference": e["pubmedId"],
                "notes": (
                    f"interactionScore={e['interactionScore']}; pubmedId null"
                    if e["pubmedId"] is None
                    else f"interactionScore={e['interactionScore']}"
                ),
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLUMNS})

    counts = {}
    for r in rows:
        counts[r["record_type"]] = counts.get(r["record_type"], 0) + 1
    print(f"wrote {OUT} ({len(rows)} rows)")
    for k, v in counts.items():
        print(f"  {k}: {v}")

    write_constraint_table(data)
    write_paralogue_table(data)


def write_paralogue_table(data):
    """Human paralogues of CD276 with pairwise identity (antibody cross-reactivity context)."""
    out = AGENT_DIR / "results" / "tables" / "cd276_human_paralogues.csv"
    rows = sorted(data["human_paralogues"], key=lambda d: d["query_pct_identity"], reverse=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(
            fh, fieldnames=["symbol", "ensembl_id", "query_pct_identity", "target_pct_identity"]
        )
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")


def write_constraint_table(data):
    """Target-level constraint / tractability / localisation, used for the safety read-out."""
    out = AGENT_DIR / "results" / "tables" / "cd276_constraint_tractability.csv"
    ti = data["target_info"]
    rows = []

    for c in ti["constraint"]:
        rows.append(
            {
                "annotation_class": "constraint",
                "annotation": c["constraintType"],
                "value": c["oe"],
                "detail": f"obs={c['obs']}; exp={c['exp']}; oe_lower={c['oeLower']}; oe_upper={c['oeUpper']}; "
                f"p={c['score']}; upperRank={c['upperRank']}; upperBin={c['upperBin']}; upperBin6={c['upperBin6']}",
                "source": "Open Targets gnomAD constraint via mcp__target__get_target_info",
            }
        )
    for t in ti["tractability"]:
        if t["value"]:
            rows.append(
                {
                    "annotation_class": "tractability",
                    "annotation": f"{t['modality']}: {t['id']}",
                    "value": "true",
                    "detail": "",
                    "source": "Open Targets tractability via mcp__target__get_target_info",
                }
            )
    for loc in ti["subcellularLocations"]:
        rows.append(
            {
                "annotation_class": "subcellular_location",
                "annotation": loc["location"],
                "value": "",
                "detail": f"source={loc['source']}; termSL={loc['termSL']}",
                "source": "mcp__target__get_target_info",
            }
        )
    rows.append(
        {
            "annotation_class": "target_class",
            "annotation": ti["targetClass"][0]["label"],
            "value": "l1",
            "detail": "",
            "source": "mcp__target__get_target_info",
        }
    )
    rows.append(
        {
            "annotation_class": "field_status",
            "annotation": "safetyLiabilities",
            "value": "null",
            "detail": "no safety-liability annotation returned for CD276",
            "source": "mcp__target__get_target_info",
        }
    )
    rows.append(
        {
            "annotation_class": "field_status",
            "annotation": "pathways",
            "value": "null",
            "detail": "Open Targets pathways field null, consistent with the Reactome count=0 result",
            "source": "mcp__target__get_target_info",
        }
    )

    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["annotation_class", "annotation", "value", "detail", "source"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
