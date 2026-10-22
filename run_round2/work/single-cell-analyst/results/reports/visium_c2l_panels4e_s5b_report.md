# Panels 4E and S5B: cell2location deconvolution and spatial neighbourhood of B7-H3 (CD276) in LUAD

**Revision 2.1** (2026-10-21). Supersedes Revision 2 and Revision 1 of the same path.
Run: `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
Agent: single-cell-analyst

All paths below are relative to `work/single-cell-analyst/`.

**What changed in Revision 2.** Every quantitative sentence below was checked
against a delivered table. The corrected statements and their old -> new values
are listed in the Revision 2 changelog immediately after this header. The
underlying model fits were not re-run except for the forced mapping re-run
described in Section 1; no DE, LIANA, TCGA or reference-model computation was
re-executed.

**What changed in Revision 2.1.** Text and recomputation only; no model was
re-run. The targeted re-review (`review_round2_rereview.md`) found four
median-of-medians values that did not reproduce, a "five families" label that
conflicted with the 20 delivered BH passes, four depth numbers that were not in
any delivered table, an over-confident single timing projection, a stale
run-log row needing an explanatory note, and two header-only history CSVs that
still existed despite being reported deleted. Each old -> new value is in the
Revision 2.1 block at the end of the changelog.

## Changelog (Revision 2 and Revision 2.1)

| # | Location | Revision 1 statement | Revision 2 statement | Evidence |
|---|---|---|---|---|
| 1 | §1 | Abundance files had "664,272 / 664,272 NaN" | **1,328,544 / 1,328,544** NaN abundance values (47,448 x 28 mean+q05; 100% of abundance columns, 73.7% of all obs cells) | `data/processed/deprecated_all_nan_export/MANIFEST.md`; `visium_c2l_run_log.csv` correction rows |
| 2 | §4 | "Tumour sections are denser ... than adjacent-normal" | Tumour has **higher sequencing depth** (pooled per-spot median total counts 4,215 vs 2,123) and more CD276-positive spots (23.8% vs 7.5%), but **slightly lower estimated cell abundance** (median of section means 6.42 vs 7.13) | `visium_c2l_section_summary.csv`; `visium_c2l_depth_balance_summary.csv` (rows `all_spot_pooled_median` and `all_spot_section_median_of_medians`) |
| 3 | §6.1 | "`>q75` empty in 22/22 sections" | **`<q25` empty in 22/22**; `n_cd276_gt_q75` is 15-617 in every section. The rank fallback is triggered by the empty low tail, not the high tail | `visium_c2l_cd276_stratification_audit.csv` |
| 4 | §6.1 | "Median total counts are 1.76x higher ... (9,164 vs 5,211)" | Those are **means of per-section means** (9,164.2 vs 5,211.2; 1.76x). **Median of per-section medians** (one value per section, unweighted): **7,545.0 vs 3,708.5 (2.03x)**. Adjacent-normal: mean-of-means 3,248.9 vs 2,539.9 (1.28x); median-of-medians **2,388.0 vs 2,083.75 (1.15x)** | `visium_c2l_depth_balance_summary.csv`; `visium_c2l_cd276_stratification_audit.csv` (`mean_` and `median_total_counts_*`) |
| 5 | §6.4 | Composition sums "across the 11 types": tumour -38.1%, adjacent-normal +3.1% | Composition covers **14 compartments**. Pooled percent-change sums: tumour **-40.1%**, adjacent-normal **+3.2%**. The additive pp endpoint sums to **0.0 exactly** (asserted < 1e-6) | `visium_neighborhood_composition_sensitivity.csv`; `visium_neighborhood_composition_pp_difference.csv` |
| 6 | §6.4 | Equal-weight tumour total abundance +12.02% (-1.12, 25.41); adjacent-normal +4.78% (3.04, 6.60); six-neighbour tumour +37.84% (2.14, 94.72); adjacent-normal +5.98% (-1.22, 13.19) | **+12.02% (-1.66, 25.99); +4.78% (3.05, 6.71); +37.83% (2.59, 100.05); +5.98% (-1.39, 13.11)**. Point estimates unchanged; CIs shifted slightly because adding two compartments to the loop changed the bootstrap RNG stream | `visium_neighborhood_composition_pp_difference.csv` |
| 7 | §6.2, §6.4 | "ns" used without definition; neutrophil +0.16 pp labelled "ns" despite p at the permutation floor | "ns" removed. Neutrophil +0.16 pp (95% CI **-0.10 to 0.45**; BH q 0.0013): significant by permutation but the **CI includes 0**, so not an enrichment. Every "ns" is now an explicit CI or q value | `visium_neighborhood_composition_pp_difference.csv` |
| 8 | §6.4 | 12 immune/context compartments only | **All 14** reported: malignant **+3.79 pp** (2.27, 5.35; 12/12 sections, 5/5 donors) and stromal/other **-0.97 pp** (-1.46, -0.51) added to the tumour all-spot table; the same two are added to the six-neighbour table (+6.31 and -1.50 pp) | `visium_neighborhood_composition_pp_difference.csv` |
| 9 | §6.4 | Six-neighbour macrophage "permutation p 0.105" | **p = 0.091 raw, BH q = 0.116** (not significant at 0.05 after correction) | `visium_neighborhood_composition_pp_difference.csv` |
| 10 | §6 | No multiplicity correction | **Benjamini-Hochberg FDR** added in **20 explicitly defined family passes** (4 absolute-abundance of 12 tests, 4 additive-composition-pp of 14, 4 relative-composition of 14, 8 single-test total-abundance); q columns added to all three neighbourhood tables | `visium_neighborhood_multiple_testing_summary.csv` |
| 11 | §6, §7 | Permutation p reported without caveat | **Spatial-autocorrelation caveat** added: the within-section label shuffle destroys spatial structure, so the null is too narrow and p is anticonservative; floor 1/1001 = 0.000999 | §6.5, §7 |
| 12 | §6, §7 | Donor consistency reported as "x/5 donors" without caveat | **Donor-cluster caveat** added: only 5 donors per histology, sections within a donor are not independent, and the section bootstrap overstates precision relative to a donor-level analysis | §6.5, §7 |
| 13 | §8 | Bottom line emphasised only DC enrichment and endothelial depletion | Bottom line now also states the **donor-concordant depletions** of NK, macrophage, monocyte and mast cells, and distinguishes them from the density-driven absolute increases | §8; `visium_neighborhood_composition_pp_difference.csv` |
| 14 | Figure 4E/S5B panels | Panel C estimator did not reconcile with `donor_pct_changes`; Panel A legend conflated colour and significance | Panel C now **reconstructs the pooled per-donor ratio** from per-section sums and matches `donor_pct_changes` (max difference 0.05 pp); Panel A legend separates **colour = compartment** from **hatch = CI includes 0** | `code/scripts/visium_c2l_41_neighborhood_figures.py`; `visium_neighborhood_robustness.csv` |
| 15 | §1 | No normal-tissue CD276 expression context | Added: CD276 is detected in **normal lung macrophages at 36.53%** (3,011 cells, mean log expression 0.260), comparable to LUAD fibroblasts (30.84%, 3,411 cells, 0.329) and SCLC fibroblasts (35.25%, 244 cells, 0.401) | `scrna_cd276_expression_by_celltype.csv` |
| 16 | §2 | Epoch reduction asserted as "deliberate CPU-budget reduction" without measured throughput | Added measured **0.192-0.216 s/step, 12 steps/epoch, 2.3-2.6 s/epoch**; 10,000 epochs projects to **8.6 h** at the 1-epoch benchmark rate (0.259 s/step) but **6.4-7.2 h** at the completed-run rates, i.e. 6.4-8.6 h, essentially the whole **~8 h CPU mapping cap with no headroom**; 3,000 epochs = 1.9-2.2 h, for a further 0.04% ELBO decrease | `logs/c2l_compute_and_api_log.md`, `c2l_mapping_full.log`, `c2l_mapping_rerun.log`, `visium_c2l_training_convergence.csv` |
| 17 | §1, §7 | SDRF age/stage not flagged | Added: SDRF age and stage vary between sections of the same patient and M2-M5 are invalid; **unusable as covariates** | `visium_sdrf_age_stage_integrity.csv`; `visium_ingest_qc_log.md` §1.1 |
| 18 | §3 | Header-only `visium_c2l_mapping_history*.csv` implied a trace | **All three** 6-byte header-only files are now absent: `visium_c2l_mapping_history.csv`, `visium_c2l_mapping_history_rerun.csv`, `c2l_reference_training_history.csv`. Read the ELBO trace from `logs/c2l_mapping_elbo_metrics_3000epoch.csv` and the re-run Lightning metrics | `results/tables/visium_c2l_mapping_history_README.md` |
| 19 | §1 | Deprecated all-NaN files preserved without a manifest | Manifest with size, shape, NaN count, md5, bug cause and superseding file | `data/processed/deprecated_all_nan_export/MANIFEST.md` |

### Revision 2.1 changelog (targeted re-review corrections)

Text and recomputation only; no model was re-run.

| # | Location | Old (Revision 2) | New (Revision 2.1) | Evidence |
|---|---|---|---|---|
| R1 | changelog #4; §6.1; §7.1 | Tumour median-of-medians **7,337 vs 3,676 (2.00x)**; adjacent-normal **2,326 vs 1,945 (1.20x)** | Tumour **7,545.0 vs 3,708.5 (2.03x)**; adjacent-normal **2,388.0 vs 2,083.75 (1.15x)**. The old four values were the *mean* of the per-section medians, not the median; the mean-of-means pair (9,164.2 vs 5,211.2, 1.76x) already reproduced | `visium_c2l_depth_balance_summary.csv`; `visium_c2l_cd276_stratification_audit.csv` |
| R2 | §4; changelog #2 | Section median-of-medians **4,472 vs 2,234**, not present in any delivered table | **4,471.5 vs 2,234.25** exact (4,472 / 2,234 are rounded), stored alongside the pooled per-spot medians 4,215 / 2,123 with explicit aggregation definitions | `visium_c2l_depth_balance_summary.csv` |
| R3 | changelog #10 | "five defined families" | **20 BH family passes** (4 absolute-abundance x 12 tests; 4 additive-composition pp x 14; 4 relative-composition x 14; 8 single-test total-abundance). The global 48-test robustness column is an extra summary, not one of the 20 | `visium_neighborhood_multiple_testing_summary.csv`; §6.5 |
| R4 | §2; changelog #16 | 10,000 epochs "projected at 8.6 h, above the ~8 h cap" (benchmark rate only) | Projection range **6.4-8.6 h** depending on the rate used: **8.6 h** from the 1-epoch benchmark (0.259 s/step), **6.4-7.2 h** from the completed runs (0.192/0.216 s/step). Conclusion: 10,000 epochs would have consumed essentially the entire ~8 h CPU budget with no headroom. The epoch decision rests mainly on the convergence evidence, not on timing | `logs/c2l_compute_and_api_log.md`; `visium_c2l_training_convergence.csv` |
| R5 | §1; §3; changelog #18 | "Three header-only files were deleted" while `visium_c2l_mapping_history.csv` and `c2l_reference_training_history.csv` still existed | **All three are now absent from `results/tables/`** (verified): `visium_c2l_mapping_history.csv`, `visium_c2l_mapping_history_rerun.csv`, `c2l_reference_training_history.csv`. Root cause: scripts 20 and 21 (original) wrote the history unconditionally; only script 21_rerun had a guard. All three writers now drop all-NaN history, write only when non-empty, and remove a stale empty file | `results/tables/visium_c2l_mapping_history_README.md`; scripts 20, 21, 21_rerun |
| R6 | §1 | Run log keeps a superseded row reading 664,272 beside the correction row reading 1,328,544 | No value changed. Added note: the earlier row counted only the **14 `mean_*`** columns (47,448 x 14); the corrected count uses all **28 mean + q05** columns (47,448 x 28) | `visium_c2l_run_log.csv` |

---

## 1. Data provenance and QC

| Item | Value |
|---|---|
| Dataset | E-MTAB-13530 (De Zuani et al., *Nat Commun* 2024), 10x Visium LUAD |
| Reference | Space Ranger 1.1.0, GRCh38-2020-A, 36,601 genes |
| Sections used | 22: 12 tumour (P10 T1-T4; P15, P16, P24, P25 T1-T2) and 10 matched adjacent-normal (B1/B2 per donor) |
| QC-passed spots | 47,448 total (27,826 tumour; 19,622 adjacent-normal) |
| Spot QC (a priori) | >=500 UMIs, >=200 genes, <=20% mitochondrial reads |
| Deconvolution reference | 384,806 cells, 14 cell types, 2,000 HVGs; CD276 excluded to avoid circularity; SCLC excluded |
| Mapping inputs | 1,926 shared genes; `N_cells_per_location=8`, `detection_alpha=20`, learning rate 0.002, section as batch, `num_samples=200` |
| Deconvolved outputs | `mean_*` and `q05_*` posterior cell abundance for 14 cell types |

The spot abundance matrix is `results/tables/visium_c2l_spot_abundances.parquet`
(47,448 rows x 38 columns: 14 mean abundances, 14 q05 abundances, depth/QC and
CD276 columns). It contains **0 NaN** values; mean abundance range
1.05e-4 to 33.40. The mapping is saved under
`data/processed/c2l_mapping_model_rerun/`.

**Forced deviation from the instruction not to re-map.** The abundance files
inherited from the source run contained **1,328,544 / 1,328,544 NaN** abundance
values: 47,448 spots x 28 columns (14 `mean_*` + 14 `q05_*`). That is 100% of the
abundance columns and 1,328,544 / 1,803,024 = 73.7% of all values in the obs
frame. Revision 1 reported 664,272 / 664,272, which counted only one of the two
posterior statistics; the correction is recorded in the deprecation manifest and
in the run log.

**Note on the two run-log counts (added in Revision 2.1).** The run log
deliberately retains the original `mapping_output_audit` row (664,272) beside
the later `correction_nan_count` row (1,328,544); the old row was not rewritten,
so the progression is auditable. The difference is scope, not arithmetic: the
earlier row counted only the **14 `mean_*`** columns (47,448 x 14 = 664,272),
whereas the defect affected all **28 `mean_*` + `q05_*`** columns
(47,448 x 28 = 1,328,544). Anyone summing or filtering the log should use the
`correction_nan_count` row.

The cause was the export code
`pd.DataFrame(adata.obsm[...], columns=[f"mean_{c}" ...])`, which treats the
prefixed names as a column **selection list** rather than a rename. A 5-epoch
API probe (`code/scripts/visium_c2l_22_export_probe.py`) proved the underlying
obsm values were finite (NaN fraction 0.0) and that the corrected construction
produced 0 NaN. No model checkpoint existed, so the mapping was re-run with the
identical configuration and a corrected export
(`code/scripts/visium_c2l_21_map_sections_rerun.py`). The invalid files are
preserved under `data/processed/deprecated_all_nan_export/`, with a manifest
recording size, shape, NaN count, md5 and the superseding file. **No DE, LIANA,
TCGA or reference-model computation was re-run.** The 4B/4C DE top-gene table
and the CD276 DE summary were rebuilt read-only from the existing 922,455-row DE
result, but the DE model itself was not re-fit.

**CD276 expression context (added in Revision 2).**
`results/tables/scrna_cd276_expression_by_celltype.csv` shows that CD276 is not
tumour-restricted at the transcript level: normal lung macrophages have the
highest detection fraction in the atlas at **36.53%** (3,011 cells, mean log
expression 0.260), comparable to LUAD fibroblasts (**30.84%**, 3,411 cells,
0.329) and SCLC fibroblasts (**35.25%**, 244 cells, 0.401). Any statement that
CD276 is tumour-specific is contradicted by this panel's own table.

**Metadata-integrity warning.** SDRF `age` and `stage` vary between sections of
the same patient and contain invalid AJCC M categories (M2-M5); no patient has a
constant age. These fields are retained verbatim in `.obs` but are unusable as
covariates. Details and the section-level table are in
`results/reports/visium_ingest_qc_log.md` §1.1 and
`results/tables/visium_sdrf_age_stage_integrity.csv`.

---

## 2. Compute environment and epoch deviations

| Model | Paper | Here | Wall time |
|---|---|---|---|
| Reference regression | 250 epochs, H100 | 250/250 epochs, CPU | 4,586.9 s (18.3 s/epoch) |
| Spatial mapping | 10,000 epochs, H100 | 3,000/3,000 epochs, CPU (original and re-run) | 7,134.4 s original; 7,769.7 s train + 204.5 s export re-run |

* Environment: cell2location 0.1.5, scvi-tools 1.4.2, PyTorch 2.12.0, **CPU
  only**. CUDA use was blocked by the run policy, not by availability of a GPU
  request; no GPU run was attempted.
* **Measured throughput (added in Revision 2).** The mapping has 47,448 spots,
  batch size 4,096, and **12 steps/epoch**. A 1-epoch benchmark measured
  **0.259 s/step, 3.1 s/epoch** (`logs/c2l_compute_and_api_log.md`). The
  completed runs measured **0.192 s/step (original)** and **0.216 s/step
  (re-run)**, i.e. **2.3-2.6 s/epoch**. 3,000 epochs therefore cost
  6,926-7,770 s (1.9-2.2 h). Extrapolating linearly, the paper's 10,000 epochs
  would have cost **8.6 h** from the single-epoch benchmark rate but only
  **6.4-7.2 h** from the two completed-run rates. The honest projection is
  therefore a **range of 6.4-8.6 h**, with the benchmark rate the most
  conservative and the completed-run rates the most representative of a full
  run. This is a linear extrapolation, not a measured 10,000-epoch run; the
  throughput of a long run may drift, which is a further, unquantified source
  of uncertainty.
* **Epoch rationale.** The reduction from 10,000 to 3,000 epochs is a
  deliberate CPU-budget decision, not an accidental truncation. Against the
  **~8 h mapping cap on CPU** recorded in `logs/c2l_compute_and_api_log.md`,
  10,000 epochs projects to **6.4-8.6 h** - i.e. essentially the entire budget
  with no headroom, not a definite overrun. The timing alone therefore does not
  force the reduction; the convergence evidence below is the stronger
  justification. The chosen 3,000 epochs x 12
  steps = 36,000 optimiser steps is comparable to the standard cell2location
  tutorial budget (~30,000 full-batch steps). It is additionally justified by
  the convergence diagnostics: 99.96% of the total ELBO decrease had occurred by
  epoch 2,700 and the last-10% slope was only -137.6 ELBO units/epoch on a 38.6M
  ELBO (-0.00036%/epoch).
* **Likely effect.** Posterior abundances should be close to converged, but
  cell-type-specific calibration may differ modestly from a 10,000-epoch model.
  Absolute abundances are not directly comparable to the paper's; within-study
  high-vs-low contrasts are the appropriate readout.

---

## 3. Model diagnostics

`results/tables/visium_c2l_training_convergence.csv`,
`results/figures/figs5_c2l_training_convergence.png`

| Model | Epochs | ELBO first | ELBO last | Last-10% mean (SD) | Rel. change last 10% | Slope/epoch | % decrease by 90% epoch |
|---|---|---|---|---|---|---|---|
| Mapping, original | 3,000 | 104,060,600 | 38,571,652 | 38,595,387 (17,552) | -0.075% | -137.6 | 99.956% |
| Mapping, re-run | 3,000 | 104,199,816 | 38,557,988 | 38,567,153 (17,353) | -0.042% | -131.3 | 99.976% |
| Reference regression | 250 | - | - | - | - | - | - |

The re-run final ELBO differs from the original by **-0.04%**, confirming that
the re-map reproduced the original fit rather than changing the model.

**Reference ELBO is UNAVAILABLE, not omitted.** The 250/250 epochs completed
(Lightning `max_epochs=250 reached`; 4,586.9 s; 18.3 s/epoch), but scvi-tools
1.4 populates `model.history` only when a Lightning logger is attached, and the
reference was trained with `logger=False`. No loss values were written. No curve
is fabricated; the figure states this explicitly. The mapping trace was recovered
from the original run's CSVLogger and is stored as
`logs/c2l_mapping_elbo_metrics_3000epoch.csv`. The per-epoch trace of the re-run
is in `logs/lightning/c2l_mapping_rerun/3000ep/metrics.csv`. **No history CSV
remains in `results/tables/`**: the three header-only files
(`visium_c2l_mapping_history.csv`, `visium_c2l_mapping_history_rerun.csv`,
`c2l_reference_training_history.csv`) were removed in Revision 2.1 and verified
absent. The writers in scripts 20, 21 and 21_rerun now drop all-NaN history,
write only when non-empty, and delete a stale empty file. See
`results/tables/visium_c2l_mapping_history_README.md`.

Abundance sanity checks (`results/tables/visium_c2l_abundance_sanity.csv`):

| Metric | Value |
|---|---|
| Spots | 47,448 |
| Spearman total abundance vs total counts | **0.402** |
| Spearman immune abundance vs total counts | **0.304** |
| Spearman total abundance vs n genes | 0.387 |
| Median total abundance / spot | 5.365 |
| Median immune abundance / spot | 2.562 |
| Spots with total abundance < 1 | 0.004% |
| Spots with immune abundance < 1 | 3.064% |
| Spots with CD276 count 0 | **83.32%** |
| Median CD276 log1p(CP10K), positive spots | 0.991 |
| Max CD276 log1p(CP10K) | 3.957 |

The positive abundance-depth correlation is expected for deconvolution and is
the reason the composition sensitivity in Section 6 was added.

---

## 4. Per-section QC and abundance summary

`results/tables/visium_c2l_section_summary.csv` (22 rows; one per section).
`results/tables/visium_c2l_cd276_stratification_audit.csv` (stratification
diagnostics).

| Histology | Sections | Spots | Mean CD276 lognorm | % CD276-positive spots* | Mean of section-mean total abundance | Median of section-mean total abundance |
|---|---|---|---|---|---|---|
| Tumour | 12 | 27,826 | 0.235 | 23.8% | 6.48 | 6.42 |
| Adjacent-normal | 10 | 19,622 | 0.109 | 7.5% | 6.73 | 7.13 |

\*section mean of the per-spot positive fraction.

Tumour sections have **higher sequencing depth** (pooled per-spot median total
counts **4,215 vs 2,123**; median of per-section medians **4,471.5 vs 2,234.25**,
quoted as 4,472 / 2,234 when rounded) and **more CD276-positive spots** (23.8%
vs 7.5%), but their **estimated total cell abundance per spot is slightly
lower** (median of section means 6.42 vs 7.13). Both depth pairs and the exact
aggregation definitions are stored in
`results/tables/visium_c2l_depth_balance_summary.csv`.
The Revision 1 sentence "tumour sections are denser" conflated these two
quantities and is corrected here. Both histologies are dominated by
epithelial/malignant, fibroblast and immune compartments in the stacked
composition (Figure 4E, bottom row).

---

## 5. Panel-split assumption

* **Figure 4E = 12 tumour sections** (P10_T1-T4, P15_T1-T2, P16_T1-T2,
  P24_T1-T2, P25_T1-T2).
* **Figure S5B = 10 matched adjacent-normal sections** (B1/B2 for the same five
  donors).

This split is **not stated in the paper or in the configuration recovered from
the source run**; it is the assignment used here, inferred from the matched
design and the task specification. No result was tuned to this assignment: the
same estimators are applied separately to the two histology labels, and all
per-section/per-donor values are reported so the split can be re-derived. If the
intended 4E/S5B assignment differs, the tables need only to be re-labelled; the
underlying per-section values do not change.

---

## 6. Neighbourhood analysis: methods, results, robustness

### 6.1 Pre-specified definitions

* B7-H3 level: CD276 **log1p(CP10K)**, not raw counts.
* Stratification unit: **section** (each Visium array is independent; pooling
  spots across sections would let section-level depth/composition drive the
  split; patient-level splitting would mix histologies). high = CD276 above the
  per-section 75th percentile; low = below the 25th; the middle 50% is excluded
  from the contrast but still contributes as a neighbour.
* Neighbourhood: k=6 nearest spots on the Visium hex lattice
  (`array_row`,`array_col`), hard radius **2.05** coordinate units. The six
  physical neighbours are at 1.414 and 2.0; the next ring is >=2.828, so the
  radius returns exactly the true neighbours and never crosses sections. Spots
  with 0 neighbours (130; 37 tumour, 93 adjacent-normal) are excluded; spots
  with 1-5 neighbours (6,002; 2,783 tumour, 3,219 adjacent-normal) use the
  available neighbours.
* Neighbour abundance: unweighted mean posterior abundance of the neighbouring
  spots, self excluded.
* Effect: `(mean_neighbour_high - mean_neighbour_low) / mean_neighbour_low * 100`.
* Uncertainty: 1,000 section-cluster bootstrap resamples (95% percentile CI);
  significance: 1,000 within-section label shuffles (group sizes fixed).
* Reproducibility: seed 42; probe run with 20 permutations/bootstraps logged
  separately (`*_probe20.csv`); full run 23.8 s.

**Stratification reality check.** CD276 is zero in 76.2% of tumour spots
(range 66.3-86.9%) and 92.5% of adjacent-normal spots (83.7-98.2%). Ties at the
lower quartile made **`<q25` empty in 22/22 sections** (`n_cd276_gt_q75` is
15-617 in every section, so the high tail is populated), and the deterministic
rank fallback (top/bottom 25% by CD276 rank) was used throughout. Revision 1
stated the opposite tail; corrected. Consequently: the high group is
CD276-positive in 87.3% of tumour spots (range 52.3-100%) but only **30.0%** of
adjacent-normal spots (7.3-65.2%); the low group is 100% CD276 zero. The
adjacent-normal "high" group has a **median CD276 of 0.0 in 8 of 10 sections**
(only P15_B1/B2 have a non-zero median), so the normal split is degenerate: it
separates a small positive tail from an all-zero tail, not "high" from "low"
expression. No tumour high group has a zero median (0/12). The adjacent-normal
contrast is therefore weak and near the detection floor.

**Depth balance (estimators corrected in Revision 2.1).** Two aggregations are
reported, and the distinction is explicit so each number is reproducible:

* **Mean of per-section means** - `np.mean` over sections of the per-section
  `mean_total_counts_high` / `_low` columns. Tumour: **9,164.2 vs 5,211.2
  (1.76x)**, 12 sections. Adjacent-normal: **3,248.9 vs 2,539.9 (1.28x)**,
  10 sections.
* **Median of per-section medians** - `np.median` over sections of the
  per-section `median_total_counts_high` / `_low` columns, one value per
  section, unweighted (this is *not* a pooled spot-level median). Tumour:
  **7,545.0 vs 3,708.5 (2.03x)**. Adjacent-normal: **2,388.0 vs 2,083.75
  (1.15x)**.

Revision 2 printed 7,337 / 3,676 and 2,326 / 1,945, which are the **means** of
the same per-section median columns, mislabelled as medians; Revision 2.1
corrects them. All four aggregations, plus the all-spot pooled median and the
all-spot section median-of-medians, are stored with their exact definition,
`n_sections` and `n_spots` in
`results/tables/visium_c2l_depth_balance_summary.csv`. Per-section Spearman
CD276 vs total counts averages 0.295 in tumour and 0.150 in adjacent-normal
(section medians 0.311 and 0.161).

### 6.2 Primary result: absolute neighbour abundance (mean posterior)

`results/tables/visium_neighborhood_robustness.csv`,
`results/tables/visium_neighborhood_immune_change.csv`,
`results/figures/fig4e_neighborhood_immune_change.png/.pdf`,
`results/figures/figs5b_neighborhood_immune_change.png/.pdf`

Tumour (12 sections, 5 donors). `q_BH` is Benjamini-Hochberg within the
histology x metric family of 12 tests:

| Cell type | % change | 95% CI | perm p | q_BH | Sections + | Donors + | CI excludes 0 |
|---|---|---|---|---|---|---|---|
| T cell | **+15.37** | 1.08, 28.95 | 0.0010 | 0.0013 | 9/12 | 3/5 | yes |
| B cell | **+15.16** | 0.60, 28.26 | 0.0010 | 0.0013 | 6/12 | 2/5 | yes |
| NK cell | +3.81 | -8.25, 17.70 | 0.0010 | 0.0013 | 8/12 | 3/5 | no |
| Macrophage | -7.58 | -18.01, 11.87 | 0.0030 | 0.0036 | 7/12 | 3/5 | no |
| Monocyte/myeloid | +2.19 | -5.26, 11.20 | 0.0270 | 0.0294 | 8/12 | 3/5 | no |
| Dendritic cell | **+28.77** | 9.42, 46.90 | 0.0010 | 0.0013 | 10/12 | 4/5 | yes |
| Mast cell | +8.45 | -4.32, 20.98 | 0.0010 | 0.0013 | 8/12 | 3/5 | no |
| Neutrophil | **+17.27** | 5.30, 29.79 | 0.0010 | 0.0013 | 11/12 | 4/5 | yes |
| Plasma cell | +2.92 | -6.27, 11.08 | 0.1489 | 0.1489 | 7/12 | 3/5 | no |
| Fibroblast | **+14.65** | 5.02, 24.89 | 0.0010 | 0.0013 | 9/12 | 3/5 | yes |
| Epithelial | +14.91 | -10.46, 35.56 | 0.0010 | 0.0013 | 6/12 | 2/5 | no |
| Endothelial | **-16.04** | -25.29, -4.83 | 0.0010 | 0.0013 | 2/12 | 0/5 | yes |

Adjacent-normal (10 sections, 5 donors): all 12 types show small positive point
estimates whose bootstrap CIs exclude zero - T +3.74 (2.11, 5.10), B +3.14
(1.93, 4.12), NK +3.37 (1.71, 5.14), macrophage **+13.40** (7.16, 18.03),
monocyte +3.86 (1.53, 6.19), DC +6.43 (4.66, 7.99), mast +3.49 (1.70, 5.10),
neutrophil +3.46 (1.90, 4.92), plasma +10.08 (1.43, 17.57), fibroblast +3.78
(0.19, 6.72), epithelial +12.48 (3.19, 23.12), endothelial +2.34 (0.52, 4.02);
9-10/10 sections and 4-5/5 donors positive for most types. All 12 remain
q_BH < 0.05. The uniformity of small positive changes is itself a signature of a
density/depth gradient rather than cell-type-specific biology (Section 6.4).

The q05 (lower posterior quantile) metric gives larger magnitudes but the same
signs: tumour T +29.35 (4.74, 49.71), DC +45.33 (18.82, 66.76), neutrophil
+33.28 (15.18, 54.01), fibroblast +19.33 (8.97, 30.35), endothelial -16.96
(-27.49, -4.66); adjacent-normal macrophage +16.57 (9.04, 21.60), DC +10.05
(6.89, 14.04), plasma +16.01 (4.09, 26.39).

### 6.3 Edge-spot sensitivity

`results/tables/visium_neighborhood_edge_spot_sensitivity.csv`

Restricting to spots with exactly six neighbours (interior spots) reverses most
tumour signs: T +15.4 -> **-7.1**, B +15.2 -> **-7.5**, macrophage -7.6 ->
**-29.1**, monocyte +2.2 -> **-25.9**, DC +28.8 -> **+0.03**, mast +8.4 ->
**-14.3**, neutrophil +17.3 -> **-4.7**, plasma +2.9 -> **-28.4**, fibroblast
+14.6 -> **-29.7**; NK goes from +3.8 to **-18.5** and endothelial from -16.0 to
**-35.0**, so both remain negative and become more so. This table now covers all
12 immune/context compartments (Revision 1's loop omitted the non-immune types,
so the NK/endothelial sentence could not be checked against it). Adjacent-normal
point estimates stay positive but are less precise (T +9.7, DC +17.2, mast
+10.0); this edge-only table reports point estimates only - the corresponding
bootstrap CIs for the composition and relative endpoints are in the post-hoc
tables below.

The tumour absolute-abundance pattern therefore depends on including 1-5
neighbour (tissue-edge / QC-boundary) spots. This is a material fragility, not a
cosmetic sensitivity.

### 6.4 Post-hoc density and composition sensitivity

`results/tables/visium_neighborhood_composition_sensitivity.csv`,
`results/tables/visium_neighborhood_composition_pp_difference.csv`

Two post-hoc questions, same graph and same per-section split. Both now use all
**14** deconvolved compartments (Revision 1 used 11 in the composition loop and
12 in the reporting; the additive pp endpoint's residual check was invalid until
all 14 were emitted).

1. **Total neighbour abundance - is the high-CD276 neighbourhood simply
   denser?** Tumour: pooled +13.21% (CI -2.34, 27.30; q_BH 0.001),
   equal-section-weight +12.02% (-1.66, 25.99), 8/12 sections and 3/5 donors
   positive, median section +6.92%. Adjacent-normal: pooled +5.21% (2.94, 7.21),
   equal-weight +4.78% (3.05, 6.71), 10/10 sections and 5/5 donors positive,
   median +4.45%. Restricting to six-neighbour spots: tumour pooled point
   estimate -9.60% (CI -28.62, 17.05; q_BH 1.0) but equal-weight +37.83%
   (2.59, 100.05) and median section +5.98% (10/12 positive). The pooled and
   equal-weight estimates diverge because the pooled ratio is dominated by a
   section whose low-group denominator is near zero; the median/equal-weight
   values are the trustworthy ones. Adjacent-normal six-neighbour: pooled
   +10.19% (-5.30, 26.04), equal-weight +5.98% (-1.39, 13.11), median +2.59%.

2. **Relative composition - with density removed, which fractions actually
   shift?** The additive endpoint is the equal-section-weight mean of
   `100 * (high fraction - low fraction)` in percentage points (pp). Because all
   14 compartments are emitted, the pp values across a complete composition sum
   to **0.0 by construction**; the script asserts a residual < 1e-6 per
   histology x variant, and the observed sums are 0.0. The percent-change
   version is also reported, but it weights sections unequally and does **not**
   sum to zero: across the 14 compartments it sums to **-40.1%** in tumour and
   **+3.2%** in adjacent-normal (Revision 1: -38.1% / +3.1% across 11 types), so
   it is not used alone.

Tumour, all spots (pp, 95% CI, q_BH): DC **+0.49** (0.15, 0.84; q 0.0013; 9/12
sections, 4/5 donors); endothelial **-2.03** (-3.02, -1.05; q 0.0013; 0/12,
0/5); NK **-0.49** (-0.67, -0.30; 0/12, 0/5); macrophage **-0.40** (-0.72,
-0.11; 2/12, 1/5); monocyte **-0.23** (-0.34, -0.12; 2/12, 1/5); mast -0.24
(-0.34, -0.16; 1/12, 0/5); T cell +0.11 (-0.10, 0.38; 7/12, 2/5); B -0.07
(-0.31, 0.14; q 0.082); neutrophil +0.16 (-0.10, 0.45; q 0.0013 but CI includes
0); plasma -0.11 (-0.25, 0.03; q 0.091); fibroblast +0.31 (-0.11, 0.81; q
0.011); epithelial -0.33 (-0.91, 0.17; q 0.0013 but CI includes 0); malignant
**+3.79** (2.27, 5.35; 12/12, 5/5); stromal/other **-0.97** (-1.46, -0.51;
1/12, 1/5). Relative percent changes agree in direction (T +1.45%, CI -0.75 to
4.41; DC +9.81%; endothelial -21.47%; malignant +17.89%; stromal -19.88%).

Adjacent-normal, all spots (pp): macrophage **+0.45** (0.14, 0.82; q 0.0047;
8/10, 5/5); endothelial **-0.42** (-0.72, -0.15; q 0.0105; 1/10, 1/5); T -0.08
(-0.14, -0.03; q 0.0047; 3/10, 1/5); B -0.10 (-0.16, -0.04; q 0.0047; 2/10,
0/5); mast -0.06 (-0.09, -0.04; q 0.0196; 0/10, 0/5); DC +0.03 (-0.02, 0.07;
q 0.312); epithelial +0.32 (-0.12, 0.79; q 0.079). No other adjacent-normal
compartment reaches q_BH < 0.05: NK -0.07 (q 0.236), monocyte +0.05 (q 0.300),
plasma -0.002 (q 0.950), fibroblast -0.07 (q 0.312), malignant +0.04 (q 0.562),
stromal/other -0.05 (q 0.666).

Six-neighbour-only, tumour (pp): endothelial **-2.47** (-4.88, -0.70; q 0.0023),
malignant **+6.31** (3.30, 9.85; q 0.0023), fibroblast **-1.19** (-1.96, -0.38;
q 0.0157), epithelial **+1.43** (0.31, 3.09; q 0.0080), stromal/other **-1.50**
(-2.91, -0.05; q 0.0023), NK **-0.70** (-1.30, -0.23; q 0.0023), monocyte
**-0.63** (-1.01, -0.25; q 0.0023), macrophage -0.59 (-0.87, -0.26; p 0.091,
**q 0.116**), mast -0.50 (-0.87, -0.14; q 0.0023), plasma -0.42 (-0.70, -0.19;
q 0.116); T cell -0.005 (-0.28, 0.20; q 0.970), DC +0.39 (-0.21, 1.09; p 0.035,
q 0.054), neutrophil -0.03 (-0.32, 0.23; q 0.849). In interior spots the
composition axis is therefore epithelium/malignant up, endothelium and
fibroblast down, not an immune shift.

**Interpretation.** The pre-specified absolute-abundance increases for T cells,
B cells, DCs and neutrophils in tumour are largely explained by a ~12-13% higher
total cell density around high-CD276 spots (which itself tracks capture depth:
rho = 0.40 abundance vs counts). Once density is removed, only DCs show a
consistent positive immune-composition shift (+0.5 pp), while the endothelial
fraction falls by ~2 pp and the malignant fraction rises by ~3.8 pp. T cells are
not selectively enriched (relative change +1.4%, CI includes 0; +0.1 pp). In
adjacent-normal tissue the same pattern is weaker: small absolute increases
across all types, macrophage +0.45 pp as the only immune enrichment, endothelial
-0.42 pp. The interior-spot analysis removes most immune effects in tumour.

### 6.5 Multiplicity, spatial autocorrelation and donor clustering

**(a) Multiplicity.** Revision 1 reported raw within-section permutation
p-values with no correction. Revision 2 adds Benjamini-Hochberg FDR within
explicitly declared families: **20 family passes in total**, one row each in
`visium_neighborhood_multiple_testing_summary.csv`, and all three
neighbourhood tables now carry `permutation_p_bh`. The 20 passes are:

* absolute abundance = histology x metric (mean/q05): **4 passes of 12 tests**;
* additive composition pp = histology x variant x `composition_pp`:
  **4 passes of 14 tests**;
* relative composition = histology x variant x `relative_composition`:
  **4 passes of 14 tests**;
* each `total_abundance` endpoint (additive-pct and relative, all-spots and
  six-neighbour, both histologies): **8 single-test passes**.

In addition - not one of the 20 - the robustness table carries a global
48-test column (`permutation_p_bh_global48`). Revision 2 changelog #10 said
"five defined families"; that was an error and is corrected to 20 passes here
and in the Revision 2.1 block. Summary counts are in
`results/tables/visium_neighborhood_multiple_testing_summary.csv`.

Selected families:

| Family | n tests | q_BH < 0.05 | min raw p |
|---|---|---|---|
| Tumour absolute abundance (mean) | 12 | 11 | 0.0010 |
| Adjacent-normal absolute abundance (mean) | 12 | 12 | 0.0010 |
| Tumour composition pp, all spots | 14 | 12 | 0.0010 |
| Adjacent-normal composition pp, all spots | 14 | 5 | 0.0010 |
| Tumour composition pp, six-neighbour | 14 | 8 | 0.0010 |
| Adjacent-normal composition pp, six-neighbour | 14 | 0 | 0.126 |
| Tumour relative composition, all spots | 14 | 11 | 0.0010 |
| Adjacent-normal relative composition, all spots | 14 | 8 | 0.0010 |
| Tumour relative composition, six-neighbour | 14 | 5 | 0.0010 |
| Adjacent-normal relative composition, six-neighbour | 14 | 0 | 0.078 |

The correction does not rescue the fragile endpoints: the tumour six-neighbour
composition family retains 8/14 signals driven by the malignant/endothelial/
fibroblast axis, and the adjacent-normal six-neighbour family retains none
(min raw p = 0.126). The plasma-cell absolute increase (p = 0.149) and the
six-neighbour macrophage depletion (q = 0.116) remain non-significant.

**(b) Spatial autocorrelation.** The permutation null shuffles high/low labels
**within a section**, which destroys the spatial autocorrelation of both CD276
and the neighbour abundances. The resulting null is therefore too narrow and the
permutation p-values are **anticonservative**. This is a property no
multiplicity correction can fix. The 1,000-permutation floor is
1/1001 = 0.000999, and 9-10 of the 12 absolute-abundance tests sit exactly at
that floor; those q values should be read as "p <= 1/1001", not as precise
probabilities. The section-cluster bootstrap is the more defensible uncertainty
statement, and it is the one used for the CIs quoted above.

**(c) Donor clustering.** There are only **5 donors per histology**. "3/5" or
"4/5 donors positive" is a descriptive consistency count, not a formal test. The
bootstrap resamples sections, not donors, so it treats sections from one patient
as independent and **overstates precision relative to a donor-cluster analysis**.
The per-donor values are reported in the `donor_pct_changes` column of
`visium_neighborhood_robustness.csv` and in Figure 4E/S5B panel C so a
donor-level analysis can be reconstructed.

---

## 7. Limitations

1. **Depth confounding.** Total and immune abundance correlate with total
   counts (rho 0.40 and 0.30); high-CD276 spots are deeper in tumour
   (mean-of-section-means 9,164.2 vs 5,211.2; median-of-per-section-medians
   7,545.0 vs 3,708.5). Both aggregation definitions are in
   `visium_c2l_depth_balance_summary.csv`. Composition and density endpoints
   mitigate but do not eliminate this; a count-matched or depth-regressed
   design would be stronger.
2. **Sparsity / weak contrast.** CD276 is zero in 83% of all spots; the rank
   fallback was used in 22/22 sections because `<q25` was empty. In
   adjacent-normal, the "high" group is only 30% CD276-positive and has a median
   CD276 of 0.0 in 8/10 sections, so that panel tests a degenerate shallow tail
   and is close to noise.
3. **Edge dependence.** Most tumour immune effects change sign when 1-5
   neighbour spots are excluded; the primary estimate is not robust to spot
   inclusion.
4. **No independent validation.** Results are from one dataset (E-MTAB-13530);
   no held-out section or external Visium cohort was used.
5. **Model approximation.** Mapping used 3,000 epochs (paper 10,000) and CPU;
   the ELBO is flat, but absolute abundances are model-dependent and should not
   be compared across studies.
6. **Reference ELBO unavailable** (logger=False), so reference convergence can
   only be inferred from the reported 250/250 epochs and wall time.
7. **Post-hoc endpoints.** Composition and total-abundance sensitivity analyses
   were added after observing the depth and edge sensitivity; they are
   exploratory, not pre-registered. BH correction reduces but does not remove
   the exploratory-inference problem.
8. **Permutation null ignores spatial autocorrelation**, so p-values are
   anticonservative (Section 6.5b).
9. **Only 5 donors per histology**; section-level resampling overstates
   precision relative to a donor-level analysis (Section 6.5c).
10. **Panel-split assumption** (Section 5) is inferred, not documented.
11. **SDRF age/stage are unusable** (invalid M categories; age varies within
    patient), so no age- or stage-adjusted analysis is possible.

---

## 8. Bottom line

**Does the B7-H3-high niche show altered neighbouring immune abundance, and in
which direction?** In the pre-specified absolute-abundance analysis, yes:
tumour high-CD276 spots have higher neighbouring T cells (+15.4%, CI 1.1-29.0),
B cells (+15.2%, 0.6-28.3), dendritic cells (+28.8%, 9.4-46.9) and neutrophils
(+17.3%, 5.3-29.8), and lower endothelial cells (-16.0%, -25.3 to -4.8).
Adjacent-normal shows uniformly small positive changes (3-13%).

**How confident?** **Weak-to-moderate for a B7-H3-specific immune niche; strong
only for a density/endothelial story.** The absolute immune increases are
largely proportional to a ~12-13% higher total cell abundance around high-CD276
spots and do not survive restriction to interior spots. The composition analysis
leaves one consistent immune signal - dendritic cells +0.5 pp (9/12 sections,
4/5 donors) - and a set of **donor-concordant depletions**:

* **endothelium -2.03 pp** (0/12 sections positive, 0/5 donors),
* **NK cells -0.49 pp** (0/12, 0/5),
* **macrophage -0.40 pp** (2/12, 1/5),
* **monocyte/myeloid -0.23 pp** (2/12, 1/5),
* **mast cells -0.24 pp** (1/12, 0/5),
* plus a **malignant-cell enrichment of +3.79 pp** (12/12, 5/5) and a
  stromal/other depletion of -0.97 pp (1/12, 1/5).

The malignant/endothelial shift is the dominant composition axis; it is a
tumour-versus-stroma contrast, not an immune-cell recruitment signal. There is
**no evidence for selective T-cell enrichment**: the relative T-cell fraction is
essentially unchanged (+0.1 pp; +1.4% with CI crossing zero). The adjacent-normal
panel is weaker still and should be read as a shallow-gradient control, not as
independent confirmation. All of these composition estimates are exploratory and
carry the anticonservative-permutation and 5-donor caveats in Section 6.5.

**What the data support claiming:** high-CD276 regions in LUAD are modestly
denser, endothelial- and stromal-poor, malignant-enriched, and show a small
dendritic-cell enrichment; they are not a selectively T-cell-inflamed niche. The
paper's qualitative "immune-hot B7-H3 niche" pattern is reproduced only in
absolute abundance and is confounded by capture depth and edge effects.

---

### Output index

| File | Content |
|---|---|
| `results/tables/visium_c2l_training_convergence.csv` | Mapping ELBO convergence; reference explicitly unavailable |
| `results/tables/visium_c2l_abundance_sanity.csv` | Abundance vs depth, empty-spot and CD276-zero checks |
| `results/tables/visium_c2l_section_summary.csv` | Per-section spots, abundance, composition, CD276 |
| `results/tables/visium_c2l_depth_balance_summary.csv` | Depth-balance numbers with exact aggregation definitions: group median-of-medians and mean-of-means, all-spot pooled median, all-spot section median-of-medians |
| `results/tables/visium_c2l_cd276_stratification_audit.csv` | Per-section zero %, quartiles, fallback, mean and median depth balance |
| `results/tables/visium_neighborhood_immune_change.csv` | Per-section high-vs-low neighbour change |
| `results/tables/visium_neighborhood_robustness.csv` | Pooled effect, CI, permutation p, BH q, section/donor consistency (mean and q05) |
| `results/tables/visium_neighborhood_stratification.csv` | Group sizes and CD276 levels per section |
| `results/tables/visium_neighborhood_edge_spot_sensitivity.csv` | All spots vs six-neighbour-only, all 12 immune/context types |
| `results/tables/visium_neighborhood_composition_sensitivity.csv` | Post-hoc total abundance and relative composition percent change, 14 compartments, BH q |
| `results/tables/visium_neighborhood_composition_pp_difference.csv` | Post-hoc additive composition (percentage points), 14 compartments, equal-section weight, BH q |
| `results/tables/visium_neighborhood_multiple_testing_summary.csv` | Per-family test counts, p-at-floor counts and BH-significant counts |
| `results/tables/visium_c2l_mapping_history_README.md` | Which history files were removed (all three; none remain), why they were empty, and where the ELBO traces live |
| `data/processed/deprecated_all_nan_export/MANIFEST.md` | Audit manifest for the superseded all-NaN export |
| `results/figures/fig4e_c2l_tumor.png/.pdf` | Panel 4E: deconvolution maps and composition, 12 tumour sections |
| `results/figures/figs5b_c2l_adjacent_normal.png/.pdf` | Panel S5B: same for 10 adjacent-normal sections |
| `results/figures/fig4e_neighborhood_immune_change.png/.pdf` | Panel 4E: pooled, per-section and per-donor neighbourhood effects |
| `results/figures/figs5b_neighborhood_immune_change.png/.pdf` | Panel S5B: same for adjacent-normal |
| `results/figures/figs5_c2l_training_convergence.png` | Mapping ELBO and tail flatness; reference trace unavailable |

### Related corrections outside this report

These artifacts belong to Panels 4B/4C and to the Visium ingest QC, not to
4E/S5B, but they were produced in the same revision and are recorded here so the
synthesis can find them:

| File | Change |
|---|---|
| `results/tables/scrna_pseudobulk_de_top_genes.csv` | Rebuilt with an explicit sign filter (up = log2FC > 0, down = log2FC < 0, padj < 0.05 and abs(log2FC) > 0.5); 486 rows, 0 wrong-sign rows; generating script `code/scripts/scrna_pseudobulk_de_top_genes_signfiltered.py` committed |
| `results/tables/scrna_cd276_de_summary.csv` | CD276 row for all 15 contrasts; **0/15 significant**, smallest padj 0.2913 (SCLC macrophage, log2FC -0.9529) |
| `results/tables/scrna_census_batch_log.csv` | Marked as reconstructed; counts re-derived from merge-log shapes (90,384 + 206,186 + 205,736 = 502,306); file sizes/retries flagged hardcoded |
| `results/reports/visium_ingest_qc_log.md` | §1.1 added: SDRF age/stage anomalies (M2-M5 invalid; age varies within patient) |
| `results/tables/visium_sdrf_age_stage_integrity.csv` | 22-section audit table behind §1.1 |
