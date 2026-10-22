# Panels 4B / 4C — Single-cell atlas and pseudobulk DE in LUAD and SCLC

Round 2 rebuild. All outputs are prefixed `scrna_` (Visium outputs from the
parallel instance, prefixed `visium_`/`fig4e_`/`figs5b_`, were not touched).

## 1. Headline results

1. Integrated atlas of **413,996 cells / 80 donors / 15 cell types** from two
   CELLxGENE Census datasets (576f193c, 1e6a6ef9), full transcriptome
   (61,497 features), raw counts preserved.
2. Pseudobulk differential expression (PyDESeq2 0.5.4) was run for **15
   disease-vs-normal contrasts in 6 LUAD and 5 SCLC cell types** (plus 4 paired
   LUAD sensitivity contrasts). Significant genes (FDR<0.05, |log2FC|>0.5)
   ranged from 6 (LUAD mast cell) to 4,885 (SCLC epithelial cell).
3. **CD276 is not significantly differentially expressed in any tested cell
   type** in either histology (all padj > 0.29 in primary contrasts; smallest
   padj 0.291, SCLC macrophage, log2FC -0.95).
4. CD276 is expressed at low levels overall; the highest detection is in
   **fibroblasts** (LUAD 30.8% of 3,411 cells, mean log-normalised 0.329; SCLC
   35.3% of 244 cells, 0.401) and in **normal-lung macrophages** (36.5% of
   3,011 cells, 0.260).
5. **Disease-vs-normal DE is not testable for fibroblasts** (only 1 normal
   donor with >=10 fibroblasts, 31 cells total). This is the cell type most
   relevant to the downstream CAF/LIANA question, so it is a real gap, not a
   null result.
6. Several "tumour-up" genes in non-malignant compartments are cell-type
   identity genes of the tumour (SCLC: ASCL1, GRP, INSM1; LUAD: COL1A1,
   COL3A1), i.e. **ambient-RNA / doublet contamination**. These are flagged in
   Section 7 and should not be read as immune-cell-intrinsic biology.

## 2. Dataset selection (full inventory in `scrna_dataset_inventory.csv`)

Pre-specified criteria: human, tissue lung, 10x assay, donor_id and cell_type
present, disease label in {lung adenocarcinoma, small cell lung carcinoma,
normal}, fibroblasts present.

| Dataset | Role | Cells (primary 10x, lung) | Donors | Reason |
|---|---|---|---|---|
| 576f193c-75d0-4a11-bd25-8676587e6dc2 | included | 90,384 | 26 | Only candidate containing LUAD, SCLC **and** normal lung in one study; 3 LUAD donors have paired adjacent normal. Supplies the entire DE contrast. |
| 1e6a6ef9-7ec9-4c90-bbfb-2ad3c3165fd1 | included | 411,922 | 54 | Largest primary 10x LUAD cohort; 44 donors with fibroblasts. Adds atlas breadth/donor depth only — **no normal samples**, so not used for DE. |
| 9f222629 | excluded | — | 300 | 300 donors and 15 diseases under one `dataset_id`; disease is confounded with study/batch de facto. |
| other LUAD/SCLC candidates | excluded | 0 | — | 0 primary human 10x lung cells after filtering. |
| normal-only atlases | excluded | — | — | No tumour arm. |

## 3. Data pull — full transcriptome (log in `scrna_census_batch_log.csv`)

Every pull used `gene_symbols=None`; no gene panel was ever applied.
2 GB/query cap respected by splitting the 1e6a6ef9 cohort by donor.

| Batch | Dataset | Cells | Size (MB) | Success | Retries |
|---|---|---|---|---|---|
| b1 | 576f193c | 90,384 | 402.4 | yes | 0 |
| b2 | 1e6a6ef9 (donors 1–26) | 206,186 | 613.2 | yes | 0 |
| b3 | 1e6a6ef9 (donors 27–54) | 205,736 | 568.4 | yes | 0 |

Census `var_names` are numeric IDs; `feature_name` was promoted to `var_names`
immediately after each download, then made unique.

## 4. QC and cell/donor audit (`scrna_cell_donor_audit.csv`)

| Stage | Cells | Donors | Cell types |
|---|---|---|---|
| raw pull | 502,306 | 80 | 15 |
| post QC | 494,982 | 80 | 15 |
| post downsampling | 413,996 | 80 | 15 |
| final integrated / plotted | 413,996 | 80 | 15 |

QC filters: 300–9,000 detected genes; mitochondrial fraction <=15%. Failures:
7,310 cells below 300 genes, 14 above 9,000 genes, **0 failed the mito filter**.

Per dataset × disease (post QC -> final): 576f193c LUAD 42,509 (16 donors),
normal 11,642 (4), SCLC 29,178 (9); 1e6a6ef9 LUAD 330,667 (54). Downsampling
cap was 10,000 cells/donor, proportional by cell type with a 5-cell floor for
rare types and largest-remainder rounding; 14 donors were capped.

**Limitation — mitochondrial QC was not informative.** All 37 MT- features in
the Census raw matrices have zero non-zero entries for these cells (e.g.
MT-ND1, MT-CO1, MT-ATP6 nnz = 0), so `pct_mito` is 0 for every cell and the
<=15% filter removed nothing. This is a property of the Census raw layer, not
evidence of high-quality cells; the mito criterion should be regarded as
**not assessed** rather than passed.

## 5. Normalisation and integration (Panel 4B = `fig4b_umap_luad_sclc.png/.pdf`)

Library-size normalisation to 10,000 counts then log1p (scanpy 1.11.5);
3,000 HVGs (`flavor="seurat"`, `batch_key="dataset_id"`); PCA 50 components;
Harmony on `dataset_id` (20 iterations, seed 42); neighbours (15) and UMAP on
`X_harmony`.

Harmony was keyed on `dataset_id` because the two datasets are separate
studies with different nuclei/cell isolation protocols; `disease` was not used
as a batch key because it is the biological variable of interest.

Validation (`scrna_harmony_validation.csv`):

| Representation | ASW dataset | ASW disease | kNN same-dataset fraction |
|---|---|---|---|
| X_pca | 0.152 | 0.104 | 0.994 |
| X_harmony | 0.016 | -0.019 | 0.883 |

Integration removed dataset structure as intended. **Caveat:** `dataset_id` is
partially confounded with disease (1e6a6ef9 is LUAD-only), so correcting on
dataset also attenuates disease separation (ASW_disease 0.104 -> -0.019).
Pseudobulk DE is unaffected because it is computed **within 576f193c only**,
where all three conditions are present.

Marker validation (`scrna_celltype_marker_validation.csv`) confirms canonical
identities: TPSAB1/CPA3 in mast cells, DCN/COL1A1 in fibroblasts, PECAM1/VWF in
endothelium, CD68/C1QA in macrophages, CD3D/CD3E in T cells, MS4A1 in B cells,
EPCAM/KRT18 in epithelial/malignant cells.

## 6. Pseudobulk DE (Panel 4C = `fig4c_pseudobulk_de_luad_sclc.png/.pdf`)

**Aggregation.** Raw counts summed per donor x cell type x condition (condition
is part of the key so the three paired donors do not merge tumour and normal
into one pseudobulk). Pseudobulk retained at >=10 cells; contrast tested at
>=3 donors per group.

**Designs.**
- Primary (all donors, dataset 576f193c): `~condition`,
  contrast `["condition", <disease>, "normal"]`, run separately for LUAD and SCLC.
- Paired sensitivity (LUAD only, donors RU675/RU682/RU684): `~donor_id + condition`.

**Thresholds.** FDR < 0.05 (Benjamini-Hochberg) and |log2FC| > 0.5.
Full results: 922,455 rows in `scrna_pseudobulk_de_luad_sclc.csv` (all genes,
all contrasts, both designs). Top 20 up/down per contrast:
`scrna_pseudobulk_de_top_genes.csv`.

### 6.1 Testable contrasts and significant genes

| Histology | Cell type | Disease vs normal donors | Genes tested | Significant |
|---|---|---|---|---|
| LUAD | B cell | 15 vs 4 | 17,196 | 169 |
| LUAD | T cell | 16 vs 4 | 19,162 | 532 |
| LUAD | dendritic cell | 13 vs 4 | 16,857 | 273 |
| LUAD | epithelial cell | 15 vs 4 | 20,116 | 57 |
| LUAD | macrophage | 16 vs 4 | 18,821 | 659 |
| LUAD | mast cell | 10 vs 4 | 14,865 | 6 |
| SCLC | B cell | 4 vs 4 | 12,864 | 15 |
| SCLC | T cell | 8 vs 4 | 18,295 | 880 |
| SCLC | dendritic cell | 6 vs 4 | 15,342 | 165 |
| SCLC | epithelial cell | 9 vs 4 | 21,589 | 4,885 |
| SCLC | macrophage | 9 vs 4 | 18,056 | 1,118 |
| LUAD (paired) | B cell | 3 vs 3 | 14,529 | 2 |
| LUAD (paired) | T cell | 3 vs 3 | 17,336 | 139 |
| LUAD (paired) | epithelial cell | 3 vs 3 | 17,873 | 122 |
| LUAD (paired) | macrophage | 3 vs 3 | 18,133 | 280 |

### 6.2 Contrasts not tested (gaps, not nulls)

`scrna_de_testability_by_celltype.csv` records the donor counts behind each gap.

- **Fibroblast — LUAD (11 vs 1 donors) and SCLC (4 vs 1): not testable.** Only
  one normal donor contributes >=10 fibroblasts (31 cells). Tumour fibroblasts
  are plentiful (LUAD 3,411 cells/11 donors, SCLC 244/4), so the atlas supports
  fibroblast characterisation but not a disease-vs-normal fibroblast DE.
  This directly limits any CAF conclusion drawn from DE.
- Endothelial: LUAD 9 vs 2, SCLC 5 vs 2 — not testable.
- Plasma cell: LUAD 5 vs 0, SCLC 0 vs 0 — no normal plasma cells.
- Neutrophil: LUAD 2 vs 1, SCLC 0 vs 1 — not testable.
- Mast cell in SCLC: 1 vs 4 — not testable (LUAD mast cell is testable).
- Paired sensitivity: only B, T, epithelial and macrophage have all three
  paired donors with both conditions; DC, endothelial, fibroblast, mast,
  neutrophil and plasma cell were skipped.

### 6.3 Leading genes (primary contrasts)

- LUAD T cells up: COL3A1 +8.9, CXCL13 +8.0, IGFL2 +7.6, MMP2 +7.2, THY1 +7.0.
- LUAD macrophage up: CXCL13 +8.5, SPP1 +8.2, COL1A2 +7.6, COL3A1 +7.5.
- LUAD dendritic cell up: COL1A1 +7.0, COL3A1 +6.9, BGN +6.3, COL1A2 +5.8, LUM +5.6.
- LUAD B cells up: TGFB1 +3.0, HOPX +2.9; down: CSTA -6.2, FABP4 -5.7.
- SCLC epithelial up: SCG3 +10.7, INSM1 +10.6, NDUFA4L2 +9.9, EEF1A2 +9.7,
  CRABP1 +9.6; down: SCGB1A1 -11.8, FABP4 -11.2, SFTPC -10.1 (loss of normal
  airway/alveolar programme, gain of neuroendocrine programme).
- SCLC macrophage up: ASCL1 +12.4, GRP +11.2, INSM1 +10.9; down: SCGB1A1 -8.6,
  FABP4 -8.2, SFTPC -7.4.
- SCLC T cells up: GRP +10.8, ASCL1 +9.3, UCHL1 +8.9, GNG4 +8.5, CXCL13 +8.3.

## 7. Critical caveats

1. **Ambient RNA / doublets dominate many "tumour-up" calls.** ASCL1, GRP and
   INSM1 are SCLC tumour-cell identity genes, yet they top the SCLC macrophage
   and T-cell and dendritic-cell lists. Likewise COL1A1/COL3A1/LUM top the LUAD
   T-cell and dendritic-cell lists. These compartments are almost certainly
   contaminated by tumour and stromal transcripts; the DE statistics are valid
   for the pseudobulk as measured but the biological attribution is not. Any
   claim built on these genes should be restricted to epithelial/malignant
   cells or validated by decontamination (e.g. SoupX/CellBender) before use.
2. **Only 4 normal donors** underpin every disease-vs-normal contrast, and all
   four come from a single study. All primary-design p-values are therefore
   conditional on that small, single-study reference.
3. **SCLC has no paired normal donor**; the SCLC contrast is unpaired
   (9 tumour vs 4 normal donors, no donor overlap).
4. **Mito QC not assessed** (Section 4).
5. **Dataset/disease confounding of the embedding** (Section 5); DE unaffected.
6. **Atlas cell-type labels are Census author labels**, harmonised only by
   spelling (15 labels retained). `malignant cell`, `monocyte/myeloid`,
   `stromal/other` and NK cells occur only in 1e6a6ef9, so they cannot enter
   the within-576f193c DE.
7. **Pre-integration intermediate deleted.** `scrna_qc_downsampled_v2.h5ad`
   (and a redundant 2.7 GB copy) were removed to stay under the BeeGFS per-user
   quota. The integrated atlas contains every column needed to reproduce the DE
   and downstream analysis; scripts `06a` and `06` therefore read
   `scrna_luad_sclc_integrated.h5ad`.

## 8. Files

Data: `data/processed/scrna_luad_sclc_integrated.h5ad` (5.4 GB; counts layer,
lognorm X, X_pca, X_harmony, X_umap; obs donor_id, dataset_id, cell_type,
cell_type_original, disease, tissue, assay, n_genes, pct_mito, total_counts, nnz).

Tables: `scrna_cell_donor_audit.csv`, `scrna_dataset_inventory.csv`,
`scrna_census_batch_log.csv`, `scrna_harmony_validation.csv`,
`scrna_celltype_marker_validation.csv`, `scrna_atlas_validation.csv`,
`scrna_cd276_expression_by_celltype.csv`, `scrna_de_testability_by_celltype.csv`,
`scrna_pseudobulk_de_sample_summary.csv`, `scrna_pseudobulk_de_luad_sclc.csv`,
`scrna_pseudobulk_de_top_genes.csv`.

Figures: `fig4b_umap_luad_sclc.png/.pdf`, `fig4c_pseudobulk_de_luad_sclc.png/.pdf`.

Scripts: `03b_merge_qc_downsample_instrumented.py`, `05_integrate_annotate.py`,
`06_pseudobulk_de.py`, `06a_de_testability.py`, `07_fig_de.py`,
`08_validate_atlas.py`.

Environment: scanpy 1.11.5, anndata 0.12.7, harmonypy 0.2.0, PyDESeq2 0.5.4,
seed 42 throughout.
