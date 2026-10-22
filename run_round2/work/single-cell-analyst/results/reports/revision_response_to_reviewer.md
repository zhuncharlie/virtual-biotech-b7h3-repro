# Response to the Round-2 full review — single-cell-analyst scope

**Review addressed:** `work/scientific-reviewer/results/reports/review_round2_full.md`,
Section 7, items 1-20.
**Date:** 2026-10-21.
**Scope:** only files under `work/single-cell-analyst/`. Items owned by other
agents (genomics, clinical, functional genomics) are marked NOT APPLICABLE here
and are not claimed as done.
**Main revised report:** `results/reports/visium_c2l_panels4e_s5b_report.md`
(Revision 2.1).

**Revision 2.1 (2026-10-21).** Recomputation and text only; no model re-run.
Corrects the four median-of-medians values in item 4 (7,337/3,676 -> 7,545.0/
3,708.5, 2.03x; 2,326/1,945 -> 2,388.0/2,083.75, 1.15x), adds
`visium_c2l_depth_balance_summary.csv` for the depth numbers that were not in a
delivered table, resolves "five families" to 20 BH passes, states the 6.4-8.6 h
epoch projection range, adds the 664,272/1,328,544 scope note, and actually
removes the remaining two header-only history CSVs (with guarded writers).

Status legend: **DONE** = fixed and regenerated/verified;
**PARTIAL** = the in-scope part is fixed, an out-of-scope part remains;
**NOT APPLICABLE** = outside this agent's directories or computations.

| # | Item | Status | What changed / evidence |
|---|---|---|---|
| 1 | Emit all 14 compartments in composition endpoints | **DONE** | Scripts 31 and 32 now set `TYPES = IMMUNE + CONTEXT + MALIGNANT_STROMAL` (14) and assert `sorted(TYPES) == sorted(avail)`. Both tables regenerated. The additive pp endpoint sums to **0.0** for every histology x variant (asserted < 1e-6); the old -2.820 / -4.811 residuals are gone. `visium_neighborhood_composition_pp_difference.csv`, `visium_neighborhood_composition_sensitivity.csv`. |
| 2 | Edge-spot loop all 12 types | **DONE** | Script 30 now loops `for ct in CELL_TYPES`. `visium_neighborhood_edge_spot_sensitivity.csv` has 24 rows (12 types x 2 histologies). NK +3.81 -> **-18.55**; endothelial -16.04 -> **-34.98**. Both are now present and both remain negative, so report §6.3 quotes them explicitly instead of asserting it. |
| 3 | Correct depth-direction prose | **DONE** | Report §4 now states: tumour has higher sequencing depth (pooled per-spot median total counts 4,215 vs 2,123; median of per-section medians 4,471.5 vs 2,234.25) and more CD276-positive spots (23.8% vs 7.5%), but **lower** estimated cell abundance (median of section means 6.42 vs 7.13). `visium_c2l_section_summary.csv`, `visium_c2l_depth_balance_summary.csv`. |
| 4 | Rename or recompute `median_total_counts_high/low` | **DONE** | Both done: existing columns renamed to `mean_total_counts_high/low`, and true medians added as `median_total_counts_high/low` via `np.median`. Script 43 rerun; audit table has 22 rows and 25 columns. **Revision 2.1**: the four aggregate values previously quoted in changelog #4 were the *means* of the per-section medians (7,337 / 3,676 and 2,326 / 1,945); the medians of those columns are **7,545.0 / 3,708.5 (2.03x)** and **2,388.0 / 2,083.75 (1.15x)**. `visium_c2l_cd276_stratification_audit.csv`, `visium_c2l_depth_balance_summary.csv`. |
| 5 | Fix all-NaN arithmetic | **DONE** | Run log correction row `correction_nan_count` and report §1 now state **1,328,544 / 1,328,544** (47,448 x 28 mean+q05; 100% of abundance columns; 73.7% of all obs cells), replacing 664,272/664,272. `data/processed/deprecated_all_nan_export/MANIFEST.md`. |
| 6 | `>q75` -> `<q25` | **DONE** | Report §6.1 and §7 now say **`<q25` empty in 22/22**; `n_cd276_gt_q75` is 15-617 everywhere, `n_cd276_lt_q25` is 0 everywhere. `visium_c2l_cd276_stratification_audit.csv`. |
| 7 | "11 types" -> correct count | **DONE, with a correction to the review** | The composition endpoint covers **14**, not 12: all 14 deconvolved compartments are needed for the pp residual to close. Report text and all sums now use 14 (tumour -40.1%, adjacent-normal +3.2%). `visium_neighborhood_composition_pp_difference.csv`. |
| 8 | Define "ns" or fix neutrophil label | **DONE** | "ns" removed entirely. Neutrophil is now reported as +0.16 pp (95% CI -0.10 to 0.45; BH q 0.0013): permutation-significant but CI includes 0. Every other former "ns" carries an explicit CI or q. Report §6.4. |
| 9 | Multiplicity + spatial-autocorrelation + donor-cluster caveats | **DONE** | BH-FDR added in 20 family passes (`visium_c2l_44_multiple_testing.py`; q columns in all three tables; `visium_neighborhood_multiple_testing_summary.csv`). Report §6.5 documents: (a) family definitions and q counts; (b) the within-section shuffle destroys spatial autocorrelation, so p is anticonservative and the floor is 1/1001; (c) only 5 donors, section bootstrap overstates precision. Report §7 items 8-9. |
| 10 | Surface NK/endothelial/macrophage/monocyte/mast depletions | **DONE** | Report §8 lists each with pp, section and donor counts: endothelial -2.03 (0/12, 0/5), NK -0.49 (0/12, 0/5), macrophage -0.40 (2/12, 1/5), monocyte -0.23 (2/12, 1/5), mast -0.24 (1/12, 0/5), alongside malignant +3.79 (12/12, 5/5). `visium_neighborhood_composition_pp_difference.csv`. |
| 11 | Reconcile Figure Panel C with table | **DONE** | Panel C now reconstructs the pooled per-donor ratio `sum(mean_high*n_high - mean_low*n_low) / sum(mean_low*n_low)`, matching `donor_pct_changes` in `visium_neighborhood_robustness.csv` (max difference 0.05 pp). Axis label names the estimator. `visium_c2l_41_neighborhood_figures.py`. |
| 12 | Fix Panel A legend | **DONE** | Colour now encodes compartment (red immune, blue context) and hatch `///` on white encodes CI-includes-0, with a separate four-entry `Patch` legend. `visium_c2l_41_neighborhood_figures.py`; figure regenerated and visually checked. |
| 13 | Restore spot QC table, scripts, logs | **DONE** | `results/tables/visium_spot_qc_metrics.csv`, `code/scripts/visium_01_verify_extract.py`, `code/scripts/visium_02_qc_combine.py`, `logs/visium_01_verify_extract.log`, `logs/visium_02_qc_combine.log` are present in LIVE and byte-identical to SOURCE (md5 compared for each). |
| 14 | Repoint script 21 and copy h5ad | **DONE** | Script 21 now reads `data/processed/visium_sections_qc.h5ad` with a `FileNotFoundError` guard and no cross-run path. The file is present in LIVE; md5 `a9066b064a85bc24cf710d7fba31e5db` matches SOURCE. `cp -l` was not permitted across runs, so a full `cp -p` was used. |
| 15 | Deprecated-artifact manifest | **DONE** | `data/processed/deprecated_all_nan_export/MANIFEST.md` records byte size, md5, row/column count, NaN count, NaN fraction of abundance columns, root cause and superseding file for both the parquet and the h5ad. |
| 16 | Delete or annotate mapping-history CSVs | **DONE (corrected in Revision 2.1)** | Revision 2 said all three 6-byte header-only files were deleted, but `visium_c2l_mapping_history.csv` and `c2l_reference_training_history.csv` still existed. **All three are now verified absent** (`visium_c2l_mapping_history.csv`, `visium_c2l_mapping_history_rerun.csv`, `c2l_reference_training_history.csv`). Root cause: scripts 20 and 21 (original) wrote unconditionally; only 21_rerun was guarded. All three now drop all-NaN history, write only when non-empty, and remove a stale empty file. `results/tables/visium_c2l_mapping_history_README.md` points to the real traces and states which files were removed. |
| 17 | Measured throughput + 8 h cap rationale | **DONE (corrected in Revision 2.1)** | Report §2 gives the 1-epoch benchmark (0.259 s/step, 3.1 s/epoch) and completed-run rates (0.192/0.216 s/step; 2.3-2.6 s/epoch). 10,000 epochs projects to **8.6 h** at the benchmark rate but **6.4-7.2 h** at the completed-run rates, i.e. a **6.4-8.6 h range**, essentially the whole ~8 h CPU mapping cap with no headroom. The report no longer asserts a single 8.6 h figure and notes the extrapolation uncertainty; the epoch decision rests primarily on the convergence evidence. `logs/c2l_compute_and_api_log.md`, `visium_c2l_training_convergence.csv`. |
| 18 | CD276 fibroblast / normal-macrophage provenance | **DONE** | Report §1 added: normal lung macrophages 36.53% detected (3,011 cells, mean log expression 0.260), LUAD fibroblasts 30.84% (3,411, 0.329), SCLC fibroblasts 35.25% (244, 0.401). `scrna_cd276_expression_by_celltype.csv`. |
| 19 | Interim recomputations #1-6 | **PARTIAL (in scope: DONE)** | 4B/4C: CD276 row extracted for all 15 contrasts (`scrna_cd276_de_summary.csv`, 0/15 significant, min padj 0.2913); top-gene table rebuilt with a sign filter and a committed script (486 rows, 0 wrong-sign rows); batch log annotated as reconstructed with counts re-derived from the merge log. Visium: spot QC table restored and SDRF age/stage note added (`visium_ingest_qc_log.md` §1.1; `visium_sdrf_age_stage_integrity.csv`). **G7 69/65 vs 201/195 is NOT resolved here**: it is in `genomics-analyst`'s directory, which this agent must not modify. Tahoe (interim #5) and 4D/4F are likewise outside this scope. |
| 20 | Shared fail-fast assertion | **DONE** | `checked_frame()` in `visium_c2l_common.py` asserts exact column name/order, non-zero rows, and `notna().any().any()`. It is now used for every delivered table in scripts 30, 31, 32, 40, 42, 43 and 44, with additional shape/row-count/known-column assertions (e.g. 48 robustness rows x 21 columns; 60 pp rows x 15 columns; 14 compartments; 22 sections; 22/22 SDRF rows). The all-NaN and column-alignment bug classes now abort rather than write a table. |

## New issues found while fixing (not in the review)

| Issue | Resolution |
|---|---|
| The run log's `mapping_output_audit` row used 664,272 (14 columns) while the defect affected 28 columns | Appended `correction_nan_count` with old -> new; report §1 corrected |
| `n_p_at_floor` in the multiplicity summary was 0 because the threshold was 0.000999 but the true floor is 1/1001 = 0.000999001 | Fixed in script 44 (`<= 1/(N_PERM+1)`) and rerun; the count is now 9-10 in the 12-test absolute-abundance families |
| Script 30's edge loop omitted non-immune types, so the NK/endothelial sentence could not be checked | Fixed (item 2); all 12 types now emitted |
| The adjacent-normal "high-CD276" group is degenerate: median CD276 = 0.0 in **8/10** sections | Added to report §6.1 and §7 |
| SDRF `age`/`stage` are section-index artefacts (age increments within patient; M2-M5 invalid); no constant age exists | Added to the ingest QC report §1.1 with a 22-row audit table; flagged unusable as covariates |
| Three 6-byte header-only history CSVs looked like results | All three now removed and verified absent (Revision 2.1); writers in scripts 20, 21 and 21_rerun guarded so an empty history never produces a CSV; README explains where the ELBO traces are |

## What remains open

1. **G7 69/65 vs 201/195** (reviewer item 19) — outside this agent's directory;
   needs the genomics analyst.
2. **Spatial autocorrelation in the permutation null** — disclosed, not solved.
   A spatially constrained null (e.g. toroidal rotation or block bootstrap) would
   be the correct fix but is a new analysis, not a recomputation from existing
   outputs.
3. **Donor-level inference** — 5 donors per histology; the donor values are
   reported so a formal donor-level test can be run, but none is claimed here.
4. **Adjacent-normal split is degenerate** — disclosed; no fix is possible
   without a different stratification (e.g. detection-only contrast).

---

# Response to the Section 3 review — LIANA Panels 4D / S5A

**Review addressed:** `work/scientific-reviewer/scientific_review_interim_panels1-6.md`,
Section 3 (lines 135–143), plus the associated cross-panel checks.
**Revised report:** `results/reports/liana_panels4d_s5a_report.md` (Revision 2).
**Constraint honoured:** LIANA and all models were **not** re-run; no result value was
changed. Only prose, derived audit tables and provenance were corrected.

| # | Item | Status | What changed / evidence |
|---|---|---|---|
| 1 | §4.3 wrongly lists CXCL12 → CXCR3 as a dominant low receptor | **PARTIAL (prose DONE; reviewer premise not supported)** | The sentence was replaced with the actual leading SCLC low calls: CXCL12 → ITGA5 (neutrophil, Δ −0.809), → CD4 (T cell, Δ −0.237), → ITGAV (mast cell, Δ −0.192), plus MDK → SORL1 (neutrophil, Δ −0.641). **CXCR3 is present in the data** (12 CXCR3-receptor rows per pair table): CXCL12 → CXCR3 is an enriched_low call for B cells (Δ −0.138, rank 11/53) and T cells (Δ −0.086, rank 22/53). It is now reported at its true lower rank rather than as dominant. Evidence: `liana_pair_level_comparison_sclc.csv`, `liana_cxcl12_pairs.csv`. |
| 2 | §4.3 pair arithmetic does not reconcile | **DONE** | Replaced with a reconciliation table: SCLC 3,564 shared + 486 high-only + 1 low-only = 4,051; LUAD 4,041 + 970 + 42 = 5,053. Presence is defined by non-null `lr_means_high/low`; |H| = 4,050/5,011 and |L| = 3,565/4,083. Evidence: `liana_pair_status_counts.csv`, `liana_caf_source_group_counts.csv`. |
| 3 | §5 says a/b/c "collapse to the same split" in SCLC | **DONE** | Now states: a and b are identical (43 high / 201 low); c is 43 high / 158 low; the 43 CD276 = 1 cells are high in c, low in a/b, and unassigned in c. The sensitivity run tested definition a only. Evidence: `liana_b7h3_caf_definition.csv`. |
| 4 | Fibroblast myCAF/iCAF subtype limitation missing | **DONE** | New marker-score proxy table and prose in §6, §8 item 10, §9: LUAD high group myCAF 1.43 vs 1.00 (cell p = 1.1e-83; donor paired p = 4.8e-7, n = 22) and anatomically skewed (62.8% vs 44.1% "fibroblast"). SCLC 1.72 vs 1.51, cell p = 0.053, only 2 paired donors. The report states this is a proxy, not a classification, and that subtype and depth are not independent. Evidence: `liana_caf_subtype_check.csv`, `liana_caf_subtype_check_tests.csv`. |
| 5 | SCLC universe `.h5ad` is 0 bytes/truncated | **PARTIAL (annotation corrected; reviewer premise not supported)** | The SOURCE universe is **intact**: 1,414,231,381 bytes, md5 `5492f9a728a02a5a120ff0ee9ec193e4`, 29,178 × 61,497, valid HDF5; the R0 copy is also intact. The only 0-byte copy is in abandoned run `20261021-103545-…-3c05f9f0`. No SCLC result was lost: `liana_raw_sclc.parquet` is intact (md5 `bc460cd8e9e52bdd3c37202dda59d121`) and the universe is deterministically reconstructible. Report §1 and §10 now say this. |
| 6 | Provenance: scripts point at SOURCE/R0; inputs not identified | **DONE** | 13 LIANA scripts re-pointed so `ROOT` resolves to LIVE and only large read-only inputs come from an explicit `SRC_ROOT`. Report §10 now lists SOURCE paths, byte sizes and md5s for the atlas and both universes, md5s for all four raw parquets, and the copied logs. Re-running `04b`, `04e`, `04f` produced byte-identical tables (md5 unchanged). |
| 7 | Keep the caveats prominent; do not soften | **DONE** | Detection-based (not expression-quantile) split, 55–69% detected-gene depth gap, 2-donor SCLC limitation, no formal between-group test and no FDR all remain in §1, §6, §8 and §9. The subtype limitation was **added** to the same caveat set. |

## What remains open (LIANA)

1. **No formal high-vs-low test and no depth-matched contrast.** The calls are rank-based
   differential-specificity candidates. A depth-matched or donor-level test remains a new,
   pre-specifiable analysis, not a correction.
2. **Subtype is a proxy, not an annotation.** The atlas has no myCAF/iCAF labels; the
   marker-score analysis shows the confound but cannot resolve it. A subtype-aware contrast
   needs independent annotation or a deconvolution reference.
3. **SCLC donor-level inference is not possible** with 2 donors contributing ≥10 high cells.
4. **The reviewer's two factual premises** (no CXCR3; SCLC universe 0 bytes in SOURCE) are
   contradicted by the data and are corrected here rather than adopted.
