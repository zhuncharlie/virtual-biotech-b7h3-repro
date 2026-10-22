#!/usr/bin/env python
"""Consistency checks for the panel 4A outputs. Fails loudly on any mismatch.

Revision 2 (2026-10-22): paths resolve against this LIVE workspace; checks added
for the two gene-body locus-overlap universes, the stored within-window score and
distance distributions, and the trait-label audit.
"""
import os
from pathlib import Path
import pandas as pd

# Workspace root = .../work/genomics-analyst (script lives in code/scripts/)
BASE = str(Path(__file__).resolve().parents[2])
T = os.path.join(BASE, "results", "tables")
F = os.path.join(BASE, "results", "figures")
R = os.path.join(BASE, "results", "reports")

errors = []


def check(name, got, want):
    ok = got == want
    print(f"[{'OK' if ok else 'FAIL'}] {name}: got={got!r} want={want!r}")
    if not ok:
        errors.append(name)


ver = pd.read_csv(os.path.join(T, "cd276_round2_germline_verification.csv"))
check("verification rows", len(ver), 9)
check("verification check ids", list(ver.check_id), [f"G{i}" for i in range(1, 10)])

rec = pd.read_csv(os.path.join(T, "cd276_round2_credible_set_window_reconciliation.csv"))
check("reconciliation rows", len(rec), 8)
r = rec.set_index("definition")
check("303 all types", int(r.loc[r.index.str.startswith("R1_QUERY"), "n_credible_sets_all_types"].iloc[0]), 303)
check("303 -> 123 gwas", int(r.loc[r.index.str.startswith("R1_QUERY"), "n_credible_sets_gwas"].iloc[0]), 123)
check("303 -> 116 gwas studies", int(r.loc[r.index.str.startswith("R1_QUERY"), "n_distinct_gwas_studies"].iloc[0]), 116)
check("250kb all", int(r.loc["TSS +/-250 kb", "n_credible_sets_all_types"]), 599)
check("250kb gwas", int(r.loc["TSS +/-250 kb", "n_credible_sets_gwas"]), 224)
check("500kb all", int(r.loc["TSS +/-500 kb", "n_credible_sets_all_types"]), 1252)
check("500kb gwas", int(r.loc["TSS +/-500 kb", "n_credible_sets_gwas"]), 545)
check("gene body all", int(r.loc["CD276 gene body (lead variant inside gene span)", "n_credible_sets_all_types"]), 65)
check("gene body gwas", int(r.loc["CD276 gene body (lead variant inside gene span)", "n_credible_sets_gwas"]), 41)
gb_r1 = r.loc[r.index.str.startswith("CD276 gene body (locus interval overlap; round-1")]
gb_full = r.loc[r.index.str.startswith("CD276 gene body (locus interval overlap; full")]
check("gene body locus overlap round-1 universe all", int(gb_r1["n_credible_sets_all_types"].iloc[0]), 69)
check("gene body locus overlap round-1 universe gwas", int(gb_r1["n_credible_sets_gwas"].iloc[0]), 65)
check("gene body locus overlap full universe all", int(gb_full["n_credible_sets_all_types"].iloc[0]), 201)
check("gene body locus overlap full universe gwas", int(gb_full["n_credible_sets_gwas"].iloc[0]), 195)
check("250kb locus overlap gwas", int(r.loc["TSS +/-250 kb (locus interval overlap)", "n_credible_sets_gwas"]), 134)
check("500kb locus overlap gwas", int(r.loc["TSS +/-500 kb (locus interval overlap)", "n_credible_sets_gwas"]), 286)
check("source files unambiguous", int(rec.source_file.str.contains(" or ").sum()), 0)
check("every reconciliation row has a definition", int(rec.definition.isna().sum()), 0)

# G7 note must contain both computed universes and must not be a bare literal
g7 = ver.set_index("check_id").loc["G7"]
check("G7 note states round-1 universe 69/65", "69 all types / 65 GWAS" in g7.note, True)
check("G7 note states full universe 201/195", "201 all types / 195 GWAS" in g7.note, True)
check("G7 note cites the reconciliation table", "cd276_round2_credible_set_window_reconciliation.csv" in g7.note, True)

ps = pd.read_csv(os.path.join(T, "cd276_round2_per_study_locus_check.csv"))
check("per-study rows", len(ps), 8)
check("per-study with 500kb hit", int((ps.lead_variant_within_500kb_of_TSS > 0).sum()), 0)
check("per-study with gene-body hit", int((ps.lead_variant_in_CD276_gene_body > 0).sum()), 0)
check("per-study with locus overlap 500kb", int((ps.credible_set_locus_overlaps_500kb > 0).sum()), 0)
check("min chr15 distance", int(ps.min_distance_chr15_lead_variant_to_CD276_TSS_bp.min()), 4881214)

e2g = pd.read_csv(os.path.join(T, "cd276_e2g_regulatory_elements.csv"))
lin = e2g[e2g.is_CD276_target_gene]
win = lin[lin.overlaps_TSS_500kb].drop_duplicates("name")
check("E2G total retained rows", len(e2g), 7332)
check("CD276-linked rows", len(lin), 839)
check("window unique elements", len(win), 77)
check("window outside 500kb", int((~lin.overlaps_TSS_500kb).sum()), 762)
check("gene-body linked elements", int(lin.overlaps_CD276_gene_body.sum()), 6)
check("self-promoter linked", int(lin.isSelfPromoter.sum()), 1)
check("window class promoter", int((win["class"] == "promoter").sum()), 17)
check("window class genic", int((win["class"] == "genic").sum()), 31)
check("window class intergenic", int((win["class"] == "intergenic").sum()), 29)
for thr, want in [(0.1, 9), (0.05, 16), (0.02, 29), (0.01, 78), (0.005, 122)]:
    check(f"linked score >= {thr}", int((lin.Score >= thr).sum()), want)
check("all score>=0.02 within window", int((lin[lin.Score >= 0.02].overlaps_TSS_500kb).sum()), 29)
loc = e2g[e2g.overlaps_TSS_500kb]
for thr, want in [(0.1, 24), (0.05, 38), (0.02, 49)]:
    check(f"locus unique elements (any link) score >= {thr}",
          int(loc.loc[loc.Score >= thr, "name"].nunique()), want)
    check(f"locus unique CD276-linked elements score >= {thr}",
          int(loc.loc[(loc.Score >= thr) & loc.is_CD276_target_gene, "name"].nunique()),
          {0.1: 9, 0.05: 16, 0.02: 29}[thr])
check("every delivered row carries a filter", int(e2g["filter"].isna().sum()), 0)

# Revision-2 deliverable tables
linked_tab = pd.read_csv(os.path.join(T, "cd276_e2g_cd276_linked_all_839.csv"))
check("linked deliverable rows", len(linked_tab), 839)
check("linked deliverable has filter", int(linked_tab["filter"].isna().sum()), 0)
win_tab = pd.read_csv(os.path.join(T, "cd276_e2g_within_500kb_77_elements.csv"))
check("window deliverable rows", len(win_tab), 77)
check("window deliverable unique elements", win_tab.name.nunique(), 77)
check("window deliverable has filter", int(win_tab["filter"].isna().sum()), 0)
dist = pd.read_csv(os.path.join(T, "cd276_e2g_within_window_score_distance_distribution.csv"))
check("distribution rows", len(dist), 77)
check("distribution unique elements", dist.element.nunique(), 77)
check("distribution has filter", int(dist["filter"].isna().sum()), 0)
check("distribution score median", round(float(dist.e2g_score.median()), 4), 0.0143)
check("distribution distance median kb", round(float(dist.distance_to_CD276_TSS_bp.median()) / 1000, 0), 241)
dsum = pd.read_csv(os.path.join(T, "cd276_e2g_within_window_score_distance_summary.csv"))
check("distance summary median bp", round(float(dsum.loc[dsum.metric == "distance_to_CD276_TSS_bp_median", "value"].iloc[0]), 1), 241123.0)
check("summary has source md5", "source_file_md5" in set(pd.read_csv(os.path.join(T, "cd276_e2g_summary.csv")).metric), True)

trait = pd.read_csv(os.path.join(T, "cd276_gwas_trait_label_audit.csv"))
check("trait audit has datasets", set(trait.dataset), {"gene_body_gwas_credible_sets", "gene_body_all_credible_sets", "l2g_loci"})
gb_trait = trait[trait.dataset == "gene_body_gwas_credible_sets"]
check("trait audit 13/41 labelled", int(gb_trait.loc[gb_trait.trait_label != "UNLABELLED", "n_rows"].sum()), 13)
check("trait audit 41 total", int(gb_trait.n_rows.sum()), 41)
l2g_trait = trait[trait.dataset == "l2g_loci"]
check("trait audit 17/67 labelled", int(l2g_trait.loc[l2g_trait.trait_label != "UNLABELLED", "n_rows"].sum()), 17)
check("trait audit 67 total", int(l2g_trait.n_rows.sum()), 67)

sm = pd.read_csv(os.path.join(T, "cd276_e2g_summary.csv"))
check("summary has primary threshold", float(sm.loc[sm.metric == "primary_score_threshold", "value"].iloc[0]), 0.02)

for f in ["fig4a_genetics_e2g_cd276.png", "fig4a_genetics_e2g_cd276.pdf"]:
    check(f"figure exists {f}", os.path.exists(os.path.join(F, f)), True)
check("report exists", os.path.exists(os.path.join(R, "cd276_panel4a_report.md")), True)
check("reviewer response exists", os.path.exists(os.path.join(R, "revision_response_to_reviewer.md")), True)

rep = open(os.path.join(R, "cd276_panel4a_report.md")).read()
for token in ["303", "599", "1,252", "65 all types / 41 GWAS", "0/8", "0/67",
              "77 CD276-linked elements", "Score ≥ 0.02", "839", "1,252",
              "Revision 2 changelog", "cd276_e2g_within_window_score_distance_distribution.csv",
              "cd276_gwas_trait_label_audit.csv"]:
    check(f"report contains {token!r}", token in rep, True)

print("\n%d failure(s)" % len(errors))
raise SystemExit(1 if errors else 0)
