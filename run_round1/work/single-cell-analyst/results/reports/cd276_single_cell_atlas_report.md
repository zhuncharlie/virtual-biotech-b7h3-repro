# CD276 (B7-H3) single-cell expression in LUAD and SCLC

**Agent:** single-cell-analyst
**Date:** 2026-10-20
**Data:** CELLxGENE Census (stable release), normalized layer, reported as CPM-equivalent (fraction of counts per cell x 1e6; no log transform)
**Scope:** transcript-level characterisation of CD276 in lung adenocarcinoma (LUAD), small cell lung carcinoma (SCLC), and a multi-organ normal reference panel. This is not a protein or surface-expression measurement.

---

## 1. Data and scope

### Tumour datasets

| Indication | Cells | Datasets | Cell-type labels | Per-cell-type donor counts |
|---|---:|---:|---:|---|
| LUAD | 635,998 | 3 | 55 | up to 115 (macrophage) |
| SCLC | 31,540 | 1 | 10 | up to 9 |

LUAD datasets: `1e6a6ef9-7ec9-4c90-bbfb-2ad3c3165fd1` (548,457 cells), `576f193c-75d0-4a11-bd25-8676587e6dc2` (46,529 cells), `9f222629-9e39-47d0-b83f-e08d610c7479` (41,012 cells). SCLC: `576f193c-75d0-4a11-bd25-8676587e6dc2` (31,540 cells).

**Donor accounting.** The LUAD count of 635,998 cells from 3 datasets is reproducible from the saved dataset inventory. We do **not** assert a single total unique-donor count, because donor identifiers are not guaranteed to be deduplicated across the three datasets. Donor support is reported per cell type instead; the maximum observed in a single pooled cell-type row is **115 donors** (LUAD macrophage). The 3-donor paired analysis is the only donor-matched comparison.

A single total unique-donor count is not asserted and should not be cited; per-cell-type donor support is the traceable unit.

### Normal reference panel

3,074,946 cells from 19 organ groups. The normal lung subset used for the paired and SCLC comparisons is from dataset `576f193c` (12,315 lung cells, 4 donors).

### Important design caveat

The three LUAD datasets are assay-heterogeneous (the largest spans 10x 3' v1/v2/v3, 10x 5' v1, Smart-seq2, BD Rhapsody, GEXSCOPE, and inDrop). Pooled means therefore mix platform and study effects with biology. Only the donor-matched analysis within dataset `576f193c` controls for this.

---

## 2. Key findings

### 2.1 LUAD malignant cells versus non-malignant epithelial cells

| Class | Cells | Donors | Mean CPM | % expressing |
|---|---:|---:|---:|---:|
| Malignant cell | 26,179 | 92 | 23.58 | 15.4% |
| Epithelial (non-malignant) | 47,002 | 93 | 16.40 | 7.5% |

CD276 is ~1.44-fold higher in annotated malignant cells than in non-malignant epithelial cells in the same indication (23.58 vs 16.40 CPM). This is a between-cell-class comparison, not a donor-matched contrast.

### 2.2 Donor-matched LUAD tumour versus adjacent normal epithelium (3 donors, dataset 576f)

**Corrected claim:** CD276 was higher in tumour than adjacent normal epithelium in 3/3 donor-matched LUAD pairs, but reached >=2x in only 2/3 (3.26, 3.40, 1.09) and was not statistically significant at n=3.

| Donor | Tumour cells | Normal cells | Tumour CPM | Normal CPM | Tumour/normal ratio | Tumour % expr. | Normal % expr. |
|---|---:|---:|---:|---:|---:|---:|---:|
| RU675 | 291 | 221 | 14.34 | 4.39 | 3.26 | 14.8% | 2.7% |
| RU682 | 120 | 191 | 40.13 | 11.81 | 3.40 | 27.5% | 7.9% |
| RU684 | 189 | 150 | 26.59 | 24.30 | 1.09 | 13.2% | 7.3% |
| **Pooled** | **600** | **562** | **27.02** | **13.50** | — | **18.5%** | **6.0%** |

The direction is consistent (3/3 pairs) but the effect size is heterogeneous: one donor (RU684) shows essentially no difference (1.09x). Two summary ratios are therefore reported rather than a single headline multiple: the ratio of donor means is 2.00, while the mean of the three donor ratios is 2.59. Neither should be quoted as "~2x in all pairs."

A two-sided paired t-test on the three donor means gives p = 0.22 (mean CPM) and p = 0.09 (% expressing); with n = 3 this is underpowered. Full statistics are in `cd276_luad_paired_donor_stats.csv`. The prose conclusion is restricted to "not statistically significant at n=3."

### 2.3 SCLC epithelial cells versus normal lung epithelium

| Class | Cells | Donors | Mean CPM | % expressing |
|---|---:|---:|---:|---:|
| SCLC epithelial | 25,988 | 9 | 28.54 | 19.5% |
| Normal lung epithelial | 851 | 4 | 17.09 | 6.8% |

SCLC epithelial CD276 is 1.67-fold the normal lung epithelial mean (28.54 vs 17.09 CPM) with a higher expressing fraction (19.5% vs 6.8%). This comparison is **not donor-matched**: the tumour and normal cells come from the same dataset but from disjoint donor sets.

### 2.4 Normal-tissue distribution

Weighted mean CD276 by organ (top and bottom of the panel):

| Organ | Cells | Donors | Weighted mean CPM | % cells expressing |
|---|---:|---:|---:|---:|
| skin | 178,563 | 13 | 46.0 | 25.6% |
| kidney | 64,510 | 9 | 42.6 | 3.2% |
| adrenal gland | 43,476 | 6 | 37.6 | 2.7% |
| adipose | 86,064 | 22 | 34.5 | 9.3% |
| colon | 49,095 | 12 | 30.8 | 15.3% |
| lung (normal) | 12,315 | 4 | 13.9 | 9.8% |
| blood (progenitor-rich) | 338,903 | 90 | 0.30 | 0.06% |
| spleen/lymph node | 389,682 | 23 | 0.24 | 0.13% |
| bone marrow | 263,159 | 45 | 0.21 | 0.12% |
| blood (mature PBMC) | 207,225 | 13 | 0.07 | 0.04% |

Within normal lung, macrophage (39.6 CPM, 3,334 cells), fibroblast/stromal (39.2 CPM but only 37 cells) and mast cell (27.2 CPM) exceed epithelial cells (17.1 CPM, 851 cells).

**Normal-tissue caveat:** kidney CD276 (42.6 CPM) is accompanied by markedly low housekeeping detection (ACTB in 23.8% of cells and GAPDH in 32.1%, versus >95% for ACTB in blood/skin and 95.8% in SCLC). Kidney was generated with sci-RNA-seq3, so its high rank may reflect platform/normalisation behaviour rather than pure biology. Normal-tissue rankings should be read as hypothesis-generating.

### 2.5 Stromal/myeloid signal exceeds tumour-cell signal in BOTH indications (symmetry)

| Indication | Tumour cell | Tumour CPM | Comparator | Comparator CPM | Comparator / tumour |
|---|---:|---:|---|---:|---:|
| LUAD | malignant (26,179 cells) | 23.6 | fibroblast (3,979 cells) | 75.9 | 3.2x |
| LUAD | malignant (26,179 cells) | 23.6 | macrophage (116,365 cells) | 33.5 | 1.4x |
| SCLC | epithelial (25,988 cells) | 28.5 | fibroblast (328 cells) | 68.1 | 2.4x |
| SCLC | epithelial (25,988 cells) | 28.5 | macrophage (375 cells) | 48.8 | 1.7x |

The same ordering is present in both indications: fibroblast/stromal CD276 (LUAD 75.9; SCLC 68.1 CPM) is higher than malignant/epithelial CD276 (LUAD 23.6; SCLC 28.5 CPM), and macrophages also exceed tumour cells. In LUAD the fibroblast/stromal lineage aggregate is 55.45 CPM across 9,909 cells from 75 donors.

**Interpretation (explicit):** this is a **transcript-level caveat** and a **potential stromal antigen sink**. It is **not** a measure of tumour-cell surface protein and is not evidence against an ADC. Bulk or stromal mRNA can inflate apparent target expression while surface protein on malignant cells remains the relevant quantity for an ADC; conversely, stromal protein could act as an antigen sink. Resolving this requires protein-level data (IHC, flow, or spatial proteomics), not scRNA-seq alone.

---

## 3. Caveats and limitations

1. **Transcript only.** Normalized counts report mRNA, not surface protein density. No conclusion about B7-H3 protein level, internalisation, or therapeutic window follows directly.
2. **Sparse expression.** Median CPM is 0 for essentially every cell type; mean CPM is driven by the expressing minority (e.g. 15.4% of LUAD malignant cells). Means and expressing fractions are both reported.
3. **Donor-matched evidence is n=3** and underpowered; the three ratios (3.26, 3.40, 1.09) show real heterogeneity.
4. **SCLC comparison is not donor-matched** (disjoint donors within one dataset).
5. **Assay heterogeneity** across the three LUAD datasets and across the normal panel; pooled means are not batch-corrected.
6. **Cell-type labels are dataset-provided**, not re-annotated here. EPCAM and PTPRC were used as compartment sanity checks; normal lung epithelial cells retain substantial PTPRC signal (56.5 CPM), indicating immune contamination in that reference.
7. **No additional cell-level QC** was applied beyond Census-provided cells (`is_primary_data == True`); n_genes/complexity cannot be recomputed from the 3-gene subset used.
8. **Platform caveat for normal tissues**, particularly kidney (sci-RNA-seq3; low ACTB/GAPDH detection).

---

## 4. What the data support, and what they do not

**Supported:**
- CD276 transcripts are detectable in LUAD malignant cells (23.6 CPM; 15.4% expressing) and SCLC epithelial cells (28.5 CPM; 19.5% expressing).
- In 3 donor-matched LUAD pairs, CD276 was higher in tumour than adjacent normal epithelium in 3/3, but >=2x in only 2/3 (3.26, 3.40, 1.09), and was not statistically significant at n=3.
- Fibroblast/stromal and macrophage CD276 transcripts exceed malignant/epithelial transcripts in both LUAD and SCLC.

**Not supported:**
- "~2x adjacent normal in all 3 donor-matched pairs."
- A claim of uniform or tumour-cell-selective overexpression.
- Any claim that transcript levels establish ADC target adequacy or a therapeutic window.

---

## 5. Evidence artifacts

| Artifact | Content |
|---|---|
| `results/tables/cd276_epithelial_tumor_vs_normal_donor_paired.csv` | Per-donor paired cell counts, mean CPM, expressing fraction, EPCAM/PTPRC, and tumour/normal ratio |
| `results/tables/cd276_epithelial_tumor_vs_normal_donor_paired_summary.csv` | Clean one-row-per-donor summary with ratios |
| `results/tables/cd276_luad_paired_donor_stats.csv` | Explicit paired statistics: n=3, ratios, t and p values, caveat |
| `results/tables/cd276_luad_sclc_celltype_expression.csv` | Pooled per-cell-type expression, all LUAD (55) and SCLC (10) labels, with n_cells and n_donors |
| `results/tables/cd276_key_comparisons.csv` | Pre-specified comparisons, corrected donor-matched wording |
| `results/tables/cd276_normal_tissue_organ_summary.csv` | Organ-level weighted means and donor counts |
| `results/tables/cd276_stromal_vs_tumor_symmetry.csv` | Side-by-side LUAD/SCLC stromal and myeloid versus tumour-cell values with interpretation |
| `results/tables/cd276_dataset_inventory.csv` | Verified cell and dataset counts (LUAD 635,998 / 3 datasets; SCLC 31,540 / 1 dataset) |
| `results/tables/qc_housekeeping_scale_check.csv` | ACTB/GAPDH/CD276 scale check underpinning the platform caveat |
| `results/figures/cd276_luad_tumor_vs_normal_paired.png` | Paired donor plot, ratios labelled, 3/3 and 2/3 stated |
| `results/figures/cd276_stromal_vs_tumor_symmetry.png` | Symmetry of stromal/myeloid > tumour-cell signal in LUAD and SCLC |
| `results/figures/cd276_luad_sclc_celltype_expression.png` | Top cell types by CD276 in LUAD and SCLC |
| `results/figures/cd276_normal_tissues_organ_by_lineage.png` | Normal-tissue lineage expression |
| `results/figures/cd276_normal_tissues_top_celltypes.png` | Normal-tissue top cell types |
| `results/figures/cd276_normal_organ_weighted_mean.png` | Normal organ weighted means |

**Analysis parameters:** `results/tables/cd276_analysis_parameters.csv` (Census stable, normalized layer, CPM-equivalent, no log, `is_primary_data == True`).
