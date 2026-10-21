# Scientific Review: B7-H3 (CD276) Therapeutic Candidacy in LUAD and SCLC

**Reviewer:** scientific-reviewer
**Date:** 2026-10-20
**Query under review:** "Evaluate the therapeutic candidacy of B7-H3 (CD276) in lung
cancer. Scope strictly to LUAD and SCLC — not NSCLC broadly, not other lung
histologies. Database MCP servers only; prior knowledge labelled. Spatial/Visium
out of scope."

**Review method.** Read all eight specialist reports and fifteen result tables;
independently re-derived or spot-checked headline numbers from the saved
artifacts (Section B). No new analysis was performed.

---

## Overall assessment

The evidence package is unusually well disciplined on epistemics: negative and
zero-result queries are almost everywhere labelled as gaps rather than findings,
prior knowledge is segregated, and the genetics stream explicitly refuses to
manufacture a causal rationale. The weak points are not missing data so much as
**asymmetric use of the same data across streams** and **three claims that the
saved tables do not support**: the "2x in 3/3 donors" result, the SCLC
"malignant reference" label, and the "normal lung level-4 expresser" framing as
a lung-specific liability. The overall recommendation (SCLC conditional GO /
LUAD deprioritise) is **broadly supportable but not as written**; the
corrections in Section H are required before synthesis.

---

## 1. Verdicts

| # | Stream | Verdict | Basis |
|---|---|---|---|
| 1 | genomics-analyst | **Pass** (2 corrections) | Correct conclusion, well bounded, disease IDs correct; internal count inconsistency (303 vs 123 credible sets "in the window") and an unverified CI level. |
| 2 | single-cell-analyst | **Revise** | Headline "2x in 3/3 donor pairs" is contradicted by its own table; no methods/QA document; "128 donors" not traceable; a compartment column mislabels normal epithelium as malignant. |
| 3 | functional-genomics-analyst | **Pass** | Best-documented stream. Numbers reproduce exactly. Histology curation is prior knowledge but disclosed with a sensitivity analysis. |
| 4 | bio-pathways-ppi-analyst | **Pass** (2 corrections) | Excellent restraint; "LoF tolerance: favourable" is the wrong reading of o/e 0.667; "95% CI" is not supported by the source table. |
| 5 | clinical-trialist | **Pass** (3 corrections) | Counts reproduce (43 curated, 26 SCLC-contributing, 6 Phase 3, 4 with results). Needs trial-vs-molecule distinction and an explicit LUAD-representation statement. |
| 6 | fda-safety-officer | **Revise** | Two prior-knowledge claims contradict the expression stream; target-level and payload-level risk are conflated in the headline rating. |
| 7 | target-biologist | **Pass** (1 correction) | Accurate and well-labelled. Should note that the highest normal expressers (macrophages) have no reliable protein data. |
| 8 | medchem-pharmacologist | **Revise** | Recommendation direction is defensible; the decision logic carries three traceability/scope errors (Section 3–5). |

---

## A. Scope compliance

**Compliant:** genomics (explicitly excludes `EFO_0003060` NSCLC, MONDO_0003438
combined SCLC, and NSCLC/mixed studies), functional genomics (NSCLC used only as
a labelled comparator), target biology, pathways, safety.

**Disease IDs:** `EFO_0000571` (LUAD) and `EFO_0000702` (SCLC) are used
consistently in `cd276_disease_ids.csv` and in target-biologist's targeted
zero-match query. The clinical and safety streams are registry- or
gene-centric and do not carry EFO IDs, which is acceptable. **No disease-ID
drift found.** One nuance worth recording: genomics used the synonym "small cell
lung carcinoma" because the exact string "small cell lung cancer" returned zero —
this is documented and correct.

**Partial drift, labelled:** the clinical stream includes 16 NSCLC-context
trials. This is transparent and acceptable *as context*. The drift occurs
downstream: medchem uses the nonsquamous-NSCLC Phase 3 (NCT07464327) as LUAD's
"credible clinical path" and assigns LUAD a clinical-precedence score of 2 while
simultaneously stating "zero LUAD-specific trials." Under the user's strict
scope, a LUAD clinical-precedence score of 1 is the consistent choice. The rank
of the ADC does not change (Section 5), but the score and the rationale must.

**No stream drifted into other histologies** in a way that altered a headline
conclusion. DepMap's "Lung Neuroendocrine Tumor" label is a tool limitation, is
documented, and is handled with a sensitivity analysis.

---

## B. Numeric traceability (independent checks)

| # | Claim | Source checked | Result |
|---|---|---|---|
| 1 | LUAD mean gene effect −0.230, n=46 | `cd276_depmap_group_comparisons.csv` | **Verified** (−0.23034, n=46) |
| 2 | SCLC mean −0.204, n=25, 0% essential <−0.5 | same | **Verified** (−0.20398, n=25; per-line min −0.482) |
| 3 | 0/8 LUAD+SCLC studies with a CD276-locus credible set | `cd276_luad_sclc_study_cd276_locus_check.csv` | **Verified** (8 rows, all `False`; nearest 4.88 Mb) |
| 4 | 67 L2G rows, none LUAD/SCLC | `cd276_l2g_predictions.csv` | **Verified** (67 data rows; `is_luad_or_sclc=False` in every row inspected, including all top and bottom rows) |
| 5 | 43 curated trials, 26 SCLC-contributing, 6 Phase 3, 4 with posted results | `b7h3_luad_sclc_trials.csv`, `b7h3_posted_results_extract.csv` | **Verified by row count and scope/phase fields** |
| 6 | LUAD 636k cells; SCLC 31.5k cells | `cd276_luad_sclc_celltype_expression.csv` | **Verified** (column sum 635,998; 31,540) |
| 7 | Fibroblast 75.9 CPM vs malignant 23.6 CPM (LUAD) | same | **Verified** (75.915; 23.584) |
| 8 | Tumor epithelium "2x adjacent normal in 3/3 donor pairs" | `cd276_epithelial_tumor_vs_normal_donor_paired.csv` | **NOT SUPPORTED.** Ratios are 3.26, 3.40, **1.09**. Only 2/3 reach 2x. The "2x" is a ratio of donor means (27.0/13.5); direction is 3/3, magnitude is not. |
| 9 | LoF o/e 0.667 (0.506–0.888), p=4.29e-8 | `cd276_constraint_tractability.csv` | **Numbers verified.** The table does **not** state a CI level; pathway calls it 95%, safety calls it 90%. |
| 10 | Normal lung 1,682.5 TPM, RNA level 4, protein level 2 | `cd276_tissue_expression_summary.csv` | **Verified** |
| 11 | SCLC ADC composite 4.20; LUAD 3.15 | `b7h3_modality_ranking.csv` | **Verified** (with equal-weight 4.0 / 3.0) |
| 12 | "128 LUAD donors"; paired-test p=0.22 | no saved artifact | **Not traceable.** Max per-cell-type donor count is 115; the p-value appears in no table. |

---

## C. Ruling: stromal-vs-malignant finding

**Ruling: the observation is real but the caveat is not carried into the
decision logic, and the finding is over-weighted as a LUAD-specific negative.**

What the data actually show (LUAD, CPM): fibroblast 75.9 (26.7% expressing),
alveolar macrophage 34.1, macrophage 32.9, epithelial 28.6, malignant 23.6
(15.4%), endothelial 22.8, T cell 1.5. Median CPM is **0** in every key type.
SCLC shows the same ordering: fibroblast 68.1 > macrophage 48.8 > epithelial
28.5.

1. **The caveat is adequate in prose, absent from the decision fields.** Medchem
   §2.3 and Limitation 2 correctly say "CPM is not protein," "median CPM is 0,"
   "small n," and "the LUAD epithelial mean is above the malignant mean." But
   the bottom-line table and the ranking-CSV rationale state flatly "single-cell
   transcript is higher in fibroblasts/macrophages than malignant cells" with no
   caveat. Decision-facing text must carry the same qualification as the prose.
2. **It is asymmetric.** The identical pattern exists in SCLC (malignant:fibroblast
   0.42 vs 0.31 in LUAD — SCLC is only marginally less stromal-skewed) yet it is
   used as a LUAD pillar and not as an SCLC one. It cannot be a LUAD-specific
   discriminator in its current form.
3. **It is the wrong comparison for an ADC.** The ADC question is tumor-cell
   *surface protein* versus normal-lung-epithelium surface protein; stromal
   expression matters as an **antigen sink and bystander-toxicity amplifier**,
   not as a substitute for malignant-cell density. The stream has a better
   dataset for the relevant comparison — the paired donor analysis (tumor-region
   vs normal-region epithelium, 3.26x / 3.40x / 1.09x, directional in 3/3,
   non-significant, n=3) — and the synthesis should lead with that, with the
   stromal result as the sink argument.
4. **Does it undercut an ADC rationale?** Only partially, and not enough to
   decide either indication. It (a) does not rule out sufficient surface density
   on malignant cells; (b) is confounded by ambient RNA and dissociation, which
   preferentially inflate fibroblast signal; (c) is transcript, not protein; and
   (d) omits the larger, unquantified sink — shed soluble B7-H3 and myeloid
   cells (HPA macrophage RNA 9,456–14,497 TPM, **protein not reliable**). The
   correct conclusion is: "the tumour-selectivity argument is unproven and the
   sink is unquantified; a protein-level tumor-to-normal and tumor-to-stroma
   density study is decisive." That is a gate, not a verdict.

**Required correction:** apply the finding symmetrically; move the caveat into
the ranking CSV rationale; replace "malignant-to-comparator" framing with
"epithelial-to-comparator" for both indications; and state that the paired-donor
result is the ADC-relevant comparison.

---

## D. Ruling: LUAD conclusion

**Ruling: "NO-GO by default" is defensible as a *strategic* decision and
overstated as a *scientific* one. "No LUAD-specific trials" is being used as a
proxy for "no LUAD evidence," and that inference is not valid.**

1. "No LUAD-specific trial" is **correctly established** and the six
   "lung adenocarcinoma" registry hits were individually audited — one is not
   B7-H3-directed, five are pan-tumour/SCLC trials with LUAD only in eligibility
   text. This is good work.
2. But **LUAD patients are exposed in the curated evidence**: NCT07464327
   (Phase 3, nonsquamous NSCLC), NCT06780085 (Phase 2, nonsquamous NSCLC),
   NCT07824882 (Phase 2, nonsquamous NSCLC), NCT05142189, and the pan-tumour
   Phase 1/2 studies. Nonsquamous NSCLC is adenocarcinoma-dominated (prior
   knowledge, and it should be labelled as such). None reports a LUAD-specific
   readout, so the accurate statement is **"no LUAD-stratified efficacy or
   safety readout exists"**, not "there is no LUAD evidence."
3. The three biological pillars offered for LUAD are weaker than presented:
   - *Zero LUAD-specific trials* — a development-landscape fact, not biology.
   - *Stromal > malignant transcript* — see Section C; not LUAD-specific.
   - *"Normal lung is a level-4 expresser"* — this is HPA **RNA** level 4 at
     1,683 TPM, roughly 2x the median of all 120 entries and ~1/9 of macrophage
     levels, while HPA **protein** is level 2 (reliable) and the Census
     single-cell organ summary puts normal lung at 13.9 CPM, among the *lowest*
     organs (skin 46.0, kidney 42.6, adrenal 37.6, adipose 34.5, colon 30.8).
     The claim must be stated as "moderate RNA, moderate protein, cell-level
     transcript low," not "level-4 expresser" used as a high-expression flag.
4. The legitimate LUAD negatives — crowded TROP2/HER3 ADC space, no
   differentiation hypothesis, ILD margin in a comorbid/prior-IO population —
   are **strategic and competitive**, and are strong enough to justify
   deprioritisation. They are not evidence that the target is biologically
   invalid in LUAD.
5. **The LUAD/SCLC asymmetry is driven mainly by trial density, not biology.**
   Both indications have: no dependency, no receptor, no genetic causality,
   broad normal expression, stromal-high transcript, and no efficacy readout.
   The differing recommendation is a portfolio judgment and must be labelled as
   one. If the CSO presents it as "the biology supports SCLC but not LUAD," that
   would be unsupported.

**Required correction:** reframe LUAD as "no LUAD-stratified evidence;
deprioritise on competitive/strategic grounds; the biological gate is
untested and cheap to test," and set LUAD clinical precedence to 1 in the
ranking (composite becomes 2.90; rank unchanged).

---

## E. Ruling: SCLC conclusion

**Ruling: "GO" is premature as stated. The correct statement is a conditional
go to a gated preclinical package, with the first Phase 3 readout as the
decision point. Feasibility is established; efficacy is not.**

1. The evidence for feasibility is real: four distinct B7-H3 ADC molecules in
   Phase 3 (I-DXd; HS-20093/GSK5764227; MHB088C; YL201), plus CAR-T and a
   radioligand in Phase 1/2, plus one expanded-access programme. The ADC class
   works in SCLC via DLL3 (prior knowledge). None of this is efficacy evidence.
2. **"6 Phase 3" overstates independent validation.** Three of the six are the
   same molecule (HS-20093/GSK5764227: NCT06498479, NCT06526624, NCT07099898).
   The correct count is **6 trials / 4 molecules**. This cuts both ways: less
   independent validation than implied, and more concentration of competitive
   risk than a "crowded class" framing suggests.
3. **The composite is inflated by counting trials.** Clinical precedence is
   weighted 0.25 and scored 5/5, which mechanically converts trial density into
   confidence. Capping it at 4 (no readout) gives 3.95 — still rank 1, so the
   *rank* is robust, but the *absolute* 4.20 should not be read as 4.2/5
   confidence.
4. **The decisive readout already exists but is unused.** ARTEMIS-008
   (NCT06498479, n=461, HS-20093 vs topotecan) is **COMPLETED (2026-08-20) with
   no registry results**. That is the single highest-value piece of information
   for this decision and it is buried as a "watch item" in §7. The
   recommendation must be staged on it: no commitment to ADC CMC before that
   result (and the I-DXd Phase 3) is visible.
5. **The only posted SCLC result is 0/9** with atrial fibrillation 3/9 and
   infectious/respiratory SAEs. The clinical stream correctly calls it
   underpowered and not evidence of class failure. It is also not reassuring,
   and medchem's "GO" headline does not carry that tension.
6. The gates in §7.1 are well constructed and explicitly labelled as proposed
   thresholds, not validated cut-offs. This is the strongest part of the
   stream. The headline table should reflect it.

**Required correction:** replace "GO" with "CONDITIONAL GO — gated preclinical
package only; stage the decision on ARTEMIS-008 / I-DXd Phase 3; no me-too DXd
ADC." Add the 4-molecule count.

---

## F. Materiality of gaps

| Gap | Materiality | Why |
|---|---|---|
| **No protein-level tumour density or normal-lung protein (membrane, molecules/cell, tumour:normal ratio)** | **Critical** | This is the decision the ADC choice actually hinges on. Every stream correctly names it; none can fill it. It is the one gap that changes the answer in either direction. |
| **No internalization / recycling / lysosomal delivery** | **Critical** | ADC payload and linker selection cannot be specified without it; all statements are class prior knowledge. |
| **No shedding rate / soluble B7-H3** | **High** | The sink competes with tumour binding and may be larger than the stromal sink being emphasised. |
| **No LUAD-stratified (or nonsquamous-NSCLC histology-stratified) clinical readout** | **High for LUAD** | Without it, LUAD has no efficacy or safety anchor. |
| **ARTEMIS-008 / I-DXd Phase 3 results not posted** | **High for SCLC** | The only route to an efficacy signal in this pass. |
| **SCLC single-cell = one dataset, 9 donors, no malignant label** | **Moderate** | Undermines the SCLC arm of the stromal claim and the "malignant reference"; does not change go/no-go. |
| **Isoform (2Ig vs 4Ig) expression in tumours** | **Moderate** | Antibody/ADC epitope and isoform selectivity cannot be assessed; 4Ig predominates in human tissue (prior knowledge). |
| **No macaque/NHP safety data** | **Moderate** | The recommended toxicology species (94.6% identity) has no retrieved data; mouse is non-predictive (52.4%). |
| **Tahoe-100M unavailable (env var)** | **Low** | Correctly recorded as a failed query, not a zero result. It would inform perturbation/combination biology, not target density or the go/no-go. Must not be cited as a limitation *of the recommendation*. |
| **No FDA records for I-DXd / MGC018** | **Low-moderate** | Means no label-based safety verification for the two agents that matter most. Class ILD/myelosuppression remains prior knowledge. Absence must not be read as a clean profile — the safety stream says this correctly. |
| **No target-level OpenFDA AEs, no mouse phenotype, no PGx** | **Low** | Zero-record queries from an incomplete source; uninformative in both directions. |

**Gap not listed by any stream:** no normal-tissue *protein* data beyond ordinal
HPA levels; the highest RNA expressers (macrophages) have HPA protein
`reliable=False`, so the myeloid-sink argument is currently RNA-only. This
should be stated wherever the sink is invoked.

---

## G. Internal contradictions

1. **LoF CI level.** Pathway: "95% CI 0.506–0.888." Safety table and report:
   "90% CI." The source table records bounds but no level. Same numbers, two
   confidence levels — at most one is right. Harmonise and record the level from
   the raw tool output (gnomAD convention is 90%).
2. **"Overexpressed on LUAD/SCLC relative to normal tissue."** Asserted as prior
   knowledge in the safety stream (both report and
   `b7h3_safety_signals.csv` row 16) and used to frame the risk-benefit read.
   This is contradicted by the single-cell stream (malignant 23.6 CPM vs normal
   epithelium 28.6 CPM; only 2/3 donors ≥2x at region level) and by DepMap
   (non-cancerous lines 5.91 vs LUAD 5.46 on the expression scale). It must be
   downgraded to "asserted from literature; not verified in this run and
   partially contradicted by the transcript data."
3. **"Normal lung is among the highest normal expressers."** Safety says the
   highest are "liver, lung, heart, kidney and bladder"; the actual table has
   lung below macrophages (9,456–14,497), placenta (5,914), tibial artery
   (4,665), smooth muscle (4,181), adipose (4,354) and adrenal (4,092), and
   bladder is not in the table at all. The Census organ summary independently
   ranks lung near the bottom. This prior-knowledge claim should be removed or
   corrected.
4. **SCLC "malignant reference."**
   `cd276_malignant_vs_stromal_ratios.csv` names the SCLC reference
   "epithelial cell" in a column called `malignant_reference_cell_type`, and the
   medchem text calls the ratios "malignant-to-comparator." The single-cell
   stream explicitly reports "no malignant label" for SCLC. An unlabelled
   epithelial population is being promoted to malignant. Relabel or verify.
5. **Trial counts.** "6 Phase 3" = 6 trials / 4 molecules. "26 SCLC-contributing"
   includes one withdrawn, never-enrolled Phase 2 (NCT06052423) and at least
   five combination regimens where B7-H3 is only one component (gocatamig +
   I-DXd). The landscape count should distinguish B7-H3-directed monotherapy
   programmes from B7-H3-containing regimens.
6. **Credible-set counts.** Genomics reports 303 credible sets in the queried
   window, then "116 studies / 123 credible sets in the CD276 window," then 67
   L2G loci. These may be different windows/definitions but the report never
   says so. Clarify or the negative result looks less auditable than it is.
7. **Interaction counts.** Medchem: "40 low-confidence interactions"
   (`get_target_info`). Pathways: 26 STRING + 30 IntAct, 29 distinct partners.
   Different endpoints; should be labelled as such.
8. **LUAD clinical precedence.** Score 2 while the text says zero LUAD-specific
   trials; the 2 is granted on NSCLC context, contrary to the stated scope rule.
9. **"Antibody-tractable: strong."** The tractability table shows every
   localisation-quality flag `False` (UniProt high/medium confidence, GO CC
   high/medium, HPA localisation). The only positive flags are "Advanced
   Clinical" and "SigP or TMHMM." That is sufficient for an ADC, but "strongly
   antibody-tractable" overstates the Open Targets evidence; "clinically
   antibody-bound" is the accurate claim.
10. **"LoF tolerance: favourable" (pathways).** o/e 0.667 with a CI excluding 1.0
    means LoF variants are *depleted* — moderate constraint, not tolerance. A
    safety-favourable reading is an over-interpretation. Both streams correctly
    add that germline constraint says nothing about acute antibody-mediated
    depletion; keep that, drop "favourable."

---

## H. Is the overall recommendation supportable as written?

**Partly.** The direction (SCLC pursue a differentiated ADC; LUAD deprioritise)
is defensible and is the right portfolio answer. It is **not** supportable in
its current wording because:

- **SCLC "GO"** is stated as a conclusion while the report's own evidence is
  feasibility only, the only efficacy datapoint is 0/9, and a completed Phase 3
  readout is unposted.
- **LUAD "NO-GO by default"** is presented with three biological pillars, two of
  which are not supported as stated (stromal transcript is not LUAD-specific;
  "level-4 expresser" is RNA-only and contradicted at cell level), and one of
  which is a development-landscape fact rather than evidence.
- **The asymmetry between the two indications** is not biological and is not
  labelled as strategic.
- **Three decision-facing claims are not traceable to the saved tables**
  (2x in 3/3; "malignant" SCLC reference; 6 Phase 3 as independent validation).

**Minimum corrections for synthesis:**

1. Restate SCLC as "conditional go to a gated preclinical package; decision
   staged on ARTEMIS-008 and the I-DXd Phase 3; 6 trials / 4 molecules; no
   me-too DXd ADC." Do not lift the word "GO" unqualified.
2. Restate LUAD as "no LUAD-stratified evidence; deprioritise on competitive and
   strategic grounds, not because the biology is negative." Note that LUAD
   patients are enrolled in nonsquamous-NSCLC trials and that nonsquamous NSCLC
   is adenocarcinoma-dominated (label as prior knowledge). Set LUAD clinical
   precedence to 1.
3. Apply the stromal finding symmetrically to LUAD and SCLC, carry its caveats
   into the ranking rationale, and relabel the SCLC reference as "epithelial
   (malignant label not available)" or verify it.
4. Correct the normal-lung statement to "HPA RNA level 4 (1,683 TPM), protein
   level 2 (reliable), Census cell-level transcript low (13.9 CPM, among the
   lowest organs)." Remove the claim that lung is among the highest normal
   expressers.
5. Withdraw "2x adjacent normal in 3/3 donor pairs"; replace with "tumor-region
   epithelium ≥2x normal-region epithelium in 2/3 donors; 3.26x, 3.40x, 1.09x;
   p not saved; n=3, underpowered." Save the test statistic.
6. Downgrade FDA's "B7-H3 overexpressed in LUAD/SCLC relative to normal" to a
   labelled literature assertion, explicitly noting the transcript contradiction.
7. Separate **target-level** risk (loosely constrained, broad expression,
   moderate constraint, no receptor) from **payload/class-level** risk (ILD,
   myelosuppression) in the safety headline. "Moderate-to-High" for SCLC is
   largely a payload/SOC-overlap statement, not a target statement.
8. Harmonise the LoF CI level and state that o/e 0.667 indicates moderate
   constraint, not tolerance.
9. List Tahoe-100M, absent FDA records, and absent mouse phenotype once, as
   non-material gaps, and keep the protein-density/internalization/shedding gaps
   as the material ones.
10. Add the missing statement that the myeloid/stromal sink argument rests on RNA
    only (HPA protein unreliable for macrophages) and that soluble B7-H3 is
    unquantified.

---

## Artifacts reviewed

Specialist reports (8), tables (15), including:
`work/genomics-analyst/results/tables/{cd276_luad_sclc_study_cd276_locus_check,
cd276_l2g_predictions, cd276_qtl_colocalization_summary, cd276_disease_ids,
cd276_tractability}.csv`; `work/single-cell-analyst/results/tables/
{cd276_luad_sclc_celltype_expression, cd276_epithelial_tumor_vs_normal_donor_paired,
cd276_normal_tissue_organ_summary}.csv`; `work/functional-genomics-analyst/
results/tables/{cd276_depmap_luad_sclc, cd276_depmap_group_comparisons}.csv`;
`work/bio-pathways-ppi-analyst/results/tables/cd276_constraint_tractability.csv`;
`work/clinical-trialist/results/tables/{b7h3_luad_sclc_trials, b7h3_posted_results_extract,
b7h3_luad_search_hits}.csv`; `work/fda-safety-officer/results/tables/
{b7h3_safety_signals, b7h3_agent_registry_lung_cancer}.csv`;
`work/target-biologist/results/tables/{cd276_tissue_expression_summary,
cd276_tractability_by_modality}.csv`; `work/medchem-pharmacologist/results/tables/
{b7h3_modality_ranking, cd276_malignant_vs_stromal_ratios}.csv`.
