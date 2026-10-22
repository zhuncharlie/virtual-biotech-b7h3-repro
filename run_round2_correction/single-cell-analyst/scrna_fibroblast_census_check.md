# Correction Task B — can the normal-lung fibroblast comparator be expanded?

Run: `20261022-094819-this-is-a-targeted-correction-pa-d24cb49b`
Agent: single-cell-analyst
Question: does CELLxGENE Census contain additional **matched-study** normal-lung
fibroblast donors that would make the paper's Figure 4C fibroblast DE testable,
without breaking the within-study disease-vs-normal design?

**Answer: no. The gap cannot be closed safely. No additional data were pulled.**

## 1. Why the question matters

`scrna_cd276_de_summary.csv` in the source run has **no fibroblast row**. The
existing `scrna_de_testability_by_celltype.csv` records the reason:
fibroblast LUAD-vs-normal is not testable because the normal compartment has
**31 cells across 3 donors, only 1 donor with >=10 cells** (after QC and
downsampling). The paper's 4C claim is specifically about fibroblasts
("significantly increased expression in fibroblasts"), so the 15 non-fibroblast
null contrasts are **not** a direct test of that claim.

## 2. Queries run (CELLxGENE Census, via the single-cell MCP tools)

| # | Query | Result |
|---|---|---|
| 1 | `count_cells(tissue=='lung' and disease=='normal' and cell_type=='fibroblast' and dataset_id=='576f193c-75d0-4a11-bd25-8676587e6dc2')` | **37 cells** |
| 2 | `query_cell_metadata(... same filter ...)` | 37 cells, **3 donors**, all `10x 3' v2` |
| 3 | `count_cells(tissue=='lung' and disease=='normal' and cell_type=='fibroblast' and dataset_id=='350237e0-9f48-4cbd-9140-3b44495549f3')` | **104 cells** |
| 4 | `query_cell_metadata(... 350237e0 ...)` | 104 cells, **17 donors**, 4 with >=10 cells, `10x 5'` / `10x 5' v1` |
| 5 | `list_metadata_values('disease', dataset_id=='350237e0...')` | only `normal` (670,749 cells); **no tumour arm** |
| 6 | `count_cells(dataset_id=='1b350d0a-4535-4879-beb6-1142f3f94947' and lung and normal and fibroblast)` | **0** (129,457 normal lung cells, but no fibroblast-labelled cells) |
| 7 | `count_cells(dataset_id=='eb499fd8-7000-419f-8854-926b9b61b11f' and lung and normal and fibroblast)` | **0** |
| 8 | `count_cells(dataset_id=='f14bc322-1322-4184-8d16-409557525ea5' and lung and normal and fibroblast)` | **0** |
| 9 | `list_metadata_values('dataset_id', lung and normal and fibroblast)` | 15 datasets with >=1 normal-lung fibroblast; only one is the matched study |

Per-donor counts are saved in
`results/tables/scrna_fibroblast_census_donor_counts.csv`.

## 3. Per-donor counts

### Matched multi-histology study `576f193c-75d0-4a11-bd25-8676587e6dc2`

| donor_id | normal-lung fibroblasts (Census) | >=10 cells |
|---|---|---|
| RU675 | 28 | yes |
| RU682 | 5 | no |
| RU685 | 4 | no |

Census holds 37 cells / 3 donors; the original QC + downsampling pipeline
retained 31 cells / 3 donors / 1 testable donor. Either way the conclusion is
the same: **one testable normal donor**, and PyDESeq2 requires >=3 donors per
group. Nothing further can be pulled from this study.

### Normal-only atlas `350237e0-9f48-4cbd-9140-3b44495549f3`

104 normal-lung fibroblasts, 17 donors, 4 with >=10 cells (HDBR15332 25,
HDBR14815 18, HDBR14944 17, HDBR15383 14), assay `10x 5' transcription
profiling`. This dataset is **normal-only** (670,749 cells; the only populated
disease label is `normal`). It has no tumour arm and is a different study and
platform from `576f193c` (10x 3' v2). Using its normal fibroblasts against
`576f193c` LUAD fibroblasts would confound disease with study and platform —
exactly the design violation the correction brief forbids.

### Other normal-only atlases named in the inventory

| dataset | normal lung cells | normal-lung fibroblasts |
|---|---|---|
| `1b350d0a-4535-4879-beb6-1142f3f94947` | 129,457 | 0 |
| `eb499fd8-7000-419f-8854-926b9b61b11f` | 122,445 | 0 |
| `f14bc322-1322-4184-8d16-409557525ea5` | 94,870 | 0 |

None can contribute a fibroblast comparator, and all three are unmatched
normal-only atlases regardless.

### Other datasets carrying normal-lung fibroblasts

`list_metadata_values` returned 15 dataset IDs with normal-lung fibroblasts.
After `576f193c`, `350237e0` and the aggregated mega-dataset `9f222629`
(15 diseases under one ID; disease confounded with study), the remaining
datasets (3de0ad6d, b617ee1b, d8da613f, 8c42cfd0, 493a8b60, e04daea4,
f9846bb4, fcadb222, 093d3bfe, e871881f, 2adb1f8a, d224c8e0) are independent
studies with no paired tumour/normal arm in the same dataset. They are not
matched to `576f193c` and were not pulled, for the same confounding reason.

## 4. Decision

The decision rule in the brief: run the fibroblast PyDESeq2 pipeline **only if**
a quick, safe pull yields >1 testable normal donor **without** reopening atlas
construction and **without** breaking the matched within-study design.

* Matched study: only 1 testable normal donor; no more data exist to pull.
* The only dataset with multiple testable normal donors (`350237e0`) is
  normal-only, a different study, and a different assay. It is unmatched by
  construction.

Therefore: **do not pull; the fibroblast gap remains a gap.** No PyDESeq2
fibroblast model was run. The 15 testable non-fibroblast contrasts are
untouched and remain a real broader negative finding.

## 5. Corrected verdict language (for the synthesis)

> The paper's specific fibroblast claim is **untestable in this reproduction**:
> the normal-lung fibroblast comparator has **31 cells across 3 normal donors,
> only 1 of which reaches the >=10-cell per-donor threshold** (Census holds 37
> cells / 3 donors before QC). The 15 testable non-fibroblast disease-vs-normal
> contrasts show no CD276 disease-association (smallest padj 0.291); this is a
> broad negative finding across the other compartments — suggestive, but
> **NOT a direct test of the paper's fibroblast-specific claim**.

The 15 null contrasts must be preserved as a real broader negative; they must
not be described as a refutation of the fibroblast claim.

## 6. Output files

| File | Content |
|---|---|
| `results/tables/scrna_fibroblast_census_donor_counts.csv` | per-donor normal-lung fibroblast counts for the matched study and the one multi-donor normal-only atlas |
| `data/processed/scrna_census_576f193c_normal_lung_fibroblast_metadata.csv/.parquet` | the 37 matched-study normal fibroblast records |
| `data/processed/scrna_census_350237e0_normal_lung_fibroblast_metadata.csv/.parquet` | the 104 normal-only-atlas fibroblast records |
