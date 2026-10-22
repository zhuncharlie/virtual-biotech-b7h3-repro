# CD276 (B7-H3) genetic evidence in LUAD and SCLC

**Target:** CD276 / B7-H3, ENSG00000103855 (verified via `mcp__target__search_targets_by_name`; single hit).

**Location (GRCh38):** chr15:73,683,966-73,714,514; canonical TSS 73,684,383 (Open Targets target info). Note: CD276 is on chromosome 15 (16q24-like assumptions would be wrong).

## Scope and disease identifiers

| Histology | Open Targets disease ID | Verification |
|---|---|---|
| Lung adenocarcinoma (LUAD) | `EFO_0000571` | `search_diseases_by_name("lung adenocarcinoma")` returned this exact record; `get_disease_info` confirmed name/ontology |
| Small cell lung carcinoma (SCLC) | `EFO_0000702` | `search_diseases_by_name("small cell lung carcinoma")`; note the exact-string query `"small cell lung cancer"` returned **0 results**, so the broader synonym was used |

Excluded terms: `MONDO_0000503` (adenocarcinoma in situ), `MONDO_0003892` (acinar), `EFO_1000046` (papillary), `EFO_0005288` (duplicate NSCLC-adeno term), `MONDO_0003438` (combined SCLC), `EFO_0003060` (NSCLC, out of scope). SCLC study lists also surfaced NSCLC and mixed SCLC/NSCLC studies (e.g., GCST002993, GCST012199, GCST008834, FINNGEN_R12_C3_NSCLC_*); these were excluded from the analysis.

## Method and tool limitations (read before interpreting)

The genetics MCP exposes GWAS/credible-set data by **study ID, variant, chromosome or region** — there is no gene-by-disease GWAS query. I therefore:
1. Queried the whole CD276 window (chr15:73.5-73.9 Mb) across all studies (303 credible sets), and
2. Pulled full credible sets for the largest available LUAD (5) and SCLC (3) GWAS, and checked each for a CD276-locus variant.

**Limitation:** this database stores fine-mapped/curated credible sets, not genome-wide summary statistics (e.g., the 109k-sample LUAD study returned only 3 credible sets). A negative result means *no CD276-locus credible set in the queried data* — it does not exclude a sub-threshold or non-fine-mapped association. This is "no association found in the queried database," not "no biology."

## GWAS associations — LUAD and SCLC

**Result: no CD276-locus association found in either histology.**

- 8 major studies queried (5 LUAD, 3 SCLC; 24.1k-379.7k samples). **0/8** contained a credible set within +/-500 kb of the CD276 TSS, and **0/8** contained a variant in the CD276 gene body.
- Closest chr15 credible sets in these studies were **~4.88-4.93 Mb away** (the 15q25 CHRNA5/CHRNA3 nicotinic-receptor locus), or ~24.6 Mb away.
- At the region level, 116 distinct GWAS studies have credible sets in the CD276 window, but **0 are LUAD or SCLC studies**.
- The 123 GWAS credible sets in the CD276 window are instead for non-lung traits. Verified examples: alanine aminotransferase, aspartate aminotransferase, AST/ALT ratio, gamma-glutamyl transferase, sex hormone-binding globulin, BMI, statin use. **41 credible sets fall inside the CD276 gene body**, all from these non-lung traits — i.e., CD276 is a genuine pleiotropic biomarker locus, not a lung-cancer locus in this database.

Supplementary: no LUAD/SCLC study appears in the 67 CD276 L2G loci (below), so the two independent checks agree.

## L2G predictions

- **67** L2G predictions for ENSG00000103855 (min_score 0.1); **56 with score >= 0.5**, max score **0.953** (GCST90019492, ALT levels).
- **0/67 loci derive from a LUAD or SCLC GWAS.** All 67 are within the CD276 window and come from biomarker/other-trait GWAS.
- Interpretation: the high L2G scores are real but **disease-mismatched**. They support CD276 as the effector gene at a liver-enzyme/biomarker locus, not as a LUAD/SCLC causal gene.

## QTL colocalization (disease-agnostic)

Features are attached to the L2G loci, not to LUAD/SCLC loci. There is **no disease-QTL colocalization to report for LUAD or SCLC**, because neither disease has a GWAS locus at CD276.

| QTL | Loci with CLPP > 0.01 | Loci with H4 > 0.6 | Max CLPP | Max H4 | Top-locus trait |
|---|---|---|---|---|---|
| eQTL | 56/67 | 37/67 | 0.269 | 0.998 | AST levels |
| pQTL | 16/67 | 7/67 | 0.294 | 0.998 | AST/ALT ratio |
| sQTL | 54/67 | 36/67 | 0.281 | 0.998 | BMI |

These show CD276 expression/protein/splicing is under strong cis-genetic control (a well-powered pQTL exists: UKB-PPP CD276, n=33,649). That is evidence of assayability and biological regulation, **not** of disease causality.

## Target prioritisation scores

`get_target_prioritisation_scores` returned a **single global record with no disease stratification**; per-disease scores for EFO_0000571 / EFO_0000702 could not be produced with this tool. Global values: hasPocket 0, hasLigand 0, hasSmallMoleculeBinder 0, geneticConstraint -0.14, maxClinicalTrialPhase 0.5, isInMembrane 0, isSecreted 0, mouseKOScore -0.19. The `isInMembrane`/`isSecreted` zeros conflict with the known type I transmembrane biology (see prior knowledge) and should not be over-read.

## Tractability by modality

| Modality | Readout | Assessment |
|---|---|---|
| Antibody | **Advanced Clinical = true**; signal peptide/TM = true; no approved drug | Strongly antibody-tractable |
| Small molecule | All buckets false (no ligand, no pocket, no druggable family, no clinical) | Not small-molecule tractable |
| PROTAC | No approved/clinical/literature; database ubiquitination and half-life data only | Weak/annotative only |

The antibody "Advanced Clinical" flag is an aggregate across indications and is **not** specific to LUAD or SCLC.

## Candid interpretation

**Genetic evidence for CD276 as a LUAD or SCLC driver/causal target: ABSENT** in the queried genetics database. There is no disease-locus association, no disease-relevant L2G, and no disease-QTL colocalization in either histology. What exists is a strong, reproducible *biomarker* locus (liver enzymes, SHBG, BMI) and strong cis-QTL regulation of CD276 itself.

CD276 is an immune-checkpoint-family surface antigen (B7 family), **not a classic genetically driven oncogene**. Its therapeutic rationale in LUAD/SCLC is therefore antigen expression/tumor selectivity and antibody-drug-conjugate delivery, not human genetics. *(Prior knowledge, not derived from the MCP tools: B7-H3 is overexpressed in SCLC and other tumors and is targeted by antibody-drug conjugates such as ifinatamab deruxtecan; this should be validated by the expression/functional workstreams.)*

**Bottom line:** do not manufacture a genetic rationale for CD276 in LUAD/SCLC. The genetic stream is negative; the antibody tractability and QTL/expression data are supporting, not causal.

## Artifact index

- `results/tables/cd276_disease_ids.csv` — IDs used and excluded terms
- `results/tables/cd276_luad_sclc_study_cd276_locus_check.csv` — per-study credible-set check
- `results/tables/cd276_luad_sclc_region_overlap_check.csv` — 0/8 LUAD/SCLC study overlap
- `results/tables/cd276_l2g_predictions.csv` — 67 L2G rows with QTL features
- `results/tables/cd276_qtl_colocalization_summary.csv` — eQTL/pQTL/sQTL summary
- `results/tables/cd276_region_credible_sets.csv` — 303 credible sets in the window
- `results/tables/cd276_tractability.csv` — modality buckets
- `results/tables/cd276_prioritisation_scores.csv` — global prioritisation record
- `data/raw/cd276_l2g_predictions_raw.json` — raw L2G tool output
