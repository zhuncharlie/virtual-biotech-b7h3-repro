# Independent Scoped Review — Targeted Figure 4 Correction Pass (B7-H3 / CD276)

**Reviewer:** scientific-reviewer
**Review run:** `20261022-120126-this-continues-a-targeted-correc-06b840ce`
**Correction run under review:** `20261022-094819-this-is-a-targeted-correction-pa-d24cb49b` (CORR)
**Round-2 baseline:** `20261022-010102-round-2-of-the-b7-h3-cd276-case-76d40ca3`
**Date:** 2026-10-22

**VERDICT: ACCEPT WITH DISCLOSED LIMITATIONS.** The three targeted corrections are substantively correct, concordant with all four ground-truth quotes, and statistically supported by the delivered CSVs, script, and fit log. No blocking scientific error was found. Four non-blocking defects should be corrected editorially before the artifacts are cited as final: (i) three p-value transcription errors in the specialist sensitivity detail table, (ii) one caveat omission in the primary comparison document, (iii) dangling references to an ERRATA/FINAL_REPORT/claims file that do not exist in the CORR run, and (iv) minor 4B/4C labeling imprecision. No re-analysis and no second review round is required; a targeted re-check of the three p-values is sufficient.

**Path convention.** Locations below are relative to the CORR root unless stated otherwise:
`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261022-094819-this-is-a-targeted-correction-pa-d24cb49b/`

---

## 1. Findings

| # | Location | Severity | What is wrong or confirmed | Required / recommended fix |
|---|---|---|---|---|
| F1 | `report/panel_by_paper_comparison.md:100-112` vs `work/single-cell-analyst/results/tables/visium_correction_mixed_effects_4e.csv:2-10` | Observation (confirmed) | **Exact match** for all 9 cell types between the panel doc table and the primary CSV: β, 95% CI, BH q, adjusted %, unadjusted %. Examples: T cell β −0.016416→−0.0164; CI −0.023327 to −0.009505→−0.0233 to −0.0095; q 5.405e−6→5.4e−6; adj −3.222→−3.22. Macrophage β −0.025209→−0.0252; q 5.041e−6→5.0e−6; adj −12.005→−12.00. DC β −0.010644→−0.0106; CI −0.019209 to −0.002080→−0.0192 to −0.0021; q 0.016704→0.0167. n = 13,886 (6,943 high / 6,943 low), 12 sections, 5 patients in every row. | None. |
| F2 | `work/single-cell-analyst/code/scripts/visium_correction_mixed_effects_4e.py:69-72,110,137-146,175-178,195-201,205-220,414-425` | Observation (confirmed) | **The script implements the stated model exactly**: response `nb_<celltype>` (neighbour mean, self excluded, radius 2.05); predictor `grp` = per-section top vs bottom 25% with rank fallback; fixed effects `z_log_depth + z_cov_fib + z_cov_malig` (own-spot `log1p(total_counts)`, `mean_fibroblast`, `mean_malignant cell`); `MixedLM(..., groups=section, re_formula="1")`; `fit(reml=True, method="lbfgs", maxiter=300)`; Wald p; BH computed per analysis across 9 types. | None. |
| F3 | `.../visium_correction_mixed_effects_4e_fit_log.txt:44-152`; `..._sensitivity.csv:2-109` | Observation (confirmed) | **108 fits = 12 analyses × 9 types; every row `converged=True`, `status=ok`.** Primary 9 rows also converged. Fit log line 6 degree distribution (0:130, 1-5:6,002, 6:3,000, 7:6,013, 8:32,303) sums to 47,448, the loaded row count (fit log line 3). | None. |
| F4 | `visium_correction_mixed_effects_4e_report.md:151-167` vs sensitivity CSV | Observation (confirmed) | **Per-analysis summary matches the CSV exactly**: q<0.05 counts 8, 8, 9, 8, 7, 7, 8, 3, 7, 8, 1, 6 across the 12 analyses; directions as stated (primary/log1p/neighbour-covariate/nested/full-ring all 8 decrease; detection 9 decrease; spot-own and patient-RE 7 decrease; depth-only 3 decrease; adjacent-normal primary 1 increase; adjacent-normal detection mixed). | None. |
| F5 | `visium_correction_mixed_effects_4e.csv:2,5,6,7`; panel doc `:25,112,148` | Observation (confirmed) | **All four paper-named compartments are significantly depleted**: T cell q 5.40e−6, macrophage q 5.04e−6, monocyte/myeloid q 7.56e−4, dendritic cell q 0.0167; all β < 0. The ninth type (neutrophil) is null (β +2.3e−5, q 0.988). 8/9 significant, all 8 negative. | None. |
| F6 | `visium_correction_mixed_effects_4e.csv:2-10`; report `:122-125` | Observation (confirmed) | **Percent-change arithmetic is correct**: β / low-group mean. T −0.0164156/0.5094434 = −3.222%; macrophage −0.0252094/0.2099979 = −12.005%; monocyte −0.0073393/0.2385769 = −3.076%; DC −0.0106444/0.3094551 = −3.440%. Unadjusted high−low / low: T +15.368%, DC +28.767%, matching the paper-doc table. | None. |
| F7 | `visium_correction_mixed_effects_4e_report.md:176` (depth + fibroblast row, macrophage column) | **Non-blocking numeric error** | Report states **p = 2e−7**. The sensitivity CSV row 77 gives **p = 1.9799546e−06** (fit log line 120: 1.979955e−06). The reported p overstates significance by ~10×. The coefficient and CI are correct (−0.0251; −0.0353 to −0.0149), and q = 5.94e−6 remains significant, so no conclusion changes. | Correct to **p = 2.0e−6**. |
| F8 | `visium_correction_mixed_effects_4e_report.md:181` (complete-ring row, T cell and macrophage columns) | **Non-blocking numeric error** | T cell: report states **p = 2e−8**; sensitivity CSV row 83 gives **p = 2.517729e−06** (fit log line 126). Macrophage: report states **p = 2e−6**; CSV row 86 gives **p = 1.814841e−05** (fit log line 129). Both overstate significance (≈100× and ≈10×). Coefficients are correct; q = 4.53e−6 and 2.72e−5 remain significant. | Correct to **p = 2.5e−6** (T) and **p = 1.8e−5** (macrophage). |
| F9 | `report/panel_by_paper_comparison.md:114-116` vs specialist report `:145-147,246-250,255-258` and source 4E report `:673-687` | Non-blocking disclosure gap | The panel doc's "Stats caveats" states spatial autocorrelation, 12 sections / 5 donors, and adjacent-normal degeneracy, but **omits two material model limitations that the specialist reports disclose**: (a) the section random-effect variance is estimated at **0 for 7/9 types** (boundary solution; only T-cell 0.00492/ICC 0.114 and mast-cell 0.00283/ICC 0.095 non-zero), so 7/9 fits are effectively OLS with section structure absorbed by covariates; (b) the rank-fallback groups are a **positive-vs-zero contrast** (high group 52–100% CD276-positive; low group 100% zero), not a true expression-quartile contrast. | Add one sentence to the panel doc's Stats caveats covering (a) and (b). No analysis change. |
| F10 | `report/panel_by_paper_comparison.md:8` | Non-blocking for science; delivery-blocking for package | The document cites `report/ERRATA_figure4_corrections.md` and says it is the corrected source for `FINAL_REPORT.md §2`. **Neither file exists in the CORR run**, and `evidence/claims.json` (the target of the `[[claim:C105/C110/C120-C124]]` markup) is also absent. `MANIFEST.json:5` has `"completed": null`, `:7` `"status": "in_progress"`, and `:465-467` lists `report/panel_by_paper_comparison.md` under `misplaced_files`. The corrections themselves are stated inline in the panel doc, so no scientific information is lost; the cross-references are dangling. | Produce the ERRATA, FINAL_REPORT, and claims file in the planned CSO finalization step (plan s3/s5), or remove/soften the cross-references. |
| F11 | `report/panel_by_paper_comparison.md:58,23`; `scrna_panels4bc_report.md:25,150-166` | Observation | The "15 primary disease-vs-normal contrasts" label is imprecise. The DE summary table (`scrna_cd276_de_summary.csv:2-16`) contains **15 rows = 11 primary (6 LUAD + 5 SCLC) + 4 paired LUAD sensitivity contrasts**, not 15 primary. The source report's phrase "15 ... in 6 LUAD and 5 SCLC cell types (plus 4 paired ...)" is internally inconsistent (it would imply 19). The **numeric** claims are correct: all 15 are non-significant, and the minimum non-null padj is **0.29135** (SCLC macrophage, log2FC −0.9529 = −0.95). | Relabel as "11 primary + 4 paired sensitivity = 15 total". |
| F12 | `report/panel_by_paper_comparison.md:58`; `scrna_panels4bc_report.md:30-32` | Observation | The phrase "all padj > 0.29" is not literally true for all 15 rows: three primary rows have **blank padj** (LUAD B p=0.490, LUAD DC p=0.253, SCLC DC p=0.544; `scrna_cd276_de_summary.csv:3,6,14`). Their p-values are all >0.05, so "not significant in any of 15" holds. | Say "all p/padj > 0.05; minimum non-null padj 0.291" or equivalent. |
| F13 | Residual "immune-hot" locations (full judgment in §4) | Observation (confirmed) | Every occurrence is legitimate correction/explanatory context or operational metadata; **none asserts that the paper's claim is immune-hot.** | None. |
| F14 | `cd276_panel4a_constraint_crossreference.csv:2`; panel doc `:22,33,39,45`; 4A report `:280-318` | Observation (confirmed) | **4A cross-reference is exact and honestly framed**: LoF O/E 0.6666399836540222 → 0.67; obs 34; exp 51.00199890136719; 95% CI 0.5059999823570251–0.8880000114440918; p 4.2878e−08; upperRank 7792 / upperBin 4 / upperBin6 2. The documents state repeatedly that this is a gene-level population-genetic property, not a disease association, and that only the germline stream tests disease association (negative). | None. |
| F15 | `scrna_fibroblast_census_donor_counts.csv:2-8`; `scrna_fibroblast_census_check.md:9,38-61`; panel doc `:23,59-60,65` | Observation (confirmed) | **4C census decision is adequately justified and honestly framed**: matched study 576f193c has RU675 28 / RU682 5 / RU685 4 (only 1 donor ≥10; 37 Census cells, 31 after QC); normal-only 350237e0 has 104 cells / 17 donors / 4 ≥10 but no tumour arm and a different assay (10x 5′ vs 10x 3′ v2). The 15 nulls are described as a real broader negative, explicitly **not** a refutation of the fibroblast claim. Neither over- nor understated. | None. |
| F16 | Source 4E report `:584-630,673-687`; panel doc `:90-118` | Observation (confirmed) | The source §6.6 table reproduces the primary CSV exactly; the lattice caveat (2.05 radius returns up to 8 neighbours; 68.1% with 8; "six-neighbour-only" sensitivity is a partial-ring subset) and adjacent-normal degeneracy (median CD276 = 0 in the high group in 8/10 sections; significant macrophage increase) are accurate. | None. |
| F17 | Panel doc `:25,98,112`; source 4E report `:728` | Observation | The label "the paper's own adjusted mixed-effects model" is defensible for the fixed/random-effects specification, but the grouping is a **rank fallback** (positive-vs-zero), and the covariate source is **own-spot** (the paper does not specify), with a section rather than donor random effect. The deviations are disclosed nearby, but "paper-specified model with an adapted rank-fallback grouping" would be more precise. The "Agree" verdict is directional/significance agreement; the paper's effect magnitudes are not reproduced (and are unavailable). | Consider tightening the label; no numeric change. |

---

## 2. Checks performed (specific cells/lines inspected)

**Primary model table**
- `visium_correction_mixed_effects_4e.csv` rows 2–10: 9 cell types; every row n_spots=13,886, n_high=6,943, n_low=6,943, n_sections=12, n_patients=5, converged=True, status=ok.
- Row 2 T cell: β −0.01641562674512618, SE 0.003526068381751017, CI −0.0233265937803836 to −0.009504659709868756, p 3.231885580146152e−06, q 5.404973129654087e−06, pct −3.22226719103825, unadjusted pct 15.36828333879033, low mean 0.5094433754836104, high mean 0.5877360768786292, re0 0.004919533280991183, ICC 0.114225472167608.
- Row 5 macrophage: β −0.02520944303757666, q 5.04099950949518e−06, pct −12.004616891786034, low mean 0.20999789718258993.
- Row 6 monocyte/myeloid: β −0.00733932153253639, q 0.0007560247459563868, pct −3.0762912070288793.
- Row 7 dendritic cell: β −0.01064443030808727, CI −0.01920850361473695 to −0.002080357001437591, q 0.016703690326957944, pct −3.4397337821097826.
- Row 9 neutrophil: β +2.317172567427256e−05, q 0.9883802168908544, significant_q05=False.
- RE variance: 0.0 for B, NK, macrophage, monocyte, DC, neutrophil, plasma (7/9); 0.0049195 (T) and 0.0028262 (mast) non-zero.

**Sensitivity grid**
- `visium_correction_mixed_effects_4e_sensitivity.csv` lines 2–109: 108 data rows (12 analysis labels × 9 types), all converged=True, status=ok.
- Analysis labels: `primary_tumour_nb_owncov_sectionRE`, `sens_log1p_nb_tumour`, `sens_detection_group_tumour`, `sens_neighbour_covariates_tumour`, `sens_spot_own_abundance_tumour`, `sens_patient_random_effect_tumour`, `sens_nested_patient_section_tumour`, `sens_depth_only_tumour`, `sens_depth_plus_fibroblast_tumour`, `sens_full_ring_spots_tumour`, `sens_adjacent_normal_nb_owncov_sectionRE`, `sens_adjacent_normal_detection_group`.
- q<0.05 counts verified by row: primary 8; log1p 8; detection 9; neighbour covariates 8; spot-own 7; patient RE 7; nested 8; depth-only 3 (NK q=0.0119, macrophage q=0.000707, mast q=0.000344); depth+fibroblast 7; complete-ring 8; adjacent-normal primary 1 (macrophage q=0.00735, increase); adjacent-normal detection 6 (mixed).
- F7 source: CSV row 77 (depth+fibroblast macrophage) p=1.9799546e−06; fit log line 120 p=1.979955e−06.
- F8 source: CSV row 83 (complete-ring T) p=2.517729e−06; CSV row 86 (complete-ring macrophage) p=1.8148406e−05; fit log lines 126 and 129 respectively.

**Fit log**
- Line 3: loaded 47,448 spots × 39 columns; line 5: after QC 47,448.
- Line 6: neighbour counts 0:130, 1:274, 2:512, 3:914, 4:1667, 5:2635, 6:3000, 7:6013, 8:32303 (sum 47,448).
- Lines 7–29: 22 sections = 12 tumour + 10 adjacent-normal; 5 patients (P10, P15, P16, P24, P25).
- Lines 32–41: primary table exactly reproduces the CSV values.
- Lines 44–152: 108 compact rows, all converged=True, status=ok.

**Script**
- Lines 69–72: 9 immune types; paper-named set = T, macrophage, monocyte/myeloid, dendritic cell.
- Line 110: `cKDTree.query_ball_point(..., r=2.05)`, self excluded.
- Lines 137–146: strict quartiles then deterministic rank fallback.
- Lines 175–178: z-score within analysed rows.
- Lines 181–221: `y ~ grp + z_log_depth + z_cov_fib + z_cov_malig`; `smf.mixedlm(..., groups=section, re_formula="1")`; REML/lbfgs; CI = β ± 1.95996·SE; Wald z/p.
- Lines 414–425: BH per analysis across the 9 types.
- Lines 428–437: percent change = β / low-group mean; unadjusted % = (high−low)/low.

**Group construction**
- `visium_correction_mixed_effects_4e_group_construction.csv` rows 4–7, 10–11, 14–15, 18–19, 22–23: 12 tumour sections; n_high_all/n_low_all sum to 6,951 each; n_high_with_neighbour/n_low_with_neighbour sum to 6,943 each.
- Median depth high vs low: P10_T1 11,040.0 vs 3,236.5; P16_T2 6,716.0 vs 3,428.0. Median of the 12 high medians = 7,545.0; median of the 12 low medians = 3,708.5; ratio 2.0345 (panel doc 2.03×).
- pct_positive_high 52.34–100; pct_positive_low 0 in all 12 tumour sections; cd276_median_low 0 in all 22 sections.
- Adjacent-normal: median CD276 of high group = 0 in P10_B1, P10_B2, P16_B1, P16_B2, P24_B1, P24_B2, P25_B1, P25_B2 (8/10); non-zero only in P15_B1 (0.354) and P15_B2 (0.735).

**4A**
- `cd276_panel4a_constraint_crossreference.csv` row 2: lof_oe=0.6666399836540222, lof_oe_rounded_2dp=0.67, obs_lof=34, exp_lof=51.00199890136719, CI 0.5059999823570251–0.8880000114440918, p=4.2877999817392265e-08, upper_rank=7792, upper_bin=4, upper_bin6=2, paper_quoted_value=0.67, agreement AGREE.
- 4A report §8.2 reproduces the same values; §8.3 correctly bounds interpretation.

**4C**
- `scrna_cd276_de_summary.csv` rows 2–16: 15 rows = 11 primary + 4 paired; CD276 not significant in any; minimum non-null padj 0.2913460032734016 (SCLC macrophage, log2FC −0.9528604918190964).
- `scrna_fibroblast_census_donor_counts.csv` rows 2–4: 576f193c RU675 28 True, RU682 5 False, RU685 4 False; rows 5–8: 350237e0 HDBR15332 25, HDBR14815 18, HDBR14944 17, HDBR15383 14 (all True); rows 9–21: 13 further donors, all <10; assay 10x 5′ transcription profiling vs 10x 3′ v2 for 576f193c.
- 4B/4C report §6.1: 11 primary contrasts (6 LUAD + 5 SCLC) + 4 paired; §6.2 and Revision 2.2 block frame the fibroblast gap as untestable, not null.

**Source 4E report**
- §6.6 table lines 592–602 matches the primary CSV exactly; lines 604–606 state 8/9 significant and all four named compartments; lines 608–619 list sensitivities and the adjacent-normal caveat; lines 621–630 give the lattice caveat; limitations 12–14 (lines 673–691) disclose RE boundary, spatial autocorrelation, 12 sections/5 donors, and covariates as composition measures.

**Round-2 baseline comparison**
- `.../20261022-010102-.../report/panel_by_paper_comparison.md` lines 18, 74, 82, 119 contain the erroneous "immune-hot" characterization. The CORR panel doc replaces the summary row (line 25), the per-panel claim (line 90), the findings (lines 92–118), and the one-line verdict (line 148), so the correction is integrated throughout, not appended.

---

## 3. Ground-truth quote concordance

| Ground-truth quote | Corrected wording | Concordance |
|---|---|---|
| **4E caption:** "Spatial transcriptomic analyses of LUAD primary-site tissue identifies immune-excluded niches in B7-H3 expressing spots relative to B7-H3 non-expressing spots... Significant was assessed using a mixed-effects model adjusting for total UMI count, fibroblast abundance, and malignant epithelial abundance fixed effects, with random effects at the sample-level." | Panel doc `:90` reproduces the caption verbatim (including the bar-plot sentence between the two ellipses); `:25` states "Immune-excluded niches ... mixed-effects model (total UMI, fibroblast, malignant fixed effects; sample random effect)"; `:98` gives the fitted formula with section RE. | **Exact / fully concordant.** |
| **4E body:** "B7-H3-high spots exhibited significant depletion of neighboring immune cells such as T cells, macrophages, monocytes, and dendritic cells." | Panel doc `:90` quotes it verbatim; `:112` reports "all four compartments the paper names (T, macrophage, monocyte/myeloid, dendritic cell) are significantly depleted"; table `:102-110` gives the negative coefficients and q-values. | **Exact / fully concordant.** |
| **4A body:** "Constraint metrics showed a predicted loss-of-function observed-to-expected ratio of 0.67." | Panel doc `:33` quotes it verbatim; `:39` gives 0.6666 (obs 34, exp 51.002, 95% CI 0.506–0.888, p 4.29e−8) and the 0.67 rounding; `:45` correctly calls it a gene-level population-genetic property, not a disease association. | **Exact / fully concordant.** |
| **4C caption:** DE analysis "identifies significantly increased expression in fibroblasts." | Panel doc `:54` quotes it verbatim as the paper's 4C claim; `:58-60` report 0/15 non-fibroblast nulls and state the fibroblast contrast is untestable (31 cells / 3 donors / 1 ≥10); `:65` states the nulls are "not a direct test or refutation" of the fibroblast claim. | **Exact / fully concordant.** |

No corrected document introduces a new misstatement of these four quotes. In particular, the 4E discussion never says the paper claims an immune-hot niche; the 4A discussion never treats 0.67 as a GWAS/association result; the 4C discussion never treats the 15 nulls as a fibroblast test.

---

## 4. Residual "immune-hot" judgment, location by location

I read every location identified in the brief. All are legitimate correction/explanatory context or operational metadata; **none is a residual assertion that the paper's claim is immune-hot.**

| Location | Text (paraphrase) | Judgment |
|---|---|---|
| `report/panel_by_paper_comparison.md:10` | "the paper's claim is an **immune-EXCLUDED** niche (depletion ...), **not** an immune-hot niche. All previous 'immune-hot' language is corrected." | Legitimate correction statement; explicitly negates immune-hot. |
| `report/panel_by_paper_comparison.md:90` | "The round-2 delivery characterized this as an 'immune-hot' ... niche. **That was backwards**." | Legitimate historical-error acknowledgment; the surrounding text is the verbatim immune-excluded caption. |
| `report/panel_by_paper_comparison.md:148` | "the unadjusted 'immune-hot' reading was a depth artifact and a mischaracterization." | Legitimate description of the erroneous unadjusted reading; not an assertion about the paper. |
| `visium_correction_mixed_effects_4e_report.md:26` | "Round 2 characterized this as an 'immune-hot' claim... **That was backwards**." | Legitimate historical-error acknowledgment. |
| `visium_correction_mixed_effects_4e_report.md:236` | "the B7-H3-high niche ... is **immune-excluded, not immune-hot**." | Legitimate correct conclusion, explicitly negating immune-hot. |
| `visium_c2l_panels4e_s5b_report.md:14` | "The paper's Figure 4E claim is immune-EXCLUDED ... not immune-hot." | Legitimate correction statement. |
| `visium_c2l_panels4e_s5b_report.md:22` | "The old 'immune-hot' characterization in Revision 2.1 §8 was backwards and is corrected throughout." | Legitimate historical correction. |
| `visium_c2l_panels4e_s5b_report.md:740` | "**weak for any unadjusted 'immune-hot' reading**." | Legitimate: labels the unadjusted reading as weak; the adjusted/paper claim is immune-excluded. |
| `inputs/plan.json:2`; `MANIFEST.json:6`; `logs/trace.jsonl:3` | Task goal / query / verbatim brief: "correct ... from immune-hot to immune-EXCLUDED". | Operational metadata and the task instruction; not deliverable assertions. The trace line is the CSO quoting the brief. No scientific claim. |

**Conclusion:** the immune-hot reversal is complete in all reviewed deliverables.

---

## 5. Overall assessment and revision requirement

**Scientific substance.** The three targeted corrections are correct:
1. **4E:** The paper's immune-excluded claim is now stated verbatim; the round-2 error is explicitly retracted; the three analyses are kept separate (unadjusted absolute abundance disagrees and is depth-confounded; composition is mixed; the paper-specified adjusted model agrees for all four named compartments). The new model is correctly implemented (neighbour-mean response, own-spot total-UMI/fibroblast/malignant fixed effects, section random intercept, REML, BH across 9 types), and the reported coefficients, CIs, q-values, and n's match the CSV to the stated precision. The lattice, rank-fallback, adjacent-normal, spatial-autocorrelation, and small-sample caveats are accurate. The only substantive omissions are the RE-boundary and rank-fallback-consequence clauses in the panel doc (F9), both of which are disclosed in the specialist reports.
2. **4A:** The gnomAD pLoF O/E 0.6666 → 0.67 cross-reference is exact, the two round-1 sources agree, and the interpretation is appropriately bounded (gene-level constraint, not disease association; only the germline stream is negative). No overstatement.
3. **4C:** The census decision is justified by the per-donor counts; the fibroblast claim is correctly labeled untestable rather than refuted; the 15 non-fibroblast nulls are preserved as a real broader negative. No over- or understatement.

**Defects.** Three p-values in the specialist sensitivity detail table are wrong by 10–100× (F7/F8), all in the direction of overstating significance; they do not change any conclusion, but they are factual errors in a citable audit artifact and should be corrected. The panel doc omits the RE-boundary and rank-fallback-consequence caveats (F9). The panel doc's ERRATA/FINAL_REPORT/claims cross-references are dangling because those synthesis files are absent from the CORR run (F10). The "15 primary" label and the "all padj > 0.29" phrasing are imprecise (F11/F12).

**Revision round required?** **No full revision round is required** — no re-analysis, no re-fitting, and no second independent review is needed. The three p-values should be corrected by direct substitution from the CSV/fit log; the panel doc should gain one caveat sentence; and the CSO should either produce the ERRATA/FINAL_REPORT/claims in the planned finalization step or remove the references. Because F7/F8 are numeric errors, a targeted re-check of those three cells after correction is advisable. If the package is to be delivered with the specialist report as a citable artifact, F7/F8/F9/F10 should be treated as **mandatory editorial fixes**, not optional.

**No blocking scientific error was identified.** The verdict is **ACCEPT WITH DISCLOSED LIMITATIONS**, with the limitations enumerated above.
