# B7-H3 lung cancer, Round 2 — conversation record

Round 2 extends round 1 (`conversation_log.md`) with the two panels round 1
explicitly scoped out — Visium spatial transcriptomics (4E/S5B) and LIANA
ligand-receptor signalling (4D/S5A) — plus a full scientific-review, revise,
re-review cycle, the same DeepSeek-routed, unmodified-`TheVirtualBiotech`
setup as round 1 (see `../BASELINE.md`).

## Why this took five run directories

The system was interrupted four times, each a transient network/API error,
not a data or code problem (diagnosed in
`../run_round2/config/resume_after_interruption_*.md`):

1. **Original run** (`27ef6dcf`) — completed 4A/4F/4B-4C/Visium-QC,
   interrupted mid Wave 2 (LIANA + cell2location).
2. **Resume 1** (`3c05f9f0`) — copied round 1's outputs forward in full
   (a ~7–8 GB `work/` tree copy — see the disk-quota section below), made
   further progress, died silently with no error logged.
3. **Resume 2** (`ef6e8b35`) — ran cell2location (3,000-epoch CPU mapping,
   reference training + spatial mapping). Appeared to finish, but the
   stored abundance table was discovered later to be 100% NaN (see below).
   Died again right after the cell2location sub-agent returned, before the
   CSO could act on the result.
4. **Resume 3** (`a9b7a6f8`) — diagnosed and fixed the NaN bug, reran
   cell2location, ran the spatial-neighbourhood analysis, went through a
   full scientific-review cycle. Died at the very last step (recording
   final claims via the provenance MCP server).
5. **Resume 4** (`76d40ca3`) — synthesis-only, no re-analysis: wrote the
   final report, panel-by-paper comparison, workflow diagram, and
   successfully recorded all 15 claims.

Each resume was preceded by reading the previous run's `logs/trace.jsonl`
directly to find the exact point of interruption, rather than restarting
from scratch.

## The disk-quota crisis and its cleanup

By the time resume 2 was running, the host's **200 GB per-user BeeGFS
quota** (separate from, and not visible via, overall filesystem capacity —
`df -h` looked fine throughout) had ~1.8 GB of headroom left. Root cause:
each resume had copied round 1's full `work/` tree forward, producing three
near-duplicate copies of the same large `.h5ad` files (the original run plus
two resumes). After explicit, itemized user approval — full path/size/SHA-256
verification of every candidate file, confirmation no live script still
depended on the old paths, before any deletion — **8 files (not 10; 2 of 10
candidate slots were a 0-byte copy with nothing to match)** totalling
~13.46 GB were deleted from the two dead run directories, recovering headroom
to ~15 GB. Four live-run scripts that still hardcoded the dead run's path
were fixed first, so they wouldn't silently read/write the now-deleted files.
Full record: `../run_round2/config/CLEANUP_MANIFEST.md`.

A related audit found one `liana_SCLC_universe.h5ad` file at 0 bytes in the
live run — diagnosed as a write-only provenance artifact (the real scientific
output, `liana_raw_sclc.parquet`, was never affected) and restored from a
verified-identical backup rather than silently left broken.

## The cell2location NaN bug

Resume 2's "completed" cell2location mapping (3,000/3,000 epochs, ELBO
converged 104M → 38.5M) had a real training result — but its exported
abundance table was **100% NaN in all 14 cell-type columns**, independently
verified (not just taken from the sub-agent's own report) by loading the
parquet directly and checking `isna().mean()`. Root cause: the export code
built the output as `pd.DataFrame(obsm_array, columns=[...])` — when the
input is already a DataFrame, passing `columns=` performs label-based
*selection*, not renaming, so every column selected to NaN. No model
checkpoint had been saved (`enable_checkpointing=False`, to save disk), so
there was no way to re-export without retraining. Resume 3 retrained with an
identical configuration (verified by diff against the original script),
fixed the export (`.copy()` then `.columns = [...]`, the correct in-place
rename), saved the model checkpoint this time, and the corrected output was
independently verified at 0.0% NaN before being accepted.

## Review, revision, re-review

A full scientific-reviewer pass on the spatial arm returned **"Revise and
resubmit"**: the NaN-bug diagnosis and fix were independently confirmed
correct ("exemplary" handling), but the published report's bottom line
over-weighted a T-cell/dendritic-cell increase while omitting more
donor-concordant findings — consistent relative depletion of endothelial,
NK, macrophage, monocyte, and mast compartments in high-CD276 tumour
neighbourhoods. Four specialists (single-cell-analyst, genomics-analyst,
clinical-trialist, functional-genomics-analyst) filed itemized revision
responses, each verified against re-computed (not re-downloaded) local data.
A **separate, earlier interim review** of the six panels that didn't touch
spatial analysis (run concurrently with the ~2-hour cell2location CPU job,
in its own isolated process, to avoid racing the live training) had already
found two "partially supported" panels (4B/4C's DE table, Visium QC) with
real, fixable defects. A re-review confirmed all fixes and returned the
final verdict: **ACCEPT WITH DISCLOSED LIMITATIONS**, conditional on two
text-only corrections (both applied, no re-analysis needed).

## GPU exploration (did not end up mattering)

Partway through, a CUDA-enabled PyTorch install was attempted to speed up
cell2location on two idle Quadro RTX 8000 GPUs. It was cloned into an
isolated conda environment (`vbt_c2l`, hardlink-cloned from the shared `vbt`
env to avoid quota cost and avoid touching the environment the live
specialists were actively importing from) rather than installed in-place.
The live run's own agent independently attempted the same `pip install` and
was correctly blocked by a harness policy hook ("Package installation is
prohibited"), so it fell back to CPU on its own — which, at 3,000/250
epochs, finished in a documented ~2 hours and produced a complete result.
Once CPU proved sufficient, the now-unneeded `vbt_c2l` environment (~6.7 GB)
was deleted to recover disk headroom; the shared `vbt` environment was
confirmed untouched throughout.

## Final result

See `../run_round2/report/FINAL_REPORT.md` and
`panel_by_paper_comparison.md`. Headline: direction and shape mostly agree
with the paper, but strength is materially weaker across several panels —
CD276 is not tumour-restricted, not differentially expressed in any of 15
disease-vs-normal contrasts, not independently prognostic once adjusted for
stage, and the "immune-hot" spatial niche is largely a capture-depth
artifact. This supports round 1's low-confidence stance on CD276 but
revises away its SCLC-over-LUAD staging claim — the only quantitative
positives found here are in LUAD.
