# CD276 (B7-H3) — pathway and protein-interaction safety assessment

**Indication scope: LUAD and SCLC only.** Pathway and interaction annotations are
gene-level and not disease-specific; every clinical interpretation below is
written for LUAD/SCLC. Where the data cannot support an indication-specific
statement, that is stated rather than inferred.

- Target: CD276 / B7-H3, `ENSG00000103855`, UniProt `Q5ZPR3`, 15q (plus strand).
- Sources: Reactome + GO via pathway MCP; STRING v12 + IntAct via interaction MCP;
  Open Targets via target MCP. Query date 2026-10-20.
- Raw tool responses transcribed to `data/raw/cd276_mcp_query_results.json`.
- No expression, IHC, or clinical data were queried in this stream.

---

## 1. Pathway membership: none retrieved

FINDING: CD276 has no Reactome pathway annotation in the configured pathway MCP.
EVIDENCE: `results/tables/cd276_pathways_interactions.csv` (row type
`Reactome_pathway`, `evidence_count = 0`); `search_pathways("CD276")` also
returned 0; the Open Targets `pathways` field is `null`.
CONFIDENCE: strong that the annotation is absent from these sources; it is a
data gap, not evidence that CD276 participates in no pathway.

The pathway-MCP GO endpoint returned `count = 0` for all three aspects
(`GOEndpoint_status` rows in the same table). The 18 GO annotations below were
therefore taken from `mcp__target__get_target_info`, which is the authoritative
GO source in this session. The endpoint failure is recorded as a limitation.

**Consequence for safety:** there is no pathway-membership signature to use for
on-target toxicity (no essential-cascade overlap, no cell-cycle or cardiac
pathway membership to flag). Pathway-based risk must be inferred from the GO
functional profile and the interaction neighbourhood instead.

---

## 2. GO functional profile (18 annotation rows, 12 unique terms)

| Aspect | GO ID | Term | Evidence (count) | Reference |
|---|---|---|---|---|
| F | GO:0005102 | signaling receptor binding | IBA, NAS | GO_REF:0000033; PMID:11224528 |
| F | GO:0005515 | protein binding | IPI | PMID:18650384 |
| C | GO:0009897 | external side of plasma membrane | IBA, NAS | GO_REF:0000033; PMID:15188059 |
| C | GO:0016020 | membrane | NAS, IEA ×2 | PMID:15188059; GO_REF:0000043/44 |
| P | GO:0042110 | T cell activation | IDA, IEA | PMID:18650384; GO_REF:0000117 |
| P | GO:0032729 | positive regulation of type II interferon production | IDA | PMID:11224528 |
| P | GO:0042102 | positive regulation of T cell proliferation | IDA, IEA | PMID:11224528; GO_REF:0000117 |
| P | GO:0032649 | regulation of type II interferon production | IEA | GO_REF:0000117 |
| P | GO:0001819 | positive regulation of cytokine production | IEA | GO_REF:0000117 |
| P | GO:0001817 | regulation of cytokine production | IBA | GO_REF:0000033 |
| P | GO:0050852 | T cell receptor signaling pathway | IBA | GO_REF:0000033 |
| P | GO:0050776 | regulation of immune response | NAS | PMID:11224528 |

Evidence composition: 3 IDA, 1 IPI, 4 NAS, 4 IBA, 6 IEA. The strongest rows
(IDA/IPI) come from two papers (`PMID:11224528`, `PMID:18650384`); the six IEA
rows are automatic electronic annotations and carry no experimental weight.

Annotation shape: a cell-surface molecule (external side of plasma membrane;
`targetClass = Surface antigen`) annotated as *signaling receptor binding* — i.e.
ligand-like — with T-cell/cytokine functional terms. The MF term is consistent
with CD276 acting on a receptor, but no receptor is identified in the data
(Section 4).

---

## 3. Interaction network: association-level, not physical

Retrieved: 26 STRING rows (limit 25 plus the CD8A row from the evidence
endpoint), 30 IntAct rows (29 distinct partners; one partner appears as two
isoform records), and 15 STRING evidence records. The endpoints apply
hard limits and the returned windows are not score-ordered, so this is a
sample of the network, not its full membership.

**Highest-scoring partners (STRING combined score, 0–1):**

| Partner | Ensembl | Score | Observations |
|---|---|---|---|
| CD8A | ENSG00000153563 | 0.873 | 1 |
| IFNG | ENSG00000111537 | 0.780 | 1 |
| IL1B | ENSG00000125538 | 0.597 | 1 |
| THBS1 | ENSG00000137801 | 0.497 | 3 |
| DNMT3A | ENSG00000119772 | 0.483 | 2 |
| IFNAR1 | ENSG00000142166 | 0.446 | 2 |
| TP53 | ENSG00000141510 | 0.395 | 2 |

**IntAct (MI score):** LGALS1 0.53 (3 observations) is the highest; LGALS3,
CLEC5A, RYK, CD68, CD81, MAPT and 17 unresolved Ensembl IDs sit at 0.35, almost
all single-observation records. CFTR, KCNK3, HRAS, KRAS and NRAS are at 0.27.
0.35 is the modal floor of this network.

FINDING: the network contains no high-confidence physical interaction. The single
edge above the 0.7 threshold (CD8A, 0.873) is textmining-only (`MI:0110`) with
`pubmedId = null`. Across the 15 retrieved evidence records the methods are
textmining (8) and coexpression (7); every `pubmedId` is null.
EVIDENCE: `results/tables/cd276_pathways_interactions.csv` rows
`PPI_STRING` / `PPI_IntAct` / `PPI_evidence`;
`results/figures/cd276_partner_confidence.png`.
CONFIDENCE: strong for the characterisation of the retrieved records; moderate
for the network as a whole because of the endpoint caps and 35 unresolved symbols.

Interpretation: STRING "interactions" here largely reflect co-mention and
co-expression, not binding. The IntAct records are single-observation, low-score
entries. This network should not be used to infer a signalling axis.

---

## 4. Is a canonical B7-H3 receptor established? NO

FINDING: **No canonical B7-H3 receptor is established in the retrieved data.**
None of CD28, CTLA4, PDCD1, TREML2, IL20RA or IL20RB appears among the 20
resolved interaction-partner symbols. No record is receptor–ligand grade: there
is no experimental, PMID-supported, high-score partner of any kind.
EVIDENCE: `data/raw/cd276_mcp_query_results.json` →
`canonical_receptor_check`; `results/tables/cd276_pathways_interactions.csv`.
CONFIDENCE: moderate — a non-appearance finding. 35 distinct Ensembl IDs in the
retrieved windows could not be resolved to symbols in this session, so absence
from the resolved set is not proof of absence from the full network.

This gap is reported as a biological gap and is **not** filled from memory.
PRIOR KNOWLEDGE, NOT TOOL-DERIVED AND NOT CITABLE FROM THIS STREAM: B7-H3 is
commonly described in the literature as an orphan receptor with no consensus
binding partner. That statement is background only; it is not evidence produced
by this analysis.

Why it matters: without a named receptor, no receptor-level agonism or
antagonism can be designed or interpreted. Curated "signaling receptor binding"
(GO:0005102) says CD276 behaves like a ligand, but the counter-structure is
missing from every database queried.

---

## 5. Immune-checkpoint context

**Co-inhibitory vs co-stimulatory — not resolved by the data.**
The GO profile is weighted toward *positive* immune regulation: positive
regulation of type II interferon production (IDA), positive regulation of T-cell
proliferation (IDA), T-cell activation (IDA), TCR signalling (IBA). Against this,
the UniProt function text returned by the target tool says CD276 "may play a
protective role in tumor cells by inhibiting natural-killer mediated cell lysis"
and may regulate "lymphocytic activity at mucosal surfaces". The two readings are
not reconciled by any annotation in this stream. The strongest positive-costimulation
evidence rests on a single publication (`PMID:11224528`), largely in vitro.

FINDING: the retrieved annotations support "immune-modulatory surface molecule
with context-dependent effects"; they do **not** establish CD276 as either a
co-inhibitory or a co-stimulatory checkpoint in LUAD or SCLC.
EVIDENCE: `results/tables/cd276_pathways_interactions.csv` (GO_annotation rows);
UniProt function text transcribed in `data/raw/cd276_mcp_query_results.json`.
CONFIDENCE: moderate for the GO profile; weak for any checkpoint classification.

**Expression on APCs vs tumour cells — NOT ASSESSED.**
This stream queried no expression dataset. GO cellular-component terms and the
"protective role in tumor cells" sentence in the UniProt function description do
not establish which cell types express CD276 in LUAD or SCLC. Co-inhibitory
checkpoints are conventionally discussed in terms of APC versus tumour
expression, but that comparison cannot be made from these data. Defer to the
single-cell/expression stream. (The UniProt tumour-cell sentence concerns
neuroblastoma — a different indication — and is not transferred here.)

**Implication for modality choice (interpretation, not a tool output):**
- Antibody-based modality is what the annotation supports: `AB Advanced Clinical
  = true`, `AB UniProt SigP or TMHMM = true`, and every small-molecule
  tractability flag is false.
- Because no receptor is named, a strategy that requires agonising or
  antagonising a CD276 receptor cannot be rationally specified from these data.
  A payload-delivery / cell-depletion strategy (ADC, T-cell engager, radioligand)
  acts on the B7-H3-bearing cell rather than on a signalling axis, and is the
  modality the tractability and interaction data are consistent with.
- If the programme's thesis is checkpoint blockade, this stream supplies no
  mechanistic support for it — that is a material gap for the CSO, not a negative
  result.

---

## 6. Pathway- and network-based on-target safety (LUAD/SCLC)

**Germline loss-of-function tolerance: favourable.**
LoF: observed 34 vs expected 51, oe 0.667 (95% CI 0.506–0.888), p = 4.29e-8,
upperRank 7792, upperBin 4, upperBin6 2. Synonymous oe 0.868 and missense oe
0.866. Open Targets returns no `safetyLiabilities` annotation.
EVIDENCE: `results/tables/cd276_constraint_tractability.csv`.
CONFIDENCE: moderate. This is germline constraint, i.e. tolerance of inherited
LoF; it does not measure acute antibody-mediated depletion of B7-H3+ cells and
says nothing about payload bystander toxicity or Fc-effector effects.

**Shared-process exposures from the interaction neighbourhood** (all
associations low confidence — these are hypotheses to test, not findings):

1. **T-cell / IFN-γ axis** (CD8A, IFNG, IFNAR1, IL1B). If the construct has Fc
   effector function or engages T cells, immune-related adverse events
   (cytokine release, IFN-driven inflammation) are mechanistically plausible.
   Given that LUAD/SCLC patients may receive checkpoint inhibitors, overlapping
   immune toxicity would be harder to attribute.
2. **NK-cell surveillance.** The UniProt function text assigns CD276 a
   tumour-protective role via inhibition of NK-mediated lysis. Engaging or
   depleting CD276-bearing cells could therefore perturb NK activity. This is
   the one mechanism in the dataset that argues for an immune-mediated
   on-target effect rather than a pure delivery effect.
3. **Mucosal / epithelial surfaces.** UniProt describes regulation of
   lymphocytic activity at mucosal surfaces. For a payload-bearing construct in
   lung cancer this raises mucosal and pulmonary toxicity as the compartment to
   monitor; bystander payload release in lung tissue is a plausible amplifier
   (mechanistic inference, not a database output).
4. **Galectin / macrophage and tetraspanin associations** (LGALS1 0.53, LGALS3,
   CD68, CD81). Low-confidence; they suggest phagocyte/lysosomal handling and
   membrane-microdomain biology. Not sufficient to support a specific toxicity
   claim.
5. **Paralogue cross-reactivity.** The nearest human paralogues are
   butyrophilin/B7-family members with low identity: BTN1A1 16.5%, BTNL9 16.1%,
   ICOSLG 15.0%, BTN2A2 12.7%, HHLA2 12.9%, VTCN1 12.0%, BTNL2 11.8%; Open
   Targets flags none as high-confidence paralogues.
   EVIDENCE: `results/tables/cd276_human_paralogues.csv`.
   Low identity argues against broad cross-reactivity in principle, but this is
   not a substitute for epitope-level specificity testing.

**Overall pathway/network assessment: Low-to-moderate risk**, with residual risk
concentrated in payload and immune-effector strategy choices rather than in
pathway perturbation. The largest analytical limitation is not a safety signal
but the absence of any defined pathway or receptor.

---

## 7. Evidence strength summary

| Claim | Strength | Basis |
|---|---|---|
| No Reactome pathway annotation | strong (for these sources) | 3 independent queries, all zero; Open Targets field null |
| Cell-surface, antibody-tractable | strong | target class + subcellular localisation + tractability flags |
| Surface molecule with T-cell/cytokine GO terms | moderate | 18 rows, but 6 are IEA; core rests on 2 PMIDs |
| No high-confidence physical partner | moderate | capped endpoints; 35 unresolved IDs; IntAct lacks method fields |
| No canonical receptor established | moderate | non-appearance only |
| Co-inhibitory vs co-stimulatory unresolved | moderate | conflicting positive-regulation GO vs NK-inhibition text |
| LoF-tolerant in humans | moderate | gnomAD constraint, germline not acute |
| Expression on APC vs tumour | not established | no expression data queried |

---

## 8. What could not be established

- **Reactome pathway membership for CD276** — no annotation exists in the
  pathway MCP. No pathway enrichment for CD276 is possible.
- **GO via the pathway MCP** — `get_gene_ontology` returned 0 for aspects P, F
  and C, while Open Targets returned 18 annotations for the same gene. The
  pathway-MCP GO endpoint appears not to index this gene; GO results here come
  from Open Targets.
- **A canonical receptor** — unresolved (Section 4).
- **Cell-type and tissue expression in LUAD/SCLC** — not queried in this stream.
- **Full interaction network** — endpoints are capped (STRING 25, IntAct 30) and
  are not score-ordered; 35 distinct Ensembl IDs remain unresolved to symbols;
  IntAct records carry no detection-method field in this endpoint.
- **A checkpoint classification** — the data conflict and do not decide it.

**Prior knowledge used, explicitly labelled and not citable as evidence from this
stream:** (i) B7-H3 is described in the literature as an orphan receptor;
(ii) ADC bystander effects can broaden toxicity into surrounding tissue;
(iii) NK cells contribute to anti-tumour immunity in lung cancer. None of these
was produced by the MCP queries above.

---

## 9. Artifacts

| File | Contents |
|---|---|
| `data/raw/cd276_mcp_query_results.json` | Transcribed MCP responses: target annotations, 18 GO rows, 26 STRING + 30 IntAct interactions, 15 evidence records, 15 human paralogues, verified symbol map |
| `results/tables/cd276_pathways_interactions.csv` | 93-row combined pathway/GO/PPI evidence table with source, score, detection method and MI identifier |
| `results/tables/cd276_constraint_tractability.csv` | LoF/syn/mis constraint, true tractability flags, localisation, null-field record |
| `results/tables/cd276_human_paralogues.csv` | 15 human paralogues with pairwise identity |
| `results/figures/cd276_partner_confidence.png` | Partner confidence by source against the 0.7 threshold |
| `code/scripts/build_cd276_pathways_interactions_table.py` | Builds the three tables from the raw JSON |
| `code/scripts/plot_cd276_partner_confidence.py` | Builds the figure |
