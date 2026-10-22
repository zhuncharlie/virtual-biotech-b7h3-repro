# Scientific Review — Round 2 B7-H3/CD276 Lung Cancer Case
## Full evidence-level review of the spatial arm (cell2location, Panels 4E/S5B, spatial neighbourhood) + live-run consistency audit

**Reviewer:** Scientific Reviewer (read-only role)
**Date:** 2026-10-21
**LIVE write directory audited:** `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
**SOURCE read-only predecessor:** `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35`
**Interim review consulted first:** `LIVE/work/scientific-reviewer/scientific_review_interim_panels1-6.md`
**Primary object of review:** `LIVE/work/single-cell-analyst/results/reports/visium_c2l_panels4e_s5b_report.md`

---

## Scope and read-only statement

I performed **no** analysis runs, **no** database queries, and modified **no** artifact belonging to any other agent. The only file written in this review is this report, under `work/scientific-reviewer/`. Every quantitative statement below is taken from a file I opened with Read; where a claim rests on a binary artifact (`.parquet`, `.h5ad`) that Read cannot decode, I say so explicitly in Section 8 rather than assuming its contents.

This environment exposes only Read/Write/Edit — **no shell, no glob, no grep**. I therefore could not enumerate directories. Absence findings are phrased as "does not resolve at path X" and I cannot fully exclude a differently named copy.

The review covers: (a) cell2location data integrity and the all-NaN export/re-map episode; (b) Panels 4E (tumour) and S5B (adjacent-normal); (c) the spatial-neighbourhood analysis including statistics, confounding, interpretation and robustness; (d) a panel-wide live-run consistency audit and the status of the six consolidated recomputations issued in the interim review.

**Structural finding that frames everything else:** LIVE contains only the spatial arm. `LIVE/work/genomics-analyst/`, `LIVE/work/clinical-trialist/` and `LIVE/work/functional-genomics-analyst/` do not resolve. The non-spatial panels (4A, 4B/4C, 4D/S5A, 4F, Tahoe) exist only in SOURCE. Synthesis must cite SOURCE for those panels and LIVE for the spatial panels; mixing the two without labelling the run is a traceability defect.

---

## Section 1 — cell2location data integrity and the all-NaN export / re-map

### 1.1 The re-map is real, the config is genuinely identical, and the replacement output is finite

I independently corroborated the known history rather than accepting it.

**The bug is reproducible from source.** `SOURCE/work/single-cell-analyst/code/scripts/visium_c2l_21_map_sections.py` builds the export as
`pd.DataFrame(adata.obsm[...], index=adata.obs_names, columns=[f"mean_{c}" for c in factor_names])`.
In pandas, `columns=` is a *selection label set*, not a rename. The obsm array's columns are `meanscell_abundance_w_sf_<type>`, so every requested `mean_<type>` label misses and the result is 100 % NaN. The original script had **no finiteness guard** and **did not save a model**, which is exactly why the defect escaped to disk undetected.

**A controlled probe confirms the mechanism** (`logs/c2l_export_probe_finiteness.csv`, script `visium_c2l_22_export_probe.py`, run-log row `export_probe`):
- raw `obsm` mean: NaN fraction **0.0000** (min 0.5236, max 0.6369)
- buggy prefixed-column construction: NaN fraction **1.0000**
- fixed rename construction: NaN fraction **0.0000**

This isolates the fault to the export construction, not to the model.

**The re-run is a genuine re-run, not a relabel.** `visium_c2l_21_map_sections_rerun.py` uses lr 0.002, batch 4096, N_cells_per_location 8, detection_alpha 20, 3,000 epochs, 22 sections as batch, seed 42 — identical to the original. It differs only in the corrected rename and the added finiteness guard plus model save. The ELBO traces differ numerically as expected from a non-deterministic re-fit: original 104,060,600 → 38,571,652; re-run 104,199,816 → 38,557,988; relative tail change −0.0752 % vs −0.0416 %. Section counts and spot counts are unchanged (22 sections; 47,448 spots; 27,826 tumour; 19,622 adjacent-normal).

**The replacement output passes a finiteness test**, which the original never did. `logs/c2l_mapping_rerun.log` prints "mean nan frac 0.0 min 0.0001046 max 33.3999"; q05 NaN fraction 0.0. Run-log row `mapping_rerun,ok` independently records `nan_frac=0`, `model_saved=True`.

### 1.2 Defects in the reporting of the incident (none changes a scientific conclusion)

1. **Column arithmetic in the report is wrong.** `visium_c2l_run_log.csv` row `mapping_output_audit,failed` states "100% NaN in all 28 abundance columns (664,272/664,272)". 28 columns × 47,448 spots = 1,328,544, not 664,272. 664,272 = 47,448 × **14**. The report (`§1`) repeats "664,272/664,272". The correct statement is either "28 columns (mean + q05), 1,328,544/1,328,544" or "14 mean columns, 664,272/664,272". Numbers that do not reconcile to their own stated column count undermine confidence in an otherwise honest incident log.
2. **The deprecated all-NaN artifact is not locatable.** I probed `LIVE/.../data/processed/deprecated_all_nan_export/visium_c2l_spot_abundances.parquet` and several plausible alternate names and manifests; none resolves. The report implies a quarantined copy exists. Either it does not, or it is differently named. This matters because a reviewer cannot confirm that nothing downstream reads stale data.
3. **No spot-level equivalence check is possible.** Because the original file is not recoverable, one cannot demonstrate spot-for-spot correspondence between original and re-run geometry. The section-level reconciliation (counts, per-section means) is what is available.

### 1.3 The reference model's ELBO is genuinely unavailable — and correctly *not* fabricated

`visium_c2l_training_convergence.csv` carries a reference row with `trace_available=False`, and `visium_c2l_42_diagnostics.py` plus `figs5_c2l_training_convergence.png` explicitly annotate the reference curve as **UNAVAILABLE** rather than plotting a substitute. This is the right call. `visium_c2l_run_log.csv` row `reference_train_correction` documents the cause: scvi-tools 1.4 populates `model.history` only when a Lightning logger is attached; `logger=False` was used; therefore `len(model.history)==0` and the earlier `epochs_completed=0` was a logging artefact, not a training failure (250/250 epochs reached, 4,581 s, 18.3 s/epoch).

**Residual trap:** `visium_c2l_mapping_history.csv` and `..._mapping_history_rerun.csv` are **header-only** (single column `epoch`) for the same reason, even though the mapping *was* logged. The real traces live in `logs/c2l_mapping_elbo_metrics_3000epoch.csv` (3,000 rows, 104,060,600 → 38,571,652) and `logs/lightning/c2l_mapping_rerun/3000ep/metrics.csv`. A future analyst reading the history CSVs would wrongly conclude no trace exists. These header-only files should either be deleted or carry a pointer row.

---

## Section 2 — Panels 4E (tumour) and S5B (adjacent-normal)

### 2.1 What reconciles

- **`visium_c2l_section_summary.csv`**: 22 rows, 14 `mean_*` abundance columns. Spot totals reconcile exactly to the QC chain: tumour 27,826, adjacent-normal 19,622, total 47,448.
- Mean CD276 log-normalised expression: **0.235 tumour / 0.109 adjacent-normal**; section-mean % positive **23.8 % / 7.5 %**. This is consistent with CD276 being more abundant in tumour than in adjacent normal — the directional claim the panels are built to support.
- **`visium_c2l_abundance_sanity.csv`** reproduces exactly into the report: total abundance vs counts Spearman **0.401901**, immune vs counts **0.303456**, vs n_genes **0.387261**; median total 5.365, median immune 2.562; total <1 in 0.004215 %, immune <1 in 3.064 %; CD276 zero fraction **83.3186 %**, median positive 0.9908, max 3.9567.
- `logs/c2l_diagnostics_run.log` reproduces the convergence and sanity tables line for line.
- Figures `fig4e_c2l_tumor.png` (12 tumour sections; representative P24_T1, n = 3,248) and `figs5b_c2l_adjacent_normal.png` (10 sections; P24_B2, n = 2,801) are non-degenerate, and their section counts, labels and units match the tables. Composition stacked bars span all 14 compartments and are normalised per section in `visium_c2l_40_panels.py`.

### 2.2 What does not reconcile

**(a) "Tumour sections are denser" is contradicted by the analyst's own table.** Reading `visium_c2l_section_summary.csv` column-wise, median `mean_total_abundance` is **~7.14 in adjacent-normal vs ~6.42 in tumour**. The report's characterisation of tumour as the denser compartment is backwards at the section-median level. Given that the whole neighbourhood sensitivity analysis (Section 3) exists *because* absolute abundance is depth/density-confounded, getting the direction of the density difference wrong is not cosmetic — it changes how a reader interprets the absolute-abundance endpoints.

**(b) CD276 in adjacent-normal is largely a near-zero measurement.** The stratification audit (`visium_c2l_cd276_stratification_audit.csv`) shows the adjacent-normal **"high-CD276" quartile has median CD276 = 0.0 in 8 of 10 sections** (all except P15_B1/B2). So for the majority of normal sections, "high CD276" is a tie-broken arbitrary split among zeros, not a biological high group. Any panel claim about "high-CD276 adjacent-normal neighbourhoods" is therefore weak by construction and must be stated with this caveat. Tumour high-group medians (0.34–1.06) are genuinely above zero, so the tumour split is better founded.

**(c) CD276 in tumour is fibroblast-dominated, and the panels do not say so.** Per `SOURCE/.../results/tables/scrna_cd276_expression_by_celltype.csv`: LUAD fibroblast 3,411 cells / 30.84 % positive / mean 0.329; malignant and epithelial compartments lower; normal macrophage 3,011 / 36.53 % / 0.260. The spatial panel is presented as a CD276 abundance story without an explicit statement that the dominant CD276 source in tumour is the fibroblast compartment. This is a provenance/interpretation gap, and a **safety-relevant** one: CD276 is detectable in normal macrophages at 36.53 % positivity, which bears on any normal-tissue-sparing argument for a CD276-directed agent.

---

## Section 3 — Spatial-neighbourhood analysis

### 3.1 The method is soundly specified and correctly implemented

`visium_c2l_30_neighborhood_analysis.py` implements what the report says: k = 6 hex lattice via `cKDTree.query_ball_point(r=2.05)` with the centre spot excluded; unweighted neighbour mean; per-section CD276 log1p(CP10K) top/bottom quartile; 1,000 section bootstrap resamples; 1,000 within-section label-shuffle permutations; pooled ratio estimator Σ(high−low)/Σ(low). `logs/c2l_neighborhood_full.log` reproduces the delivered `visium_neighborhood_robustness.csv` mean block exactly, and I re-verified all 48 primary rows against the CSV. Median per-section values: T 5.89 (9/12 sections, 3/5 donors), B 1.21 (6/12, 2/5), dendritic 6.64 (10/12, 4/5), neutrophil 5.95 (11/12, 4/5), endothelial −5.27 (2/12, 0/5). q05 reproduces the same signs.

### 3.2 Statistics: the correct caveats are missing

- **No multiplicity correction anywhere.** A single FDR/BH pass over the 48 primary rows plus the composition endpoints is required before any endpoint is labelled "significant."
- **The permutation null ignores spatial autocorrelation.** Shuffling high/low labels *within* a section destroys the spatial structure that generates the signal. Under positive spatial autocorrelation, the effective number of independent observations is far below the spot count, so these p-values are anticonservative. `p = 0.000999` is the arithmetic floor of 1,000 permutations, not evidence of overwhelming effect.
- **Donor clustering is unmodelled.** The bootstrap resamples **sections**, but donors supply multiple sections. The donor-consistency columns (`n_donors`, `n_donors_positive`) are reported descriptively, yet the CI treats sections as independent. A donor-level cluster bootstrap (or at minimum a stated caveat) is needed. Several effects have low donor concordance — e.g. endothelial 0/5 donors, NK 0/5 donors in tumour all-spots — which the CIs do not reflect.
- **"ns" is undefined and inconsistently applied.** The report calls neutrophil "+0.16 (ns)" while the corresponding row in `visium_neighborhood_composition_pp_difference.csv` has `permutation_p = 0.000999`. Either "ns" means "CI includes zero" (state it) or the label is wrong.

### 3.3 Confounding: honest, and the analyst deserves credit

The composition sensitivity is the strongest part of this analysis. It correctly recognises that absolute neighbour abundance scales with local density, and it supplies both a relative-composition endpoint and an additive percentage-point endpoint with equal section weighting. Its central finding is robust and uncomfortable: **the tumour absolute-abundance effect is a density effect.** Tumour total neighbour abundance is **+13.21 %** (−2.34, 27.30) with only 3/5 donors positive, while the *relative* composition shifts down for most immune types and the interior-only variant flips the total to **−9.60 %**. This must be foregrounded, not buried.

### 3.4 Statistical errors in the composition endpoint

**(a) The "sums to ~0" check is invalid because the denominator has 14 compartments but only 12 are reported.** `visium_c2l_31_...py` computes `rel` over all 14 `mean_*` columns (including `malignant cell` and `stromal/other`); `visium_c2l_32_...py` computes over 14 but reports `TYPES` = 12. The printed check and the report both assert the percentage-point differences sum to ~0. They do not:

| Scope | Sum of reported pp differences |
|---|---|
| Tumour, all spots | **−2.820** |
| Tumour, interior only | **−4.811** |
| Adjacent-normal, all spots | +0.0084 |
| Adjacent-normal, interior only | +0.0017 |

The residual is the un-reported malignant + stromal movement (denser tumour neighbourhoods are relatively more malignant/stromal). Reporting the other 12 as if they exhaust the composition is a real inference error, and it directly weakens the interior-only claim that the shift "is not an immune shift" — the missing −4.81 pp is being attributed nowhere. **Fix:** emit all 14 `TYPES` (or explicitly report a `malignant+stromal` "remainder" row and remove the "sums to ~0" assertion).

**(b) The report says "11 types"; the table has 12.** `visium_c2l_31_...py` line 2 of its printed header lists 12: T, B, NK, macrophage, monocyte/myeloid, dendritic, mast, neutrophil, plasma, fibroblast, epithelial, endothelial. The corresponding relative percentage changes sum to **−38.13 %** in tumour and **+3.07 %** in adjacent-normal — not the "−18.2 % / +3.5 %" written in the `visium_c2l_32_...py` docstring (stale) and not a zero-sum quantity.

**(c) The composition column-alignment correction is real and correctly documented.** `visium_c2l_run_log.csv` row `neighborhood_composition_sensitivity_correction` (23:21:31) records that the 23:15:02 run had `nb_rel` with 14 columns while `TYPES` had 11, mislabelling relative-composition rows; it was fixed and re-run at 23:18:48, and `logs/c2l_neighborhood_composition_sensitivity.log` (the corrected run) reproduces the delivered `visium_neighborhood_composition_sensitivity.csv` exactly. The additivity-defect that remains (§3.4a) is a *different* problem and was **not** introduced by that fix.

### 3.5 Edge-spot and interpretation errors

**(a) The edge-spot table omits the three context types.** `visium_c2l_30_...py` loops `for ct in IMMUNE_TYPES` for the edge sensitivity, so `visium_neighborhood_edge_spot_sensitivity.csv` has only 9 rows per histology — no fibroblast, epithelial or endothelial. The report nonetheless says "NK and endothelial remain negative." **Endothelial is not in the table at all, and NK flips sign** in tumour (pooled +3.81 all-spots → −18.55 interior). The sentence is wrong on both clauses. Tumour sign flips across the board (T +15.37→−7.06, B +15.16→−7.48, macrophage −7.58→−29.11, monocyte +2.19→−25.94, neutrophil +17.27→−4.72, plasma +2.92→−28.37) — a signal that the edge sensitivity undermines nearly every tumour immune claim, and that adjacent-normal effects are stable (all positive). **Fix:** loop over `CELL_TYPES`, and rewrite the sentence.

**(b) The bottom line omits the most robust depletions.** The strongest, most donor-concordant composition effects are **endothelial −2.03 pp (0/12 sections positive, 0/5 donors)**, **NK −0.49 pp (0/12, 0/5)**, macrophage −0.40, monocyte −0.23, mast −0.24. The report's bottom line focuses on dendritic-cell increase and B-cell fragility while omitting the consistent negative compartments. For a target-evaluation deliverable, the reproducible *depletion* of NK/endothelial/myeloid in high-CD276 tumour neighbourhoods is at least as relevant as the DC increase.

### 3.6 Stratification mechanics

- **Rank fallback is active in 22/22 sections** (`visium_c2l_cd276_stratification_audit.csv`): `n_cd276_lt_q25 = 0` everywhere, because CD276 is zero in 76.22 % (range 66.29–86.91) of tumour spots and **92.51 %** (83.71–98.18) of adjacent-normal spots. `np.argsort(..., kind="stable")` then defines the low quartile by input order. This is deterministic for a fixed file but arbitrary with respect to biology, and the tie-break bias has not been tested (e.g. by re-running with a shuffled index and checking stability of the sign).
- **`median_total_counts_high` / `_low` are mislabelled means.** `visium_c2l_43_...py` lines computing these use `.mean()`, not a median. The column names in `visium_c2l_cd276_stratification_audit.csv` are therefore wrong and must be renamed or recomputed, especially since they are the evidence used to argue the depth confound.
- **The report's ">q75 empty" statement is wrong.** The audit's `n_cd276_gt_q75` is non-zero in **6 tumour sections**; it is `n_cd276_lt_q25` that is zero in all 22. Only the low quartile is degenerate.
- Isolated spots: 37 tumour / 93 normal = 130; 1–5-neighbour spots 2,783 / 3,219 = 6,002. These support including the edge variant.

### 3.7 Figure/data inconsistency

`visium_c2l_41_neighborhood_figures.py` Panel C plots per-donor values as the **unweighted mean of per-section percentage changes**, while `visium_neighborhood_robustness.csv` computes `donor_pct_changes` as the **pooled ratio**. These are different estimators and can differ substantially when donors contribute unequal spot counts. A reader comparing the figure to the table will see unexplained discrepancies. Also in Panel A, the legend colour rule conflates "context type" with "CI includes zero," so a grey point is ambiguous.

### 3.8 Bottom line on Section 3

The neighbourhood analysis is **methodologically honest about density confounding and reproducible from its logs**, but its headline should be: *in tumour, high-CD276 neighbourhoods are denser overall and relatively depleted of NK, endothelial, macrophage, monocyte and mast compartments, with a relative DC increase; the absolute-abundance effects flip sign at section edges; the adjacent-normal split is degenerate in 8/10 sections; and the percentage-point accounting is incomplete.* Nothing here should be reported as "significant" without multiplicity correction, a spatial-correlation caveat, and donor-level clustering.

---

## Section 4 — Live-run consistency across ALL panels, and status of the six interim recomputations

### 4.1 LIVE is spatial-only and not self-contained

- `LIVE/work/genomics-analyst/`, `LIVE/work/clinical-trialist/`, `LIVE/work/functional-genomics-analyst/` do **not resolve**. Panels 4A/4B/4C/4D-S5A/4F/Tahoe exist only in SOURCE.
- `LIVE/.../data/processed/visium_sections_qc.h5ad` does **not resolve**, yet `visium_c2l_21_map_sections_rerun.py` reads the h5ad from a **hardcoded SOURCE path**. LIVE cannot be re-run independently of SOURCE.
- `LIVE/.../results/tables/visium_spot_qc_metrics.csv` is **absent**, though it exists in SOURCE with the full `qc_pass`/`qc_fail_reason` schema.
- `LIVE/.../code/scripts/visium_01_verify_extract.py` and `visium_02_qc_combine.py` do **not resolve**, yet `LIVE/.../results/reports/visium_ingest_qc_log.md` cites both plus the missing spot-QC table.

**Present and content-identical to SOURCE:** `visium_section_qc_inventory.csv` (e.g. P10_T1 2,200→2,168), `visium_barcode_matching.csv`, and `visium_qc_threshold_sensitivity.csv`, whose six rows (300/100/15→49,401 90.4; 300/100/20→50,245 91.94; 500/200/20→47,448 86.82 primary; 500/200/15→46,627 85.32; 500/200/30→47,783 87.43; 1000/300/20→41,508 75.95) match the ingest report exactly.

### 4.2 The six consolidated recomputations from the interim review: **none applied**

SOURCE files were unmodified after 2026-10-21 22:01, and direct reads confirm each defect persists:

| # | Recomputation | Evidence it was NOT applied |
|---|---|---|
| 1 | 4A G7 locus-interval note (201/195 → 69/65) | `SOURCE/work/genomics-analyst/results/tables/cd276_round2_germline_verification.csv` still reads "Sensitivity (locus-interval overlap): 69 all types / 65 GWAS" — note:** this is the current content; if the intended correction is *to* 69/65 then the file is already correct and the interim note referred to the older 201/195 text. Either way the live table and the interim review disagree on which numbers are authoritative, and that must be resolved explicitly.** |
| 2 | 4B/4C CD276 DE summary + sign-filtered top-genes rebuild | `SOURCE/.../results/tables/scrna_pseudobulk_de_top_genes.csv` "up" ranks still contain negative log2FC (HINT1 −0.6061 … ITM2B −1.0504), and paired_3donors up/down share identical genes (TXN, CCL17) |
| 3 | 4D/S5A CXCR3/arithmetic correction | not verifiable in LIVE (no genomics-analyst directory); SOURCE not re-checked in this pass |
| 4 | 4F optional; batch log hand-write fix | `SOURCE/work/single-cell-analyst/code/scripts/04_write_batch_log.py` still hardcodes the b1 row, file sizes 613.15/568.37 MB, `retry_count: 0` |
| 5 | Tahoe lung histology counts (11 LUAD / 1 SCLC / 10 other) | LIVE has no Tahoe outputs; SOURCE prose not re-verified in this pass |
| 6 | Visium: restore `visium_spot_qc_metrics.csv` + SDRF metadata-integrity note | Table still absent from LIVE; `visium_ingest_qc_log.md` still has no SDRF age/stage integrity note |

Also unresolved from the interim: LIVE lacks `scrna_cd276_expression_by_celltype.csv`, `scrna_pseudobulk_de_top_genes.csv`, and `fig4b_umap_luad_sclc.png`; these exist only in SOURCE.

### 4.3 Do any of these defects materially change a conclusion? **No.**

I checked each against the conclusions they would support:
- The G7 note mismatch affects a *sensitivity* line, not the primary germline verdict.
- The top-genes sign-filtering error affects the *ranking labels* in a supporting table, not the direction of the overall CD276 expression difference.
- The batch-log hand-write affects provenance metadata, not any measurement.
- The missing spot-QC table affects reproducibility, not the reported QC pass rate (which reconciles to 47,448 independently via `visium_section_qc_inventory.csv`).
- The missing SDRF note is a disclosure gap on metadata integrity, not a data-quality measurement.

The material defects are the ones in Sections 2–3 of this review (density direction, pp sum, edge-table omission, mean/median labels, missing multiplicity), because those affect what a reader concludes about the target.

### 4.4 Epoch-deviation audit (independently checked)

The claimed deviations are real: reference **250** epochs / 4,586.9 s (18.3 s/epoch), mapping **3,000** epochs. But the *justification* is only partly traceable. `logs/c2l_compute_and_api_log.md` contains the measured throughput (reference 23.0 s/epoch, 94 steps, 0.24 s/step; mapping benchmark 3.1 s/epoch, 0.259 s/step, 12 steps/epoch), the GPU-policy block, and the 10,000-epoch projection (31,000 s = 8.6 h, above the ~8 h cap) that motivated 3,000 epochs. **None of those figures appear in the §2 of `visium_c2l_panels4e_s5b_report.md`.** A reader of the report alone cannot see why 3,000 was chosen; they see only a wall-clock deviation. Add the measured benchmark and the cap argument to §2.

---

## Section 5 — Recurring failure-pattern check

| Pattern | Evidence | Status |
|---|---|---|
| **Silent all-NaN / degenerate export** | Original mapping had no finiteness guard; `c2l_mapping_full.log` prints "spot abundances: (47448, 38)" with no NaN check. Re-run added one. | **Recurred once; guarded in the re-run only.** The guard exists in script 21-rerun but not in any template. Recommend a shared assertion. |
| **Prose not reconciled to delivered table** | "NK and endothelial remain negative" (Section 3.5); ">q75 empty" (3.6); "11 types" (3.4b); "tumour denser" (2.2a); "neutrophil +0.16 (ns)" (3.2); "sums to ~0" (3.4a). | **Recurring, 6 instances in one report.** The report is written ahead of / alongside the tables rather than read back from them. |
| **Column-label vs column-selection confusion** | The all-NaN bug (pandas `columns=`) and the composition `TYPES`/`nb_rel` misalignment (14 vs 11) are the same class of error, in two different scripts. | **Recurred.** Both were caught, but only after delivery. A `shape`/`columns` assertion at every DataFrame construction would prevent both. |
| **Mislabelled statistic** | `median_total_counts_high/low` computed with `.mean()` in script 43. | **Present.** |
| **Stale docstring** | Script 32 docstring says "−18.2 % / +3.5 %"; delivered is −38.13 % / +3.07 %. | **Present.** |
| **Estimator divergence between figure and table** | Figure Panel C per-donor = mean of per-section pct; table `donor_pct_changes` = pooled ratio. | **Present.** |
| **Header-only log file** | `visium_c2l_mapping_history*.csv` are empty despite successful logging elsewhere. | **Present.** |
| **Hardcoded cross-run path** | Script 21-rerun reads SOURCE h5ad. | **Present.** |
| **Correctly handled** | Reference ELBO unavailability was not fabricated; the all-NaN incident was logged in detail (including the failed audit row); the composition re-run was logged with its cause and timestamp. | **Credit where due.** |

The dominant pattern is **prose/table divergence**: the narrative contains at least six statements contradicted by the tables it cites. That is the single highest-value fix for this agent — a mandatory read-back pass where every sentence containing a number is checked against the delivering file.

---

## Section 6 — Claims inventory

Legend: **S** = supported (verified in file); **P** = partially supported (direction right, caveat/qualifier missing or a sub-clause wrong); **U** = unsupported (no file backs it); **W** = wrong (file says otherwise).

| # | Claim (as stated in `visium_c2l_panels4e_s5b_report.md`) | Verdict | Evidence / correction |
|---|---|---|---|
| 1 | Stored abundances were 100 % NaN and forced a re-map | **S** (with arithmetic error) | `c2l_export_probe_finiteness.csv`; run-log `mapping_output_audit,failed`. But "28 columns (664,272)" is arithmetically 14 columns — fix. |
| 2 | Cause was prefixed names passed as `columns=` | **S** | probe: buggy 1.0 vs fixed 0.0; original script line confirmed |
| 3 | Re-run used identical config | **S** | scripts 21 vs 21-rerun parameters identical; ELBO paths differ only as expected |
| 4 | Re-run output is finite | **S** | `c2l_mapping_rerun.log`: nan frac 0.0, min 0.0001046, max 33.3999 |
| 5 | Reference model trained 250 epochs, 4,586.9 s | **S** | run-log `reference_train_correction`; 18.3 s/epoch |
| 6 | Reference ELBO is unavailable | **S, correctly handled** | convergence CSV `trace_available=False`; figure annotation |
| 7 | Mapping trained 3,000 epochs | **S** | metrics CSVs; run-log |
| 8 | Rationale for 3,000 epochs (throughput, 8 h cap) | **P** | present in `c2l_compute_and_api_log.md`, **absent from report §2** |
| 9 | 22 sections, 47,448 spots | **S** | `visium_c2l_section_summary.csv`; ingest logs |
| 10 | Tumour mean CD276 lognorm 0.235 vs normal 0.109 | **S** | `visium_c2l_section_summary.csv` |
| 11 | Section-mean % positive 23.8 % / 7.5 % | **S** | same file |
| 12 | CD276 zero in 83.32 % of spots; median positive 0.9908 | **S** | `visium_c2l_abundance_sanity.csv` |
| 13 | Total abundance vs counts Spearman 0.402 | **S** | same file |
| 14 | "Tumour sections are denser" | **W** | section-summary median total abundance ~7.14 normal vs ~6.42 tumour |
| 15 | High-CD276 quartile defined per section, fallback applied | **S** | audit: rank_fallback 22/22 |
| 16 | "Low quartile empty because >q75 is empty" | **W** | `n_cd276_lt_q25` = 0 in 22; `n_cd276_gt_q75` non-zero in 6 tumour sections |
| 17 | `median_total_counts_high/low` are medians | **W** | script 43 uses `.mean()` |
| 18 | Adjacent-normal high group is a real high-CD276 group | **P/W** | high-group median CD276 = 0.0 in 8/10 normal sections |
| 19 | Tumour high-CD276 neighbourhoods show higher absolute immune abundance | **P** | +13.21 % pooled but CI (−2.34, 27.30) includes 0; 3/5 donors positive |
| 20 | Effect is a density effect, not composition | **P** | supported by relative-composition results, but the report does not foreground it |
| 21 | Relative composition: DC increase | **S** | +0.4944 pp (0.1480, 0.8405), 9/12 sections, 4/5 donors |
| 22 | Relative composition: NK depletion | **S but omitted from bottom line** | −0.4870 pp, 0/12, 0/5 |
| 23 | Relative composition: endothelial depletion | **S but omitted from bottom line** | −2.0304 pp, 0/12, 0/5 |
| 24 | "NK and endothelial remain negative under edge sensitivity" | **W** | endothelial absent from edge table; NK flips +3.81 → −18.55 |
| 25 | Percentage-point differences "sum to ~0" | **W** | tumour sum −2.820 (all) / −4.811 (interior) |
| 26 | "11 types" in composition endpoint | **W** | 12 types in script header and table |
| 27 | Neutrophil "+0.16 (ns)" | **W / P** | `permutation_p = 0.000999` |
| 28 | Edge-spot sensitivity covered all cell types | **W** | script loops `IMMUNE_TYPES` only (9, not 12) |
| 29 | Interior-only total abundance is negative in tumour | **S** | −9.600 (−29.667, 20.659), p = 1.0 |
| 30 | B-cell effect is fragile | **S** | T 1.21 (6/12, 2/5) |
| 31 | q05 abundance reproduces mean direction | **S** | `visium_neighborhood_robustness.csv` q05 block |
| 32 | Convergence: 99.96 % of decrease by epoch 2,700 (original) | **S** | `visium_c2l_training_convergence.csv` |
| 33 | Convergence: re-run 99.98 %, slope −131.31 | **S** | same file |
| 34 | Panel figures match underlying tables | **S** (with cosmetic issues) | figures read; Panel C estimator differs from table |
| 35 | All 48 primary neighbourhood rows | **S** | re-verified against CSV |
| 36 | CD276 dominant source in tumour is fibroblast | **U (omitted)** | `scrna_cd276_expression_by_celltype.csv` (SOURCE): LUAD fibroblast 30.84 %, mean 0.329 |
| 37 | Normal-tissue safety context (CD276 in normal macrophages) | **U (omitted)** | same file: normal macrophage 36.53 % positive |
| 38 | Deprecated all-NaN artifact is preserved | **U** | path does not resolve |
| 39 | LIVE run is self-contained | **W** | h5ad only in SOURCE; spot-QC table and Visium scripts absent |

---

## Section 7 — Required recomputations (file, script, column)

**Priority 1 — changes an interpretation**
1. **Emit all 14 compartments in the composition endpoints.** Scripts `visium_c2l_31_neighborhood_composition_sensitivity.py` and `visium_c2l_32_neighborhood_composition_pp.py`: set `TYPES = ALL14` (add `malignant cell`, `stromal/other`), or add an explicit remainder row. Regenerate `visium_neighborhood_composition_pp_difference.csv` and `visium_neighborhood_composition_sensitivity.csv`; remove the "should be ~0" assertion or make it apply to the full 14. Report the residual that currently sits at −2.820 (tumour all) / −4.811 (tumour interior).
2. **Fix the edge-spot loop to all 12 types.** Script `visium_c2l_30_neighborhood_analysis.py`, edge loop `for ct in IMMUNE_TYPES` → `for ct in CELL_TYPES`. Regenerate `visium_neighborhood_edge_spot_sensitivity.csv`. Rewrite the sentence in §6 of the report about NK/endothelial.
3. **Correct the depth-direction prose.** Report §4/§2: replace "tumour sections are denser" with the section-summary values (median `mean_total_abundance` ~6.42 tumour vs ~7.14 normal).

**Priority 2 — reporting accuracy**
4. **Rename or recompute `median_total_counts_high/low`.** Script `visium_c2l_43_cd276_stratification_audit.py`: either change `.mean()` → `np.median()` or rename columns to `mean_total_counts_high/low`. Regenerate `visium_c2l_cd276_stratification_audit.csv`.
5. **Fix the all-NaN column arithmetic.** `visium_c2l_run_log.csv` row `mapping_output_audit,failed` and report §1: state 28 columns/1,328,544 or 14 columns/664,272 consistently.
6. **Fix ">q75 empty" → "<q25 empty"** in report §5/§6.
7. **Fix "11 types" → 12** in report §6.
8. **Define "ns" or fix the neutrophil label.** Report §6; use the delivered `permutation_p`.
9. **Add multiplicity correction and a spatial-autocorrelation caveat** to report §6/§7, and a donor-cluster caveat.
10. **Surface the omitted robust depletions** (NK, endothelial, macrophage, monocyte, mast) in the report bottom line.
11. **Reconcile Figure Panel C with the table.** Script `visium_c2l_41_neighborhood_figures.py`: either compute per-donor pooled ratio (matching `donor_pct_changes`) or state on the figure that it is a section-mean estimator.
12. **Fix the Panel A legend** so "context type" and "CI includes zero" are distinct encodings.

**Priority 3 — provenance**
13. **Restore `visium_spot_qc_metrics.csv`** to `LIVE/work/single-cell-analyst/results/tables/` (copy from SOURCE); restore `visium_01_verify_extract.py`, `visium_02_qc_combine.py` and their logs, or re-point the ingest report's citations.
14. **Repoint script 21.** `visium_c2l_21_map_sections_rerun.py`: replace the hardcoded SOURCE h5ad path with a LIVE path and copy `visium_sections_qc.h5ad` into LIVE `data/processed/`.
15. **Add a deprecated-artifact manifest** (path, row/column count, NaN count, superseding file) for the original all-NaN parquet, or state that it was deleted.
16. **Delete or annotate** `visium_c2l_mapping_history.csv` / `_rerun.csv`.
17. **Add measured throughput and the 8 h cap rationale** to report §2.
18. **Add a provenance sentence on CD276's fibroblast source and normal-macrophage positivity** to report §1 or §7.
19. **Apply recomputations 1–6 from the interim review** (Section 4.2), at minimum #2 (top-genes sign filter), #4 (batch log), #6 (spot table + SDRF note); resolve the G7 69/65 ambiguity explicitly.

**Priority 4 — reproducibility controls**
20. **Add a shared assertion** (`assert df.notna().any().any()`, `assert df.shape[1] == len(expected)`) at every DataFrame construction in the c2l scripts, so the all-NaN and column-alignment classes of bug fail fast. This is the single highest-leverage change.

---

## Section 8 — What I could not verify

Stated plainly, per the adversarial-but-fair instruction:

1. **Binary artifacts.** `visium_c2l_spot_abundances.parquet`, `visium_c2l_abundances_small.h5ad`, `visium_sections_qc.h5ad` cannot be decoded by Read. Every numerical statement about them in this review comes from a CSV/log derived from them, not from the binaries.
2. **Deprecated all-NaN export.** Path does not resolve under `data/processed/deprecated_all_nan_export/`; I could not confirm its existence, shape, or NaN count.
3. **Spot-level equivalence** between original and re-run mapping cannot be tested.
4. **LIVE non-spatial panels.** `genomics-analyst`, `clinical-trialist`, `functional-genomics-analyst` directories do not resolve; those panels' LIVE-state recomputations (#3, #5) are unverified. SOURCE files were not re-read for this pass except as cited.
5. **Tahoe prose recomputation (#5).** I could not resolve a Tahoe report filename in LIVE and did not confirm the 11/1/10 histology correction.
6. **G7 note direction.** The live table reads "69 all types / 65 GWAS"; the interim review described the defective text as 201/195. I cannot determine from the files alone which numbers the correction intended, so I flag the contradiction rather than assert an error.
7. **Directory enumeration.** No shell/glob/grep. Absence findings are path-specific and cannot exclude differently named copies.
8. **Donor identity in the bootstrap.** I confirmed sections are the resampling unit by reading the code; I did not re-derive the donor mapping to confirm no donor is split across `histology` groups.
9. **Provenance registration.** The `mcp__provenance__register_artifact` tool is not available in this environment; artifacts are not explicitly registered by me.

---

## Section 9 — Bottom line

**What may safely be concluded now**

- CD276 (B7-H3) is more highly expressed in these LUAD tumour sections than in patient-matched adjacent-normal sections (mean lognorm 0.235 vs 0.109; % positive 23.8 % vs 7.5 %), with the caveat that CD276 is zero in 83 % of tumour spots.
- In tumour, high-CD276 spatial neighbourhoods are **denser overall** (total neighbour abundance +13.21 %, CI crossing zero) and show a **relative depletion** of NK, endothelial, macrophage, monocyte and mast compartments, with a relative **dendritic-cell increase** (+0.49 pp, 9/12 sections, 4/5 donors). These composition directions are reproducible across bootstrap and permutation and are not an artefact of capture depth.
- The absolute-abundance framing is **not** safe on its own: the effect reverses sign at section edges in tumour (interior total −9.60 %), so any "immune-hot neighbourhood" language must be restricted to interior spots and stated with the composition results alongside.
- The all-NaN export episode is genuine, was caused by a pandas `columns=` selection error, was fixed by a genuinely identical re-run, and the replacement output is finite. The reference model's ELBO is genuinely unavailable and was not fabricated. Both are handled honestly.

**What must be softened or corrected before synthesis**

1. Delete "tumour sections are denser" — the section summary shows the opposite.
2. Delete "NK and endothelial remain negative under edge sensitivity" — endothelial is absent from the table and NK flips.
3. Do not assert that the composition percentage-point differences sum to ~0 — they sum to −2.820 (all spots) / −4.811 (interior) because malignant and stromal compartments are omitted.
4. Replace ">q75 empty" with "<q25 empty."
5. Rename `median_total_counts_*` or recompute them as medians.
6. State that the adjacent-normal "high-CD276" group has median CD276 = 0.0 in 8/10 sections — the normal split is degenerate.
7. Add multiplicity correction, a spatial-autocorrelation caveat, and a donor-cluster caveat to every significance claim.
8. Promote NK / endothelial / macrophage depletion to the bottom line; they are the most donor-concordant findings and are currently omitted.
9. Report the fibroblast origin of tumour CD276 and the 36.5 % positivity in normal macrophages — both are directly relevant to target rationale and to normal-tissue safety.

**Verdict:** **Revise and resubmit.** The underlying computations are largely trustworthy and the analyst's handling of the two hardest integrity questions (all-NaN re-map, missing reference ELBO) is exemplary. The failure is at the prose/table interface: at least six numeric sentences in the report are contradicted by the tables it cites, and three interpretation errors (density direction, pp accounting, edge-sensitivity claim) would mislead a reader about the biology. None of these requires re-running a model; all are fixable from the existing outputs, plus the Priority-1 script changes in Section 7. The six interim recomputations remain outstanding across the run and should be closed before synthesis.

---

*All paths above are relative to the LIVE run root unless prefixed with `SOURCE/`. Findings derive only from files opened with Read in this session.*
