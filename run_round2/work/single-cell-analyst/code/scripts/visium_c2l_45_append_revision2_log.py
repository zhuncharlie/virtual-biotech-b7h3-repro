"""
Append Revision-2 correction rows to visium_c2l_run_log.csv.

The run log is append-only: earlier rows are never edited. Each row below states
the old value, the new value, and the artifact that supports the correction.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import log_run  # noqa: E402

ROWS = [
    ("correction_nan_count",
     "OLD: mapping_output_audit said 664,272/664,272 NaN. NEW: 1,328,544/"
     "1,328,544 NaN abundance values (47,448 x 28 mean+q05 = 100% of abundance "
     "columns; 73.7% of all 1,803,024 obs cells). Old figure counted only the 14 "
     "mean columns. Evidence: deprecated_all_nan_export/MANIFEST.md."),
    ("correction_depth_direction",
     "OLD report S4: 'tumour sections are denser'. NEW: tumour has higher "
     "sequencing depth (median total counts 4,215 vs 2,123 per spot) and more "
     "CD276-positive spots (23.8% vs 7.5%), but LOWER estimated cell abundance "
     "(median of section means 6.42 vs 7.13). Evidence: "
     "visium_c2l_section_summary.csv, visium_c2l_spot_abundances.parquet."),
    ("correction_quartile_tail",
     "OLD report S6: '>q75 empty in 22/22 sections'. NEW: '<q25 empty in 22/22'; "
     "n_cd276_gt_q75 is 15-617 in every section and n_cd276_lt_q25 is 0 in every "
     "section. Evidence: visium_c2l_cd276_stratification_audit.csv."),
    ("correction_depth_statistic",
     "OLD report S6: 'Median total counts 9,164 vs 5,211'. NEW: those are means "
     "of per-section means (1.76x); median of per-section medians is 7,337 vs "
     "3,676 (2.00x). Adjacent-normal: 3,249 vs 2,540 (mean-of-means) and 2,326 vs "
     "1,945 (median-of-medians). Evidence: "
     "visium_c2l_cd276_stratification_audit.csv."),
    ("correction_composition_coverage",
     "OLD report S6: '11 types'; observed pooled percent-change sums -38.1% "
     "(tumour) / +3.1% (normal). NEW: all 14 compartments emitted; sums -40.1% / "
     "+3.2%; additive pp endpoint sums to 0.0 exactly (asserted <1e-6). Evidence: "
     "visium_neighborhood_composition_sensitivity.csv, "
     "visium_neighborhood_composition_pp_difference.csv."),
    ("correction_composition_ci",
     "OLD equal-weight total-abundance CIs: tumour +12.02 (-1.12, 25.41), normal "
     "+4.78 (3.04, 6.60), tumour six-neighbour +37.84 (2.14, 94.72), normal "
     "six-neighbour +5.98 (-1.22, 13.19). NEW: +12.02 (-1.66, 25.99), +4.78 "
     "(3.05, 6.71), +37.83 (2.59, 100.05), +5.98 (-1.39, 13.11). Point estimates "
     "unchanged; CIs shifted because adding two compartments changed the "
     "bootstrap RNG stream. Evidence: composition_pp_difference.csv."),
    ("correction_ns_label",
     "OLD report S6 used undefined 'ns', including neutrophil +0.16 pp. NEW: 'ns' "
     "removed; neutrophil +0.16 pp (95% CI -0.10 to 0.45, BH q 0.0013) is "
     "significant by permutation but the CI includes 0. Evidence: "
     "visium_neighborhood_composition_pp_difference.csv."),
    ("correction_panel_c",
     "OLD Figure panel C used a section-mean estimator that did not reconcile with "
     "donor_pct_changes. NEW: panel C reconstructs the pooled per-donor ratio "
     "sum(mean_high*n_high - mean_low*n_low)/sum(mean_low*n_low) and matches "
     "donor_pct_changes (max difference 0.05 pp). Evidence: "
     "visium_c2l_41_neighborhood_figures.py, visium_neighborhood_robustness.csv."),
    ("correction_panel_a_legend",
     "OLD Panel A legend conflated cell compartment with CI significance. NEW: "
     "colour = compartment (red immune, blue context) and hatch '///' = CI "
     "includes 0, with a separate Patch legend. Evidence: "
     "visium_c2l_41_neighborhood_figures.py."),
    ("correction_multiple_testing",
     "NEW: Benjamini-Hochberg FDR added in 20 family passes across robustness, "
     "composition pp and relative-composition tables. Also corrected n_p_at_floor "
     "from 0 to 9-10 in the 12-test absolute-abundance families: the floor is "
     "1/1001 = 0.000999001, so a 0.000999 threshold was too strict. Evidence: "
     "visium_neighborhood_multiple_testing_summary.csv."),
    ("correction_top_genes_signfilter",
     "OLD scrna_pseudobulk_de_top_genes.csv had no direction filter and no "
     "surviving generating script. NEW: rebuilt with up = log2FC>0, down = "
     "log2FC<0, padj<0.05 and |log2FC|>0.5; 486 rows; 0 wrong-sign rows; script "
     "code/scripts/scrna_pseudobulk_de_top_genes_signfiltered.py committed. "
     "CD276 summary: 0/15 significant, smallest padj 0.2913 (SCLC macrophage, "
     "log2FC -0.9529). Evidence: scrna_pseudobulk_de_top_genes.csv, "
     "scrna_cd276_de_summary.csv."),
    ("correction_census_batch_log",
     "OLD scrna_census_batch_log.csv was hand-written without a marker. NEW: "
     "annotated as reconstructed; cell counts re-derived from merge-log shapes "
     "(90,384 + 206,186 + 205,736 = 502,306); file sizes and retry counts flagged "
     "hardcoded/unverifiable. Evidence: scrna_census_batch_log.csv, "
     "logs/scrna_census_batch_log_annotation.log."),
    ("correction_sdrf_metadata",
     "NEW: SDRF age varies within every patient (3-5 year span; no constant age) "
     "and stage varies within 18/22 sections' patients; 10/22 sections carry "
     "invalid AJCC M2-M5. Both fields are unusable as covariates and are retained "
     "verbatim only for traceability. Evidence: "
     "visium_sdrf_age_stage_integrity.csv, visium_sdrf_age_stage_patient_summary.csv."),
    ("correction_mapping_history",
     "DELETED: visium_c2l_mapping_history.csv, visium_c2l_mapping_history_rerun.csv "
     "and c2l_reference_training_history.csv were 6-byte header-only files. The "
     "per-epoch ELBO lives in logs/c2l_mapping_elbo_metrics_3000epoch.csv and "
     "logs/lightning/c2l_mapping_rerun/3000ep/metrics.csv; the reference trace is "
     "unavailable. Evidence: visium_c2l_mapping_history_README.md."),
    ("correction_deprecated_manifest",
     "NEW: data/processed/deprecated_all_nan_export/MANIFEST.md records byte "
     "size, shape, NaN count, md5, root cause and the superseding file for both "
     "deprecated all-NaN artifacts."),
]

for step, detail in ROWS:
    log_run(step=step, status="correction", detail=detail)

print(f"appended {len(ROWS)} correction rows")
