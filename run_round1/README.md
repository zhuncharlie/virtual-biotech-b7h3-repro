# Run `20261020-085513-evaluate-the-therapeutic-candida-a03f0a23`

> Evaluate the therapeutic candidacy of B7-H3 (CD276) in lung cancer. Scope the disease strictly to lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC) -- not NSCLC broadly, not other lung histologies. General web search and web scraping are disabled for this study; use only the configured database MCP servers (Open Targets, CELLxGENE Census, etc.) and your own prior knowledge, clearly labeled as such when you rely on it. Spatial transcriptomics / Visium analysis is out of scope for this pass.

| | |
|---|---|
| **Status** | incomplete |
| **Started** | 2026-10-20T08:55:13.174142 |
| **Duration** | 179.6 min |
| **Specialists** | 10 |
| **Artifacts** | 208 (154.7 MB) |
| **Tool calls** | 1041 (1014 by specialists, 27 by the CSO) |
| **Tool errors** | 71 |
| **Claims** | 17 |
| **Evidence coverage** | incomplete |

> **Evidence audit incomplete.** File hashes alone do not establish that the report's conclusions have recorded support.

- mcp__functional_genomics__find_drugs_affecting_gene: {"status": "tool_error", "tool": "find_drugs_affecting_gene", "error": "Query failed: TAHOE_DATA_PATH not set in environment. Set it to the directory containing Tahoe pseudobulk parquet files.", "instruction": "This call did not produce evidence. Report the failure and its effect on the analysis. Identify any alternative source explicitly; do not attribute it to this failed call."}
- mcp__functional_genomics__query_drug_perturbation: {"status": "tool_error", "tool": "query_drug_perturbation", "error": "Query failed: TAHOE_DATA_PATH not set in environment. Set it to the directory containing Tahoe pseudobulk parquet files.", "instruction": "This call did not produce evidence. Report the failure and its effect on the analysis. Identify any alternative source explicitly; do not attribute it to this failed call."}
- mcp__functional_genomics__query_drug_perturbation: {"status": "tool_error", "tool": "query_drug_perturbation", "error": "Query failed: TAHOE_DATA_PATH not set in environment. Set it to the directory containing Tahoe pseudobulk parquet files.", "instruction": "This call did not produce evidence. Report the failure and its effect on the analysis. Identify any alternative source explicitly; do not attribute it to this failed call."}
- mcp__disease__search_diseases_by_name: <tool_use_error>Cancelled: parallel tool call Bash(ls -d /mnt/beegfs/xqinag/projects/TheVir…) errored</tool_use_error>
- mcp__disease__search_diseases_by_name: <tool_use_error>Cancelled: parallel tool call Bash(ls -d /mnt/beegfs/xqinag/projects/TheVir…) errored</tool_use_error>
- mcp__target__search_targets_by_name: <tool_use_error>Cancelled: parallel tool call Bash(ls -d /mnt/beegfs/xqinag/projects/TheVir…) errored</tool_use_error>
- mcp__single_cell__get_anndata: Error calling tool 'get_anndata': Query size (3.26 GB) exceeds maximum (2.5 GB). Cells: 635,998, Genes: 3. Please apply more restrictive filters or subset genes.
- mcp__single_cell__count_cells: MCP error -32000: Connection closed
- mcp__single_cell__get_census_info: <tool_use_error>Cancelled: parallel tool call Bash(ls /mnt/beegfs/xqinag/projects/TheVirtua…) errored</tool_use_error>

Evidence coverage checks recorded pointers and report references; it does not verify scientific correctness or external citations. Use `verify` below to also check artifact hashes.

## The analysis plan

**Goal:** Evaluate B7-H3 (CD276) as a therapeutic target in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC) only: tumor biology rationale, genetic/functional support, expression specificity and safety liability, clinical precedence, and ranked modality options.

| Step | Specialist | Depends on | Task |
|---|---|---|---|
| `s1` | `genomics-analyst` | — | Genetic evidence and tractability for CD276 in LUAD and SCLC: resolve exact disease IDs, q… |
| `s2` | `single-cell-analyst` | — | CD276 expression across cell types in LUAD and SCLC tumors versus normal lung, plus normal… |
| `s3` | `functional-genomics-analyst` | — | DepMap CRISPR dependency of CD276 across LUAD and SCLC cell lines and selectivity versus o… |
| `s4` | `bio-pathways-ppi-analyst` | — | Pathway and protein-interaction context for CD276: Reactome/GO annotations, interaction pa… |
| `s5` | `clinical-trialist` | — | Clinical precedence for B7-H3-directed agents in LUAD and SCLC: ClinicalTrials.gov trials,… |
| `s6` | `fda-safety-officer` | — | Safety profile of B7-H3 targeting: target safety events, known B7-H3 drug warnings/adverse… |
| `s7` | `target-biologist` | — | CD276 target biology for modality selection: protein class, isoforms, subcellular localiza… |
| `s8` | `medchem-pharmacologist` | s5, s7 | Rank the top modalities for B7-H3 in LUAD and SCLC (e.g., ADC, bispecific/T-cell engager, … |
| `s9` | `scientific-reviewer` | s1, s2, s3, s4, s5, s6, s7, s8 | Review all specialist outputs against the user query, checking scope (LUAD/SCLC only), dat… |

Intended waves (steps in a wave may run concurrently): [s1, s2, s3, s4, s5, s6, s7] → [s8] → [s9]

**Planned vs actual:** 9 steps planned, 14 dispatches observed, 2 deviation(s) from the plan.

- *missing_output* — Step s1 declared output 'work/genomics-analyst/results/tables/cd276_luad_sclc_genetic_evidence.csv', which this run never produced.
- *missing_output* — Step s2 declared output 'work/single-cell-analyst/results/figures/cd276_expression_luad_sclc.png', which this run never produced.

> Deviations are expected when a specialist's findings change what should happen next; they are recorded so the actual sequence is auditable, not to flag an error.

## How the analysis flowed

The CSO dispatched these specialists, in this order:

| # | Specialist | Started | Duration | Messages | Cost |
|---|---|---|---|---|---|
| 1 | `genomics-analyst` | 08:56:27 | 503.86s | 206 | $5.460 |
| 2 | `single-cell-analyst` | 08:56:30 | 8297.19s | 400 | $9.007 |
| 3 | `functional-genomics-analyst` | 08:56:32 | 388.41s | 171 | $3.000 |
| 4 | `bio-pathways-ppi-analyst` | 08:56:34 | 494.0s | 225 | $4.176 |
| 5 | `clinical-trialist` | 08:56:37 | 1148.64s | 373 | $9.140 |
| 6 | `fda-safety-officer` | 08:56:40 | 217.02s | 117 | $1.765 |
| 7 | `target-biologist` | 08:56:42 | 345.39s | 126 | $3.268 |
| 8 | `medchem-pharmacologist` | 11:15:00 | 855.76s | 228 | $6.711 |
| 9 | `scientific-reviewer` | 11:29:36 | 251.42s | 77 | $0.637 |
| 10 | `single-cell-analyst` | 11:34:08 | —s | 0 | — |
| 11 | `medchem-pharmacologist` | 11:34:12 | 670.45s | 223 | $5.239 |
| 12 | `fda-safety-officer` | 11:34:14 | —s | 0 | — |
| 13 | `single-cell-analyst` | 11:45:31 | 448.84s | 174 | $2.954 |
| 14 | `fda-safety-officer` | 11:45:33 | 392.95s | 157 | $2.507 |

<details><summary>Delegation prompts (what the CSO asked each specialist)</summary>

**`genomics-analyst`**

```
You are contributing the genetic-evidence stream to a CSO-led therapeutic-candidacy evaluation of B7-H3 (CD276; Ensembl ENSG00000103855) in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC).

HARD SCOPE: Analyze only LUAD and SCLC. Do NOT analyze NSCLC broadly or other lung histologies (e.g., lung squamous, large-cell, carcinoid). If a query returns mixed lung-cancer results, filter them down to LUAD and SCLC and state what you excluded.

CONSTRAINTS: General web search and web scraping are disabled. Use only the configured MCP servers (genetics, target, disease, provenance) and your own prior knowledge, clearly labeled as prior knowledge. Do not install packages.

METHOD:
1. Invoke the evidence-citation skill first.
2. Resolve the exact Open Targets disease IDs for LUAD and SCLC using mcp__disease__search_diseases_by_name. Verify the IDs rather than assuming them; report the IDs used.
3. Verify the CD276 target ID with mcp__target__search_targets_by_name.
4. Query and report, separately for LUAD and SCLC: GWAS associations, L2G predictions, QTL colocalization (eQTL/pQTL/sQTL), and target prioritisation scores. Save the underlying tables to work/genomics-analyst/results/tables/.
5. Report target tractability by modality (antibody, small molecule, PROTAC) from mcp__target__get_target_tractability.
6. Interpret candidly: CD276 is an immune-checkpoint-family surface antigen, not a classic genetically driven oncogene. If genetic evidence is absent or weak, say so expli
… [truncated]
```

**`single-cell-analyst`**

```
You are contributing the single-cell expression stream to a CSO-led therapeutic-candidacy evaluation of B7-H3 (CD276; Ensembl ENSG00000103855) in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC).

HARD SCOPE: Analyze only LUAD and SCLC. Do NOT analyze NSCLC broadly or other lung histologies. Spatial transcriptomics / Visium is explicitly out of scope.

CONSTRAINTS: General web search and web scraping are disabled. Use only the configured MCP servers (single_cell/CELLxGENE Census, expression, target, provenance) and prior knowledge clearly labeled as such. Do not install packages.

METHOD:
1. Invoke the evidence-citation skill first, and review the relevant skill files in .claude/skills/ before starting analysis (per routing guidance).
2. Discover available LUAD and SCLC datasets/cell types in CELLxGENE Census. Report exact disease filters, tissue filters, number of cells and number of donors for every comparison. If SCLC single-cell data are sparse or absent, say so explicitly rather than substituting NSCLC.
3. For each indication, quantify CD276 expression: mean expression and percent-expressing by cell type, with emphasis on malignant/epithelial tumor cells versus immune and stromal compartments. Save a tidy table to work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv and a figure to results/figures/.
4. Compare tumor versus non-tumor/adjacent-normal samples where the metadata permit, and state whether the comparison is donor-matched 
… [truncated]
```

**`functional-genomics-analyst`**

```
You are contributing the functional-genomics stream to a CSO-led therapeutic-candidacy evaluation of B7-H3 (CD276; Ensembl ENSG00000103855) in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC).

HARD SCOPE: Analyze only LUAD and SCLC cell lines. Do NOT broaden to NSCLC or other histologies except as a clearly labeled selectivity comparator, and never as the primary analysis.

CONSTRAINTS: General web search and web scraping are disabled. Use only the configured MCP servers (functional_genomics/DepMap and Tahoe-100M, target, provenance) and prior knowledge clearly labeled as such. Do not install packages.

METHOD:
1. Invoke the evidence-citation skill first.
2. Query CD276 CRISPR essentiality in DepMap, filtered to LUAD and separately to SCLC. Report number of cell lines, mean gene effect, essential fraction, and the distribution — not just a single number. Save to work/functional-genomics-analyst/results/tables/cd276_depmap_luad_sclc.csv.
3. Assess cancer-type selectivity: is CD276 dependency higher in LUAD/SCLC than in other lineages? Report the comparator explicitly.
4. Interpret the result in the correct frame: B7-H3 is being evaluated as a surface antigen for payload delivery (ADC/bispecific/CAR), so a lack of intrinsic dependency is expected and is NOT disqualifying. State clearly whether DepMap supports an intrinsic-dependency rationale or not.
5. If available, use Tahoe-100M to check (a) any perturbation effects on CD276 expression and (b) whether known B7-H
… [truncated]
```

**`bio-pathways-ppi-analyst`**

```
You are contributing the pathway/PPI context stream to a CSO-led therapeutic-candidacy evaluation of B7-H3 (CD276; Ensembl ENSG00000103855) in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC).

HARD SCOPE: Keep the therapeutic interpretation to LUAD and SCLC. Pathway and interaction data are gene-level, but all safety/biology conclusions should be framed for these two indications only.

CONSTRAINTS: General web search and web scraping are disabled. Use only the configured MCP servers (pathway, interaction, target, provenance) and prior knowledge clearly labeled as such. Do not install packages.

METHOD:
1. Invoke the evidence-citation skill first.
2. Retrieve Reactome pathways and GO annotations (biological process, molecular function, cellular component) for CD276. Save a table to work/bio-pathways-ppi-analyst/results/tables/cd276_pathways_interactions.csv.
3. Retrieve protein-protein interactions and detailed interaction evidence. Report the highest-confidence partners and detection methods. Note explicitly whether a canonical B7-H3 receptor is established in the data; if the receptor remains unresolved, state that as a biological gap rather than filling it from memory (any prior-knowledge statement must be labeled).
4. Characterize the immune-checkpoint context: co-inhibitory vs co-stimulatory signaling, expression on antigen-presenting cells/tumor cells, and what pathway perturbation would imply for an agonist vs antagonist vs payload-delivery strategy.
5. Ass
… [truncated]
```

**`clinical-trialist`**

```
You are contributing the clinical-precedence stream to a CSO-led therapeutic-candidacy evaluation of B7-H3 (CD276; Ensembl ENSG00000103855) in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC).

HARD SCOPE: Include only trials/evidence in LUAD and SCLC. Exclude other lung histologies and pan-tumor trials unless the LUAD/SCLC cohort is separately reported; if you include a pan-tumor trial, label it and extract only the LUAD/SCLC-relevant information.

CONSTRAINTS: General web search and web scraping are disabled. Use only the configured MCP servers (clinicaltrials, drug, target, provenance) and prior knowledge clearly labeled as such. Do not install packages.

METHOD:
1. Invoke the evidence-citation skill first.
2. Search ClinicalTrials.gov for B7-H3/CD276-directed agents in LUAD and SCLC. Seed terms from prior knowledge (clearly labeled): ifinatamab deruxtecan (I-DXd/DS-7300), vobramitamab duocarmazine (MGC018), enoblituzumab (MGA271), omburtamab/8H9, MGD009, ABBV-155, HS-20093, DS-5573a, and any others the database surfaces. Search by condition and by intervention; also search mechanism terms such as "B7-H3" and "CD276".
3. For each relevant trial, extract: NCT ID, title, phase, status, indication (confirm LUAD vs SCLC), agent/modality, line of therapy, enrollment, primary endpoint, and any posted results. Save to work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv.
4. Summarize the clinical landscape separately for LUAD and SCLC: how many trials, whic
… [truncated]
```

**`fda-safety-officer`**

```
You are contributing the safety stream to a CSO-led therapeutic-candidacy evaluation of B7-H3 (CD276; Ensembl ENSG00000103855) in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC).

HARD SCOPE: Frame the risk-benefit for LUAD and SCLC only. These are oncology indications, so some toxicity is tolerable; distinguish manageable from dose-limiting/fatal risk.

CONSTRAINTS: General web search and web scraping are disabled. Use only the configured MCP servers (drug, target, provenance) and prior knowledge clearly labeled as such. Do not install packages.

METHOD:
1. Invoke the evidence-citation skill first.
2. Retrieve the CD276 target safety profile and mouse knockout phenotypes. Save quantitative results to work/fda-safety-officer/results/tables/b7h3_safety_signals.csv.
3. Retrieve known B7-H3-targeted drugs and their warnings, indications, mechanisms, and adverse-event signals (OpenFDA). Prioritize agents plausibly used in LUAD/SCLC: ifinatamab deruxtecan, vobramitamab duocarmazine, enoblituzumab, omburtamab, and any others the database surfaces. If an agent has no FDA record (e.g., investigational), state that explicitly rather than inferring a clean safety profile.
4. Assess on-target off-tumor risk: B7-H3 has broad low-level normal-tissue expression. Identify the organ systems most likely to drive toxicity and what type of toxicity (payload-independent vs payload-driven). Clearly separate prior knowledge from database evidence.
5. Retrieve pharmacogenomics and homo
… [truncated]
```

**`target-biologist`**

```
You are contributing the target-biology stream to a CSO-led therapeutic-candidacy evaluation of B7-H3 (CD276; Ensembl ENSG00000103855) in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC).

HARD SCOPE: Frame all conclusions for LUAD and SCLC only. Do not broaden to NSCLC or other lung histologies.

CONSTRAINTS: General web search and web scraping are disabled. Use only the configured MCP servers (target, drug, interaction, pathway, expression, provenance) and prior knowledge clearly labeled as such. Do not install packages.

METHOD:
1. Invoke the evidence-citation skill first.
2. Retrieve and report CD276 target annotations: approved symbol/name, biotype, genomic location, protein class (ChEMBL target classification), subcellular localization, homologues, and function descriptions. Save to work/target-biologist/results/tables/cd276_target_biology.csv.
3. Retrieve tractability predictions by modality (antibody, small molecule, PROTAC) and any chemical probes. Interpret what the localization and topology imply for surface-antigen modalities.
4. Retrieve tissue expression overview (GTEx/Expression Atlas via expression MCP) to characterize breadth of normal expression; this informs both accessibility and off-tumor risk.
5. Summarize the target-biology features that determine modality choice: surface exposure, internalization requirement for ADCs, suitability for T-cell engagement, antigen density/modulation, soluble isoform or shedding considerations, and blood-brain-b
… [truncated]
```

**`medchem-pharmacologist`**

```
You are producing the modality-selection deliverable for a CSO-led therapeutic-candidacy evaluation of B7-H3 (CD276; Ensembl ENSG00000103855) in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC).

HARD SCOPE: Rank modalities for LUAD and SCLC only. Do not broaden to NSCLC or other lung histologies. General web search and web scraping are disabled; use only configured MCP servers (drug, target, pathway, interaction, provenance) and prior knowledge clearly labeled as such. Do not install packages.

INPUTS ALREADY COMPLETED — read these exact files first:
- work/clinical-trialist/results/reports/b7h3_clinical_landscape.md
- work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv
- work/target-biologist/results/reports/cd276_modality_biology.md
- work/target-biologist/results/tables/cd276_target_biology.csv
- work/target-biologist/results/tables/cd276_tractability_by_modality.csv
- work/target-biologist/results/tables/cd276_known_clinical_drugs.csv
- work/fda-safety-officer/results/reports/b7h3_safety_assessment.md
- work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv

KEY FACTS TO INCORPORATE (from those streams):
- CD276 is a type I surface antigen; antibody tractability strong, small molecule all-false, PROTAC not viable.
- No intrinsic CRISPR dependency in LUAD or SCLC (mean gene effect ~-0.20 to -0.23; 0-2% essential) — signalling-inhibition monotherapy is not supported; payload delivery/cell depletion is the rationale.
- Clinic
… [truncated]
```

**`scientific-reviewer`**

```
You are the scientific reviewer for a CSO-led therapeutic-candidacy evaluation of B7-H3 (CD276; ENSG00000103855) in lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC).

USER QUERY (verbatim): "Evaluate the therapeutic candidacy of B7-H3 (CD276) in lung cancer. Scope the disease strictly to lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC) -- not NSCLC broadly, not other lung histologies. General web search and web scraping are disabled for this study; use only the configured database MCP servers (Open Targets, CELLxGENE Census, etc.) and your own prior knowledge, clearly labeled as such when you rely on it. Spatial transcriptomics / Visium analysis is out of scope for this pass."

YOUR JOB: Read the specialist outputs below and produce a rigorous review. Do NOT perform new data analysis; assess whether each output answers the query, whether its conclusions are supported by saved evidence, whether scope is respected, and where there is overreach, contradiction, or a material gap.

SPECIALIST OUTPUTS AND EXACT PATHS (run root: /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23):

1. genomics-analyst
- work/genomics-analyst/results/reports/cd276_genetic_evidence.md
- work/genomics-analyst/results/tables/cd276_luad_sclc_study_cd276_locus_check.csv
- work/genomics-analyst/results/tables/cd276_l2g_predictions.csv
- work/genomics-analyst/results/tables/cd276_tractability.csv
Summary: no CD276 GWAS/L2G evi
… [truncated]
```

**`medchem-pharmacologist`**

```
You are revising the modality recommendation for the B7-H3 (CD276) LUAD/SCLC evaluation after scientific review. Read your existing outputs first; do not redo the whole analysis.

EXISTING ARTIFACTS (run root /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23):
- work/medchem-pharmacologist/results/tables/b7h3_modality_ranking.csv
- work/medchem-pharmacologist/results/tables/b7h3_modality_precedent_evidence.csv
- work/medchem-pharmacologist/results/tables/cd276_malignant_vs_stromal_ratios.csv
- work/medchem-pharmacologist/results/reports/b7h3_modality_recommendation.md
- Also re-read: work/clinical-trialist/results/reports/b7h3_clinical_landscape.md and work/target-biologist/results/reports/cd276_modality_biology.md

REVIEWER RULINGS TO INCORPORATE:
1. SCLC "GO" is premature and must be staged. Feasibility is established (26 SCLC-contributing trials, 6 Phase 3 trials across only 4 molecules), but efficacy is not: the only posted SCLC-specific result is MGC018 ORR 0/9 (n=9), and the completed Phase 3 ARTEMIS-008 has no posted results. Reframe SCLC as "GO conditional on (a) class-level Phase 3 efficacy readout and (b) a differentiated molecule/profile" — not an unconditional GO.
2. LUAD "NO-GO by default" is defensible as a strategic prioritization, not as a scientific conclusion. Reframe accordingly: deprioritized on competitive/precedence grounds, with clinical precedence scored 1/5, and explicitly acknowledge that LUA
… [truncated]
```

**`single-cell-analyst`**

```
This is a retry after a transient 403 error; no work was done in the prior attempt. You are revising an existing single-cell deliverable for the B7-H3 (CD276) LUAD/SCLC evaluation. Do NOT re-run the analysis — read the existing artifacts, correct them, and re-save.

RUN ROOT: /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23
Read first:
- work/single-cell-analyst/results/tables/cd276_epithelial_tumor_vs_normal_donor_paired.csv
- work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv
- work/single-cell-analyst/results/tables/cd276_key_comparisons.csv
- work/single-cell-analyst/results/tables/cd276_normal_tissue_organ_summary.csv
- your existing report under work/single-cell-analyst/results/reports/

CORRECTIONS REQUIRED:
1. The claim "~2x adjacent normal in all 3 donor-matched pairs" is unsupported. Individual donor ratios are 3.26, 3.40, 1.09. Correct every occurrence to: "CD276 was higher in tumour than adjacent normal epithelium in 3/3 donor-matched LUAD pairs, but reached >=2x in only 2/3 (3.26, 3.40, 1.09) and was not statistically significant at n=3." Do not quote a p-value unless a saved statistical artifact produces it; otherwise remove it.
2. Replace the untraceable "128 donors" with verified counts: 635,998 cells from 3 datasets, plus per-cell-type donor counts you can substantiate from the saved table (max observed 115). Do not assert a total donor count you cannot trace.
3. Add a sy
… [truncated]
```

**`fda-safety-officer`**

```
This is a retry after a transient 403 error; no work was done in the prior attempt. You are revising an existing safety deliverable for the B7-H3 (CD276) LUAD/SCLC evaluation. Do NOT redo the analysis — read the existing artifacts, correct them, and re-save.

RUN ROOT: /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23
Read first:
- work/fda-safety-officer/results/tables/b7h3_safety_signals.csv
- work/fda-safety-officer/results/tables/b7h3_agent_registry_lung_cancer.csv
- work/fda-safety-officer/results/tables/b7h3_modality_class_toxicities.csv
- work/fda-safety-officer/results/reports/b7h3_safety_assessment.md

CORRECTIONS REQUIRED:
1. Harmonize the CD276 LoF constraint statement. The o/e is 0.667. One stream quoted a 90% CI (0.506-0.888) and upperBin 4; another quoted a different bin. Cite the CI with its correct confidence level from the retrieved record, or simply report o/e 0.667 with "moderate LoF tolerance" and omit the CI/bin. Do not mix confidence levels or bins.
2. Make target-level vs payload-level risk separation explicit throughout: broad low-level expression, stromal expression, and soluble antigen are target-level; ILD/pneumonitis, myelosuppression, ocular toxicity, CRS/ICANS, and marrow suppression are payload/modality-level. Do not attribute payload toxicity to B7-H3 biology.
3. Qualify normal-tissue expression: broad low-level expression is supported by bulk RNA (HPA) and prior knowledge; HPA protein 
… [truncated]
```

</details>

## What each agent produced

### Genomics Analyst  ·  21 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/genomics-analyst/code/scripts/cd276_genetic_evidence_tables.py` | code | 12.1 KB | `call_00_qLQ5Z9…` | — |
| `work/genomics-analyst/data/raw/cd276_l2g_predictions_raw.json` | data | 155.7 KB | `call_00_ET_Lfg…` | — |
| `work/genomics-analyst/results/reports/cd276_genetic_evidence.md` | report | 7.1 KB | `call_00_AKq5zC…` | — |
| `work/genomics-analyst/data/raw/cd276_locus_credible_sets_all_studies.parquet` | table | 208.6 KB | `call_00_9WEm6C…` | — |
| `work/genomics-analyst/data/raw/luad_GCST004744_credible_sets.parquet` | table | 26.6 KB | `call_03_T2RYDM…` | — |
| `work/genomics-analyst/data/raw/luad_GCST008836_credible_sets.parquet` | table | 47.5 KB | `call_02_B3Qinx…` | — |
| `work/genomics-analyst/data/raw/luad_GCST90134662_credible_sets.parquet` | table | 52.3 KB | `call_01_UWofL7…` | — |
| `work/genomics-analyst/data/raw/luad_GCST90297563_credible_sets.parquet` | table | 25.3 KB | `call_00_uLrHGR…` | — |
| `work/genomics-analyst/data/raw/luad_GCST90455522_credible_sets.parquet` | table | 83.2 KB | `call_00_IZbgBt…` | — |
| `work/genomics-analyst/data/raw/sclc_FINNGEN_R12_C3_SCLC_EXALLC_credible_sets.parquet` | table | 22.3 KB | `call_06_hNGnuK…` | — |
| `work/genomics-analyst/data/raw/sclc_GCST004746_credible_sets.parquet` | table | 21.3 KB | `call_04_6Suo4j…` | — |
| `work/genomics-analyst/data/raw/sclc_GCST90134664_credible_sets.parquet` | table | 22.6 KB | `call_05_pA0nJV…` | — |
| `work/genomics-analyst/data/raw/test_locus_credset.parquet` | table | 18.7 KB | `call_01_fIbYZG…` | — |
| `work/genomics-analyst/results/tables/cd276_disease_ids.csv` | table | 499 B | `call_00_ET_Lfg…` | — |
| `work/genomics-analyst/results/tables/cd276_l2g_predictions.csv` | table | 27.5 KB | `call_00_ET_Lfg…` | C3 |
| `work/genomics-analyst/results/tables/cd276_luad_sclc_region_overlap_check.csv` | table | 110 B | `call_00_ET_Lfg…` | — |
| `work/genomics-analyst/results/tables/cd276_luad_sclc_study_cd276_locus_check.csv` | table | 802 B | `call_00_ET_Lfg…` | C3 |
| `work/genomics-analyst/results/tables/cd276_prioritisation_scores.csv` | table | 498 B | `call_00_ET_Lfg…` | — |
| `work/genomics-analyst/results/tables/cd276_qtl_colocalization_summary.csv` | table | 420 B | `call_00_ET_Lfg…` | — |
| `work/genomics-analyst/results/tables/cd276_region_credible_sets.csv` | table | 1.3 MB | `call_00_ET_Lfg…` | — |
| `work/genomics-analyst/results/tables/cd276_tractability.csv` | table | 725 B | `call_00_ET_Lfg…` | — |

### Single Cell Analyst  ·  74 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/single-cell-analyst/code/scripts/01_discover_datasets.py` | code | 2.8 KB | `call_00_QHykn3…` | — |
| `work/single-cell-analyst/code/scripts/02_matched_donors.py` | code | 2.2 KB | `call_01_CB5Vfb…` | — |
| `work/single-cell-analyst/code/scripts/03_inspect_h5ad.py` | code | 1.5 KB | `call_01_0nyu0o…` | — |
| `work/single-cell-analyst/code/scripts/04_cd276_expression_analysis.py` | code | 13.6 KB | `call_00_1ttoG2…` | — |
| `work/single-cell-analyst/code/scripts/05_lineage_summary.py` | code | 6.1 KB | `call_00_4j3bBA…` | — |
| `work/single-cell-analyst/code/scripts/06_final_tables.py` | code | 8.4 KB | `call_00_mBR2tw…` | — |
| `work/single-cell-analyst/code/scripts/07_verify_counts.py` | code | 2.1 KB | `call_00_1BoPwn…` | — |
| `work/single-cell-analyst/code/scripts/08_apply_corrections.py` | code | 9.4 KB | `call_00_PmtUIF…` | — |
| `work/single-cell-analyst/data/raw/luad_ds1e6a_epithelial_stromal_cd276.h5ad` | data | 3.1 MB | `call_00_ET_xT8…` | — |
| `work/single-cell-analyst/data/raw/luad_ds1e6a_lymphoid_cd276.h5ad` | data | 8.4 MB | `call_00_76XDNL…` | — |
| `work/single-cell-analyst/data/raw/luad_ds1e6a_myeloid_cd276.h5ad` | data | 5.8 MB | `call_00_B0tAap…` | — |
| `work/single-cell-analyst/data/raw/luad_other_datasets_cd276.h5ad` | data | 3.1 MB | `call_00_aId95D…` | — |
| `work/single-cell-analyst/data/raw/normal_adipose_cd276.h5ad` | data | 2.8 MB | `call_00_d3iq7S…` | — |
| `work/single-cell-analyst/data/raw/normal_adrenal_cd276.h5ad` | data | 1.7 MB | `call_02_Og6sLR…` | — |
| `work/single-cell-analyst/data/raw/normal_blood_cd276.h5ad` | data | 9.3 MB | `call_00_jNQFLm…` | — |
| `work/single-cell-analyst/data/raw/normal_blood_mature_pbmc_cd276.h5ad` | data | 5.9 MB | `call_00_zO1WqX…` | — |
| `work/single-cell-analyst/data/raw/normal_bone_marrow_cd276.h5ad` | data | 7.3 MB | `call_01_W0gUxy…` | — |
| `work/single-cell-analyst/data/raw/normal_brain_cortex_cd276.h5ad` | data | 3.7 MB | `call_03_lNXHCX…` | — |
| `work/single-cell-analyst/data/raw/normal_breast_cd276.h5ad` | data | 3.6 MB | `call_03_SnhAmT…` | — |
| `work/single-cell-analyst/data/raw/normal_colon_cd276.h5ad` | data | 1.9 MB | `call_01_YePdvf…` | — |
| `work/single-cell-analyst/data/raw/normal_esophagus_cd276.h5ad` | data | 2.8 MB | `call_01_ie6fdc…` | — |
| `work/single-cell-analyst/data/raw/normal_heart_cd276.h5ad` | data | 6.4 MB | `call_00_RQNvux…` | — |
| `work/single-cell-analyst/data/raw/normal_ileum_cd276.h5ad` | data | 2.8 MB | `call_02_RxNCk4…` | — |
| `work/single-cell-analyst/data/raw/normal_kidney_cd276.h5ad` | data | 4.6 MB | `call_02_w9P8Rr…` | — |
| `work/single-cell-analyst/data/raw/normal_liver_cd276.h5ad` | data | 4.8 MB | `call_01_Y7KDAo…` | — |
| `work/single-cell-analyst/data/raw/normal_lung_matched_cd276.h5ad` | data | 995.8 KB | `call_01_ET_Whc…` | — |
| `work/single-cell-analyst/data/raw/normal_pancreas_cd276.h5ad` | data | 2.6 MB | `call_03_Y1OfoY…` | — |
| `work/single-cell-analyst/data/raw/normal_skeletal_muscle_cd276.h5ad` | data | 5.2 MB | `call_00_qyrYQF…` | — |
| `work/single-cell-analyst/data/raw/normal_skin_cd276.h5ad` | data | 5.3 MB | `call_00_6N7RGZ…` | — |
| `work/single-cell-analyst/data/raw/normal_spleen_lymphnode_cd276.h5ad` | data | 11.0 MB | `call_02_XMRQ1P…` | — |
| `work/single-cell-analyst/data/raw/normal_thymus_cd276.h5ad` | data | 7.6 MB | `call_03_BJqsah…` | — |
| `work/single-cell-analyst/data/raw/qc_scale_blood_pbmc_actb.h5ad` | data | 7.3 MB | `call_00_oaY6MK…` | — |
| `work/single-cell-analyst/data/raw/qc_scale_kidney_actb.h5ad` | data | 4.9 MB | `call_02_9CigVN…` | — |
| `work/single-cell-analyst/data/raw/qc_scale_sclc_actb.h5ad` | data | 1.7 MB | `call_03_nWaM2o…` | — |
| `work/single-cell-analyst/data/raw/qc_scale_skin_actb.h5ad` | data | 6.5 MB | `call_01_gMLI9D…` | — |
| `work/single-cell-analyst/data/raw/sclc_cd276.h5ad` | data | 1.6 MB | `call_00_ET_w2M…` | — |
| `work/single-cell-analyst/results/figures/cd276_luad_sclc_celltype_expression.png` | figure | 408.1 KB | `call_00_zXrOHz…` | — |
| `work/single-cell-analyst/results/figures/cd276_luad_tumor_vs_normal_paired.png` | figure | 146.9 KB | `call_00_ET_Q31…` | — |
| `work/single-cell-analyst/results/figures/cd276_normal_organ_weighted_mean.png` | figure | 247.4 KB | `call_00_pyqBXw…` | — |
| `work/single-cell-analyst/results/figures/cd276_normal_tissues_organ_by_lineage.png` | figure | 376.6 KB | `call_00_ET_pm0…` | — |
| `work/single-cell-analyst/results/figures/cd276_normal_tissues_top_celltypes.png` | figure | 727.4 KB | `call_00_zXrOHz…` | — |
| `work/single-cell-analyst/results/figures/cd276_stromal_vs_tumor_symmetry.png` | figure | 124.6 KB | `call_00_ET_Q31…` | — |
| `work/single-cell-analyst/data/raw/01_discovery_summary.log` | log | 8.5 KB | `call_00_ET_vAA…` | — |
| `work/single-cell-analyst/data/raw/02_matched_donors.log` | log | 1.5 KB | `call_00_ET_Pnv…` | — |
| `work/single-cell-analyst/data/raw/03_inspect_h5ad.log` | log | 5.7 KB | `call_00_ET_YnY…` | — |
| `work/single-cell-analyst/results/tables/04_analysis_run.log` | log | 9.3 KB | `call_00_zXrOHz…` | — |
| `work/single-cell-analyst/results/tables/05_lineage_run.log` | log | 8.3 KB | `call_00_ET_pm0…` | — |
| `work/single-cell-analyst/results/tables/06_final_tables.log` | log | 3.9 KB | `call_00_JH9HOf…` | — |
| `work/single-cell-analyst/results/reports/cd276_single_cell_atlas_report.md` | report | 10.8 KB | `call_00_XrJxi5…` | — |
| `work/single-cell-analyst/data/raw/luad_lung_cell_metadata.parquet` | table | 1.8 MB | — | — |
| `work/single-cell-analyst/data/raw/normal_lung_cell_metadata.parquet` | table | 5.1 MB | `call_00_UfaUz8…` | — |
| `work/single-cell-analyst/data/raw/sclc_lung_cell_metadata.parquet` | table | 276.1 KB | `call_01_iTsQct…` | — |
| `work/single-cell-analyst/results/tables/cd276_analysis_parameters.csv` | table | 1.1 KB | `call_00_pyqBXw…` | — |
| `work/single-cell-analyst/results/tables/cd276_dataset_inventory.csv` | table | 606 B | `call_00_JH9HOf…` | C15 |
| `work/single-cell-analyst/results/tables/cd276_epithelial_epcam_stratified.csv` | table | 315 B | `call_00_ZVNH1O…` | — |
| `work/single-cell-analyst/results/tables/cd276_epithelial_tumor_vs_normal_donor_paired.csv` | table | 690 B | `call_00_ET_Q31…` | — |
| `work/single-cell-analyst/results/tables/cd276_epithelial_tumor_vs_normal_donor_paired_summary.csv` | table | 443 B | `call_00_ET_Q31…` | C5 |
| `work/single-cell-analyst/results/tables/cd276_key_comparisons.csv` | table | 1.5 KB | `call_00_ET_Q31…` | — |
| `work/single-cell-analyst/results/tables/cd276_luad_malignant_by_assay.csv` | table | 445 B | `call_00_VMNm1y…` | — |
| `work/single-cell-analyst/results/tables/cd276_luad_paired_donor_stats.csv` | table | 612 B | `call_00_ET_Q31…` | C5 |
| `work/single-cell-analyst/results/tables/cd276_luad_sclc_by_dataset_celltype.csv` | table | 19.6 KB | `call_00_JH9HOf…` | — |
| `work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv` | table | 8.2 KB | `call_00_JH9HOf…` | — |
| `work/single-cell-analyst/results/tables/cd276_luad_sclc_compartment_summary.csv` | table | 1.4 KB | `call_00_zXrOHz…` | — |
| `work/single-cell-analyst/results/tables/cd276_luad_sclc_lineage_expression.csv` | table | 2.5 KB | `call_00_ET_pm0…` | C4 |
| `work/single-cell-analyst/results/tables/cd276_luad_sclc_top_celltypes_min200cells.csv` | table | 7.9 KB | `call_00_zXrOHz…` | — |
| `work/single-cell-analyst/results/tables/cd276_normal_dataset_inventory.csv` | table | 967 B | `call_00_JH9HOf…` | — |
| `work/single-cell-analyst/results/tables/cd276_normal_tissue_organ_summary.csv` | table | 2.1 KB | `call_00_zXrOHz…` | C6 |
| `work/single-cell-analyst/results/tables/cd276_normal_tissues_celltype_expression.csv` | table | 65.2 KB | `call_00_zXrOHz…` | — |
| `work/single-cell-analyst/results/tables/cd276_normal_tissues_lineage_expression.csv` | table | 19.4 KB | `call_00_ET_pm0…` | — |
| `work/single-cell-analyst/results/tables/cd276_normal_tissues_top_celltypes.csv` | table | 48.3 KB | `call_00_zXrOHz…` | — |
| `work/single-cell-analyst/results/tables/cd276_stromal_vs_tumor_symmetry.csv` | table | 1.6 KB | `call_00_ET_Q31…` | C4 |
| `work/single-cell-analyst/results/tables/cd276_tumor_vs_normal_per_donor.csv` | table | 33.4 KB | `call_00_zXrOHz…` | — |
| `work/single-cell-analyst/results/tables/normal_tissue_dataset_assays.csv` | table | 967 B | `call_01_CMFo4x…` | — |
| `work/single-cell-analyst/results/tables/qc_housekeeping_scale_check.csv` | table | 976 B | `call_00_pwVQTr…` | — |

### Functional Genomics Analyst  ·  15 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/functional-genomics-analyst/code/scripts/cd276_depmap_analysis.py` | code | 15.7 KB | `call_00_S8bxKV…` | — |
| `work/functional-genomics-analyst/data/raw/cd276_depmap_essentiality_raw.json` | data | 178.4 KB | — | — |
| `work/functional-genomics-analyst/results/tables/cd276_tahoe_query_status.json` | data | 2.2 KB | — | C15 |
| `work/functional-genomics-analyst/results/figures/cd276_depmap_luad_sclc_distribution.pdf` | figure | 57.5 KB | `call_00_J5Qi0n…` | — |
| `work/functional-genomics-analyst/results/figures/cd276_depmap_luad_sclc_distribution.png` | figure | 318.9 KB | `call_00_J5Qi0n…` | — |
| `work/functional-genomics-analyst/code/cd276_run.log` | log | 4.5 KB | `call_00_J5Qi0n…` | — |
| `work/functional-genomics-analyst/results/reports/cd276_functional_genomics.md` | report | 14.1 KB | `call_01_ET_38S…` | — |
| `work/functional-genomics-analyst/results/tables/cd276_depmap_all_cell_lines_annotated.csv` | table | 160.7 KB | — | — |
| `work/functional-genomics-analyst/results/tables/cd276_depmap_broad_label_sensitivity.csv` | table | 621 B | — | — |
| `work/functional-genomics-analyst/results/tables/cd276_depmap_disease_comparator.csv` | table | 4.4 KB | — | — |
| `work/functional-genomics-analyst/results/tables/cd276_depmap_gene_effect_bins.csv` | table | 1.1 KB | — | — |
| `work/functional-genomics-analyst/results/tables/cd276_depmap_group_comparisons.csv` | table | 972 B | — | C2 |
| `work/functional-genomics-analyst/results/tables/cd276_depmap_group_summary.csv` | table | 2.1 KB | — | — |
| `work/functional-genomics-analyst/results/tables/cd276_depmap_luad_sclc.csv` | table | 9.4 KB | — | C2 |
| `work/functional-genomics-analyst/results/tables/cd276_histology_mapping.csv` | table | 107.7 KB | — | — |

### Bio Pathways Ppi Analyst  ·  8 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/bio-pathways-ppi-analyst/code/scripts/build_cd276_pathways_interactions_table.py` | code | 9.1 KB | `call_00_9Prhli…` | — |
| `work/bio-pathways-ppi-analyst/code/scripts/plot_cd276_partner_confidence.py` | code | 2.2 KB | `call_00_jkFHvT…` | — |
| `work/bio-pathways-ppi-analyst/data/raw/cd276_mcp_query_results.json` | data | 20.7 KB | `call_00_mLaDyU…` | — |
| `work/bio-pathways-ppi-analyst/results/figures/cd276_partner_confidence.png` | figure | 174.6 KB | `call_00_ET_ahC…` | C14 |
| `work/bio-pathways-ppi-analyst/results/reports/cd276_pathway_safety.md` | report | 14.9 KB | `call_00_ET_ivE…` | — |
| `work/bio-pathways-ppi-analyst/results/tables/cd276_constraint_tractability.csv` | table | 1.7 KB | `call_00_ET_v5M…` | — |
| `work/bio-pathways-ppi-analyst/results/tables/cd276_human_paralogues.csv` | table | 638 B | `call_00_ET_v5M…` | — |
| `work/bio-pathways-ppi-analyst/results/tables/cd276_pathways_interactions.csv` | table | 17.2 KB | `call_00_ET_v5M…` | C14 |

### Clinical Trialist  ·  50 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/clinical-trialist/code/scripts/build_b7h3_luad_sclc_trials.py` | code | 28.1 KB | `call_00_hzPI3G…` | — |
| `work/clinical-trialist/code/scripts/build_b7h3_trial_candidates.py` | code | 4.5 KB | `call_00_2XN1QU…` | — |
| `work/clinical-trialist/code/scripts/ctgov_b7h3_search.py` | code | 3.2 KB | `call_00_ZEJu3F…` | — |
| `work/clinical-trialist/code/scripts/parse_ctgov_record.py` | code | 4.1 KB | `call_00_ET_zz4…` | — |
| `work/clinical-trialist/code/scripts/plot_b7h3_phase_landscape.py` | code | 2.7 KB | `call_00_84wDi1…` | — |
| `work/clinical-trialist/code/scripts/query_cd276_chembl_parquet.py` | code | 4.0 KB | `call_00_Fzg1aj…` | — |
| `work/clinical-trialist/data/processed/summary_NCT03729596.json` | data | 4.1 KB | `call_00_QiapdC…` | — |
| `work/clinical-trialist/data/raw/clinicaltrials_gov_NCT02475213.json` | data | 182.4 KB | `call_00_EWlxnN…` | — |
| `work/clinical-trialist/data/raw/clinicaltrials_gov_NCT03729596.json` | data | 178.2 KB | `call_00_wdYZq6…` | — |
| `work/clinical-trialist/data/raw/clinicaltrials_gov_NCT05551117_results_extract.json` | data | 195.5 KB | `call_00_wbAx9C…` | — |
| `work/clinical-trialist/data/raw/clinicaltrials_gov_NCT06227546.json` | data | 11.7 KB | `call_00_hWI9mW…` | — |
| `work/clinical-trialist/data/raw/ctgov_b7h3_search_counts.json` | data | 9.4 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_b7h3_search_index.json` | data | 17.9 KB | `call_00_ET_zb1…` | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_8H9.json` | data | 59.6 KB | `call_00_ET_zb1…` | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_ABBV-155.json` | data | 48.6 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_BNT324.json` | data | 182.9 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_DB-1311.json` | data | 182.9 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_DS-5573a.json` | data | 7.2 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_DS-7300.json` | data | 182 B | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_HS-20093.json` | data | 367.2 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_MGA271.json` | data | 140.6 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_MGC018.json` | data | 92.3 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_MGD009.json` | data | 29.8 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_MHB088C.json` | data | 88.7 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_enoblituzumab.json` | data | 137.1 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_ifinatamab_deruxtecan.json` | data | 817.0 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_omburtamab.json` | data | 138.5 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_orlotamab.json` | data | 16.8 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_intervention_vobramitamab_duocarmazine.json` | data | 80.1 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_term_B7-H3.json` | data | 2.5 MB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_term_B7-H3__condition_lung_adenocarcinoma.json` | data | 201.5 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_term_B7-H3__condition_non-small_cell_lung_cancer.json` | data | 413.5 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_term_B7-H3__condition_small_cell_lung_cancer.json` | data | 808.9 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_term_B7H3.json` | data | 733.1 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_term_CD276.json` | data | 509.4 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_term_CD276__condition_lung_adenocarcinoma.json` | data | 18.9 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_term_CD276__condition_non-small_cell_lung_cancer.json` | data | 18.8 KB | — | — |
| `work/clinical-trialist/data/raw/ctgov_search_term_CD276__condition_small_cell_lung_cancer.json` | data | 37.5 KB | — | — |
| `work/clinical-trialist/results/figures/b7h3_phase_landscape.pdf` | figure | 17.9 KB | `call_00_ET_KoI…` | — |
| `work/clinical-trialist/results/figures/b7h3_phase_landscape.png` | figure | 82.7 KB | `call_00_ET_KoI…` | — |
| `work/clinical-trialist/results/reports/b7h3_clinical_landscape.md` | report | 7.7 KB | `call_00_7MZGuw…` | C7, C9 |
| `work/clinical-trialist/data/processed/b7h3_ctgov_candidates.csv` | table | 66.7 KB | `call_00_ofB5aL…` | — |
| `work/clinical-trialist/data/processed/b7h3_trial_selection_audit.csv` | table | 33.7 KB | `call_00_ET_3yk…` | — |
| `work/clinical-trialist/data/processed/cd276_chembl_parquet_rows.csv` | table | 1.4 KB | `call_00_ET_3yk…` | — |
| `work/clinical-trialist/results/tables/b7h3_ctgov_query_counts.csv` | table | 2.0 KB | `call_00_ET_3yk…` | — |
| `work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv` | table | 33.7 KB | `call_00_ET_3yk…` | C7, C8, C9, C16 |
| `work/clinical-trialist/results/tables/b7h3_luad_search_hits.csv` | table | 4.8 KB | `call_00_ET_3yk…` | — |
| `work/clinical-trialist/results/tables/b7h3_posted_results_extract.csv` | table | 1.3 KB | `call_00_ET_3yk…` | C8 |
| `work/clinical-trialist/results/tables/cd276_chembl_parquet_coverage.csv` | table | 145 B | `call_00_ET_3yk…` | — |
| `work/clinical-trialist/results/tables/cd276_known_drugs_drug_mcp.csv` | table | 1004 B | `call_00_ET_3yk…` | — |

### Fda Safety Officer  ·  10 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/fda-safety-officer/code/scripts/apply_b7h3_safety_revision3_corrections.py` | code | 6.7 KB | `call_00_14Wk62…` | — |
| `work/fda-safety-officer/code/scripts/build_b7h3_safety_tables.py` | code | 15.5 KB | `call_00_FJKorH…` | — |
| `work/fda-safety-officer/code/scripts/revise_b7h3_safety_tables_for_review.py` | code | 25.9 KB | `call_01_qvw0xs…` | — |
| `work/fda-safety-officer/data/raw/b7h3_known_drugs_raw.json` | data | 4.6 KB | `call_01_ET_eTm…` | — |
| `work/fda-safety-officer/data/raw/cd276_target_info_and_constraint.json` | data | 2.8 KB | `call_00_ET_DKK…` | — |
| `work/fda-safety-officer/results/reports/b7h3_safety_assessment.md` | report | 20.8 KB | `call_01_RMcgyS…` | C11, C17 |
| `work/fda-safety-officer/data/processed/b7h3_expression_evidence_for_safety.csv` | table | 3.2 KB | `call_00_ET_kTD…` | C6 |
| `work/fda-safety-officer/results/tables/b7h3_agent_registry_lung_cancer.csv` | table | 2.3 KB | `call_00_ET_GHC…` | C10 |
| `work/fda-safety-officer/results/tables/b7h3_modality_class_toxicities.csv` | table | 4.3 KB | `call_00_ET_GHC…` | C11 |
| `work/fda-safety-officer/results/tables/b7h3_safety_signals.csv` | table | 7.8 KB | `call_00_ET_GHC…` | C10 |

### Target Biologist  ·  10 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/target-biologist/code/scripts/build_cd276_target_biology.py` | code | 22.6 KB | `call_00_VGrdf0…` | — |
| `work/target-biologist/results/figures/cd276_normal_tissue_expression.pdf` | figure | 21.1 KB | `call_00_ET_5ns…` | — |
| `work/target-biologist/results/figures/cd276_normal_tissue_expression.png` | figure | 172.6 KB | `call_00_ET_5ns…` | — |
| `work/target-biologist/results/reports/cd276_modality_biology.md` | report | 17.6 KB | `call_00_VZbLDw…` | C15 |
| `work/target-biologist/data/raw/cd276_tissue_expression_raw.csv` | table | 8.9 KB | — | — |
| `work/target-biologist/results/tables/cd276_known_clinical_drugs.csv` | table | 1.3 KB | — | — |
| `work/target-biologist/results/tables/cd276_lung_indication_drug_query_result.csv` | table | 235 B | — | — |
| `work/target-biologist/results/tables/cd276_target_biology.csv` | table | 3.3 KB | — | C1, C17 |
| `work/target-biologist/results/tables/cd276_tissue_expression_summary.csv` | table | 3.3 KB | — | — |
| `work/target-biologist/results/tables/cd276_tractability_by_modality.csv` | table | 1.1 KB | — | C1 |

### _Mcp  ·  2 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/_mcp/data/processed/2026-10-20/genetics/index.json` | data | 6.5 KB | — | — |
| `work/_mcp/data/processed/2026-10-20/single_cell/index.json` | data | 35.6 KB | — | — |

### Medchem Pharmacologist  ·  17 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/medchem-pharmacologist/code/scripts/build_b7h3_modality_ranking.py` | code | 54.6 KB | `call_00_ET_wVw…` | — |
| `work/medchem-pharmacologist/code/scripts/build_cd276_expression_summary.py` | code | 7.5 KB | `call_00_7j2D1e…` | — |
| `work/medchem-pharmacologist/results/figures/b7h3_modality_composite_scores.pdf` | figure | 22.3 KB | `call_00_920sga…` | — |
| `work/medchem-pharmacologist/results/figures/b7h3_modality_composite_scores.png` | figure | 120.5 KB | `call_00_920sga…` | — |
| `work/medchem-pharmacologist/results/figures/b7h3_modality_dimension_heatmap.pdf` | figure | 24.1 KB | `call_00_920sga…` | — |
| `work/medchem-pharmacologist/results/figures/b7h3_modality_dimension_heatmap.png` | figure | 129.1 KB | `call_00_920sga…` | — |
| `work/medchem-pharmacologist/results/figures/cd276_malignant_vs_stromal_expression.pdf` | figure | 19.8 KB | `call_00_8qtPVy…` | — |
| `work/medchem-pharmacologist/results/figures/cd276_malignant_vs_stromal_expression.png` | figure | 268.8 KB | `call_00_8qtPVy…` | — |
| `work/medchem-pharmacologist/data/processed/ranking_build.log` | log | 2.6 KB | `call_00_920sga…` | — |
| `work/medchem-pharmacologist/results/reports/b7h3_modality_recommendation.md` | report | 40.0 KB | `call_00_tU30zd…` | C12, C13 |
| `work/medchem-pharmacologist/data/processed/b7h3_mcp_query_log.csv` | table | 4.6 KB | `call_00_F2tGza…` | — |
| `work/medchem-pharmacologist/results/tables/b7h3_modality_precedent_evidence.csv` | table | 6.5 KB | `call_00_920sga…` | C16 |
| `work/medchem-pharmacologist/results/tables/b7h3_modality_ranking.csv` | table | 21.5 KB | `call_00_920sga…` | C12, C13 |
| `work/medchem-pharmacologist/results/tables/b7h3_target_vs_payload_risk_attribution.csv` | table | 3.9 KB | `call_00_920sga…` | C11 |
| `work/medchem-pharmacologist/results/tables/cd276_key_celltype_expression.csv` | table | 2.1 KB | `call_00_8qtPVy…` | — |
| `work/medchem-pharmacologist/results/tables/cd276_malignant_vs_stromal_ratios.csv` | table | 1.3 KB | `call_00_8qtPVy…` | — |
| `work/medchem-pharmacologist/results/tables/cd276_normal_lung_expression_qualification.csv` | table | 1.2 KB | `call_00_920sga…` | C6 |

### Scientific Reviewer  ·  1 artifacts

| File | Kind | Size | Produced by | Cited by |
|---|---|---|---|---|
| `work/scientific-reviewer/results/reports/b7h3_review.md` | report | 24.2 KB | `call_00_7gczD1…` | — |

## Claims and their evidence

### [✓] `C1` — CD276 is a type I cell-surface antigen that is strongly antibody-tractable, with no small-molecule tractability and no viable PROTAC route.

*Target Biologist · confidence: strong*

- **table** `work/target-biologist/results/tables/cd276_tractability_by_modality.csv` — antibody advanced-clinical TRUE and signal-peptide/TM TRUE; all small-molecule flags FALSE  ·  _✓ verified_
- **table** `work/target-biologist/results/tables/cd276_target_biology.csv` — ChEMBL L1 surface antigen; UniProt membrane localization  ·  _✓ verified_

### [✓] `C2` — CD276 is not intrinsically essential in LUAD or SCLC: mean CRISPR gene effect is -0.230 across 46 LUAD lines (2.2% essential) and -0.204 across 25 SCLC lines (0% essential), with no lineage selectivity.

*Functional Genomics Analyst · confidence: strong*

- **table** `work/functional-genomics-analyst/results/tables/cd276_depmap_luad_sclc.csv` — per-cell-line gene effect; 46 LUAD and 25 SCLC lines  ·  _✓ verified_
- **table** `work/functional-genomics-analyst/results/tables/cd276_depmap_group_comparisons.csv` — LUAD vs other NSCLC difference +0.008, p=0.77  ·  _✓ verified_

### [✓] `C3` — No CD276-locus genetic association was found for LUAD or SCLC: 0 of 8 queried GWAS contained a CD276-locus credible set, and none of 67 L2G predictions derive from LUAD or SCLC studies.

*Genomics Analyst · confidence: strong*

- **table** `work/genomics-analyst/results/tables/cd276_luad_sclc_study_cd276_locus_check.csv` — 0/8 studies with a CD276-locus credible set  ·  _✓ verified_
- **table** `work/genomics-analyst/results/tables/cd276_l2g_predictions.csv` — 67 L2G rows, all non-LUAD/SCLC traits  ·  _✓ verified_

### [✓] `C4` — In dissociated tumor transcriptomes, CD276 is higher in stromal and myeloid cells than in malignant or epithelial cells in both indications (LUAD fibroblast 75.9 vs malignant 23.6 CPM; SCLC fibroblast 68.1 vs epithelial 28.5 CPM).

*Single Cell Analyst · confidence: strong*

- **table** `work/single-cell-analyst/results/tables/cd276_luad_sclc_lineage_expression.csv` — lineage-level CPM for LUAD and SCLC  ·  _✓ verified_
- **table** `work/single-cell-analyst/results/tables/cd276_stromal_vs_tumor_symmetry.csv` — symmetric LUAD/SCLC stromal-vs-tumor comparison  ·  _✓ verified_

### [✓] `C5` — CD276 transcript was higher in LUAD tumor epithelium than paired adjacent normal in 3/3 donors, but reached at least 2-fold in only 2/3 (ratios 3.26, 3.40, 1.09) and was not statistically significant at n=3.

*Single Cell Analyst · confidence: weak*

- **table** `work/single-cell-analyst/results/tables/cd276_epithelial_tumor_vs_normal_donor_paired_summary.csv` — per-donor ratios 3.26, 3.40, 1.09  ·  _✓ verified_
- **table** `work/single-cell-analyst/results/tables/cd276_luad_paired_donor_stats.csv` — n=3 paired statistics  ·  _✓ verified_

### [✓] `C6` — Normal-tissue CD276 expression is broad and low-to-moderate, highest in skin and kidney and near-zero in hematopoietic tissues; normal lung shows 1,683 TPM bulk RNA (HPA level 4) but only HPA protein level 2 and a comparatively low cell-level transcript (13.9 CPM).

*Single Cell Analyst · confidence: moderate*

- **table** `work/single-cell-analyst/results/tables/cd276_normal_tissue_organ_summary.csv` — organ-level weighted means; skin and kidney highest, hematopoietic near zero  ·  _✓ verified_
- **table** `work/fda-safety-officer/data/processed/b7h3_expression_evidence_for_safety.csv` — normal lung 1,682.5 TPM RNA level 4, protein level 2  ·  _✓ verified_
- **table** `work/medchem-pharmacologist/results/tables/cd276_normal_lung_expression_qualification.csv` — Census normal-lung cell-level transcript 13.9 CPM  ·  _✓ verified_

### [✓] `C7` — There are zero LUAD-specific B7-H3 clinical trials, whereas 26 SCLC-contributing interventional trials exist, including 6 Phase 3 trials across 4 molecules, overwhelmingly ADCs.

*Clinical Trialist · confidence: strong*

- **table** `work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv` — 43-row curated trial table; 0 LUAD-specific, 26 SCLC-contributing, 6 Phase 3  ·  _✓ verified_
- **artifact** `work/clinical-trialist/results/reports/b7h3_clinical_landscape.md` — landscape report with phase distribution and modality breakdown  ·  _✓ verified_

### [✓] `C8` — Only 4 of 43 curated B7-H3 trials have posted ClinicalTrials.gov results, and the only SCLC-specific posted result is MGC018 with ORR 0/9 (n=9); no LUAD-specific outcome is posted.

*Clinical Trialist · confidence: strong*

- **table** `work/clinical-trialist/results/tables/b7h3_posted_results_extract.csv` — MGC018 SCLC n=9 ORR 0/9; no LUAD-specific outcome  ·  _✓ verified_
- **table** `work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv` — 4/43 trials with posted results  ·  _✓ verified_

### [✓] `C9` — Clinical precedence establishes B7-H3 feasibility in SCLC but not efficacy; the completed Phase 3 ARTEMIS-008 trial has no posted results, so a SCLC go decision must be staged on a class-level Phase 3 readout.

*Clinical Trialist · confidence: moderate*

- **artifact** `work/clinical-trialist/results/reports/b7h3_clinical_landscape.md` — ARTEMIS-008 completed with no results module; feasibility vs efficacy distinction  ·  _✓ verified_
- **table** `work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv` — ARTEMIS-008 NCT06498479 status  ·  _✓ verified_

### [✓] `C10` — CD276 is moderately loss-of-function tolerant (o/e 0.667); the queried databases contain no target-level OpenFDA adverse events, mouse phenotypes, or pharmacogenomic records, and no FDA records at all for ifinatamab deruxtecan or vobramitamab duocarmazine, which are evidence gaps rather than clean safety.

*Fda Safety Officer · confidence: strong*

- **table** `work/fda-safety-officer/results/tables/b7h3_safety_signals.csv` — LoF o/e 0.667; zero target-level AE/mouse/PGx records  ·  _✓ verified_
- **table** `work/fda-safety-officer/results/tables/b7h3_agent_registry_lung_cancer.csv` — no FDA records for I-DXd or MGC018; enoblituzumab/omburtamab records with zero warnings  ·  _✓ verified_

### [✓] `C11` — The dominant safety risk for a B7-H3 ADC is payload-level, notably ILD/pneumonitis and myelosuppression, rather than target-level toxicity; prior thoracic radiation and checkpoint pneumonitis narrow the pulmonary safety margin in both indications.

*Fda Safety Officer · confidence: moderate*

- **table** `work/medchem-pharmacologist/results/tables/b7h3_target_vs_payload_risk_attribution.csv` — 11 risks classified as target-level vs payload-level  ·  _✓ verified_
- **table** `work/fda-safety-officer/results/tables/b7h3_modality_class_toxicities.csv` — payload/modality-level toxicities marked not B7-H3 biology  ·  _✓ verified_
- **artifact** `work/fda-safety-officer/results/reports/b7h3_safety_assessment.md` — risk-benefit framing for LUAD and SCLC  ·  _✓ verified_

### [✓] `C12` — ADC ranks first in both indications; SCLC is a staged GO (composite 4.20) conditional on class-level Phase 3 efficacy and a differentiated profile, while LUAD is deprioritized (ADC composite 2.90, clinical precedence 1/5).

*Medchem Pharmacologist · confidence: moderate*

- **table** `work/medchem-pharmacologist/results/tables/b7h3_modality_ranking.csv` — SCLC ADC 4.20 staged GO; LUAD ADC 2.90 deprioritized  ·  _✓ verified_
- **artifact** `work/medchem-pharmacologist/results/reports/b7h3_modality_recommendation.md` — revised indication-specific recommendations  ·  _✓ verified_

### [✓] `C13` — The decisive de-risking experiment is paired quantitative surface B7-H3 density plus internalization in tumor versus normal lung, with proposed gates of at least 50,000 molecules/cell, tumor/normal ratio at least 3, internalization at least 40%, and at least 30% PDX regression.

*Medchem Pharmacologist · confidence: moderate*

- **artifact** `work/medchem-pharmacologist/results/reports/b7h3_modality_recommendation.md` — go/no-go gates and decisive experiment  ·  _✓ verified_
- **table** `work/medchem-pharmacologist/results/tables/b7h3_modality_ranking.csv` — conditions attached to the ADC recommendation  ·  _✓ verified_

### [✓] `C14` — A canonical B7-H3 receptor is not established in the queried interaction data and no high-confidence physical interaction was retrieved; co-inhibitory versus co-stimulatory function remains unresolved.

*Bio Pathways Ppi Analyst · confidence: moderate*

- **table** `work/bio-pathways-ppi-analyst/results/tables/cd276_pathways_interactions.csv` — interaction evidence is textmining/coexpression; no receptor-grade partner  ·  _✓ verified_
- **figure** `work/bio-pathways-ppi-analyst/results/figures/cd276_partner_confidence.png` — only textmining-only CD8A exceeds 0.7  ·  _✓ verified_

### [✓] `C15` — Material evidence gaps remain: tumor/normal surface-protein density, internalization, and shedding are not retrievable from the configured databases; SCLC single-cell data come from one dataset (9 donors); and Tahoe-100M perturbation data were unavailable.

*Target Biologist · confidence: strong*

- **artifact** `work/target-biologist/results/reports/cd276_modality_biology.md` — internalization, shedding, surface density, isoform-resolved expression not retrievable  ·  _✓ verified_
- **table** `work/single-cell-analyst/results/tables/cd276_dataset_inventory.csv` — SCLC 31,540 cells from 1 dataset/9 donors  ·  _✓ verified_
- **table** `work/functional-genomics-analyst/results/tables/cd276_tahoe_query_status.json` — TAHOE_DATA_PATH not set  ·  _✓ verified_

### [✓] `C16` — Although no LUAD-specific B7-H3 trial exists, LUAD patients are eligible in at least three nonsquamous-NSCLC trials (NCT07464327 Phase 3, NCT06780085 Phase 2, NCT07824882 Phase 2), so absence of a LUAD-specific trial is not absence of LUAD evidence.

*Medchem Pharmacologist · confidence: strong*

- **table** `work/medchem-pharmacologist/results/tables/b7h3_modality_precedent_evidence.csv` — three nonsquamous-NSCLC trials with LUAD eligibility  ·  _✓ verified_
- **table** `work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv` — trial scope and indications  ·  _✓ verified_

### [✓] `C17` — Mouse CD276 identity is only 52.4%, whereas macaque identity is 94.6%, making mouse a poor toxicology species for a human-selective B7-H3 agent.

*Fda Safety Officer · confidence: strong*

- **table** `work/target-biologist/results/tables/cd276_target_biology.csv` — homologue sequence identity by species  ·  _✓ verified_
- **artifact** `work/fda-safety-officer/results/reports/b7h3_safety_assessment.md` — cross-species identity and toxicology-species implication  ·  _✓ verified_

## Reproducing this run

```bash
./run.sh verify 20261020-085513-evaluate-the-therapeutic-candida-a03f0a23   # check file hashes and evidence coverage
./run.sh verify 20261020-085513-evaluate-the-therapeutic-candida-a03f0a23 --rerun   # also re-execute analysis scripts
./run.sh replay 20261020-085513-evaluate-the-therapeutic-candida-a03f0a23   # re-run the same turns into a new run dir
```

`verify` checks recorded files, claims and report references. With `--rerun`, it also re-executes the analysis scripts under `work/*/code/` and compares the reproduced outputs. `replay` re-runs the agents against the same pinned models and prompts — LLM sampling means it is comparable, not bit-identical.

<details><summary>Pinned configuration</summary>

```json
{
  "session_id": "f528cbed-f3bf-40b4-85f8-e31264fc6ba0",
  "cso_model": "claude-sonnet-4-5-20250929",
  "specialist_model": "claude-sonnet-4-5-20250929",
  "specialist_model_label": "claude-sonnet-4-5-20250929",
  "effort": "xhigh",
  "max_turns": 100,
  "python": "3.11.17",
  "host": "n4",
  "started": "2026-10-20T08:55:13.111814",
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
  "total_cost_usd": 28.580156,
  "num_turns": 1,
  "interrupted_turns": [],
  "data_source_errors": [
    {
      "tool_use_id": "call_01_lMwkDWjNO3K07gNZp11Q0009",
      "tool_name": "mcp__functional_genomics__find_drugs_affecting_gene",
      "error": "{\"status\": \"tool_error\", \"tool\": \"find_drugs_affecting_gene\", \"error\": \"Query failed: TAHOE_DATA_PATH not set in environment. Set it to the directory containing Tahoe pseudobulk parquet files.\", \"instruction\": \"This call did not produce evidence. Report the failure and its effect on the analysis. Identify any alternative source explicitly; do not attribute it to this failed call.\"}"
    },
    {
      "tool_use_id": "call_00_Tfn9b6jMYwYYnyDf4Z3H0163",
      "tool_name": "mcp__functional_genomics__query_drug_perturbation",
      "error": "{\"status\": \"tool_error\", \"tool\": \"query_drug_perturbation\", \"error\": \"Query failed: TAHOE_DATA_PATH not set in environment. Set it to the directory containing Tahoe pseudobulk parquet files.\", \"instruction\": \"This call did not produce evidence. Report the failure and its effect on the analysis. Identify any alternative source explicitly; do not attribute it to this failed call.\"}"
    },
    {
      "tool_use_id": "call_01_u28eJz9GM9jP9PAzZQTW2232",
      "tool_name": "mcp__functional_genomics__query_drug_perturbation",
      "error": "{\"status\": \"tool_error\", \"tool\": \"query_drug_perturbation\", \"error\": \"Query failed: TAHOE_DATA_PATH not set in environment. Set it to the directory containing Tahoe pseudobulk parquet files.\", \"instruction\": \"This call did not produce evidence. Report the failure and its effect on the analysis. Identify any alternative source explicitly; do not attribute it to this failed call.\"}"
    },
    {
      "tool_use_id": "call_01_DOF6Uectv34B19PTYOoA5705",
      "tool_name": "mcp__disease__search_diseases_by_name",
      "error": "<tool_use_error>Cancelled: parallel tool call Bash(ls -d /mnt/beegfs/xqinag/projects/TheVir\u2026) errored</tool_use_error>"
    },
    {
      "tool_use_id": "call_02_43FlureTpHaNmDSPz9kn9418",
      "tool_name": "mcp__disease__search_diseases_by_name",
      "error": "<tool_use_error>Cancelled: parallel tool call Bash(ls -d /mnt/beegfs/xqinag/projects/TheVir\u2026) errored</tool_use_error>"
    },
    
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

*Generated 2026-10-20 11:54:46 by `src/utils/run_report.py`.*