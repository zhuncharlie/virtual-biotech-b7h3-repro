# Panel-by-Paper Comparison — Round 2 B7-H3 (CD276) Case Study (final, reviewed)

**Finalization run:** `20261022-120126-this-continues-a-targeted-correc-06b840ce`
**Correction run (source of the corrected analyses):** `20261022-094819-this-is-a-targeted-correction-pa-d24cb49b`
**Delivery run being corrected:** `20261022-010102-round-2-of-the-b7-h3-cd276-case-76d40ca3`
**Analysis run:** `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
**Reference paper:** Virtual Biotech, Figure 4A–F + Supplementary Figure S5A–B (PMC12970349), LUAD and SCLC.

This file is a standalone, number-by-number comparison of what the paper claims and what this round reproduced. It is the corrected source document for Table 2 in `report/FINAL_REPORT.md`. Three corrections have been applied relative to the round-2 delivery (see `report/ERRATA_figure4_corrections.md`):

1. **Panel 4E/S5B** — the paper's claim is an **immune-EXCLUDED** niche (depletion of neighbouring immune cells in B7-H3-high spots), **not** an immune-hot niche. All previous "immune-hot" language is corrected.
2. **Panel 4A** — the gene-constraint stream (gnomAD pLoF O/E = 0.67) already existed in round-1 artifacts and was never connected to the comparison; it is now a **third evidence stream**.
3. **Panel 4B/4C** — the paper's **fibroblast-specific** claim was **never tested** (the normal-lung fibroblast comparator is underpowered); the 15 tested non-fibroblast contrasts (11 primary + 4 paired sensitivity) are **not** a refutation of it.

Status labels: **Agree**, **Weaker** (same direction, materially lower strength), **Disagree** (not supported / contradicted), **Inconclusive** (not testable).

---

## Summary table

| Panel | Paper claim | This round | Status |
|---|---|---|---|
| 4A | CD276 has genetic credible-set support and lung regulatory-element links; constraint metrics show a pLoF O/E of 0.67 (caption conflates several evidence types) | Germline 0/8 credible sets, 0/67 L2G. Regulatory 839 CD276-linked lung elements (77 within ±500 kb), 29 at Score ≥ 0.02, promoter 0.973 — annotation only. Gene constraint LoF O/E 0.6666 (obs 34, exp 51.002, 95% CI 0.506–0.888) ≈ the paper's 0.67[[claim:C130]] | **Disagree (genetic) / Agree (regulatory + constraint, annotation-only)** |
| 4B/4C | LUAD/SCLC single-cell atlas; pseudobulk DE identifies CD276-associated populations, with significantly increased expression in fibroblasts | 413,996 cells / 80 donors / 15 types; CD276 0 of 15 tested **non-fibroblast** contrasts (11 primary + 4 paired; all p/padj > 0.05, minimum non-null padj 0.291)[[claim:C134]]; the fibroblast contrast the paper names is **untestable** (31 normal cells / 3 donors / 1 ≥10)[[claim:C134]] | **Weaker; tested compartments disagree on "CD276-associated"; the fibroblast claim is untestable, not refuted** |
| 4D/S5A | Signalling unique to B7-H3+ CAFs (SCLC main, LUAD supp) | Rank-based ECM/proteolysis enrichment; no unique signalling; 55–69% depth gap; SCLC 2 donors | **Weaker / Disagree on "unique"** |
| 4E/S5B | **Immune-excluded** niches: B7-H3-high spots have **depleted** neighbouring T cells, macrophages, monocytes and dendritic cells under a mixed-effects model (total UMI, fibroblast, malignant fixed effects; sample random effect) | Three analyses: unadjusted absolute abundance **disagrees** (T +15%, DC +29%, depth-confounded)[[claim:C132]]; depth-robust composition is **mixed**[[claim:C132]]; the paper-specified adjusted model (adapted grouping/random effect) **agrees** (8/9 immune types depleted; all four named compartments depleted)[[claim:C131]] | **Agree under the paper-specified adjusted model (adapted) / disagree unadjusted / mixed composition** |
| 4F | High CD276 → worse OS (1.62, p = 0.028) and DSS (1.82, p = 0.031), n = 566 | Unadjusted Q4-vs-Q1 OS 1.80 (p = 0.0051), DSS 1.86 (p = 0.021); adjusted OS p = 0.106, DSS p = 0.249 | **Agree unadjusted / Weaker adjusted** (unchanged) |
| Tahoe/DepMap | (target-assessment context) | Tahoe DE blocked — not assessable/no evidence either way; DepMap mean CERES −0.230, 1/46 essential | **Inconclusive / Agree (not essential)** (unchanged) |

---

## Panel 4A — Genetics, regulatory elements, and gene constraint

**Paper claim.** Figure 4A presents CD276 as supported by genetics and lung regulatory-element evidence. The caption mixes evidence types (statistical credible-set/genetic association, regulatory enhancer–gene prediction, and 41 "high-confidence" elements). The body text separately states: *"Constraint metrics showed a predicted loss-of-function observed-to-expected ratio of 0.67."*

**What this round found.** Three evidence streams, deliberately kept separate:

- **Germline (statistical genetic) stream — DISAGREES.** 0 of 8 LUAD+SCLC GWAS studies carry a CD276-locus credible set within ±500 kb (also 0/8 by gene-body overlap and 0/8 by locus-interval overlap); 0 of 67 L2G loci derive from a LUAD or SCLC study. Evidence: `cd276_round2_germline_verification.csv` (round-2 analysis run).
- **Regulatory (E2G) stream — AGREES, annotation-only.** ENCODE DNase-only lung rE2G predictions link 839 elements to CD276 genome-wide; 77 lie within ±500 kb of the TSS (median 241.1 kb); 29 reach the pre-declared Score ≥ 0.02 threshold; the top element is the CD276 promoter itself (Score 0.973, 64.5 bp from TSS). Evidence: `cd276_e2g_within_window_score_distance_summary.csv` (round-2 analysis run).
- **Gene-constraint stream (NEW) — AGREES.** gnomAD pLoF observed/expected = **0.6666** (observed 34 vs expected 51.002; 95% CI 0.506–0.888; p = 4.29 × 10⁻⁸), which rounds to the paper's quoted **0.67**[[claim:C130]]. This value was retrieved in round 1 (Open Targets gnomAD constraint via `mcp__target__get_target_info`, 2026-10-20) and was never before connected to this panel. Both round-1 sources (CSV and JSON) agree on every field; the cross-reference is filed in `work/genomics-analyst/results/tables/cd276_panel4a_constraint_crossreference.csv` and documented in `work/genomics-analyst/results/reports/cd276_panel4a_constraint_crossreference.md`.

**Agreement.** Regulatory annotation **agrees** that CD276 has strong local regulatory annotation in lung; gene constraint **agrees** that the gene is under moderate purifying selection; the germline stream **disagrees** — there is no credible-set or L2G support in LUAD/SCLC.

**Important distinctions.**
- E2G Score is a regulatory-link score, not a p-value or disease effect. The 0.02 threshold was chosen from the observed score distribution (above the 95th percentile), **not** to reproduce the paper's 41.
- Gene constraint is a **gene-level population-genetic property** (depletion of LoF variants in a population cohort). It says nothing about LUAD/SCLC and is not a therapeutic hypothesis. Only the germline stream tests disease association, and it is negative.
- The two agreeing streams are annotations of the gene, not evidence of disease causality.

**What would close the gap.** A LUAD/SCLC-specific E2G model (the staged file is lung-biosample, DNase-only, with an averaged Hi-C contact track), an explicit separation of credible-set vs regulatory vs constraint evidence in the paper's caption, and knowledge of the gnomAD release the paper used (not recoverable from our saved artifacts).

---

## Panel 4B/4C — Single-cell atlas and pseudobulk DE

**Paper claim.** A LUAD/SCLC single-cell atlas with pseudobulk differential expression identifying CD276-associated populations. The Figure 4C caption states the DE analysis "identifies significantly increased expression in fibroblasts."

**What this round found.**
- **Atlas:** 413,996 cells, 80 donors, 15 cell types, 61,497 features, after the paper's QC (300–9,000 genes, ≤15% mitochondrial reads, donor-level downsampling to 10,000 cells, library-size normalisation + log1p, 3,000 HVGs, Harmony, UMAP). Evidence: `scrna_cell_donor_audit.csv`, `scrna_panels4bc_report.md` (round-2 analysis run).
- **Differential expression in the tested compartments:** CD276 is **not significant in any of the 15 tested non-fibroblast contrasts** (11 primary: 6 LUAD + 5 SCLC cell types; 4 paired-donor LUAD sensitivity contrasts). All p/padj > 0.05; the smallest non-null padj is **0.291** (SCLC macrophage, log2FC −0.95)[[claim:C134]].
- **Fibroblasts — the compartment the paper names — were NOT tested.** The normal-lung fibroblast comparator has **31 cells across 3 normal donors, only 1 of which reaches the ≥10-cell per-donor threshold** (Census: 37 cells / 3 donors; per-donor 28 / 5 / 4). PyDESeq2 requires ≥3 donors per group, so the fibroblast disease-vs-normal contrast is untestable[[claim:C134]].
- **Census check:** a targeted CELLxGENE Census query (this correction run) found **no safe additional matched normal-lung fibroblast donor**[[claim:C135]]. The only dataset with more testable donors (`350237e0`; 104 fibroblasts / 17 donors, 4 with ≥10) is a **normal-only atlas** on a different platform (10x 5′ vs 10x 3′ v2) with no tumour arm; using it against `576f193c` LUAD would confound disease with study and platform and break the within-study design. Other normal-only atlases (`1b350d0a`, `eb499fd8`, `f14bc322`) contain zero fibroblast-labelled normal lung cells. Details: `work/single-cell-analyst/results/reports/scrna_fibroblast_census_check.md`, `work/single-cell-analyst/results/tables/scrna_fibroblast_census_donor_counts.csv`.
- **Detection (not expression change):** highest percentages in fibroblasts (LUAD 30.8% of 3,411 cells; SCLC 35.3% of 244) and normal-lung macrophages (36.5% of 3,011). Evidence: `scrna_cd276_expression_by_celltype.csv` (round-2 analysis run).

**Agreement — scoped honestly.**
- In the compartments that **were** tested, the atlas is reproduced but there is no disease-associated CD276 signal; any "CD276+ population" claim would rest on detection prevalence, not differential biology.
- The paper's **fibroblast-specific** claim is **untestable in this reproduction**, not refuted. The 15 tested non-fibroblast contrasts are a real, broader negative finding across the *other* compartments — suggestive, but they must **not** be described as a direct test or refutation of the fibroblast claim[[claim:C134]].

**Gap.** Fibroblast disease-vs-normal DE remains a genuine gap (not a null). This is the compartment most relevant to the CAF question.

**Caveat.** Several "tumour-up" genes in non-malignant compartments are tumour identity genes (ASCL1/GRP/INSM1 in SCLC; COL1A1/COL3A1 in LUAD) — ambient RNA/doublets, not immune-intrinsic biology.

---

## Panels 4D/S5A — Cell–cell communication (LIANA)

**Paper claim.** Signalling **unique** to B7-H3+ cancer-associated fibroblasts (SCLC in the main figure, LUAD in the supplement).

**What this round found.** (Unchanged from the round-2 delivery.)[[claim:C139]]
- **Call counts:** SCLC 290 high / 53 low of 4,051 pairs; LUAD 540 / 91 of 5,053.
- **Recurring programme:** THBS2 → CD47 (top call in both diseases, Δ ≈ 0.91–0.92); PLAU → PLAUR/ITGA5/ITGB5/LRP1/IGF2R; SERPINE1 → LRP1/PLAUR; INHBA → ACTR2/ENG (LUAD); SCLC-specific PLTP → ABCA1, MXRA5 → PILRB, WNT5A → FZD3. Evidence: `liana_top_differential_pairs.csv`.
- **Confounding:** the high-vs-low split is detection-based, with a **55–69% detected-gene depth gap**; the high group is also myCAF-marker-enriched (1.43 vs 1.00; donor paired p = 4.8e-7). Evidence: `liana_caf_depth_audit.csv`, `liana_panels4d_s5a_report.md`.

**Agreement.** **Weaker; disagree on "unique."** Most pairs are shared between groups, and there is no formal between-group test, no FDR, and no depth-matched contrast. The defensible statement is a quantitative, rank-based enrichment of an ECM/proteolysis programme in CD276-detected CAFs — conditional on describing them as myCAF-marker-enriched and deeper-sequenced.

**Donor support.** LUAD: 1,676 high cells across 47 donors; programme survives an alternative CAF definition (80% of high calls reproduced). SCLC: **2 donors with ≥10 high cells**; top-3 calls not reproduced. SCLC-specific conclusions are not supportable beyond descriptive.

---

## Panels 4E/S5B — Visium deconvolution and spatial neighbourhood

**Paper claim (CORRECTED).** An **immune-EXCLUDED** niche. Verbatim Figure 4E caption: *"Spatial transcriptomic analyses of LUAD primary-site tissue identifies immune-excluded niches in B7-H3 expressing spots relative to B7-H3 non-expressing spots. Bar plot quantifies the percent change in neighbor immune abundance between top and bottom quartile of B7-H3-expressing spots across 12 LUAD tumor samples. Significance was assessed using a mixed-effects model adjusting for total UMI count, fibroblast abundance, and malignant epithelial abundance fixed effects, with random effects at the sample-level."* Body text: *"B7-H3-high spots exhibited significant depletion of neighboring immune cells such as T cells, macrophages, monocytes, and dendritic cells."* The round-2 delivery characterized this as an "immune-hot" (increased immune abundance) niche. **That was backwards.**

**What this round found — three analyses that must not be rounded to a single verdict.**

1. **Unadjusted absolute abundance — DISAGREES for T and DC, agrees for macrophage, and is confounded[[claim:C132]].** Tumour high-CD276 spots have higher neighbouring T cells (+15.4%, CI 1.1–29.0), B cells (+15.2%), DCs (+28.8%, 9.4–46.9) and neutrophils (+17.3%), and lower endothelial cells (−16.0%); macrophage −7.6% (CI includes 0). These increases track a **~2.03× median-of-medians capture-depth difference** (tumour 7,545.0 vs 3,708.5) and do not survive the paper's adjustment. This is the part of round 2 that disagrees with the paper.

2. **Depth-robust composition — MIXED[[claim:C132]].** With density removed but no covariate adjustment: macrophage (**−0.40 pp**) and monocyte (**−0.23 pp**) deplete in the same direction as the paper; **T cells (+0.11 pp) and dendritic cells (+0.49 pp) are flat-to-up**, which does not match the paper. The dominant axis is malignant +3.79 pp and endothelial −2.03 pp (a tumour-versus-stroma/density axis). NK −0.49 pp, mast −0.24 pp.

3. **The paper-specified adjusted mixed-effects model (adapted) — AGREES for all four named compartments[[claim:C131]].** Reusing the existing per-spot tables (no new Visium pull, no cell2location re-run), the model is: neighbour-mean immune abundance ~ per-section top-vs-bottom-quartile CD276 (rank fallback) + z(log1p(total_counts)) + z(mean_fibroblast) + z(mean_malignant cell) + (1|section), REML `MixedLM`, 12 tumour sections, n = 13,886 spots (6,943 high / 6,943 low), 5 donors. Two adaptations from the paper's description should be read explicitly: grouping is a per-section top-vs-bottom-quartile split with a deterministic rank fallback that in practice becomes a **positive-vs-zero** contrast (see caveats), and the random effect is at the **section** rather than sample level. Results (BH across 9 immune types):

   | Cell type | β | 95% CI | BH q | Adjusted % | Unadjusted % |
   |---|---|---|---|---|---|
   | **T cell** | −0.0164 | −0.0233 to −0.0095 | 5.4e-6 | **−3.22** | +15.37 |
   | B cell | −0.0184 | −0.0260 to −0.0108 | 5.0e-6 | −4.34 | +15.16 |
   | NK cell | −0.0228 | −0.0300 to −0.0157 | 1.5e-9 | −5.46 | +3.81 |
   | **Macrophage** | −0.0252 | −0.0355 to −0.0149 | 5.0e-6 | **−12.00** | −7.58 |
   | **Monocyte/myeloid** | −0.0073 | −0.0115 to −0.0032 | 7.6e-4 | **−3.08** | +2.19 |
   | **Dendritic cell** | −0.0106 | −0.0192 to −0.0021 | 0.0167 | **−3.44** | +28.77 |
   | Mast cell | −0.0197 | −0.0255 to −0.0139 | 2.4e-10 | −5.63 | +8.45 |
   | Neutrophil | +0.00002 | −0.0031 to +0.0031 | 0.988 | +0.01 (null) | +17.27 |
   | Plasma cell | −0.0237 | −0.0338 to −0.0137 | 5.4e-6 | −9.17 | +2.92 |

   **8/9 immune types are significantly depleted after adjustment; all four compartments the paper names (T, macrophage, monocyte/myeloid, dendritic cell) are significantly depleted.** The unadjusted positive signal was a depth confound; the direction reverses under the adjusted model. Evidence: `work/single-cell-analyst/results/tables/visium_correction_mixed_effects_4e.csv`, `.../visium_correction_mixed_effects_4e_sensitivity.csv`, `.../results/reports/visium_correction_mixed_effects_4e_report.md`.

**Lattice caveat (newly disclosed).** The reused neighbourhood logic labels the graph "k=6", but the 2.05-radius graph actually returns **up to 8 neighbours** (4 at 1.414, 4 at 2.0; 68.1% of spots have 8)[[claim:C137]]. The graph is retained for comparability with the source analysis; the complete-ring (`n_neighbours==8`) sensitivity is consistent with the primary adjusted model. The earlier "six-neighbour-only" edge sensitivity is a **partial-ring subset, not an interior-spot subset**, and should be read with that caveat.

**Stats caveats.** Within-section label-shuffle permutations are anticonservative (floor 1/1001). The section bootstrap overstates precision (22 sections, 5 donors/histology). The adjusted model's Wald p-values are anticonservative under spatial autocorrelation and rest on 12 sections / 5 donors — read as strong directional evidence, not calibrated p-values. The adjacent-normal panel is degenerate (median CD276 = 0 in the high group in 8/10 sections) and shows a significant macrophage *increase*; it is not a confirmation. Two further limitations are disclosed in the specialist report[[claim:C133]]: (i) the section random-effect variance is estimated at the boundary (**0 for 7/9 types**; only T cell 0.00492/ICC 0.114 and mast cell 0.00283/ICC 0.095 are non-zero), so those fits behave as OLS with section structure absorbed by the fixed covariates; and (ii) the rank-fallback groups are a **positive-vs-zero contrast** (high group 52–100% CD276-positive; low group 100% zero in all 12 tumour sections), not a true expression-quartile contrast.

**Compute deviation.** Reference model 250 epochs (as paper); spatial mapping 3,000 epochs on CPU vs the paper's 10,000 on an H100 (CUDA blocked by run policy). Convergence diagnostics justify the reduction (99.96% of ELBO decrease by epoch 2,700). Absolute abundances are not directly comparable to the paper's.

---

## Panel 4F — TCGA LUAD survival

**Paper claim.** High CD276 expression is associated with worse overall survival (HR 1.62, 95% CI 1.05–2.48, p = 0.028) and disease-specific survival (HR 1.82, 95% CI 1.06–3.15, p = 0.031) in n = 566.

**What this round found.** (Unchanged from the round-2 delivery; evidence `tcga_luad_cd276_cox_models.csv`, `tcga_luad_cohort_construction.csv`.)[[claim:C139]]
- Unadjusted Q4 vs Q1: OS 1.80 (1.19–2.71), p = 0.0051; DSS 1.86 (1.10–3.13), p = 0.0206.
- Adjusted (age, stage, sex): OS 1.44 (p = 0.106); DSS 1.39 (p = 0.249).
- Sensitivity: stage-adjusted Q4-vs-rest OS 1.45 (p = 0.026) — nominal, not the pre-specified primary contrast.

**Agreement.** **Agree unadjusted; weaker adjusted.** Direction and significance match the paper before adjustment. After adjustment for stage, CD276 is **not an independent prognostic factor** in this cohort on this analysis. The paper does not state whether its HRs are adjusted.

---

## Tahoe-100M and DepMap (target-assessment context)

**Tahoe-100M.** The differential-expression track is **blocked**: all three MCP calls failed with `TAHOE_DATA_PATH not set in environment`; the 82.76 GiB DE payload has no gene→shard manifest and was not bulk-downloaded. Correct reading: **not assessable / no evidence either way** — not "non-material," not evidence of absence. (Unchanged from the round-2 delivery.)[[claim:C139]]

**DepMap.** Round-1 artifacts re-verified 54/54. Mean gene effect **−0.230 in LUAD (n = 46)** and **−0.204 in SCLC (n = 25)**; **1/46 LUAD and 0/25 SCLC** lines below the −0.5 essentiality threshold. Cancer cell lines only. (Unchanged from the round-2 delivery.)

---

## One-line verdict per panel

- **4A:** genetic association — no; regulatory annotation — yes, annotation only; gene constraint — yes (LoF O/E 0.6666 ≈ the paper's 0.67), annotation only.
- **4B/4C:** atlas reproduced; CD276 is not differentially expressed in any of the 15 tested non-fibroblast contrasts (11 primary + 4 paired); the paper's fibroblast claim is untestable here, not refuted.
- **4D/S5A:** ECM/proteolysis enrichment in CD276-detected CAFs, but **not unique** and not depth-matched.
- **4E/S5B:** under the paper-specified adjusted model (adapted grouping/random effect), high-CD276 regions are **immune-excluded** (T, macrophage, monocyte/myeloid, dendritic cell all depleted); the unadjusted "immune-hot" reading was a depth artifact and a mischaracterization.
- **4F:** unadjusted association agrees with the paper; it does **not** survive adjustment for stage.
- **Tahoe/DepMap:** Tahoe inconclusive (blocked); DepMap says CD276 is not essential.
