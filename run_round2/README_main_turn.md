# Run `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`

> Round 2 of the B7-H3 (CD276) case study was interrupted mid-execution by a transient API connection error, not a data or code problem. Before doing anything else, read this resume file in full: /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/config/resume_after_interruption_3.md -- it tells you exactly what is already done and verified (reuse directly, do not redo), what was in progress when the interruption hit (verify what exists on disk, resume rather than restart), and what has not started yet. The original scope/rules file is still at /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/config/full_requirements.md if you need to check any detail not covered in the resume file. State briefly that you have read the resume file, then continue execution: finish Wave 2 (LIANA 4D/S5A, cell2location 4E/S5B), then proceed through the spatial-neighborhood analysis, the scientific-reviewer pass (checking underlying data/scripts/figures directly, not just report prose), and final synthesis. No approval checkpoint needed this time -- proceed straight through to delivery.

| | |
|---|---|
| **Status** | interrupted |
| **Started** | 2026-10-21T20:40:38.906893 |
| **Duration** | 248.6 min |
| **Specialists** | 5 |
| **Artifacts** | 344 (700.7 MB) |
| **Tool calls** | 1012 (882 by specialists, 130 by the CSO) |
| **Tool errors** | 106 |
| **Claims** | 0 |
| **Evidence coverage** | incomplete |

> **Evidence audit incomplete.** File hashes alone do not establish that the report's conclusions have recorded support.

- Scientific analysis was recorded, but no claims were filed; the evidence audit is incomplete.
- The final report contains no claim references, so its conclusions are not linked to the recorded evidence.
- Research turn 1 has no valid claim references; an earlier turn's citations do not cover its findings.
- Turn 1 was interrupted; its response or evidence record may be incomplete.

Evidence coverage checks recorded pointers and report references; it does not verify scientific correctness or external citations. Use `verify` below to also check artifact hashes.

## The analysis plan

**Goal:** Finish Round 2 B7-H3 case study from the verified resume point: complete cell2location panels 4E/S5B, spatial-neighborhood analysis, evidence-level scientific review of all panels, reviewer-driven recomputations, and final synthesis. Reuse the completed CPU cell2location outputs; do not retrain.

| Step | Specialist | Depends on | Task |
|---|---|---|---|
| `r1` | `single-cell-analyst` | — | Run diagnostics, 4E/S5B panel figures, k=6 spatial-neighborhood analysis, and write the vi… |
| `r2` | `scientific-reviewer` | r1 | Evidence-level review of panels 4A, 4B/4C, 4D/S5A, 4E/S5B, 4F by opening underlying data, … |
| `r3` | `single-cell-analyst` | r2 | Address any reviewer-required recomputations in the single-cell/spatial panels and re-file… |

Intended waves (steps in a wave may run concurrently): [r1] → [r2] → [r3]

**Planned vs actual:** 3 steps planned, 8 dispatches observed, 4 deviation(s) from the plan.

- *unplanned* — genomics-analyst ran but was not in the plan.
- *unplanned* — functional-genomics-analyst ran but was not in the plan.
- *out_of_order* — single-cell-analyst (step r3) started before scientific-reviewer (step r2), which it depends on.
- *missing_output* — Step r2 declared output 'work/scientific-reviewer/results/reports/review_round2.md', which this run never produced.

> Deviations are expected when a specialist's findings change what should happen next; they are recorded so the actual sequence is auditable, not to flag an error.

## How the analysis flowed

The CSO dispatched these specialists, in this order:

| # | Specialist | Started | Duration | Messages | Cost |
|---|---|---|---|---|---|
| 1 | `single-cell-analyst` | 20:45:27 | 9385.07s | 510 | $11.961 |
| 2 | `scientific-reviewer` | 23:26:54 | 437.63s | 208 | $1.979 |
| 3 | `single-cell-analyst` | 23:34:58 | 1361.42s | 558 | $13.472 |
| 4 | `genomics-analyst` | 23:59:01 | 513.91s | 225 | $5.142 |
| 5 | `functional-genomics-analyst` | 00:07:42 | 319.66s | 171 | $2.594 |
| 6 | `single-cell-analyst` | 00:13:12 | 812.31s | 346 | $8.724 |
| 7 | `scientific-reviewer` | 00:28:36 | 425.07s | 221 | $2.206 |
| 8 | `single-cell-analyst` | 00:35:50 | 378.84s | 203 | $4.306 |

<details><summary>Delegation prompts (what the CSO asked each specialist)</summary>

**`single-cell-analyst`**

```
You are finishing a resumed analysis (a prior session was killed by a transient API error, NOT a data/code problem). cell2location training and spatial mapping ALREADY COMPLETED SUCCESSFULLY on CPU. Do NOT retrain, re-map, or re-run LIANA/scRNA/TCGA — only complete the remaining deliverables for Panels 4E/S5B and the spatial-neighborhood analysis.

## Invoke the evidence-citation skill FIRST
Use the Skill tool to invoke `evidence-citation`, then follow it: write tables/figures before asserting, register every finding-bearing artifact with a one-line description via mcp__provenance__register_artifact, and cite artifact paths.

## Run directory (write here)
/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8
Work tree: <RUN>/work/single-cell-analyst/
Python: /home/xqinag/miniconda/envs/vbt/bin/python
Older source run (READ-ONLY; do not write there): /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35

## What is already done and verified (reuse, do not redo)
- Data: 22 LUAD Visium sections from ArrayExpress E-MTAB-13530 (De Zuani et al. Nat Commun 2024; the paper's actual source). 12 tumour (P10_T1-T4, P15_T1-T2, P16_T1-T2, P24_T1-T2, P25_T1-T2), 10 matched adjacent-normal (same patients, B1/B2). 47,448 QC-passed spots (tumour 27,826; adjacent-normal 19,622), 36,601 genes; QC was >=500 UMIs, >=200 genes, <=20% mito, a priori.
- cell2location reference: 384,806 LUAD+no
… [truncated]
```

**`scientific-reviewer`**

```
You are the scientific reviewer for a partly-completed Round-2 B7-H3 (CD276) lung-cancer case study. A prior interim review covered six panels; your job is (A) the full, evidence-level review of the remaining spatial work, and (B) a final live-run consistency audit. You are READ-ONLY on all data: do not run analysis scripts, do not re-query databases, do not modify any artifact outside your own report file.

## Run layout

LIVE (your write directory; all citations must be from here where possible):
`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`

SOURCE (read-only predecessor, contains upstream specialists' original work):
`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35`

An earlier interim review is at `LIVE/work/scientific-reviewer/scientific_review_interim_panels1-6.md`. Read it first. It covers Panel 4A, Panels 4B/4C, Panels 4D/S5A, Panel 4F, Tahoe-100M, and Visium ingest/QC. It explicitly EXCLUDED cell2location, Panel 4E, Panel S5B and the spatial-neighbourhood analysis — those are your primary scope. It also lists six consolidated required recomputations. **Verify whether any of them was applied:** no SOURCE file was modified after 2026-10-21 22:01, so they were almost certainly not. Confirm and report; then re-check whether any of the six defects materially changes a conclusion (not just an artifact).

## Data context

- Visium: ArrayExpress E-MTAB
… [truncated]
```

**`single-cell-analyst`**

```
You are revising completed spatial work in a Round-2 B7-H3 (CD276) lung-cancer case study after a full scientific review returned "revise and resubmit". The underlying computations were judged largely trustworthy — the failure is at the prose/table interface, plus several fixable script bugs. Do NOT retrain the reference model and do NOT re-run the cell2location spatial mapping; everything below can be fixed from existing outputs plus cheap table/plot regenerations.

## Working directory (write only here)
`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
Write only under `work/single-cell-analyst/`. Do not modify any other agent's directory.

Read-only predecessor (original inputs, upstream ingest scripts/logs, 4B/4C artifacts):
`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35`

## Read this first (the specification)
`work/scientific-reviewer/results/reports/review_round2_full.md` — especially Section 7 (Required recomputations), Section 9 (Bottom line), and Section 4 (live-run consistency). Read the whole thing; it is precise about file, script and column. Also read the earlier interim review `work/scientific-reviewer/scientific_review_interim_panels1-6.md` for items 1–6 in its consolidated list.

The report under revision: `work/single-cell-analyst/results/reports/visium_c2l_panels4e_s5b_report.md`.

## Fix list (verify each against the data yourself; do n
… [truncated]
```

**`genomics-analyst`**

```
You are correcting a completed Panel 4A (CD276 germline credible sets + ENCODE-rE2G) analysis after a scientific review. This is a fix-and-re-document task, not a new analysis. Work only in the LIVE run below.

LIVE (write here): `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8/work/genomics-analyst/`
SOURCE (read-only, contains the original raw ENCODE-rE2G input and any intermediates): `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/genomics-analyst/`

The full review is at `LIVE/../scientific-reviewer/results/reports/review_round2_full.md` (Section 4.2) and the interim review at `work/scientific-reviewer/scientific_review_interim_panels1-6.md` (Section 1). Read the Panel 4A sections of the interim review carefully.

The LIVE directory currently holds copies of the SOURCE report, tables, figures and scripts. Do not modify SOURCE.

## Fixes required

1. **G7 note is internally contradictory.** `results/tables/cd276_round2_germline_verification.csv` row G7 says "Sensitivity (locus-interval overlap): 69 all types / 65 GWAS", while `cd276_round2_credible_set_window_reconciliation.csv` computes 201 all types / 195 GWAS for gene-body locus-interval overlap. Determine which number is correct by recomputing from the underlying data (the SOURCE run's credible-set inputs are available; do not guess). Fix the G7 note, remove the hardcoded literal from `code/scri
… [truncated]
```

**`functional-genomics-analyst`**

```
You are correcting a completed Tahoe-100M / DepMap supplemental analysis after a scientific review. This is a documentation-accuracy task; do not re-run any downloads or large computations.

LIVE (write here): `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8/work/functional-genomics-analyst/`
SOURCE (read-only originals, if needed): `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/functional-genomics-analyst/`

The relevant review is `work/scientific-reviewer/scientific_review_interim_panels1-6.md`, Section 5 (Tahoe-100M) and the cross-panel failure-pattern note. Read those first.

## Fixes required

1. **Lung-line histology counts are off by one.** The report says "10 LUAD, 1 SCLC, 11 other NSCLC". `tahoe_lung_cell_lines_cd276_context.csv` actually lists **11 LUAD, 1 SCLC, 10 other** (9 "Other NSCLC" + SW 1271 "Other lung (SMARCA4-dUT)"). Recount from the CSV yourself, then correct every occurrence in `results/reports/tahoe_round2_status.md`.

2. **Remove the "NON-MATERIAL data gap" label.** The review's conclusion: this is a data-availability failure, not an effect-size judgement, and the DE question is *unassessed*. Replace "non-material" with "**not assessable / no evidence either way**" and leave the materiality judgement to the CSO. Also soften the sentence "the therapeutic assessment is independent of Tahoe" — it is a synthesis-level claim; state
… [truncated]
```

**`single-cell-analyst`**

```
You are correcting a completed LIANA Panels 4D/S5A report after a scientific review. The computations were judged sound; only specific prose and provenance statements need fixing. Do not re-run LIANA or any model.

LIVE (write here): `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8/work/single-cell-analyst/`
SOURCE (read-only originals): `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/single-cell-analyst/`

The report to correct is `results/reports/liana_panels4d_s5a_report.md` (a copy now exists in LIVE; the LIANA tables and figure are also copied). Read Section 3 of `work/scientific-reviewer/scientific_review_interim_panels1-6.md` first, then verify each correction against `results/tables/liana_pair_level_comparison_sclc.csv`, `liana_pair_level_comparison_luad.csv`, `liana_high_vs_low_differential_summary.csv`, `liana_caf_source_group_counts.csv`, `liana_filter_cascade.csv`, `liana_cascade_audit.csv`, `liana_caf_depth_audit.csv`, and `liana_run_log.csv`.

## Fixes required (report prose and, where noted, a small audit table)

1. **§4.3 CXCR3 is not in the data.** The report says "CXCL12 -> CXCR3/ITGA5/ITGAV". No CXCR3 interaction exists in either pair-level table. The actual low-group calls are CXCL12 -> ITGA5 (neutrophil), CXCL12 -> CD4 (T cell), CXCL12 -> ITGAV (mast cell). Correct the sentence with the actual pairs and their source groups.

2. **§
… [truncated]
```

**`scientific-reviewer`**

```
You are performing a targeted re-review after "revise and resubmit" on a Round-2 B7-H3 (CD276) lung-cancer case study. Your job is to verify that the required corrections were actually made and that no new errors were introduced, then issue a final verdict. You are READ-ONLY on all data; do not run analysis scripts or modify any artifact other than your own report.

Run root (LIVE): `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
Read-only source (SOURCE): `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35`

## Read first
1. `LIVE/work/scientific-reviewer/results/reports/review_round2_full.md` — your predecessor's full review (Sections 7 and 9 are the checklist).
2. `LIVE/work/scientific-reviewer/scientific_review_interim_panels1-6.md` — the six-panel interim review and its six consolidated recomputations.
3. The four revision-response files:
   - `LIVE/work/single-cell-analyst/results/reports/revision_response_to_reviewer.md` (spatial items 1–20, then a LIANA section)
   - `LIVE/work/genomics-analyst/results/reports/revision_response_to_reviewer.md`
   - `LIVE/work/functional-genomics-analyst/results/reports/revision_response_to_reviewer.md`
4. The revised reports themselves.

## What to verify

### A. Spatial arm (the 20 items in review_round2_full.md §7)
Open the revised `work/single-cell-analyst/results/reports/visium_c2l_panels4e_s5b_report.md` (Revisio
… [truncated]
```

**`single-cell-analyst`**

```
Apply a small set of final text/artifact corrections flagged by the re-review of your Revision 2 spatial report. Do not re-run any model; these are recomputation-from-existing-tables and text fixes only.

LIVE: `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8/work/single-cell-analyst/`
Re-review: `LIVE/../scientific-reviewer/results/reports/review_round2_rereview.md` (read Sections 1–3 and the item notes).

## Fixes

1. **Item 16 is NOT VERIFIED.** `results/tables/visium_c2l_mapping_history.csv` (one line, `epoch`) and `results/tables/c2l_reference_training_history.csv` (one line, `epoch`) still exist, but the revision response and `visium_c2l_mapping_history_README.md` (and report §3 line ~156) say they were deleted. Either delete those two files or amend the README/changelog to say exactly which files were removed and which remain. Also check `visium_c2l_21_map_sections_rerun.py`: it was documented as writing the history file only when non-empty; the guard apparently did not fire on an empty frame. Fix the guard so an empty history never produces a header-only CSV.

2. **Item 4 numbers do not reproduce.** The re-review recomputed from `visium_c2l_cd276_stratification_audit.csv`:
   - tumour median-of-per-section-medians: **7,545.0 / 3,708.5 (2.03x)**, not 7,337 / 3,676 (2.00x)
   - adjacent-normal: **2,388.0 / 2,083.75 (1.15x)**, not 2,326 / 1,945 (1.20x)
   - mean-of-means 9,164.2 / 5,211.2 (1.76x) reproduces.
   
… [truncated]
```

</details>

## What each agent produced

### Single Cell Analyst  ·  249 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/single-cell-analyst/code/scripts/00_profile_metadata.py` | code | 1.4 KB | — | — |
| `work/single-cell-analyst/code/scripts/01_liana_b7h3_caf_definition.py` | code | 7.9 KB | `call_00_livM15…` | — |
| `work/single-cell-analyst/code/scripts/01_make_batches.py` | code | 1.9 KB | — | — |
| `work/single-cell-analyst/code/scripts/02_inspect_raw.py` | code | 1.0 KB | — | — |
| `work/single-cell-analyst/code/scripts/02_liana_probe.py` | code | 2.4 KB | `call_01_d5zGIu…` | — |
| `work/single-cell-analyst/code/scripts/03_liana_run.py` | code | 9.3 KB | `call_02_7TZthK…` | — |
| `work/single-cell-analyst/code/scripts/03_merge_qc_downsample.py` | code | 8.8 KB | — | — |
| `work/single-cell-analyst/code/scripts/03b_merge_qc_downsample_instrumented.py` | code | 10.1 KB | — | — |
| `work/single-cell-analyst/code/scripts/03b_reconstruct_luad_run_log.py` | code | 3.5 KB | `call_00_MpqsOH…` | — |
| `work/single-cell-analyst/code/scripts/03c_restore_interrupted_run_log_rows.py` | code | 1.4 KB | `call_11_VBJsdH…` | — |
| `work/single-cell-analyst/code/scripts/04_liana_extract_compare.py` | code | 12.5 KB | `call_06_cEDsYf…` | — |
| `work/single-cell-analyst/code/scripts/04_write_batch_log.py` | code | 1.7 KB | — | — |
| `work/single-cell-analyst/code/scripts/04b_liana_cascade_audit.py` | code | 3.8 KB | `call_07_GUZpzk…` | — |
| `work/single-cell-analyst/code/scripts/04c_caf_depth_audit.py` | code | 5.8 KB | `call_03_qmYzeo…` | — |
| `work/single-cell-analyst/code/scripts/04e_liana_timeline_verification.py` | code | 4.6 KB | `call_05_cr4BIq…` | — |
| `work/single-cell-analyst/code/scripts/04f_liana_top_pairs.py` | code | 3.7 KB | `call_08_tmGCJp…` | — |
| `work/single-cell-analyst/code/scripts/04g_top_pair_gene_expression.py` | code | 3.5 KB | `call_04_KGMVss…` | — |
| `work/single-cell-analyst/code/scripts/05_integrate_annotate.py` | code | 7.7 KB | — | — |
| `work/single-cell-analyst/code/scripts/05_liana_figures.py` | code | 9.4 KB | `call_09_kx2I4z…` | — |
| `work/single-cell-analyst/code/scripts/06_liana_sensitivity_run.py` | code | 5.8 KB | `call_05_PywrRF…` | — |
| `work/single-cell-analyst/code/scripts/06_pseudobulk_de.py` | code | 9.4 KB | — | — |
| `work/single-cell-analyst/code/scripts/06a_de_testability.py` | code | 2.3 KB | — | — |
| `work/single-cell-analyst/code/scripts/06b_sensitivity_concordance.py` | code | 2.7 KB | — | — |
| `work/single-cell-analyst/code/scripts/06c_top_hit_sensitivity.py` | code | 2.4 KB | — | — |
| `work/single-cell-analyst/code/scripts/07_fig_de.py` | code | 5.4 KB | — | — |
| `work/single-cell-analyst/code/scripts/08_validate_atlas.py` | code | 3.6 KB | — | — |
| `work/single-cell-analyst/code/scripts/liana_revision2_caf_subtype_check.py` | code | 5.7 KB | `call_00_ET_8Tn…` | — |
| `work/single-cell-analyst/code/scripts/liana_revision2_presence.py` | code | 3.3 KB | `call_00_4T1Rxr…` | — |
| `work/single-cell-analyst/code/scripts/liana_revision2_subtype_probe.py` | code | 2.3 KB | `call_00_rTt5l4…` | — |
| `work/single-cell-analyst/code/scripts/liana_revision2_verify.py` | code | 3.1 KB | `call_00_Qmi8Gn…` | — |
| `work/single-cell-analyst/code/scripts/scrna_05_annotate_census_batch_log.py` | code | 4.9 KB | `call_00_OiGd0l…` | — |
| `work/single-cell-analyst/code/scripts/scrna_pseudobulk_de_top_genes_signfiltered.py` | code | 6.0 KB | `call_00_WaceBE…` | — |
| `work/single-cell-analyst/code/scripts/source_04_write_batch_log_reference.py` | code | 1.7 KB | `call_00_S2qCEk…` | — |
| `work/single-cell-analyst/code/scripts/visium_01_verify_extract.py` | code | 13.6 KB | `call_00_S2qCEk…` | — |
| `work/single-cell-analyst/code/scripts/visium_02_qc_combine.py` | code | 16.5 KB | `call_00_S2qCEk…` | — |
| `work/single-cell-analyst/code/scripts/visium_03_sdrf_metadata_integrity.py` | code | 7.4 KB | `call_00_hjqQVH…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_10_prep_reference.py` | code | 6.6 KB | — | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_11_benchmark.py` | code | 2.3 KB | — | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_20_train_reference.py` | code | 5.0 KB | `call_00_kZNG2Y…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_21_map_sections.py` | code | 8.6 KB | `call_01_VH8Mti…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_21_map_sections_rerun.py` | code | 9.2 KB | `call_00_ET_8Jh…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_21b_api_smoke_test.py` | code | 2.3 KB | — | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_22_export_probe.py` | code | 3.8 KB | `call_00_y09Juf…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_30_neighborhood_analysis.py` | code | 17.3 KB | `call_01_gYAfdl…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_31_neighborhood_composition_sensitivity.py` | code | 9.3 KB | `call_00_ho2o1B…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_32_neighborhood_composition_pp.py` | code | 12.2 KB | `call_00_jqs0qa…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_40_panels.py` | code | 9.2 KB | `call_00_ET_R3M…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_41_neighborhood_figures.py` | code | 7.7 KB | `call_00_lkFe3d…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_42_diagnostics.py` | code | 9.4 KB | `call_02_f8EM3X…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_43_cd276_stratification_audit.py` | code | 5.2 KB | `call_02_cPDQeQ…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_44_multiple_testing.py` | code | 6.2 KB | `call_01_DY0TWq…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_45_append_revision2_log.py` | code | 6.2 KB | `call_00_rKJBEl…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_46_depth_balance_summary.py` | code | 6.0 KB | `call_00_ET_lrN…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_47_append_revision21_log.py` | code | 1.7 KB | `call_00_Yo7jVh…` | — |
| `work/single-cell-analyst/code/scripts/visium_c2l_common.py` | code | 2.7 KB | `call_00_ET_Ykm…` | — |
| `work/single-cell-analyst/data/processed/deprecated_all_nan_export/visium_c2l_abundances_small_all_nan_superseded.h5ad` | data | 3.1 MB | `call_00_GETJ4h…` | — |
| `work/single-cell-analyst/data/processed/visium_c2l_abundances_small.h5ad` | data | 7.6 MB | `call_00_RPjahW…` | — |
| `work/single-cell-analyst/data/processed/visium_sections_qc.h5ad` | data | 429.5 MB | `call_00_SOUjk3…` | — |
| `work/single-cell-analyst/logs/synthetic_test/visium_c2l_abundances_small_SYNTHETIC.h5ad` | data | 12.7 MB | `call_00_ET_KOo…` | — |
| `work/single-cell-analyst/results/tables/liana_PROBE_meta.json` | data | 357 B | — | — |
| `work/single-cell-analyst/results/tables/liana_b7h3_caf_definition_meta.json` | data | 752 B | — | — |
| `work/single-cell-analyst/results/tables/liana_sensitivity_luad_meta.json` | data | 572 B | — | — |
| `work/single-cell-analyst/results/tables/liana_sensitivity_sclc_meta.json` | data | 567 B | — | — |
| `work/single-cell-analyst/logs/synthetic_test/figures/fig4e_c2l_tumor.pdf` | figure | 549.4 KB | `call_00_ET_fdF…` | — |
| `work/single-cell-analyst/logs/synthetic_test/figures/fig4e_c2l_tumor.png` | figure | 2.6 MB | `call_00_ET_fdF…` | — |
| `work/single-cell-analyst/logs/synthetic_test/figures/fig4e_neighborhood_immune_change.pdf` | figure | 41.4 KB | `call_00_ET_Lzr…` | — |
| `work/single-cell-analyst/logs/synthetic_test/figures/fig4e_neighborhood_immune_change.png` | figure | 306.2 KB | `call_00_ET_Lzr…` | — |
| `work/single-cell-analyst/logs/synthetic_test/figures/figs5b_c2l_adjacent_normal.pdf` | figure | 453.6 KB | `call_00_ET_fdF…` | — |
| `work/single-cell-analyst/logs/synthetic_test/figures/figs5b_c2l_adjacent_normal.png` | figure | 2.0 MB | `call_00_ET_fdF…` | — |
| `work/single-cell-analyst/logs/synthetic_test/figures/figs5b_neighborhood_immune_change.pdf` | figure | 41.7 KB | `call_00_ET_Lzr…` | — |
| `work/single-cell-analyst/logs/synthetic_test/figures/figs5b_neighborhood_immune_change.png` | figure | 313.5 KB | `call_00_ET_Lzr…` | — |
| `work/single-cell-analyst/results/figures/caf_b7h3_detection_depth_audit.png` | figure | 143.3 KB | — | — |
| `work/single-cell-analyst/results/figures/fig4b_umap_luad_sclc.pdf` | figure | 26.7 MB | — | — |
| `work/single-cell-analyst/results/figures/fig4b_umap_luad_sclc.png` | figure | 4.9 MB | — | — |
| `work/single-cell-analyst/results/figures/fig4c_pseudobulk_de_luad_sclc.pdf` | figure | 87.8 KB | — | — |
| `work/single-cell-analyst/results/figures/fig4c_pseudobulk_de_luad_sclc.png` | figure | 817.6 KB | — | — |
| `work/single-cell-analyst/results/figures/fig4d_liana_sclc_caf_b7h3.pdf` | figure | 38.5 KB | — | — |
| `work/single-cell-analyst/results/figures/fig4d_liana_sclc_caf_b7h3.png` | figure | 452.9 KB | — | — |
| `work/single-cell-analyst/results/figures/fig4e_c2l_tumor.pdf` | figure | 512.9 KB | `call_00_ET_1t7…` | — |
| `work/single-cell-analyst/results/figures/fig4e_c2l_tumor.png` | figure | 2.6 MB | `call_00_ET_1t7…` | — |
| `work/single-cell-analyst/results/figures/fig4e_neighborhood_immune_change.pdf` | figure | 42.4 KB | `call_00_2AR3qr…` | — |
| `work/single-cell-analyst/results/figures/fig4e_neighborhood_immune_change.png` | figure | 454.9 KB | `call_00_2AR3qr…` | — |
| `work/single-cell-analyst/results/figures/figs5_c2l_training_convergence.png` | figure | 204.5 KB | `call_00_OBCJ6G…` | — |
| `work/single-cell-analyst/results/figures/figs5a_liana_luad_caf_b7h3.pdf` | figure | 37.1 KB | — | — |
| `work/single-cell-analyst/results/figures/figs5a_liana_luad_caf_b7h3.png` | figure | 449.6 KB | — | — |
| `work/single-cell-analyst/results/figures/figs5b_c2l_adjacent_normal.pdf` | figure | 431.3 KB | `call_00_ET_1t7…` | — |
| `work/single-cell-analyst/results/figures/figs5b_c2l_adjacent_normal.png` | figure | 2.0 MB | `call_00_ET_1t7…` | — |
| `work/single-cell-analyst/results/figures/figs5b_neighborhood_immune_change.pdf` | figure | 42.4 KB | `call_00_2AR3qr…` | — |
| `work/single-cell-analyst/results/figures/figs5b_neighborhood_immune_change.png` | figure | 361.0 KB | `call_00_2AR3qr…` | — |
| `work/single-cell-analyst/results/figures/visium_qc_inventory_table.png` | figure | 85.8 KB | — | — |
| `work/single-cell-analyst/results/figures/visium_qc_metrics_by_section.png` | figure | 74.8 KB | — | — |
| `work/single-cell-analyst/results/figures/visium_qc_raw_vs_retained.png` | figure | 39.6 KB | — | — |
| `work/single-cell-analyst/results/figures/visium_qc_spatial_retained_example.png` | figure | 55.0 KB | — | — |
| `work/single-cell-analyst/logs/c2l_benchmark.log` | log | 2.2 KB | — | — |
| `work/single-cell-analyst/logs/c2l_cd276_stratification_audit_rerun.log` | log | 3.3 KB | `call_00_CzHQaQ…` | — |
| `work/single-cell-analyst/logs/c2l_diagnostics_rerun.log` | log | 2.8 KB | `call_00_OBCJ6G…` | — |
| `work/single-cell-analyst/logs/c2l_diagnostics_run.log` | log | 2.8 KB | `call_00_xKkmJo…` | — |
| `work/single-cell-analyst/logs/c2l_env_setup.log` | log | 1.4 KB | — | — |
| `work/single-cell-analyst/logs/c2l_export_probe.log` | log | 7.7 KB | `call_00_ET_KSV…` | — |
| `work/single-cell-analyst/logs/c2l_mapping_benchmark.log` | log | 2.4 KB | — | — |
| `work/single-cell-analyst/logs/c2l_mapping_full.log` | log | 8.1 KB | — | — |
| `work/single-cell-analyst/logs/c2l_mapping_rerun.log` | log | 7.9 KB | `call_00_RPjahW…` | — |
| `work/single-cell-analyst/logs/c2l_mapping_smoke_test.log` | log | 3.1 KB | — | — |
| `work/single-cell-analyst/logs/c2l_multiple_testing.log` | log | 5.2 KB | `call_00_ET_zO1…` | — |
| `work/single-cell-analyst/logs/c2l_multiple_testing_rerun.log` | log | 5.2 KB | `call_00_ET_iNm…` | — |
| `work/single-cell-analyst/logs/c2l_neighborhood_composition_pp.log` | log | 10.7 KB | `call_00_ET_NgV…` | — |
| `work/single-cell-analyst/logs/c2l_neighborhood_composition_pp_rerun.log` | log | 12.4 KB | `call_00_1tKNPj…` | — |
| `work/single-cell-analyst/logs/c2l_neighborhood_composition_sensitivity.log` | log | 6.1 KB | `call_00_YgmRGM…` | — |
| `work/single-cell-analyst/logs/c2l_neighborhood_composition_sensitivity_rerun.log` | log | 6.9 KB | `call_00_KtnBM7…` | — |
| `work/single-cell-analyst/logs/c2l_neighborhood_figures.log` | log | 84 B | `call_00_9Y9iZU…` | — |
| `work/single-cell-analyst/logs/c2l_neighborhood_figures_rerun.log` | log | 84 B | `call_00_2AR3qr…` | — |
| `work/single-cell-analyst/logs/c2l_neighborhood_full.log` | log | 9.2 KB | `call_00_OA0P99…` | — |
| `work/single-cell-analyst/logs/c2l_neighborhood_full_rerun.log` | log | 9.2 KB | `call_00_ET_9xS…` | — |
| `work/single-cell-analyst/logs/c2l_neighborhood_probe20.log` | log | 9.2 KB | `call_00_IxirN0…` | — |
| `work/single-cell-analyst/logs/c2l_panels_rerun.log` | log | 3.8 KB | `call_00_ET_1t7…` | — |
| `work/single-cell-analyst/logs/c2l_panels_run.log` | log | 3.8 KB | `call_00_HoWjqq…` | — |
| `work/single-cell-analyst/logs/c2l_reference_train.log` | log | 3.2 KB | — | — |
| `work/single-cell-analyst/logs/liana_probe.log` | log | 3.6 KB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/logs/liana_revision2_04b_rerun.log` | log | 1.6 KB | `call_00_aL1gH7…` | — |
| `work/single-cell-analyst/logs/liana_revision2_04e_rerun.log` | log | 2.0 KB | `call_00_aL1gH7…` | — |
| `work/single-cell-analyst/logs/liana_revision2_04f_rerun.log` | log | 2.8 KB | `call_00_aL1gH7…` | — |
| `work/single-cell-analyst/logs/liana_revision2_caf_subtype_check.log` | log | 2.2 KB | `call_00_ET_wBx…` | — |
| `work/single-cell-analyst/logs/liana_revision2_presence.log` | log | 4.6 KB | `call_00_ET_ygC…` | — |
| `work/single-cell-analyst/logs/liana_revision2_subtype_probe.log` | log | 4.9 KB | `call_00_ET_5HY…` | — |
| `work/single-cell-analyst/logs/liana_revision2_verify.log` | log | 70.6 KB | `call_00_auZl2x…` | — |
| `work/single-cell-analyst/logs/liana_run_LUAD_main.log` | log | 5.7 KB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/logs/liana_run_SCLC_benchmark50.log` | log | 4.4 KB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/logs/liana_run_SCLC_main.log` | log | 6.3 KB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/logs/liana_sensitivity_LUAD.log` | log | 4.6 KB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/logs/liana_sensitivity_SCLC.log` | log | 4.6 KB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/logs/scrna_census_batch_log_annotation.log` | log | 533 B | `call_00_ET_O1g…` | — |
| `work/single-cell-analyst/logs/scrna_pseudobulk_de_top_genes_signfiltered.log` | log | 3.7 KB | `call_00_7ZFW64…` | — |
| `work/single-cell-analyst/logs/sdrf_metadata_integrity.log` | log | 1.4 KB | `call_00_ET_oDe…` | — |
| `work/single-cell-analyst/logs/synthetic_test/neighborhood_figures_synthetic.log` | log | 84 B | `call_00_ET_Lzr…` | — |
| `work/single-cell-analyst/logs/synthetic_test/neighborhood_synthetic.log` | log | 9.2 KB | `call_00_AzsWSq…` | — |
| `work/single-cell-analyst/logs/synthetic_test/panels_synthetic.log` | log | 3.8 KB | `call_00_ET_fdF…` | — |
| `work/single-cell-analyst/logs/visium_01_run.log` | log | 8.1 KB | `call_00_S2qCEk…` | — |
| `work/single-cell-analyst/logs/visium_01_verify_extract.log` | log | 8.1 KB | `call_00_S2qCEk…` | — |
| `work/single-cell-analyst/logs/visium_02_qc_combine.log` | log | 3.4 KB | `call_00_S2qCEk…` | — |
| `work/single-cell-analyst/logs/visium_02_run.log` | log | 3.4 KB | `call_00_S2qCEk…` | — |
| `work/single-cell-analyst/data/processed/c2l_mapping_model_rerun/model.pt` | other | 26.3 MB | `call_00_RPjahW…` | — |
| `work/single-cell-analyst/data/processed/deprecated_all_nan_export/MANIFEST.md` | report | 3.6 KB | `call_00_9aEOlu…` | — |
| `work/single-cell-analyst/logs/c2l_compute_and_api_log.md` | report | 3.3 KB | — | — |
| `work/single-cell-analyst/logs/synthetic_test/README.md` | report | 2.2 KB | `call_00_gs3rjM…` | — |
| `work/single-cell-analyst/logs/test_write.txt` | report | 0 B | `call_00_2UAmT5…` | — |
| `work/single-cell-analyst/results/reports/liana_panels4d_s5a_report.md` | report | 37.0 KB | `call_00_2C3fmY…` | — |
| `work/single-cell-analyst/results/reports/revision_response_to_reviewer.md` | report | 15.5 KB | `call_00_DllKkN…` | — |
| `work/single-cell-analyst/results/reports/scrna_panels4bc_report.md` | report | 11.8 KB | — | — |
| `work/single-cell-analyst/results/reports/visium_c2l_panels4e_s5b_report.md` | report | 44.8 KB | `call_00_ClP1Tw…` | — |
| `work/single-cell-analyst/results/reports/visium_ingest_qc_log.md` | report | 13.4 KB | `call_00_lHuEpu…` | — |
| `work/single-cell-analyst/results/tables/visium_c2l_mapping_history_README.md` | report | 2.7 KB | `call_00_qRJSDA…` | — |
| `work/single-cell-analyst/data/processed/deprecated_all_nan_export/visium_c2l_spot_abundances_all_nan_superseded.parquet` | table | 904.4 KB | `call_00_GETJ4h…` | — |
| `work/single-cell-analyst/logs/c2l_export_probe_finiteness.csv` | table | 767 B | `call_00_ET_KSV…` | — |
| `work/single-cell-analyst/logs/c2l_mapping_elbo_metrics_3000epoch.csv` | table | 65.4 KB | `call_00_vclpBn…` | — |
| `work/single-cell-analyst/logs/lightning/c2l_mapping_rerun/3000ep/metrics.csv` | table | 65.4 KB | `call_00_RNOjaw…` | — |
| `work/single-cell-analyst/logs/synthetic_test/visium_c2l_section_summary.csv` | table | 8.4 KB | `call_00_ET_fdF…` | — |
| `work/single-cell-analyst/logs/synthetic_test/visium_c2l_spot_abundances_SYNTHETIC.parquet` | table | 13.6 MB | `call_00_AzsWSq…` | — |
| `work/single-cell-analyst/logs/synthetic_test/visium_neighborhood_edge_spot_sensitivity_synthetic.csv` | table | 1.3 KB | `call_00_AzsWSq…` | — |
| `work/single-cell-analyst/logs/synthetic_test/visium_neighborhood_immune_change.csv` | table | 33.7 KB | `call_00_ET_Lzr…` | — |
| `work/single-cell-analyst/logs/synthetic_test/visium_neighborhood_immune_change_synthetic.csv` | table | 33.7 KB | `call_00_AzsWSq…` | — |
| `work/single-cell-analyst/logs/synthetic_test/visium_neighborhood_robustness.csv` | table | 10.8 KB | `call_00_ET_Lzr…` | — |
| `work/single-cell-analyst/logs/synthetic_test/visium_neighborhood_robustness_synthetic.csv` | table | 10.8 KB | `call_00_AzsWSq…` | — |
| `work/single-cell-analyst/logs/synthetic_test/visium_neighborhood_stratification_synthetic.csv` | table | 4.1 KB | `call_00_AzsWSq…` | — |
| `work/single-cell-analyst/results/tables/c2l_reference_celltype_signatures_mean.csv` | table | 345.2 KB | `call_00_YOzeJZ…` | — |
| `work/single-cell-analyst/results/tables/c2l_reference_celltype_signatures_q05.csv` | table | 350.4 KB | `call_00_YOzeJZ…` | — |
| `work/single-cell-analyst/results/tables/c2l_reference_signature_marker_check.csv` | table | 1.1 KB | — | — |
| `work/single-cell-analyst/results/tables/c2l_reference_training_history.csv` | table | 6 B | — | — |
| `work/single-cell-analyst/results/tables/liana_PROBE_sca20_perms.csv` | table | 3.7 MB | — | — |
| `work/single-cell-analyst/results/tables/liana_b7h3_caf_definition.csv` | table | 5.7 KB | — | — |
| `work/single-cell-analyst/results/tables/liana_b7h3_caf_definition_by_donor.csv` | table | 5.0 KB | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_b7h3_group_composition_by_dataset.csv` | table | 252 B | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_b7h3_luad_s5a.csv` | table | 2.6 MB | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_b7h3_luad_sens_a.csv` | table | 2.8 MB | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_b7h3_sclc_4d.csv` | table | 2.2 MB | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_b7h3_sclc_sens_a.csv` | table | 2.2 MB | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_depth_audit.csv` | table | 751 B | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_depth_by_donor.csv` | table | 4.0 KB | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_source_group_counts.csv` | table | 154 B | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_source_group_counts_sens_a.csv` | table | 154 B | — | — |
| `work/single-cell-analyst/results/tables/liana_caf_subtype_check.csv` | table | 20.3 KB | `call_00_ET_wBx…` | — |
| `work/single-cell-analyst/results/tables/liana_caf_subtype_check_tests.csv` | table | 244 B | `call_00_ET_wBx…` | — |
| `work/single-cell-analyst/results/tables/liana_cascade_audit.csv` | table | 669 B | `call_00_aL1gH7…` | — |
| `work/single-cell-analyst/results/tables/liana_cxcl12_pairs.csv` | table | 14.4 KB | `call_00_ET_ygC…` | — |
| `work/single-cell-analyst/results/tables/liana_differential_composition.csv` | table | 462 B | `call_00_aL1gH7…` | — |
| `work/single-cell-analyst/results/tables/liana_filter_cascade.csv` | table | 689 B | — | — |
| `work/single-cell-analyst/results/tables/liana_filter_cascade_sens_a.csv` | table | 686 B | — | — |
| `work/single-cell-analyst/results/tables/liana_high_vs_low_differential_summary.csv` | table | 321 B | — | — |
| `work/single-cell-analyst/results/tables/liana_high_vs_low_differential_summary_sens_a.csv` | table | 453 B | — | — |
| `work/single-cell-analyst/results/tables/liana_pair_level_comparison_luad.csv` | table | 1.3 MB | — | — |
| `work/single-cell-analyst/results/tables/liana_pair_level_comparison_luad_sens_a.csv` | table | 1.4 MB | — | — |
| `work/single-cell-analyst/results/tables/liana_pair_level_comparison_sclc.csv` | table | 1.1 MB | — | — |
| `work/single-cell-analyst/results/tables/liana_pair_level_comparison_sclc_sens_a.csv` | table | 1.1 MB | — | — |
| `work/single-cell-analyst/results/tables/liana_pair_status_counts.csv` | table | 178 B | `call_00_ET_ygC…` | — |
| `work/single-cell-analyst/results/tables/liana_pre_registered_filters.csv` | table | 2.0 KB | — | — |
| `work/single-cell-analyst/results/tables/liana_raw_luad.parquet` | table | 2.1 MB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/results/tables/liana_raw_luad_sens_a.parquet` | table | 2.2 MB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/results/tables/liana_raw_sclc.parquet` | table | 1.4 MB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/results/tables/liana_raw_sclc_sens_a.parquet` | table | 1.4 MB | `call_00_tbLFzz…` | — |
| `work/single-cell-analyst/results/tables/liana_run_log.csv` | table | 4.1 KB | — | — |
| `work/single-cell-analyst/results/tables/liana_sensitivity_concordance.csv` | table | 975 B | — | — |
| `work/single-cell-analyst/results/tables/liana_timeline_verification.csv` | table | 3.4 KB | `call_00_aL1gH7…` | — |
| `work/single-cell-analyst/results/tables/liana_top_differential_pairs.csv` | table | 10.0 KB | `call_00_aL1gH7…` | — |
| `work/single-cell-analyst/results/tables/liana_top_hits_primary_vs_sens_a.csv` | table | 8.8 KB | — | — |
| `work/single-cell-analyst/results/tables/liana_top_pair_gene_expression.csv` | table | 3.9 KB | — | — |
| `work/single-cell-analyst/results/tables/scrna_atlas_validation.csv` | table | 395 B | — | — |
| `work/single-cell-analyst/results/tables/scrna_cd276_de_summary.csv` | table | 2.5 KB | `call_00_7ZFW64…` | — |
| `work/single-cell-analyst/results/tables/scrna_cd276_expression_by_celltype.csv` | table | 4.0 KB | `call_00_S2qCEk…` | — |
| `work/single-cell-analyst/results/tables/scrna_cell_donor_audit.csv` | table | 3.7 KB | — | — |
| `work/single-cell-analyst/results/tables/scrna_cell_donor_audit_stage1_v2.csv` | table | 2.2 KB | — | — |
| `work/single-cell-analyst/results/tables/scrna_celltype_marker_validation.csv` | table | 3.6 KB | — | — |
| `work/single-cell-analyst/results/tables/scrna_census_batch_log.csv` | table | 3.9 KB | `call_00_ET_O1g…` | — |
| `work/single-cell-analyst/results/tables/scrna_dataset_inventory.csv` | table | 4.1 KB | — | — |
| `work/single-cell-analyst/results/tables/scrna_de_testability_by_celltype.csv` | table | 1.6 KB | — | — |
| `work/single-cell-analyst/results/tables/scrna_donor_downsampling_report.csv` | table | 2.6 KB | — | — |
| `work/single-cell-analyst/results/tables/scrna_donor_downsampling_report_v2.csv` | table | 2.6 KB | — | — |
| `work/single-cell-analyst/results/tables/scrna_harmony_validation.csv` | table | 197 B | — | — |
| `work/single-cell-analyst/results/tables/scrna_pseudobulk_de_luad_sclc.csv` | table | 109.1 MB | — | — |
| `work/single-cell-analyst/results/tables/scrna_pseudobulk_de_sample_summary.csv` | table | 2.8 KB | — | — |
| `work/single-cell-analyst/results/tables/scrna_pseudobulk_de_top_genes.csv` | table | 60.3 KB | `call_00_7ZFW64…` | — |
| `work/single-cell-analyst/results/tables/visium_barcode_matching.csv` | table | 1.1 KB | — | — |
| `work/single-cell-analyst/results/tables/visium_c2l_abundance_sanity.csv` | table | 599 B | `call_00_OBCJ6G…` | — |
| `work/single-cell-analyst/results/tables/visium_c2l_cd276_stratification_audit.csv` | table | 5.0 KB | `call_00_CzHQaQ…` | — |
| `work/single-cell-analyst/results/tables/visium_c2l_depth_balance_summary.csv` | table | 2.6 KB | `call_00_ET_U09…` | — |
| `work/single-cell-analyst/results/tables/visium_c2l_mapping_history.csv` | table | 6 B | — | — |
| `work/single-cell-analyst/results/tables/visium_c2l_mapping_history_rerun.csv` | table | 6 B | `call_00_RNOjaw…` | — |
| `work/single-cell-analyst/results/tables/visium_c2l_reference_gene_selection.csv` | table | 354 B | — | — |
| `work/single-cell-analyst/results/tables/visium_c2l_reference_preparation.csv` | table | 910 B | — | — |
| `work/single-cell-analyst/results/tables/visium_c2l_run_log.csv` | table | 15.7 KB | `call_00_ET_hh9…` | — |
| `work/single-cell-analyst/results/tables/visium_c2l_section_summary.csv` | table | 5.6 KB | `call_00_ET_1t7…` | — |
| `work/single-cell-analyst/results/tables/visium_c2l_signature_genes_missing_from_visium.csv` | table | 710 B | `call_00_YxnGiE…` | — |
| `work/single-cell-analyst/results/tables/visium_c2l_spot_abundances.parquet` | table | 8.5 MB | `call_00_RPjahW…` | — |
| `work/single-cell-analyst/results/tables/visium_c2l_training_convergence.csv` | table | 1.2 KB | `call_00_OBCJ6G…` | — |
| `work/single-cell-analyst/results/tables/visium_file_verification.csv` | table | 3.7 KB | — | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_composition_pp_difference.csv` | table | 13.0 KB | `call_00_ET_iNm…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_composition_sensitivity.csv` | table | 12.4 KB | `call_00_ET_iNm…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_edge_spot_sensitivity.csv` | table | 1.7 KB | `call_00_ET_9xS…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_edge_spot_sensitivity_probe20.csv` | table | 1.3 KB | `call_00_IxirN0…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_immune_change.csv` | table | 33.8 KB | `call_00_ET_9xS…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_immune_change_probe20.csv` | table | 33.8 KB | `call_00_IxirN0…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_multiple_testing_summary.csv` | table | 2.6 KB | `call_00_ET_iNm…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_robustness.csv` | table | 13.2 KB | `call_00_ET_iNm…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_robustness_probe20.csv` | table | 10.6 KB | `call_00_IxirN0…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_stratification.csv` | table | 4.1 KB | `call_00_ET_9xS…` | — |
| `work/single-cell-analyst/results/tables/visium_neighborhood_stratification_probe20.csv` | table | 4.1 KB | `call_00_IxirN0…` | — |
| `work/single-cell-analyst/results/tables/visium_qc_threshold_sensitivity.csv` | table | 253 B | — | — |
| `work/single-cell-analyst/results/tables/visium_sdrf_age_stage_integrity.csv` | table | 5.8 KB | `call_00_ET_oDe…` | — |
| `work/single-cell-analyst/results/tables/visium_sdrf_age_stage_patient_summary.csv` | table | 516 B | `call_00_ET_oDe…` | — |
| `work/single-cell-analyst/results/tables/visium_section_qc_inventory.csv` | table | 2.4 KB | — | — |
| `work/single-cell-analyst/results/tables/visium_spot_qc_metrics.csv` | table | 7.4 MB | `call_00_S2qCEk…` | — |

### Scientific Reviewer  ·  3 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/scientific-reviewer/results/reports/review_round2_full.md` | report | 39.3 KB | `call_00_MlhIEe…` | — |
| `work/scientific-reviewer/results/reports/review_round2_rereview.md` | report | 27.9 KB | `call_00_ET_mB1…` | — |
| `work/scientific-reviewer/scientific_review_interim_panels1-6.md` | report | 34.9 KB | — | — |

### Clinical Trialist  ·  21 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/clinical-trialist/code/scripts/01_import_mcp_clinical.py` | code | 1.9 KB | — | — |
| `work/clinical-trialist/code/scripts/02_inventory_endpoints.py` | code | 3.0 KB | — | — |
| `work/clinical-trialist/code/scripts/03_pull_cd276_expression.py` | code | 3.2 KB | — | — |
| `work/clinical-trialist/code/scripts/04_build_cohort.py` | code | 8.2 KB | — | — |
| `work/clinical-trialist/code/scripts/05_cox_models.py` | code | 7.5 KB | — | — |
| `work/clinical-trialist/code/scripts/06_figure4f.py` | code | 6.9 KB | — | — |
| `work/clinical-trialist/code/scripts/07_expression_summary.py` | code | 1.5 KB | — | — |
| `work/clinical-trialist/code/scripts/08_alternative_study_expression_counts.py` | code | 1.9 KB | — | — |
| `work/clinical-trialist/results/figures/fig4f_tcga_luad_cd276_survival.pdf` | figure | 49.3 KB | — | — |
| `work/clinical-trialist/results/figures/fig4f_tcga_luad_cd276_survival.png` | figure | 326.9 KB | — | — |
| `work/clinical-trialist/results/reports/tcga_luad_cd276_survival_report.md` | report | 12.9 KB | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_alternative_study_cd276_counts.csv` | table | 376 B | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_cd276_cox_models.csv` | table | 16.7 KB | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_cd276_expression_quartiles.csv` | table | 55.1 KB | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_cd276_expression_summary.csv` | table | 519 B | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_cd276_logrank.csv` | table | 180 B | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_cd276_quartile_event_counts.csv` | table | 617 B | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_clinical_endpoint_inventory.csv` | table | 456 B | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_cohort_construction.csv` | table | 1.4 KB | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_median_followup.csv` | table | 152 B | — | — |
| `work/clinical-trialist/results/tables/tcga_luad_tool_call_log.csv` | table | 2.3 KB | — | — |

### Functional Genomics Analyst  ·  36 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/functional-genomics-analyst/code/scripts/audit_tahoe_drug_targets_annotation.py` | code | 1.8 KB | `call_00_Bz8wWQ…` | — |
| `work/functional-genomics-analyst/code/scripts/recount_tahoe_lung_histology.py` | code | 1.6 KB | `call_00_uqkKeJ…` | — |
| `work/functional-genomics-analyst/code/scripts/tahoe_metadata_representation_analysis.py` | code | 8.0 KB | `call_00_6hZsTz…` | — |
| `work/functional-genomics-analyst/code/scripts/tahoe_round2_probe.py` | code | 5.5 KB | `call_01_A8RYfS…` | — |
| `work/functional-genomics-analyst/code/scripts/verify_round1_depmap.py` | code | 7.2 KB | `call_02_VrS4Ow…` | — |
| `work/functional-genomics-analyst/data/processed/tahoe_environment_diagnostic.json` | data | 2.1 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/cd276_depmap_essentiality_raw.json` | data | 178.4 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/tables/cd276_tahoe_query_status.json` | data | 2.2 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/results/tables/tahoe_metadata_scope_summary.json` | data | 1.3 KB | `call_00_20qGNC…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/figures/cd276_depmap_luad_sclc_distribution.pdf` | figure | 57.5 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/figures/cd276_depmap_luad_sclc_distribution.png` | figure | 318.9 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/results/figures/tahoe_lung_lines_cd276_expression.png` | figure | 101.5 KB | `call_00_20qGNC…` | — |
| `work/functional-genomics-analyst/logs/metadata_analysis_rerun.log` | log | 1.3 KB | `call_00_20qGNC…` | — |
| `work/functional-genomics-analyst/results/reports/revision_response_to_reviewer.md` | report | 5.4 KB | `call_00_qE4YI8…` | — |
| `work/functional-genomics-analyst/results/reports/tahoe_round2_status.md` | report | 15.5 KB | `call_00_sXkPbX…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/tables/cd276_depmap_all_cell_lines_annotated.csv` | table | 160.7 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/tables/cd276_depmap_broad_label_sensitivity.csv` | table | 621 B | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/tables/cd276_depmap_disease_comparator.csv` | table | 4.4 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/tables/cd276_depmap_gene_effect_bins.csv` | table | 1.1 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/tables/cd276_depmap_group_comparisons.csv` | table | 972 B | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/tables/cd276_depmap_group_summary.csv` | table | 2.1 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/tables/cd276_depmap_luad_sclc.csv` | table | 9.4 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/round1_depmap_inputs/tables/cd276_histology_mapping.csv` | table | 107.7 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/tahoe_de_shard_inventory.csv` | table | 83.2 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/tahoe_metadata/metadata/cell_line_metadata.parquet` | table | 18.6 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/tahoe_metadata/metadata/drug_metadata.parquet` | table | 39.5 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/tahoe_metadata/metadata/gene_metadata.parquet` | table | 1.3 MB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/data/raw/tahoe_metadata/metadata/sample_metadata.parquet` | table | 64.1 KB | `call_00_P0mMku…` | — |
| `work/functional-genomics-analyst/results/tables/round1_depmap_recomputed_group_summary.csv` | table | 855 B | `call_00_xyPTYY…` | — |
| `work/functional-genomics-analyst/results/tables/round1_depmap_verification.csv` | table | 3.2 KB | `call_00_xyPTYY…` | — |
| `work/functional-genomics-analyst/results/tables/tahoe_cell_lines_cd276_context.csv` | table | 6.5 KB | `call_00_20qGNC…` | — |
| `work/functional-genomics-analyst/results/tables/tahoe_drug_panel_b7h3_check.csv` | table | 223 B | `call_00_20qGNC…` | — |
| `work/functional-genomics-analyst/results/tables/tahoe_drug_targets_annotation_audit.csv` | table | 157 B | `call_00_ET_npp…` | — |
| `work/functional-genomics-analyst/results/tables/tahoe_lung_cell_lines_cd276_context.csv` | table | 1.4 KB | `call_00_20qGNC…` | — |
| `work/functional-genomics-analyst/results/tables/tahoe_lung_histology_recount.csv` | table | 174 B | `call_00_ET_JCV…` | — |
| `work/functional-genomics-analyst/results/tables/tahoe_round2_attempt_log.csv` | table | 4.9 KB | — | — |

### Genomics Analyst  ·  35 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/genomics-analyst/code/scripts/01_verify_germline_cd276.py` | code | 18.8 KB | `call_00_ET_axA…` | — |
| `work/genomics-analyst/code/scripts/02_parse_encode_re2g_cd276.py` | code | 17.5 KB | `call_00_ET_2Kl…` | — |
| `work/genomics-analyst/code/scripts/03_fig4a_genetics_e2g_cd276.py` | code | 11.4 KB | `call_00_iG4v6z…` | — |
| `work/genomics-analyst/code/scripts/04_validate_panel4a_outputs.py` | code | 8.4 KB | `call_00_BulKEB…` | — |
| `work/genomics-analyst/code/scripts/05_trait_label_audit_cd276.py` | code | 4.9 KB | `call_00_YaZF1k…` | — |
| `work/genomics-analyst/results/figures/fig4a_genetics_e2g_cd276.pdf` | figure | 83.0 KB | `call_00_R5TF2N…` | — |
| `work/genomics-analyst/results/figures/fig4a_genetics_e2g_cd276.png` | figure | 793.9 KB | `call_00_R5TF2N…` | — |
| `work/genomics-analyst/logs/02_parse_encode_re2g_revision2.log` | log | 3.2 KB | `call_00_lniZ3b…` | — |
| `work/genomics-analyst/data/processed/cd276_e2g_parse_log.txt` | report | 3.2 KB | `call_00_lniZ3b…` | — |
| `work/genomics-analyst/data/processed/cd276_round2_germline_verification_log.txt` | report | 4.6 KB | `call_00_AlpTHj…` | — |
| `work/genomics-analyst/data/processed/cd276_trait_label_audit_log.txt` | report | 486 B | `call_00_ET_qqC…` | — |
| `work/genomics-analyst/results/reports/cd276_panel4a_report.md` | report | 28.2 KB | `call_00_e9p6Z5…` | — |
| `work/genomics-analyst/results/reports/revision_response_to_reviewer.md` | report | 5.1 KB | `call_00_vJydj9…` | — |
| `work/genomics-analyst/data/raw/cd276_l2g_predictions.csv` | table | 27.5 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/cd276_locus_credible_sets_all_studies.parquet` | table | 208.6 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/cd276_tss250kb_region_query_round2.parquet` | table | 313.0 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/cd276_tss500kb_region_query_round2.parquet` | table | 762.3 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/round1_per_study/luad_GCST004744_credible_sets.parquet` | table | 26.6 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/round1_per_study/luad_GCST008836_credible_sets.parquet` | table | 47.5 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/round1_per_study/luad_GCST90134662_credible_sets.parquet` | table | 52.3 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/round1_per_study/luad_GCST90297563_credible_sets.parquet` | table | 25.3 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/round1_per_study/luad_GCST90455522_credible_sets.parquet` | table | 83.2 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/round1_per_study/sclc_FINNGEN_R12_C3_SCLC_EXALLC_credible_sets.parquet` | table | 22.3 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/round1_per_study/sclc_GCST004746_credible_sets.parquet` | table | 21.3 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/data/raw/round1_per_study/sclc_GCST90134664_credible_sets.parquet` | table | 22.6 KB | `call_00_f9uEIB…` | — |
| `work/genomics-analyst/results/tables/cd276_e2g_cd276_linked_all_839.csv` | table | 178.5 KB | `call_00_lniZ3b…` | — |
| `work/genomics-analyst/results/tables/cd276_e2g_regulatory_elements.csv` | table | 2.3 MB | `call_00_lniZ3b…` | — |
| `work/genomics-analyst/results/tables/cd276_e2g_summary.csv` | table | 8.4 KB | `call_00_lniZ3b…` | — |
| `work/genomics-analyst/results/tables/cd276_e2g_within_500kb_77_elements.csv` | table | 23.3 KB | `call_00_lniZ3b…` | — |
| `work/genomics-analyst/results/tables/cd276_e2g_within_window_score_distance_distribution.csv` | table | 22.4 KB | `call_00_lniZ3b…` | — |
| `work/genomics-analyst/results/tables/cd276_e2g_within_window_score_distance_summary.csv` | table | 2.2 KB | `call_00_lniZ3b…` | — |
| `work/genomics-analyst/results/tables/cd276_gwas_trait_label_audit.csv` | table | 7.2 KB | `call_00_ET_qqC…` | — |
| `work/genomics-analyst/results/tables/cd276_round2_credible_set_window_reconciliation.csv` | table | 2.0 KB | `call_00_AlpTHj…` | — |
| `work/genomics-analyst/results/tables/cd276_round2_germline_verification.csv` | table | 3.9 KB | `call_00_AlpTHj…` | — |
| `work/genomics-analyst/results/tables/cd276_round2_per_study_locus_check.csv` | table | 1.5 KB | `call_00_AlpTHj…` | — |

## Reproducing this run

```bash
./run.sh verify 20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8   # check file hashes and evidence coverage
./run.sh verify 20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8 --rerun   # also re-execute analysis scripts
./run.sh replay 20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8   # re-run the same turns into a new run dir
```

`verify` checks recorded files, claims and report references. With `--rerun`, it also re-executes the analysis scripts under `work/*/code/` and compares the reproduced outputs. `replay` re-runs the agents against the same pinned models and prompts — LLM sampling means it is comparable, not bit-identical.

<details><summary>Pinned configuration</summary>

```json
{
  "session_id": "86aa9b68-4073-406f-aa9d-d2d1efcbcfdc",
  "cso_model": "claude-sonnet-4-5-20250929",
  "specialist_model": "claude-sonnet-4-5-20250929",
  "specialist_model_label": "claude-sonnet-4-5-20250929",
  "effort": "xhigh",
  "max_turns": 100,
  "python": "3.11.17",
  "host": "n1",
  "started": "2026-10-21T20:40:38.866175",
  "interface": "web_or_batch",
  "audit_required": true,
  "claude_agent_sdk": "0.1.69",
  "git_commit": "71f9da68c95c5ee0ef4c1d9b8f45f10693de022d",
  "prompt_sha256": {
    "chief_of_staff/system_prompt.md": "8bcdef74c90cc045",
    "cso/system_prompt.md": "ce111aaf81408dc1",
    "modality_selection/system_prompts/medchem_pharmacologist_short.md": "73c865ec6f1c745d",
    "modality_selection/system_prompts/target_biologist_short.md": "e2be1776d719164f",
    "safety/system_prompts/bio_pathways_ppi_analyst_short.md": "f00ec50864bc9caf",
    "safety/system_prompts/clinical_trialist_short.md": "c0403869a6bd312a",
    "safety/system_prompts/fda_safety_officer_short.md": "415e8d0d20f96b6d",
    "scientific_reviewer/system_prompt.md": "0858303b50d034ed",
    "target_id/system_prompts/functional_genomics_analyst_short.md": "a8ddac7f120e5e01",
    "target_id/system_prompts/genomics_analyst_short.md": "ddc34ab89d5f1f84",
    "target_id/system_prompts/single_cell_analyst_short.md": "5485dce25d3ebf3e",
    "trial_matching/system_prompt.md": "6b9620e4d034229a"
  },
  "mcp_servers": [
    "association",
    "clinicaltrials",
    "disease",
    "drug",
    "expression",
    "functional_genomics",
    "genetics",
    "interaction",
    "pathway",
    "provenance",
    "single_cell",
    "target"
  ],
  "research_turns": [
    1
  ],
  "total_cost_usd": 32.721156,
  "num_turns": 1,
  "interrupted_turns": [
    1
  ],
  "data_source_errors": []
}
```

</details>

## Directory layout

```
MANIFEST.json   every artifact: hash, producing agent, producing tool call
inputs/         the query, the analysis plan, the pinned config
work/<agent>/   per-agent outputs — code/, data/, results/
evidence/       claims.json (claim → evidence), provenance.json (tool → agent)
logs/           trace.jsonl, cost_report.json, transcript.md
report/         the CSO's final synthesis
```

*Generated 2026-10-22 00:49:14 by `src/utils/run_report.py`.*