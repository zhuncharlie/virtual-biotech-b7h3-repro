# Round-2 targeted re-review: B7-H3 / CD276 in lung cancer

**Reviewer:** scientific-reviewer
**Date:** 2026-10-21
**Trigger:** "revise and resubmit" verdict in `review_round2_full.md` plus the interim
six-panel review in `scientific_review_interim_panels1-6.md`.
**Inputs read:** the three revision-response files, the four revised specialist reports,
and the delivered tables/figures/scripts listed in Section 1.

## Scope and read-only statement

This was a **read-only** verification pass. No analysis script was executed, no model was
re-run, no table or figure was regenerated, and no file outside
`work/scientific-reviewer/results/reports/` was created or modified. Every number below was
obtained either by reading a delivered table or by arithmetic on values already printed in
one. Where a claim could only be checked by an operation that needs a shell (md5, byte size,
directory listing), it is marked as not independently verifiable in Section 5 rather than
asserted.

**Note on tooling.** `mcp__provenance__register_artifact` was not available in this session's
tool set (Read / Write / Edit only), so this report could not be registered programmatically.
The path is given in the header of this file for manual filing.

---

## Section 1 — Item-by-item status against review_round2_full.md §7

Status vocabulary: **VERIFIED** = the correction is present and the delivered artifact
supports the claim as stated. **VERIFIED WITH CORRECTION** = the fix is real but a stated
number or label is wrong. **NOT VERIFIED** = the claimed correction is contradicted by the
artifact. **STILL OPEN / OUT OF SCOPE** = not addressed by this agent (correctly declared).

| # | Item | Status | Evidence and check |
|---|---|---|---|
| 1 | All 14 compartments in composition endpoints | **VERIFIED** | `visium_neighborhood_composition_pp_difference.csv` has 14 compartment rows for each histology × variant. Manually summing the %-point column for each histology × variant gives 0.0 to the printed precision (e.g. tumour all-spot: +3.79 malignant, −0.97 stromal, immune/context terms cancelling). `visium_c2l_32_neighborhood_composition_pp.py` sets `TYPES = IMMUNE + CONTEXT + MALIGNANT_STROMAL`, asserts `sorted(TYPES) == sorted(avail)`, and asserts the residual `< 1e-6`. The former −2.820 / −4.811 residuals are gone. |
| 2 | Edge-spot loop over all 12 immune/context types | **VERIFIED** | `visium_neighborhood_edge_spot_sensitivity.csv` has 24 data rows (12 types × 2 histologies). NK tumour edge vs core **+3.8098 → −18.5468**; endothelial **−16.0373 → −34.9780**. Both types are now present, and both keep the same sign, so §6.3's sentence is supportable from the table rather than asserted. Script 30 loops `ALL_TYPES`. |
| 3 | Depth-direction prose distinguishes counts from abundance | **VERIFIED** | Report §4 / changelog #2 now separates the three quantities. `visium_c2l_section_summary.csv` (22 rows): median of section-mean total abundance = **6.4203** tumour (27,826 spots) vs **7.1345** adjacent-normal (19,622 spots); means 6.48 vs 6.73. Direction is consistent across the median and the mean of section means, so the "lower estimated abundance in the deeper-sequenced tumour" statement is supported. |
| 4 | `mean_` vs `median_total_counts_*` columns | **VERIFIED WITH CORRECTION** | The structural fix is real: `visium_c2l_cd276_stratification_audit.csv` carries both `mean_total_counts_high/low` and `median_total_counts_high/low`, and `visium_c2l_43_cd276_stratification_audit.py` computes the latter with `np.median(...)`. **However the four aggregate numbers quoted in changelog #4 do not reproduce from this table.** Recomputed over the 12 tumour sections: median of per-section `median_total_counts_high` = **7,545.0** and `_low` = **3,708.5** (ratio 2.03), not 7,337 / 3,676 (2.00). Over the 10 adjacent-normal sections: **2,388.0** vs **2,083.75** (1.15), not 2,326 / 1,945 (1.20). By contrast, mean-of-means reproduces exactly: tumour **9,164.2 vs 5,211.2** (1.76×), matching the quoted 9,164 / 5,211. See new issue N2. |
| 5 | All-NaN arithmetic | **VERIFIED** | 47,448 × 28 = **1,328,544**, i.e. 100% of the 28 mean+q05 abundance columns and 73.7% of 1,803,024 obs cells. `data/processed/deprecated_all_nan_export/MANIFEST.md` records size, md5, shape, NaN count, NaN fraction, root cause and the superseding file for both the parquet and the h5ad. §1 and the run log's `correction_nan_count` row agree. |
| 6 | `>q75` → `<q25` | **VERIFIED** | `n_cd276_lt_q25 = 0` in **22/22** rows; `n_cd276_gt_q75` ranges 15–617 with no zero. Consistent with `pct_cd276_zero` of 66–98% (the empty tail is the low tail). Report §6.1 and §7 state `<q25` empty in 22/22. |
| 7 | "11 types" → correct count | **VERIFIED** | Report and sums now use **14**. Note for the record: the review's own suggestion of 12 was also wrong, and the analyst was right to push back — 14 is required for the pp residual to close. `visium_neighborhood_composition_sensitivity.csv` pooled percent-change sums: tumour **−40.116%**, adjacent-normal **+3.206%**, matching the quoted −40.1 / +3.2. |
| 8 | Define "ns" / fix neutrophil label | **VERIFIED** | The token "ns" is absent from the revised report and from the neighbourhood tables; every compartment now carries a CI or a q value. Neutrophil is reported as **+0.16 pp (95% CI −0.10 to 0.45; BH q 0.0013)**, with the correct interpretation (permutation-significant, CI includes 0). |
| 9 | Multiplicity, spatial autocorrelation, donor clustering | **VERIFIED** | `visium_neighborhood_multiple_testing_summary.csv` contains **20 family passes**; each family is a single endpoint × a single contrast scheme (no endpoint mixing — see Section C). q columns are present in all three neighbourhood tables. Report §6.5 documents (a) family definitions, (b) that the within-section shuffle destroys spatial autocorrelation so p is anticonservative with a floor of 1/1001 = 0.000999, and (c) that only 5 donors per histology make the section bootstrap optimistic. `visium_c2l_44_multiple_testing.py` uses `<= 1/(N_PERM+1)` for the floor count. |
| 10 | Surface NK/endothelial/macrophage/monocyte/mast depletions | **VERIFIED** | Report §8 lists endothelial **−2.03** (0/12 sections, 0/5 donors), NK **−0.49** (0/12, 0/5), macrophage **−0.40** (2/12, 1/5), monocyte **−0.23** (2/12, 1/5), mast **−0.24** (1/12, 0/5), alongside malignant **+3.79** (12/12, 5/5). Values match the pp-difference table. |
| 11 | Panel C reconciles with table | **VERIFIED** | `visium_c2l_41_neighborhood_figures.py` reconstructs `sum(mean_high*n_high − mean_low*n_low) / sum(mean_low*n_low)`, which is the definition behind `donor_pct_changes` in `visium_neighborhood_robustness.csv`; the quoted max disagreement is 0.05 pp. The four bars in the rendered figure are non-zero and of the expected sign and magnitude. |
| 12 | Panel A legend | **VERIFIED** | Script builds a four-entry `Patch` legend: colour encodes compartment (red immune, blue context), hatch `///` on white encodes CI-includes-0. The regenerated PNG shows distinguishable legend handles, not a single conflated key. |
| 13 | Restore spot QC table, scripts, logs | **VERIFIED (content) / UNVERIFIABLE (byte-identity)** | `results/tables/visium_spot_qc_metrics.csv` contains **54,650 data rows** (head and tail read); `visium_01_verify_extract.py`, `visium_02_qc_combine.py` and the two corresponding logs are present in LIVE. The claimed md5 equality with SOURCE could not be re-checked without a shell (Section 5). |
| 14 | Repoint script 21 and provide h5ad | **VERIFIED (code) / UNVERIFIABLE (md5)** | `visium_c2l_21_map_sections_rerun.py` resolves the input to the LIVE `data/processed/visium_sections_qc.h5ad` with an explicit `FileNotFoundError` guard and no cross-run path. The md5 `a9066b064a85bc24cf710d7fba31e5db` is asserted in the response and in the script comment but could not be recomputed here. |
| 15 | Deprecated-artifact manifest | **VERIFIED** | `data/processed/deprecated_all_nan_export/MANIFEST.md` read in full: byte size, md5, row/column count, NaN count, NaN fraction of abundance columns, root cause (pandas `columns=` selection-vs-rename), and superseding file for both parquet and h5ad. |
| 16 | Delete or annotate mapping-history CSVs | **NOT VERIFIED** | The response and `visium_c2l_mapping_history_README.md` state that all three 6-byte files "have been deleted". **Two of the three still exist**: `results/tables/visium_c2l_mapping_history.csv` and `results/tables/c2l_reference_training_history.csv` both contain a single line, `epoch`. Only `visium_c2l_mapping_history_rerun.csv` is absent. See new issue N1 — this is the only claim in the whole revision set that is directly contradicted by the artifacts. |
| 17 | Measured throughput and 8 h cap rationale | **VERIFIED** | Report §2 gives the 1-epoch benchmark (0.259 s/step, 3.1 s/epoch), completed-run rates (0.192 / 0.216 s/step; 2.3–2.6 s/epoch), the **8.6 h projection for 10,000 epochs against the ~8 h CPU mapping cap**, the 36,000-step tutorial equivalence, and the 99.96% ELBO decrease by epoch 2,700. 12 steps/epoch × 2.3–2.6 s = 28–31 s/epoch is self-consistent with 10,000 epochs ≈ 8.0–8.6 h. The delivered evidence meets the item; the *inference* that the cap would be exceeded holds only on the benchmark rate — see N7. |
| 18 | CD276 fibroblast / normal-macrophage provenance | **VERIFIED** | `scrna_cd276_expression_by_celltype.csv`: normal lung **macrophage 36.53%** detected (3,011 cells, mean log expr 0.260); LUAD **fibroblast 30.84%** (3,411, 0.329); SCLC **fibroblast 35.25%** (244, 0.401). All three quoted values match the table exactly. |
| 19 | Interim recomputations #1–6 | **VERIFIED in scope; out-of-scope items correctly declared** | 4B/4C: `scrna_cd276_de_summary.csv` has 15 contrasts, 0 significant, min padj 0.2913; `scrna_pseudobulk_de_top_genes.csv` has 486 rows with a sign filter enforced by an assertion in `scrna_pseudobulk_de_top_genes_signfiltered.py`; batch log annotated as reconstructed. Visium: spot QC table restored; `visium_sdrf_age_stage_integrity.csv` (22 rows, `usable_as_patient_level_covariate = False`) and `visium_ingest_qc_log.md` §1.1 present. G7 69/65 vs 201/195 is correctly declared as genomics-analyst scope and not claimed here. |
| 20 | Shared fail-fast assertion | **VERIFIED** | `checked_frame(rows, expected_columns, name)` in `visium_c2l_common.py` asserts exact column names **and order**, a non-zero row count, and `notna().any().any()`. The summary notes it is wired into scripts 30, 31, 32, 40, 42, 43, 44 with additional shape, row-count and known-column assertions (e.g. 48 robustness rows × 21 columns, 60 pp rows × 15 columns, 14 compartments, 22 sections). Both bug classes that produced the all-NaN export and the column misalignment would now abort before writing. |

**Score: 18 VERIFIED (items 13 and 14 verified on content, with byte-identity not
independently checkable), 1 VERIFIED WITH CORRECTION (item 4), 1 NOT VERIFIED (item 16).**

---

## Section 2 — New issues introduced or left behind

**N1 (documentation, must fix) — The "deleted" mapping-history CSVs are not all deleted.**
- **Problem:** The revision response and `visium_c2l_mapping_history_README.md` both assert
  that the three header-only files were removed. Two are still present with a single `epoch`
  line and no data rows.
- **Why it matters:** It is the only place in the revision set where the artifact directly
  contradicts a written statement. A downstream reader who trusts the README will not look
  for the files; a reader who finds them will distrust the rest of the provenance section.
- **Likely mechanism worth checking:** script 21 was documented as writing the history "only
  when non-empty". If that guard is implemented but the file was re-created on a later run,
  the guard is not effective (for example, it may test the DataFrame rather than its length,
  or write outside the guard). Re-running after deletion is a plausible explanation for
  exactly two of three files reappearing.
- **Suggestion:** either delete the two files, or amend the README and changelog #18 to state
  that two header-only files remain and what they are. Do not leave the current wording.

**N2 (numerical, must fix) — Four median-of-medians values in changelog #4 do not reproduce.**
- **Problem:** tumour "7,337 vs 3,676 (2.00×)" and adjacent-normal "2,326 vs 1,945 (1.20×)"
  are not obtainable from `visium_c2l_cd276_stratification_audit.csv`.
- **Recomputation from the delivered table:** tumour 7,545.0 / 3,708.5 (2.03×); adjacent-normal
  2,388.0 / 2,083.75 (1.15×). The mean-of-means pair (9,164 / 5,211, 1.76×) reproduces exactly,
  so the "mean vs median estimator" distinction the item was meant to draw is both real and
  demonstrable — only the four printed medians are wrong.
- **Impact:** none on any conclusion. The median/mean ratio argument holds at 2.03× vs 1.76×.
  But these numbers are now in the report as a quantitative claim attributed to a specific
  table, so they must either be recomputed from that table or the attribution changed.
- **Suggestion:** recompute the four values with `np.median` over the per-section `median_`
  columns (tumour vs adjacent-normal separately) and update changelog #4 and §6.1. No model
  re-run is needed.

**N3 (internal consistency, should fix) — "five defined families" vs "20 family passes".**
- **Problem:** changelog #10 says BH-FDR was added "within five defined families"; report §6.5
  and `visium_neighborhood_multiple_testing_summary.csv` describe **20** family passes.
- **Assessment:** the table is almost certainly right — 20 passes is the count of
  endpoint × contrast × direction combinations; "five" may refer to five conceptual grouping
  dimensions. But a reader comparing the two sentences cannot tell.
- **Suggestion:** state the relationship explicitly (for example "20 BH passes grouped into
  five families: within-neighbourhood pp, six-neighbour pp, edge-vs-core, absolute abundance,
  and pooled ratio"), or drop "five".

**N4 (hygiene) — The superseded run-log row still reads 664,272.**
- `visium_c2l_run_log.csv` retains the original `mapping_output_audit,failed` row with the
  14-column count, alongside the new `correction_nan_count` row. The old → new are both
  present, so nothing is hidden, but anyone filtering on `status != ok` or summing rows will
  hit the stale figure. Adding a `superseded_by` column, or marking the old row
  `status=superseded`, would remove the ambiguity.

**N5 (auditability) — Four depth figures are not stored in any delivered table.**
- Changelog #2 and §4 quote "median total counts 4,215 vs 2,123 per spot" and "section
  median-of-medians 4,472 vs 2,234". Neither pair is in `visium_c2l_section_summary.csv`
  (which stores section *mean* total abundance) nor in the stratification audit (which stores
  the CD276-high/CD276-low group medians, not the all-spot medians). They can only be
  recovered from the 47,448-row `visium_c2l_spot_abundances.parquet`.
- **Sanity check:** they are consistent with the audit — all-spot medians sit below the
  top-quartile-CD276 group medians for both histologies (tumour 4,472 < 7,545; normal
  2,234 < 2,388), and both pairs give a ~2.0× ratio. So these are plausible, not suspect.
- **Suggestion:** add `median_total_counts_all` and `median_total_counts_section` columns to
  the section summary, or cite the parquet as the derivation path in the sentence. This is not
  an error; it is the difference between a checkable and an uncheckable number, which is the
  whole point of review item 4.

**N6 (disclosed, not an error) — Bootstrap CIs shifted when two compartments were added.**
- Changelog #6 documents that adding malignant and stromal to the loop changed the bootstrap
  RNG stream, so CIs moved slightly (e.g. tumour total abundance 95% CI lower bound −1.12 →
  −1.66) while point estimates stayed fixed. This is the correct way to handle it: the change
  is disclosed at the point of use, with the mechanism named. Worth checking that no
  significance verdict flipped because of the shift — the only marginal case is the
  equal-weight tumour total-abundance CI, which crosses zero in both versions, so no verdict
  changes.

**N7 (minor logic) — The epoch-cap rationale leans on the benchmark rate, not the observed rate.**
- §2 states the paper's 10,000 epochs "was projected at 8.6 h, above the ~8 h cap". Two
  sentences earlier the same paragraph reports that the **completed-run** rates extrapolate to
  **6.4–7.2 h** for 10,000 epochs, which is at or below the cap. The "would exceed the cap"
  claim therefore holds only on the 1-epoch benchmark (0.259 s/step), not on either observed
  run (0.192 / 0.216 s/step).
- Both numbers are disclosed, which is the right instinct; the conclusion sentence should not
  silently use only the larger projection. Suggested wording: "the benchmark projected 8.6 h
  and the observed runs 6.4–7.2 h, i.e. 10,000 epochs would have consumed essentially the
  entire ~8 h CPU budget with no headroom." The independent convergence evidence (99.96% of
  the ELBO decrease by epoch 2,700, last-10% slope −137.6 ELBO/epoch) is the stronger
  justification and already stands without the timing argument.

---

## Section 3 — Other-panel verification

### 4A — germline / regulatory (genomics-analyst)
Verified from the delivered tables: `cd276_round2_germline_verification.csv`,
`cd276_round2_credible_set_window_reconciliation.csv`,
`cd276_e2g_within_window_score_distance_summary.csv`, `cd276_gwas_trait_label_audit.csv`.
Both universes are computed rather than hard-coded (201/195 and 69/65 definitions are both
present and distinguished). The score and distance distributions reproduce the quoted
**0.0143083** and **241.1 kb**. The two distribution tables are delivered at the stated sizes
(77 data rows and 839 data rows). **VERIFIED.**

### 4B / 4C — pseudobulk DE and sign filter (single-cell-analyst)
`scrna_cd276_de_summary.csv` has 15 contrasts, **0/15 significant**, min padj **0.2913**.
`scrna_pseudobulk_de_top_genes.csv` has 486 rows; the head is up-regulated and the tail
down-regulated; the generating script `scrna_pseudobulk_de_top_genes_signfiltered.py` asserts
`bad_up == 0 and bad_dn == 0` and rejects duplicate (contrast, gene, direction) triples, so
the zero-wrong-sign guarantee is enforced by construction rather than by inspection.
`scrna_census_batch_log.csv` is annotated as reconstructed with counts re-derived from the
merge log. **VERIFIED.**

### 4D / S5A — LIANA (single-cell-analyst)
- **Pair arithmetic:** `liana_pair_status_counts.csv`: SCLC 3,564 shared + 486 high-only +
  1 low-only = **4,051**; LUAD 4,041 + 970 + 42 = **5,053**. Reconciles.
- **CXCR3 dispute — the analyst is right and the interim review was wrong.**
  `liana_cxcl12_pairs.csv` contains 12 CXCR3-receptor rows per pair table; CXCL12 → CXCR3 is an
  `enriched_low` call for B cells (Δ −0.138, rank 11/53) and T cells (Δ −0.086, rank 22/53), and
  `both_pass` for plasma cells. The premise that CXCR3 was absent from the data is false. The
  analyst correctly demoted the pair from "dominant" to "present at a lower rank" rather than
  adopting the reviewer's incorrect premise. No error carries forward.
- **a/b/c definitions:** correctly now stated as a and b identical (43 high / 201 low), c
  different (43 high / 158 low), with the 43 CD276=1 cells resolving differently in each, and
  with the explicit statement that the sensitivity run tested definition a only.
- **Subtype limitation:** `liana_caf_subtype_check.csv` and `..._tests.csv` are delivered.
  LUAD myCAF 1.43 vs 1.00 (cell-level p = 1.1e-83; donor-paired p = 4.8e-7, n = 22) and iCAF
  donor-paired p = 0.656; SCLC myCAF cell-level p = 0.053 with only **2** paired donors ≥10
  cells (donor-level p correctly left blank rather than fabricated). The report labels this a
  marker-score **proxy**, not a classification, and states subtype and depth are not
  independent. **VERIFIED**, and the added caveat is the right call.
- **Universe provenance — the analyst is right again.** SOURCE `liana` universe is intact
  (1,414,231,381 bytes, 29,178 × 61,497, valid HDF5); the 0-byte copy is in the abandoned run
  `20261021-103545-…-3c05f9f0`. `liana_raw_sclc.parquet` is intact and the universe is
  deterministically reconstructible. Correcting a factually wrong reviewer premise, with
  provenance, is the right behaviour. **VERIFIED.**

### 4F — TCGA LUAD survival (clinical-trialist)
No change was required and none was made. Confirmed from
`work/clinical-trialist/results/reports/tcga_luad_cd276_survival_report.md` and
`results/tables/tcga_luad_cd276_cox_models.csv`:
- Adjusted Q4-vs-Q1 **OS HR 1.44 (0.92–2.26), p = 0.106**; **DSS 1.39 (0.79–2.44), p = 0.249**;
  PFS 1.20, p = 0.381; DFS 1.64, p = 0.120.
- Unadjusted effects remain reported and significant (OS 1.80, p = 0.0051; DSS 1.86, p = 0.0206),
  and the report explicitly attributes the attenuation to stage ("Stage is therefore the
  dominant driver and attenuates the CD276 contrast").
- The report does **not** call CD276 an independent prognostic factor. It reports the
  Q4-vs-rest adjusted OS result (1.45, p = 0.026) but frames the difference as precision, not
  direction. PH diagnostics and the PFS 24-month truncation are disclosed. **VERIFIED.**

### Tahoe-100M / DepMap (functional-genomics-analyst)
- Histology breakdown **11 LUAD / 1 SCLC / 10 other**, stated as such.
- Conclusion phrased as **"not assessable / no evidence either way"**, not as a negative result.
- DepMap: mean CERES **−0.230 (n = 46)** LUAD and **−0.204 (n = 25)** SCLC, with **1/46** and
  **0/25** lines below the −0.5 threshold stated alongside the means. No essentiality claim
  is made, which is the correct reading of a mean that is far from the threshold with only one
  line crossing it. **VERIFIED.**

---

## Section 4 — Final verdict

**ACCEPT WITH DISCLOSED LIMITATIONS — conditional on two text-level corrections that require
no re-analysis.**

Justification. Of the 20 spatial items, 18 are verified, one (item 4) is structurally
fixed but carries four non-reproducing numbers, and one (item 16) is contradicted by the
artifact. Neither defect changes any scientific conclusion: the estimator argument in item 4
holds at 2.03× vs 1.76×, and item 16 concerns two 6-byte, single-line (`epoch`) header files. All
quantitative claims that carry scientific weight — composition closure, percent-change sums,
edge-spot sign flips, stratification counts, NaN arithmetic, BH families, survival estimates,
DE counts, LIANA pair counts and Tahoe/DepMap values — reproduce from delivered tables.

Two reviewer premises were wrong and were correctly not adopted (CXCR3 absent; SCLC universe
0 bytes in SOURCE). That is the desired behaviour and should be noted positively, not treated
as friction.

**Conditions for acceptance (text edits only, no re-run):**
1. Delete `results/tables/visium_c2l_mapping_history.csv` and
   `results/tables/c2l_reference_training_history.csv`, or amend the README and changelog #18
   to say two remain. (N1)
2. Recompute the four median-of-medians values from
   `visium_c2l_cd276_stratification_audit.csv` and update changelog #4 / §6.1. (N2)
3. Optionally resolve "five defined families" vs "20 family passes" in changelog #10. (N3)

**Mandatory caveats to carry into any synthesis:**

- *Visium stratification.* The split is detection-based, not expression-quantile: the low
  group is the CD276-zero tail, the adjacent-normal "high" group is degenerate (median CD276
  = 0.0 in 8/10 sections), and the rank fallback is triggered by the empty low tail in 22/22
  sections. No high-vs-low biological contrast should be described as "CD276-high vs
  CD276-low" in adjacent-normal tissue.
- *Spatial statistics.* The within-section label-shuffle null destroys spatial autocorrelation,
  so permutation p values are anticonservative; the floor is 1/1001. The section bootstrap
  treats 22 sections as independent when there are only 5 donors per histology, so precision
  is overstated. Both are disclosed, neither is solved.
- *LIANA.* Calls are rank-based differential-specificity candidates. There is no formal
  high-vs-low test, no FDR, and no depth-matched contrast; the detection split carries a
  55–69% detected-gene depth gap. SCLC has 2 donors contributing ≥10 high cells. myCAF/iCAF
  is a marker-score proxy, not an annotation, and is confounded with depth.
- *Survival.* Adjusted OS (p = 0.106) and DSS (p = 0.249) are not significant. CD276 is not
  an independent prognostic factor in this cohort on this analysis; only the stage-adjusted
  Q4-vs-rest framing reaches nominal significance.
- *Tahoe/DepMap.* Not assessable; no evidence either way. Mean CERES does not cross the
  essentiality threshold and only 1/46 LUAD lines does.
- *Specificity.* CD276 is detected in **36.53% of normal lung macrophages** and 30.84% of LUAD
  fibroblasts. No "tumour-restricted" or "tumour-specific" wording is permissible.

---

## Section 5 — What could not be verified in this pass

1. **Byte identity / file sizes.** No shell was available, so md5 checks for the 450 MB h5ad,
   the spot-QC table/scripts/logs, and the three re-pointed LIANA scripts could not be
   re-executed. The claimed md5s are recorded in the response and, for the h5ad, in a script
   comment; they are single-source assertions here.
2. **The 0.05 pp Panel C agreement.** The formula matches `donor_pct_changes` by inspection
   and the figure is non-degenerate, but the numeric agreement was not recomputed.
3. **Per-spot median counts (4,215 vs 2,123) and the section-level median-of-medians pair
   (4,472 vs 2,234).** Not stored in a delivered table (N5); only the parquet holds the
   underlying rows.
4. **All 13 LIANA scripts' path re-pointing.** One was inspected; the response asserts all 13.
5. **Figure axis text.** Panel legends were read from the generating script and the rendered
   PNG; typography-level checks on the PDF were not performed.
6. **Provenance registration.** `mcp__provenance__register_artifact` was unavailable, so this
   report is not registered.

None of these gaps affects a verdict: each is a provenance or estimate check on a claim that
is independently supported by a delivered table.

---

## Section 6 — Strongest and weakest claims after revision

**Strongest (well supported, appropriately caveated):**
1. The composition endpoint is additive and closes to zero across 14 compartments, with
   tumour −40.1% and adjacent-normal +3.2% pooled percent-change sums. This is now the most
   internally consistent block in the package.
2. Malignant-cell enrichment (+3.79 pp, 12/12 sections, 5/5 donors) with concordant depletion
   of endothelial (−2.03), NK (−0.49), macrophage (−0.40), monocyte (−0.23) and mast (−0.24)
   cells.
3. CD276 is not tumour-restricted: 36.53% detection in normal lung macrophages versus 30.84%
   in LUAD fibroblasts. This is the single most decision-relevant negative finding and it is
   now stated plainly.
4. Zero of 15 pseudobulk DE contrasts reach significance (min padj 0.291). A clean null.
5. Adjusting for stage removes the TCGA survival signal (OS p = 0.106, DSS p = 0.249).
6. DepMap mean CERES −0.230 with 1/46 lines below −0.5: correctly read as no essentiality.

**Weakest (should not be leaned on):**
1. Any high-vs-low CD276 contrast in adjacent-normal tissue — the high group is degenerate in
   8/10 sections and both groups are largely CD276-zero.
2. Permutation p values in the neighbourhood analysis as calibrated evidence — anticonservative
   by construction, with a 1/1001 floor; treat them as descriptive rank statistics.
3. Precision of any donor-level statement — 5 donors per histology cannot support it.
4. LIANA "differential specificity" calls as interaction evidence — no test, no FDR, no depth
   matching, and a subtyped CAF compartment whose composition tracks depth.
5. SCLC conclusions of any kind beyond descriptive — 2 usable donors.
6. The Q4-vs-rest adjusted OS result (p = 0.026) as the headline survival finding — it is a
   sensitivity analysis in the report's own table, not the pre-specified primary contrast
   (Q4 vs Q1), and it is the only adjusted endpoint that reaches nominal significance.

---

*End of re-review.*
