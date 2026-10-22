# Resume instructions after transient API interruption

**What happened:** run `20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf`
was progressing normally -- panels 4A, 4F, 4B/4C, and Visium QC (4E stage 1)
were all completed and internally verified against saved tables, both
mandated reviewer-correction checks (LoF-constraint wording, Tahoe-100M
materiality) were pinned down, and Wave 2 (LIANA for 4D/S5A, cell2location
for 4E/S5B) had just been released in parallel -- when the turn was cut off
by `API Error: Unable to connect to API (ConnectionRefused)`. This was a
transient network issue (DeepSeek endpoint), not a data or code problem;
connectivity was confirmed restored immediately after. No disk-space or
inode issue either (31% used, 139TB free at interruption time -- an earlier
inode-quota check the agent ran itself came back clean).

**Your job this turn: resume, not restart.** Read everything below, then
read the interrupted run's own directory directly (reports, tables, logs,
code) before writing or redoing anything.

## What is already done and verified (reuse directly, cite the source run)

Source run: `runs/20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf`

- **4A** (`work/genomics-analyst/results/reports/cd276_panel4a_report.md` +
  figure): round-1's 0/8 and 0/67 independently reproduced; 839 CD276-linked
  E2G element-gene links, 29 at the pre-declared Score>=0.02 threshold.
- **4B/4C** (`work/single-cell-analyst/results/reports/scrna_panels4bc_report.md`
  + figures): 413,996-cell / 80-donor / 15-cell-type full-transcriptome atlas
  (`genes_subsetted=false`, `retry_count=0` -- no silent fallback), pseudobulk
  DE across 15 contrasts. CD276 not significantly DE anywhere (padj>=0.291).
  Two honestly-disclosed limitations: the >=15% mito filter is a no-op
  (Census raw matrices have all-zero MT genes), and SCLC fibroblasts are only
  244 cells / 9 donors.
- **4E stage 1 / Visium QC** (`work/single-cell-analyst/results/reports/visium_ingest_qc_log.md`):
  22/22 sections, 54,650 raw in-tissue spots -> 47,448 QC-passed (86.8%).
- **4F** (`work/clinical-trialist/results/reports/tcga_luad_cd276_survival_report.md`
  + figure): `luad_tcga_pan_can_atlas_2018`, 566 clinical patients / 510 with
  CD276 mRNA, Q4-vs-Q1 OS n=251. Unadjusted OS HR 1.80 (1.19-2.71) p=0.0051,
  adjusted (age/sex/stage) 1.44 (0.92-2.26) p=0.106; DSS 1.86 -> 1.39. All
  four endpoints (OS/PFS/DSS/DFS) computable with PH-assumption caveats
  noted. The paper's HRs sit close to the *unadjusted* numbers here; the
  association attenuates after adjustment -- state this plainly, do not
  smooth it over.
- **Tahoe / DepMap / pathway-safety / clinical-landscape round-1 reuse**:
  already verified per the interrupted run's own notes; the LoF-constraint
  artifact carries the correct raw numbers (o/e 0.667, 34 vs 51 expected,
  p=4.3e-8).
- **The two mandated reviewer-correction checks are already pinned down
  precisely** (do not re-derive, just apply them when reviewing/synthesizing):
  1. LoF constraint: o/e 0.667 with a CI excluding 1.0 = **moderate
     constraint**, not "tolerance," not "favourable." Round 1 inconsistently
     called the CI level 95% and 90% across two reports -- harmonize.
  2. Tahoe-100M: a failed/incomplete query is **low materiality**, must never
     be cited as a limitation of the recommendation, must not be converted
     into a zero result. Watch specifically for "0/379 drugs annotate CD276"
     being misread as "no perturbation effect."

## What was IN PROGRESS when the interruption hit (verify before trusting, resume rather than redo from zero)

Wave 2, dispatched in parallel, both under `work/single-cell-analyst/`:

- **LIANA (4D/S5A)**: a B7-H3+ CAF definition was pre-registered BEFORE
  running LIANA (`results/tables/liana_b7h3_caf_definition.csv` +
  `_by_donor.csv` + `_meta.json`) -- good practice, keep it, do not
  re-derive the cutoff after the fact. Filters were also pre-registered
  (`results/tables/liana_pre_registered_filters.csv`). A probe run
  (`liana_PROBE_*`) and what looks like a real SCLC run in progress
  (`results/tables/liana_raw_sclc.parquet`, `liana_run_log.csv`,
  `data/processed/liana/liana_SCLC_universe.h5ad`, ~1.4GB) exist. Check
  `liana_run_log.csv` and the `logs/liana_run_SCLC_main.log` file to
  determine exactly how far this got (full rank_aggregate with 1,000
  permutations, or still running) before deciding whether to resume it or
  restart the SCLC run; LUAD (S5A) may not have started at all -- check.
- **cell2location (4E/S5B stage 2)**: reference preparation is done
  (`data/processed/c2l_reference_luad_normal_hvg2000.h5ad`,
  `results/tables/visium_c2l_reference_preparation.csv`,
  `visium_c2l_reference_gene_selection.csv`) -- CD276 should already be
  excluded from this reference per the plan; verify that explicitly. A
  benchmark script (`visium_c2l_11_benchmark.py`) exists but check
  `results/tables/visium_c2l_run_log.csv` and `logs_c2l_bench_ref.log` /
  `logs_c2l_10_prep.log` to see whether the actual reference *training* run
  (not just prep) completed, and whether spatial mapping has started at all
  (it almost certainly has not -- this is the longest single step in the
  whole plan). GPU: 2x Quadro RTX 8000, not the paper's H100 -- confirm
  epoch counts were adjusted and documented as planned.

## What has not started yet

- Spatial neighborhood analysis (k=6, top/bottom B7-H3 quartile, neighbor
  immune-abundance change) -- depends on cell2location finishing.
- Scientific-reviewer pass -- depends on everything above.
- Final synthesis, workflow diagram, panel-by-panel comparison to the paper,
  README/repo update and push.

## Rules carried over unchanged

No WebSearch/WebFetch for any role. No fitting analysis to the paper's
reported numbers -- every deviation gets documented, not smoothed over.
Failed tool calls get logged with error/fix/retry, not silently dropped or
silently retried. Reviewer must check underlying data/scripts/figures
directly, not just report prose. CSO forms its recommendation from this
round's actual evidence; round 1's conclusion is not assumed to carry over.
