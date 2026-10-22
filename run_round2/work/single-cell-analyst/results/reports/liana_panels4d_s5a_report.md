# LIANA cell–cell communication in B7-H3-high vs B7-H3-low CAFs
## Panels 4D (SCLC, main) and S5A (LUAD, supplementary)

Original computation run: `20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35` (SOURCE)
Corrected report written in: `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8` (LIVE)
Revision: **2** (prose and provenance corrections after scientific review; no LIANA run,
model or result value was changed)
Agent: single-cell-analyst (LIANA track only; no visium/cell2location files touched)
Analysis date: 2026-10-21
Software: liana 1.7.0, Python 3.11 (env `vbt`)

### Revision 2 changelog

| # | Old statement (Revision 1) | Corrected statement | Supporting table / column |
|---|---|---|---|
| 1 | "Enriched_low is dominated by CXCL12 → CXCR3/ITGA5/ITGAV" | CXCR3 **is** present, but is not dominant: the leading SCLC low calls are CXCL12 → ITGA5 (neutrophil, Δ −0.81), → CD4 (T cell, Δ −0.24), → ITGAV (mast cell, Δ −0.19). CXCR3 calls rank 11/53 (B cell) and 22/53 (T cell). | `liana_pair_level_comparison_sclc.csv` (`receptor_complex`, `delta_specificity_rank`, `differential_call`); `liana_cxcl12_pairs.csv` |
| 2 | Pair arithmetic stated as "3,564/4,051 shared and 486 high-only; 4,041/5,053 shared and 970 high-only" without reconciliation | Explicit inclusion–exclusion: SCLC 3,564 shared + 486 high-only + 1 low-only = 4,051; LUAD 4,041 + 970 + 42 = 5,053 | `liana_pair_status_counts.csv` (`shared`, `high_only`, `low_only`, `reconciled_sum`); `liana_caf_source_group_counts.csv` |
| 3 | "a/b/c collapse to the same split in SCLC" | Only a and b are identical (43 high / 201 low). c is 43 high / 158 low; the 43 CD276 = 1 cells are high in c, low in a/b, and **unassigned** in c | `liana_b7h3_caf_definition.csv` (`high_cells`, `low_cells`) |
| 4 | Fibroblast subtype imbalance not mentioned | Added marker-score proxy and explicit limitation: LUAD high group is myCAF-marker-high (1.43 vs 1.00, donor paired p = 4.8e-7, n = 22) and anatomically skewed (62.8% vs 44.1% "fibroblast") | `liana_caf_subtype_check.csv`, `liana_caf_subtype_check_tests.csv` |
| 5 | "the SCLC universe `.h5ad` from the interrupted run is 0 bytes/truncated and was not used" | The SOURCE and earlier R0 universes are **intact** (1,414,231,381 bytes, md5 `5492f9a7…`, 29,178 × 61,497). The only 0-byte copy is in abandoned run `20261021-103545-…-3c05f9f0`. No SCLC result was lost; the raw parquet is intact and the universe is deterministically reconstructible | `ls -l` / `md5sum` of the two universe files; `liana_run_log.csv` (`universe_h5ad`) |
| 6 | Scripts carried hardcoded paths to SOURCE/R0; report cited only relative paths | Scripts re-pointed to LIVE for outputs and to explicit SOURCE paths for read-only inputs; SOURCE paths and md5s recorded in §10 | `code/scripts/01…06` (ROOT/SRC_ROOT), §10 "Reproduction and external inputs" |
| 7 | Caveats stated but not consolidated | Re-checked and kept, not softened: detection-based (not quantile) split, 55–69% detected-gene depth gap, 2-donor SCLC limitation, no formal between-group test | §1, §6, §8, §9 |

---

## 1. Data and group definitions

Input atlas (read-only SOURCE):
`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/single-cell-analyst/data/processed/scrna_luad_sclc_integrated.h5ad`
(5,699,624,838 bytes; md5 `57c86760d9eaebce5f75cb69768e0cab`; 413,996 cells, 80 donors,
15 cell types; `layers['counts']`, log-normalised `.X`, `obsm['X_harmony']`).
Panels 4B/4C were completed previously and are not repeated here.

| Disease | Disease cells | Fibroblast-labelled cells | Datasets |
|---|---:|---:|---:|
| SCLC | 29,178 | 244 | 1 |
| LUAD | 373,176 | 7,022 | 2 |

**Primary CAF definition (pre-registered, `results/tables/liana_b7h3_caf_definition.csv`,
written 14:48:41–58Z, before any LIANA run):**

- `CAF_B7H3_high` = fibroblast with CD276 **raw count > 0**
- `CAF_B7H3_low` = fibroblast with CD276 **raw count == 0**

| Disease | High cells (donors; donors with ≥10 high cells) | Low cells (donors; ≥10 low cells) | Fraction high |
|---|---:|---:|---:|
| SCLC | 86 (7; **2**) | 158 (9; 4) | 35.3% |
| LUAD | 1,676 (47; 22) | 5,346 (58; 45) | 23.9% |

The split is **detection-based, not expression-quantile-based**: Q25 and Q75 of CD276 are 0
in both diseases (SCLC median 0, Q75 1; LUAD median 0, Q75 0), so any quartile split would
place all CD276-zero cells in the bottom group. Three sensitivity definitions (a: > median of
CD276-positive cells; b: > Q75; c: quartile split with empty-bottom fallback) were pre-specified
in the same table before LIANA output existed.

**Cell universe (pre-registered in `results/tables/liana_pre_registered_filters.csv`):**

- **SCLC:** the full disease atlas, all 29,178 cells, 11 `liana_group` levels:
  epithelial 24,254; T 3,767; DC 289; macrophage 212; B 200; endothelial 169;
  CAF_low 158; CAF_high 86; mast 29; neutrophil 7; plasma 7.
- **LUAD:** all 7,022 disease fibroblasts + a fixed-seed (42) sample of at most 1,500
  non-fibroblast cells per cell type. This gives 25,162 cells and 16 `liana_group` levels:
  CAF_low 5,346; CAF_high 1,676; 12 non-fibroblast types at 1,500 each; neutrophil 128;
  erythrocyte 12. This is the **documented deviation** from the full 373,176-cell atlas.
  Script `03_liana_run.py` implements exactly this rule (verified by the logged universe
  count and group sizes). The universe `.h5ad` written by the run is
  `data/processed/liana/liana_LUAD_universe.h5ad` (651,265,125 bytes; md5
  `74b2443fa241338d88b826bfebb49d50`). The SCLC universe in SOURCE is **intact**:
  `data/processed/liana/liana_SCLC_universe.h5ad`, 1,414,231,381 bytes, md5
  `5492f9a728a02a5a120ff0ee9ec193e4`, 29,178 cells × 61,497 genes, valid HDF5. A 0-byte
  file with the same name exists only in the abandoned run
  `20261021-103545-round-2-of-the-b7-h3-cd276-case-3c05f9f0` and was never used. No SCLC
  result depends on it: the raw output (`liana_raw_sclc.parquet`, 25,028 rows, md5
  `bc460cd8e9e52bdd3c37202dda59d121`) is intact and matches the provenance copy, and the
  universe is deterministically reconstructible from the atlas with the rule in
  `03_liana_run.py`. (Revision 1 said the SCLC universe was 0 bytes/truncated; that was
  wrong for SOURCE and R0 — see Revision 2 changelog item 5.)

---

## 2. LIANA methods and filters

Identical parameters for both diseases:

- `liana.mt.rank_aggregate`, resource `consensus`, `aggregate_method='rra'`
- 5 constituent methods: CellPhoneDB, Connectome, log2FC, NATMI, SingleCellSignalR
- `expr_prop=0.1`, `min_cells=5`, `n_perms=1000`, `seed=1337`, `n_jobs=32`
- input layer: `.X` (log-normalised), `use_raw=False`, `layer=None`
- SCLC: 25,028 rows × 13 columns, 1,655 ligand–receptor pairs, 0.86 min LIANA time
  (md5 `bc460cd8e9e52bdd3c37202dda59d121`, identical to the provenance copy in
  `data/raw/provenance_interrupted_run/`)
- LUAD: 37,684 rows × 13 columns, 1,479 ligand–receptor pairs, 0.80 min LIANA time.
  The run wrote its parquet successfully but the final `append_log()` raised
  `pandas.errors.EmptyDataError` because the carried-over `liana_run_log.csv` was 0 bytes.
  The log-writing bug was fixed (0-byte files are now skipped) and the LUAD log row was
  reconstructed from the run log and output parquet; no LIANA result was altered.

**Pre-specified filters (identical for both diseases):**

1. `specificity_rank <= 0.1` (top decile of the LIANA consensus RRA specificity score,
   0 = most specific).
2. `cellphone_pvals < 0.01` (CellPhoneDB permutation p-value, 1,000 permutations).
3. `n_methods_finite_rank >= 3` (at least 3 of the 5 methods have a finite score).

**Differential rule:** `enriched_high` = the high side passes all three filters, the low side
does not, and `specificity_rank_high < specificity_rank_low`; symmetric for `enriched_low`;
otherwise `both_pass` or `neither`. The unit is a unique
(target cell type, ligand complex, receptor complex) pair.

**Important implementation result:** in both diseases filters 2 and 3 removed **zero** rows
among top-decile CAF-source interactions, and all five method scores were finite for every
retained row. Therefore the only discriminating filter is the specificity-rank filter.
This was anticipated in the pre-registered CSV for the ≥3-method rule but not for the
p-value rule: `cellphone_pvals` is rounded to 3 decimal places and 64% of all raw rows are
exactly 0, so `p < 0.01` cannot separate the top-decile interactions.

There is **no multiple-testing correction and no formal high-vs-low statistical test**.
The differential call is a comparison of two RRA specificity ranks, not a hypothesis test.

---

## 3. Filter cascade

| Disease | Step | Interactions | % of all CAF-source |
|---|---|---:|---:|
| SCLC | 0 all CAF-source | 7,615 | 100.00 |
| SCLC | 1 top-decile specificity rank | 2,387 | 31.35 |
| SCLC | 2 p < 0.01 | 2,387 | 31.35 |
| SCLC | 3 ≥3 finite methods | 2,387 | 31.35 |
| LUAD | 0 all CAF-source | 9,094 | 100.00 |
| LUAD | 1 top-decile specificity rank | 3,931 | 43.23 |
| LUAD | 2 p < 0.01 | 3,931 | 43.23 |
| LUAD | 3 ≥3 finite methods | 3,931 | 43.23 |

Split by source group after all three filters:

| Disease | High-source survivors | Low-source survivors |
|---|---:|---:|
| SCLC | 1,312 / 4,050 (32.4%) | 1,075 / 3,565 (30.2%) |
| LUAD | 2,190 / 5,011 (43.7%) | 1,741 / 4,083 (42.6%) |

The survival rates are similar between groups; the differential calls are driven by **where**
the interaction ranks, not by a large difference in the number of interactions that pass.

An independent audit (`04b_liana_cascade_audit.py`) recomputed each step from the raw parquet
without calling the processing functions: every step is a strict subset of the previous one,
every count matches the reported cascade, and the two non-discriminating filters are confirmed
(`results/tables/liana_cascade_audit.csv`).

---

## 4. Differential results

### 4.1 SCLC (Panel 4D)

4,051 unique target–LR pairs compared: **290 enriched_high** (7.2%), **53 enriched_low**
(1.3%), 1,022 both_pass (25.2%), 2,686 neither (66.3%).

63/290 high calls (21.7%) have **no low-side row at all** (the pair was not detected in the
low group at `expr_prop=0.1`); 0/53 low calls lack a high-side row. Median |log2(lr_means
high/low)| is 0.46 for high calls and 0.18 for low calls: the rank differences are much
larger than the expression differences.

Top enriched_high (all pass all three filters; Δ = rank_low − rank_high, >0 = higher in high):

| Rank | Target | Ligand → receptor | Δ rank | rank high | rank low | p high | p low | lr_means high/low | log2FC |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | mast cell | THBS2 → CD47 | 0.922 | 0.0776 | 1.000 | 0 | 0.062 | 0.729 / 0.518 | 0.49 |
| 2 | plasma cell | PLAU → IGF2R | 0.914 | 0.0855 | 1.000 | 0 | 0.009 | 0.443 / 0.282 | 0.65 |
| 3 | plasma cell | PLTP → ABCA1 | 0.878 | 0.0527 | 0.930 | 0 | 0.002 | 0.500 / 0.336 | 0.57 |
| 4 | plasma cell | MXRA5 → PILRB | 0.768 | 0.0511 | 0.819 | 0 | 0.003 | 0.520 / 0.338 | 0.62 |
| 5 | epithelial cell | WNT5A → FZD3 | 0.709 | 0.0988 | 0.808 | 0 | 0 | 0.259 / 0.151 | 0.78 |
| 6 | CAF_B7H3_high | PLAU → PLAUR (self) | 0.531 | 0.0979 | 0.629 | 0 | 0 | 0.643 / 0.481 | 0.42 |

Other recurrent high calls include PLAU → ITGAM (macrophage, Δ 0.480), PLAU → ITGA5
(dendritic cell, 0.422), LAMC1 → ITGA1 (T cell, 0.350), TNC → EGFR (epithelial, 0.334) and
LAMC1 → CD44 (macrophage, 0.320).

Top enriched_low:

| Rank | Target | Ligand → receptor | Δ rank | rank high | rank low | p high | p low | lr_means high/low | log2FC |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | neutrophil | CXCL12 → ITGA5 | −0.809 | 0.860 | 0.0511 | 0.001 | 0 | 0.311 / 0.384 | −0.30 |
| 2 | neutrophil | MDK → SORL1 | −0.641 | 0.733 | 0.0920 | 0.002 | 0 | 1.564 / 1.605 | −0.04 |
| 3 | T cell | CXCL12 → CD4 | −0.237 | 0.314 | 0.0775 | 0 | 0 | 0.217 / 0.289 | −0.42 |
| 4 | neutrophil | ANGPT1 → ITGA5 | −0.214 | 0.265 | 0.0511 | 0.001 | 0 | 0.297 / 0.306 | −0.04 |
| 5 | mast cell | CXCL12 → ITGAV | −0.192 | 0.243 | 0.0511 | 0 | 0 | 0.278 / 0.350 | −0.33 |

### 4.2 LUAD (Panel S5A)

5,053 unique target–LR pairs compared: **540 enriched_high** (10.7%), **91 enriched_low**
(1.8%), 1,650 both_pass (32.7%), 2,772 neither (54.9%).

224/540 high calls (41.5%) have no low-side row; 3/91 low calls have no high-side row.
Median |log2(lr_means high/low)| is 0.57 for high calls and 0.16 for low calls.

Top enriched_high:

| Rank | Target | Ligand → receptor | Δ rank | rank high | rank low | p high | p low | lr_means high/low | log2FC |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | neutrophil | THBS2 → CD47 | 0.912 | 0.0885 | 1.000 | 0 | 0.006 | 0.717 / 0.468 | 0.62 |
| 2 | stromal/other | PLAU → LRP1 | 0.834 | 0.0891 | 0.923 | 0 | 0.001 | 0.436 / 0.295 | 0.57 |
| 3 | macrophage | PLAU → ITGB5 | 0.759 | 0.0831 | 0.842 | 0 | 0 | 0.340 / 0.198 | 0.78 |
| 4 | erythrocyte | INHBA → ACTR2 | 0.728 | 0.0564 | 0.785 | 0 | 0.014 | 0.801 / 0.613 | 0.39 |
| 5 | dendritic cell | SERPINE1 → LRP1 | 0.723 | 0.0824 | 0.806 | 0 | 0 | 0.614 / 0.396 | 0.63 |
| 6 | malignant cell | PLAU → ITGB5 | 0.710 | 0.0746 | 0.784 | 0 | 0 | 0.345 / 0.203 | 0.76 |
| 7 | T cell | HLA-B → CD8B | 0.681 | 0.0564 | 0.737 | 0 | 0.077 | 1.624 / 1.428 | 0.19 |
| 8 | dendritic cell | PLAU → ITGA5 | 0.614 | 0.0663 | 0.680 | 0 | 0 | 0.362 / 0.221 | 0.71 |

Also PLAU → ITGB5 (stromal/other, 0.614), PLAU → ITGA5 (macrophage, 0.559),
SERPINE1 → PLAUR (malignant, 0.532), INHBA → ENG (dendritic, 0.516),
LMAN1 → MCFD2 (erythrocyte, 0.512), PLAU → IGF2R (CAF_low, 0.485) and
COL4A2 → ITGB5 (macrophage, 0.480).

Top enriched_low:

| Rank | Target | Ligand → receptor | Δ rank | rank high | rank low | p high | p low | lr_means high/low | log2FC |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | malignant cell | GPC3 → CD81 | −0.917 | 1.000 | 0.0828 | 0.007 | 0 | 0.478 / 0.650 | −0.44 |
| 2 | epithelial cell | GPC3 → CD81 | −0.472 | 0.528 | 0.0564 | 0 | 0 | 0.558 / 0.730 | −0.39 |
| 3 | malignant cell | GPC3 → IGF1R | −0.468 | 0.524 | 0.0564 | 0 | 0 | 0.181 / 0.353 | −0.96 |
| 4 | CAF_B7H3_low | GPC3 → IGF1R | −0.452 | 0.508 | 0.0564 | 0 | 0 | 0.182 / 0.354 | −0.96 |
| 5 | epithelial cell | GPC3 → IGF1R | −0.421 | 0.477 | 0.0564 | 0 | 0 | 0.185 / 0.357 | −0.95 |
| 6 | macrophage | GPC3 → LRP1 | −0.361 | 0.418 | 0.0564 | 0 | 0 | 0.401 / 0.573 | −0.52 |
| 7 | CAF_B7H3_high | GPC3 → UNC5C | −0.352 | 0.396 | 0.0444 | 0 | 0 | 0.167 / 0.339 | −1.02 |
| 8 | macrophage | TFPI → LRP1 | −0.325 | 0.393 | 0.0680 | 0 | 0 | 0.669 / 0.736 | −0.14 |

### 4.3 Recurring biology and the "unique signaling" question

The same few ligand programmes recur across diseases and directions:

- **THBS2 → CD47** is the top enriched_high interaction in both SCLC (mast-cell target) and
  LUAD (neutrophil target), with Δ ≈ 0.91–0.92 and low-side p = 0.006–0.062.
- **PLAU (uPA) → PLAUR / ITGA5 / ITGB5 / LRP1 / IGF2R** appears repeatedly in enriched_high
  calls in both diseases (SCLC self/PLAUR, macrophage ITGAM, dendritic ITGA5, plasma IGF2R;
  LUAD LRP1, ITGB5, ITGA5, IGF2R).
- **SERPINE1 (PAI-1) → LRP1 / PLAUR** and **INHBA → ACTR2 / ENG** recur in LUAD high calls.
- SCLC also has PLTP → ABCA1, MXRA5 → PILRB and WNT5A → FZD3 in the high direction.
- **Enriched_low** in SCLC is led by CXCL12 → ITGA5 (neutrophil, Δ −0.81), CXCL12 → CD4
  (T cell, Δ −0.24), CXCL12 → ITGAV (mast cell, Δ −0.19) and MDK → SORL1 (neutrophil,
  Δ −0.64). CXCL12 → CXCR3 is also called enriched_low, but at much lower rank (B cell,
  Δ −0.138, rank 11/53; T cell, Δ −0.086, rank 22/53), so CXCR3 is present but is not the
  dominant receptor of this programme. In LUAD the low direction is dominated by
  GPC3 → CD81/IGF1R/LRP1/UNC5C and TFPI/A2M → LRP1. The GPC3 programme is a coherent
  glypican axis, but it is confined to the low group and must be interpreted with the same
  caution as the high calls. (Full CXCL12 pair list: `liana_cxcl12_pairs.csv` — 54 SCLC and
  67 LUAD target–pair rows.)

**Do any interactions survive all pre-specified filters?** Yes, in the narrow sense: 2,387
SCLC and 3,931 LUAD CAF-source interactions pass all three filters, and 290/53 (SCLC) and
540/91 (LUAD) pair-level calls are enriched_high/enriched_low. But "survives the filters"
does **not** mean "statistically significant high-vs-low": there is no formal test, no FDR,
and two of the three filters are non-discriminating. The calls should be described as
**nominal, rank-based differential-specificity candidates**, not as validated differential
interactions.

Most target–LR pairs are detected in both groups. Presence is inferred from a non-null
`lr_means_high` / `lr_means_low` (the pair table has no explicit presence flag), and the
counts reconcile by inclusion–exclusion (`shared = |H| + |L| − |union|`;
`liana_pair_status_counts.csv`):

| Disease | Union | Shared | High-only | Low-only | Reconciliation |
|---|---:|---:|---:|---:|---|
| SCLC | 4,051 | 3,564 | 486 | 1 | 3,564 + 486 + 1 = 4,051 |
| LUAD | 5,053 | 4,041 | 970 | 42 | 4,041 + 970 + 42 = 5,053 |

(|H| and |L| are the 4,050 / 3,565 SCLC and 5,011 / 4,083 LUAD source-group pair counts in
`liana_caf_source_group_counts.csv`.) The pairs absent from the low group are absent because
they fail the `expr_prop=0.1` detection threshold there, which is exactly the kind of
difference that can be produced by the depth difference documented in §6. Of the
enriched_high calls, 63/290 (SCLC) and 224/540 (LUAD) rest on a pair with no low-side row at
all — a subset of the 486 / 970 high-only pairs.

---

## 5. Sensitivity to the CAF definition

The pre-specified definitions in `liana_b7h3_caf_definition.csv`:

| Disease | Definition | High rule | High cells | Low cells |
|---|---|---|---:|---:|
| SCLC | primary | CD276 > 0 | 86 | 158 |
| SCLC | a (median positive) | CD276 > 1.5 (i.e. ≥2) | 43 | 201 |
| SCLC | b (Q75) | CD276 > 1 | 43 | 201 |
| SCLC | c (quartile top) | CD276 > 1 | 43 | 158 |
| LUAD | primary | CD276 > 0 | 1,676 | 5,346 |
| LUAD | a (median positive) | CD276 > 1 (i.e. ≥2) | 551 | 6,471 |
| LUAD | b (Q75) | CD276 > 0 (Q75 = 0) | 1,676 | 5,346 |
| LUAD | c (quartile top) | CD276 > 0 (Q75 = 0) | 1,676 | 5,346 |

Thus b and c are identical to the primary definition in LUAD. In SCLC, only **a and b** are
the same split (43 high / 201 low); **c is 43 high / 158 low**. The 43 cells with CD276 = 1
are high in c but low in a and b, and definition c leaves those 43 cells unassigned rather
than placing them in the low group. The sensitivity run tested definition **a** only. We
reran LIANA with identical parameters and the identical cell universe for definition **a**
in both diseases (`liana_raw_{sclc,luad}_sens_a.parquet`, 1,000 permutations; SCLC 25,378
rows/1,681 LR pairs, LUAD 38,671 rows/1,524 pairs).

| Disease | Definition | CAF-source rows | Pass all filters | Enriched high | Enriched low |
|---|---|---:|---:|---:|---:|
| SCLC | primary | 7,615 | 2,387 | 290 | 53 |
| SCLC | a | 7,706 | 2,481 | 282 | 81 |
| LUAD | primary | 9,094 | 3,931 | 540 | 91 |
| LUAD | a | 9,651 | 4,122 | 590 | 138 |

Concordance of the calls between primary and sensitivity a:

| Disease | Direction | Primary | Sens a | Shared | % of primary reproduced |
|---|---|---:|---:|---:|---:|
| SCLC | enriched_high | 290 | 282 | 183 | 63.1% |
| SCLC | enriched_low | 53 | 81 | 35 | 66.0% |
| LUAD | enriched_high | 540 | 590 | 431 | 79.8% |
| LUAD | enriched_low | 91 | 138 | 78 | 85.7% |

Overall directional agreement among pairs called in both runs is 94.3% (SCLC) and 93.9% (LUAD).
At the level of individual calls, the conclusion is **partially robust**: LUAD high calls are
reproduced ~80% of the time, SCLC only ~63%. The very top SCLC hits are not robust:
THBS2 → CD47, PLAU → IGF2R and WNT5A → FZD3 become `neither` under definition a, whereas
PLTP → ABCA1 and MXRA5 → PILRB remain enriched_high. In LUAD, all top-5 high calls
(THBS2 → CD47, PLAU → LRP1, PLAU → ITGB5, INHBA → ACTR2, SERPINE1 → LRP1) are reproduced;
the top low call GPC3 → CD81 (malignant) is not, while the GPC3 → IGF1R calls are.

---

## 6. Depth confounding of the detection-based split

This is the most important caveat for interpretation. CD276 raw-count detection is a function
of sequencing depth, and the high group is systematically deeper:

| Disease | Median genes high | Median genes low | Difference | Median counts high/low | Spearman CD276 vs genes (all fib) | Donor-level Spearman frac_high vs median genes |
|---|---:|---:|---:|---:|---:|---:|
| SCLC | 3,312 | 1,959 | +69% | 9,808 / 4,507 | ρ = 0.452 (p ≈ 0) | ρ = 0.647 (p = 0.060, n = 9) |
| LUAD | 2,556 | 1,654 | +55% | 8,342 / 4,358 | ρ = 0.421 (p ≈ 0) | ρ = 0.609 (p < 0.001, n = 58) |

`results/tables/liana_caf_depth_audit.csv`, `liana_caf_depth_by_donor.csv`,
`results/figures/caf_b7h3_detection_depth_audit.png`.

Consequences:

1. Many "high-only" interactions may reflect greater detectability in deeper cells rather than
   a cell-state-specific signalling programme.
2. The high group is not a clean biological "B7-H3-high" state; it is "B7-H3-detected", which
   is partly "deeply sequenced".
3. The rank-based specificity score can also shift when a group has more detected genes
   (more competing interactions), so direction is not guaranteed to be depth-neutral.
4. No depth matching or depth-normalised split was pre-specified. We did **not** add a
   post-hoc matched analysis, because it would be exploratory; if the claim is to be
   published, a depth-matched or donor-level analysis should be pre-specified and run.

**A second, related imbalance: fibroblast subtype.** The atlas has no myCAF/iCAF labels;
`cell_type_original` only separates "fibroblast", "fibroblast of lung" and "bronchus
fibroblast of lung". We therefore computed a transparent marker-score proxy, not a subtype
classification (`liana_caf_subtype_check.csv`): myCAF score = mean log-normalised
ACTA2/TAGLN/MYL9/CNN1/CTHRC1/POSTN/MMP11/FAP; iCAF score = mean IL6/CXCL12/HAS1/PDGFRA/LIF.
In LUAD the high group is clearly myCAF-marker-high (mean 1.43 vs 1.00; cell-level
Mann–Whitney p = 1.1e-83; donor-level paired Wilcoxon p = 4.8e-7 over 22 donors with ≥10
cells in both groups) and is anatomically skewed (62.8% "fibroblast" vs 44.1%; 24.9%
"fibroblast of lung" vs 45.6%). In SCLC the difference is smaller and not significant at cell
level (myCAF 1.72 vs 1.51, p = 0.053; only 2 paired donors, so no donor-level test; iCAF
p = 0.98). The LUAD high group is therefore partly a myCAF-like state — plausible biology,
since activated/myCAF fibroblasts may express more CD276 — but the contrast cannot be
attributed to B7-H3 detection alone: it also contrasts fibroblast states and anatomical
labels. The subtype and depth differences are not independent, because myCAF markers are
themselves depth-sensitive. This limitation is carried into §8 and §9.

Gene-level expression for the top-pair ligands/receptors (mean log-normalised expression and
percent detected, high vs low) is in `results/tables/liana_top_pair_gene_expression.csv`
(66 rows: 39 SCLC genes, 27 LUAD genes). This checks whether the genes behind a call differ
after normalisation, rather than only in rank. Two things follow.

*Source-side (CAF ligand) genes do differ after normalisation*, consistent with the calls:
PLAU log2FC 1.04 (SCLC) / 0.97 (LUAD), THBS2 0.71 / 0.76, WNT5A 1.28 (SCLC), PLTP 0.83 (SCLC),
INHBA 0.83 (LUAD), SERPINE1 0.73 (LUAD). The high group is not merely rank-shifted; it carries
more of these transcripts per normalised unit.

*Target-side genes differ much less*, so the differential is mostly a property of the CAF
source: CD47 0.45 / 0.27, LRP1 0.29 / 0.21, IGF2R 0.81 / 0.47, CD81 0.30 (LUAD). Some calls
rest on very sparse genes and should not be over-read: FZD3 (1.2% vs 0% detected in SCLC),
CD8B (1.7% / 0.9% in LUAD), SORL1 (1.2% / 2.5%) and PILRB (14% / 5.7%). CD276 itself is
100% detected in the high group and 0% in the low group by construction, which confirms the
split rule was applied as intended.

---

## 7. Verified pre-registration timeline (transparency correction)

All timestamps below were read programmatically from file mtimes or embedded timestamps
(`04e_liana_timeline_verification.py` → `results/tables/liana_timeline_verification.csv`).
Local time is America/Chicago (UTC−5).

| UTC time | Event | Evidence |
|---|---|---|
| 14:48:41 / 14:48:47.9 | CAF definition table written | file mtime / embedded `pre_registered_utc` |
| 14:48:51 / 14:48:58.4 | CAF definition meta written | file mtime / embedded `timestamp_utc` |
| 14:50:05–06 | 20-permutation timing probe output and log exist | probe CSV/meta/log mtimes |
| 14:52:26 | LIANA parameters and universe rule fixed in script 03 (original run) | script mtime |
| 14:52:55 (start) → ~14:54:07 | 50-permutation benchmark | log embedded start + 1.2 min wall; log mtime 14:54:01 |
| 14:53:15 | Filter values fixed in script 04 (original run) | script mtime |
| **14:54:43** | **Main 1,000-permutation SCLC run STARTED** | log embedded `timestamp_utc` (set before the run) |
| 14:55:02 / 14:55:09.0 | Consolidated filters CSV written | file mtime / embedded `pre_registered_utc` |
| **14:55:50** | **Main run raw parquet and log written; estimated finish 14:55:57** | file mtimes; 1.24 min total wall |

**Correct statement:** the CAF definition was fixed before any LIANA run (14:48:58Z). The
filter values were fixed in code at 14:53:15Z, **before the main 1,000-permutation run started
at 14:54:43Z**, but **after a 20-permutation probe** whose output existed at 14:50:06Z and
could in principle have been inspected. The consolidated `liana_pre_registered_filters.csv`
was written at 14:55:02–09Z, i.e. **during** the main run and before its output parquet existed
at 14:55:50Z. Filter values were never changed after seeing main-run results.

Corrections to the brief required by the evidence:

- The main SCLC run **started** at 14:54:43Z; it completed at ~14:55:50–57Z. The brief's
  statement that it completed at 14:54:43Z is incorrect.
- The consolidated filters CSV therefore **postdates the start of the main run but precedes
  its output**; it does not postdate the completed main run. The stronger and accurate claim
  is that it was written while the main run was executing, so it cannot encode main-run
  results.
- The sentence in the CSV itself, "written before any LIANA result was inspected", is an
  overstatement because the 20-permutation probe had already run. The CSV is left unmodified
  as an audit artifact; this report is the correction.

---

## 8. Limitations

1. **Small SCLC sample.** 244 fibroblasts; 86 high cells from 7 donors, but only **2 donors**
   contribute ≥10 high cells. Cell-level LIANA does not account for donor structure, so
   pseudo-replication is a real risk. LUAD is larger (1,676 high cells, 47 donors, 22 with ≥10)
   but still analysed at cell level.
2. **Depth confounding.** Documented in §6; the high group has 55–69% more detected genes.
   The split is detection-based, not expression-quantile-based, because Q25/Q75 are zero.
3. **Batch/dataset structure.** SCLC is one dataset (576f193c). LUAD has two datasets with
   different high fractions (17.3% vs 30.8%), so disease-level results may partly reflect
   dataset composition.
4. **No formal high-vs-low test and no FDR.** The differential call is a rank comparison;
   `cellphone_pvals` is a within-group permutation p-value, not a between-group test. The
   p-value and ≥3-method filters removed zero rows, so the analysis is effectively a single
   top-decile specificity filter.
5. **p-value resolution.** `cellphone_pvals` is rounded to 3 decimals; `p = 0` means
   `p < 0.0005` (or ≤1/1001) and cannot resolve smaller differences.
6. **Resource coverage.** The consensus resource yields 1,479–1,655 LR pairs; absence of a
   pair is not evidence of absent signalling.
7. **LUAD universe deviation.** Non-fibroblast cells were downsampled to at most 1,500 per
   type, whereas SCLC used the full atlas. Specificity ranks are relative to each run's own
   universe, so absolute ranks are not directly comparable across diseases. The directional
   theme (PLAU/SERPINE1/THBS2) is comparable; the numeric ranks are not.
8. **No spatial validation here.** Cell2location/Visium is handled by another agent; this
   report contains no spatial evidence.
9. **Log repairs.** The LUAD `append_log()` `EmptyDataError` was fixed and its row
   reconstructed; the SCLC benchmark/main rows were restored from the interrupted run because
   the carried-over log was 0 bytes. No analysis values were changed.
10. **Fibroblast subtype imbalance (not controlled).** The atlas has no myCAF/iCAF
    annotation. A marker-score proxy (`liana_caf_subtype_check.csv`) shows the LUAD high group
    is myCAF-marker-high (1.43 vs 1.00; cell p = 1.1e-83; donor-level paired p = 4.8e-7,
    n = 22) and enriched for the "fibroblast" anatomical label (62.8% vs 44.1%; "fibroblast
    of lung" 24.9% vs 45.6%). The contrast therefore confounds CD276 detection with
    fibroblast subtype and anatomical composition, on top of sequencing depth. SCLC is too
    small to test at donor level (2 paired donors; cell-level myCAF p = 0.053). This is not a
    subtype classification and does not by itself prove a myCAF state.

---

## 9. Bottom line: is there signalling unique to B7-H3-high CAFs?

**No unique signalling is demonstrated.** What the data support is a **quantitative,
rank-based enrichment** of a coherent ECM/proteolysis programme in CD276-detected CAFs:

- THBS2 → CD47 (top call in both diseases; Δ ≈ 0.91–0.92);
- PLAU → PLAUR / ITGA5 / ITGB5 / LRP1 / IGF2R (repeated across both diseases);
- SERPINE1 → LRP1 / PLAUR and INHBA → ACTR2 / ENG (LUAD);
- plus SCLC-specific PLTP → ABCA1, MXRA5 → PILRB and WNT5A → FZD3.

The same theme is the strongest signal in both panels and survives the alternative CAF
definition in LUAD (80% of high calls reproduced; top-5 all reproduced). In SCLC the direction
survives but the specific calls are unstable (63% reproduced; top-3 not reproduced).

**Confidence:**

- **Moderate** that CD276-detected LUAD CAFs are enriched for PLAU/SERPINE1/THBS2
  ECM-remodelling interactions (consistent direction, n = 1,676 high cells/47 donors,
  sensitivity-robust at the programme level). This confidence is **conditional** on
  describing the contrast as "CD276-detected, myCAF-marker-enriched CAFs": the high group is
  also myCAF-marker-high (1.43 vs 1.00; donor paired p = 4.8e-7) and depth-deeper, so it is
  not a pure B7-H3 effect.
- **Weak** for SCLC (n = 86 high cells, 2 donors with ≥10 cells, top calls not
  sensitivity-robust, subtype difference not testable at donor level).
- **Weak** for the word "unique": most pairs are shared, the split is depth- and
  subtype-confounded, and there is no formal between-group test or donor-level validation.

**Recommended wording for the paper:** "In LUAD, CD276-detected CAFs — which are also
myCAF-marker-enriched and deeper-sequenced than CD276-negative CAFs — show enriched
ECM-proteolysis and remodelling ligand–receptor programmes (PLAU–PLAUR/ITGA5/ITGB5/LRP1,
SERPINE1–LRP1, THBS2–CD47); the direction is consistent in SCLC but the calls are less
stable. The detection-based split is depth-dependent, the high group also differs in
fibroblast subtype, and the calls are nominal differential-specificity candidates, not
validated unique interactions." Do **not** claim signalling unique to B7-H3-positive CAFs
without a depth-matched, subtype-aware, donor-level validation.

---

## 10. Output inventory

Key outputs (all under `work/single-cell-analyst/`):

| Path | Rows | Content |
|---|---:|---|
| `results/tables/liana_raw_sclc.parquet` | 25,028 × 13 | raw SCLC rank_aggregate (md5 `bc460cd8e9e52bdd3c37202dda59d121`) |
| `results/tables/liana_raw_luad.parquet` | 37,684 × 13 | raw LUAD rank_aggregate (md5 `f46213df00b593a30e4976489a11a09b`) |
| `results/tables/liana_caf_b7h3_sclc_4d.csv` | 7,615 × 26 | SCLC CAF-source interactions + pass flags + call |
| `results/tables/liana_caf_b7h3_luad_s5a.csv` | 9,094 × 26 | LUAD CAF-source interactions + pass flags + call |
| `results/tables/liana_pair_level_comparison_{sclc,luad}.csv` | 4,051 / 5,053 × 24 | one row per target–LR pair |
| `results/tables/liana_filter_cascade.csv` | 8 | cascade, both diseases |
| `results/tables/liana_cascade_audit.csv` | 8 | independent recomputation |
| `results/tables/liana_high_vs_low_differential_summary.csv` | 2 | per-disease summary |
| `results/tables/liana_top_differential_pairs.csv` | 60 | top 20 high + top 10 low per disease |
| `results/tables/liana_differential_composition.csv` | 4 | call composition / absence / effect sizes |
| `results/tables/liana_top_pair_gene_expression.csv` | 66 | gene-level lognorm / % detected for top-pair genes |
| `results/tables/liana_caf_depth_audit.csv` | 2 | depth confounding |
| `results/tables/liana_caf_depth_by_donor.csv` | 67 | donor-level depth/positivity |
| `results/tables/liana_sensitivity_concordance.csv` | 6 | primary vs sensitivity a |
| `results/tables/liana_top_hits_primary_vs_sens_a.csv` | 50 | top hits with sensitivity calls |
| `results/tables/liana_raw_{sclc,luad}_sens_a.parquet` | 25,378 / 38,671 × 13 | sensitivity raw LIANA |
| `results/tables/liana_caf_b7h3_{sclc,luad}_sens_a.csv` | 7,706 / 9,651 × 26 | sensitivity CAF-source tables |
| `results/tables/liana_timeline_verification.csv` | 11 | pre-registration timeline |
| `results/tables/liana_run_log.csv` | 3 | benchmark50, main SCLC (restored), LUAD (reconstructed) |
| `results/tables/liana_pair_status_counts.csv` | 2 | Revision 2: presence/inclusion–exclusion counts per disease |
| `results/tables/liana_cxcl12_pairs.csv` | 121 | Revision 2: every CXCL12 target pair with call and Δ rank (54 SCLC, 67 LUAD) |
| `results/tables/liana_caf_subtype_check.csv` | 125 | Revision 2: myCAF/iCAF marker scores and anatomical fractions by group and donor |
| `results/tables/liana_caf_subtype_check_tests.csv` | 2 | Revision 2: cell-level Mann–Whitney and donor-level paired Wilcoxon |
| `results/figures/fig4d_liana_sclc_caf_b7h3.png/.pdf` | — | Panel 4D |
| `results/figures/figs5a_liana_luad_caf_b7h3.png/.pdf` | — | Panel S5A |
| `results/figures/caf_b7h3_detection_depth_audit.png` | — | depth audit |

Pre-existing, reused unchanged: `liana_b7h3_caf_definition.csv`,
`liana_b7h3_caf_definition_by_donor.csv`, `liana_b7h3_caf_definition_meta.json`,
`liana_pre_registered_filters.csv`.

### Reproduction and external inputs

Outputs are written under the LIVE workspace
`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8/work/single-cell-analyst/`.
Inputs that are too large to copy remain in SOURCE
(`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/single-cell-analyst/`)
and are read read-only:

| Input | SOURCE relative path | Size (bytes) | md5 |
|---|---|---:|---|
| integrated atlas | `data/processed/scrna_luad_sclc_integrated.h5ad` | 5,699,624,838 | `57c86760d9eaebce5f75cb69768e0cab` |
| SCLC LIANA universe | `data/processed/liana/liana_SCLC_universe.h5ad` | 1,414,231,381 | `5492f9a728a02a5a120ff0ee9ec193e4` |
| LUAD LIANA universe | `data/processed/liana/liana_LUAD_universe.h5ad` | 651,265,125 | `74b2443fa241338d88b826bfebb49d50` |

Raw outputs and run logs were copied from SOURCE into LIVE with `cp -p` (mtimes preserved)
and md5-verified; no values were rewritten:

| LIVE file | md5 |
|---|---|
| `results/tables/liana_raw_sclc.parquet` | `bc460cd8e9e52bdd3c37202dda59d121` |
| `results/tables/liana_raw_luad.parquet` | `f46213df00b593a30e4976489a11a09b` |
| `results/tables/liana_raw_sclc_sens_a.parquet` | `6f60cf77274be847438019cf72bbacb9` |
| `results/tables/liana_raw_luad_sens_a.parquet` | `c04cc28ff51a62c71f7cf730521058fc` |

Logs copied unchanged: `logs/liana_probe.log`, `logs/liana_run_SCLC_benchmark50.log`,
`logs/liana_run_SCLC_main.log`, `logs/liana_run_LUAD_main.log`,
`logs/liana_sensitivity_SCLC.log`, `logs/liana_sensitivity_LUAD.log`.

In Revision 2 the scripts were re-pointed so `ROOT` resolves to LIVE and only the inputs
above are read from SOURCE. Re-running the deterministic post-processing scripts
(`04b_liana_cascade_audit.py`, `04e_liana_timeline_verification.py`,
`04f_liana_top_pairs.py`) produced byte-identical tables (md5 unchanged), and `04e` still
resolved the original SOURCE mtimes. Commands from LIVE:

```
source /mnt/beegfs/xqinag/projects/TheVirtualBiotech/activate.sh
cd /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8/work/single-cell-analyst
python code/scripts/04b_liana_cascade_audit.py
python code/scripts/04e_liana_timeline_verification.py
python code/scripts/04f_liana_top_pairs.py
python code/scripts/liana_revision2_presence.py
python code/scripts/liana_revision2_caf_subtype_check.py
```

LIANA itself (`03_liana_run.py`, `06_liana_sensitivity_run.py`) was **not** re-run in
Revision 2; the raw parquets above are the originals.

The 0-byte SCLC universe copy (not used anywhere) is in the abandoned run
`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-103545-round-2-of-the-b7-h3-cd276-case-3c05f9f0/work/single-cell-analyst/data/processed/liana/liana_SCLC_universe.h5ad`
(md5 `d41d8cd98f00b204e9800998ecf8427e`, the empty-file hash). The SOURCE and R0 copies are
intact.
