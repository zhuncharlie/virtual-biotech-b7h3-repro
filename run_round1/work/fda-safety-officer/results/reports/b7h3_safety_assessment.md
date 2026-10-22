# B7-H3 (CD276) Safety Assessment — LUAD and SCLC

**Target:** CD276 / B7-H3, Ensembl ENSG00000103855, chromosome 15q24.1, surface antigen.
**Scope:** lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC) only.
**Revision:** 3 — 2026-10-20. Targeted corrections to the revision-2 safety stream:
harmonised LoF wording, explicit target-versus-payload attribution, qualified
normal-lung expression, stated evidence gaps, and SCLC staging. The change log is in
§8. The original assessment date was 2026-10-20.

**Overall safety risk (split by attribution level):**

| Level | Rating | Basis |
|---|---|---|
| **Target-level (B7-H3 biology)** | **Low–Moderate** | Moderate LoF tolerance (o/e 0.667); broad low-level normal expression (HPA bulk RNA + prior knowledge); stromal/immune expression and soluble antigen sink; no receptor, no target-linked AE record, benign knockout biology (prior knowledge). None of these are payload or modality toxicities. |
| **Payload/modality-level** | **Moderate (LUAD) / Moderate–High (SCLC)** | DXd ILD/pneumonitis and myelosuppression, duocarmycin ocular and marrow toxicity, CAR-T/engager CRS/ICANS, 131I marrow suppression. Driven by payload and by overlap with standard-of-care toxicity, **not** by B7-H3 biology |

**Recommendation:** Safety does not preclude a B7-H3-directed ADC in either indication,
but the two decisions are different. **LUAD:** no LUAD-stratified efficacy or safety
readout exists; deprioritise on competitive and strategic grounds, not because the
target biology is negative — if pursued, lung-toxicity mitigation is the binding
constraint. **SCLC:** conditional proceed only within a staged clinical decision —
feasibility is established, efficacy is unproven; hold commitment until ARTEMIS-008
(NCT06498479) and the I-DXd Phase 3 read out. Risk tolerance is conditional on a
positive class-level Phase 3 readout; absent that, the payload/modality toxicity
burden is not justified by B7-H3 biology. Payload selection, not target choice,
is the decisive safety lever.

---

## 1. Evidence base and its limits

Sources used were the configured MCP tool sets (`mcp__target__*`, `mcp__drug__*`) plus
cross-stream artifacts from this run, cited explicitly where used. No web search or
scraping was performed.

| Query | Result | Interpretation |
|---|---|---|
| Target info / genetic constraint | Returned (quantitative) | Usable |
| OpenFDA target-level adverse events (CD276) | **0 records** | Gap; uninformative |
| Mouse knockout phenotypes | **0 records** | Gap; uninformative |
| Pharmacogenomics | **0 records** | Gap; uninformative |
| Known drugs targeting CD276 | 9 target–disease rows, **2 unique agents** | Both unapproved |
| Drug warnings, enoblituzumab / 8H9-131I | **0 records each** | Likely unapproved status (no FDA label), not safety |
| Drug warnings, positive control (infliximab, CHEMBL1201581) | **2 black-box warnings** | Tool confirmed functional |

The warnings tool is functional (positive control returned two black-box warnings), so
the zero counts for enoblituzumab and omburtamab **may reflect their unapproved status
(absence of an FDA label), not a clean safety profile**. Conversely, bevacizumab
(CHEMBL1201583) returned zero despite having a boxed warning, so the warnings dataset is
also incomplete for some approved drugs. Neither zero nor the presence of a record
should be over-read.

**Coverage-gap statement (required).** The database contains **no record for ifinatamab
deruxtecan (DS-7300 / I-DXd), vobramitamab duocarmazine (MGC018), or any B7-H3
CAR-T/T-cell engager**. Because no drug record exists, **no agent-specific OpenFDA
warning query was possible**. Zero retrievable records for these agents is an
**evidence gap, not a clean safety profile**, and no safety conclusion about them can be
drawn from their absence. Their discussion below is prior knowledge, labelled as such.

| Agent that matters clinically | Drug record | Warning query possible? | What the zero means |
|---|---|---|---|
| Ifinatamab deruxtecan (I-DXd) | None | No | Evidence gap — not "no ILD" |
| Vobramitamab duocarmazine (MGC018) | None | No | Evidence gap — not "no marrow/ocular toxicity" |
| B7-H3 CAR-T / engagers | None | No | Evidence gap — not "no CRS/ICANS" |
| Enoblituzumab | Yes (unapproved) | Yes, 0 records | Unapproved status, not safety |
| Omburtamab (131I-8H9) | Yes (unapproved) | Yes, 0 records | Unapproved status, not safety |

---

## 2. Target-level versus payload/modality-level risk (core separation)

This separation governs every statement in this report. **Payload and modality
toxicities are not evidence of B7-H3 biology and must not be attributed to it.**

| Risk | Attribution | What drives it | Evidence |
|---|---|---|---|
| Broad low-level normal-tissue expression | **Target-level** | B7-H3 antigen present outside tumour | HPA bulk RNA + prior knowledge; Census transcript low in normal lung |
| Stromal/immune expression, antigen sink | **Target-level** | Fibroblast/macrophage transcript exceeds malignant transcript; shed soluble antigen | Census single-cell; shedding not quantified |
| Moderate LoF tolerance, no receptor, benign KO | **Target-level** | Germline tolerance to partial LoF; no acute antibody-depletion data | gnomAD constraint; mouse phenotype (prior knowledge) |
| ILD / pneumonitis (DXd ADC) | **Payload-level** | DXd payload, class effect | Prior knowledge only |
| Myelosuppression (DXd, duocarmycin, 131I) | **Payload-level** | Cytotoxic payload or ionising radiation | Prior knowledge; no marrow transcript support |
| Ocular surface toxicity (duocarmycin) | **Payload-level** | Duocarmazine class | Prior knowledge only |
| CRS / ICANS (CAR-T, engagers) | **Modality-level** | Immune activation by the construct | Prior knowledge only |
| Marrow suppression (131I radioimmunotherapy) | **Payload-level** | Radiation dose | Prior knowledge only |
| Direct antibody-mediated injury to B7-H3-low normal tissue | **Target-level** | Antigen density + effector potency | Theoretical; protein density not measured |

Consequence for interpretation: **a high observed rate of ILD or cytopenia in a B7-H3
ADC says nothing about B7-H3 biology.** It says something about the payload, the linker,
the dosing schedule and the patient population. The target-level items are broad
low-level normal expression, stromal/immune expression, the soluble antigen sink and
moderate LoF tolerance; the payload/modality items are ILD/pneumonitis,
myelosuppression, ocular toxicity, CRS/ICANS and marrow suppression. Target-level
findings do not mitigate payload toxicity, and payload toxicity is never evidence
against B7-H3 biology.

---

## 3. Target-level safety findings

### 3.1 Genetic constraint (harmonised)

CD276 LoF: **34 observed vs 51.0 expected, o/e 0.667**, described as **moderate LoF
tolerance** — partial depletion of LoF variants rather than strict haploinsufficiency.
Moderate tolerance is not a safety guarantee: it does not address acute
antibody-mediated depletion of B7-H3-positive cells.

The retrieved record carries o/e interval bounds and more than one bin field but does
**not label the interval's confidence level**. To avoid mixing confidence levels or
bins, this revision reports the point estimate only and **quotes no CI and no bin**.
The source did not return a pLI, and none is reported. Missense o/e is 0.866
(634/732.0), near-neutral; synonymous o/e is 0.868 (275/316.7) and is not used for
safety inference.

### 3.2 Mouse phenotype

No database phenotype records (gap). Prior knowledge: constitutive *Cd276* knockout mice
are viable and fertile with no overt spontaneous phenotype; immune-dysregulation
phenotypes have been reported mainly in challenge models. This is weak reassurance:
mouse CD276 is only **52.4%** identical to human at the query region, so human-targeting
antibodies may not engage mouse CD276. Macaque (94.6%) and chimpanzee (98.9%) are the
pharmacologically relevant species. No NHP safety data were retrieved.

### 3.3 Normal-tissue expression — qualified

**Breadth (target-level).** Broad low-level normal expression is supported by HPA bulk
RNA and prior knowledge: 109/120 sampled normal tissues/immune populations were
detected, median 834 TPM, and 49/120 at RNA level 4–5. This is bulk tissue RNA, not
surface protein density, and it is the main target-level off-tumour consideration.
It does not establish high protein expression on normal lung or any other normal tissue.

**Normal lung specifically — do not imply high protein expression.** Three data layers
disagree in magnitude:

| Layer | Normal lung value | Reading |
|---|---|---|
| HPA bulk RNA | 1,682.5 TPM, RNA level 4 | Moderate bulk RNA; partly attributable to resident macrophages |
| HPA protein | Level 2 (reliable) | Moderate, ordinal IHC level — not high, not molecules/cell |
| Census single-cell transcript | Organ weighted mean 13.9 CPM (12,315 cells, 4 donors); epithelial 17.1 CPM; macrophage 39.6 CPM; all medians 0 | Comparatively low; 13.9 CPM is at the median of 19 sampled organs and well below skin (46.0) and kidney (42.6) |

The correct summary is **"moderate RNA, level-2 (ordinal) protein, comparatively low
cell-level transcript"** in normal lung — not "high normal-lung protein expression."
HPA protein level 2 does not indicate high protein. The bulk lung RNA signal is
plausibly inflated by macrophages, the highest HPA expressers (9,456–14,497 TPM);
however, HPA protein for macrophages is flagged unreliable, so the myeloid sink
argument is **RNA-only**.

**Tumour selectivity is unproven.** The prior-knowledge assertion that B7-H3 is
overexpressed in LUAD/SCLC relative to normal tissue is downgraded to a **literature
assertion not verified in this run**, and it is partly contradicted by the transcript
data. In LUAD, fibroblast 75.9 CPM and alveolar macrophage 34.1 CPM exceed malignant
cells at 23.6 CPM, and non-malignant epithelial cells are 28.6 CPM. In SCLC, fibroblast
68.1 CPM and macrophage 48.8 CPM exceed the epithelial population at 28.5 CPM (no
malignant label is available for SCLC). Paired tumour-region versus normal-region
epithelium was ≥2x in only 2/3 donors (3.26x, 3.40x, 1.09x; n=3, underpowered). The
stromal signal is an **antigen-sink and bystander-exposure** consideration, not evidence
of malignant-cell surface density. A protein-level tumour-to-normal and tumour-to-stroma
density study is the decisive gate.

---

## 4. Agent-specific findings and evidence gaps

| Agent | Modality | Database record | Warnings record | Indications in DB | Lung-cancer record |
|---|---|---|---|---|---|
| Enoblituzumab (MGA-271) | Fc-optimized anti-B7-H3 mAb | Yes, CHEMBL3545373 | 0 (no FDA label) | HNSCC ph2 withdrawn; prostate ph2; melanoma ph1 terminated | None |
| Omburtamab / 131I-8H9 | Radioimmunotherapy | Yes, CHEMBL2109310 | 0 (no FDA label) | Neuroblastoma ph2 terminated; leptomeningeal metastasis ph2 terminated; peritoneal ph1; DIPG ph1 withdrawn | None |
| Ifinatamab deruxtecan (DS-7300) | DXd ADC | **No record** | **No query possible** | — | Prior knowledge: SCLC programme |
| Vobramitamab duocarmazine (MGC018) | Duocarmycin ADC | **No record** | **No query possible** | — | Prior knowledge: prostate/solid tumours |
| B7-H3 CAR-T / engagers | Cell therapy / bispecific | **No record** | **No query possible** | — | Prior knowledge |

Both database-recorded agents are **unapproved**. Enoblituzumab is recorded in prostate
cancer (recruiting/active) and previously HNSCC (withdrawn) and melanoma (terminated).
**No agent-specific adverse-event frequencies could be retrieved for any B7-H3 agent in
this run.** No conclusion can be drawn from the absence of records. Zero warnings for
enoblituzumab and omburtamab may reflect their unapproved status; zero records for
I-DXd and MGC018 mean no agent-specific query was possible. Both are evidence gaps,
not clean profiles. All toxicities discussed for these agents are payload- or
modality-level and are not attributed to B7-H3 biology.

---

## 5. Payload- and modality-level toxicities (prior knowledge)

These are class effects. They are **payload- or modality-level**, are **not** B7-H3
biology, and should not be presented as target-derived risk.

- **DXd ADC** (ifinatamab deruxtecan class): interstitial lung disease/pneumonitis is the
  principal dose-limiting and potentially fatal risk; myelosuppression, nausea, fatigue,
  alopecia and stomatitis are common. No retrieved record supports these statements.
- **Duocarmycin ADC** (vobramitamab class): myelosuppression (neutropenia), fatigue, rash
  and infusion reactions; ocular surface toxicity (conjunctivitis, keratitis, dry eye) is
  a recognised duocarmazine-class effect.
- **CAR-T / T-cell engagers**: CRS (grade 1–4) and ICANS/neurotoxicity. These are
  modality-level immune-activation risks; the only target-level component is on-target
  injury to B7-H3-expressing normal tissue, whose antigen density is unmeasured.
- **Radioimmunotherapy (131I-8H9)**: myelosuppression and, with
  intraventricular/intrathecal delivery, chemical meningitis, raised intracranial
  pressure and leukoencephalopathy; late hypothyroidism and secondary malignancy.
  Compartmental delivery limits systemic applicability to lung cancer.

**Marrow-specific correction.** Myelosuppression should be attributed to the payload, not
to B7-H3 on marrow progenitors. Census bone marrow shows CD276 at 0.21 CPM with 0.12% of
cells expressing (marrow stromal max 22.4 CPM). There is no transcript support for an
on-target marrow mechanism.

**Where target and payload meet.** Normal-tissue and stromal/soluble antigen can act as
an antigen sink, reducing tumour exposure and increasing normal-tissue exposure. This is
a **target-level pharmacokinetic consideration**; the mechanism of resulting injury is
still the payload. For ADCs, most observed toxicity is payload-driven, with target
expression modulating where the payload is delivered.

---

## 6. Risk–benefit read for LUAD and SCLC

**LUAD — safety permits, strategy does not prioritise.** LUAD is a chronic,
increasingly IO/targeted-therapy-managed disease. Safety does not preclude a B7-H3 ADC
after platinum/IO failure, but **no LUAD-stratified efficacy or safety readout exists**
(LUAD patients appear only within nonsquamous-NSCLC and pan-tumour trials). The binding
safety constraint is **lung toxicity (payload-level ILD/pneumonitis, not B7-H3
biology)**: baseline emphysema, prior thoracic radiation and prior immune-checkpoint
pneumonitis all narrow the ILD margin. Required mitigations:
baseline and serial chest imaging, explicit pneumonitis history capture, steroid
algorithms, exclusion of active interstitial lung disease, and CBC monitoring.
Acceptable risk profile: **moderate, conditional**. The *decision* to deprioritise LUAD
is competitive/strategic, not a safety verdict; the biological gate (protein-level
tumour-to-normal density) is untested.

**SCLC — staged clinical decision; feasibility established, efficacy unproven.** SCLC
has high unmet need and a higher tolerated toxicity ceiling, but that does not by
itself justify the payload/modality risk. **Risk tolerance is conditional on a positive
class-level Phase 3 readout:** grade 3 myelosuppression and ILD are acceptable only if
a class-level Phase 3 trial demonstrates a survival benefit. Feasibility is
real: six Phase 3 B7-H3 ADC trials representing four distinct molecules
(I-DXd; HS-20093/GSK5764227 in three trials; MHB088C; YL201), plus CAR-T and radioligand
programmes in Phase 1/2. Efficacy is **not** established: the only posted SCLC-specific
result is MGC018 0/9 in a small single-arm trial, ARTEMIS-008 (NCT06498479, HS-20093 vs
topotecan) is completed with no results posted, and no SCLC Phase 3 readout is available.
Toxicity also overlaps heavily with platinum/etoposide and thoracic radiotherapy
(cytopenias) and with prior IO (pneumonitis); neurological toxicity is hard to attribute
given high baseline CNS-metastasis prevalence. None of these toxicities is B7-H3
biology; they are payload- or modality-level. Radioimmunotherapy is not a systemic
option for SCLC. Recommendation: **conditional proceed to a gated preclinical package
only; stage the decision on ARTEMIS-008 and the I-DXd Phase 3; do not commit to a
me-too DXd ADC.**

**Bottom line.** No target-level signal in the database argues against B7-H3, but the
absence of target-linked AE, mouse-phenotype and PGx records is an **evidence gap, not
reassurance**. The dominant risks are payload- and modality-driven — especially pulmonary
and haematological toxicity — and must not be attributed to B7-H3 biology. Payload
selection and lung-toxicity mitigation are the decisive design choices.

---

## 7. Evidence strength

| Claim | Strength | Basis |
|---|---|---|
| CD276 LoF o/e 0.667, moderate LoF tolerance | Strong | Direct database value; point estimate only; no CI/bin quoted |
| No mouse knockout phenotype / no target AE / no PGx record | Strong (as a gap) | Direct zero-count query results |
| Only 2 B7-H3 agents in database, both unapproved; no I-DXd/MGC018 record | Strong | Target-restricted query, count = 9 rows |
| Broad low-level normal-tissue expression | Moderate | HPA bulk RNA + prior knowledge; not protein density |
| Normal lung: moderate RNA, level-2 protein, low cell-level transcript | Moderate | HPA bulk RNA/protein and Census single-cell concordant on "not high" |
| Stromal > malignant transcript in LUAD and SCLC | Moderate | Direct single-cell values; medians 0, transcript not protein |
| Tumour overexpression relative to normal | Weak / unproven | Literature assertion, partly contradicted by transcript |
| ADC/CAR-T/radioimmunotherapy class toxicities | Moderate | Prior knowledge; no retrieved label/ADR record |
| LUAD vs SCLC risk–benefit framing | Moderate | Inference combining database constraints, indication biology and the staged clinical readout |

---

## 8. Change log

### Revision 3 — 2026-10-20 (this revision)

1. **LoF statement harmonised to one phrasing.** The report and signals table now say
   only "o/e 0.667, moderate LoF tolerance". The retrieved record does not label its
   interval's confidence level and carries more than one bin field, so **no CI and no
   bin are quoted anywhere**; the earlier conflicting CI/bin wording is withdrawn.
2. **Attribution separation made explicit throughout.** Broad low-level expression,
   stromal/immune expression and soluble antigen are tagged target-level;
   ILD/pneumonitis, myelosuppression, ocular toxicity, CRS/ICANS and marrow suppression
   are tagged payload/modality-level and marked "NOT B7-H3 biology". The modality table
   identifies on-target off-tumour injury as the only target-level item in its set.
3. **Normal-lung expression qualified.** Broad low-level expression is attributed to
   HPA **bulk RNA** plus prior knowledge, not protein density. Normal lung is stated as
   moderate bulk RNA (1,682.5 TPM, level 4), HPA protein **level 2** (ordinal, not high)
   and comparatively low Census cell-level transcript (13.9 CPM). No high normal-lung
   protein expression is implied.
4. **Evidence gaps restated.** Zero OpenFDA records for I-DXd and MGC018 is an evidence
   gap, not a clean profile; zero warnings for enoblituzumab and omburtamab **may**
   reflect unapproved status, not safety.
5. **SCLC conclusion tied to staging.** Feasibility is established (six Phase 3 trials /
   four molecules); efficacy is unproven (MGC018 0/9; ARTEMIS-008 completed without
   results; I-DXd Phase 3 unposted). Risk tolerance is explicitly conditional on a
   positive class-level Phase 3 readout.

### Revision 2 — 2026-10-20 (superseded in part by revision 3)

1. Withdrew the conflicting CI/bin statements from the report and signals table.
2. Added the §2 attribution table and `risk_level` columns; removed the on-target marrow
   mechanism claim from the DXd myelosuppression row.
3. Qualified normal-lung expression and removed the "among the highest normal
   expressers" claim.
4. Labelled zero-record agents as evidence gaps.
5. Tied the SCLC recommendation to the staged clinical decision.

---

## Artifacts

- `results/tables/b7h3_safety_signals.csv` — 22 signals, each tagged target-level,
  payload/modality-level or evidence-gap.
- `results/tables/b7h3_agent_registry_lung_cancer.csv` — 5 agents; unapproved/absent
  records labelled as gaps.
- `results/tables/b7h3_modality_class_toxicities.csv` — 11 class toxicities with
  `risk_level` and explicit "NOT B7-H3 biology" drivers.
- `data/processed/b7h3_expression_evidence_for_safety.csv` — HPA and Census values used
  for the qualified normal-lung/tumour-stroma statements, with source artifact pointers.
- `data/raw/cd276_target_info_and_constraint.json` — raw target/constraint query.
- `data/raw/b7h3_known_drugs_raw.json` — raw known-drug query.
- `code/scripts/build_b7h3_safety_tables.py` — original table build (revision 1).
- `code/scripts/revise_b7h3_safety_tables_for_review.py` — revision 2 generator.
- `code/scripts/apply_b7h3_safety_revision3_corrections.py` — revision 3 correction
  patch (reads the existing tables, applies the wording/attribution fixes, re-saves).
