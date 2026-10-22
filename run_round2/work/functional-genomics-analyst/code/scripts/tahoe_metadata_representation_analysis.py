#!/usr/bin/env python
"""Bounded Tahoe-100M analysis possible without the pseudobulk DE shards.

The functional_genomics MCP server cannot open Tahoe (TAHOE_DATA_PATH unset),
and the 1,026 DE shards total 82.76 GiB, so differential-expression rows are
not retrievable inside this non-blocking track. The four small metadata tables
from the same pinned release (2dc57900) are retrievable and answer two narrow,
positive-scope questions:

  1. Is CD276 in the Tahoe-100M gene vocabulary?
  2. Are any B7-H3 (CD276)-targeted agents in the Tahoe-100M drug panel?

It also cross-references the Tahoe cell-line list with round-1 DepMap CD276
expression, so a future DE analysis knows which lung lines to prioritise.

Source: Tahoe-100M (tahoebio/Tahoe-100M, revision 2dc57900b7981cfcf5e211527169a0b006546a95),
official Hugging Face release, metadata tables only. CANCER CELL LINES ONLY.
This is NOT a substitute for the MCP DE query and says nothing about the
transcriptional effect of any drug on CD276.
"""
import json
import os
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# Paths are resolved from this file (parents[2] == the agent workspace), so the
# script runs unchanged from any run directory. Inputs were copied byte-for-byte
# from SOURCE run 20261021-113551-...-ef6e8b35; see the report's provenance table.
WORK = Path(__file__).resolve().parents[2]
META = WORK / "data/raw/tahoe_metadata/metadata"
R1 = WORK / "data/raw/round1_depmap_inputs/tables"
OUT_T = WORK / "results/tables"
OUT_F = WORK / "results/figures"
os.makedirs(OUT_T, exist_ok=True)
os.makedirs(OUT_F, exist_ok=True)

B7H3_AGENT_ALIASES = [
    "enoblituzumab", "mga271",
    "ifinatamab", "ds-7300", "ds7300",
    "vobramitamab", "mgc018",
    "omburtamab", "8h9",
    "b7-h3", "b7h3", "cd276",
]

gene = pd.read_parquet(os.path.join(META, "gene_metadata.parquet"))
drug = pd.read_parquet(os.path.join(META, "drug_metadata.parquet"))
sample = pd.read_parquet(os.path.join(META, "sample_metadata.parquet"))
cline = pd.read_parquet(os.path.join(META, "cell_line_metadata.parquet"))

# ---- 1. CD276 in gene vocabulary -------------------------------------------------
cd276 = gene[gene["gene_symbol"].str.upper() == "CD276"]
gene_check = {
    "gene_symbol": "CD276",
    "present_in_gene_metadata": bool(len(cd276)),
    "ensembl_id": cd276["ensembl_id"].iloc[0] if len(cd276) else None,
    "token_id": int(cd276["token_id"].iloc[0]) if len(cd276) else None,
    "n_genes_in_vocabulary": int(len(gene)),
}

# ---- 2. B7-H3 agents in the drug panel -------------------------------------------
text_cols = [c for c in drug.columns if drug[c].dtype == object]
drug_text = drug[text_cols].fillna("").astype(str).agg(" | ".join, axis=1).str.lower()
target_text = drug["targets"].fillna("").astype(str).str.upper()

target_cd276 = drug[target_text.str.contains("CD276", regex=False)]
drug_rows = []
for alias in B7H3_AGENT_ALIASES:
    pattern = re.escape(alias.lower())
    name_hit = drug[drug["drug"].fillna("").astype(str).str.lower().str.contains(pattern, regex=True)]
    any_hit = drug[drug_text.str.contains(pattern, regex=True)]
    drug_rows.append({
        "alias_searched": alias,
        "n_name_matches": int(len(name_hit)),
        "n_any_field_matches": int(len(any_hit)),
        "matched_drugs": ";".join(sorted(set(any_hit["drug"].astype(str)))) if len(any_hit) else "",
    })
drug_checks = pd.DataFrame(drug_rows)
drug_checks.to_csv(os.path.join(OUT_T, "tahoe_drug_panel_b7h3_check.csv"), index=False)

panel_scope = {
    "n_drugs_in_drug_metadata": int(drug["drug"].nunique()),
    "n_drugs_with_annotated_target": int(drug["targets"].notna().sum()),
    "n_drugs_without_annotated_target": int(drug["targets"].isna().sum()),
    "n_drugs_targeting_CD276": int(target_cd276["drug"].nunique()),
    "n_drugs_name_or_field_matching_any_b7h3_alias": int(
        drug_checks.loc[drug_checks["alias_searched"] != "cd276", "matched_drugs"]
        .replace("", pd.NA).dropna().pipe(lambda s: len({x for v in s for x in v.split(";") if x}))
    ),
    "n_samples_in_sample_metadata": int(len(sample)),
    "n_distinct_drugs_in_sample_metadata": int(sample["drug"].nunique()),
}

# ---- 3. Cell lines present, lung subset, CD276 expression context ------------------
lines = (cline.drop_duplicates(subset=["Cell_ID_DepMap", "cell_name"])
         .loc[:, ["cell_name", "Cell_ID_DepMap", "Cell_ID_Cellosaur", "Organ"]]
         .copy())
lines["Organ"] = lines["Organ"].fillna("Unknown")

round1 = pd.read_csv(os.path.join(R1, "cd276_depmap_all_cell_lines_annotated.csv"))
ctx = lines.merge(round1, left_on="Cell_ID_DepMap", right_on="depmap_id", how="left")
ctx["matched_round1_depmap"] = ctx["gene_effect"].notna()
ctx_out = ctx.loc[:, ["cell_name", "Cell_ID_DepMap", "Organ", "cell_line",
                      "histology_group", "gene_effect", "depmap_expression",
                      "matched_round1_depmap"]]
ctx_out = ctx_out.sort_values(["Organ", "cell_name"])
ctx_out.to_csv(os.path.join(OUT_T, "tahoe_cell_lines_cd276_context.csv"), index=False)

lung = ctx[ctx["Organ"] == "Lung"].copy()
lung_out = lung.loc[:, ["cell_name", "Cell_ID_DepMap", "histology_group",
                        "gene_effect", "depmap_expression", "matched_round1_depmap"]]
lung_out = lung_out.sort_values(["histology_group", "depmap_expression"],
                                ascending=[True, False])
lung_out.to_csv(os.path.join(OUT_T, "tahoe_lung_cell_lines_cd276_context.csv"), index=False)

# ---- 4. Figure: CD276 expression in Tahoe lung lines that map to DepMap -----------
plot_df = lung.dropna(subset=["depmap_expression"]).copy()
plot_df["group_label"] = plot_df["histology_group"].fillna("unmapped/unannotated")
order = [g for g in ["LUAD", "SCLC", "Other NSCLC"] if g in set(plot_df["group_label"])]
plot_df = plot_df.sort_values("depmap_expression", ascending=False)
fig, ax = plt.subplots(figsize=(8.2, 4.2))
colors = {"LUAD": "#2b6cb0", "SCLC": "#c53030", "Other NSCLC": "#718096"}
ax.scatter(range(len(plot_df)), plot_df["depmap_expression"],
           c=[colors.get(g, "#a0aec0") for g in plot_df["group_label"]], s=46, zorder=3)
ax.set_xticks(range(len(plot_df)))
ax.set_xticklabels(plot_df["cell_name"], rotation=60, ha="right", fontsize=8)
ax.set_ylabel("DepMap CD276 expression\n(relative units)")
ax.set_title("CD276 expression in Tahoe-100M lung cancer lines\n(left axis: round-1 DepMap values; n=%d lines mapped)"
             % len(plot_df), fontsize=10)
for g, c in colors.items():
    if g in set(plot_df["group_label"]):
        ax.scatter([], [], c=c, label=g, s=40)
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(OUT_F, "tahoe_lung_lines_cd276_expression.png"), dpi=200)
plt.close(fig)

summary = {
    "data_source": "Tahoe-100M metadata tables (pinned revision 2dc57900), official Hugging Face release",
    "scope": "cancer cell lines only; metadata-level representation, NOT differential expression",
    "gene_vocabulary_check": gene_check,
    "drug_panel_scope": panel_scope,
    "n_unique_cell_lines": int(len(lines)),
    "n_lung_cell_lines": int((lines["Organ"] == "Lung").sum()),
    "n_cell_lines_matched_to_round1_depmap": int(ctx["matched_round1_depmap"].sum()),
    "n_lung_lines_matched_to_round1_depmap": int(lung["matched_round1_depmap"].sum()),
    "lung_lines_with_cd276_expression": int(lung["depmap_expression"].notna().sum()),
    "limitations": [
        "Drug target annotation is absent for 115/379 drugs; absence of a CD276 target or a B7-H3 agent name is a statement about this annotated panel, not proof no such molecule was screened.",
        "CD276 expression values are round-1 DepMap bulk transcript levels, not Tahoe-100M measurements.",
        "No perturbation effect on CD276 is assessed; the DE shards could not be queried.",
    ],
}
out = os.path.join(OUT_T, "tahoe_metadata_scope_summary.json")
with open(out, "w") as fh:
    json.dump(summary, fh, indent=2)
print(json.dumps(summary, indent=2))
