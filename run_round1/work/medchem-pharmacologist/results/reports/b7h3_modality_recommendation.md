# B7-H3 (CD276) Therapeutic Modality Recommendation — LUAD and SCLC

**Target:** CD276 / B7-H3, Ensembl ENSG00000103855  
**Scope:** lung adenocarcinoma (LUAD) and small cell lung cancer (SCLC) only.  
**As of:** 2026-10-20  
**Role:** Medicinal Chemistry & Pharmacology, Modality Selection Division.

**Revision:** 2026-10-20, post scientific review. The ranking scores are unchanged
except LUAD ADC clinical precedence (2 -> 1/5). Decision and interpretation
fields are revised: SCLC is now a **staged** GO, LUAD is **deprioritized on
competitive/precedence grounds** rather than a scientific no-go, the
stromal-vs-malignant finding is applied symmetrically, normal-lung expression is
qualified by assay scale, and target-level risk is separated from payload-level
risk.

---

## Bottom line

| Indication | Recommendation | Lead modality | Why |
|---|---|---|---|
| **SCLC** | **GO — STAGED**: conditional on (a) a class-level Phase 3 efficacy readout and (b) a differentiated molecule/profile | **B7-H3 ADC** (topoisomerase-I payload default) | Feasibility is established (26 SCLC-contributing trials; 6 Phase 3 trials across only 4 molecules) but efficacy is not. The only posted SCLC-specific result is MGC018 ORR 0/9 (n=9); ARTEMIS-008 is completed with no posted results. |
| **LUAD** | **DEPRIORITIZED** on competitive/precedence grounds — not a scientific no-go | **B7-H3 ADC** (highest-ranked, but no LUAD-specific precedence) | No LUAD-specific trial (clinical precedence 1/5), intense TROP2/HER3 ADC and IO competition. LUAD patients are, however, eligible in nonsquamous-NSCLC Phase 2/3 trials (NCT07464327, NCT06780085, NCT07824882); this is not an absence of LUAD evidence and the biology is not disqualifying. |

**Do not** lead with a B7-H3 bispecific/T-cell engager, CAR-T or radioligand in either indication. Those are backup/research options, not the primary programme.

**Most important caveat:** the clinical landscape establishes feasibility, not efficacy. The only posted SCLC-specific B7-H3 result is MGC018 ORR 0/9 (n=9), a small under-enrolled trial; the completed Phase 3 ARTEMIS-008 has no posted results. No LUAD-specific B7-H3 efficacy result is posted as of 2026-10-20.

---

## 1. Evidence base and what it can support

### 1.1 Inputs used

- `work/clinical-trialist/results/reports/b7h3_clinical_landscape.md`
- `work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv`
- `work/target-biologist/results/reports/cd276_modality_biology.md`
- `work/target-biologist/results/tables/cd276_target_biology.csv`
- `work/target-biologist/results/tables/cd276_tractability_by_modality.csv`
- `work/target-biologist/results/tables/cd276_known_clinical_drugs.csv`
- `work/fda-safety-officer/results/reports/b7h3_safety_assessment.md`
- `work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv`

### 1.2 MCP precedent queries run for this deliverable

The full query log is `data/processed/b7h3_mcp_query_log.csv`. Key results:

| Query | Result | Interpretation |
|---|---|---|
| `search_known_drugs(CD276, min_phase=0)` | 9 target-disease rows; 2 unique agents (enoblituzumab, 8H9 131I); max phase 2; 0 approved; 0 lung indications | The drug MCP contains no B7-H3 ADC, TCE, CAR-T or radioligand record. This is a coverage gap, not evidence of absence. |
| `get_chemical_probes(CD276)` | 0 probes; 0 high-quality | No chemical-probe route. |
| `get_target_tractability(CD276)` | Small molecule all false; antibody advanced clinical true and SigP/TMHMM true; PROTAC binder false | Surface antigen with antibody tractability; no small-molecule or degrader support. |
| `get_target_info(CD276)` | Surface antigen; Membrane + Vesicles; LoF o/e 0.667; 40 low-confidence interactions; no Reactome pathway | Type I surface antigen; no signalling-dependency rationale. |
| `get_drug_indications(enoblituzumab)` | Prostate, melanoma, HNSCC; no lung | Naked antibody, no lung precedent. |
| `get_drug_indications(8H9 131I)` | Leptomeningeal, neuroblastoma, DIPG, peritoneal; no lung | Compartmental RIT, not systemic lung precedent. |
| `search_known_drugs(DLL3, SCLC)` | 6 records, all rovalpituzumab tesirine (ADC); max phase 3 | DLL3 ADC is a competing SCLC target. |
| `search_known_drugs(TACSTD2/TROP2, SCLC)` | 1 record: sacituzumab govitecan, Phase 1, suspended | TROP2 ADC is a competing SCLC target. |
| `search_known_drugs(TACSTD2/TROP2, LUAD)` | 0 records | Coverage gap; not evidence that no TROP2 LUAD programme exists. |
| `search_known_drugs(SEZ6, SCLC)` | 0 records | Coverage gap; ABBV-706 is prior knowledge, not MCP evidence. |

The disease-level Phase 3 queries reached the 50-record limit and were not fully parsed; they were used only for orientation, not for a specific claim.

### 1.3 What the evidence cannot support

- **No efficacy claim.** No LUAD-specific B7-H3 trial exists, but LUAD patients are eligible within nonsquamous-NSCLC trials, so "no LUAD-specific trial" must not be written as "no LUAD evidence." The only posted SCLC-specific result is 0/9. Phase 3 trials are ongoing or completed without posted results. "Trial exists" is not "efficacy demonstrated."
- **No quantitative surface antigen density.** The databases give bulk RNA (TPM), single-cell transcript (CPM) and ordinal IHC levels, not molecules per cell.
- **No internalization, recycling or shedding rate.** These are required for ADC payload selection and are explicitly not retrievable.
- **No systemic lung-cancer radioligand or CAR-T efficacy.**
- **No class-level safety conclusion.** Registry-posted safety is limited to MGC018 (atrial fibrillation 3/9; infectious/respiratory serious events in 1/9 each) and NSCLC-context trials.

---

## 2. Biology-to-modality logic

### 2.1 Why payload delivery, not signalling inhibition

CD276 is a **type I surface antigen** with an extracellular Ig-domain ectodomain, a transmembrane helix and a short cytoplasmic tail. Open Targets antibody tractability is positive (advanced clinical = true; SigP/TMHMM = true); small-molecule and PROTAC tractability are negative (no binder, no ubiquitination-site evidence, no probes).

There is **no intrinsic CRISPR dependency** in LUAD or SCLC (mean gene effect approximately -0.20 to -0.23; 0-2% essential). A naked antibody or a signalling antagonist therefore has no strong monotherapy rationale. The defensible mechanism is **payload delivery or cell depletion**: ADC, TCE, CAR-T or radiation.

### 2.2 The central safety problem: broad normal expression

CD276 is not tumour-restricted. In the normal-tissue expression data, 109/120 samples are detected; 80/120 are at HPA level >= 3. The highest normal expressers are alternatively activated macrophages (14,497 TPM) and inflammatory macrophages (11,950 TPM). This creates:

- an on-target/off-tumour risk for every cytotoxic modality;
- a large antigen sink for antibodies/ADCs (soluble B7-H3 and myeloid cells);
- a potential lung-toxicity risk in LUAD and SCLC.

**Normal lung must be described with its assay-scale qualification.** Bulk lung RNA is HPA level 4 (1,682.5 TPM), but HPA **protein is level 2**, and the CELLxGENE Census normal-lung **cell-level transcript is comparatively low** (13.9 CPM cell-weighted mean across 12,315 cells from 4 donors). The high bulk RNA signal is not reproduced at cell resolution and is largely driven by lung macrophages (39.6 CPM) rather than epithelium (17.1 CPM). "Normal lung is a high expresser" is therefore **not** supported at protein or cell-resolved transcript level; the defensible statement is that CD276 is present in lung at moderate protein level and that the tumour-to-normal protein-density window is unmeasured. See `results/tables/cd276_normal_lung_expression_qualification.csv`.

Bronchus shows reliable HPA protein level 2 despite zero RNA; this RNA/protein discordance should be treated as a potential on-target airway signal, not dismissed (and not over-interpreted from ordinal IHC alone).

The genetic constraint is moderate, not extreme (LoF o/e 0.667, LOEUF bin 4). The database has no mouse phenotype record; prior knowledge is that constitutive Cd276 knockout mice are viable and fertile, but this is weak translational support because mouse CD276 is only ~52% identical to human CD276. That is not a clean safety package.

### 2.3 Single-cell transcript: malignant cells are not the dominant source

The single-cell data are transcript (CPM), not surface protein. They show that CD276 is sparse (median CPM 0 in the key cell types) and that stromal/myeloid cells are higher than malignant/epithelial cells.

**LUAD** (malignant cell reference: 23.58 CPM; 15.4% expressing):

| Comparator | Mean CPM | Malignant-to-comparator ratio |
|---|---:|---:|
| Fibroblast | 75.91 | 0.31 |
| Alveolar macrophage | 34.09 | 0.69 |
| Macrophage | 32.86 | 0.72 |
| Epithelial cell | 28.61 | 0.82 |
| Pulmonary alveolar type 2 cell | 14.52 | 1.62 |
| Endothelial cell | 22.78 | 1.04 |
| T cell | 1.54 | 15.28 |

**SCLC** (epithelial cell reference: 28.54 CPM; 19.5% expressing):

| Comparator | Mean CPM | Malignant-to-comparator ratio |
|---|---:|---:|
| Fibroblast | 68.10 | 0.42 |
| Macrophage | 48.81 | 0.58 |
| Endothelial cell | 40.80 | 0.70 |
| Dendritic cell | 5.10 | 5.60 |
| T cell | 1.42 | 20.04 |

**Implication:** an ADC or TCE that simply targets "B7-H3" will deliver payload to, or kill, B7-H3-high stromal and myeloid cells as well as tumour cells. This does not kill the target, but it weakens the tumour-selectivity argument and raises the bar for a quantitative tumour-versus-normal protein-density package. It is also a reason to prefer a payload with a favourable bystander/toxicity profile and a tumour-selective linker/conjugation strategy.

**Apply this symmetrically.** The same fibroblast > epithelial pattern exists in both diseases: SCLC epithelial-to-fibroblast ratio 0.42 and epithelial-to-macrophage 0.58; LUAD malignant-to-fibroblast 0.31 and malignant-to-macrophage 0.72. SCLC is not exempt from the stromal/myeloid antigen sink, and this finding must not be used as a LUAD-specific disqualifier. It is a shared caveat for any B7-H3-directed cytotoxic modality in both indications.

Caveats: CPM is not protein; some cell types have small n (SCLC: 9 donors; LUAD malignant: 1 dataset); median CPM is 0; and the LUAD "epithelial cell" mean (28.61) is slightly above "malignant cell" (23.58), so the malignant-versus-normal epithelial contrast is weak at transcript level.

### 2.4 Internalization and shedding

Not established by these databases. Prior knowledge says B7-H3 is internalized on antibody binding and is used as an ADC target, but the absolute rate, antigen turnover and lysosomal delivery fraction are cell-line-dependent and must be measured. Prior knowledge also says the ectodomain can be shed as soluble B7-H3 (sB7-H3), creating a decoy/sink; the rate and concentration are not retrievable.

---

## 3. Scoring framework

Each modality is scored 1-5 on five dimensions. The composite is a weighted sum:

| Dimension | Weight | What a 5 means |
|---|---:|---|
| Mechanistic fit to the biology | 0.25 | Surface-accessible, payload/cell-killing mechanism matches a non-dependency antigen, and the format exploits tumour selectivity. |
| Clinical precedence in the indication | 0.25 | Multiple in-scope trials at Phase 3 with a credible path; 1 = no in-scope trial. |
| Feasibility (CMC/manufacturing) | 0.20 | Established platform, standard analytics, scalable supply; 1 = bespoke, supply-constrained. |
| Differentiation vs SOC and competitor ADCs | 0.15 | Clear biomarker/mechanism niche versus current SOC and TROP2/DLL3/SEZ6 agents. |
| Risk profile (5 = lowest risk) | 0.15 | Manageable, monitorable toxicity with a credible mitigation. |

Clinical precedence is weighted highly because it is the strongest de-risking evidence available, but it is **feasibility evidence only**. An equal-weight sensitivity check is included in the ranking CSV; the rank order is stable in both indications (LUAD CAR-T and radioligand tie at 1.85, broken by direct lung-cancer clinical presence and absence of an isotope supply chain).

**Revision note on scoring.** The quantitative composite scores are retained. The only score change is LUAD ADC clinical precedence, now **1/5** rather than 2/5, because there is no LUAD-specific trial; the indirect nonsquamous-NSCLC trials establish eligibility, not LUAD-specific precedence. This changes the LUAD ADC composite from 3.15 to 2.90 but does not change the rank order. The SCLC ADC composite remains 4.20; the change there is to the **decision rule** (staged GO), not the score. Decision status, conditions, risk attribution and normal-lung qualification are carried as separate fields so that a high feasibility score cannot be read as an efficacy claim.

---

## 4. Ranked modalities

### 4.1 SCLC

| Rank | Modality | Composite | Recommendation | Core rationale |
|---:|---|---:|---|---|
| **1** | **B7-H3 ADC** (topoisomerase-I payload default) | **4.20** | **STAGED GO — conditional** | Feasibility is established (26 SCLC-contributing trials; 6 Phase 3 across 4 molecules), efficacy is not. Commit after a positive class-level Phase 3 readout and with a differentiated molecule/profile. |
| 2 | B7-H3 bispecific / T-cell engager | 3.05 | Backup only, with a tumour-selective format | Off-the-shelf, and the TCE class has clinical proof in SCLC via DLL3-directed agents (prior knowledge), but there are no B7-H3 TCE data and the normal-tissue window is narrow. |
| 3 | B7-H3 CAR-T (autologous; NK-CAR not precedented) | 2.65 | Research track | One Phase 1, no results; autologous manufacturing and solid-tumour barriers. |
| 4 | B7-H3 radioligand / RIT | 2.40 | Research/combination track | Crossfire is orthogonal, but isotope/dosimetry/logistics and normal-lung dose keep it behind ADC/TCE. |

### 4.2 LUAD

| Rank | Modality | Composite | Recommendation | Core rationale |
|---:|---|---:|---|---|
| **1** | **B7-H3 ADC** (topoisomerase-I payload default) | **2.90** | **DEPRIORITIZED — competitive/precedence grounds** | No LUAD-specific trial (clinical precedence 1/5) and intense TROP2/HER3 ADC and IO competition. LUAD patients are eligible in nonsquamous-NSCLC trials (NCT07464327 Phase 3, NCT06780085 Phase 2, NCT07824882 Phase 2). The shared stromal/myeloid antigen sink and ILD margin are caveats, not a scientific no-go. |
| 2 | B7-H3 bispecific / T-cell engager | 2.25 | Not a lead — deprioritized | No LUAD-specific TCE; CRS/pulmonary toxicity on a background of lung disease. |
| 3 | B7-H3 CAR-T | 1.85 | Not a lead — deprioritized | No LUAD-specific data; manufacturing and on-target lung toxicity. |
| 4 | B7-H3 radioligand / RIT | 1.85 | Not a lead — deprioritized | No LUAD-specific data; normal-lung dose and isotope logistics. |

The full row-level scores, decision status/conditions, rationale, timeline and cost ranges are in `results/tables/b7h3_modality_ranking.csv`. Figures: `results/figures/b7h3_modality_composite_scores.png` and `results/figures/b7h3_modality_dimension_heatmap.png`.

### 4.3 Target-level versus payload-level risk

Risk is separated by attribution in `results/tables/b7h3_target_vs_payload_risk_attribution.csv`. **Target-level** risks (broad low-level expression, the shared stromal/myeloid sink, soluble B7-H3 decoy, unquantified density/internalization/isoform) apply to every B7-H3-directed cytotoxic modality in both indications. **Payload-level** risks (DXd-class ILD/pneumonitis, myelosuppression, CRS/ICANS, radioligand absorbed dose, autologous manufacturing) are properties of the chosen payload or format and must not be attributed to CD276 biology. The unposted Phase 3 efficacy is a **programme-level evidence gap**, not a toxicity signal.

---

## 5. Modality-by-modality assessment

### 5.1 B7-H3 ADC — Rank #1 in both indications

**Precedent.**
- SCLC: 26 SCLC-contributing interventional trials; 6 Phase 3 across 4 molecules (I-DXd NCT06203210; HS-20093/risvutatug rezetecan NCT06498479 and NCT07099898; MHB088C NCT06954246; YL201 NCT06612151; plus limited-stage NCT06526624). ARTEMIS-008 (NCT06498479) is completed with no posted results. Only posted SCLC-specific result: MGC018 ORR 0/9 (n=9), with atrial fibrillation 3/9 and infectious/respiratory serious events.
- LUAD: zero LUAD-specific trials, so clinical precedence is 1/5. LUAD patients are an eligible subset of the nonsquamous-NSCLC trials: NCT07464327 (HS-20093 + adebrelimab, Phase 3, not yet recruiting), NCT06780085 (I-DXd + raludotatug deruxtecan, Phase 2, recruiting) and NCT07824882 (HS-20093 + adebrelimab, Phase 2, not yet recruiting). NSCLC-context efficacy: enoblituzumab + pembrolizumab ORR 33.3% (5/15, IO-naive) and MGC018 ORR 15.0% (3/20); neither reports LUAD separately. **No LUAD-specific trial is not the same as no LUAD evidence.**
- Drug MCP: no CD276 ADC record. The registry, not the drug MCP, is the precedent source.

**Pros.**
- Surface antigen with an extracellular ectodomain; payload delivery does not require an intrinsic dependency.
- Established ADC CMC, analytics and supply chain; off-the-shelf.
- SCLC is chemo-sensitive and has a higher tolerated toxicity ceiling (prior knowledge); B7-H3 is a heavily trialled target (feasibility precedent, not efficacy).
- A biomarker (B7-H3 IHC) and a payload/linker differentiation strategy are feasible.

**Cons — target-level.**
- Broad normal expression, including lung and myeloid cells; shared stromal/myeloid antigen sink (SCLC 0.42 and LUAD 0.31 fibroblast-to-epithelial/malignant ratio; LUAD macrophage 0.72).
- Internalization and shedding are not quantified; the antigen sink may reduce tumour exposure.

**Cons — payload-level.**
- DXd-class ILD/pneumonitis and myelosuppression; duocarmycin-class ocular/myelosuppression liabilities. These are payload liabilities, not CD276 biology.

**Cons — programme-level.**
- Crowded class: six Phase 3 B7-H3 ADCs in SCLC. A me-too ADC is not investable.
- No proven efficacy in either indication.

**Feasibility, timeline, indicative cost.**
- Hit-to-clinic: 2.5-4.0 years; full development: 7-9 years.
- Cost to IND: $15-30M; full development: $0.8-1.5B (indicative prior-knowledge range; excludes platform/build-out; assumes existing ADC capability).
- CMC: linker/payload supply, DAR control, conjugation site, release/characterization, stability; topoisomerase-I payload supply is the main external dependency.

**Differentiation versus SOC and competitor ADCs.**
- SCLC: versus DLL3 ADC (rovalpituzumab tesirine, Phase 3 completed/terminated) and DLL3xCD3 TCE (tarlatamab, prior knowledge). B7-H3 can address DLL3-low/negative and post-DLL3 disease, but must show a survival benefit over topotecan and a safety advantage over I-DXd/HS-20093.
- SCLC: versus TROP2 ADC (sacituzumab govitecan, Phase 1 suspended in the MCP) and SEZ6 ADC (ABBV-706, prior knowledge; 0 MCP records). TROP2/SEZ6 have less Phase 3 momentum in SCLC than B7-H3.
- LUAD: versus TROP2 ADC (datopotamab deruxtecan, prior knowledge; 0 MCP LUAD records), HER3 ADC (patritumab deruxtecan, prior knowledge), and other ADCs. B7-H3 needs a TROP2-refractory/high-B7-H3 niche or a differentiated payload; otherwise it is late and undifferentiated.

**Key risks (separated by attribution).**
- Target-level: broad low-level expression; shared stromal/myeloid antigen sink; soluble B7-H3; unquantified density/internalization.
- Payload-level: ILD/pneumonitis, especially in LUAD with prior IO/radiation; myelosuppression; off-tumour payload delivery.
- Programme-level: no posted Phase 3 efficacy; crowded class.

**Recommendation.**
- SCLC: **STAGED GO** — commit only after (a) a class-level Phase 3 efficacy readout is available and positive (ARTEMIS-008 or I-DXd vs physician's choice) and (b) the molecule has a differentiated payload/linker, biomarker niche or combination. Do not advance a "me-too" DXd ADC on feasibility alone.
- LUAD: **DEPRIORITIZED on competitive/precedence grounds** (not a scientific no-go). Re-evaluate on a LUAD-specific readout or a demonstrated tumour-to-normal-lung protein-density window. See Section 7.2 for the evidence that would change the decision.

---

### 5.2 B7-H3 bispecific / T-cell engager — Rank #2 SCLC; #2 LUAD but deprioritized

**Precedent.**
- No SCLC or LUAD B7-H3 TCE.
- MGD009 (B7-H3xCD3 DART) was Phase 1 in NSCLC context and terminated for business reasons (NCT02628535); no LUAD/SCLC cohort or efficacy result.
- IBB0979 is a B7-H3xIL-10R antibody-cytokine fusion, not a TCE (NCT07076095, SCLC, not yet recruiting). Gocatamig is DLL3xCD3 and is being combined with I-DXd; it is not a B7-H3 TCE.
- DLL3 TCE (tarlatamab) validates the TCE class in SCLC (prior knowledge), but not B7-H3.

**Pros.**
- Off-the-shelf antibody logistics; no autologous manufacturing.
- Potent T-cell redirection; can kill antigen-low cells and be combined with checkpoint blockade or ADCs.
- A tumour-selective format (masked/prodrug, affinity-tuned, density-gated) could address the normal-tissue problem.

**Cons.**
- CRS/ICANS; on-target/off-tumour killing of B7-H3-low normal lung and myeloid cells.
- No posted B7-H3 TCE efficacy or safety result; narrow therapeutic window.
- SCLC immunosuppression and T-cell exhaustion may limit activity.
- LUAD patients often have compromised pulmonary reserve and prior checkpoint pneumonitis.

**Feasibility, timeline, indicative cost.**
- Hit-to-clinic: 2.0-3.5 years; full development: 7-10 years.
- Cost to IND: $10-25M; full development: $0.6-1.2B (indicative prior-knowledge range).
- CMC: bispecific format engineering, half-life extension, potency/CRS assays; standard antibody manufacturing.

**Differentiation versus SOC and competitor ADCs.**
- SCLC: must differentiate from DLL3 TCE (tarlatamab) and from B7-H3 ADCs. A B7-H3 TCE could be used after DLL3-directed therapy or in DLL3-low disease, but there is no data.
- LUAD: competes with PD-1xVEGF and EGFR/MET bispecifics and with established IO/chemotherapy; no B7-H3 TCE data.
- Versus TROP2/DLL3/SEZ6 ADCs: a TCE is a different killing mechanism and could complement ADCs, but it is not a near-term replacement.

**Key risks.** CRS/ICANS; normal-lung/myeloid toxicity; no clinical proof; narrow window; immunosuppressive microenvironment.

**Recommendation.** SCLC **backup** only, with a tumour-selective format and a density/masking strategy. LUAD **not a lead — deprioritized** (no LUAD-specific precedent and no density-based selectivity).

---

### 5.3 B7-H3 CAR-T (including NK-CAR) — Rank #3 SCLC; #3 LUAD but deprioritized

**Precedent.**
- One Phase 1 autologous B7-H3 CAR-T in pretreated ES-SCLC (NCT07509034, recruiting, start 2026-10-25, n=40, MTD/DCR). No results.
- One EGFR/B7H3 dual CAR-T in lung cancer, early Phase 1, histology not specified (NCT05341492). No results.
- No B7-H3 NK-CAR clinical programme was found. Allogeneic NK-CAR remains preclinical for this target.

**Pros.**
- T-cell killing is independent of B7-H3 signalling and can be durable.
- Dual-target CAR-T (EGFR/B7H3) could reduce antigen escape.
- Allogeneic NK-CAR could improve scalability and reduce CRS if it becomes clinically mature.

**Cons.**
- Autologous vein-to-vein manufacturing (typically 3-6 weeks), lymphodepletion and high per-patient COGS.
- CRS/ICANS; on-target lung toxicity; poor solid-tumour trafficking and persistence.
- Heavily pretreated SCLC patients may not tolerate lymphodepletion.
- No posted B7-H3 CAR-T efficacy in a solid tumour was found; no NK-CAR clinical precedent.

**Feasibility, timeline, indicative cost.**
- Hit-to-clinic: 2.0-3.0 years; full development: 8-12 years.
- Cost to IND: $20-40M; full development: $0.8-1.5B; per-patient COGS approximately $50-150k (indicative prior-knowledge range).
- CMC: viral vector, apheresis, automated manufacturing, release testing, chain-of-identity/custody.

**Differentiation versus SOC and competitor ADCs.**
- SCLC: CAR-T is a distinct, potentially durable option after ADC/TCE failure, but it is not competitive as a first-in-class modality.
- LUAD: even less precedented; on-target lung toxicity and manufacturing scale are prohibitive for a broad population.
- Versus TROP2/DLL3/SEZ6 ADCs: CAR-T is orthogonal and could be a later-line option, not a replacement.

**Key risks.** Manufacturing failure/logistics; CRS/ICANS; on-target lung toxicity; antigen escape; no efficacy; cost.

**Recommendation.** SCLC **research track**; LUAD **not a lead — deprioritized**. NK-CAR is a watch item, not a ranked modality.

---

### 5.4 B7-H3 radioimmunotherapy / radioligand — Rank #4 in both

**Precedent.**
- 177Lu-BetaBart Phase 1/2 in relapsed solid tumours including an SCLC cohort (NCT07189871, recruiting, n=61, cohort size not reported). No LUAD-specific cohort.
- 8H9 131I (omburtamab) reached Phase 2 only in compartmental/CNS indications (leptomeningeal metastasis, neuroblastoma, peritoneal cancer, DIPG) and was terminated/withdrawn. Drug MCP confirms four indications, no lung. This is not a systemic lung-cancer precedent.
- No posted B7-H3 radioligand efficacy in LUAD or SCLC was found.

**Pros.**
- Radiation crossfire can address antigen heterogeneity and does not require internalization.
- Orthogonal to ADC/TCE; potential combination or later-line option.
- A thermostic pair (imaging + therapy) could support patient selection.

**Cons.**
- Normal-lung and marrow absorbed dose; kidney/off-target dose.
- Isotope supply, radiochemistry, cold chain, radiation safety and repeated-dosing logistics.
- No systemic SCLC/LUAD efficacy; compartmental 8H9 data do not transfer to IV dosing.

**Feasibility, timeline, indicative cost.**
- Hit-to-clinic: 2.0-4.0 years; full development: 7-10 years.
- Cost to IND: $10-25M; full development: $0.4-0.8B (indicative prior-knowledge range).
- CMC: Lu-177 supply, chelator/linker, specific activity, radiochemical purity, dosimetry.

**Differentiation versus SOC and competitor ADCs.**
- SCLC: an orthogonal payload; could be combined with an ADC or TCE, but not a lead.
- LUAD: normal-lung dose is a major liability; no LUAD data.
- Versus TROP2/DLL3/SEZ6 ADCs: different mechanism; likely combination/later-line, not a competitive first-line modality.

**Key risks.** Marrow/lung/kidney dose; isotope supply; radiation safety; no efficacy; compartmental precedent only.

**Recommendation.** SCLC **research/combination track**; LUAD **not a lead — deprioritized**.

---

### 5.5 Not ranked

| Modality | Assessment | Reason |
|---|---|---|
| Small molecule | **Not viable** | All Open Targets SM criteria false; 0 chemical probes; no pocket/ligand. |
| PROTAC/degrader | **Not viable** | No small-molecule binder; no UniProt ubiquitination-site evidence; generic database flags do not enable degradation. |
| Naked antibody | **Not competitive** | Enoblituzumab is Phase 2 in HNSCC/prostate/melanoma, no lung indication; no intrinsic dependency or payload, so no monotherapy rationale in LUAD/SCLC. |
| B7-H3xIL-10R fusion | **Watch item** | IBB0979 is an immune-cytokine fusion, not a TCE; SCLC Phase 2/3 with topotecan is not yet recruiting. Not a ranked modality. |

---

## 6. Differentiation versus SOC and competitor ADCs

### 6.1 SCLC

**Current SOC (prior knowledge, not MCP-derived):** first-line platinum/etoposide plus a PD-L1 inhibitor; second-line topotecan, lurbinectedin, tarlatamab (DLL3xCD3 bispecific) and amrubicin in some regions.

| Competitor class | Evidence status | Implication for B7-H3 |
|---|---|---|
| DLL3 ADC (rovalpituzumab tesirine) | Phase 3 completed/withdrawn/terminated (MCP: 6 records, one agent) | Validates DLL3 as a target but is a caution on ADC translation; B7-H3 can address DLL3-low disease. |
| DLL3 TCE (tarlatamab) | Prior knowledge; not mapped in the drug MCP | The key SCLC competitor. B7-H3 ADC/TCE must show benefit after or alongside DLL3-directed therapy. |
| TROP2 ADC (sacituzumab govitecan) | Phase 1 suspended in SCLC (MCP) | Less Phase 3 momentum than B7-H3; a secondary competitor. |
| SEZ6 ADC (ABBV-706) | Prior knowledge; 0 MCP records | Early-phase competitor; monitor. |
| B7-H3 ADC class | 6 Phase 3 trials (registry) | Crowded. Differentiation must be safety (ILD), payload novelty, or combination. |

### 6.2 LUAD

**Current SOC (prior knowledge, not MCP-derived):** platinum doublet plus PD-(L)1; targeted therapy for actionable drivers (EGFR, ALK, ROS1, BRAF, MET, RET, KRAS G12C); second-line docetaxel and ADCs.

| Competitor class | Evidence status | Implication for B7-H3 |
|---|---|---|
| TROP2 ADC (datopotamab deruxtecan) | Prior knowledge; 0 MCP records for LUAD (coverage gap) | The main ADC competitor in nonsquamous NSCLC. B7-H3 needs a TROP2-refractory/high-B7-H3 niche. |
| TROP2 ADC (sacituzumab govitecan) | Prior knowledge; MCP has SCLC but not LUAD | Additional TROP2 competition. |
| HER3 ADC (patritumab deruxtecan) | Prior knowledge | Another ADC competitor in EGFR-mutant/refractory LUAD. |
| DLL3 / SEZ6 ADCs | Not relevant in LUAD (SCLC/neuroendocrine targets) | No differentiation angle from these targets in LUAD. |
| B7-H3 TCE | No LUAD data | Competes with PD-1xVEGF and EGFR/MET bispecifics; not a near-term lead. |

**Key point:** in SCLC, B7-H3 is a crowded but heavily trialled ADC target. In LUAD, B7-H3 is a crowded, unvalidated target with no LUAD-specific trial and intense TROP2/HER3 and IO competition. LUAD patients are eligible in the nonsquamous-NSCLC trials, so the difference is one of **precedence and strategic positioning**, not evidence that the biology is disqualifying or that the normal-tissue window is worse in LUAD — the stromal/myeloid sink is shared.

---

## 7. Decision criteria and the decisive experiments

### 7.1 SCLC — STAGED GO on ADC

**Preconditions to the GO (both must be satisfied before committing ADC CMC):**

1. **(a) Class-level Phase 3 efficacy readout.** A positive randomised Phase 3 result for a B7-H3 ADC in SCLC (e.g. ARTEMIS-008 or I-DXd vs physician's choice) showing a credible OS or PFS benefit. ARTEMIS-008 is completed with no posted results, and the only posted SCLC-specific result is MGC018 ORR 0/9 (n=9), a small under-enrolled signal. **Trial existence is not efficacy.** If the class-level readout is negative, stop.
2. **(b) Differentiated molecule/profile.** A novel payload/linker with lower ILD risk, a combination that improves durability (e.g., with a DLL3 TCE or PD-L1), or a biomarker-defined population not adequately served by I-DXd/HS-20093/MHB088C/YL201. A "me-too" profile is not investable, regardless of feasibility.

**Programme go criteria (all should be met before committing ADC CMC):**

These thresholds are proposed decision gates, not validated clinical cut-offs; they must be calibrated with the assay and the chosen payload.

1. **Target density.** >= 60% of SCLC tumours show >= 2+ membranous B7-H3 by IHC; calibrated surface density >= 50,000 molecules/cell in >= 2 SCLC models; tumour-to-normal-lung ratio >= 3.
2. **Internalization.** >= 40% of surface-bound antibody internalized within 24 h with lysosomal delivery in SCLC cells; payload release confirmed.
3. **Preclinical activity.** >= 30% tumour regression (or >= 50% growth inhibition) in >= 2 SCLC PDX models at exposures with an acceptable safety margin; compare topoisomerase-I versus duocarmycin payloads.
4. **Safety.** No grade >= 3 lung toxicity in cynomolgus at >= 3x the efficacious AUC; reversible myelosuppression; no unexpected CNS toxicity.
5. **Differentiation.** Restated from precondition (b) with a concrete profile.
6. **Clinical.** A Phase 1 signal of ORR >= 25-30% and mPFS >= 4 months in 2L+ SCLC would support Phase 2. This is a benchmark, not an assumption.

**No-go criteria:**

- < 30% of tumours at >= 2+, or tumour-to-normal-lung ratio < 2.
- Internalization < 20%.
- No PDX regression at tolerated exposures.
- Unacceptable lung or marrow toxicity in NHP.
- A "me-too" profile with no differentiation from the six Phase 3 B7-H3 ADCs.
- A class-level Phase 3 readout showing no OS benefit.

**Single most important experiment:** a **paired quantitative surface-B7-H3 density and internalization study** in >= 20 SCLC patient tumours and matched normal lung, using calibrated IHC/flow (molecules per cell) plus a lysosomal-trafficking assay. This simultaneously tests the efficacy premise (enough tumour target) and the toxicity premise (tumour-versus-normal window), which is the decision the ADC choice hinges on. The external readout that gates the staged GO is the first randomised Phase 3 OS result (ARTEMIS-008 or I-DXd vs physician's choice).

### 7.2 LUAD — DEPRIORITIZED, not a scientific no-go

The current decision is a **strategic prioritization**: no LUAD-specific trial (precedence 1/5), intense TROP2/HER3 ADC and IO/chemotherapy competition, and no demonstrated differentiation. It is **not** a conclusion that B7-H3 biology is disqualifying, and it is **not** a claim that no LUAD evidence exists — LUAD patients are eligible in the nonsquamous-NSCLC trials (NCT07464327 Phase 3, NCT06780085 Phase 2, NCT07824882 Phase 2).

**Evidence that would trigger re-evaluation (all would be required):**

These thresholds are proposed decision gates, not validated clinical cut-offs; they must be calibrated with the assay and the chosen payload.

1. **LUAD-specific target density.** >= 50% of LUAD specimens show >= 2+ membranous B7-H3; tumour-to-normal-lung ratio >= 3; malignant-cell surface density above the shared stromal/myeloid background.
2. **Internalization.** >= 40% in LUAD PDX; payload delivery confirmed.
3. **Preclinical activity.** >= 30% regression in >= 2 LUAD PDX after platinum/IO.
4. **Safety.** An ILD/pneumonitis profile acceptable in a population with prior IO/radiation; clean NHP lung histopathology at efficacious exposure. This is a payload-level gate, not a target-level one.
5. **Differentiation.** A biomarker-defined niche versus TROP2/HER3 ADCs (e.g., TROP2-low/refractory, B7-H3-high) or a differentiated payload/combination. Without this, stay deprioritized.
6. **Clinical.** A LUAD-specific Phase 1/2 readout with ORR >= 20-25% in 2L+ and manageable ILD, or a LUAD-specific subgroup analysis from the nonsquamous-NSCLC trials. No such data exist today.

**Reasons to remain deprioritized (strategic, any one is sufficient):**

- No clear differentiation versus TROP2/HER3 ADCs or the current SOC.
- A strategic requirement for a fast path: the absence of a LUAD-specific trial means the programme would start from zero in a crowded indication.
- A LUAD-specific tumour-to-normal-lung protein-density window is not demonstrated.
- An ILD signal in NHP or early clinic (payload-level).
- A class-level Phase 3 readout in SCLC that fails to show benefit would also weaken the LUAD case, because the antigen and the stromal sink are shared.

**Single most important experiment:** a **LUAD-specific, matched tumour/normal-lung surface B7-H3 density study with a TROP2 comparator**, plus internalization in LUAD PDX. The transcript data show that malignant cells are not the dominant source in either LUAD or SCLC; the decisive question is whether surface protein density on malignant cells is high enough, and the tumour-to-normal-lung ratio wide enough, to support a cytotoxic payload. If that study fails, no ADC design can rescue the programme — but that would be a target/format failure, not evidence that the diagnosis of LUAD is the problem.

---

## 8. Limitations

1. **No tumour expression in the MCP expression dataset.** It contains 123 normal-tissue/immune entries and no LUAD/SCLC tumour samples. Tumour expression is from the single-cell table (transcript) and prior knowledge; neither is a substitute for IHC/flow protein density.
2. **Single-cell transcript is sparse and not protein.** Median CPM is 0 in the key cell types; some cell-type estimates have small n (SCLC: 9 donors; normal lung: 4 donors); the LUAD malignant estimate comes from one dataset. The fibroblast/macrophage signal is a shared caution in both indications, not a definitive target-density measurement.
3. **Normal-lung expression depends on assay scale.** Bulk RNA level 4 (1,683 TPM) is not reproduced at protein level (HPA level 2) or at cell-level transcript (13.9 CPM weighted mean). No conclusion about a tumour-to-normal-lung protein window can be drawn from these data.
4. **Internalization, recycling and shedding are not retrievable.** ADC payload/linker selection is therefore based on prior knowledge and class precedent, not measured kinetics.
5. **Drug MCP coverage is incomplete.** It contains only enoblituzumab and 8H9 131I for CD276, with no ADC, TCE, CAR-T or radioligand records and no lung-cancer indications. Zero-match queries are coverage statements, not evidence of absence.
6. **ClinicalTrials.gov results lag.** Most trials are recruiting or not yet recruiting. The absence of posted results is not evidence of failure. ARTEMIS-008 is completed with no results module; MGC018 ORR 0/9 (n=9) is a small under-enrolled signal.
7. **No proven efficacy.** The only posted SCLC-specific result is 0/9. No LUAD-specific B7-H3 trial exists, but LUAD patients are eligible in nonsquamous-NSCLC trials and no LUAD-specific readout has been reported. All efficacy statements are framed as benchmarks or hypotheses.
8. **Payload toxicities are not target toxicities.** ILD/pneumonitis, myelosuppression, CRS/ICANS and radioligand absorbed dose are attributed to the payload or format. The target-level liabilities are broad expression, the shared stromal/myeloid sink, soluble antigen and unquantified density.
9. **Cost and timeline are indicative prior-knowledge ranges**, not database-derived. They exclude platform/build-out costs and assume an existing biologics/ADC capability.
10. **Competitor statements for tarlatamab, datopotamab deruxtecan, patritumab deruxtecan and ABBV-706 are prior knowledge**, because the drug MCP did not return them for the relevant target/indication queries. They are labelled as such and are not used as MCP evidence.
11. **No web search, publications or conference abstracts were queried.** The clinical evidence is registry-based.

---

## 9. Artifacts

| Artifact | What it shows |
|---|---|
| `results/tables/b7h3_modality_ranking.csv` | Eight indication x modality rows with the five dimension scores, weighted and equal-weight composites, rank stability, decision status, decision conditions, recommendation, target-level vs payload-level risks, precedent, normal-lung qualification, stromal-sink note, timeline and cost ranges. |
| `results/tables/b7h3_modality_precedent_evidence.csv` | Precedent rows for ADC, TCE, CAR-T, NK-CAR, RIT, naked antibody, small molecule/PROTAC and competitor DLL3/TROP2/SEZ6 queries, with source and coverage notes; includes the three LUAD-eligible nonsquamous-NSCLC trials. |
| `results/tables/cd276_normal_lung_expression_qualification.csv` | Normal-lung CD276 by assay scale: bulk RNA 1,683 TPM (level 4), HPA protein level 2, Census cell-level transcript 13.9 CPM weighted mean (12,315 cells, 4 donors). |
| `results/tables/b7h3_target_vs_payload_risk_attribution.csv` | Eleven risks classified as target-level, payload-level or programme-level, with affected modalities, evidence source, mitigation and attribution note. |
| `data/processed/b7h3_mcp_query_log.csv` | Every MCP query run for this deliverable, its result count/summary, interpretation and whether it was used as evidence. |
| `results/tables/cd276_key_celltype_expression.csv` | CD276 mean CPM and percent expressing per key LUAD/SCLC cell type, with ratios to the malignant/epithelial reference. |
| `results/tables/cd276_malignant_vs_stromal_ratios.csv` | Malignant-to-comparator ratios for the single-cell data; shows the shared stromal > malignant pattern in both SCLC (0.42) and LUAD (0.31). |
| `results/figures/cd276_malignant_vs_stromal_expression.png` | Bar chart showing CD276 is higher in fibroblasts/macrophages than malignant/epithelial cells in both indications. |
| `results/figures/b7h3_modality_composite_scores.png` | Ranked composite scores for LUAD and SCLC, titled to reflect the staged GO and the LUAD deprioritization. |
| `results/figures/b7h3_modality_dimension_heatmap.png` | Dimension-level heatmap for the eight ranked rows. |
| `code/scripts/build_cd276_expression_summary.py` | Reproducible single-cell summary and figure. |
| `code/scripts/build_b7h3_modality_ranking.py` | Reproducible scoring, ranking, precedent table, normal-lung qualification, risk attribution and figures. |

---

*Prepared for the CSO-led therapeutic-candidacy evaluation. All efficacy statements are bounded by the absence of posted B7-H3 Phase 3 results in LUAD and SCLC as of 2026-10-20; ARTEMIS-008 (NCT06498479) is completed with no results module. SCLC is a staged GO, and LUAD is deprioritized on competitive/precedence grounds rather than declared a scientific no-go.*
