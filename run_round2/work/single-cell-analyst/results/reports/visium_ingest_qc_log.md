# Visium Panel 4E part 1 — data ingest and spot QC

**Scope:** Ingest and QC the 22 E-MTAB-13530 LUAD Visium sections (12 tumor,
10 adjacent-normal). cell2location is deliberately **not** run here — this
hand-off file is the input for that later step.

**Result in one line:** 22/22 sections passed integrity checks and loaded;
**54,650 raw in-tissue spots → 47,448 QC-passed spots (86.8%)** across 12
tumor (29,185 → 27,826) and 10 adjacent-normal (25,465 → 19,622) sections.

---

## 1. Data source and files

- Accession **E-MTAB-13530** (BioStudies/ArrayExpress), De Zuani et al.,
  *Nat Commun* 2024 (PMID 38782901), cited by the Virtual Biotech paper as its
  Visium source. Provenance chain is in
  `config/visium_data_provenance.md`.
- Staged at
  `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/data/visium_raw/`
  (download log ends `DONE_ALL_VISIUM_DOWNLOADS`; all 44 data files non-zero).
- Space Ranger **1.1.0**, reference **GRCh38-2020-A**, 36,601 Gene Expression
  features per section.
- Section metadata come from two sources. `sampling_site`, `disease`, `stage`,
  `age` and `sex` are parsed verbatim from `E-MTAB-13530.sdrf.txt`. `patient`
  and `histology` are derived from the section name (`patient_of()`,
  `histology_of()`: `_T` = tumor, `_B` = adjacent-normal) and then checked
  against the SDRF `Characteristics[original source name]` and
  `Characteristics[sampling site]`; the two agree for all 22 sections. All 22
  target sections are `Characteristics[disease] = lung adenocarcinoma`.
  **The SDRF `age` and `stage` fields are not usable as covariates — see §1.1.**

## 1.1 Metadata-integrity warning: SDRF age and disease staging

**Status: the section-level `age` and `stage` values in `.obs` must not be used
as patient covariates in any downstream model.**

Audit script: `code/scripts/visium_03_sdrf_metadata_integrity.py`
Tables: `results/tables/visium_sdrf_age_stage_integrity.csv` (22 sections),
`results/tables/visium_sdrf_age_stage_patient_summary.csv` (5 patients)

The deposited SDRF encodes one `Characteristics[age]` and one
`Characteristics[disease staging]` value **per section**, not per patient. Both
increment with the section index:

| patient | sections | age range | stages |
|---|---|---|---|
| P10 | 6 | 72–77 | T3N0M0 … T3N0M5 |
| P15 | 4 | 73–76 | T3N0M0 … T3N0M3 |
| P16 | 4 | 87–90 | T2bN0M0 (all four) |
| P24 | 4 | 52–55 | T3N0M0 … T3N0M3 |
| P25 | 4 | 64–67 | T3N0M0 … T3N0M3 |

- **No patient has a constant age** (all five have an age span of 3–5 years
  across 2–4 years of sections), so a valid patient-level age cannot be
  recovered from this field.
- **M2–M5 are not valid AJCC M categories.** 10 of 22 sections carry M2–M5
  (P10 four, P15 two, P24 two, P25 two); this is a data-entry artefact, not
  metastatic progression within a patient.
- Stage varies within 18 of 22 sections' patients (all except P16, whose four
  sections share T2bN0M0). Even there, age still varies.
- `.obs['age']` and `.obs['stage']` are retained **verbatim** for traceability
  and are identical to the SDRF (asserted in the audit script). They are
  labelled `usable_as_patient_level_covariate = False` in the audit table.
- Consequence: analyses in this panel are **not** adjusted for age or stage, and
  no per-section age/stage comparison is performed. Any synthesis statement that
  treats these as patient metadata would be unsupported.

## 2. Verification and staging (22/22 pass)

Script: `code/scripts/visium_01_verify_extract.py`
Table: `results/tables/visium_file_verification.csv`

For every section the `.h5` was opened with h5py and checked for the complete
10x matrix schema (`matrix/{barcodes,data,indices,indptr,shape}` and
`matrix/features/{id,name,feature_type}`), internal shape consistency
(`shape[0]` = n features, `shape[1]` = n barcodes, `len(indptr)` = n barcodes+1,
`indptr[-1]` = nnz, `max(indices) < n features`), and non-negative integer
counts. Every `.tar` was opened as a POSIX tar (`tarfile` mode `r:`) and
required to contain all six Space Ranger spatial files:

`aligned_fiducials.jpg`, `detected_tissue_image.jpg`,
`scalefactors_json.json`, `tissue_hires_image.png`,
`tissue_lowres_image.png`, `tissue_positions_list.csv`.

The `-spatial.tar` files are uncompressed tar archives; extraction was done
with `tar -xf` (never `-xzf`). Each section was staged as

```
data/raw/visium_extracted/<section>/filtered_feature_bc_matrix.h5
data/raw/visium_extracted/<section>/spatial/<six files>
```

so that `scanpy.read_visium` works directly on the directory.

**Outcome:** h5 22/22 OK, tar 22/22 OK, extraction 22/22 OK. No section was
dropped.

## 3. Barcode matching (perfect)

Table: `results/tables/visium_barcode_matching.csv`

| metric | value (22 sections) |
|---|---|
| matrix barcodes | 54,650 |
| array positions in positions files | 109,824 (= 22 × 4,992) |
| positions flagged in_tissue=1 | 54,650 |
| matrix barcodes absent from positions file | **0** |
| in-tissue positions absent from matrix | **0** |
| positions absent from matrix | 55,174 — all are `in_tissue=0` off-tissue positions |

Every filtered-matrix barcode matched an in-tissue spatial coordinate, and the
number of in-tissue positions equals the number of matrix barcodes in every
section. `tissue_positions_list.csv` is the headerless Space Ranger 1.1 format
(6 columns: barcode, in_tissue, array_row, array_col, pxl_row_in_fullres,
pxl_col_in_fullres) and was parsed accordingly.

## 4. Failure / retry log

| # | Stage | Symptom | Root cause | Fix | Outcome |
|---|---|---|---|---|---|
| 1 | First verification run | `ValueError: not enough values to unpack (expected 3, got 2)` in `verify_tar` | helper returned a 2-tuple on success and a 3-tuple on exception | made it return `(ok, info, err)` on all paths | run completed |
| 2 | First barcode matching | 0 matches in all 22 sections, with `matrix_bc_not_in_positions` = n barcodes | numpy `bytes` were coerced via `astype(str)` giving `"b'ACGT...'"`, so strings never matched | explicit `x.decode("utf-8")` for bytes/`np.bytes_` | rerun: 100% match, 0 unmatched |
| 3 | Environment | `source activate.sh && python` never ran python | `activate.sh` exits 1 even when activation succeeds | use `source activate.sh; python ...` | scripts run in the `vbt` env |
| 4 | Integrity | no failures | — | — | 22/22 h5, 22/22 tar, 22/22 extract |

The first-run artefacts are overwritten by the successful reruns; the scripts
and this log document the corrections.

## 5. Spot QC

Script: `code/scripts/visium_02_qc_combine.py`
Per-spot metrics: `results/tables/visium_spot_qc_metrics.csv` (54,650 rows,
one per raw spot, includes the pass flag and failure reason)
Per-section inventory: `results/tables/visium_section_qc_inventory.csv`

### Thresholds (stated a priori; NOT tuned to any reported count)

| filter | threshold | justification |
|---|---|---|
| total counts | ≥ 500 UMIs | below this a Visium spot is dominated by ambient/empty capture; standard Visium lower bound |
| detected genes | ≥ 200 | 200 genes is a conventional floor separating low-complexity/ambient spots from real tissue |
| mitochondrial % | ≤ 20% | >20% mitochondrial reads marks damaged/necrotic tissue; 20% is the common Visium upper bound (a 15% alternative is shown in sensitivity) |

Mitochondrial content is computed from the 13 `MT-` genes present in
GRCh38-2020-A. No upper count cap is applied: a Visium spot contains multiple
cells, so high UMI counts are legitimate.

### Overall outcome

| group | raw spots | QC-passed | retained |
|---|---|---|---|
| tumor (12 sections) | 29,185 | 27,826 | 95.3% |
| adjacent-normal (10 sections) | 25,465 | 19,622 | 77.1% |
| **all 22 sections** | **54,650** | **47,448** | **86.8%** |

Failure attributions (a spot can fail more than one filter): 6,811 low counts,
3,085 low genes, 436 high mitochondrial %; 3,104 spots failed more than one.

### Threshold sensitivity

`results/tables/visium_qc_threshold_sensitivity.csv`

| min counts | min genes | max mito % | spots retained | % |
|---|---|---|---|---|
| 300 | 100 | 15 | 49,401 | 90.4 |
| 300 | 100 | 20 | 50,245 | 91.9 |
| **500** | **200** | **20** | **47,448** | **86.8** |
| 500 | 200 | 15 | 46,627 | 85.3 |
| 500 | 200 | 30 | 47,783 | 87.4 |
| 1000 | 300 | 20 | 41,508 | 75.9 |

### Per-section landscape

Median raw counts range from **263** (P16_B2) to **5,978** (P15_T1) — a >20×
depth range across sections. This is a property of the deposited data, not of
the filtering.

Low-retention sections are all adjacent-normal and low-depth:

| section | raw | QC | retained | median raw counts | median raw genes |
|---|---|---|---|---|---|
| P16_B2 | 3,351 | 825 | 24.6% | 263 | 218 |
| P16_B1 | 3,123 | 1,603 | 51.3% | 514 | 390 |
| P10_B2 | 1,842 | 1,067 | 57.9% | 597 | 439 |
| P10_B1 | 1,755 | 1,380 | 78.6% | 989 | 654 |

All 12 tumor sections retained 87–99%; the other six adjacent-normal sections
retained 92–98%. Downstream work should treat P16_B2 (and to a lesser degree
P16_B1/P10_B1/P10_B2) as low-power and consider a per-section minimum-spot
check before any per-section claim.

## 6. The paper's ~65,000 spots

The deposited **filtered** matrices contain **29,185** in-tissue spots across
the 12 LUAD tumor sections and **54,650** across all 22 sections. QC can only
remove spots, so the paper's ~65,000 post-QC figure **cannot be reached from
these filtered matrices by any thresholding**; most likely it derives from a
different counting basis (e.g. unfiltered/raw matrices that include all 4,992
array positions per section, or a different section subset). This is recorded
as a data-landscape discrepancy. **No threshold was adjusted toward it.**

## 7. Combined AnnData

### `data/processed/visium_sections_qc.h5ad` (primary hand-off)

- **47,448 spots × 36,601 genes**, 22 sections.
- `.X` = **raw integer counts** (CSR, int32) — retained for cell2location.
- `.layers['lognorm']` = log1p(CP10K), for visualization only.
- `.obs`: `section`, `patient`, `histology` (`tumor`/`adjacent-normal`),
  `sampling_site`, `disease`, `stage`, `age`, `sex`, `array_row`, `array_col`,
  `in_tissue`, `total_counts`, `n_genes_by_counts`, `pct_counts_mt`,
  `pct_counts_ribo`, `pct_counts_hb`, `qc_pass`, `qc_fail_reason`.
- `.obsm['spatial']` = `[pxl_col_in_fullres, pxl_row_in_fullres]` (full-resolution
  pixel coordinates), shape (47,448, 2).
- `.uns['spatial'][section]`: `images['lowres']`, `scalefactors`
  (spot_diameter_fullres, tissue_hires_scalef, tissue_lowres_scalef,
  fiducial_diameter_fullres), `metadata`, `section_metadata`.
- `.uns['visium_section_metadata']`: per-section JSON-safe record with
  library id, scalefactors, array row/col ranges, spot diameter and the path to
  the hires PNG.
- `.uns['qc_thresholds']` and `.uns['provenance']` record the exact parameters
  and source.
- Gene names are symbols (Ensembl IDs retained in `.var['gene_ids']`); names
  were made unique deterministically and are identical across all 22 sections.

**Spatial connectivity metadata preserved for the later graph step:**
`array_row`/`array_col` per spot plus per-section `scalefactors` and
`spot_diameter_fullres` are sufficient to build the paper's k=6 nearest-neighbour
graph per section without re-extracting the tarballs. The sections are not
coordinate-registered to each other (they are separate tissue slices), so any
graph must be built **within** section, never across sections.

**Deliberate omission:** only the low-resolution tissue image is embedded in
`.uns` (11 MB total). The high-resolution PNG is *not* embedded (would add
~260 MB); its original path is retained in `section_metadata.hires_image_path`
and the staging tree keeps the file. This does not affect deconvolution or
spot-level analyses.

### `data/raw/visium_sections_all_spots_raw_counts.h5ad` (audit copy)

All **54,650 raw spots**, raw counts, including QC failures, so nothing is
discarded. Same obs/obsm/uns structure and a `qc_pass` column.

## 8. Figure index

| file | shows |
|---|---|
| `results/figures/visium_qc_metrics_by_section.png` | per-section distributions of total counts, genes, mito% against thresholds |
| `results/figures/visium_qc_raw_vs_retained.png` | raw vs retained spots per section with % labels |
| `results/figures/visium_qc_spatial_retained_example.png` | spatial maps of passed/failed spots for P10_T1 and P10_B1 |
| `results/figures/visium_qc_inventory_table.png` | rendered per-section inventory |

## 9. Hand-off notes for cell2location

1. Use `.X` (raw counts) from `visium_sections_qc.h5ad`; do **not** use
   `layers['lognorm']` for the model.
2. Exclude CD276 from the reference/training genes (per requirements) at the
   cell2location step, not here — it is still present in this object.
3. Fit/build the spatial graph per `section` using `array_row`/`array_col`;
   spots are not comparable across sections.
4. Low-depth adjacent-normal sections (P16_B2, P16_B1, P10_B1, P10_B2) have
   fewer retained spots; report per-section n alongside any deconvolution
   result.

## 10. Reproducibility

- Random seed 42 (no stochastic step is used in this ingest/QC step).
- Scripts: `code/scripts/visium_01_verify_extract.py`,
  `code/scripts/visium_02_qc_combine.py`,
  `code/scripts/visium_03_sdrf_metadata_integrity.py`.
- Run logs: `logs/visium_01_run.log`, `logs/visium_01_verify_extract.log`,
  `logs/visium_02_run.log`, `logs/visium_02_qc_combine.log`,
  `logs/sdrf_metadata_integrity.log`.
- All scripts and logs cited above are present in this run (`LIVE`); the
  per-spot QC table `results/tables/visium_spot_qc_metrics.csv` is also present.
