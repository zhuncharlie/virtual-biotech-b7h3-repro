# CD276 / B7-H3 Functional Genomics: LUAD and SCLC

**Agent:** functional-genomics-analyst
**Date:** 2026-10-20
**Target:** CD276 (B7-H3), Ensembl ENSG00000103855, chromosome 15q24.1, protein-coding, annotated as a surface antigen
**Scope:** LUAD and SCLC only. NSCLC and other lineages are used only as labeled selectivity comparators.
**Data sources:** DepMap CRISPR (via `mcp__functional_genomics__query_gene_essentiality` and `compare_essentiality_across_diseases`); Open Targets target annotation; Tahoe-100M attempted but unavailable (see Section 6).

---

## 1. Bottom line

**DepMap does NOT support an intrinsic-dependency rationale for CD276 in LUAD or SCLC.** CD276 is not essential in either histology, in any other lineage tested, or in the dataset overall. This is an expected and non-disqualifying result for a surface-antigen payload strategy (ADC, bispecific, CAR), where the therapeutic mechanism is delivery of a cytotoxic or immune payload to antigen-expressing cells, not inhibition of a growth dependency.

- **LUAD:** 46 cell lines; mean gene effect **-0.230**; median **-0.245**; **2.2%** essential at the <-0.5 threshold (1/46); **0%** at <-0.7.
- **SCLC:** 25 cell lines; mean gene effect **-0.204**; median **-0.181**; **0%** essential at <-0.5; **0%** at <-0.7.
- **Selectivity:** none. LUAD vs other NSCLC mean difference +0.008 (Welch p=0.77); LUAD vs all other lineages -0.009 (p=0.66); SCLC vs all other lineages +0.017 (p=0.49). At the disease-label level, NSCLC ranks 30/78 and Lung Neuroendocrine Tumor 40/78 by mean essentiality (1 = most essential).
- **Antigen expression (supportive, not a dependency claim):** CD276 is expressed in essentially all LUAD and SCLC lines (SCLC 100% >4; LUAD 93.2% >4 on the DepMap expression scale). Absolute units are not stated by the tool and are likely log2(TPM+1).

**Evidence strength: strong** that CD276 is not an intrinsic dependency in LUAD/SCLC (large, direct, internally consistent CRISPR dataset; 46 + 25 lines; all comparators null). **Not established** in this stream: normal-tissue expression/safety, surface-protein density, internalization, and Tahoe perturbation data. DepMap cannot address those.

---

## 2. Data and method

### 2.1 Query and raw data
- `mcp__functional_genomics__query_gene_essentiality(gene_id="ENSG00000103855")` returned 1,183 cancer cell lines across 29 tissue blocks (29 tissues / 78 disease labels). The raw JSON is saved at `data/raw/cd276_depmap_essentiality_raw.json`.
- `mcp__functional_genomics__compare_essentiality_across_diseases(gene_id="ENSG00000103855")` returned disease-level summary for 78 disease labels.
- Target annotation from `mcp__target__get_target_info("ENSG00000103855")`: approved symbol CD276; target class **Surface antigen**; subcellular location Membrane/Vesicles; antibody tractability "Advanced Clinical" = true.

### 2.2 Histology assignment (important)
The DepMap extract exposes only broad disease labels:
- **"Non-Small Cell Lung Cancer" (n=98)** collapses LUAD, lung squamous, large-cell and other NSCLC.
- **"Lung Neuroendocrine Tumor" (n=26)** mixes SCLC with pulmonary carcinoid.

The tool's disease filter cannot be used to isolate SCLC: because "Non-Small Cell Lung Cancer" contains the substring "Small Cell Lung Cancer", `query_gene_essentiality(disease="Small Cell Lung Cancer")` returned all **98 NSCLC** lines and zero SCLC-specific lines. `disease="Lung Adenocarcinoma"` returned **0** lines because the label does not exist in the extract. This is a genuine tool/matching limitation, recorded here so the filter is not mistaken for a biological result.

To honor the LUAD/SCLC scope, histology was assigned from documented cell-line identity (prior knowledge: Cellosaurus/ATCC/CCLE-derived histology), using only unambiguous lines. Derivatives (`A549_CRAF_KD`, `HCC-827-GR5`, `NCI-H157-DM`) were excluded from the core sets to avoid pseudo-replication. The mapping is saved at `results/tables/cd276_histology_mapping.csv` and the annotation is in every per-cell-line row.

- **LUAD core (n=46):** A549, ABC-1, COR-L105, EKVX, HCC-44, HCC-78, HCC-461, HCC-827, HCC-1359, HOP-62, LCAM1, LOU-NH91, LXF-289, NCI-H23, NCI-H358, NCI-H441, NCI-H522, NCI-H1355, NCI-H1373, NCI-H1437, NCI-H1568, NCI-H1573, NCI-H1648, NCI-H1650, NCI-H1666, NCI-H1693, NCI-H1792, NCI-H1793, NCI-H1944, NCI-H1975, NCI-H1993, NCI-H2009, NCI-H2023, NCI-H2030, NCI-H2087, NCI-H2110, NCI-H2122, NCI-H2126, NCI-H2172, NCI-H2291, NCI-H3122, PC-14, RERF-LC-Ad1, RERF-LC-Ad2, RERF-LC-AI, VMRC-LCD.
  - Calu-3 is a documented LUAD line but is **absent from this DepMap extract**; it is therefore not in n=46.
- **SCLC core (n=25):** COR-L279, COR-L311, COR-L47, DMS 273, DMS 53, HCC-33, Lu-134-A, Lu-135, Lu-139, Lu-165, NCI-H1048, NCI-H1092, NCI-H1694, NCI-H1836, NCI-H1882, NCI-H209, NCI-H211, NCI-H2171, NCI-H2286, NCI-H446, NCI-H510, NCI-H526, NCI-H82, SCLC-22H, SHP-77.
  - NCI-H727 (pulmonary carcinoid) was excluded from SCLC and kept as a separate labeled group.
- **Comparators:** Other NSCLC = remaining 52 NSCLC lines (squamous, large-cell, adenosquamous, unclassified, plus derivatives). Other lineages = 1,041 non-lung cancer lines. Non-cancerous = 16 lines.

### 2.3 Statistics
Per-group n, mean, median, SD, min, quartiles, max; fractions below -0.3, -0.5 (standard essentiality threshold), and -0.7 (strong); explicit histogram bins; Welch t-test and Mann-Whitney U with Cohen's d. Code: `code/scripts/cd276_depmap_analysis.py`.

---

## 3. Results

### 3.1 Required LUAD and SCLC cell-line table
`results/tables/cd276_depmap_luad_sclc.csv` — 71 rows (46 LUAD + 25 SCLC) with cell line, DepMap ID, histology group, DepMap disease label, tissue, gene effect, expression, and histology evidence.

### 3.2 Gene-effect distribution
`results/tables/cd276_depmap_group_summary.csv`, `results/tables/cd276_depmap_gene_effect_bins.csv`, `results/figures/cd276_depmap_luad_sclc_distribution.png`

| Group | n | Mean | Median | SD | IQR (Q1–Q3) | Min–Max | Fraction <-0.5 | Fraction <-0.7 |
|---|---:|---:|---:|---:|---|---|---:|---:|
| **LUAD** | 46 | -0.230 | -0.245 | 0.139 | -0.314 to -0.150 | -0.540 to +0.107 | 2.2% (1/46) | 0% |
| **SCLC** | 25 | -0.204 | -0.181 | 0.118 | -0.265 to -0.123 | -0.482 to -0.035 | 0% | 0% |
| Other NSCLC | 52 | -0.238 | -0.247 | 0.137 | -0.324 to -0.162 | -0.509 to +0.120 | 3.8% (2/52) | 0% |
| Other lineages | 1,041 | -0.221 | -0.212 | 0.144 | -0.304 to -0.135 | -0.963 to +0.298 | 3.4% | 0.4% |
| Non-cancerous lines | 16 | -0.163 | -0.142 | 0.082 | -0.220 to -0.100 | -0.322 to -0.039 | 0% | 0% |

**Distribution shape.** In LUAD, 25/46 (54.3%) of lines fall between -0.3 and -0.1; 11/46 (23.9%) between -0.5 and -0.3; 8/46 (17.4%) between -0.1 and +0.1; one line between -0.7 and -0.5 (NCI-H1573, -0.540); one above +0.1. In SCLC, 16/25 (64%) fall between -0.3 and -0.1 and 5/25 (20%) between -0.1 and +0.1; no SCLC line reaches -0.5. The distributions are unimodal and centered near -0.2, the null region for DepMap gene effect. There is no subgroup of dependent lines.

The single LUAD line below -0.5 (NCI-H1573, -0.540) is only marginally past the threshold; it is not accompanied by any other dependent line and does not survive a strong-essentiality threshold. It is most plausibly noise/line-specific, not a subgroup signal.

### 3.3 Selectivity
`results/tables/cd276_depmap_group_comparisons.csv`, `results/tables/cd276_depmap_disease_comparator.csv`

| Comparison | Mean difference (A−B) | Cohen's d | Welch p | Mann–Whitney p |
|---|---:|---:|---:|---:|
| LUAD vs Other NSCLC | +0.008 | 0.06 | 0.77 | 0.83 |
| LUAD vs Other lineages | -0.009 | -0.06 | 0.66 | 0.43 |
| SCLC vs Other lineages | +0.017 | 0.12 | 0.49 | 0.33 |
| SCLC vs Other NSCLC | +0.034 | 0.26 | 0.26 | 0.11 |
| LUAD vs SCLC | -0.026 | -0.20 | 0.40 | 0.25 |

All differences are small (|d| ≤ 0.26) and non-significant. At the disease-label level, **Non-Small Cell Lung Cancer ranks 30th of 78** by mean gene effect (more negative = more essential) and **Lung Neuroendocrine Tumor ranks 40th of 78**. Most diseases above them are small-n categories (n=1-4) with noisy means; among large lineages, CD276 is uniformly non-essential. **Assessment: no cancer-type selectivity; CD276 is neither broadly essential nor selectively essential.**

### 3.4 Antigen expression (context for a payload strategy)
`results/tables/cd276_depmap_group_summary.csv`, Figure panel B

| Group | n with expression | Mean | Median | Range | Fraction >4 | Fraction >5 |
|---|---:|---:|---:|---|---:|---:|
| **LUAD** | 46 | 5.46 | 5.57 | 3.14–7.62 | 93.2% | 68.2% |
| **SCLC** | 25 | 5.39 | 5.33 | 4.08–6.23 | 100% | 80.0% |
| Other NSCLC | 52 | 5.68 | 5.76 | 4.28–7.57 | 100% | 74.5% |
| Other lineages | 1,041 | 5.23 | 5.66 | 0.00–9.68 | 85.4% | 71.4% |
| Non-cancerous lines | 16 | 5.91 | 6.08 | 2.28–6.87 | 92.9% | 92.9% |

CD276 transcript is present in essentially every LUAD and SCLC line, and SCLC shows the most uniform expression (all 25 lines >4). This is consistent with B7-H3 being a broadly expressed surface antigen, but it is **not** target-selectivity evidence: expression is comparably high in other lineages and in the 16 "Non-Cancerous" lines. DepMap expression is bulk transcript-level and cannot establish protein density, membrane localization, or the tumor-to-normal ratio. Note the expression units are not defined by the tool; values are likely log2(TPM+1), so only relative comparisons are appropriate.

---

## 4. Interpretation for a B7-H3 payload strategy

1. **Intrinsic dependency rationale: absent.** CD276 knockout/knockdown does not impair LUAD or SCLC cell fitness. There is no synthetic-lethal or oncogene-addiction case here.
2. **This is not disqualifying.** For an ADC, bispecific engager, or CAR, the required properties are (a) antigen presence on tumor cells, (b) sufficient antigen density and accessibility, (c) a tumor-to-normal expression window, and (d) efficient payload delivery/internalization. None of these is a CRISPR dependency. A non-essential surface antigen is the expected profile for this modality.
3. **What DepMap does and does not rule out.** It rules out a monotherapy "inhibit B7-H3 signaling to kill tumor cells" rationale in these histologies. It does not rule out payload delivery. It also cannot assess normal-tissue expression; the high expression in the 16 non-cancerous lines is a caution flag that must be resolved with normal-tissue IHC/single-cell data, not treated as a safety verdict.
4. **Resistance/combination hypotheses are not addressed.** CD276 loss could be a resistance mechanism to a B7-H3 ADC (antigen escape). DepMap cannot model that; it would require antigen-negative vs antigen-positive isogenic pairs or clinical post-progression samples.

---

## 5. Limitations and caveats

- **Cancer cell lines only.** DepMap has no normal-tissue essentiality or expression data. No safety claim can be made from this stream.
- **Histology is curated.** The DepMap extract does not separate LUAD from other NSCLC, and its SCLC lines sit under "Lung Neuroendocrine Tumor". The 46-line LUAD set is conservative and excludes ambiguous lines. As a sensitivity check, the entire 98-line NSCLC label has mean -0.235 (vs -0.230 in the curated LUAD set), so the conclusion is insensitive to LUAD misclassification. The 25-line SCLC set excludes one carcinoid line; even including all 26 neuroendocrine lines gives mean -0.210.
- **Tool quirk.** `disease="Small Cell Lung Cancer"` returns NSCLC because of substring matching; any downstream user should not use that filter. `disease="Lung Adenocarcinoma"` returns zero.
- **Expression scale.** Units are not stated by the MCP tool; treat as relative.
- **CRISPR gene effect is a fitness readout, not a protein-abundance or antibody-accessibility readout.** It does not model extracellular payload delivery, bystander effect, or immune engagement.
- **Calu-3 absent** from the extract.
- **Tahoe-100M unavailable** (Section 6).

---

## 6. Tahoe-100M: not established

Three Tahoe-100M calls failed with the same server error: `TAHOE_DATA_PATH not set in environment. Set it to the directory containing Tahoe pseudobulk parquet files.`
- `find_drugs_affecting_gene(gene_name="CD276")` — failed
- `query_drug_perturbation(drug_name="Enoblituzumab")` — failed
- `query_drug_perturbation(drug_name="Ifinatamab deruxtecan")` — failed

No prepared Tahoe pseudobulk directory or parquet shard exists in the project tree (only `tools/prepare_tahoe.py` and setup documentation); a prior run documented the same failure. Web search/scraping is disabled, so no alternative perturbation source was used.

**Consequence:** It is **not established** whether any perturbation modulates CD276 expression, and it is **unknown** whether B7-H3-targeted agents are represented in Tahoe-100M. This is a data-availability failure, **not** a zero-result query and **not** evidence of absence. The DepMap conclusion is independent of Tahoe.

---

## 7. Artifacts

| Path | Contents |
|---|---|
| `results/tables/cd276_depmap_luad_sclc.csv` | Required per-cell-line table: 46 LUAD + 25 SCLC lines with gene effect, expression, labels, histology evidence |
| `results/tables/cd276_depmap_group_summary.csv` | Distribution summary by group: n, mean, median, SD, IQR, min/max, essential fractions, expression coverage |
| `results/tables/cd276_depmap_gene_effect_bins.csv` | Explicit histogram bins of gene effect per group |
| `results/tables/cd276_depmap_group_comparisons.csv` | Pairwise LUAD/SCLC/comparator tests with Cohen's d |
| `results/tables/cd276_depmap_disease_comparator.csv` | 78-disease mean essentiality ranking (reproduces `compare_essentiality_across_diseases`) |
| `results/tables/cd276_depmap_broad_label_sensitivity.csv` | Broad-label sensitivity analysis (NSCLC, Lung Neuroendocrine Tumor) |
| `results/tables/cd276_histology_mapping.csv` | Auditable line-level histology assignment and evidence |
| `results/tables/cd276_depmap_all_cell_lines_annotated.csv` | All 1,183 lines annotated by group |
| `results/tables/cd276_tahoe_query_status.json` | Tahoe-100M failure record, exact errors, scope of the gap |
| `results/figures/cd276_depmap_luad_sclc_distribution.png` (and .pdf) | Two-panel distribution: gene effect and CD276 expression by group |
| `data/raw/cd276_depmap_essentiality_raw.json` | Raw MCP essentiality result |
| `code/scripts/cd276_depmap_analysis.py` | Reproducible analysis script |
