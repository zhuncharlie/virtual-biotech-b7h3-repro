# Panel-by-Paper Comparison — Round 2 B7-H3 (CD276) Case Study

**Delivery run:** `20261022-010102-round-2-of-the-b7-h3-cd276-case-76d40ca3`
**Analysis run:** `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
**Reference paper:** Virtual Biotech, Figure 4A–F + Supplementary Figure S5A–B (PMC12970349), LUAD and SCLC.

This file is a standalone, number-by-number comparison of what the paper claims and what this round reproduced. It is the source document for the comparison table in `FINAL_REPORT.md` §2. Status labels: **Agree**, **Weaker** (same direction, materially lower strength), **Disagree** (not supported / contradicted), **Inconclusive** (not testable).

---

## Summary table

| Panel | Paper claim | This round | Status |
|---|---|---|---|
| 4A | CD276 has genetic credible-set support and lung regulatory-element links (caption conflates the two; mentions 41 "high-confidence" elements) | Germline 0/8 credible sets, 0/67 L2G. Regulatory 839 CD276-linked lung elements (77 within ±500 kb), 29 at Score ≥ 0.02, promoter 0.973 — annotation only | **Disagree (genetic) / Agree (regulatory, annotation-only)** |
| 4B/4C | LUAD/SCLC single-cell atlas; pseudobulk DE identifies CD276-associated populations | 413,996 cells / 80 donors / 15 types; CD276 0/15 DE contrasts (min padj 0.291) | **Weaker / Disagree on "CD276-associated"** |
| 4D/S5A | Signalling unique to B7-H3+ CAFs (SCLC main, LUAD supp) | Rank-based ECM/proteolysis enrichment; no unique signalling; 55–69% depth gap; SCLC 2 donors | **Weaker / Disagree on "unique"** |
| 4E/S5B | Immune-hot B7-H3 niche around high-CD276 spots | Reproduced only in absolute abundance (depth/edge-confounded); composition signal is malignant enrichment + endothelial/NK/macrophage depletion | **Weaker / Disagree on "immune-hot"** |
| 4F | High CD276 → worse OS (1.62, p = 0.028) and DSS (1.82, p = 0.031), n = 566 | Unadjusted Q4-vs-Q1 OS 1.80 (p = 0.0051), DSS 1.86 (p = 0.021); adjusted OS p = 0.106, DSS p = 0.249 | **Agree unadjusted / Weaker adjusted** |
| Tahoe/DepMap | (target-assessment context) | Tahoe DE blocked — not assessable/no evidence either way; DepMap mean CERES −0.230, 1/46 essential | **Inconclusive / Agree (not essential)** |

---

## Panel 4A — Genetics and regulatory elements

**Paper claim.** Figure 4A presents CD276 as supported by genetics and lung regulatory-element evidence. The caption mixes two evidence types (statistical credible-set/genetic association and regulatory enhancer–gene prediction) and mentions 41 "high-confidence" elements.

**What this round found.**
- **Germline (statistical genetic) stream:** 0 of 8 LUAD+SCLC GWAS studies carry a CD276-locus credible set within ±500 kb (also 0/8 by gene-body overlap and 0/8 by locus-interval overlap); 0 of 67 L2G loci derive from a LUAD or SCLC study. Evidence: `cd276_round2_germline_verification.csv`.
- **Regulatory (E2G) stream:** ENCODE DNase-only lung rE2G predictions link 839 elements to CD276 genome-wide; 77 lie within ±500 kb of the TSS (median distance 241.1 kb); 29 reach the pre-declared Score ≥ 0.02 threshold; the top element is the CD276 promoter itself (Score 0.973, 64.5 bp from TSS). Evidence: `cd276_e2g_within_window_score_distance_summary.csv`.

**Agreement.** The regulatory stream **agrees** that CD276 has strong local regulatory annotation in lung. The genetic stream **disagrees**: there is no credible-set or L2G support in LUAD/SCLC.

**Important distinction.** E2G Score is a regulatory-link score, not a p-value or disease effect. The 0.02 threshold was chosen from the observed score distribution (above the 95th percentile), **not** to reproduce the paper's 41. No number here should be read as "GWAS-supported" or "disease-associated."

**What would close the gap.** A LUAD/SCLC-specific E2G model (the staged file is lung-biosample, DNase-only, with an averaged Hi-C contact track) and an explicit separation of credible-set vs regulatory evidence in the paper's caption.

---

## Panel 4B/4C — Single-cell atlas and pseudobulk DE

**Paper claim.** A LUAD/SCLC single-cell atlas with pseudobulk differential expression identifying CD276-associated populations.

**What this round found.**
- **Atlas:** 413,996 cells, 80 donors, 15 cell types, 61,497 features, after the paper's QC (300–9,000 genes, ≤15% mitochondrial reads, donor-level downsampling to 10,000 cells, library-size normalisation + log1p, 3,000 HVGs, Harmony, UMAP). Evidence: `scrna_cell_donor_audit.csv`, `scrna_panels4bc_report.md`.
- **Differential expression:** CD276 is **not significant in any of 15 primary disease-vs-normal contrasts** (all padj > 0.29; smallest 0.291, SCLC macrophage, log2FC −0.95). Evidence: `scrna_cd276_de_summary.csv`.
- **Detection (not expression change):** highest percentages in fibroblasts (LUAD 30.8% of 3,411 cells; SCLC 35.3% of 244) and normal-lung macrophages (36.5% of 3,011). Evidence: `scrna_cd276_expression_by_celltype.csv`.

**Agreement.** **Weaker / disagree on "CD276-associated."** The atlas is reproduced, but there is no disease-associated CD276 signal in any compartment. Any "CD276+ population" claim would rest on detection prevalence, not differential biology.

**Gap.** Fibroblast disease-vs-normal DE is **not testable** (1 normal donor, 31 cells). This is the compartment most relevant to the CAF question and remains a genuine gap, not a null.

**Caveat.** Several "tumour-up" genes in non-malignant compartments are tumour identity genes (ASCL1/GRP/INSM1 in SCLC; COL1A1/COL3A1 in LUAD) — ambient RNA/doublets, not immune-intrinsic biology.

---

## Panels 4D/S5A — Cell–cell communication (LIANA)

**Paper claim.** Signalling **unique** to B7-H3+ cancer-associated fibroblasts (SCLC in the main figure, LUAD in the supplement).

**What this round found.**
- **Call counts:** SCLC 290 high / 53 low of 4,051 pairs; LUAD 540 / 91 of 5,053.
- **Recurring programme:** THBS2 → CD47 (top call in both diseases, Δ ≈ 0.91–0.92); PLAU → PLAUR/ITGA5/ITGB5/LRP1/IGF2R; SERPINE1 → LRP1/PLAUR; INHBA → ACTR2/ENG (LUAD); SCLC-specific PLTP → ABCA1, MXRA5 → PILRB, WNT5A → FZD3. Evidence: `liana_top_differential_pairs.csv`.
- **Confounding:** the high-vs-low split is detection-based, with a **55–69% detected-gene depth gap**; the high group is also myCAF-marker-enriched (1.43 vs 1.00; donor paired p = 4.8e-7). myCAF/iCAF is a marker-score proxy, not an annotation. Evidence: `liana_caf_depth_audit.csv`, `liana_panels4d_s5a_report.md`.

**Agreement.** **Weaker; disagree on "unique."** Most pairs are shared between groups, and there is no formal between-group test, no FDR, and no depth-matched contrast. The defensible statement is a quantitative, rank-based enrichment of an ECM/proteolysis programme in CD276-detected CAFs — conditional on describing them as myCAF-marker-enriched and deeper-sequenced.

**Donor support.** LUAD: 1,676 high cells across 47 donors; programme survives an alternative CAF definition (80% of high calls reproduced). SCLC: **2 donors with ≥10 high cells**; top-3 calls not reproduced. SCLC-specific conclusions are not supportable beyond descriptive.

---

## Panels 4E/S5B — Visium deconvolution and spatial neighbourhood

**Paper claim.** An immune-hot B7-H3 niche: high-CD276 spots surrounded by increased immune-cell abundance.

**What this round found.**
- **Data:** 22 sections (12 tumour, 10 adjacent-normal), 47,448 spots, E-MTAB-13530 — the paper's actual source. CD276 is zero in ~83% of spots.
- **Stratification:** detection-based, not expression-quantile. Low group = CD276-zero tail; adjacent-normal "high" group is degenerate (median CD276 = 0.0 in 8/10 sections); rank fallback triggered in 22/22 sections. Evidence: `visium_c2l_cd276_stratification_audit.csv`.
- **Absolute abundance:** immune cells rise around high-CD276 tumour spots (T +15%, B +15%, DC +29%, neutrophil +17%, endothelial −16%), but this tracks a ~2× capture-depth difference (tumour median-of-medians 7,545 vs 3,708; 2.03×) and **does not survive restriction to interior spots**. Evidence: `visium_neighborhood_edge_spot_sensitivity.csv`.
- **Composition (percentage points, depth-robust):** malignant +3.79 pp (12/12 sections, 5/5 donors); DC +0.49 (9/12, 4/5); endothelial −2.03 (0/12, 0/5); NK −0.49 (0/12, 0/5); macrophage −0.40; monocyte −0.23; mast −0.24; T-cell fraction +0.11 pp. Evidence: `visium_neighborhood_composition_pp_difference.csv`.

**Agreement.** **Weaker; disagree on "immune-hot."** The qualitative immune-hot pattern is reproduced only in absolute abundance and is confounded by capture depth and edge effects. The donor-concordant composition signal is malignant enrichment and endothelial/NK/macrophage depletion — a tumour-versus-stroma/density axis, not immune recruitment.

**Compute deviation.** Reference model 250 epochs (as paper); spatial mapping **3,000 epochs on CPU** vs the paper's 10,000 on an H100 (CUDA blocked by run policy). Convergence diagnostics justify the reduction (99.96% of ELBO decrease by epoch 2,700), but absolute abundances are not directly comparable to the paper's.

**Statistics caveats.** Within-section label-shuffle permutations are anticonservative (floor 1/1001); the section bootstrap overstates precision (22 sections, 5 donors/histology).

---

## Panel 4F — TCGA LUAD survival

**Paper claim.** High CD276 expression is associated with worse overall survival (HR 1.62, 95% CI 1.05–2.48, p = 0.028) and disease-specific survival (HR 1.82, 95% CI 1.06–3.15, p = 0.031) in n = 566.

**What this round found.**
- **Cohort:** 566 patients confirmed as the study size; 510 have CD276 mRNA; 251 enter the unadjusted Q4-vs-Q1 contrast, 246 the adjusted model. Evidence: `tcga_luad_cohort_construction.csv`.
- **Unadjusted Q4 vs Q1:** OS 1.80 (1.19–2.71), p = 0.0051; DSS 1.86 (1.10–3.13), p = 0.0206. Evidence: `tcga_luad_cd276_cox_models.csv`.
- **Adjusted (age, stage, sex):** OS 1.44 (p = 0.106); DSS 1.39 (p = 0.249).
- **Sensitivity:** stage-adjusted Q4-vs-rest OS 1.45 (p = 0.026) — nominal, not the pre-specified primary contrast.

**Agreement.** **Agree unadjusted; weaker adjusted.** Direction and significance match the paper before adjustment. After adjustment for stage, CD276 is **not an independent prognostic factor** in this cohort on this analysis. The paper does not state whether its HRs are adjusted; an adjusted paper estimate would sit closer to ours (1.44/1.39).

**Why the numbers differ slightly.** (1) analysis-set size (510 expression-available vs 566; 251 in the quartile contrast); (2) adjustment set; (3) quartile cut/expression scale; (4) DSS endpoint derivation. Nothing was tuned to close the gap.

---

## Tahoe-100M and DepMap (target-assessment context)

**Tahoe-100M.** The differential-expression track is **blocked**: all three MCP calls failed with `TAHOE_DATA_PATH not set in environment`; the 82.76 GiB DE payload has no gene→shard manifest and was not bulk-downloaded. Evidence: `tahoe_round2_attempt_log.csv`. Metadata checks succeeded: CD276 is in the 62,710-gene vocabulary (token 2859), and **no B7-H3-targeted agent appears in the 379-drug annotated panel** (12 aliases). Correct reading: **not assessable / no evidence either way** — not "non-material," not evidence of absence.

**DepMap.** Round-1 artifacts re-verified 54/54. Mean gene effect **−0.230 in LUAD (n = 46)** and **−0.204 in SCLC (n = 25)**; **1/46 LUAD and 0/25 SCLC** lines below the standard −0.5 essentiality threshold. Evidence: `round1_depmap_recomputed_group_summary.csv`. Cancer cell lines only.

---

## One-line verdict per panel

- **4A:** genetic — no; regulatory — yes, but annotation only.
- **4B/4C:** atlas reproduced; CD276 is not differentially expressed in any compartment.
- **4D/S5A:** ECM/proteolysis enrichment in CD276-detected CAFs, but **not unique** and not depth-matched.
- **4E/S5B:** immune-hot pattern is a depth/edge artifact; the real composition shift is malignant enrichment + endothelial/immune depletion.
- **4F:** unadjusted association agrees with the paper; it does **not** survive adjustment for stage.
- **Tahoe/DepMap:** Tahoe inconclusive (blocked); DepMap says CD276 is not essential.
