# ERRATA — Figure 4 comparison, round 2 B7-H3 (CD276) case study

**Finalization run:** `20261022-120126-this-continues-a-targeted-correc-06b840ce`
**Correction run (source of the corrected analyses):** `20261022-094819-this-is-a-targeted-correction-pa-d24cb49b`
**Delivery run being corrected:** `20261022-010102-round-2-of-the-b7-h3-cd276-case-76d40ca3`
**Analysis run:** `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
**Date:** 2026-10-22

This note exists so the correction is traceable. It does **not** replace or overwrite the round-2 delivery: verbatim copies of the round-2 `panel_by_paper_comparison.md` (sha256 `836abbef…`) and `FINAL_REPORT.md` (sha256 `6cbd7bf4…`) are preserved in `report/archive/round2_delivery/`. The final, correct comparison is `report/panel_by_paper_comparison.md` in this run.

---

## 1. What was wrong in the round-2 delivery (`76d40ca3`)

Three errors, one of which changes the headline interpretation of a panel.

### 1.1 Panel 4E/S5B was interpreted backwards — "immune-hot" instead of "immune-excluded"

The round-2 delivery characterized the B7-H3-high spatial niche as **immune-hot** (increased neighbouring immune abundance). The paper's claim is the opposite. Verbatim Figure 4E caption:

> "Spatial transcriptomic analyses of LUAD primary-site tissue identifies immune-excluded niches in B7-H3 expressing spots relative to B7-H3 non-expressing spots. Bar plot quantifies the percent change in neighbor immune abundance between top and bottom quartile of B7-H3-expressing spots across 12 LUAD tumor samples. Significance was assessed using a mixed-effects model adjusting for total UMI count, fibroblast abundance, and malignant epithelial abundance fixed effects, with random effects at the sample-level."

and body text:

> "B7-H3-high spots exhibited significant depletion of neighboring immune cells such as T cells, macrophages, monocytes, and dendritic cells."

The round-2 error arose because the unadjusted absolute-abundance comparison was read as the answer. That comparison is confounded: tumour high-CD276 spots have a **~2.03× median-of-medians capture-depth difference** (median of per-section medians 7,545.0 vs 3,708.5), which inflates apparent neighbour abundance. Unadjusted, T cells read +15.4% and dendritic cells +28.8%; after the paper's adjustment both are significantly **depleted**. The round-2 delivery reported the confounded direction as the paper-agreement finding.

### 1.2 Panel 4A omitted the gene-constraint stream that the paper's body text reports

The paper's 4A body text states: *"Constraint metrics showed a predicted loss-of-function observed-to-expected ratio of 0.67."* Round 1 had already retrieved the matching gnomAD value (pLoF O/E = 0.6666; observed 34, expected 51.002), but round 2 never connected it to the panel comparison. Panel 4A was therefore presented as a two-stream comparison (germline credible sets; regulatory elements) when the paper makes three kinds of statement.

### 1.3 Panel 4B/4C overstated what the null contrasts could say about fibroblasts

The paper's 4C caption says the DE analysis "identifies significantly increased expression in fibroblasts." The round-2 delivery reported 15 null disease-vs-normal contrasts in **non-fibroblast** compartments in a way that implied they bore on that claim. They do not: the fibroblast compartment was never tested, because the normal-lung comparator has **31 cells across 3 donors, only 1 of which reaches the ≥10-cell per-donor threshold** (Census: 37 cells / 3 donors; per-donor 28 / 5 / 4), while PyDESeq2 requires ≥3 donors per group. The correct reading is **untestable**, not refuted. Two related wording imprecisions are also corrected: the 15 rows are **11 primary contrasts (6 LUAD + 5 SCLC) + 4 paired-donor LUAD sensitivity contrasts**, not "15 primary"; and three rows have blank padj, so the accurate statement is "all p/padj > 0.05; minimum non-null padj 0.291", not "all padj > 0.29".

---

## 2. What is correct now, and why

All three corrections reuse existing data. **No new Visium pull, no cell2location re-run, no new donor data, and no re-fitting during this finalization pass.**

### 2.1 Panel 4E/S5B — paper-specified adjusted mixed-effects model

The corrected analysis fits the model the paper describes, using the existing per-spot tables:

```
neighbour-mean immune abundance ~ CD276 group
    + z(log1p(total_counts))
    + z(mean_fibroblast)
    + z(mean_malignant cell)
    + (1 | section)
```

REML `MixedLM`, 12 tumour sections, n = 13,886 spots (6,943 high / 6,943 low), 5 donors, BH correction across 9 immune types. Two adaptations are disclosed rather than hidden: the top-vs-bottom-quartile split uses a deterministic rank fallback that in practice becomes a **positive-vs-zero** contrast, and the random effect is at the **section** rather than sample level.

**Result: 8/9 immune types are significantly depleted; all four compartments the paper names are significantly depleted.**

| Cell type | β | 95% CI | BH q | Adjusted % |
|---|---|---|---|---|
| T cell | −0.0164 | −0.0233 to −0.0095 | 5.4e-6 | −3.22 |
| Macrophage | −0.0252 | −0.0355 to −0.0149 | 5.0e-6 | −12.00 |
| Monocyte/myeloid | −0.0073 | −0.0115 to −0.0032 | 7.6e-4 | −3.08 |
| Dendritic cell | −0.0106 | −0.0192 to −0.0021 | 0.0167 | −3.44 |

The ninth type (neutrophil) is null (β +2.3e-5, q 0.988). Limitations are disclosed in the final comparison: the section random-effect variance is estimated at the boundary (0) for 7/9 types (only T cell 0.00492/ICC 0.114 and mast cell 0.00283/ICC 0.095 are non-zero), the rank-fallback grouping is positive-vs-zero (high group 52–100% positive; low group 100% zero in all 12 tumour sections), the 2.05-radius neighbourhood returns up to 8 neighbours rather than 6, and Wald p-values are anticonservative under spatial autocorrelation. The result should be read as strong directional evidence, not calibrated p-values.

### 2.2 Panel 4A — constraint stream cross-referenced, not recomputed

The round-1 gnomAD value is cross-referenced directly: **pLoF O/E = 0.6666399836540222 → 0.67**, observed 34 vs expected 51.00199890136719, 95% CI 0.5059999823570251–0.8880000114440918, p = 4.2877999817392265e-08. Both round-1 sources (CSV and JSON) agree on every field. The documents state explicitly that this is a **gene-level population-genetic property, not a disease association**: only the germline stream tests disease association, and it is negative (0/8 credible sets, 0/67 disease-matched L2G loci).

### 2.3 Panel 4B/4C — testability, not refutation

A targeted CELLxGENE Census check found **no safe additional matched normal-lung fibroblast donor**. The matched study `576f193c` offers 3 normal donors (28 / 5 / 4 cells), only one testable. The only dataset with more testable donors (`350237e0`; 104 fibroblasts / 17 donors / 4 with ≥10) is a **normal-only atlas on a different platform** (10x 5′ vs 10x 3′ v2) with no tumour arm; using it would confound disease with study and platform. Other normal-only atlases contain zero fibroblast-labelled normal lung cells. **No data were pulled.** The fibroblast claim therefore remains **untestable**, and the 15 tested non-fibroblast contrasts remain a real broader negative — explicitly not a refutation of the fibroblast claim.

---

## 3. Changes made during this correction pass (editorial only)

The independent review found no blocking scientific error but identified three transcribed p-values in the 4E specialist sensitivity table that overstated significance by 10–100×. They were corrected by direct substitution from the sensitivity CSV and fit log — **no re-fitting**:

| Location | Was | Now | Ground truth |
|---|---|---|---|
| Depth + fibroblast, macrophage | `p=2e-7` | `p=2.0e-6` | 1.9799546e-06 (CSV; fit-log line 120) |
| Complete ring, T cell | `p=2e-8` | `p=2.5e-6` | 2.517729e-06 (CSV; fit-log line 126) |
| Complete ring, macrophage | `p=2e-6` | `p=1.8e-5` | 1.8148406e-05 (CSV; fit-log line 129) |

Coefficients and confidence intervals are unchanged, all three q-values remain significant (5.94e-6, 4.53e-6, 2.72e-5), and **no conclusion changes**. A `diff` against the correction-run original shows exactly two changed lines and three changed tokens. The final comparison document additionally discloses the random-effect boundary and rank-fallback consequences, and relabels the 4B/4C nulls and the 4E model as described above.

---

## 4. Reviewer verdict

**Initial independent review:** **ACCEPT WITH DISCLOSED LIMITATIONS.** The reviewer confirmed all four primary-source quotes are reproduced verbatim, that the 4E model specification is implemented exactly as stated (neighbour-mean response, own-spot depth/fibroblast/malignant fixed effects, section random intercept, REML, BH across 9 types), that all 108 sensitivity fits converged, that the reported coefficients/CIs/q-values/n match the CSV, that the 4A cross-reference is exact and honestly bounded, and that the 4C census decision is adequately justified. No blocking scientific error was found. The only defects were the three p-value transcriptions, one caveat omission, dangling packaging references, and two wording imprecisions.

**Targeted re-confirmation:** **F7, F8, F9, F11, F12 and F17 all RESOLVED; no new defects; the corrected package's scientific content is citable as final.** The reviewer independently checked each corrected value against the sensitivity CSV and fit log, verified the three-token diff, and confirmed no re-analysis occurred.

**Immune-hot sweep:** every remaining occurrence of "immune-hot" in the corrected files is a legitimate historical/correction statement or operational metadata; none asserts that the paper's claim is immune-hot.

---

## 5. What did not change

Panels 4D/S5A (LIANA), 4F (TCGA survival), and the Tahoe-100M/DepMap context are unchanged from the round-2 delivery. The atlas counts, the germline and regulatory 4A streams, and the 15 tested non-fibroblast nulls are unchanged numerically. The correction is scoped to the interpretation and reporting of 4A, 4B/4C and 4E/S5B.

---

## 6. Where the evidence lives

| Item | Path in this run |
|---|---|
| Final comparison document | `report/panel_by_paper_comparison.md` |
| Final report | `report/FINAL_REPORT.md` |
| 4E primary results | `work/single-cell-analyst/results/tables/visium_correction_mixed_effects_4e.csv` |
| 4E sensitivity results (108 analyses) | `work/single-cell-analyst/results/tables/visium_correction_mixed_effects_4e_sensitivity.csv` |
| 4E group construction / depth audit | `work/single-cell-analyst/results/tables/visium_correction_mixed_effects_4e_group_construction.csv` |
| 4E fit log | `work/single-cell-analyst/results/reports/visium_correction_mixed_effects_4e_fit_log.txt` |
| 4E reproduction script | `work/single-cell-analyst/code/scripts/visium_correction_mixed_effects_4e.py` |
| 4E corrected specialist report | `work/single-cell-analyst/results/reports/visium_correction_mixed_effects_4e_report.md` |
| 4A constraint cross-reference | `work/genomics-analyst/results/tables/cd276_panel4a_constraint_crossreference.csv` |
| 4A interpretation report | `work/genomics-analyst/results/reports/cd276_panel4a_constraint_crossreference.md` |
| 4C census testability check | `work/single-cell-analyst/results/reports/scrna_fibroblast_census_check.md` |
| 4C per-donor counts | `work/single-cell-analyst/results/tables/scrna_fibroblast_census_donor_counts.csv` |
| 4C DE summary (11 primary + 4 paired) | `work/single-cell-analyst/results/tables/scrna_cd276_de_summary.csv` |
| 4C testability table | `work/single-cell-analyst/results/tables/scrna_de_testability_by_celltype.csv` |
| Initial review | `work/scientific-reviewer/results/reports/review_correction_pass.md` |
| Re-confirmation | `work/scientific-reviewer/results/reports/review_reconfirmation_corrections.md` |
| Archived round-2 delivery (verbatim) | `report/archive/round2_delivery/` |

Claim-evidence objects for these corrections are filed in `evidence/claims.json` as C130–C139. They are **new claims** that supersede or extend the corresponding round-2 claims; the round-2 claims are not modified.
