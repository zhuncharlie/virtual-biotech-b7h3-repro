# Revision response — Panel 4A (CD276 germline credible sets + ENCODE-rE2G)

**Reviewer source:** `work/scientific-reviewer/scientific_review_interim_panels1-6.md` §1; `work/scientific-reviewer/results/reports/review_round2_full.md` §4.2.
**Agent:** genomics-analyst. **Date:** 2026-10-22. **Report:** `results/reports/cd276_panel4a_report.md` (Revision 2).
**Scope discipline:** no new database query, no package installation, no change to SOURCE. All numbers below are recomputed from the inputs in §5.

| # | Review item | Status | What was done | Evidence |
|---|---|---|---|---|
| 1 | G7 note contradicts the reconciliation table (69/65 vs 201/195); literal hardcoded in script 01 | **DONE** | Recomputed both from underlying credible-set data. **Both numbers are correct but answer different definitions.** *Full TSS ±500 kb retrieval universe:* locus interval overlaps gene body = **201 all types / 195 GWAS**. *Round-1 303-row artifact only (lead variants 73.5–73.9 Mb):* same overlap = **69 all types / 65 GWAS**. The 69/65 set is a subset of 201/195. The G7 note is now generated from the data and names both universes; the hardcoded literal is gone. The reconciliation table gained an explicit row for the round-1 universe (8 rows total), each with `definition` and `source_file`. | `results/tables/cd276_round2_germline_verification.csv` (G7); `results/tables/cd276_round2_credible_set_window_reconciliation.csv` (rows 5–6); `code/scripts/01_verify_germline_cd276.py`; `data/processed/cd276_round2_germline_verification_log.txt` |
| 2 | Within-window score median/range and median distance stored nowhere | **DONE** | Reparsed the raw ENCODE-rE2G BED and wrote all **77** per-element score and distance values with the exact filter. Summary: score median **0.0143083** (min 0.0011955, max 0.9734559); distance median **241,123 bp = 241.1 kb** (min 64.5, max 496,317.5 bp). These match the report's rounded values; the report now cites these tables. | `results/tables/cd276_e2g_within_window_score_distance_distribution.csv` (77 rows); `results/tables/cd276_e2g_within_window_score_distance_summary.csv` |
| 3 | Trait-label counts 13/41 and 17/67 not tabulated | **DONE** | Emitted per-label counts with numerator and denominator definitions. Gene-body GWAS credible sets: **13/41** labelled (ALT 4, GGT 5, AST 1, AST/ALT ratio 1, SHBG 1, GGT synonym 1; 28 unlabelled). L2G loci: **17/67** labelled (50 unlabelled). Both reproduce the prose exactly. The map uses `trait_resolved` from the round-1 L2G table keyed by `studyId`; all 41 studyIds are present in that table. | `results/tables/cd276_gwas_trait_label_audit.csv`; `code/scripts/05_trait_label_audit_cd276.py`; `data/processed/cd276_trait_label_audit_log.txt` |
| 4 | Delivered E2G elements table is a 29-row score-filtered subset, so the 77-element distribution cannot be re-derived | **DONE (with a factual note)** | The reviewed working copy's union table actually contains **7,332 rows**, not 29; the 29 rows are the **CD276-linked Score ≥ 0.02** subset. Regardless, the ambiguity is removed: the full union table is delivered, and explicit **839-row** and **77-row** tables are now written, each with a `filter` column, plus the 77-row distribution table. | `results/tables/cd276_e2g_regulatory_elements.csv` (7,332 rows); `results/tables/cd276_e2g_cd276_linked_all_839.csv`; `results/tables/cd276_e2g_within_500kb_77_elements.csv`; `data/processed/cd276_e2g_parse_log.txt` |
| 5 | Provenance: scripts must resolve against LIVE; remove hardcoded `ef6e8b35`/R0 constants; disclose any raw input left in SOURCE | **DONE** | Scripts 01–04 no longer hardcode the old BASE (`20261021-080518-…`) or external round-1 paths. Each resolves its workspace as `Path(__file__).resolve().parents[2]`. Round-1 and round-2 inputs were copied byte-for-byte into `data/raw/` (md5 recorded). The only external read-only input left in place is the 321 MB raw ENCODE-rE2G BED; its absolute path, md5 (`3b4198cdb65f7011e5535f1a94574496`) and size (321,602,896 bytes) are stated in report §7.2 and in `cd276_e2g_summary.csv`. A new script 05 follows the same convention. | `code/scripts/01_verify_germline_cd276.py` … `05_trait_label_audit_cd276.py`; report §7.2; `results/tables/cd276_e2g_summary.csv` (`source_file_full_path`, `source_file_md5`) |

## Verification

`code/scripts/04_validate_panel4a_outputs.py` asserts every corrected value, including:
- reconciliation rows = 8, with 69/65 (round-1 universe) and 201/195 (full universe);
- G7 note contains both definitions and cites the reconciliation table;
- distribution table = 77 rows, score median 0.0143, distance median 241 kb;
- trait audit: 13/41 and 17/67;
- every delivered E2G row carries a `filter`;
- the 7,332 / 839 / 77 row counts and all original headline counts (303 / 123 / 116 / 599 / 1,252 / 65 / 41 / 67 / 0-of-8 / 0-of-67).

## Open items

None from the five review items. The interpretive limitations already stated in report §1.3 and §2.3 are unchanged: the genetics database holds curated credible sets, not genome-wide summary statistics; the E2G stream is a single lung DNase-only prediction and carries no disease association.
