# B7-H3 (CD276) clinical landscape in LUAD and SCLC

**As of:** 2026-10-20
**Source:** ClinicalTrials.gov API v2, queried through the configured
`clinicaltrials` MCP server (global searches, `country=None`). Registry results
modules were read where posted. No general web search, publications, or
conference abstracts were queried.
**Scope:** LUAD and SCLC only. NSCLC trials are included as labelled context
because LUAD is an NSCLC subset; pan-tumor trials are included only where an
SCLC cohort is explicitly listed.

## Headline counts

| Population | Trials | Note |
|---|---:|---|
| LUAD-specific | **0** | No trial has a LUAD-specific condition or cohort |
| SCLC-specific, interventional | **16** | Conditions/title are SCLC |
| SCLC-specific, expanded access | **1** | NCT07535359 medical access program |
| Pan-tumor with explicit SCLC cohort | **10** | SCLC cohort labelled; cohort sizes often not reported |
| **SCLC-contributing, interventional** | **26** | 16 SCLC-specific + 10 pan-tumor |
| NSCLC context (not LUAD-specific) | 16 | Included for LUAD-adjacent inference only |

The broad `lung adenocarcinoma` condition search returned 6 registry hits, but
none is a LUAD-specific trial: one is not B7-H3-directed (NCT04514484,
cabozantinib + nivolumab), and five are pan-tumor/NSCLC/SCLC trials that mention
lung adenocarcinoma only in eligibility text (NCT02628535, NCT05914116,
NCT06242470, NCT06953089, NCT07509034). See
`results/tables/b7h3_luad_search_hits.csv`.

## Phase distribution (SCLC-contributing, n=26)

| Phase (registry) | Trials |
|---|---:|
| Phase 3 | 6 |
| Phase 2 | 5 (1 withdrawn, n=0) |
| Phase 1/2 | 10 |
| Phase 1 | 5 |

Highest phase in SCLC is **Phase 3**. The six Phase 3 trials are ifinatamab
deruxtecan (I-DXd; NCT06203210), HS-20093/risvutatug rezetecan (NCT06498479,
NCT06526624, NCT07099898), MHB088C (NCT06954246), and YL201 (NCT06612151).
NCT07076095 (IBB0979) is titled Phase II/III but is registered as Phase 2.
Highest phase in the NSCLC context set is also Phase 3 (NCT07464327, HS-20093 +
adebrelimab, not yet recruiting, previously treated nonsquamous NSCLC).

## Dominant agents and modalities

B7-H3 antibody-drug conjugates (ADCs) dominate: I-DXd (DXd payload), HS-20093 /
risvutatug rezetecan / GSK5764227, MGC018 / vobramitamab duocarmazine,
MHB088C, YL201, DB-1311 / BNT324, MGC026, and ABBV-155. Non-ADC modalities are
a minority: one B7-H3 CAR-T (NCT07509034), one 177Lu-B7-H3 radioligand
(NCT07189871), the naked antibody enoblituzumab (NSCLC context), the B7-H3xCD3
DART MGD009 (NSCLC context, terminated), a B7-H3xIL-10R fusion (IBB0979), and a
B7-H3 mAb-IL-15 fusion (SPGL008; NSCLC context). Several SCLC trials combine a
B7-H3 ADC with a DLL3 T-cell engager (gocatamig) or an anti-PD-L1.

## Trial existence versus reported results

**Only 4 of the 43 curated trials have results posted in ClinicalTrials.gov**
(any indication): NCT06227546 (MGC018, SCLC), NCT05551117 (MGC018, pan-tumor
Part 2 with an SCLC-eligible cohort), NCT02475213 (enoblituzumab +
pembrolizumab, NSCLC), and NCT03729596 (MGC018, NSCLC expansion).

### SCLC-specific posted result

- **NCT06227546**, MGC018, Phase 2, relapsed/refractory ES-SCLC, **n=9**:
  ORR **0/9 (0%)**. Serious adverse events at the >=5% threshold: atrial
  fibrillation 3/9, lung infection 1/9, sepsis 1/9, respiratory failure 1/9,
  creatinine increased 1/9, rash maculo-papular 1/9, hypotension 1/9. The study
  is active, not recruiting; the registry does not state why enrolment stopped
  at 9. This is a small, under-enrolled single-arm trial and is not evidence of
  class-level failure.

**No SCLC Phase 3 results are posted.** ARTEMIS-008 (NCT06498479, HS-20093 vs
topotecan) is marked COMPLETED with no results module. I-DXd, MHB088C, YL201,
and the other SCLC Phase 3 trials have no posted results. "Trial exists" is not
"efficacy demonstrated."

### NSCLC-context posted results (not LUAD-specific)

- **NCT02475213**, enoblituzumab + pembrolizumab, Phase 1: NSCLC PD-1/PD-L1
  naive ORR **33.3% (5/15; 95% CI 11.8-61.6)**, mPFS 5.1 months, mOS 10.3
  months; PD-1/PD-L1 experienced ORR **10.5% (2/19; 95% CI 1.3-33.1)**, mPFS
  3.5 months, mOS 6.0 months.
- **NCT03729596**, MGC018, Phase 1/2 NSCLC expansion: ORR **15.0% (3/20
  evaluable; 95% CI 3.2-37.9)**, mPFS 4.0 months, mOS 7.0 months. Terminated
  for a business decision.
- **NCT05551117**, MGC018, Phase 2 Part 2 (SCLC-eligible mixed cohort):
  **n=4, ORR 0%**, no SCLC-specific breakdown. Terminated for business reasons.

These are small single-arm Phase 1/2 experiences; none reports a LUAD cohort
separately, and none is a randomised LUAD efficacy result.

## Clinical-precedence assessment

**SCLC: strong clinical precedence.** B7-H3 is the target of six Phase 3 ADC
trials, including randomised comparisons against topotecan or physician's
choice, plus Phase 1/2 CAR-T and radioligand programmes. This establishes
target feasibility, a competitive development landscape, and substantial
investment in SCLC. It does **not** establish efficacy: the only posted
SCLC-specific result is 0/9 in a small MGC018 trial, and the Phase 3 readouts
are not in the registry.

**LUAD: no direct clinical precedence.** No LUAD-specific trial exists. The
closest evidence is the NSCLC context set, including a Phase 3 trial of HS-20093
+ adebrelimab in previously treated nonsquamous NSCLC (NCT07464327, not yet
recruiting) and Phase 1/2 enoblituzumab and MGC018 experiences that do not
report LUAD separately. Any LUAD efficacy claim from this stream would be
indirect and must be labelled as such.

**Safety:** Registry-posted safety data are limited to the MGC018 SCLC
experience (notably atrial fibrillation 3/9 and infectious/respiratory serious
events) and the NSCLC-context trials. No class-level safety conclusion is
supported from posted registry results alone.

## Limitations

1. **Registry results lag.** Most trials are recruiting or not yet recruiting;
   absence of posted results is not evidence of failure.
2. **Database coverage gap.** The configured drug MCP / ChEMBL known-drug
   mapping contains only enoblituzumab and 8H9-131I for CD276, with **zero
   lung-cancer indications**; the bundled ChEMBL clinical parquet has 9 CD276
   rows across 7 NCTs and **zero lung-related rows** (see
   `cd276_chembl_parquet_coverage.csv`). This is a coverage gap, not evidence of
   absence. The ClinicalTrials.gov registry is the primary evidence here.
3. **Pan-tumor cohorts.** SCLC cohort sizes and SCLC-specific outcomes are
   usually not reported separately; where results exist, they may pool
   histologies.
4. **Target linkage.** Most included trials state B7-H3/CD276 explicitly.
   ABBV-155 and MGC026 are included on agent identity from prior knowledge
   because the registry record does not name the target; these linkages are
   labelled moderate. YL201 is supported by NCT06612151's B7-H3-expression
   testing requirement.
5. **No publications or conference abstracts were queried.** Prior-knowledge
   efficacy claims are not made here; only registry-posted results are reported.

## Evidence files

- `results/tables/b7h3_luad_sclc_trials.csv` - 43-row curated trial table.
- `results/tables/b7h3_posted_results_extract.csv` - verified posted results.
- `results/tables/b7h3_ctgov_query_counts.csv` - all registry query counts.
- `results/tables/b7h3_luad_search_hits.csv` - 6 LUAD-search hits and why none
  is LUAD-specific.
- `results/tables/cd276_chembl_parquet_coverage.csv` and
  `results/tables/cd276_known_drugs_drug_mcp.csv` - database-coverage audit.
- `results/figures/b7h3_phase_landscape.png` / `.pdf` - phase distribution.
- `data/processed/b7h3_trial_selection_audit.csv` - curated table with registry
  query provenance per trial.
- `data/raw/ctgov_b7h3_search_index.json` and `ctgov_b7h3_search_counts.json` -
  raw query index and counts.
