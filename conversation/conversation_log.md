# B7-H3 lung cancer (LUAD + SCLC) formal case-study run — conversation record

This file is the engineering-side audit trail of every message sent to and
received from the Virtual Biotech system for this case study, kept
separately from the repo's own per-run records (`runs/<RUN_ID>/`) as a
convenience index. The repo's own run directory remains the authoritative
source (MANIFEST.json, logs/trace.jsonl, evidence/claims.json, work/).

## Prior attempt (superseded, not used for results)

- Run dir: `runs/20261020-084506-evaluate-the-therapeutic-candida-da2a2b86`
- Query used a generic "lung cancer" framing (not LUAD+SCLC) and did not
  disable WebSearch/WebFetch. Terminated by user decision after confirming
  51+ WebSearch calls and NSCLC+SCLC (not LUAD+SCLC) scope — does not match
  the intended study design. Left on disk, not deleted, but excluded from
  any findings.
- **Incident:** the first termination attempt (`kill -TERM` on the Python
  wrapper/run_vbt.py PID) did not actually stop the run. The underlying
  bundled `claude` CLI subprocess spawned by `claude_agent_sdk` (a separate
  PID, not a child the wrapper's death reaped) survived as an orphan and
  kept executing autonomously — confirmed by this run's `trace.jsonl`
  growing from 585 to 831 events over the ~45 minutes it went unnoticed.
  Found and fixed by checking for orphaned descendants directly (`ps -eo
  pid,ppid,etime,stat,%cpu,comm`) rather than trusting the first kill;
  `kill -TERM` on the orphan's actual PID stopped it and all its MCP-server
  children. Lesson: when stopping a `claude_agent_sdk`-based run, verify the
  bundled CLI subprocess (not just the launching Python process) is gone,
  by checking trace-file growth stops, not just that the PID you sent
  SIGTERM to disappeared.

## Formal run

- Script: `validation/run_b7h3_formal.py` (DeepSeek-routed via
  subprocess-scoped env vars only; strips WebFetch/WebSearch from CSO +
  all specialists via a `ClaudeAgentOptions` monkeypatch, no repo edits;
  disease scope stated explicitly in the query text).

### Turn 1 — initial query (sent)

```
Evaluate the therapeutic candidacy of B7-H3 (CD276) in lung cancer. Scope
the disease strictly to lung adenocarcinoma (LUAD) and small cell lung
cancer (SCLC) -- not NSCLC broadly, not other lung histologies. General
web search and web scraping are disabled for this study; use only the
configured database MCP servers (Open Targets, CELLxGENE Census, etc.)
and your own prior knowledge, clearly labeled as such when you rely on
it. Spatial transcriptomics / Visium analysis is out of scope for this
pass.
```

- Run dir: `runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23`
- Manifest status: `incomplete` (not `completed`) — several MCP tool calls failed
  during the CSO's final verification/revision pass (transient 403s and
  other errors on `mcp__functional_genomics__find_drugs_affecting_gene`,
  `query_drug_perturbation`, `mcp__disease__search_diseases_by_name`,
  `mcp__target__search_targets_by_name`, `mcp__single_cell__get_anndata`,
  `count_cells`, `get_census_info`). The system's own final message
  surfaces this as a "Data/evidence warning" rather than hiding it.
  WebSearch/WebFetch count: 0 throughout the entire run (confirmed by grep
  over the full trace.jsonl after completion).
- 9 specialists contributed (2 more than the 7 originally dispatched,
  pulled in by the reviewer's correction loop): bio-pathways-ppi-analyst,
  clinical-trialist, fda-safety-officer, functional-genomics-analyst,
  genomics-analyst, medchem-pharmacologist, scientific-reviewer,
  single-cell-analyst, target-biologist.
- The scientific-reviewer caught and sent back two overstated claims before
  synthesis: a single-cell "≥2× tumor/normal in 3/3 donors" claim that was
  actually true in only 2/3 donors, and an unconditional SCLC "GO" that was
  really feasibility-only, not efficacy-proven.

### CSO's final reply (verbatim, from `formal_run.log`)

```
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
```

### Artifacts

- Run dir: `runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23`
- README.md and audit.html generated
- `report/FINAL_REPORT.md` (8.6KB)
- `evidence/claims.json` — 17 claim-evidence objects
- 208 total artifacts (68 data, 80 table, 24 code, 9 report, 19 figure, 8 log)
- Specialists in the manifest: `_cso`, `_mcp`, `bio-pathways-ppi-analyst`,
  `clinical-trialist`, `fda-safety-officer`, `functional-genomics-analyst`,
  `genomics-analyst`, `medchem-pharmacologist`, `scientific-reviewer`,
  `single-cell-analyst`, `target-biologist`
