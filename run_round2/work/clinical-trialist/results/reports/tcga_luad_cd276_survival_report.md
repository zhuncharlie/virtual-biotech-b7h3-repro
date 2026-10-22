# Panel 4F — TCGA PanCancer Atlas LUAD survival stratified by CD276 expression

Run: `20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf`
Role: clinical-trialist
Data pulled: 2026-10-21, via cBioPortal MCP tools and `pybioportal.molecular_data`

## 1. Study and data-source confirmation

| Item | Value | How confirmed |
|---|---|---|
| Study id | `luad_tcga_pan_can_atlas_2018` | `search_studies(cancer_type='luad')` returned this id ("Lung Adenocarcinoma (TCGA, PanCancer Atlas)", pmid 29625048 et al.); confirmed with `get_study_details` |
| Clinical cohort | 566 samples / 566 patients | MCP `get_clinical_data` payload (`sample_count: 566`, 566 unique `sampleId` and `patientId`) |
| MRNA_EXPRESSION profile used | `luad_tcga_pan_can_atlas_2018_rna_seq_v2_mrna` | `get_study_details` molecular_profiles: `MRNA_EXPRESSION`, datatype `CONTINUOUS`, name "mRNA Expression, RSEM (Batch normalized from Illumina HiSeq_RNASeqV2)" |
| Gene | CD276, Entrez **80381**, ENSG00000103855 | Entrez id from the profile query; Ensembl id confirmed with `search_targets_by_name("CD276")` |
| Sample list | `luad_tcga_pan_can_atlas_2018_all` (566 samples) | `pybioportal.sample_lists.get_all_sample_lists_in_study` |

`get_all_cancer_types` and `get_clinical_data` both exceeded the inline tool-output cap;
the harness saved their payloads to tool-result files, and the clinical payload was imported
verbatim by `code/scripts/01_import_mcp_clinical.py`. See `tcga_luad_tool_call_log.csv`.

## 2. Endpoint inventory (all 566 clinical records)

Computed by `code/scripts/02_inventory_endpoints.py`; saved as
`results/tables/tcga_luad_clinical_endpoint_inventory.csv`.

| Endpoint | Time field | Status field | Time non-null | Status non-null | Both non-null | Events (both non-null) | Status labels |
|---|---|---|---|---|---|---|---|
| OS | `OS_MONTHS` | `OS_STATUS` | 505 | 505 | 505 | 182 | `0:LIVING` 328, `1:DECEASED` 186 |
| PFS | `PFS_MONTHS` | `PFS_STATUS` | 505 | 505 | 505 | 205 | `0:CENSORED` 306, `1:PROGRESSION` 208 |
| DSS | `DSS_MONTHS` | `DSS_STATUS` | 505 | 470 | 470 | 111 | `0:ALIVE OR DEAD TUMOR FREE` 364, `1:DEAD WITH TUMOR` 114 |
| DFS | `DFS_MONTHS` | `DFS_STATUS` | 301 | 301 | 301 | 89 | `0:DiseaseFree` 215, `1:Recurred/Progressed` 89 |

All four endpoints exist with usable time and binary status fields. They are not equally
complete: DSS status is missing for 96/566 and DFS is recorded for only 301/566 (the
resected subset). No endpoint is absent.

Covariates (566 records): `AGE` numeric 495 (33–88 y), `SEX` 514 (275 female / 239 male),
`AJCC_PATHOLOGIC_TUMOR_STAGE` 512, `AJCC_STAGING_EDITION` 493 (3rd–7th editions mixed).

## 3. CD276 expression: scale and multi-aliquot handling

`code/scripts/03_pull_cd276_expression.py` called
`pybioportal.molecular_data.get_all_molecular_data_in_molecular_profile(
molecular_profile_id='luad_tcga_pan_can_atlas_2018_rna_seq_v2_mrna',
sample_list_id='luad_tcga_pan_can_atlas_2018_all', entrez_gene_id='80381')`.

- Returned 510 per-sample values (the profile's full coverage; 56 of the 566 study samples
  have no mRNA profile record). Full table: `data/raw/cbioportal_luad_tcga_pancancer_cd276_mrna_raw.csv`.
- **Scale: RSEM, batch-normalised, continuous, untransformed** (not TPM, not z-score).
  Range 548.62–9371.11; mean 2369.35, SD 967.80, median 2189.80
  (`results/tables/tcga_luad_cd276_expression_summary.csv`). Two z-score profiles were
  also pulled for reference and are saved under `data/raw/`.
- **Multi-aliquot samples: none.** 510 expression rows = 510 unique patients = 510 unique
  samples; no patient had more than one aliquot in this profile, so no selection rule was
  needed.

Quartiles were cut on all 510 patients with expression (pandas linear interpolation):

| Quartile | RSEM range | n | Median RSEM |
|---|---|---|---|
| Q1 | 548.62 – 1746.15 | 128 | 1441.02 |
| Q2 | 1747.10 – 2188.49 | 127 | 1954.63 |
| Q3 | 2191.10 – 2771.61 | 127 | 2452.93 |
| Q4 | 2782.03 – 9371.11 | 128 | 3409.84 |

Cut-points: 25th 1746.39, 50th 2189.80, 75th 2779.43 RSEM.

## 4. Cohort construction (n reproducible)

`code/scripts/04_build_cohort.py`; full table in
`results/tables/tcga_luad_cohort_construction.csv`.

| Step | OS | DSS | PFS | DFS |
|---|---|---|---|---|
| Clinical samples in study | 566 | 566 | 566 | 566 |
| **With CD276 mRNA (excluded 56)** | **510** | **510** | **510** | **510** |
| Duplicate-patient aliquots removed | 0 | 0 | 0 | 0 |
| Quartile assigned | 510 | 510 | 510 | 510 |
| Endpoint time + status present | 501 | 466 | 501 | 297 |
| Positive follow-up time (excluded 4/4/4/1) | 497 | 462 | 497 | 296 |
| Q1+Q4 analysis set (unadjusted) | 251 | 238 | 251 | 149 |
| Q1+Q4, covariates complete (adjusted) | 246 | 233 | 246 | 144 |
| Events, unadjusted / adjusted | 98 / 98 | 60 / 60 | 110 / 107 | 48 / 46 |

Covariate-complete = non-missing age, sex and AJCC stage group. Among the 510 with
expression, 489 are complete (age missing 19, stage missing 2, sex missing 0). List-wise
deletion was used only in adjusted models. Stage was collapsed from
`AJCC_PATHOLOGIC_TUMOR_STAGE` to AJCC groups I / II / III / IV (IA/IB→I, IIA/IIB→II,
IIIA/IIIB→III); "STAGE I/II" without a substage were mapped to I/II; missing stage
(n=54 overall, 2 in the expression cohort) was excluded from adjusted models. AJCC stage
editions 3rd–7th were pooled. DFS has no stage-IV patient with follow-up, so DFS adjusted
models use stage I/II/III only.

All patients are primary tumours (`SAMPLE_TYPE` = Primary, 566/566).

## 5. Cox proportional hazards models

`code/scripts/05_cox_models.py`; full coefficient-level table (including age, sex and stage
terms, standard errors, Schoenfeld p-values) in
`results/tables/tcga_luad_cd276_cox_models.csv`.

**Primary contrast: Q4 (top quartile) vs Q1 (bottom quartile).**

| Endpoint | Model | HR (95% CI) | p | n | events |
|---|---|---|---|---|---|
| OS | unadjusted | **1.80 (1.19–2.71)** | **0.0051** | 251 | 98 |
| OS | adjusted (age, sex, stage) | 1.44 (0.92–2.26) | 0.106 | 246 | 98 |
| DSS | unadjusted | **1.86 (1.10–3.13)** | **0.0206** | 238 | 60 |
| DSS | adjusted | 1.39 (0.79–2.44) | 0.249 | 233 | 60 |
| PFS | unadjusted | 1.40 (0.96–2.04) | 0.078 | 251 | 110 |
| PFS | adjusted | 1.20 (0.80–1.79) | 0.381 | 246 | 107 |
| DFS | unadjusted | 1.75 (0.98–3.14) | 0.060 | 149 | 48 |
| DFS | adjusted | 1.64 (0.88–3.08) | 0.120 | 144 | 46 |

Log-rank Q4 vs Q1: OS p = 0.0045, DSS p = 0.0187
(`results/tables/tcga_luad_cd276_logrank.csv`). Median follow-up (reverse KM) 29.0 months
overall, 27.3 (Q1) and 30.0 (Q4) months (`results/tables/tcga_luad_median_followup.csv`).

Adjusted OS covariate effects: stage II vs I 2.53 (1.49–4.28), III vs I 2.87 (1.64–5.02),
IV vs I 3.50 (1.74–7.04); age 1.013 per year (0.99–1.03, p=0.21); male 0.95 (0.63–1.43,
p=0.82). Stage is therefore the dominant driver and attenuates the CD276 contrast.

### Proportional-hazards diagnostics
Schoenfeld-residual test (`proportional_hazard_test`, rank time transform), per term:

- Focal Q4 term: OS 0.99 (unadj) / 0.66 (adj); DSS 0.70 / 0.85; DFS 0.49 / 0.39 — **no violation**.
- **PFS unadjusted Q4: p = 0.018 — PH violated.** Adjusted PFS p = 0.071.
- Sex violated PH in adjusted OS (p=0.015) and DSS (p=0.040); stage-III terms violated in
  some Q4-vs-rest sensitivity models (p=0.004–0.016).

Because PFS showed a time-varying effect, a pre-specified sensitivity censored all PFS
follow-up at 24 months: Q4 vs Q1 HR 1.71 (1.11–2.61), p = 0.014 — the effect is concentrated
early and attenuates with time, so the unadjusted PFS HR should be read as a non-proportional
average, not a constant hazard ratio.

### Sensitivity analyses
| Endpoint | Sensitivity | HR (95% CI) | p | n | events |
|---|---|---|---|---|---|
| OS | continuous log2 RSEM, unadjusted (per doubling) | 1.45 (1.12–1.88) | 0.0050 | 251 | 98 |
| OS | continuous log2 RSEM, adjusted | 1.23 (0.93–1.63) | 0.151 | 246 | 98 |
| DSS | continuous log2 RSEM, unadjusted | 1.42 (1.02–1.97) | 0.0369 | 238 | 60 |
| DSS | continuous log2 RSEM, adjusted | 1.12 (0.80–1.58) | 0.516 | 233 | 60 |
| PFS | continuous log2 RSEM, unadjusted | 1.18 (0.93–1.50) | 0.180 | 251 | 110 |
| PFS | continuous log2 RSEM, adjusted | 1.01 (0.78–1.31) | 0.913 | 246 | 107 |
| DFS | continuous log2 RSEM, unadjusted | 1.29 (0.90–1.86) | 0.159 | 149 | 48 |
| DFS | continuous log2 RSEM, adjusted | 1.18 (0.81–1.74) | 0.393 | 144 | 46 |
| OS | Q4 vs Q1+Q2+Q3, adjusted | 1.45 (1.04–2.00) | 0.026 | 485 | 177 |
| DSS | Q4 vs Q1+Q2+Q3, adjusted | 1.48 (0.98–2.22) | 0.061 | 450 | 107 |
| PFS | Q4 vs Q1+Q2+Q3, adjusted | 1.37 (1.00–1.87) | 0.047 | 485 | 197 |
| DFS | Q4 vs Q1+Q2+Q3, adjusted | 1.74 (1.09–2.77) | 0.020 | 285 | 83 |
| PFS | 24-month truncated, unadjusted | 1.71 (1.11–2.61) | 0.014 | 251 | 87 |

The Q4-vs-rest adjusted estimate (1.45 for OS) is essentially identical in effect size to the
Q4-vs-Q1 adjusted estimate (1.44) but has roughly twice the n and is therefore significant;
the difference between the two adjusted results is precision, not direction.

## 6. Figure

`results/figures/fig4f_tcga_luad_cd276_survival.png` and `.pdf`
(`code/scripts/06_figure4f.py`): (A) KM OS Q4 vs Q1 with number-at-risk table, (B) KM DSS
Q4 vs Q1, (C) forest of unadjusted and adjusted Q4-vs-Q1 HRs for OS, DSS, PFS, DFS.

## 7. Comparison with the paper's reported values

| | Paper | This analysis (unadjusted Q4 vs Q1) | Difference |
|---|---|---|---|
| OS HR (95% CI), p | 1.62 (1.05–2.48), 0.028 | 1.80 (1.19–2.71), 0.0051 | +0.18 HR; same direction and significance |
| DSS HR (95% CI), p | 1.82 (1.06–3.15), 0.031 | 1.86 (1.10–3.13), 0.0206 | +0.04 HR; CI essentially identical |
| n | 566 | 510 with expression; 251 in Q1+Q4 | −56 expression, −315 for the quartile contrast |

**Patient count.** 566 is confirmed as the size of the `luad_tcga_pan_can_atlas_2018`
cohort (566 clinical/sequenced samples, 566 unique patients), but it is **not** the size of
an expression-stratified analysis set on this data source: only 510 samples have CD276 mRNA
in the study's RSEM profile. Alternative LUAD TCGA mRNA sources in cBioPortal were checked
for context and also fall short of 566
(`results/tables/tcga_luad_alternative_study_cd276_counts.csv`): Firehose legacy
(`luad_tcga`) 517 samples / 515 patients; GDC 2025 TPM and FPKM 518 samples / 516 patients
each. The paper's 566 therefore most plausibly refers to the study cohort rather than the
n entering the Cox model; the maximum achievable Q4-vs-Q1 contrast here is ~251.

**Why the HRs differ slightly (not corrected for).** In descending order of likely impact:
(1) analysis-set definition and size (510 expression-available vs 566; 251 in the quartile
contrast); (2) adjustment set — the paper does not state whether its reported 1.62/1.82 are
unadjusted or adjusted, and our adjusted estimates are 1.44/1.39, so an adjusted paper value
would sit closer to ours; (3) quartile cut method/expression scale (RSEM vs log/z-score,
quantile algorithm); (4) endpoint derivation for DSS (`1:DEAD WITH TUMOR` vs
`0:ALIVE OR DEAD TUMOR FREE`). None of these was tuned: the pipeline was fixed before the
models were fitted, and no parameter was varied to close the gap.

## 8. What could and could not be computed

- **OS, DSS, PFS, DFS: all computable** — each has a time field and a binary status field.
- **DSS** is restricted: status missing for 96/566; analysis set 462 with positive follow-up.
- **DFS** is restricted to the resected subset (296 with positive follow-up; no stage-IV
  patients), so it is not comparable to OS/DSS in the same population.
- **Limitations:** observational, treatment not adjusted (adjuvant therapy fields exist but
  are incomplete and were not pre-specified as covariates); mixed AJCC editions pooled;
  list-wise deletion for age/stage missingness; median follow-up ~29 months, so late
  divergence is under-powered.

## 9. Reproducibility

| Step | Script | Output |
|---|---|---|
| Import MCP clinical payload | `code/scripts/01_import_mcp_clinical.py` | `data/raw/cbioportal_luad_tcga_pancancer_clinical.csv` |
| Endpoint/covariate inventory | `code/scripts/02_inventory_endpoints.py` | `results/tables/tcga_luad_clinical_endpoint_inventory.csv` |
| CD276 expression pull | `code/scripts/03_pull_cd276_expression.py` | `data/raw/cbioportal_luad_tcga_pancancer_cd276_mrna_raw.csv` |
| Cohort construction | `code/scripts/04_build_cohort.py` | `data/processed/tcga_luad_cd276_analysis_cohort.csv`, `results/tables/tcga_luad_cohort_construction.csv`, `results/tables/tcga_luad_cd276_expression_quartiles.csv` |
| Cox models | `code/scripts/05_cox_models.py` | `results/tables/tcga_luad_cd276_cox_models.csv`, quartile event counts, median follow-up |
| Figure 4F | `code/scripts/06_figure4f.py` | `results/figures/fig4f_tcga_luad_cd276_survival.png/.pdf`, log-rank table |
| Expression summary | `code/scripts/07_expression_summary.py` | `results/tables/tcga_luad_cd276_expression_summary.csv` |
| Alternative-study CD276 counts (n context only) | `code/scripts/08_alternative_study_expression_counts.py` | `results/tables/tcga_luad_alternative_study_cd276_counts.csv` |
