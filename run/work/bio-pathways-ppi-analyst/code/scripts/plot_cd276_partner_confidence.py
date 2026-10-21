#!/usr/bin/env python3
"""Plot CD276 interaction-partner confidence by source.

Shows that no retrieved partner reaches the 0.7 high-confidence threshold except
the textmining-only CD8A edge, and that IntAct physical-interaction scores
cluster at 0.35 or below.

Input : data/raw/cd276_mcp_query_results.json
Output: results/figures/cd276_partner_confidence.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json

AGENT_DIR = Path(__file__).resolve().parents[2]
RAW = AGENT_DIR / "data" / "raw" / "cd276_mcp_query_results.json"
OUT = AGENT_DIR / "results" / "figures" / "cd276_partner_confidence.png"

data = json.loads(RAW.read_text())

string_rows = sorted(data["string_interactions"], key=lambda d: d["score"], reverse=True)[:14]
intact_rows = sorted(data["intact_interactions"], key=lambda d: d["score"], reverse=True)[:14]

labels, scores, colors = [], [], []
for r in string_rows:
    labels.append(f"{r['symbol'] or r['ensembl_id']} (STRING)")
    scores.append(r["score"])
    colors.append("#3b6fb6")
for r in intact_rows:
    labels.append(f"{r['symbol'] or r['ensembl_id']} (IntAct)")
    scores.append(r["score"])
    colors.append("#b6653b")

fig, ax = plt.subplots(figsize=(8, 9))
y = range(len(labels))
ax.barh(list(y), scores, color=colors, height=0.72)
ax.set_yticks(list(y))
ax.set_yticklabels(labels, fontsize=7)
ax.invert_yaxis()
ax.axvline(0.7, color="black", linestyle="--", linewidth=1)
ax.text(0.71, 0.5, "0.7 high-confidence threshold", fontsize=7, rotation=90, va="center")
ax.set_xlim(0, 1.0)
ax.set_xlabel("Interaction confidence score (0-1)")
ax.set_title("CD276 (B7-H3) interaction partners by confidence and source\n"
             "STRING combined score vs IntAct MI score; both capped at limit=25/30", fontsize=9)
fig.text(0.01, 0.012,
         "Only CD8A (STRING) crosses 0.7, and its evidence is textmining-only (MI:0110, no PMID). "
         "Highest IntAct score is 0.53 (LGALS1).\nGenes labelled by Ensembl ID only were not resolved to a symbol in this session.",
         fontsize=6.5, va="bottom")
plt.tight_layout(rect=(0, 0.035, 1, 1))
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=200)
print(f"wrote {OUT}")
