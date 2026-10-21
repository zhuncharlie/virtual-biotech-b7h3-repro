I'll orchestrate this as a full therapeutic-candidacy evaluation across the Target ID, Safety, Modality, and Clinical divisions, scoped strictly to LUAD and SCLC. First, let me load the run-organization contract and inspect the run directory.

The run is fresh and the provenance server is configured. I'll record the analysis plan (7 parallel evidence streams, then modality ranking, then QA).

Plan recorded (9 steps). I'm launching seven parallel evidence streams across the Target ID, Safety, Clinical, and Modality divisions; the modality ranker and scientific reviewer will follow once their upstream inputs exist.

All seven parallel streams returned. The picture is already differentiated: SCLC has substantial clinical investment (ADCs, 6 Phase 3 trials) while LUAD has zero B7-H3-specific trials; genetic causality is absent in both; and single-cell data show CD276 transcript is highest in stromal cells, which cuts against a simple tumor-cell-selectivity story. I'm now sending the biology and clinical landscape to the modality ranker.

The modality ranker converges on ADC-first, with SCLC as GO and LUAD as conditional/no-go. Before synthesizing, I'm sending all eight outputs to the scientific reviewer to stress-test scope, data support, and the two places the evidence could be over-read: the stromal-vs-malignant expression pattern and the "zero LUAD trials" claim.

The reviewer verified the headline numbers but flagged three material corrections: the single-cell "2× in 3/3 donor pairs" claim is wrong (individual ratios 3.26, 3.40, 1.09 — ≥2× in only 2/3), the SCLC "GO" is premature because feasibility is established but efficacy is not, and the LUAD "no-go" conflates absence of LUAD-specific trials with absence of LUAD evidence. I'm sending targeted revisions to those three specialists before synthesizing.

The modality revision succeeded; the single-cell and safety revisions hit transient 403 errors before doing any work. I'm retrying those two — no analysis changes, just the reviewer's corrections.

All corrections are in. I'm now reconciling the exact artifact paths from the run manifest before filing the claim-evidence objects.

All 17 claims are filed and evidence-verified. I'm writing the run report, then I'll give you the decision summary.

## Bottom line

B7-H3 is a **credible surface-antigen target for payload delivery in SCLC, but not a validated one**. It is **not a defensible signalling target** in either histology, and **LUAD should be deprioritized on strategic grounds, not because the biology is disqualifying**. ADC is the modality of choice in both indications.

The scientific reviewer caught two overstatements before synthesis — a single-cell "2× tumor/normal in 3/3 donors" claim that was actually ≥2× in only 2/3, and an unconditional SCLC "GO" that is really feasibility-only. Both were corrected in the underlying artifacts.

## What the evidence shows

**Target biology (Modality division).** CD276 is a type I surface antigen with strong antibody tractability, no small-molecule tractability, and no viable PROTAC route[[claim:C1]]. No canonical B7-H3 receptor is established in the queried interaction data, and co-inhibitory versus co-stimulatory function remains unresolved[[claim:C14]]. The therapeutic rationale must therefore be payload delivery or cell depletion, not pathway inhibition.

**Genetic and functional support (Target ID division).** Human genetics is absent for these indications: 0/8 queried LUAD/SCLC GWAS contained a CD276-locus credible set, and 0/67 L2G predictions derive from LUAD or SCLC studies[[claim:C3]]. CD276 is also non-essential in both histologies — mean CRISPR gene effect −0.230 in 46 LUAD lines (2.2% essential) and −0.204 in 25 SCLC lines (0% essential), with no lineage selectivity[[claim:C2]]. This rules out a signalling-inhibitor monotherapy but does not undercut an ADC.

**Expression and selectivity (Target ID division).** In dissociated tumor transcriptomes, CD276 is higher in fibroblasts and macrophages than in malignant/epithelial cells in **both** indications (LUAD fibroblast 75.9 vs malignant 23.6 CPM; SCLC fibroblast 68.1 vs epithelial 28.5 CPM)[[claim:C4]]. LUAD tumor epithelium was higher than paired adjacent normal in 3/3 donors, but reached ≥2× in only 2/3 (ratios 3.26, 3.40, 1.09) and was not significant at n=3[[claim:C5]]. Normal-tissue expression is broad and low-to-moderate, highest in skin/kidney and near-zero in hematopoietic tissue; normal lung is 1,683 TPM by bulk RNA (HPA level 4) but only protein level 2 and 13.9 CPM at cell level[[claim:C6]]. The key caveat: these are transcripts, not surface protein. The stromal signal is a shared antigen-sink/bystander concern, not a LUAD-specific disqualifier.

**Clinical precedence (Clinical Officers).** There are **zero LUAD-specific B7-H3 trials**, versus **26 SCLC-contributing trials including 6 Phase 3 trials across 4 molecules**, overwhelmingly ADCs[[claim:C7]]. LUAD patients are nonetheless eligible in at least three nonsquamous-NSCLC trials (NCT07464327, NCT06780085, NCT07824882), so absence of a LUAD-specific trial is not absence of LUAD evidence[[claim:C16]]. Efficacy is unproven: only 4/43 curated trials have posted results, the sole SCLC-specific posted result is MGC018 ORR 0/9 (n=9), and the completed Phase 3 ARTEMIS-008 has no posted results[[claim:C8]][[claim:C9]].

**Safety (Safety division).** CD276 is moderately LoF-tolerant (o/e 0.667); target-level OpenFDA AEs, mouse phenotypes, and PGx records are absent, and there are no FDA records for I-DXd or MGC018 — evidence gaps, not clean safety[[claim:C10]]. Mouse CD276 identity is only 52.4% versus macaque 94.6%, making mouse a poor toxicology species[[claim:C17]]. The dominant ADC risk is payload-level — ILD/pneumonitis and myelosuppression — not target biology, and prior thoracic radiation or checkpoint pneumonitis narrows the pulmonary margin[[claim:C11]].

## Recommendation

| Indication | Decision | Modality |
|---|---|---|
| **SCLC** | **Staged GO** (composite 4.20) — conditional on a positive class-level Phase 3 readout and a differentiated profile | B7-H3 ADC |
| **LUAD** | **Deprioritized** (ADC composite 2.90; clinical precedence 1/5) | ADC internally ranked first, but no LUAD-specific precedence |

ADC ranks first in both indications; T-cell engager is the backup, CAR-T and radioimmunotherapy are research options[[claim:C12]]. A me-too B7-H3 ADC is not investable given the crowded SCLC class; differentiation must come from safety, a novel payload/linker, rational combination (e.g., DLL3 TCE or PD-L1), or a biomarker-defined population.

**Decisive de-risking experiment:** paired quantitative surface B7-H3 density plus internalization in patient tumor versus normal lung, with proposed gates of ≥50,000 molecules/cell, tumor/normal ≥3, internalization ≥40%, and ≥30% PDX regression[[claim:C13]]. The external readout to watch is the first Phase 3 OS result for a B7-H3 ADC (ARTEMIS-008 or I-DXd vs physician's choice)[[claim:C9]].

**Material gaps:** tumor/normal surface-protein density, internalization, and shedding are not retrievable from the configured databases; SCLC single-cell data come from one dataset (9 donors); and Tahoe-100M perturbation data were unavailable[[claim:C15]]. These gaps are why the SCLC recommendation is staged rather than unconditional.

The full audited report is at `report/FINAL_REPORT.md`; 17 claim-evidence objects are filed in `evidence/claims.json`.

**Suggested next steps:**
1. **Commission the paired surface-density/internalization study** in ≥20 SCLC and LUAD resections versus normal lung — it resolves the single largest unknown and gates both indications.
2. **Design the SCLC differentiation package** (novel payload/linker or DLL3 TCE/PD-L1 combination) — a me-too ADC has no commercial path in this crowded class.
3. **Set a Phase 3 readout trigger** (ARTEMIS-008 / I-DXd OS) — no SCLC commitment should precede it.
4. **If LUAD remains strategically important, benchmark against TROP2/HER3 ADCs** and define a biomarker niche before any investment.

Would you like me to pursue any of these?

Data/evidence warning: these tools failed during this turn: mcp__functional_genomics__find_drugs_affecting_gene, mcp__functional_genomics__query_drug_perturbation, mcp__disease__search_diseases_by_name, mcp__target__search_targets_by_name, mcp__single_cell__get_anndata, mcp__single_cell__count_cells, mcp__single_cell__get_census_info. Their results cannot support this answer. Any alternative sources must be identified separately; evidence coverage is incomplete.