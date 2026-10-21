# Data provenance

This repo commits **code, configuration, and analysis results** (tables, figures,
reports). It does not commit large primary data pulled from external
databases during the run. This file records exactly what was excluded and how
to regenerate it.

## Excluded: raw CELLxGENE Census pulls (single-cell-analyst)

**Excluded directory:** `run/work/single-cell-analyst/data/raw/*.h5ad`,
`*.parquet` (29 files, ~140MB total, listed below with original byte sizes).

**Why excluded:** primary single-cell data re-downloadable from a public
source; not practical to version in git.

**How to regenerate:** every file below was produced by one of the committed
scripts in `run/work/single-cell-analyst/code/scripts/` (`01_discover_datasets.py`
through `08_apply_corrections.py`), calling the repo's own
`mcp__single_cell__get_anndata` / `count_cells` / `get_census_info` tools
against the CELLxGENE Census (`census_version: stable` at the time of the run,
2026-10-20). Re-running those scripts against a live Census connection
reproduces the same files (Census content for a fixed `census_version` is
immutable upstream).

**Provenance preserved in this repo (committed, not excluded):**
- `run/work/single-cell-analyst/results/tables/cd276_dataset_inventory.csv`
  and `cd276_normal_dataset_inventory.csv` — the exact dataset IDs, donor
  counts, and cell counts pulled from Census for every file below.
- `run/work/single-cell-analyst/data/raw/*.log` (small text logs, 3 files,
  committed) — discovery and QC run logs, no binary data.
- All derived tables/figures/reports in `results/` — committed in full,
  these are the actual numbers cited in the final report and already
  independently re-verified by the scientific-reviewer against these same
  saved tables (see `run/work/scientific-reviewer/results/reports/b7h3_review.md`,
  section B).

**Excluded file manifest (filename, bytes):**

```
luad_ds1e6a_epithelial_stromal_cd276.h5ad   3,283,191
luad_ds1e6a_lymphoid_cd276.h5ad             8,789,107
luad_ds1e6a_myeloid_cd276.h5ad              6,133,212
luad_lung_cell_metadata.parquet             1,856,209
luad_other_datasets_cd276.h5ad              3,286,295
normal_adipose_cd276.h5ad                   2,940,309
normal_adrenal_cd276.h5ad                   1,775,095
normal_blood_cd276.h5ad                     9,726,419
normal_blood_mature_pbmc_cd276.h5ad         6,184,785
normal_bone_marrow_cd276.h5ad               7,660,323
normal_brain_cortex_cd276.h5ad              3,874,651
normal_breast_cd276.h5ad                    3,755,354
normal_colon_cd276.h5ad                     1,969,165
normal_esophagus_cd276.h5ad                 2,948,453
normal_heart_cd276.h5ad                     6,717,962
normal_ileum_cd276.h5ad                     2,904,447
normal_kidney_cd276.h5ad                    4,820,124
normal_liver_cd276.h5ad                     5,017,680
normal_lung_cell_metadata.parquet           5,323,639
normal_lung_matched_cd276.h5ad              1,019,679
normal_pancreas_cd276.h5ad                  2,719,959
normal_skeletal_muscle_cd276.h5ad           5,478,612
normal_skin_cd276.h5ad                      5,589,619
normal_spleen_lymphnode_cd276.h5ad         11,497,957
normal_thymus_cd276.h5ad                    8,017,992
qc_scale_blood_pbmc_actb.h5ad                7,616,050
qc_scale_kidney_actb.h5ad                    5,183,884
qc_scale_sclc_actb.h5ad                      1,734,818
qc_scale_skin_actb.h5ad                      6,847,270
sclc_cd276.h5ad                              1,632,279
sclc_lung_cell_metadata.parquet                282,754
```

## Open Targets 25.09 reference archive

Not part of this repo at all (3508 Parquet files, ~29GB locally). Required
only to boot the original repo's formal entry point
(`require_reference_data()` in `src/data/readiness.py`), not specific to the
B7-H3 question. Download script: `tools/download_open_targets.py` in the
original repo (see `BASELINE.md`).

## Everything else

All ClinicalTrials.gov JSON (`work/clinical-trialist/data/raw/`, ~8MB),
Open Targets genetics parquet subsets (`work/genomics-analyst/data/raw/`,
~700KB), and DepMap/pathway/target query results are small enough to commit
directly and are included in full under `run/work/*/data/`.
