# Resume instructions after a third interruption

**What happened:** run `20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35`
died silently again. MANIFEST.json status is "interrupted". The orchestrator's
own trace.jsonl stops right after receiving the cell2location sub-agent's
Agent-tool result as `completed` (14:27:07) -- the orchestrator process itself
crashed a few minutes later (~14:30), most likely another transient network
disruption, not a data or code problem. A detached nohup'd background training
process kept running independently of the dead orchestrator and finished
writing real results to disk at 15:08:38, well after the parent had already
died. Not a reason to distrust that data -- it was verified against the run
log (see below).

**Your job this turn: resume from the FURTHEST point reached. Do NOT retrain
or re-run cell2location -- it already completed successfully on CPU.** Reuse
these outputs directly, verified present and consistent with the run log:

- `work/single-cell-analyst/data/processed/visium_c2l_abundances_small.h5ad`
  (3.2 MB)
- `work/single-cell-analyst/results/tables/visium_c2l_spot_abundances.parquet`
  (926 KB) -- one row per spot, cell-type abundances, 47,448 spots, 22 sections
- `work/single-cell-analyst/results/tables/visium_c2l_mapping_history.csv`
- `work/single-cell-analyst/results/tables/visium_c2l_run_log.csv` -- last row:
  `mapping,ok,3000,3000,4096,cpu,47448,1926,7134.4,...22 sections,CPU only`
  (3000/3000 epochs completed, N_cells_per_location=8, detection_alpha=20,
  section-as-batch). Reference row: `reference_train,ok,250,250,...,4586.9,...`
  (250/250 epochs, 18.3 s/epoch). Both are genuine completed runs, not partial.
- GPU note: the live run's own agent attempted to enable CUDA and was
  correctly BLOCKED by a harness policy hook ("Package installation is
  prohibited: 'pip install'") -- see `work/single-cell-analyst/logs/c2l_env_setup.log`.
  This is expected and fine: CPU already produced complete, documented results
  in ~2 hours train + ~2 hours mapping. Do not attempt pip install again inside
  the run; there is no need to -- the GPU path is no longer necessary for this
  round. (A separate isolated GPU conda env, `vbt_c2l`, was created outside the
  run for exploration but has since been deleted since CPU already succeeded --
  do not reference it, it no longer exists.)

**What is NOT done yet -- this is the actual remaining work:**
1. Spatial-neighborhood analysis (CD276-high vs low spot, k=6 neighbor immune
   abundance). Script already exists: `code/scripts/visium_c2l_30_neighborhood_analysis.py`
   -- inspect it, fix the `ROOT` path constant to point at this run directory
   if it's stale, then run it against the completed abundances above.
2. Panel figures: `code/scripts/visium_c2l_40_panels.py` (fig4e_c2l_tumor,
   figs5b_c2l_adjacent_normal) and `code/scripts/visium_c2l_41_neighborhood_figures.py`
   (fig4e_neighborhood_immune_change). Also `code/scripts/visium_c2l_42_diagnostics.py`
   for model diagnostics. Same caveat: check/fix `ROOT` before running.
3. The final report `results/reports/visium_c2l_panels4e_s5b_report.md` --
   not written at all yet. Needs: data/provenance, the documented CPU epoch
   deviation from the paper's 10,000 epochs (with measured throughput and
   rationale -- already logged, just needs to be written up), per-section
   abundance summary, the 4E=tumor/S5B=adjacent-normal panel-split assumption
   (state explicitly), neighborhood methods/results/robustness, limitations,
   bottom-line statement.
4. After single-cell-analyst finishes the above: the spatial-neighborhood
   analysis task description originally bundled items 1-3 together with the
   cell2location run itself -- check `logs/trace.jsonl` around 11:40-14:27 for
   the exact original task prompt if you need the full spec (search for
   "cell2location 4E/S5B and neighborhoods").
5. **Scientific-reviewer has not started at all.** No `work/scientific-reviewer/`
   directory exists. Dispatch it after single-cell-analyst's remaining work
   above is done -- it must check underlying data/scripts/figures directly,
   not just report prose, across ALL specialists' work (LIANA, scRNA, TCGA,
   Tahoe, Visium QC, and the new cell2location/neighborhood results).
6. Final synthesis, panel-by-panel comparison to the paper, workflow diagram,
   README/repo update and push -- not started.

**Disk quota note:** per-user BeeGFS quota is 200GB (separate from overall
filesystem capacity). Just recovered to ~13GB headroom (pip cache purge +
deletion of an unneeded GPU conda env). Check with
`beegfs-ctl --getquota --uid $(whoami) --csv` before any large write.
**Do not copy the full `work/` tree from a predecessor run again** -- this
exact mistake caused a quota crisis twice already (triple-duplicated ~7-8GB
of large h5ad files across 3 prior resumes, requiring a verified manual
cleanup). You are already working directly in this run's own directory
(`...ef6e8b35`); there is no need to copy anything from an older run at all
this time -- everything needed is already here on disk, verified above.

Continue exactly as instructed before: finish the cell2location
report/figures/neighborhood analysis (reusing the already-completed
training/mapping data), scientific-reviewer pass (checking data/scripts/
figures directly), final synthesis, panel-by-panel comparison to the paper,
workflow diagram, README/repo update and push. No approval checkpoint needed.
