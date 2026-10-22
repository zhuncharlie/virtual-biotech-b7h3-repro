# Targeted Re-confirmation Review — B7-H3 / CD276 Figure 4 Correction Package

**Reviewer:** scientific-reviewer
**Review scope:** re-confirmation of six mandated editorial fixes (F7, F8, F9, F11, F12, F17) only. No re-analysis.
**Current (finalization) run:** `20261022-120126-this-continues-a-targeted-correc-06b840ce`
**Source correction run (CORR):** `20261022-094819-this-is-a-targeted-correction-pa-d24cb49b` (read-only)
**Prior review:** `work/scientific-reviewer/results/reports/review_correction_pass.md`
**Date:** 2026-10-22

**Overall verdict: RESOLVED (all six fixes). No new error introduced.**

---

## (a) Verdict by finding

| Finding | Verdict | Verification |
|---|---|---|
| **F7** — depth+fibroblast macrophage p-value | **RESOLVED** | Report line 176 now reads `p=2.0e-6`. Sensitivity CSV line 77 (`sens_depth_plus_fibroblast_tumour`, macrophage) = `1.9799546054193754e-06`; fit log line 120 = `1.979955e-06`. Correct to 2 s.f. Coefficient β −0.025059 and 95% CI −0.035387 to −0.014731 are unchanged and match the CSV. |
| **F8** — complete-ring T and macrophage p-values | **RESOLVED** | Report line 181 now reads T `p=2.5e-6`, macrophage `p=1.8e-5`. CSV line 83 (T) = `2.5177292209896303e-06`; fit log line 126 = `2.517729e-06`. CSV line 86 (macrophage) = `1.8148405751451084e-05`; fit log line 129 = `1.814841e-05`. Coefficients (−0.0194 T; −0.0254 macrophage) unchanged. |
| **F9** — disclosure of RE boundary and rank-fallback consequence | **RESOLVED** | `report/panel_by_paper_comparison.md` line 117 now states both. (i) RE variance = 0 for 7/9 types; T cell `0.00492`/ICC `0.114`, mast cell `0.00283`/ICC `0.095`. Verified against `visium_correction_mixed_effects_4e.csv`: T `re0=0.0049195`, `icc_total=0.114225`; mast `re0=0.0028262`, `icc_total=0.09544`; all seven others `re0=0.0`. (ii) Rank fallback is a positive-vs-zero contrast: high group 52–100% CD276-positive, low group 100% zero in all 12 tumour sections. Verified against `..._group_construction.csv`: tumour `pct_positive_high` min 52.341 (P10_T4), max 100; `pct_positive_low` = 0.0 in all 12 tumour rows. Accurate. |
| **F11** — 15 contrasts labelled 11 primary + 4 paired | **RESOLVED** | Intro line 13, summary line 24, body line 59, and one-line verdict line 147 all state 15 = 11 primary (6 LUAD + 5 SCLC) + 4 paired sensitivity. Verified against `scrna_cd276_de_summary.csv`: 15 data rows = 11 `primary_all_donors` (6 LUAD, 5 SCLC) + 4 `paired_3donors` (all LUAD). |
| **F12** — “all padj > 0.29” replaced with literal statement | **RESOLVED** | Lines 24 and 59 now say “all p/padj > 0.05; minimum non-null padj 0.291”. Three rows have blank padj: LUAD B `p=0.49007`, LUAD dendritic `p=0.25308`, SCLC dendritic `p=0.54430`; all exceed 0.05. Minimum non-null padj = `0.2913460032734016` (SCLC macrophage). Literal statement is correct. |
| **F17** — model label and explicit adaptations | **RESOLVED** | Line 99 now labels the analysis “**The paper-specified adjusted mixed-effects model (adapted)**” and explicitly states the two adaptations: (i) per-section top-vs-bottom-quartile split with deterministic rank fallback, in practice a positive-vs-zero contrast; (ii) random effect at the **section** rather than sample level. Summary line 26 and verdict line 149 use the same “adapted” qualifier. Consistent with the script: `smf.mixedlm(..., re_formula="1", groups=d[groups_col])` with primary `groups_col=section` (line 199), and the rank fallback at lines 130–146. |

---

## (b) Verbatim diff — specialist 4E report (CORR vs current)

**Method note.** This reviewer sandbox exposes only file-read/write tools (no shell), so `diff(1)` and `sha256sum` could not be executed. The comparison was performed by reading both files in full. Both are 279 lines. Every line is identical except lines 176 and 181; the changed lines are reproduced verbatim below, with old/new tokens exactly as they appear.

```
--- 20261022-094819.../work/single-cell-analyst/results/reports/visium_correction_mixed_effects_4e_report.md
+++ 20261022-120126.../work/single-cell-analyst/results/reports/visium_correction_mixed_effects_4e_report.md
@@ -176,1 +176,1 @@
-| Depth + fibroblast | -0.0139 (-0.0224,-0.0054) p=0.0014 | -0.0251 (-0.0353,-0.0149) p=2e-7 | -0.0070 (-0.0112,-0.0028) p=0.0012 | -0.0083 (-0.0180,0.0014) p=0.092 |
+| Depth + fibroblast | -0.0139 (-0.0224,-0.0054) p=0.0014 | -0.0251 (-0.0353,-0.0149) p=2.0e-6 | -0.0070 (-0.0112,-0.0028) p=0.0012 | -0.0083 (-0.0180,0.0014) p=0.092 |
@@ -181,1 +181,1 @@
-| Complete ring | -0.0194 p=2e-8 | -0.0254 p=2e-6 | -0.0072 p=0.0029 | -0.0150 p=0.0034 |
+| Complete ring | -0.0194 p=2.5e-6 | -0.0254 p=1.8e-5 | -0.0072 p=0.0029 | -0.0150 p=0.0034 |
```

The only changed tokens are the three p-values (`2e-7`→`2.0e-6`; `2e-8`→`2.5e-6`; `2e-6`→`1.8e-5`). No coefficient, CI, q-value, sentence, table row, or heading changed.

---

## (c) New defects introduced by the edits

**None.** Specific checks:

- **Summary table, per-panel prose, one-line verdicts intact.** The six-row summary table, all per-panel sections, and all six one-line verdicts are present and mutually consistent. The 4B/4C and 4E edits were propagated to the summary table (lines 24, 26), the body (lines 59, 66, 99, 117), and the verdicts (lines 147, 149), with no orphaned old wording.
- **Claim anchors in range.** Every `[[claim:Cxxx]]` anchor used is in C130–C137: C130 (lines 23, 40), C131 (26, 99), C132 (26, 95, 97), C133 (117), C134 (24, 59, 60, 66), C135 (61), C137 (115). No out-of-set anchor remains (the CORR anchors C105/C110/C120–C124 are all replaced). C136 is unused, which is permitted. `evidence/claims.json` does not yet exist, so anchor-to-claim semantics cannot be checked here; that is the CSO’s pending filing step, not an error in the document.
- **No new “immune-hot” assertion.** Remaining occurrences are legitimate correction/historical context: line 11 (“not an immune-hot niche. All previous … corrected”), line 91 (round-2 error acknowledged, “That was backwards”), line 149 (“the unadjusted ‘immune-hot’ reading was a depth artifact and a mischaracterization”). The 4E specialist report’s occurrences (lines 26, 236) are likewise legitimate.
- **F9 wording.** “so those fits behave as OLS with section structure absorbed by the fixed covariates” is a slightly loose shorthand (the model is pooled OLS with spot-level covariates; section fixed effects were not fitted), but it faithfully mirrors the specialist report’s own caveat and does not misstate the analysis. Non-blocking.

**Residual, out-of-scope items (not new, not among the six fixes):**
- F10 is still open: `report/ERRATA_figure4_corrections.md`, `report/FINAL_REPORT.md`, and `evidence/claims.json` do not exist in this run, so the cross-reference at panel-doc line 9 is still dangling. This is the CSO’s planned finalization step (the run is `status: in_progress` in `MANIFEST.json`), and it does not affect the scientific content of the corrected analyses.
- File hashes could not be computed (no shell). Independent evidence that nothing was re-run/re-fitted:
  - Current-run fit log line 1 is `RUN START 2026-10-22 10:11:30` and line 2 names the **CORR** script path, whereas the current run was created `2026-10-22T12:01:26` (`MANIFEST.json` line 4). The log therefore predates this run and is a copied CORR artifact, not a new execution.
  - Current and CORR `visium_correction_mixed_effects_4e.csv` (all 9 rows x 35 fields) and `..._group_construction.csv` (22 sections) are identical at full printed precision; the three affected sensitivity rows (77, 83, 86) are identical.
  - The current script’s fitting block matches CORR (`re_formula="1"`, `groups=d[groups_col]`, rank fallback unchanged).
  - `MANIFEST.json` query explicitly says “do not redo any analysis”.

---

## (d) Final one-line verdict

**The corrected package’s scientific content can be cited as final: all six mandated fixes (F7, F8, F9, F11, F12, F17) are correctly applied with accurate replacement values, the 4E report diff is limited to the three intended p-value tokens, and no new scientific or internal-consistency error was introduced; only the pre-existing, planned CSO packaging files (ERRATA, FINAL_REPORT, claims.json) remain outstanding.**
