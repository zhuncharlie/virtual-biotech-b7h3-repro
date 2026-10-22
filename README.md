# B7-H3 (CD276) in LUAD/SCLC — Virtual Biotech reproduction

A reproduction of the "B7-H3 lung-cancer" case study from *The Virtual
Biotech* (bioRxiv 10.64898/2026.02.23.707551), run against the original,
**unmodified** [TheVirtualBiotech](https://github.com/harrisongzhang/TheVirtualBiotech)
codebase at commit [`71f9da6`](BASELINE.md), with the model layer routed to
DeepSeek instead of Anthropic. See [`BASELINE.md`](BASELINE.md) for exactly
what was (and wasn't) changed to make that work.

**Two rounds, same setup:**
- **Round 1** (below): genetics, single-cell expression, functional
  genomics, pathways/PPI, clinical trials, safety, target biology, modality
  ranking — in `run_round1/`,
  [`conversation/conversation_log.md`](conversation/conversation_log.md).
- **Round 2** ([jump to section](#round-2-spatial-liana-and-a-full-review-cycle)):
  adds Visium spatial transcriptomics + cell2location (panels 4E/S5B) and
  LIANA ligand-receptor signalling (4D/S5A), plus a full scientific-review →
  revise → re-review cycle — in `run_round2/`,
  [`conversation/conversation_log_round2.md`](conversation/conversation_log_round2.md).

**This is the system's own output.** The multi-agent run (CSO + specialists,
real MCP database calls, a real scientific-reviewer pass) was executed
end-to-end by the actual repo; nothing here was written or corrected by the
engineering assistant that orchestrated the run.

## Round 1 status: **INCOMPLETE**

The run's own manifest records `"status": "incomplete"` (not
`"completed"`), because several MCP tool calls failed during the CSO's final
verification pass (see [Failed MCP calls](#failed-mcp-calls-and-their-actual-impact)
below). Despite that, the CSO still produced a full synthesized
recommendation, with the gap disclosed in its own closing message rather
than hidden.

**Done:**
- Full 9-step analysis plan executed (genetics, single-cell, functional
  genomics, pathways/PPI, clinical trials, safety, target biology, modality
  ranking) across LUAD and SCLC only, with zero general web search.
- A real scientific-review pass caught and the specialists corrected two
  overstated claims and one scope/framing error (see
  [Reviewer corrections](#reviewer-corrections) below).
- 17 claim-evidence objects filed, 208 artifacts produced, final
  recommendation delivered.

**Missing / not attempted:**
- Cell-cell communication analysis (CellPhoneDB/CellChat/LIANA) — never
  part of the CSO's plan for this question.
- Survival analysis (lifelines/Kaplan-Meier/Cox) — same; not planned.
- Spatial transcriptomics / Visium — explicitly out of scope by the user's
  own instruction for this pass.
- Protein-level tumor/normal surface density, internalization, and shedding
  data — not retrievable from any configured database; flagged by every
  specialist and by the reviewer as the single decision-critical gap.
- Tahoe-100M drug-perturbation data — environment misconfiguration
  (`TAHOE_DATA_PATH` unset), see below.

## Analysis completion matrix

| Analysis | Status | Scripts | Data | Report |
|---|---|---|---|---|
| **Genetics** (GWAS/L2G/QTL) | ✅ Done | [`run_round1/work/genomics-analyst/code/scripts/`](run_round1/work/genomics-analyst/code/scripts/) | [`run_round1/work/genomics-analyst/data/`](run_round1/work/genomics-analyst/data/) | [`cd276_genetic_evidence.md`](run_round1/work/genomics-analyst/results/reports/cd276_genetic_evidence.md) |
| **Functional genomics** (DepMap CRISPR) | ✅ Done | [`cd276_depmap_analysis.py`](run_round1/work/functional-genomics-analyst/code/scripts/cd276_depmap_analysis.py) | [`run_round1/work/functional-genomics-analyst/data/`](run_round1/work/functional-genomics-analyst/data/) | [`cd276_functional_genomics.md`](run_round1/work/functional-genomics-analyst/results/reports/cd276_functional_genomics.md) |
| **Single-cell expression** (CELLxGENE Census) | ✅ Done | [`run_round1/work/single-cell-analyst/code/scripts/`](run_round1/work/single-cell-analyst/code/scripts/) (01–08) | Results committed; raw h5ad/parquet excluded, see [`data_provenance.md`](data_provenance.md) | [`cd276_single_cell_atlas_report.md`](run_round1/work/single-cell-analyst/results/reports/cd276_single_cell_atlas_report.md) |
| **Pathway / PPI** (Reactome, GO, STRING, IntAct) | ✅ Done | [`run_round1/work/bio-pathways-ppi-analyst/code/scripts/`](run_round1/work/bio-pathways-ppi-analyst/code/scripts/) | [`run_round1/work/bio-pathways-ppi-analyst/data/`](run_round1/work/bio-pathways-ppi-analyst/data/) | [`cd276_pathway_safety.md`](run_round1/work/bio-pathways-ppi-analyst/results/reports/cd276_pathway_safety.md) |
| **Clinical trial landscape** (ClinicalTrials.gov) | ✅ Done | [`run_round1/work/clinical-trialist/code/scripts/`](run_round1/work/clinical-trialist/code/scripts/) | [`run_round1/work/clinical-trialist/data/`](run_round1/work/clinical-trialist/data/) | [`b7h3_clinical_landscape.md`](run_round1/work/clinical-trialist/results/reports/b7h3_clinical_landscape.md) |
| **Safety** (OpenFDA, constraint, tolerability) | ✅ Done | [`run_round1/work/fda-safety-officer/code/scripts/`](run_round1/work/fda-safety-officer/code/scripts/) | [`run_round1/work/fda-safety-officer/data/`](run_round1/work/fda-safety-officer/data/) | [`b7h3_safety_assessment.md`](run_round1/work/fda-safety-officer/results/reports/b7h3_safety_assessment.md) |
| **Target biology** (tractability, isoforms, homology) | ✅ Done | [`build_cd276_target_biology.py`](run_round1/work/target-biologist/code/scripts/build_cd276_target_biology.py) | [`run_round1/work/target-biologist/data/`](run_round1/work/target-biologist/data/) | [`cd276_modality_biology.md`](run_round1/work/target-biologist/results/reports/cd276_modality_biology.md) |
| **Treatment modality ranking** (ADC/TCE/CAR-T/radioligand) | ✅ Done | [`run_round1/work/medchem-pharmacologist/code/scripts/`](run_round1/work/medchem-pharmacologist/code/scripts/) | [`run_round1/work/medchem-pharmacologist/data/`](run_round1/work/medchem-pharmacologist/data/) | [`b7h3_modality_recommendation.md`](run_round1/work/medchem-pharmacologist/results/reports/b7h3_modality_recommendation.md) |
| **Cell-cell communication** (CellPhoneDB/CellChat/LIANA) | ⬜ Not executed | — | — | — (not part of this run's plan) |
| **Spatial transcriptomics / Visium** | ⬜ Not executed | — | — | — (explicitly out of scope for this pass, by user instruction) |
| **Survival analysis** (lifelines/Kaplan-Meier/Cox) | ⬜ Not executed | — | — | — (not part of this run's plan) |

## Final report, figures, and review record

- **Final synthesized report:** [`run_round1/report/FINAL_REPORT.md`](run_round1/report/FINAL_REPORT.md)
- **Bottom line:** SCLC = staged conditional GO (ADC), composite 4.20;
  LUAD = deprioritized on competitive/strategic grounds (not biological),
  composite 2.90. See the report for full reasoning and citations.
- **Audit trail / run manifest:** [`run_round1/audit.html`](run_round1/audit.html),
  [`run_round1/MANIFEST.json`](run_round1/MANIFEST.json), [`run_round1/README.md`](run_round1/README.md)
  (the run's own auto-generated index)
- **Claim-evidence objects (17 filed):** [`run_round1/evidence/claims.json`](run_round1/evidence/claims.json)
- **Full execution trace** (2120 events): [`run_round1/logs/trace.jsonl`](run_round1/logs/trace.jsonl)
- **Figures** (all committed in full resolution):
  [single-cell expression](run_round1/work/single-cell-analyst/results/figures/),
  [DepMap essentiality](run_round1/work/functional-genomics-analyst/results/figures/cd276_depmap_luad_sclc_distribution.png),
  [modality composite scores](run_round1/work/medchem-pharmacologist/results/figures/b7h3_modality_composite_scores.png),
  [clinical phase landscape](run_round1/work/clinical-trialist/results/figures/b7h3_phase_landscape.png),
  [normal-tissue expression](run_round1/work/target-biologist/results/figures/cd276_normal_tissue_expression.png),
  [pathway/PPI partner confidence](run_round1/work/bio-pathways-ppi-analyst/results/figures/cd276_partner_confidence.png)

### Reviewer corrections

The scientific-reviewer's full report — **[`b7h3_review.md`](run_round1/work/scientific-reviewer/results/reports/b7h3_review.md)**
— is substantially more thorough than a two-item list: it contains a
per-stream verdict table (8 streams), 12 independently re-derived numeric
checks, three headline rulings, and a 10-item "minimum corrections for
synthesis" list. The two corrections most visible in the final report:

1. **Single-cell "2× tumor/normal in 3/3 donors" claim was wrong.**
   Corrected to "reached ≥2× in only 2/3 donors (ratios 3.26, 3.40, 1.09),
   not significant at n=3" — verbatim in
   [`cd276_single_cell_atlas_report.md`](run_round1/work/single-cell-analyst/results/reports/cd276_single_cell_atlas_report.md#L46-L59)
   with the full per-donor table and a paired t-test.
2. **LUAD "no-go" conflated absence of LUAD-specific trials with absence of
   LUAD evidence; SCLC "GO" was feasibility-only, not efficacy-proven.**
   Corrected in
   [`b7h3_modality_recommendation.md`](run_round1/work/medchem-pharmacologist/results/reports/b7h3_modality_recommendation.md)
   (LUAD clinical-precedence score moved 2/5 → 1/5, composite 3.15 → 2.90,
   with a full revision note; SCLC reframed as "staged GO").

**Two reviewer corrections were *not* fully carried through** to the final
synthesis (independently confirmed by re-reading both the specialist report
and `FINAL_REPORT.md`):
- The reviewer required restating CD276's gnomAD constraint (o/e 0.667) as
  "moderate constraint, not tolerance" — both the safety report and
  `FINAL_REPORT.md` still say "moderately LoF-tolerant," the exact framing
  flagged as an over-interpretation.
- The reviewer required labeling the missing Tahoe-100M data as low
  materiality, separate from the critical protein-density/internalization
  gaps — `FINAL_REPORT.md`'s "Material gaps" paragraph still lists it
  alongside the critical ones, undifferentiated.

## Failed MCP calls and their actual impact

`FINAL_REPORT.md`'s own closing line lists 7 tools as having failed "during
this turn." Cross-checking against the full execution trace
(`run_round1/logs/trace.jsonl`) found this list is **partially inaccurate** — only 5
of the 7 have any matching error event anywhere in the run:

| Tool | Real failure? | Impact |
|---|---|---|
| `mcp__functional_genomics__find_drugs_affecting_gene` | ✅ Yes, 08:59:35 | `TAHOE_DATA_PATH` was never set (persistent env misconfig, not transient). Zero drug-perturbation evidence stream. Disclosed as claim `C15` with an evidence pointer; **no other conclusion depends on it**. |
| `mcp__functional_genomics__query_drug_perturbation` | ✅ Yes, 08:59:57 ×2 | Same cause, same impact as above. |
| `mcp__single_cell__get_anndata` | ✅ Yes, 09:35:18 ("query 3.26GB exceeds 2.5GB max") | **Transient.** Succeeded on retry over a dozen times afterward (09:37 onward); the single-cell numbers in the final report (635,998 LUAD cells, 31,540 SCLC cells) were independently re-verified by the reviewer against the saved tables. **No impact on any published number.** |
| `mcp__single_cell__count_cells` | ✅ Yes, 09:36:55 ("Connection closed") | **Transient.** Succeeded both before (09:02) and after (10:29 onward). **No impact.** |
| `mcp__disease__search_diseases_by_name` | ❌ No error anywhere in trace (6/6 calls succeeded) | Listed in the warning but not actually a failure — a self-reporting inaccuracy in the system's own warning footer. |
| `mcp__target__search_targets_by_name` | ❌ No error anywhere in trace (14/14 calls succeeded) | Same — inaccurate self-report. |
| `mcp__single_cell__get_census_info` | ❌ No error anywhere in trace (2/2 calls succeeded) | Same — inaccurate self-report. |

**Net effect:** the only real, lasting evidence gap is the missing
Tahoe-100M drug-perturbation stream (a fixable environment variable, not a
data-availability problem). Nothing else in the published recommendation is
built on a failed call.

## Next steps

1. Set `TAHOE_DATA_PATH` and re-run the functional-genomics drug-perturbation
   queries to close that gap (cheap — doesn't require a new full run).
2. Correct the two un-applied reviewer requirements above (LoF framing,
   Tahoe-100M materiality label) — either by re-running the affected
   specialist's revision step or by a manual patch to the two report files,
   with a clear changelog either way.
3. Decide whether to pursue cell-cell communication and survival analysis as
   separate follow-on runs (both available in the environment —
   `liana==1.7.0`, `lifelines==0.30.3` — but never invoked here) or treat
   them as out of scope for this case study.
4. Spatial/Visium analysis remains deferred to a separate full-reproduction
   pass per the original plan; not started here.
5. The decisive de-risking experiment both the CSO and reviewer converge on:
   a paired, protein-level tumor-vs-normal B7-H3 surface density and
   internalization study — no database in this stack can supply it.

## Round 2: spatial, LIANA, and a full review cycle

Round 2 took **five run directories** across four transient
network/API interruptions (not data or code problems) to deliver; see
[`conversation/conversation_log_round2.md`](conversation/conversation_log_round2.md)
for the full narrative and [`run_round2/LINEAGE.md`](run_round2/LINEAGE.md)
for exactly which run directory holds which content.

**Final report:** [`run_round2/report/FINAL_REPORT.md`](run_round2/report/FINAL_REPORT.md) ·
**Panel-by-paper comparison:** [`run_round2/report/panel_by_paper_comparison.md`](run_round2/report/panel_by_paper_comparison.md) ·
**Workflow diagram:** [`run_round2/report/workflow_diagram.svg`](run_round2/report/workflow_diagram.svg) ·
**15 claim-evidence objects:** [`run_round2/evidence/claims.json`](run_round2/evidence/claims.json)

**3-page visual summary:** [`report_B7H3_round2.pdf`](report_B7H3_round2.pdf) —
workflow comparison (paper's one-shot pipeline vs. our review-revise-reaccept
loop), key result figures against the paper's claims, and an engineering note
on DeepSeek vs. Claude as the agent driver (cost, model-routing audit,
reliability caveats).

### ⚠️ Post-review correction (2026-10-22) — Figure 4E direction was backwards

An external check against the paper's own primary-source text found that the
round-2 documents above (including the 3-page PDF) mischaracterize the
paper's Figure 4E claim as an **"immune-hot"** niche. The paper's actual
caption and body text say **"immune-excluded"** (depletion of neighbouring
T cells, macrophages, monocytes and dendritic cells near high-CD276 spots) —
the opposite direction, consistently wrong across every round-2 deliverable.
A targeted correction pass (reusing existing data, no new data pulls or
pipeline reruns) also added an existing-but-unused round-1 gene-constraint
number to panel 4A, and clarified that panel 4C's fibroblast-specific DE
claim was never actually testable in this reproduction (not refuted).

**This correction has not yet been through this project's own
scientific-reviewer pass** — it is specialist self-reported and
self-verified only. Read
[`run_round2_correction/FINAL_REPORT.md`](run_round2_correction/FINAL_REPORT.md)
(Chinese; a readable PDF is at
[`report_B7H3_round2_correction_zh.pdf`](report_B7H3_round2_correction_zh.pdf))
before trusting the Figure 4E/S5B framing anywhere above — in short: under
the paper's own adjustment model (reused on existing per-spot data), our
reproduction now **agrees** with the paper's immune-excluded claim for all
four named cell types, reversing the round-2 delivery's "disagree, depth
artifact" verdict.

**Headline result: CD276 is a low-confidence, expression-defined target.**
It has no LUAD/SCLC germline genetic support (0/8 credible sets, 0/67 L2G
loci), is **not tumour-restricted** (36.5% detection in normal lung
macrophages, 30.8% in LUAD fibroblasts), is not differentially expressed in
any of 15 disease-vs-normal contrasts, and is not essential in cancer cell
lines (mean CERES −0.230 LUAD, 1/46 lines below the essentiality threshold).
The TCGA LUAD survival association reproduces only unadjusted (OS HR 1.80,
p = 0.0051) and is not independent of stage (adjusted OS p = 0.106). The
paper's reported "immune-hot" spatial niche is largely a capture-depth/edge
artifact; the depth-robust signal is malignant-cell enrichment with
endothelial, NK, and macrophage depletion. **This supports round 1's
low-confidence stance on CD276 but revises away its SCLC-over-LUAD staging
claim** — the only quantitative positives found in round 2 are in LUAD.

**Two engineering stories worth reading even if you don't care about the
biology:**
1. **A real, independently-diagnosed-and-fixed bug.** cell2location's first
   mapping run converged correctly but exported 100% NaN abundances due to
   a pandas column-selection-vs-rename bug; no checkpoint had been saved, so
   the fix required a full retrain. The before/after NaN fraction was
   verified directly (not taken from any agent's self-report) at both ends:
   100% → 0%. See the "cell2location NaN bug" section of the conversation
   log.
2. **A real revise-and-resubmit cycle.** The first full scientific-review
   pass did not rubber-stamp the spatial analysis — it required the report's
   bottom line to surface donor-concordant findings (immune-compartment
   depletion) that had been correctly computed but omitted from the
   narrative in favour of a less robust finding. Four specialists filed
   itemized, evidence-checked revision responses before a re-review
   accepted the work.

## Repository layout

```
README.md                    — this file
BASELINE.md                  — original repo, baseline commit, exact code changes (none) made here
data_provenance.md           — what large raw data was excluded and how to regenerate it
conversation/
  conversation_log.md        — round 1: initial prompt, every clarification, all follow-up instructions
  conversation_log_round2.md — round 2: the five-run-directory saga, quota crisis, NaN bug, review cycle
engineering_validation/      — layered DeepSeek/SDK/MCP validation (A-F, E2) run before the real study
run_round1/                  — round 1's run directory from the original repo's run_vbt.py entry point
  config/run_b7h3_formal.py  — the only code-level intervention: a runtime monkeypatch wrapper (no repo edits)
  MANIFEST.json, README.md, audit.html, environment.yml
  inputs/                    — query.txt, plan.json
  evidence/                  — claims.json (17 filed claims), provenance.json
  report/FINAL_REPORT.md     — the CSO's final synthesized answer
  logs/                      — trace.jsonl, transcript.md, cost_report.json
  work/<specialist>/         — every specialist's code/scripts, data, results/{reports,tables,figures}
run_round2/                  — round 2, consolidated from its two final (of five) run directories
  LINEAGE.md                 — which of the 5 run directories this content came from, and why
  config/                    — resume instructions after each of the 4 interruptions; disk-quota cleanup manifest
  MANIFEST.json, evidence/   — from the synthesis turn (the one with the 15 successfully-recorded claims)
  README_main_turn.md, logs_main_turn/, work/<specialist>/ — from the turn that did the spatial analysis
  README_synthesis_turn.md, logs_synthesis_turn/           — from the turn that wrote the final synthesis
  report/                    — FINAL_REPORT.md, panel_by_paper_comparison.md, workflow_diagram.svg
```

## Credentials

No API keys, tokens, `.env` files, or credential-bearing log lines are
committed. All DeepSeek/Anthropic credentials used during the run were
injected into a single subprocess's environment at runtime and never
written to disk or logged; this was independently verified by scanning
every file in this repo for key-shaped strings before the initial commit.
