#!/usr/bin/env python
"""Verify the round-1 DepMap CD276 artifacts are present and internally consistent.

Does NOT re-query DepMap. Recomputes group statistics from the saved per-cell-line
table and checks them against the saved group-summary table, checks that group
membership sums to the raw JSON cell-line total, and checks every artifact exists.

Outputs:
  results/tables/round1_depmap_verification.csv
  results/tables/round1_depmap_recomputed_group_summary.csv
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

# Round-1 inputs were copied byte-for-byte into this run so verification does not
# depend on another run's directory. Paths resolve from this file.
WORK = Path(__file__).resolve().parents[2]
R1 = WORK / "data/raw/round1_depmap_inputs"
T = R1 / "tables"
F = R1 / "figures"
RAW = R1 / "cd276_depmap_essentiality_raw.json"
OUT_T = WORK / "results/tables"
os.makedirs(OUT_T, exist_ok=True)

checks = []


def add(check, expected, observed, passed, note=""):
    checks.append({"check": check, "expected": expected, "observed": observed,
                   "pass": bool(passed), "note": note})


# ---- files present and parseable --------------------------------------------------
files = [
    "cd276_depmap_luad_sclc.csv", "cd276_depmap_group_summary.csv",
    "cd276_depmap_gene_effect_bins.csv", "cd276_depmap_group_comparisons.csv",
    "cd276_depmap_disease_comparator.csv", "cd276_depmap_broad_label_sensitivity.csv",
    "cd276_histology_mapping.csv", "cd276_depmap_all_cell_lines_annotated.csv",
    "cd276_tahoe_query_status.json",
]
tables = {}
for name in files:
    path = os.path.join(T, name)
    exists = os.path.exists(path) and os.path.getsize(path) > 0
    add(f"file_present_nonzero:{name}", "exists >0 bytes",
        "exists" if exists else "MISSING/EMPTY", exists)
    if name.endswith(".csv") and exists:
        tables[name] = pd.read_csv(path)
    elif name.endswith(".json") and exists:
        tables[name] = json.load(open(path))

for name in ["cd276_depmap_luad_sclc_distribution.png",
             "cd276_depmap_luad_sclc_distribution.pdf"]:
    path = os.path.join(F, name)
    ok = os.path.exists(path) and os.path.getsize(path) > 0
    add(f"figure_present_nonzero:{name}", "exists >0 bytes",
        os.path.getsize(path) if os.path.exists(path) else "MISSING", ok)

# ---- core tables -----------------------------------------------------------------
lines = tables["cd276_depmap_luad_sclc.csv"]
all_lines = tables["cd276_depmap_all_cell_lines_annotated.csv"]
summary = tables["cd276_depmap_group_summary.csv"].set_index("histology_group")
comparator = tables["cd276_depmap_disease_comparator.csv"]
raw = tables["cd276_tahoe_query_status.json"]

add("luad_sclc_row_count", 71, len(lines), len(lines) == 71)
add("luad_row_count", 46, int((lines["histology_group"] == "LUAD").sum()),
    int((lines["histology_group"] == "LUAD").sum()) == 46)
add("sclc_row_count", 25, int((lines["histology_group"] == "SCLC").sum()),
    int((lines["histology_group"] == "SCLC").sum()) == 25)
add("luad_sclc_unique_depmap_ids", 71, lines["depmap_id"].nunique(),
    lines["depmap_id"].nunique() == 71)
add("luad_sclc_missing_gene_effect", 0, int(lines["gene_effect"].isna().sum()),
    lines["gene_effect"].isna().sum() == 0)
add("all_lines_row_count", 1183, len(all_lines), len(all_lines) == 1183)
add("all_lines_unique_depmap_ids", 1183, all_lines["depmap_id"].nunique(),
    all_lines["depmap_id"].nunique() == 1183)
add("all_lines_missing_gene_effect", 0, int(all_lines["gene_effect"].isna().sum()),
    all_lines["gene_effect"].isna().sum() == 0)

raw_json = json.load(open(RAW))
add("raw_json_num_cell_lines", 1183, raw_json.get("num_cell_lines"),
    raw_json.get("num_cell_lines") == 1183)
tissue_total = sum(t.get("num_cell_lines", 0) for t in raw_json["essentiality_by_tissue"])
add("raw_json_tissue_counts_sum", 1183, tissue_total, tissue_total == 1183)
add("raw_json_found", True, raw_json.get("found"), raw_json.get("found") is True)
add("raw_json_is_essential", False, raw_json.get("is_essential"),
    raw_json.get("is_essential") is False)

# ---- recompute group statistics from per-cell-line data ---------------------------
recomp = (all_lines.groupby("histology_group")["gene_effect"]
          .agg(n="size", mean="mean", median="median", sd="std", min="min", max="max")
          .reset_index())
recomp["frac_essential_lt_-0.5"] = all_lines.assign(ess=all_lines["gene_effect"] < -0.5) \
    .groupby("histology_group")["ess"].mean().values
recomp["n_essential_lt_-0.5"] = all_lines.assign(ess=all_lines["gene_effect"] < -0.5) \
    .groupby("histology_group")["ess"].sum().values
recomp["frac_strong_lt_-0.7"] = all_lines.assign(ess=all_lines["gene_effect"] < -0.7) \
    .groupby("histology_group")["ess"].mean().values
recomp = recomp.sort_values("histology_group").reset_index(drop=True)
recomp.to_csv(os.path.join(OUT_T, "round1_depmap_recomputed_group_summary.csv"), index=False)

add("group_rows_sum_to_raw_total", 1183, int(recomp["n"].sum()),
    int(recomp["n"].sum()) == 1183)

for group, exp_n, exp_mean, exp_median in [
        ("LUAD", 46, -0.23034075154347822, -0.244609455),
        ("SCLC", 25, -0.20397630699999997, -0.18130262),
        ("Other NSCLC", 52, -0.23840156584038466, -0.24652950499999998),
        ("Other lineages", 1041, -0.22097978695334294, -0.21249175),
        ("Non-cancerous", 16, -0.1632603015, -0.142390305)]:
    r = recomp[recomp["histology_group"] == group].iloc[0]
    add(f"{group}:n_summary_vs_recomputed", exp_n, int(r["n"]), int(r["n"]) == exp_n)
    add(f"{group}:mean_summary_vs_recomputed", round(exp_mean, 9), round(float(r["mean"]), 9),
        abs(float(r["mean"]) - exp_mean) < 1e-9)
    add(f"{group}:median_summary_vs_recomputed", round(exp_median, 9),
        round(float(r["median"]), 9), abs(float(r["median"]) - exp_median) < 1e-9)
    if group in summary.index:
        s = summary.loc[group]
        add(f"{group}:summary_table_mean_matches_recomputed",
            round(float(s["mean_gene_effect"]), 9), round(float(r["mean"]), 9),
            abs(float(s["mean_gene_effect"]) - float(r["mean"])) < 1e-9)
        add(f"{group}:summary_table_n_matches_recomputed",
            int(s["n"]), int(r["n"]), int(s["n"]) == int(r["n"]))

add("disease_comparator_rows", 78, len(comparator), len(comparator) == 78)
add("disease_comparator_n_sum", 1183, int(comparator["n"].sum()),
    int(comparator["n"].sum()) == 1183)
add("disease_comparator_rank_unique", True,
    comparator["rank_most_essential"].is_unique,
    comparator["rank_most_essential"].is_unique)

# Context: round-1 report's headline numbers
add("reported_luad_mean_matches", -0.230, round(float(recomp.loc[recomp.histology_group == 'LUAD', 'mean'].iloc[0]), 3),
    round(float(recomp.loc[recomp.histology_group == 'LUAD', 'mean'].iloc[0]), 3) == -0.230)
add("reported_sclc_mean_matches", -0.204, round(float(recomp.loc[recomp.histology_group == 'SCLC', 'mean'].iloc[0]), 3),
    round(float(recomp.loc[recomp.histology_group == 'SCLC', 'mean'].iloc[0]), 3) == -0.204)

out = pd.DataFrame(checks)
out.to_csv(os.path.join(OUT_T, "round1_depmap_verification.csv"), index=False)
print(out.to_string(index=False))
print("\nPASS:", int(out["pass"].sum()), "/", len(out))
if not out["pass"].all():
    print("FAILED CHECKS:")
    print(out.loc[~out["pass"]].to_string(index=False))
