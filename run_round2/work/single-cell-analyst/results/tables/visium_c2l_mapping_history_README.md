# Training-history tables: which file to use

**Revision 2.1 (2026-10-21).** No training-history CSV now exists in
`results/tables/`. Three 6-byte, header-only files were written by earlier runs:

| file | writer | status (verified 2026-10-21) |
|---|---|---|
| `visium_c2l_mapping_history.csv` | `code/scripts/visium_c2l_21_map_sections.py` (original mapping) | **removed** |
| `visium_c2l_mapping_history_rerun.csv` | `code/scripts/visium_c2l_21_map_sections_rerun.py` | **absent** (never written; guard fired) |
| `c2l_reference_training_history.csv` | `code/scripts/visium_c2l_20_train_reference.py` | **removed** |

Each contained only the column name `epoch` and no data rows. A header-only
file is not a training curve and must not be cited as one. **None remain as of
Revision 2.1.**

## Root cause of the reappearance

Script 21_rerun already had a non-empty guard, but scripts 20 and 21 (original)
called `hist.to_csv(...)` unconditionally. `mod.history` is populated from the
Lightning logger and is empty in scvi-tools 1.4 when `logger=False` (reference)
or before the logger flushes (mapping), so both writers emitted a header-only
CSV. Deleting the files without fixing those two writers is why two of the
three reappeared on a later run.

**Guard now applied in all three writers.** Each drops all-NaN history, writes
only when at least one non-empty row exists, and removes a stale empty file when
the history is empty. An empty history can no longer produce a header-only CSV.

## Where the ELBO traces actually are

| model | trace available? | location | rows |
|---|---|---|---|
| Spatial mapping, original 3,000-epoch run | yes | `logs/c2l_mapping_elbo_metrics_3000epoch.csv` (columns `elbo_train,epoch,step`) | 3,000 |
| Spatial mapping, re-run (corrected export) | yes | `logs/lightning/c2l_mapping_rerun/3000ep/metrics.csv` | 3,000 |
| Reference signature RegressionModel | no | none written | 0 |

The derived statistics (first/last ELBO, last-10% slope, percent of total
decrease reached by 90% of epochs) are in
`results/tables/visium_c2l_training_convergence.csv`; the figure is
`results/figures/figs5_c2l_training_convergence.png`.

## Why the CSVs were empty

`mod.history` in scvi-tools 1.4 is populated from the Lightning logger. In the
re-run script a `CSVLogger` was attached, so the per-epoch values were written by
Lightning under `logs/lightning/`, but `mod.history` itself was empty at the time
the table was written. The reference model was trained with `logger=False`, so no
values were persisted anywhere.

The reference model's history is therefore **not** recoverable: the model
completed 250/250 epochs (Lightning reported `max_epochs=250 reached`; 4,586.9 s,
18.3 s/epoch) but the loss values were never written. No curve is fabricated.
