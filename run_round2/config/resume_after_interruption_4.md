# Resume instructions after a fourth interruption -- SYNTHESIS ONLY

**What happened:** run `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
died while calling `mcp__provenance__record_claims` (tool_error), right at the
very last step. No OOM, no disk/memory issue -- almost certainly another
transient network/API disruption, not a data or code problem. `claims.json`
in that run has 0 claims recorded; no CSO-authored synthesis was ever
written.

**Everything substantive is already done and verified. Your ONLY job this
turn is to write the final synthesis, workflow diagram, panel-by-paper
comparison, update the repo README, and push. Do NOT redo, re-verify, or
re-run any analysis -- every number below has already survived a full
scientific-review-and-revision cycle.**

## What is done (reuse directly, do not touch)

All in run directory `20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8`
(henceforth LIVE). Note: this turn will automatically get its own new run
directory as scaffolding/home (trace.jsonl, MANIFEST.json) -- that is normal
and expected, not something to avoid. What matters is: read everything below
from LIVE by absolute path, and write your final synthesis deliverables
(the synthesis report, workflow diagram, panel-by-paper comparison) directly
into LIVE's own directory by absolute path, since that is where everything
they synthesize already lives and where a human auditor will look. Do not
copy LIVE's large data files into your new home directory -- read them in
place.

- **Panel 4A** (genomics-analyst): `work/genomics-analyst/results/reports/cd276_panel4a_report.md`
  + `revision_response_to_reviewer.md` (Revision 2, all 5 review items resolved).
- **Panels 4B/4C** (single-cell-analyst): `work/single-cell-analyst/results/reports/scrna_panels4bc_report.md`.
- **Panels 4D/S5A** (single-cell-analyst, LIANA): `work/single-cell-analyst/results/reports/liana_panels4d_s5a_report.md`
  + `revision_response_to_reviewer.md`.
- **Panels 4E/S5B + spatial neighbourhood** (single-cell-analyst, cell2location):
  `work/single-cell-analyst/results/reports/visium_c2l_panels4e_s5b_report.md`.
  This went through a real retrain (the first mapping's export had a
  column-rename bug producing 100% NaN abundances -- independently verified;
  the rerun is config-identical, fixed, and model-checkpointed) and a full
  review-revise-rereview cycle.
- **Panel 4F** (clinical-trialist, TCGA survival): `work/clinical-trialist/results/reports/tcga_luad_cd276_survival_report.md`.
- **Tahoe-100M** (functional-genomics-analyst): `work/functional-genomics-analyst/results/reports/tahoe_round2_status.md`
  + `revision_response_to_reviewer.md`.
- **Visium ingest/QC** (single-cell-analyst): `work/single-cell-analyst/results/reports/visium_ingest_qc_log.md`.
- **Scientific review**: `work/scientific-reviewer/results/reports/review_round2_full.md`
  (first full pass, "Revise and resubmit") and
  `work/scientific-reviewer/results/reports/review_round2_rereview.md`
  (final verdict: **ACCEPT WITH DISCLOSED LIMITATIONS**). The two acceptance
  conditions were both already resolved (the two leftover training-history
  CSV stubs were deleted; the four median-of-medians values in the
  stratification audit were recomputed) -- verify they are still absent/
  updated, but do not redo the recomputation if they already are.

## Mandatory caveats from the final re-review -- carry these into the synthesis verbatim, do not soften

- Visium stratification is detection-based, not expression-quantile; the
  adjacent-normal "high" group is degenerate (median CD276 = 0.0 in 8/10
  sections). Never describe adjacent-normal tissue as "CD276-high vs
  CD276-low."
- Spatial permutation p-values are anticonservative (within-section shuffle
  destroys spatial autocorrelation; floor 1/1001); the bootstrap overstates
  precision (22 sections but only 5 donors per histology).
- LIANA calls are rank-based differential-specificity candidates with no
  formal test, no FDR, no depth-matched contrast; 55-69% detected-gene depth
  gap between high/low groups; SCLC has only 2 donors with >=10 high cells;
  myCAF/iCAF is a marker-score proxy, not an annotation.
- Survival: adjusted OS (p=0.106) and DSS (p=0.249) are NOT significant.
  CD276 is not an independent prognostic factor in this cohort on this
  analysis; only the stage-adjusted Q4-vs-rest framing reaches nominal
  significance.
- Tahoe/DepMap: "not assessable, no evidence either way" -- not "non-material."
  Mean CERES does not cross the essentiality threshold; only 1/46 LUAD lines
  does.
- CD276 is detected in 36.53% of normal lung macrophages and 30.84% of LUAD
  fibroblasts. No "tumour-restricted" or "tumour-specific" wording anywhere
  in the final synthesis.
- Cell2location/neighbourhood bottom line: density-confounded; absolute
  immune increases (T/B/DC/neutrophil) do not survive restriction to interior
  spots; the donor-concordant signal is relative depletion of endothelium,
  NK, macrophage, monocyte, mast -- not the T-cell/DC increase. State this
  as "weak-to-moderate for a B7-H3-specific immune niche; strong only for a
  density/endothelial story."

## Your job this turn

1. Dispatch the chief-of-staff (or write directly yourself) the final
   synthesis report: executive summary, panel-by-panel comparison to the
   source paper's claims (state agreement/disagreement/inconclusive per
   panel), the caveats above carried through honestly, and an overall
   assessment of B7-H3/CD276 as a lung-cancer target given everything found.
2. A workflow diagram (how the analysis flowed: data -> specialists -> review
   -> revision -> synthesis).
3. Record the claims via `mcp__provenance__record_claims` (this is what
   failed last time -- retry it; if it fails again, log the exact error and
   try once more before giving up and flagging it in the final report rather
   than silently omitting claims).
4. Update the top-level repo README.md to point to this case study's results.
5. Commit and push.

No approval checkpoint needed. If record_claims fails again, do not let that
block writing and saving the synthesis report itself to disk -- the report
file is more important than the provenance claim registration.
