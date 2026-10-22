# Correction Task A — fitting the paper's actual Figure 4E mixed-effects model

Run: `20261022-094819-this-is-a-targeted-correction-pa-d24cb49b`
Agent: single-cell-analyst
Scope: targeted correction of the Figure 4E/S5B interpretation. No new Visium
data pull and no cell2location re-run. Inputs are the existing per-spot tables
from run `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`.

## 1. Why this analysis was required

The paper's Figure 4E caption states (verbatim ground truth):

> "Spatial transcriptomic analyses of LUAD primary-site tissue identifies
> **immune-excluded niches** in B7-H3 expressing spots relative to B7-H3
> non-expressing spots. Bar plot quantifies the percent change in neighbor
> immune abundance between top and bottom quartile of B7-H3-expressing spots
> across 12 LUAD tumor samples. Significance was assessed using a
> **mixed-effects model adjusting for total UMI count, fibroblast abundance,
> and malignant epithelial abundance fixed effects, with random effects at the
> sample-level**."

The body text adds that B7-H3-high spots showed "significant depletion of
neighboring immune cells such as T cells, macrophages, monocytes, and dendritic
cells."

Round 2 characterized this as an "immune-hot" claim (increased immune
abundance). That was backwards. Round 2 also had two analyses that did not
implement the paper's model: (i) an unadjusted absolute-abundance contrast
(T +15%, DC +29%) that is depth/edge-confounded, and (ii) a depth-robust
composition contrast (macrophage -0.40 pp, monocyte -0.23 pp, T +0.11 pp,
DC +0.49 pp). Neither adjusted for total UMI count, fibroblast abundance and
malignant abundance simultaneously with a sample-level random effect.

This report fits that model directly, on the existing per-spot data.

## 2. Inputs and parquet-to-CSV bridge

Inputs (read-only):

| File | Use |
|---|---|
| `.../a9b7a6f8/.../results/tables/visium_c2l_spot_abundances.parquet` | per-spot abundances, CD276, depth, section, patient (47,448 x 39) |
| `.../visium_spot_qc_metrics.csv` | cross-check of `total_counts` (already present in the parquet; not re-merged) |
| `.../visium_c2l_cd276_stratification_audit.csv` | per-section quartile/fallback diagnostics, used as a cross-check |

**Environment constraint and bridge.** The active `python` (pytorch env) has
pandas 2.3.3, numpy, scipy and statsmodels 0.14.6 but no parquet reader.
`pyarrow` 19.0 in `conda` env `qlib_real` aborts on this file
(`OSError: Repetition level histogram size mismatch`), including on a local
copy, so the failure is in the file's page metadata, not the filesystem.
`pyarrow` 20.0 in env `vbt` reads the file correctly. The parquet was therefore
exported once with:

```
conda run -n vbt python -c "import pyarrow.parquet as pq; \
  pq.read_table(SRC).to_pandas().to_csv(DST, index=False)"
```

to `data/processed/visium_c2l_spot_abundances.csv` (47,448 rows x 39 columns;
verified unique `spot_barcode`, 27,826 tumour / 19,622 adjacent-normal). The
model script then reads the CSV in the active env. **No package was installed
or upgraded.**

`total_counts` in the parquet was compared with the QC CSV for the overlap;
the parquet column is used.

## 3. Model specification (exactly what was fitted)

Primary analysis: **12 tumour sections only** (matches the paper's "12 LUAD
tumor samples"), spots in the per-section top or bottom CD276 quartile, with at
least one spatial neighbour.

```
y_i = beta0 + beta1 * CD276_high_i
        + beta2 * z(log1p(total_counts_i))
        + beta3 * z(mean_fibroblast_i)
        + beta4 * z(mean_malignant cell_i)
        + u_section[i] + epsilon_i
u_section ~ N(0, sigma_section^2);  epsilon ~ N(0, sigma^2)
```

* `y_i` = **neighbour-mean abundance** of the immune cell type, mean over the
  spatial neighbours of spot i, self excluded. This is the paper's "neighbor
  immune abundance".
* `CD276_high_i` = 1 for the per-section top quartile of `CD276_lognorm`
  (log1p CP10K), 0 for the bottom quartile. The middle 50% is excluded from the
  contrast but still contributes as a neighbour.
* Continuous covariates are z-scored within the analysed rows.
* Random effect: random intercept for `section` (the paper's sample level).
* Estimator: `statsmodels.formula.api.mixedlm`, **REML**, `method="lbfgs"`,
  maxiter 300. Wald z p-values. BH-FDR across the 9 immune types within each
  analysis.
* Seed 42; all fits converged (`converged == True` for all 108 fits).

**Neighbourhood graph.** Reused verbatim from
`visium_c2l_30_neighborhood_analysis.py`: `cKDTree` on
(`array_row`,`array_col`), query radius **2.05**, self excluded.

**Important lattice finding.** On this coordinate table the 2.05 radius returns
**up to 8 neighbours**, not 6: 4 at distance 1.414 and 4 at distance 2.0 (next
ring 2.828). The realised degree distribution is: 0 neighbours 130 spots,
1-5 neighbours 6,002, exactly 6 neighbours 3,000, 7 neighbours 6,013,
**8 neighbours 32,303** (68.1%). The source script and report describe this as
a "k=6 hex lattice"; that description is inaccurate for this table. The graph
logic itself is unchanged, and the unadjusted contrasts computed from it
reproduce the source table exactly (Section 6), so all comparisons remain
internally consistent. The sensitivity labelled "full ring" uses the modal
complete ring (`n_neighbours == 8`). The source report's "six-neighbour-only"
edge sensitivity (Section 6.3 of the source) therefore selected *partial-ring*
spots, not interior spots; this is flagged as a caveat rather than re-run.

**Group construction.** The strict `>q75` / `<q25` split is impossible in
22/22 sections because CD276 is zero in the majority of spots and `<q25` is
empty. The deterministic rank fallback (top/bottom 25% by CD276 rank) used in
the source analysis is reused. Tumour: 6,951 high + 6,951 low spots before the
neighbour filter; 6,943 + 6,943 (13,886) enter the model. All 12 tumour
sections triggered the fallback; the high group is CD276-positive in 52-100%
of spots per section and the low group is 100% CD276-zero.

## 4. Primary result — tumour, neighbour abundance, paper covariates, section RE

`results/tables/visium_correction_mixed_effects_4e.csv` (9 rows). Percent change
is the adjusted coefficient divided by the crude low-group mean (descriptive
denominator). `unadjusted %` is the crude high-vs-low difference, which
reproduces the source absolute-abundance table exactly.

| Cell type | beta | SE | 95% CI | p | BH q | Direction | Adjusted % | Unadjusted % |
|---|---|---|---|---|---|---|---|---|
| **T cell** | -0.01642 | 0.00353 | -0.02333 to -0.00951 | 3.23e-6 | 5.40e-6 | decrease | **-3.22** | +15.37 |
| B cell | -0.01837 | 0.00388 | -0.02598 to -0.01076 | 2.24e-6 | 5.04e-6 | decrease | -4.34 | +15.16 |
| NK cell | -0.02285 | 0.00364 | -0.02997 to -0.01572 | 3.29e-10 | 1.48e-9 | decrease | -5.46 | +3.81 |
| **Macrophage** | -0.02521 | 0.00527 | -0.03553 to -0.01489 | 1.70e-6 | 5.04e-6 | decrease | **-12.00** | -7.58 |
| **Monocyte/myeloid** | -0.00734 | 0.00214 | -0.01153 to -0.00315 | 5.88e-4 | 7.56e-4 | decrease | **-3.08** | +2.19 |
| **Dendritic cell** | -0.01064 | 0.00437 | -0.01921 to -0.00208 | 0.0148 | 0.0167 | decrease | **-3.44** | +28.77 |
| Mast cell | -0.01969 | 0.00296 | -0.02548 to -0.01390 | 2.64e-11 | 2.38e-10 | decrease | -5.63 | +8.45 |
| Neutrophil | +0.00002 | 0.00159 | -0.00310 to +0.00314 | 0.988 | 0.988 | none | +0.01 | +17.27 |
| Plasma cell | -0.02373 | 0.00512 | -0.03377 to -0.01369 | 3.60e-6 | 5.40e-6 | decrease | -9.17 | +2.92 |

n = 13,886 spots (6,943 high, 6,943 low), 12 sections, 5 donors for every row.
**8 of 9 immune types are significantly depleted after adjustment; the
direction is negative for 8/9 and the ninth (neutrophil) is null.** The four
compartments the paper names explicitly — T cells, macrophages,
monocytes/myeloid, dendritic cells — are **all significantly depleted**.

Random-effect variance was estimated at the boundary (0) for 7/9 types;
T cells (0.00492; ICC 0.114) and mast cells (0.00283; ICC 0.095) retained a
non-zero section variance.

## 5. Sensitivity analyses

`results/tables/visium_correction_mixed_effects_4e_sensitivity.csv` (108 rows:
12 analyses x 9 types). All fits converged.

| Analysis | n spots | Types with q<0.05 | Direction of significant types |
|---|---|---|---|
| Primary (tumour, neighbour, own covariates, section RE) | 13,886 | 8/9 | 8 decrease, 0 increase |
| log1p(neighbour abundance) response | 13,886 | 8/9 | 8 decrease |
| Detection group (`CD276_counts>0` vs `=0`) | 27,789 | 9/9 | 9 decrease |
| Neighbour-mean covariates | 13,886 | 8/9 | 8 decrease |
| Spot-own abundance response | 13,886 | 7/9 | 7 decrease |
| Patient random effect (5 donors) | 13,886 | 7/9 | 7 decrease |
| Nested patient + section | 13,886 | 8/9 | 8 decrease |
| Depth adjustment only | 13,886 | 3/9 | NK, macrophage, mast decrease |
| Depth + fibroblast only | 13,886 | 7/9 | 7 decrease |
| Complete-ring spots (`n_neighbours==8`) | 10,404 | 8/9 | 8 decrease |
| Adjacent-normal, primary spec | 9,759 | 1/9 | macrophage **increase** |
| Adjacent-normal, detection group | 19,529 | 6/9 | mixed |

Key sensitivity details for the paper's four named compartments (beta, 95% CI,
p):

| Analysis | T cell | Macrophage | Monocyte/myeloid | Dendritic cell |
|---|---|---|---|---|
| Primary | -0.0164 (-0.0233,-0.0095) p=3.2e-6 | -0.0252 (-0.0355,-0.0149) p=1.7e-6 | -0.0073 (-0.0115,-0.0032) p=5.9e-4 | -0.0106 (-0.0192,-0.0021) p=0.015 |
| Depth only | -0.0066 (-0.0154,0.0022) p=0.141 | -0.0200 (-0.0305,-0.0096) p=2e-4 | +0.0014 (-0.0033,0.0061) p=0.559 | +0.0042 (-0.0060,0.0144) p=0.422 |
| Depth + fibroblast | -0.0139 (-0.0224,-0.0054) p=0.0014 | -0.0251 (-0.0353,-0.0149) p=2.0e-6 | -0.0070 (-0.0112,-0.0028) p=0.0012 | -0.0083 (-0.0180,0.0014) p=0.092 |
| Full adjust (primary) | -0.0164 p=3.2e-6 | -0.0252 p=1.7e-6 | -0.0073 p=5.9e-4 | -0.0106 p=0.015 |
| Detection group | -0.0246 (-0.0303,-0.0188) p=4e-17 | -0.0251 (-0.0337,-0.0165) p=1e-8 | -0.0114 (-0.0150,-0.0078) p=4e-10 | -0.0141 (-0.0211,-0.0071) p=8e-5 |
| Patient RE | -0.0157 p=1.1e-5 | -0.0247 p=2.6e-6 | -0.0077 p=3.1e-4 | -0.0072 p=0.105 |
| Nested patient/section | -0.0164 p=3.4e-6 | -0.0251 p=1.9e-6 | -0.0074 p=5.6e-4 | -0.0106 p=0.015 |
| Complete ring | -0.0194 p=2.5e-6 | -0.0254 p=1.8e-5 | -0.0072 p=0.0029 | -0.0150 p=0.0034 |
| Adjacent-normal | +0.0027 p=0.340 | +0.0249 p=8e-4 | +0.0031 p=0.228 | +0.0037 p=0.158 |

The **covariate decomposition** explains the round-2 discrepancy. Without
adjustment, T cells and DCs rise (+15% and +29%); adjusting for depth alone
already removes those increases (T -1.3% ns, DC +1.4% ns), and adding the
fibroblast and malignant covariates makes both significantly negative. Depth
is massively imbalanced between groups (median tumour total counts in the high
vs low group, per section, ranges e.g. 11,040 vs 3,237 in P10_T1 and 6,716 vs
3,428 in P16_T2; full table in
`visium_correction_mixed_effects_4e_group_construction.csv`).

The **adjacent-normal** analysis is not a confirmation and should not be read as
one: the "high" group has median CD276 = 0.0 in 8/10 sections, so it separates a
shallow positive tail from an all-zero tail. It shows a significant macrophage
*increase* and null T/DC/monocyte effects, opposite to the tumour direction;
this is consistent with the degenerate stratification rather than with biology.

## 6. Reproduction check

The crude high-minus-low means from this run reproduce the source
absolute-abundance table exactly (to two decimals) for all 9 types: T +15.37,
B +15.16, NK +3.81, macrophage -7.58, monocyte +2.19, DC +28.77, mast +8.45,
neutrophil +17.27, plasma +2.92 percent. This confirms that the exported CSV,
the per-section rank split and the neighbourhood graph match the source
analysis; the only new element is the paper-style adjustment.

## 7. Honest interpretation

**Against the corrected paper claim (immune-excluded / depletion), the new
adjusted model AGREES for all four named compartments.** In tumour sections,
B7-H3-high spots have significantly fewer neighbouring T cells (-3.2%,
q=5.4e-6), macrophages (-12.0%, q=5.0e-6), monocytes/myeloid (-3.1%,
q=7.6e-4) and dendritic cells (-3.4%, q=0.017), after adjusting for total UMI
count, fibroblast abundance and malignant abundance with a section random
effect. B, NK, mast and plasma cells are also significantly depleted;
neutrophils are null. The result is robust to log-transforming the response,
to a detection-group definition, to neighbour-based covariates, to patient and
nested random effects, and to restricting to complete-ring spots.

**This does not make the round-2 unadjusted finding wrong; it explains it.**
The unadjusted absolute-abundance analysis (T +15%, DC +29%) disagrees with the
paper, and it is the analysis that is depth/edge-confounded. Once the paper's
own covariates enter the model, those increases disappear and reverse. The
depth-robust composition analysis partially agrees (macrophage -0.40 pp,
monocyte -0.23 pp) and partially disagrees (T +0.11 pp, DC +0.49 pp). The
correct synthesis is therefore:

* unadjusted absolute abundance: **disagrees** for T/DC, agrees for macrophage,
  and is confounded;
* composition (density removed, but no covariate adjustment): **mixed**;
* paper-style adjusted mixed model: **agrees** for all four named compartments.

**What can be claimed.** Under the paper's own model and adjustment strategy,
the B7-H3-high niche in these 12 LUAD sections is immune-excluded, not
immune-hot. The effect is largest for macrophages and smallest (but still
significant) for T cells and monocytes.

## 8. Caveats

1. **Spatial autocorrelation is not modelled.** Up to 13,886 spots are treated
   as conditionally independent given a section random intercept. Spatially
   correlated residuals will make the Wald p-values anticonservative; they
   should be read as strong directional evidence, not calibrated probabilities.
   The coefficients and CIs are less affected than the p-values.
2. **Only 12 sections / 5 donors.** The section random-effect variance is
   estimated at zero for 7/9 types (boundary solution), so those fits are
   effectively OLS with section fixed structure absorbed by covariates. The
   patient-RE and nested sensitivities are consistent but also rest on 5
   donors.
3. **The 2.05-radius graph returns 8 neighbours, not 6.** This is inherited
   from the source analysis and is documented in Section 3. The neighbour mean
   is therefore an 8-spot mean for full-ring spots. The complete-ring
   sensitivity is consistent with the primary.
4. **Group construction relies on the rank fallback.** CD276 is zero in the
   majority of spots, so the literal quartile boundary cannot be used. The
   fallback preserves equal group sizes but the "low" group is entirely
   CD276-zero and the "high" group is only 52-100% positive across sections.
5. **Adjustment covariates are themselves tissue-composition measures.** The
   fibroblast and malignant covariates are the paper's specification but they
   may be downstream of the same niche biology; the model estimates the
   immune difference conditional on them, not a causal effect.
6. **Adjacent-normal is degenerate and underpowered** (median CD276 = 0 in the
   high group in 8/10 sections). It is reported only as a sensitivity.
7. **No new data were pulled and no independent cohort was used.** Results are
   conditional on the E-MTAB-13530 sections and the existing cell2location
   fit (3,000 epochs).

## 9. Output files

| File | Content |
|---|---|
| `code/scripts/visium_correction_mixed_effects_4e.py` | reproducible model script, including the parquet->CSV bridge |
| `data/processed/visium_c2l_spot_abundances.csv` | 47,448 x 39 per-spot table exported from the source parquet |
| `results/tables/visium_correction_mixed_effects_4e.csv` | primary per-cell-type results (9 rows) |
| `results/tables/visium_correction_mixed_effects_4e_sensitivity.csv` | 108 rows, 12 analyses x 9 types, all sensitivities |
| `results/tables/visium_correction_mixed_effects_4e_group_construction.csv` | per-section high/low sizes, CD276 medians, positivity, depth balance |
| `results/reports/visium_correction_mixed_effects_4e_fit_log.txt` | full fit log, degree distribution, convergence |
