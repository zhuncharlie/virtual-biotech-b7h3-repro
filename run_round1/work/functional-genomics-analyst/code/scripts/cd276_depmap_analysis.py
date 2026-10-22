#!/usr/bin/env python3
"""CD276 (B7-H3) DepMap CRISPR essentiality analysis in LUAD and SCLC.

Input : raw MCP result from mcp__functional_genomics__query_gene_essentiality
Output: per-cell-line table, group summary, disease comparator, figure.

The DepMap extract labels cell lines with broad Oncotree categories only:
  - "Non-Small Cell Lung Cancer" (n=98) collapses LUAD, LUSC, large-cell.
  - "Lung Neuroendocrine Tumor" (n=26) mixes SCLC and pulmonary carcinoid.
Therefore LUAD/SCLC membership is assigned from documented cell-line
histology (prior knowledge: Cellosaurus/ATCC/CCLE literature), explicitly
listed below and saved as an auditable mapping. A curated-only analysis is
paired with the broad-label analysis as a sensitivity check.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

WORK = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
            "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/"
            "functional-genomics-analyst")
RAW_SRC = Path("/home/xqinag/.claude/projects/-mnt-beegfs-xqinag-projects-TheVirtualBiotech-"
               "runs-20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/ac473c6c-"
               "4815-4a45-a884-1c979c552fa2/tool-results/"
               "mcp-functional_genomics-query_gene_essentiality-1792504673296.txt")
RAW_DST = WORK / "data/raw/cd276_depmap_essentiality_raw.json"
TABLES = WORK / "results/tables"
FIGS = WORK / "results/figures"
for d in (RAW_DST.parent, TABLES, FIGS):
    d.mkdir(parents=True, exist_ok=True)

if RAW_SRC.exists() and not RAW_DST.exists():
    shutil.copy2(RAW_SRC, RAW_DST)

# ---------------------------------------------------------------------------
# Curated histology mapping (prior knowledge, documented per line).
# Only unambiguous adenocarcinoma / SCLC lines are placed in the core sets.
# Derivatives of the same parental line are excluded from core to avoid
# pseudo-replication; they remain in the "other NSCLC" comparator.
# ---------------------------------------------------------------------------
LUAD_CORE = {
    # classic adenocarcinoma lines, EGFR/KRAS/ALK/BRAF/ROS1 models
    "A549", "ABC-1", "Calu-3", "COR-L105", "EKVX", "HCC-44", "HCC-78",
    "HCC-461", "HCC-827", "HCC-1359", "HOP-62", "LCAM1", "LOU-NH91",
    "LXF-289", "NCI-H23", "NCI-H358", "NCI-H441", "NCI-H522",
    "NCI-H1355", "NCI-H1373", "NCI-H1437", "NCI-H1568", "NCI-H1573",
    "NCI-H1648", "NCI-H1650", "NCI-H1666", "NCI-H1693", "NCI-H1792",
    "NCI-H1793", "NCI-H1944", "NCI-H1975", "NCI-H1993", "NCI-H2009",
    "NCI-H2023", "NCI-H2030", "NCI-H2087", "NCI-H2110", "NCI-H2122",
    "NCI-H2126", "NCI-H2172", "NCI-H2291", "NCI-H3122", "PC-14",
    "RERF-LC-Ad1", "RERF-LC-Ad2", "RERF-LC-AI", "VMRC-LCD",
}
# Lung Neuroendocrine Tumor label is dominated by SCLC; exclude the one
# well-differentiated pulmonary carcinoid line (NCI-H727).
SCLC_CORE = {
    "COR-L279", "COR-L311", "COR-L47", "DMS 273", "DMS 53", "HCC-33",
    "Lu-134-A", "Lu-135", "Lu-139", "Lu-165", "NCI-H1048", "NCI-H1092",
    "NCI-H1694", "NCI-H1836", "NCI-H1882", "NCI-H209", "NCI-H211",
    "NCI-H2171", "NCI-H2286", "NCI-H446", "NCI-H510", "NCI-H526",
    "NCI-H82", "SCLC-22H", "SHP-77",
}
DERIVATIVES = {"A549_CRAF_KD", "HCC-827-GR5", "NCI-H157-DM"}
CARCINOID = {"NCI-H727"}

# ---------------------------------------------------------------------------
# Flatten raw result
# ---------------------------------------------------------------------------
raw = json.loads(RAW_DST.read_text())
rows = []
for tissue_block in raw["essentiality_by_tissue"]:
    tissue = tissue_block["tissue"]["name"]
    for cl in tissue_block["cell_lines"]:
        rows.append({
            "cell_line": cl["cellLineName"],
            "depmap_id": cl["depmapId"],
            "depmap_disease_label": cl["disease"],
            "depmap_tissue": tissue,
            "gene_effect": cl["geneEffect"],
            "depmap_expression": cl["expression"],
        })
df = pd.DataFrame(rows)
assert len(df) == raw["num_cell_lines"], (len(df), raw["num_cell_lines"])

missing = (LUAD_CORE | SCLC_CORE) - set(df["cell_line"])
print("Curated lines not present in DepMap extract:", sorted(missing))
print("Duplicate cell-line names:", df["cell_line"].duplicated().sum())

def classify(r: pd.Series) -> str:
    name = r["cell_line"]
    if name in LUAD_CORE:
        return "LUAD"
    if name in SCLC_CORE:
        return "SCLC"
    if name in DERIVATIVES:
        return "Other NSCLC"
    if name in CARCINOID:
        return "Other lung (carcinoid)"
    if r["depmap_disease_label"] == "Non-Small Cell Lung Cancer":
        return "Other NSCLC"
    if r["depmap_disease_label"] == "Lung Neuroendocrine Tumor":
        return "Other lung (neuroendocrine, unclassified)"
    if r["depmap_disease_label"] == "SMARCA4-deficient undifferentiated tumor":
        return "Other lung (SMARCA4-dUT)"
    if r["depmap_disease_label"] == "Non-Cancerous":
        return "Non-cancerous"
    return "Other lineages"

df["histology_group"] = df.apply(classify, axis=1)
# histology evidence annotation
def evidence(r):
    if r["cell_line"] in LUAD_CORE:
        return "documented lung adenocarcinoma (Cellosaurus/ATCC/CCLE)"
    if r["cell_line"] in SCLC_CORE:
        return "documented small cell lung cancer (Cellosaurus/ATCC/CCLE)"
    if r["cell_line"] in CARCINOID:
        return "documented pulmonary carcinoid (well-differentiated NET)"
    if r["cell_line"] in DERIVATIVES:
        return "derivative line; excluded from core LUAD"
    return "not curated (broad DepMap disease label only)"
df["histology_evidence"] = df.apply(evidence, axis=1)

# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------
def summarize(x: pd.Series) -> dict:
    x = x.dropna()
    n = len(x)
    if n == 0:
        return {"n": 0}
    return {
        "n": n,
        "mean_gene_effect": x.mean(),
        "median_gene_effect": x.median(),
        "sd": x.std(ddof=1) if n > 1 else np.nan,
        "min": x.min(),
        "q10": x.quantile(0.10),
        "q25": x.quantile(0.25),
        "q75": x.quantile(0.75),
        "q90": x.quantile(0.90),
        "max": x.max(),
        "n_effect_lt_-0.3": int((x < -0.3).sum()),
        "frac_effect_lt_-0.3": float((x < -0.3).mean()),
        "n_essential_lt_-0.5": int((x < -0.5).sum()),
        "frac_essential_lt_-0.5": float((x < -0.5).mean()),
        "n_strong_lt_-0.7": int((x < -0.7).sum()),
        "frac_strong_lt_-0.7": float((x < -0.7).mean()),
        "n_effect_gt_0": int((x > 0).sum()),
    }

order = ["LUAD", "SCLC", "Other NSCLC", "Other lung (carcinoid)",
         "Other lung (neuroendocrine, unclassified)", "Other lung (SMARCA4-dUT)",
         "Other lineages", "Non-cancerous"]
summary = []
for g in order:
    sub = df[df["histology_group"] == g]
    if sub.empty:
        continue
    s = summarize(sub["gene_effect"])
    s["histology_group"] = g
    expr = sub["depmap_expression"].dropna()
    s["n_expression"] = len(expr)
    s["mean_expression"] = expr.mean() if len(expr) else np.nan
    s["median_expression"] = expr.median() if len(expr) else np.nan
    s["expression_min"] = expr.min() if len(expr) else np.nan
    s["expression_max"] = expr.max() if len(expr) else np.nan
    s["frac_expression_gt_4"] = float((expr > 4).mean()) if len(expr) else np.nan
    s["frac_expression_gt_5"] = float((expr > 5).mean()) if len(expr) else np.nan
    summary.append(s)
summ = pd.DataFrame(summary)
cols = ["histology_group"] + [c for c in summ.columns if c != "histology_group"]
summ = summ[cols]
summ.to_csv(TABLES / "cd276_depmap_group_summary.csv", index=False)

# ---------------------------------------------------------------------------
# Group comparisons (effect size + tests)
# ---------------------------------------------------------------------------
comparisons = []
def compare(a, b):
    x = df.loc[df["histology_group"] == a, "gene_effect"].dropna()
    y = df.loc[df["histology_group"] == b, "gene_effect"].dropna()
    if len(x) < 2 or len(y) < 2:
        return None
    pooled = np.sqrt(((len(x)-1)*x.var(ddof=1) + (len(y)-1)*y.var(ddof=1)) / (len(x)+len(y)-2))
    d = (x.mean() - y.mean()) / pooled if pooled > 0 else np.nan
    welch = stats.ttest_ind(x, y, equal_var=False)
    mw = stats.mannwhitneyu(x, y, alternative="two-sided")
    return {
        "group_a": a, "group_b": b,
        "n_a": len(x), "n_b": len(y),
        "mean_a": x.mean(), "mean_b": y.mean(),
        "mean_difference_a_minus_b": x.mean() - y.mean(),
        "cohens_d": d,
        "welch_t": welch.statistic, "welch_p": welch.pvalue,
        "mannwhitney_U": mw.statistic, "mannwhitney_p": mw.pvalue,
    }
for a, b in [("LUAD", "Other NSCLC"), ("LUAD", "Other lineages"),
             ("SCLC", "Other lineages"), ("SCLC", "Other NSCLC"),
             ("LUAD", "SCLC")]:
    r = compare(a, b)
    if r:
        comparisons.append(r)
pd.DataFrame(comparisons).to_csv(TABLES / "cd276_depmap_group_comparisons.csv", index=False)

# Broad-label sensitivity check (what the DepMap disease field alone says)
broad = []
for lab in ["Non-Small Cell Lung Cancer", "Lung Neuroendocrine Tumor"]:
    x = df.loc[df["depmap_disease_label"] == lab, "gene_effect"].dropna()
    s = summarize(x); s["label"] = lab; broad.append(s)
pd.DataFrame(broad).to_csv(TABLES / "cd276_depmap_broad_label_sensitivity.csv", index=False)

# ---------------------------------------------------------------------------
# Disease-level comparator (reproduces compare_essentiality_across_diseases)
# ---------------------------------------------------------------------------
dis = df.groupby("depmap_disease_label")["gene_effect"].agg(
    n="count", mean_gene_effect="mean",
    essential_fraction=lambda x: float((x < -0.5).mean())).reset_index()
dis = dis.sort_values("mean_gene_effect").reset_index(drop=True)
dis["rank_most_essential"] = np.arange(1, len(dis)+1)
dis.to_csv(TABLES / "cd276_depmap_disease_comparator.csv", index=False)
print("\nDisease comparator ranks:")
print(dis[dis["depmap_disease_label"].isin(
    ["Non-Small Cell Lung Cancer", "Lung Neuroendocrine Tumor"])].to_string(index=False))

# ---------------------------------------------------------------------------
# Required per-cell-line table (LUAD + SCLC only)
# ---------------------------------------------------------------------------
core = df[df["histology_group"].isin(["LUAD", "SCLC"])].copy()
core = core.sort_values(["histology_group", "gene_effect"], ascending=[True, True])
core_out = core[["cell_line", "depmap_id", "histology_group", "depmap_disease_label",
                 "depmap_tissue", "gene_effect", "depmap_expression",
                 "histology_evidence"]]
core_out.to_csv(TABLES / "cd276_depmap_luad_sclc.csv", index=False)

# explicit distribution bins (requested: report distribution, not one number)
bin_edges = [-np.inf, -0.7, -0.5, -0.3, -0.1, 0.1, np.inf]
bin_labels = ["< -0.7 (strong essential)", "-0.7 to -0.5 (essential)",
              "-0.5 to -0.3 (weak dependency)", "-0.3 to -0.1",
              "-0.1 to 0.1", "> 0.1"]
bin_rows = []
for g in ["LUAD", "SCLC", "Other NSCLC", "Other lineages"]:
    x = df.loc[df["histology_group"] == g, "gene_effect"].dropna()
    counts, _ = np.histogram(x, bins=bin_edges)
    for lab, c in zip(bin_labels, counts):
        bin_rows.append({"histology_group": g, "gene_effect_bin": lab,
                         "n": int(c), "fraction": float(c / len(x)) if len(x) else np.nan})
pd.DataFrame(bin_rows).to_csv(TABLES / "cd276_depmap_gene_effect_bins.csv", index=False)

# full annotated table for audit
df.sort_values(["histology_group", "cell_line"]).to_csv(
    TABLES / "cd276_depmap_all_cell_lines_annotated.csv", index=False)

# mapping table
mp = df[["cell_line", "depmap_disease_label", "histology_group", "histology_evidence"]].copy()
mp.to_csv(TABLES / "cd276_histology_mapping.csv", index=False)

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plot_groups = ["LUAD", "SCLC", "Other NSCLC", "Other lineages"]
colors = {"LUAD": "#1f77b4", "SCLC": "#d62728", "Other NSCLC": "#7f7f7f",
          "Other lineages": "#c7c7c7"}
fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))

# panel A: gene effect
data_a = [df.loc[df["histology_group"] == g, "gene_effect"].dropna().values
          for g in plot_groups]
bp = axes[0].boxplot(data_a, labels=plot_groups, showfliers=False, patch_artist=True,
                     medianprops=dict(color="black"))
for patch, g in zip(bp["boxes"], plot_groups):
    patch.set_facecolor(colors[g]); patch.set_alpha(0.55)
rng = np.random.default_rng(42)
for i, (g, vals) in enumerate(zip(plot_groups, data_a), start=1):
    jit = rng.normal(0, 0.06, len(vals))
    axes[0].scatter(np.full(len(vals), i) + jit, vals, s=10, alpha=0.45,
                    color=colors[g], linewidths=0)
axes[0].axhline(0, color="black", lw=0.8, ls="--")
axes[0].axhline(-0.5, color="firebrick", lw=0.8, ls=":")
axes[0].set_ylabel("DepMap CRISPR gene effect (CERES/Chronos)")
axes[0].set_title("A. CD276 intrinsic dependency")
axes[0].tick_params(axis="x", rotation=20)

# panel B: expression
data_b = [df.loc[df["histology_group"] == g, "depmap_expression"].dropna().values
          for g in plot_groups]
bp2 = axes[1].boxplot(data_b, labels=plot_groups, showfliers=False, patch_artist=True,
                      medianprops=dict(color="black"))
for patch, g in zip(bp2["boxes"], plot_groups):
    patch.set_facecolor(colors[g]); patch.set_alpha(0.55)
for i, (g, vals) in enumerate(zip(plot_groups, data_b), start=1):
    jit = rng.normal(0, 0.06, len(vals))
    axes[1].scatter(np.full(len(vals), i) + jit, vals, s=10, alpha=0.45,
                    color=colors[g], linewidths=0)
axes[1].set_ylabel("CD276 expression (DepMap units, likely log2(TPM+1))")
axes[1].set_title("B. CD276 antigen expression")
axes[1].tick_params(axis="x", rotation=20)

n_luad = int((df["histology_group"] == "LUAD").sum())
n_sclc = int((df["histology_group"] == "SCLC").sum())
n_nsclc = int((df["histology_group"] == "Other NSCLC").sum())
fig.suptitle(f"CD276 / B7-H3 in DepMap: LUAD n={n_luad}, SCLC n={n_sclc}, "
             f"other NSCLC n={n_nsclc}; no lineage is dependent", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIGS / "cd276_depmap_luad_sclc_distribution.png", dpi=300)
fig.savefig(FIGS / "cd276_depmap_luad_sclc_distribution.pdf")
plt.close(fig)

# ---------------------------------------------------------------------------
# Console report
# ---------------------------------------------------------------------------
print("\n=== GROUP SUMMARY ===")
with pd.option_context("display.width", 200, "display.max_columns", 50):
    print(summ[["histology_group", "n", "mean_gene_effect", "median_gene_effect",
                "sd", "min", "q25", "q75", "max", "frac_essential_lt_-0.5",
                "frac_strong_lt_-0.7", "mean_expression", "median_expression",
                "expression_min", "expression_max", "frac_expression_gt_4",
                "frac_expression_gt_5"]].to_string(index=False))
print("\n=== COMPARISONS ===")
with pd.option_context("display.width", 220):
    print(pd.DataFrame(comparisons)[["group_a", "group_b", "n_a", "n_b",
                                     "mean_a", "mean_b", "mean_difference_a_minus_b",
                                     "cohens_d", "welch_p", "mannwhitney_p"]].to_string(index=False))
print("\n=== ESSENTIAL-FRACTION CHECK (LUAD/SCLC) ===")
for g in ["LUAD", "SCLC"]:
    x = df.loc[df["histology_group"] == g, "gene_effect"].dropna()
    print(g, "n=", len(x), "min=", round(x.min(), 3),
          "lines < -0.5:", sorted(df.loc[(df["histology_group"] == g) & (df["gene_effect"] < -0.5), "cell_line"].tolist()))
print("\nWrote outputs to", TABLES, "and", FIGS)
