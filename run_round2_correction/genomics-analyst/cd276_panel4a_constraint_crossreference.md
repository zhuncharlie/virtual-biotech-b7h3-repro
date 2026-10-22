# CD276 panel 4A — gene-constraint cross-reference (gnomAD pLoF O/E 0.6666 vs the paper's 0.67)

**Agent:** genomics-analyst, correction pass (targeted)
**Run:** `20261022-094819-this-is-a-targeted-correction-pa-d24cb49b`
**Panel:** Figure 4A, third evidence stream
**Nature of this document:** cross-reference only. No new computation, no new database query, no re-query of Open Targets. Two round-1 artifacts were read, checked against each other, and compared with the paper's quoted value.

---

## 1. What this stream is

The paper's Figure 4A body text states:

> "Constraint metrics showed a predicted loss-of-function observed-to-expected ratio of 0.67"

This is a **gnomAD-style gene-constraint metric**, not a GWAS association and not an ENCODE regulatory annotation. It is therefore a **third evidence stream** for panel 4A, distinct from the two already reported:

| Stream | What it measures | Relationship to the paper |
|---|---|---|
| 1. Germline credible-set / L2G | Fine-mapped statistical association between germline variants and LUAD/SCLC, plus locus-to-gene assignment | **Disagrees** — 0/8 studies, 0/67 disease-matched L2G loci |
| 2. E2G regulatory annotation | Predicted enhancer–gene links in a lung DNase biosample | **Agrees, but annotation-only** — 839 CD276-linked elements; 77 within ±500 kb; 29 at Score ≥ 0.02; promoter 0.973 |
| 3. Gene constraint (this document) | Depletion of predicted-LoF variants in the population relative to expectation | **Agrees** — LoF O/E 0.6666 rounds to the paper's 0.67 |

**What gnomAD constraint is.** The pLoF observed/expected (O/E) ratio compares the number of predicted loss-of-function variants actually observed in a large population cohort with the number expected under a neutral mutation model, after accounting for sequence context and coverage. An O/E well below 1 indicates that LoF variants in the gene are depleted in the population, i.e. that LoF is subject to purifying selection. It is a **gene-level population-genetic property**; it carries no information about tumour type, disease association or therapeutic effect.

---

## 2. Exact values, and cross-check between the two round-1 sources

Source: Open Targets gnomAD constraint, retrieved via `mcp__target__get_target_info` (target_id `ENSG00000103855`, CD276) on **2026-10-20**.

| Field | Round-1 CSV | Round-1 JSON | Agree? |
|---|---|---|---|
| LoF O/E | `0.6666399836540222` | `0.66664` | yes |
| observed pLoF | `34` | `34` | yes |
| expected pLoF | `51.00199890136719` | `51.002` | yes |
| 95% CI lower | `0.5059999823570251` | `0.506` | yes |
| 95% CI upper | `0.8880000114440918` | `0.888` | yes |
| p (departure from O/E = 1) | `4.2877999817392265e-08` | `4.2878e-08` | yes |
| upperRank | `7792` | `7792` | yes |
| upperBin | `4` | `4` | yes |
| upperBin6 | `2` | `2` | yes |

The CSV retains full float precision; the JSON carries the same values rounded to 5–6 decimal places. Fields and md5s are recorded in the output table and in `data/processed/cd276_constraint_crossreference_log.txt`.

**Paper match.** `0.6666` rounded to two decimal places is **0.67**, identical to the paper's quoted value. Agreement is exact at the precision the paper reports.

---

## 3. Round-1 source files

- `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/bio-pathways-ppi-analyst/results/tables/cd276_constraint_tractability.csv`
  — row key `annotation_class=constraint, annotation=lof`; md5 `38d309e0823cf4c79cb48c0182981af1`.
- `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/fda-safety-officer/data/raw/cd276_target_info_and_constraint.json`
  — field `constraint.lof`; md5 `89a01dcd0b16a29c898a170ce8c9bfc6`.

The brief's original paths (`virtual-biotech-b7h3-repro/run_round1/...`) are stale; the files above are the ones that exist and were read. Nothing in either source run was modified.

---

## 4. Interpretation — and what it does not mean

**What the numbers support.**

- 34 LoF variants observed against 51.002 expected: a 33% shortfall.
- The 95% CI on O/E is **0.506–0.888**. The upper bound is below 1, so the depletion is statistically supported, not noise (p = 4.3 × 10⁻⁸).
- The point estimate 0.67 indicates **moderate** selection against LoF. This is consistent with some degree of haploinsufficiency intolerance — a gene where losing one copy is mildly disfavoured — but it is not the profile of a severely constrained gene (the most constrained genes sit far lower, with O/E well under 0.3).

**upperBin / upperRank context.** gnomAD also stores a rank and a coarse bin for the *upper* confidence bound: `upperRank = 7792`, `upperBin = 4`, `upperBin6 = 2`. The upper bound sits relatively high, matching the moderate point estimate. The saved payload does not carry the rank denominator or the bin edges, and no web access was available in this pass, so **no percentile is derived here**. These fields are reported as stored, not re-interpreted into a percentile.

**What this must not be read as.**

- Not evidence that CD276 is dosage-sensitive in a therapeutically meaningful way. Constraint measures selection on germline LoF in populations, not the consequence of pharmacologically modulating the gene in a tumour.
- Not a disease association. It says nothing about LUAD or SCLC. Stream 1 remains the only stream that tests association, and it is negative.
- Not a therapeutic hypothesis. A moderate O/E neither supports nor refutes B7-H3 as a target.
- pLI was **not** returned by this source (`pLI_note` in the saved JSON), so no pLI is reported.

**Why it still matters for panel 4A.** The paper's panel 4A rationale cites this number. Our independently retrieved value reproduces it to the reported precision. That is a genuine, checkable point of **agreement** — a descriptive gene property, like the regulatory stream, rather than disease evidence.

**Caveat on provenance.** We cannot determine from the saved artifacts which gnomAD release the paper used. Agreement to two decimal places is strong but is agreement of a value, not proof of an identical data version.

---

## 5. Bottom line

Panel 4A now has three streams: germline genetic association **disagrees**; regulatory annotation **agrees but is annotation-only**; gene constraint **agrees** (LoF O/E 0.6666 ≈ 0.67). Only the first stream tests disease association, and it is negative. The two agreeing streams describe properties of the gene, not its role in LUAD/SCLC.

---

## 6. Artifacts

| Artifact | Contents |
|---|---|
| `results/tables/cd276_panel4a_constraint_crossreference.csv` | one tidy row: LoF O/E, obs, exp, CI, p, upperRank/Bin/Bin6, paper value 0.67, rounding check, agreement assessment, both source paths and md5s |
| `results/reports/cd276_panel4a_constraint_crossreference.md` | this document |
| `data/processed/cd276_constraint_crossreference_log.txt` | field-by-field verification log |
| `code/scripts/01_crossref_cd276_constraint_panel4a.py` | reads both round-1 sources, asserts agreement and the 0.6666→0.67 rounding, writes the table and log |
| `results/reports/cd276_panel4a_report.md` | corrected panel 4A report with the constraint stream added as the third stream |
