# Round 2: run lineage

Round 2 added spatial transcriptomics (Visium + cell2location, panels 4E/S5B
and the spatial-neighbourhood analysis) and LIANA ligand-receptor analysis
(panels 4D/S5A) on top of round 1's scope, plus a full scientific-review /
revision / re-review cycle. It took **five run directories** on disk because
the process was interrupted four times by transient network/API errors (not
data or code problems — each interruption is diagnosed in
`config/resume_after_interruption_*.md`). This directory consolidates the
two run directories that hold real, final content; see
`../conversation/conversation_log_round2.md` for the full narrative.

| # | Run directory (original name) | What happened |
|---|---|---|
| 1 | `20261021-080518-...-27ef6dcf` | Original attempt. Completed 4A/4F/4B-4C/Visium-QC; interrupted mid Wave 2. **Superseded, not included here.** |
| 2 | `20261021-103545-...-3c05f9f0` | First resume. Copied forward round 1's outputs, made some further progress, died silently. **Superseded, not included here.** |
| 3 | `20261021-113551-...-ef6e8b35` | Second resume. Ran cell2location (3,000-epoch mapping) — but an export bug produced 100% NaN abundances. Died again at the very end. **Superseded, not included here** (the bug fix happened in run 4, not this one). |
| 4 | `20261021-204038-...-a9b7a6f8` | Third resume. **Included as `README_main_turn.md` / `logs_main_turn/` / `work/`.** Diagnosed and fixed the NaN export bug (independently verified: 0% NaN on the corrected output), reran cell2location, ran the spatial-neighbourhood analysis, went through a full review → revise → re-review cycle (verdict: **ACCEPT WITH DISCLOSED LIMITATIONS**), and closed out six items flagged by an earlier interim review of panels 1–6. Died at the final claims-recording step. |
| 5 | `20261022-010102-...-76d40ca3` | Fourth resume, synthesis-only (no re-analysis). **Included as `README_synthesis_turn.md` / `logs_synthesis_turn/` / `report/`.** Wrote the final synthesis, panel-by-paper comparison, and workflow diagram, and recorded all 15 claims against evidence. |

**What's excluded from this directory and why:** the three superseded run
directories (1–3) above; raw/processed `.h5ad` and large intermediate arrays
under each specialist's `data/` (gigabytes, not needed to audit the
*results* — the code that produced them is included under `work/*/code/`);
a `synthetic_test/` scaffolding directory single-cell-analyst used to
validate its pipeline on fake data before touching the real 2-hour CPU
training run; one 110 MB CSV, kept but gzip-compressed
(`scrna_pseudobulk_de_luad_sclc.csv.gz`) to stay under GitHub's 100 MB
per-file limit.

**Two "homes," one result.** `MANIFEST.json`/`evidence/` in this directory
are from the synthesis turn (run 5) — the one with the complete,
successfully-recorded claims. `work/` (the specialist code/results) is from
the main turn (run 4) — the one that actually did the spatial analysis. Both
turns operated on the same run-4 directory on the original filesystem; the
split here only reflects that each turn writes its own run-report by design.
