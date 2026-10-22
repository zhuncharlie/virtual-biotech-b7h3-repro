# Round 2 disk-quota cleanup manifest

**Date:** 2026-10-21, ~12:15 CDT
**Trigger:** per-user BeeGFS quota (200GB hard limit, separate from overall
filesystem capacity) reached 212.8GB/214.7GB used (~1.8GB headroom) while
the live resume run (`...ef6e8b35`) was still executing. Root cause: each
of the two resume attempts copied the full ~7-8GB `work/` tree from its
predecessor run, producing 3 near-duplicate copies of the same large files
(original interrupted run + 2 resumes).

**Approved by user** on 2026-10-21, with explicit conditions: verify every
candidate file's path/size/hash against the live run before deleting, keep
all reports/scripts/figures/tables/logs/unique data, never delete a whole
run directory, never modify the live run's own data, confirm no live
script depends on the old paths, and record everything here.

## Scope clarification: 8 files, not 10

Originally 5 file *names* were considered × 2 dead runs = 10 candidate
slots. One of the five (`liana_SCLC_universe.h5ad`) is excluded from both:
- In the second dead run (`...3c05f9f0`) and in the live run
  (`...ef6e8b35`), this file is **0 bytes** (the copy never completed
  correctly) -- deleting a 0-byte file frees no space and there is nothing
  to "match."
- In the first dead run (`...27ef6dcf`), this file is **1,414,231,381
  bytes (real data)** -- it does **not** match the live run's 0-byte copy,
  so per the user's own rule ("confirm the live run isn't still relying on
  the old file" / only delete verified-matching items) **this file was
  excluded from deletion.** It remains in the first dead run, untouched.

That leaves **4 distinct files x 2 dead runs = 8 files**, all verified.

## Pre-deletion fix: 4 live-run scripts had hardcoded paths to the dead run

Before any deletion, a scan found that 4 scripts **copied into the live
run's own `work/` tree** still had their `ROOT`/`RUN` path constant
hardcoded to the first dead run (`...27ef6dcf`), left over from the earlier
resume's file copy:

| Script | Variable | Old value | Fixed to |
|---|---|---|---|
| `work/single-cell-analyst/code/scripts/01_liana_b7h3_caf_definition.py` | `ROOT` | `...27ef6dcf` | `...ef6e8b35` (live) |
| `work/single-cell-analyst/code/scripts/02_liana_probe.py` | `ROOT` | `...27ef6dcf` | `...ef6e8b35` (live) |
| `work/single-cell-analyst/code/scripts/visium_01_verify_extract.py` | `RUN` | `...27ef6dcf` | `...ef6e8b35` (live) |
| `work/single-cell-analyst/code/scripts/visium_02_qc_combine.py` | `RUN` | `...27ef6dcf` | `...ef6e8b35` (live) |

These 4 scripts directly reference the big files (`scrna_luad_sclc_integrated.h5ad`,
`visium_sections_qc.h5ad`, `visium_sections_all_spots_raw_counts.h5ad`) by
path built from that constant -- if re-executed with the old path, they
would have read/written against the (about-to-be-partially-deleted) dead
run instead of the live run. **Only the live run's copies of these 4
scripts were edited.** The dead runs' original copies of these scripts were
left completely untouched, preserving an accurate historical record of what
was actually executed in those runs.

Two other scripts (`03c_restore_interrupted_run_log_rows.py`,
`04e_liana_timeline_verification.py`) reference the dead run's path but
only for small CSV/log files (not in the deletion list) used for one-time
provenance recovery/audit -- confirmed safe, not modified.

A full re-scan after the fix confirmed zero remaining references to the 4
big files via the old dead-run path anywhere in the live run's code.

## Hash verification (SHA-256, full file)

All 4 files, both dead runs, matched the live run's copy **exactly**:

| File | SHA-256 | Size | Dead1 | Dead2 | Live |
|---|---|---|---|---|---|
| `scrna_luad_sclc_integrated.h5ad` | `5b3e2a5b7f24111c9d175432b1dc74817fb74fa725ff6b0a582be32b47fefce0` | 5,699,624,838 | match | match | (reference) |
| `visium_sections_qc.h5ad` | `2e9e76c003437ec3fa46e7e9736411ee89a2ca069ac50338fa72fdd295febeff` | 450,400,778 | match | match | (reference) |
| `c2l_reference_luad_normal_hvg2000.h5ad` | `e953c3ceb2b18d347d067c5a7b93911c5d2e0205e16c432286b04a4a21b0104d` | 337,062,173 | match | match | (reference) |
| `visium_sections_all_spots_raw_counts.h5ad` | `208dcb57c646e13f77a7ef0e0b73860d5b72bce4b0beef259294fbee66151386` | 242,522,260 | match | match | (reference) |

Raw hash output preserved in this directory: `hash_dead1.log`,
`hash_dead2.log`, `hash_verification.log`.

## Deleted (pending execution below)

```
runs/20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/single-cell-analyst/data/processed/scrna_luad_sclc_integrated.h5ad
runs/20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/single-cell-analyst/data/processed/visium_sections_qc.h5ad
runs/20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/single-cell-analyst/data/processed/c2l_reference_luad_normal_hvg2000.h5ad
runs/20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/single-cell-analyst/data/raw/visium_sections_all_spots_raw_counts.h5ad
runs/20261021-103545-round-2-of-the-b7-h3-cd276-case-3c05f9f0/work/single-cell-analyst/data/processed/scrna_luad_sclc_integrated.h5ad
runs/20261021-103545-round-2-of-the-b7-h3-cd276-case-3c05f9f0/work/single-cell-analyst/data/processed/visium_sections_qc.h5ad
runs/20261021-103545-round-2-of-the-b7-h3-cd276-case-3c05f9f0/work/single-cell-analyst/data/processed/c2l_reference_luad_normal_hvg2000.h5ad
runs/20261021-103545-round-2-of-the-b7-h3-cd276-case-3c05f9f0/work/single-cell-analyst/data/raw/visium_sections_all_spots_raw_counts.h5ad
```

**NOT deleted** (explicitly preserved): everything else in both dead run
directories -- all reports, scripts (including the un-fixed, historically
accurate originals), figures, small tables, logs, trace.jsonl, MANIFEST.json,
evidence/, and the 1.4GB real `liana_SCLC_universe.h5ad` in the first dead
run (does not match live, excluded per verification rule above).

## Going forward

Per user instruction: future resumes should not do a full fresh copy of
the predecessor's large data files. Instead, large shared inputs (the
integrated atlas, Visium QC output, cell2location reference) should live
in one controlled, shared path that every run's scripts point to, while
each run's own new outputs (reports, new tables, new figures) stay
separate per run. This will be addressed in the next resume script
revision, not retroactively applied to the already-completed runs above.
