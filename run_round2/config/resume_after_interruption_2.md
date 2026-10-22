# Resume instructions after a second interruption

**What happened:** run `20261021-103545-round-2-of-the-b7-h3-cd276-case-3c05f9f0`
(itself a resume of the first interrupted run) went silent -- no completion,
no "interrupted" status, no log output, trace frozen -- while the CSO was
mid-investigation (just finished reading the atlas h5ad and the Visium
provenance config, about to dispatch Wave 2). Likely cause: a second
transient network disruption, possibly worsened by a concurrent large
background download (a CUDA-enabled PyTorch install) competing for
bandwidth on this host -- that download has now been stopped. DeepSeek
connectivity and disk quota were both confirmed healthy immediately
afterward. Not a data or code problem.

**Your job this turn: resume again, from the FURTHEST point reached.** The
run `20261021-103545-round-2-of-the-b7-h3-cd276-case-3c05f9f0` already has
a complete copy of everything the original interrupted run
(`20261021-080518-...-27ef6dcf`) had (4A, 4F, 4B/4C, Visium QC all done and
verified; LIANA SCLC main run succeeded with 1000 perms; cell2location
reference prep done), PLUS some additional investigation already recorded
in its own `logs/trace.jsonl` that you should read directly:

- An audit finding that `liana_pre_registered_filters.csv`'s timestamp
  (14:55:09 UTC) is AFTER the SCLC main LIANA run completed (14:54:43) --
  the "pre-registered before any result was inspected" framing needs to be
  corrected to state the true timeline honestly (definition fixed at
  14:48:58, a 20-perm probe at 14:50, filters finalized in code at ~14:53,
  main run 14:54:43, filters CSV written 14:55:09). This is a transparency
  fix to apply when reporting, not a reason to redo the analysis.
- The vbt conda environment's PyTorch was CPU-only (`torch.version.cuda =
  None`). **This has NOT yet been fixed as of this resume** -- a CUDA
  install was attempted but interrupted by the same network issue. GPUs
  (2x Quadro RTX 8000, Turing/sm_75, CUDA 12.1 driver) are present and
  idle. If cell2location/scvi-tools training needs to start, check
  `python3 -c "import torch; print(torch.version.cuda, torch.cuda.is_available())"`
  first -- if still CPU-only, either retry the CUDA install yourself (`pip
  install torch==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121`;
  neither scvi-tools nor cell2location pin a torch version, so this is
  safe) or proceed on CPU with a clearly documented epoch/runtime
  reduction -- do not silently train for hours without flagging the
  tradeoff.
- An open question on the 4E/S5B panel split: the Visium data is LUAD
  tumor + adjacent-normal only (no SCLC Visium data exists). The CSO had
  not yet resolved whether 4E = tumor-only / S5B = adjacent-normal, or some
  other split, before being interrupted. Resolve this yourself (there is no
  paper-text answer beyond what's already in
  `runs/b7h3_round2_20261021/config/visium_data_provenance.md`) and document
  the interpretation explicitly as a stated assumption, not a silent guess.

**Disk quota note:** this filesystem has a 200GB **per-user** quota
(separate from overall filesystem capacity -- `df -h` will look fine even
when this quota is exceeded; check with `beegfs-ctl --getquota --uid
$(whoami) --csv` if you suspect a write is failing silently or with
"Disk quota exceeded"). Currently ~9GB of headroom. Large intermediate
files (full h5ad atlases, LIANA universes, cell2location checkpoints) can
consume this fast -- clean up intermediate files you no longer need as you
go, and flag if headroom gets tight rather than letting a write fail
silently.

Continue exactly as instructed before: finish Wave 2, spatial-neighborhood
analysis, scientific-reviewer pass (checking data/scripts/figures directly),
final synthesis, panel-by-panel comparison to the paper, workflow diagram,
README/repo update and push. No approval checkpoint needed.
