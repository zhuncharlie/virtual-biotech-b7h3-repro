# Panel 4A — CD276 (B7-H3) in LUAD and SCLC: germline credible-set verification and lung E2G regulatory annotation

**Agent:** genomics-analyst, round 2
**LIVE run:** `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
**Revision:** 2 (2026-10-22) — responses to scientific review §1 (interim) and §4.2 (full). See §7 changelog and `results/reports/revision_response_to_reviewer.md`.
**Panel:** Figure 4A (genetics). Two evidence streams, deliberately reported separately.
**Coordinates (GRCh38):** CD276 / ENSG00000103855, chr15:73,683,966–73,714,514; canonical TSS 73,684,383.

I read `config/full_requirements.md` in full before starting. No web search or web fetching was used. All numbers below are recomputed from saved artifacts and are traceable to the tables and logs listed in the artifact index. All scripts resolve their inputs inside this LIVE workspace (`data/raw/`); the one read-only external input (the raw ENCODE-rE2G BED) is identified by path and md5 in §7.2.

---

## 0. The two evidence streams must not be conflated

| Stream | What it measures | Source | What a positive result would mean |
|---|---|---|---|
| **Genetic credible-set support** | Fine-mapped statistical association between a germline variant and a trait, and locus-to-gene assignment | Open Targets / genetics MCP credible sets and L2G | A heritable contribution of the CD276 locus to LUAD/SCLC risk |
| **Regulatory-element / E2G support** | Predicted enhancer–gene links from chromatin accessibility and sequence/activity models in a biosample | ENCODE-rE2G lung predictions (DNase-only) | CD276 is plausibly transcriptionally regulated from nearby elements in lung; **not** evidence of disease association |

The paper's Figure 4A caption mixes these. This report does not.

---

## 1. Germline stream — verify-and-reuse

### 1.1 Recomputed headline claims

| Check | Claim | Recomputed | Round-1 value | Verdict |
|---|---|---|---|---|
| G1 | LUAD+SCLC GWAS studies with a CD276-locus credible set | **0/8** within ±500 kb; **0/8** in gene body; **0/8** even by credible-set locus-interval overlap | 0/8 | verified |
| G2 | L2G predictions derived from a LUAD or SCLC study | **0/67** (`is_luad_or_sclc` True in 0 rows; 0/67 study IDs match the 8 studies) | 0/67 | verified |
| G3 | Number of distinct L2G loci | **67** (65 distinct studies) | 67 | verified |
| G4 | Credible sets in the round-1 queried window | **303** | 303 | verified |
| G5 | GWAS-only credible sets in that window | **123** | 123 | verified |
| G6 | Distinct GWAS studies in that window | **116** | 116 | verified |
| G7 | Credible sets with a lead variant in the CD276 gene body | **65 all types / 41 GWAS** | 41 (GWAS) | verified, clarified |
| G8 | Any LUAD/SCLC study in the expanded ±500 kb window | **0/8** among 1,252 credible sets / 1,106 studies | not tested at this window | new |
| G9 | Round-1 303-row artifact reproducible | **yes** — identical `studyLocusId` set (303/303) | — | new |

Source: `results/tables/cd276_round2_germline_verification.csv`; per-study detail in `results/tables/cd276_round2_per_study_locus_check.csv`.

**G7 note, revised.** The previous G7 note quoted "69 all types / 65 GWAS" for locus-interval overlap without saying which credible-set universe it came from; the reconciliation table simultaneously printed 201/195 for the same word. Both are correct but answer different questions, and the note is now generated from the data rather than typed:

- **201 all types / 195 GWAS** — credible sets whose fine-mapped locus interval overlaps the gene body, within the **full TSS ±500 kb retrieval universe** (`cd276_tss500kb_region_query_round2.parquet`, 1,252 records).
- **69 all types / 65 GWAS** — the same overlap definition restricted to the **round-1 303-row artifact**, i.e. lead variants in chr15:73.5–73.9 Mb only.

The authoritative gene-body locus-overlap sensitivity for the expanded analysis is **201/195**, because it uses every credible set retrieved in ±500 kb. The 69/65 figure is a subset of it. Both rows now carry an explicit `definition` and `source_file` in `results/tables/cd276_round2_credible_set_window_reconciliation.csv`.

The eight studies are the five LUAD studies (GCST90297563, GCST90455522, GCST90134662, GCST008836, GCST004744) and three SCLC studies (GCST004746, GCST90134664, FINNGEN_R12_C3_SCLC_EXALLC); 56 credible sets were retrieved across them. Their nearest chr15 credible set to the CD276 TSS is **4,881,214 bp** away (the 15q25 nicotinic-receptor region). The 0/8 result holds whether "at the locus" is defined by lead-variant position (±500 kb, gene body) or by credible-set locus-interval overlap.

### 1.2 Resolving the 303 / 123 / 116 / 67 ambiguity

The round-1 report mixed counts from **four different definitions**. Recomputation from the saved artifacts (and two independent fresh region queries at ±250 kb and ±500 kb) gives:

| Definition | Window (GRCh38) | Filter | Credible sets, all study types | Distinct studies, all types | GWAS sets | GWAS studies |
|---|---|---|---|---|---|---|
| Round-1 query window | chr15:73,500,000–73,900,000 (TSS −184,383 to +215,617) | lead variant in window | **303** | **286** | **123** | **116** |
| TSS ±250 kb | chr15:73,434,383–73,934,383 | lead variant in window | 599 | 551 | 224 | 203 |
| TSS ±500 kb | chr15:73,184,383–74,184,383 | lead variant in window | 1,252 | 1,106 | 545 | 445 |
| CD276 gene body | chr15:73,683,966–73,714,514 | lead variant in window | 65 | 63 | 41 | 41 |
| TSS ±250 kb (sensitivity) | ±250 kb | credible-set locus interval overlaps window | 138 | 114 | 134 | 113 |
| TSS ±500 kb (sensitivity) | ±500 kb | credible-set locus interval overlaps window | 298 | 203 | 286 | 199 |
| Gene body (sensitivity; full ±500 kb retrieval universe) | gene span | credible-set locus interval overlaps window | 201 | 132 | 195 | 130 |
| Gene body (sensitivity; round-1 303-row universe) | gene span | credible-set locus interval overlaps window | 69 | 60 | 65 | 59 |

Source: `results/tables/cd276_round2_credible_set_window_reconciliation.csv`.

**What each round-1 number actually is:**

- **303** = every credible set of **any study type** whose lead variant lies in the round-1 retrieval window (73.5–73.9 Mb). Breakdown: 123 GWAS, 104 eQTL, 56 sQTL, 16 tuQTL, 4 pQTL. It is **not** a ±500 kb count.
- **123** = the **GWAS-only subset** of the same 303 rows.
- **116** = the number of **distinct GWAS studies** contributing those 123 rows (6 studies contribute more than one credible set; maximum 3).
- **67** = **distinct L2G loci** from the gene-based L2G query. These are a subset of the 123 GWAS credible sets (all 67 IDs are present in the 123; all 67 are GWAS). L2G assigned CD276 as the likely target gene at 67 of the 123 GWAS loci.
- The round-1 **41** is the GWAS-only count of lead variants inside the CD276 gene body. The all-study-type count is 65.
- Locus-interval overlap at the gene body is **201 all types / 195 GWAS** in the full ±500 kb retrieval (the value used in §1.2 and in the revised G7 note) and **69 / 65** when the same definition is applied only to the round-1 303-row artifact. The difference is the source universe, not conflicting arithmetic: fine-mapped intervals span megabases, so expanding the retrieval adds many sets whose lead variant lies outside the gene but whose interval crosses it.

An independent re-query of TSS ±250 kb restricted to 73.5–73.9 Mb returned exactly the same 303 `studyLocusId`s as the round-1 artifact — no missing or extra loci. The expanded queries (599 rows at ±250 kb; 1,252 at ±500 kb) are consistent with the round-1 retrieval being complete for its stated window and simply narrower than ±250 kb.

**Why the ±250/±500 kb counts are larger than 303:** the analysis window, not the gene, determines the count. The 73.5–73.9 Mb round-1 window excludes dense eQTL/sQTL tracks that begin just outside it. The pre-declared primary definitions in this report are the **lead-variant position** definitions (a lead variant inside the gene body, or within ±500 kb); locus-interval overlap is reported only as a sensitivity because fine-mapped locus intervals here can span several megabases and overstate proximity to CD276.

**Trait composition caveat (two places where round 1 over-stated).**

- Of the 41 gene-body GWAS credible sets, only **13/41** carry a trait label in the saved artifacts (ALT, AST, AST/ALT ratio, GGT, SHBG); the other 28 are unlabelled. Numerator definition: rows whose `studyId` maps to a non-null `trait_resolved` in the round-1 L2G table (all 41 studyIds are present in that table); denominator: the 41 GWAS credible sets with a lead variant in the gene body. Per-label counts: `results/tables/cd276_gwas_trait_label_audit.csv`. The defensible claim is narrower: **none of the 41 belongs to any of the 8 LUAD/SCLC studies**.
- Of the 67 L2G loci, only **17/67** carry a trait label (ALT, AST, GGT, AST/ALT ratio, SHBG, BMI); the remaining 50 study IDs are unlabelled. Numerator definition: L2G rows with non-null `trait_resolved`; denominator: all 67 L2G loci. Per-label counts: `results/tables/cd276_gwas_trait_label_audit.csv`. None of the 8 LUAD/SCLC study IDs appears. Round 1's statement that all 67 "come from biomarker/other-trait GWAS" is not fully verifiable from its saved table, although the annotated subset is consistent with it.

These are corrections to round-1 wording, not to its conclusion: the disease-matched negative result rests on study IDs, not on trait labels.

### 1.3 Interpretation and limits of the negative result

- The genetics database stores fine-mapped/curated credible sets, not genome-wide summary statistics. "0/8" means **no CD276-locus credible set in the queried data** for the largest available LUAD/SCLC GWAS; it does not exclude a sub-threshold or non-fine-mapped association. This limitation is unchanged from round 1.
- The 67 L2G loci are real but disease-mismatched: none is one of the eight LUAD/SCLC studies, and the 17 with trait labels are liver-enzyme/SHBG/BMI traits. Their high scores (56 ≥ 0.5; maximum 0.953, ALT levels) show CD276 is a strong effector gene at a pleiotropic biomarker/other-trait locus, **not** a LUAD/SCLC causal gene. Trait labels are unavailable for 50/67 loci in the saved table.
- There is no disease-QTL colocalization to report for LUAD/SCLC because neither disease has a GWAS locus at CD276 (round-1 QTL table: `cd276_qtl_colocalization_summary.csv`).
- **Conclusion of stream 1:** genetic credible-set support for CD276 as a LUAD or SCLC causal target is **ABSENT** in the queried genetics database.

---

## 2. Regulatory stream — ENCODE-rE2G lung elements at CD276 (new)

### 2.1 Input and filtering

- File: `ENCFF459TXD_lung_e2g_predictions.bed.gz` (dataset **ENCSR985HNP**, DNase-only full predictions, biosample **lung**).
- Size scanned: **8,609,407** data rows. No web access; the staged file was the only input.
- Selection A (**gene-linked**): `TargetGeneEnsemblID == ENSG00000103855` → **839** element–gene link records (839 distinct elements).
- Selection B (**locus-overlapping**): element interval overlaps **chr15:73,184,383–74,184,383** (TSS ±500 kb) → **6,570** link records but only **77 distinct elements** (each element is linked to many target genes in this file).
- All **77** locus-overlapping elements are also CD276-linked; 6 lie inside the CD276 gene body.
- The file's `class` field uses three categories — **promoter / genic / intergenic** — and contains no `enhancer` or `intronic` label. I report the file's own taxonomy and did not reclassify elements; "genic" includes intragenic non-promoter elements.

**Delivered tables and their filters (revision 2).** Every table now states its filter in a `filter` column, so the 77-element distribution can be re-derived without re-parsing the 8.6 M-row BED:

| Table | Rows | Filter |
|---|---|---|
| `results/tables/cd276_e2g_regulatory_elements.csv` | 7,332 | union of the two selections (839 CD276-linked + 6,570 locus-overlapping, 77 in both) |
| `results/tables/cd276_e2g_cd276_linked_all_839.csv` | 839 | `TargetGeneEnsemblID == ENSG00000103855`, all distances |
| `results/tables/cd276_e2g_within_500kb_77_elements.csv` | 77 | CD276-linked **and** element overlaps TSS ±500 kb |
| `results/tables/cd276_e2g_within_window_score_distance_distribution.csv` | 77 | same as above; one row per element with score, distance, class |
| `results/tables/cd276_e2g_within_window_score_distance_summary.csv` | 11 metrics | n, score median/min/max, distance median/min/max, filter, source path/md5/size |

The 7,332-row union table is the primary delivered element table; the 29-row **CD276-linked Score ≥ 0.02** subset mentioned in §2.2 is a threshold view of it, not the delivered table itself. Metrics are in `results/tables/cd276_e2g_summary.csv`; parsing log in `data/processed/cd276_e2g_parse_log.txt`.

### 2.2 Results

**The 839 CD276-linked records genome-wide are mostly distal, low-score candidate links** (median distance to TSS **2.81 Mb**; range 64.5 bp–4.99 Mb; 762/839 lie outside ±500 kb). This is expected for a "full predictions" file, which enumerates candidate links rather than only high-confidence ones. The biologically local set is the **77 elements within ±500 kb** (median distance **241,123 bp = 241.1 kb**; range 64.5 bp–496,317.5 bp).

Both §2.2 distribution statistics are stored, not just computed in prose: `results/tables/cd276_e2g_within_window_score_distance_distribution.csv` contains all 77 per-element score and distance values with the exact filter, and `results/tables/cd276_e2g_within_window_score_distance_summary.csv` records n = 77, score median 0.014308 (min 0.001196, max 0.973456), distance median 241,123 bp (min 64.5, max 496,317.5). The all-839 statistics are in `results/tables/cd276_e2g_summary.csv` (metrics `CD276_linked__score_*` and `CD276_linked__distanceToTSS_*`).

| Quantity | Value |
|---|---|
| CD276-linked elements, all distances | 839 |
| CD276-linked elements within TSS ±500 kb | **77** |
| … inside CD276 gene body | 6 |
| … `isSelfPromoter = TRUE` | **1** (chr15:73683537–73685152, score 0.973) |
| Within-window class breakdown | promoter 17, genic 31, intergenic 29 |
| Within-window score median (range) | 0.0143 (0.0012–0.9735) |
| All-839 score median / 95th / 99th / max | 0.00157 / 0.01485 / 0.1062 / 0.9735 |
| Distinct locus-window elements with ≥1 E2G link (to any gene) at Score ≥ 0.1 / 0.05 / 0.02 | 24 / 38 / **49** |
| Distinct locus-window elements with a **CD276 link** at Score ≥ 0.1 / 0.05 / 0.02 | **9 / 16 / 29** |
| CD276-linked elements at any distance at Score ≥ 0.1 / 0.05 / 0.02 / 0.01 / 0.005 | **9 / 16 / 29** / 78 / 122 |

All 29 CD276-linked elements with Score ≥ 0.02 lie within ±500 kb; no high-scoring link is distal. At the primary threshold the within-window class split is intergenic 17, genic 10, promoter 2.

**Top CD276-linked elements (within ±500 kb):**

| Element | Class | isSelfPromoter | Distance to TSS (bp) | Score |
|---|---|---|---|---|
| chr15:73683537-73685152 | promoter | TRUE | 64.5 | 0.9735 |
| chr15:73697023-73697523 | genic | FALSE | 12,993 | 0.9724 |
| chr15:73700174-73700674 | genic | FALSE | 16,144 | 0.6460 |
| chr15:73685317-73686251 | genic | FALSE | 1,504 | 0.3872 |
| chr15:73631940-73634003 | promoter | FALSE | 51,308.5 | 0.2828 |
| chr15:73922244-73923494 | genic | FALSE | 238,589 | 0.2400 |
| chr15:73704402-73705228 | genic | FALSE | 20,535 | 0.2149 |
| chr15:73691281-73692012 | genic | FALSE | 7,366.5 | 0.1424 |
| chr15:73636323-73636903 | intergenic | FALSE | 47,667 | 0.1169 |
| chr15:73677033-73677533 | intergenic | FALSE | 6,997.5 | 0.0888 |

**Pre-declared primary threshold: Score ≥ 0.02.** It was chosen from the observed distribution, not from the paper: it lies above the 95th percentile of the CD276-linked score distribution (0.01485) and separates the upper tail from the bulk (median 0.00157). Score ≥ 0.05 and ≥ 0.1 are reported as stricter sensitivity thresholds; Score ≥ 0.01 and ≥ 0.005 as looser ones. The paper's mention of 41 "high-confidence" elements was **not** used as a calibration target; none of our threshold counts (9, 16, 29 linked; 24, 38, 49 locus elements) was selected to match it.

### 2.3 What this stream does and does not show

**It shows:** the CD276 promoter and multiple intragenic/intergenic lung elements are predicted, by an ENCODE DNase-only rE2G model, to regulate CD276. The strongest link is the CD276 promoter itself (Score 0.973, 64.5 bp from the TSS), followed by two intragenic elements with Scores ~0.97 and ~0.65. This is consistent with CD276 being transcriptionally active and locally regulated in lung tissue.

**It does not show:** any association with LUAD or SCLC, any causal variant, or any disease-specific regulatory mechanism. The file is a **DNase-only, lung-biosample prediction of enhancer–gene links**; it has no tumor/normal contrast and no genetic association statistic. E2G Score is a regulatory-link score, not a p-value or effect size. Elements marked here must not be described as "GWAS-supported" or "disease-associated."

**Specific limitations:**
1. DNase-only activity model. Where contact information enters the score, it comes from an **average Hi-C track** (`3DContactAvgHicTrack2.Feature`), not from lung-specific Hi-C/capture-HiC data.
2. One biosample (lung), not LUAD- or SCLC-specific.
3. "Full predictions" enumerate candidate links; 762/839 CD276-linked candidates are >500 kb away and mostly very low score.
4. Class labels are promoter/genic/intergenic; there is no explicit enhancer or intronic annotation to report.
5. No producer-recommended score threshold is encoded in the staged file; our 0.02 is an analysis choice, fully reported with sensitivities.

---

## 3. Figure 4A

`results/figures/fig4a_genetics_e2g_cd276.png` (and `.pdf`).

- **A** — CD276 gene model with TSS and ±250/±500 kb boundaries.
- **B** — the 77 lung E2G elements targeting CD276 within ±500 kb, plotted by genomic position and Score (log scale), coloured by class, filled if Score ≥ 0.02, star for the self-promoter. Annotated with threshold counts. Labelled **"regulatory annotation — not a genetic association."**
- **C** — the 1,252 fine-mapped credible-set lead variants within ±500 kb, one row per study type, with per-type counts. Labelled **"statistical genetic association — 0/8 LUAD+SCLC GWAS studies; 0/67 L2G loci."**
- **D** — score distribution of all 839 CD276-linked candidate elements with the pre-declared thresholds.

The two marks types are visually distinct (E2G = coloured points/stems in B; credible sets = grey/coloured rug in C) and separately labelled.

---

## 4. Bottom line for panel 4A

1. **Germline genetic credible-set support for CD276 in LUAD/SCLC: ABSENT.** 0/8 studies with a CD276-locus credible set (verified under lead-variant and locus-overlap definitions), 0/67 disease-matched L2G loci, no disease QTL colocalization. The locus is a genuine pleiotropic biomarker locus, not a lung-cancer locus, in this database.
2. **Lung regulatory E2G support: PRESENT but annotation-only.** 77 CD276-linked elements within TSS ±500 kb; 29 at the primary Score ≥ 0.02 threshold; a strong self-promoter link and several intragenic links.
3. **The two are not interchangeable.** Figure 4A should present them as separate evidence types, exactly as the figure does. Any statement that CD276 has "genetic support" in LUAD/SCLC from E2G data would be wrong.

---

## 5. Errors, failed attempts and fixes

| # | Error / issue | Fix | Outcome |
|---|---|---|---|
| 1 | `AttributeError: in_CD276_gene_body` when reading the round-1 parquet — derived columns exist only in the CSV, not the parquet | recomputed gene-body and distance flags from `position` and the fixed GRCh38 coordinates | success; counts matched the CSV (65 all types / 41 GWAS) |
| 2 | `FileNotFoundError` reading `cd276_tss250k_region_query_round2.parquet` — filename typo (250k vs 250kb) after a successful MCP query | corrected path; verified file existed | success |
| 3 | First figure render: `set_xticks` was given Mb values (73.2…) on a base-pair axis, which expanded the axis to ~74 million and collapsed all data to the right edge | switched ticks to base-pair values with Mb labels | success; locus rendered correctly |
| 4 | Expected `enhancer`/`intronic` class labels in the E2G file; the file actually uses promoter/genic/intergenic | reported the file's own taxonomy; no speculative reclassification | documented in §2.1 |
| 5 | Fresh ±250 kb query returned 599 rows, not the round-1 303 | determined the tool filters on lead-variant position; demonstrated 303 is the 73.5–73.9 Mb subset and that the ID sets are identical | resolved; added to reconciliation table |

All MCP calls succeeded; no query failures. No packages were installed.

---

## 6. Artifact index

| Artifact | Contents |
|---|---|
| `results/tables/cd276_round2_germline_verification.csv` | 9 verification checks (G1–G9) with source file, exact filter, recomputed vs round-1 value |
| `results/tables/cd276_round2_credible_set_window_reconciliation.csv` | counts for every window/definition (303 / 599 / 1,252 / 65 / sensitivity locus-overlap) |
| `results/tables/cd276_round2_per_study_locus_check.csv` | per-study credible sets, chr15 counts, minimum distance, gene-body/±250/±500 kb and locus-overlap flags |
| `results/tables/cd276_e2g_regulatory_elements.csv` | all 7,332 union E2G rows with coordinates, class, Score, distance, locus flags and a `filter` column |
| `results/tables/cd276_e2g_cd276_linked_all_839.csv` | 839 CD276-linked elements, all distances, with `filter` column |
| `results/tables/cd276_e2g_within_500kb_77_elements.csv` | 77 CD276-linked elements within TSS ±500 kb, with `filter` column |
| `results/tables/cd276_e2g_within_window_score_distance_distribution.csv` | per-element score and distance for all 77 within-window elements, with the exact filter |
| `results/tables/cd276_e2g_within_window_score_distance_summary.csv` | n, score and distance median/min/max for the 77-element set, plus source path and md5 |
| `results/tables/cd276_gwas_trait_label_audit.csv` | per-label counts for 41 gene-body GWAS credible sets, 65 all-type gene-body sets, and 67 L2G loci, with numerator/denominator definitions |
| `results/tables/cd276_e2g_summary.csv` | 102 metrics: counts, class breakdowns, score quantiles, threshold counts, top elements, stored within-window medians, source md5 |
| `results/figures/fig4a_genetics_e2g_cd276.png` / `.pdf` | panel 4A figure |
| `data/raw/cd276_tss250kb_region_query_round2.parquet` | MCP region query, TSS ±250 kb (599 rows); md5 `9afbe0130027c45446e0703f8cd234d9` |
| `data/raw/cd276_tss500kb_region_query_round2.parquet` | MCP region query, TSS ±500 kb (1,252 rows); md5 `35b2391a1aa01a4f1dc7ad11ae40e6a6` |
| `data/raw/cd276_locus_credible_sets_all_studies.parquet` | round-1 303-row credible-set artifact; md5 `091237fe47df4900f908b8d8000a43ee` |
| `data/raw/round1_per_study/*.parquet` | eight LUAD/SCLC per-study credible-set pulls |
| `data/raw/cd276_l2g_predictions.csv` | round-1 L2G table (67 loci); md5 `061f8c8cf6aafeb5f2c0ef05a2d907b3` |
| `data/processed/cd276_round2_germline_verification_log.txt` | full recomputation log |
| `data/processed/cd276_e2g_parse_log.txt` | full E2G parsing and summary log |
| `code/scripts/01_verify_germline_cd276.py` | germline verification and reconciliation script |
| `code/scripts/02_parse_encode_re2g_cd276.py` | E2G parser and summariser |
| `code/scripts/03_fig4a_genetics_e2g_cd276.py` | figure script |
| `code/scripts/04_validate_panel4a_outputs.py` | consistency checks (fails on any mismatch) |
| `code/scripts/05_trait_label_audit_cd276.py` | trait-label audit and reconciliation of 13/41 and 17/67 |

---

## 7. Revision 2 changelog (2026-10-22)

This revision responds to the interim review §1 and the full review §4.2. No new database query was run, no package was installed, and no conclusion changed. Every corrected number is recomputed by the scripts in `code/scripts/` from files listed in §7.2.

| # | Item | Previous state | Revision 2 state | Evidence |
|---|---|---|---|---|
| 1 | G7 locus-interval note | Note said "69 all types / 65 GWAS" with no definition, beside a reconciliation table that said 201/195. The literal was hardcoded in script 01. | Both are correct but answer different universes. G7 note is now computed and states: round-1 303-row universe = **69 all types / 65 GWAS**; full TSS ±500 kb retrieval = **201 all types / 195 GWAS**; primary lead-variant-in-gene-body = **65 all types / 41 GWAS**. Reconciliation table has 8 rows with explicit `definition` and `source_file`. | `results/tables/cd276_round2_germline_verification.csv` G7; `results/tables/cd276_round2_credible_set_window_reconciliation.csv` rows 5–6; `data/processed/cd276_round2_germline_verification_log.txt` |
| 2 | Within-window distributions | "median score 0.0143 (range 0.0012–0.9735)" and "median distance 241 kb" existed only in prose. | Stored per element for all 77: score median **0.0143083** (min **0.0011955**, max **0.9734559**); distance median **241,123 bp = 241.1 kb** (min 64.5, max 496,317.5 bp). Values are unchanged from the prose; they are now re-derivable. | `results/tables/cd276_e2g_within_window_score_distance_distribution.csv`; `results/tables/cd276_e2g_within_window_score_distance_summary.csv` |
| 3 | Trait-label counts | "13/41" and "17/67" appeared only in prose / free-text note. | Per-label counts with numerator and denominator definitions: gene-body GWAS credible sets labelled **13/41** (ALT 4, GGT 5, AST 1, AST/ALT 1, SHBG 1, GGT [synonym] 1; 28 unlabelled); L2G loci labelled **17/67** (50 unlabelled). Both claims reproduce exactly. | `results/tables/cd276_gwas_trait_label_audit.csv`; `data/processed/cd276_trait_label_audit_log.txt` |
| 4 | E2G element table filtering | The review reported the delivered table as a 29-row Score ≥ 0.02 subset, which would make the 77-element distribution non-re-derivable. | The delivered union table is **7,332 rows**; explicitly filtered deliverables are now also written: **839** CD276-linked rows and **77** within-window rows, each with a `filter` column; the 77-row distribution is separately stored. The 29 rows are the CD276-linked Score ≥ 0.02 threshold subset, not the delivered table. | `results/tables/cd276_e2g_regulatory_elements.csv`; `..._cd276_linked_all_839.csv`; `..._within_500kb_77_elements.csv`; `data/processed/cd276_e2g_parse_log.txt` |
| 5 | Script provenance | Scripts 01–04 hardcoded `20261021-080518-…` as BASE; script 01 also read round-1 inputs from an external run path. | All scripts now resolve BASE as `parents[2]` of their own file, so they run from this LIVE workspace. Round-1 and round-2 inputs were copied into `data/raw/` (md5 below). Only the 321 MB raw ENCODE-rE2G BED remains a read-only external input, with path and md5 recorded in §7.2 and in `cd276_e2g_summary.csv`. | `code/scripts/01…05`; `data/processed/cd276_e2g_parse_log.txt` |

### 7.1 What did not change

The primary verdicts are unchanged: **0/8** LUAD+SCLC studies have a CD276-locus credible set; **0/67** L2G loci derive from a LUAD/SCLC study; **77** lung E2G elements target CD276 within ±500 kb, **29** at Score ≥ 0.02. Item 1 refines a sensitivity definition; items 2–4 make existing numbers citable; item 5 makes the scripts portable.

### 7.2 Data provenance and md5

| Input | Role | md5 |
|---|---|---|
| `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/data/encode_e2g/ENCFF459TXD_lung_e2g_predictions.bed.gz` | raw ENCODE-rE2G DNase-only lung predictions (ENCSR985HNP), 8,609,407 data rows, 321,602,896 bytes; read-only shared input | `3b4198cdb65f7011e5535f1a94574496` |
| `data/raw/cd276_tss250kb_region_query_round2.parquet` | TSS ±250 kb credible-set query (599 rows), copied from SOURCE run `20261021-113551-…-ef6e8b35` | `9afbe0130027c45446e0703f8cd234d9` |
| `data/raw/cd276_tss500kb_region_query_round2.parquet` | TSS ±500 kb credible-set query (1,252 rows), copied from SOURCE run `…-ef6e8b35` | `35b2391a1aa01a4f1dc7ad11ae40e6a6` |
| `data/raw/cd276_locus_credible_sets_all_studies.parquet` | round-1 303-row credible-set artifact, copied from run `20261020-085513-…` | `091237fe47df4900f908b8d8000a43ee` |
| `data/raw/cd276_l2g_predictions.csv` | round-1 L2G table (67 loci), copied from run `20261020-085513-…` | `061f8c8cf6aafeb5f2c0ef05a2d907b3` |

The SOURCE run `20261021-113551-…-ef6e8b35` was read only; nothing in it was modified. The two query parquets were copied byte-for-byte, so their md5 values match SOURCE.
