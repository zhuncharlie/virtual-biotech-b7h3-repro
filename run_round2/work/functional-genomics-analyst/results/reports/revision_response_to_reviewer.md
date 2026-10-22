# Revision 2: Response to Scientific Review

**Document revised:** `results/reports/tahoe_round2_status.md`
**Review:** `work/scientific-reviewer/scientific_review_interim_panels1-6.md`, Section 5 and the cross-panel failure-pattern note
**Revision run:** 20261021-204038 (`a9b7a6f8`)
**Scope:** documentation accuracy only. No downloads, no `pip install`, no large recomputation. Two small local recounts/audits were run against already-saved inputs.

| # | Reviewer item | Status | What changed / reason |
|---|---|---|---|
| 1 | Lung histology counts off by one: report said 10 LUAD / 1 SCLC / 11 other NSCLC | **DONE** | Recounted directly from `results/tables/tahoe_lung_cell_lines_cd276_context.csv` (27 rows, 22 matched to Round-1 DepMap): **11 LUAD, 1 SCLC, 10 other** = 9 "Other NSCLC" + SW 1271 "Other lung (SMARCA4-dUT)". The other 5 lung lines are unmatched and have no histology group in this table. Corrected in §4.3. Evidence: `results/tables/tahoe_lung_histology_recount.csv`; script `code/scripts/recount_tahoe_lung_histology.py`. |
| 2 | Remove "NON-MATERIAL data gap"; use "not assessable / no evidence either way"; soften "the therapeutic assessment is independent of Tahoe" | **DONE** | Header materiality label replaced with "**not assessable / no evidence either way**". §5 retitled and rewritten: the DE question is "not established / not assessable"; the analysis gives "no evidence either way". The "independent of Tahoe" sentence is removed and replaced by explicit "what the data can support" (CD276 in vocabulary; no B7-H3 agent in the annotated panel) and "what the data cannot support" (any perturbation effect, any negative claim, any materiality conclusion). Materiality is explicitly left to the CSO. |
| 3 | Make DepMap context explicit wherever "not essential" is implied, with −0.230 (LUAD), −0.204 (SCLC), 1/46 below −0.5 | **DONE** | The report did not previously make an explicit essentiality claim, so per instruction a sentence was added in §6: mean gene effect **−0.230 LUAD (n=46)**, **−0.204 SCLC (n=25)**; **1/46 LUAD and 0/25 SCLC** below the **−0.5** threshold; threshold definitions stated; cancer-cell-line-only limitation restated. No "not essential" claim is made by this report. Values verified in `results/tables/round1_depmap_recomputed_group_summary.csv`. |
| 4a | Hardcoded `R0` / `ef6e8b35` paths in copied scripts | **DONE (with clarification)** | No `ef6e8b35` or `R0` path existed in the copied scripts. The hardcoded paths were to run `20261021-080518-...-27ef6dcf` (outputs) and the Round-1 run `20261020-085513-...-a03f0a23` (inputs). All three scripts now resolve paths from `Path(__file__).resolve().parents[2]`; Tahoe metadata and Round-1 inputs were copied byte-for-byte into this workspace under `data/raw/`. No script writes into another run. Re-running the local scripts reproduced all CSVs/JSON with unchanged md5. |
| 4b | Metadata parquet path and md5 if it must stay in SOURCE | **DONE** | The parquet no longer has to stay in SOURCE: the four tables were copied into `data/raw/tahoe_metadata/metadata/` and their md5s are tabulated in report §8 (`cell_line` `c12c62f1…`, `drug` `5fbfd067…`, `gene` `81ba69eb…`, `sample` `bcb607a7…`). The SOURCE path is also given. Diagnostic JSON and shard inventory were likewise materialized, with md5s. |
| 4c | Description of two `functional_genomics_mcp/server.py` processes overstates the artifact | **DONE** | §1 and §3 now say the probe selected two PIDs by matching `functional_genomics_mcp/server.py` in `/proc/<pid>/cmdline`, and that the saved diagnostic records only PIDs and selected environment variables (`OPEN_TARGETS_DATA_PATH` present, `TAHOE_DATA_PATH` absent), **not** command lines. The unsupported phrase "170 inherited variables checked" was removed because no artifact records it. |
| 4d | `n_drugs_with_annotated_target` description; `targets.notna()` may not distinguish null from empty string | **DONE** | Direct audit of `drug_metadata.parquet`: 379 rows; 115 null; **0** empty/whitespace-only strings; 264 non-blank. `notna()` = 264 therefore equals the non-blank count in this release, and the report now says the equality was verified rather than assumed. Evidence: `results/tables/tahoe_drug_targets_annotation_audit.csv`; script `code/scripts/audit_tahoe_drug_targets_annotation.py`. |
| 5 | Figure title "left axis: round-1 DepMap values" | **DONE (no change needed)** | Reviewer confirmed the title is accurate; the report now states explicitly in §8 that the figure is round-1 DepMap expression, not a Tahoe measurement. |

## Verification performed

- `python code/scripts/verify_round1_depmap.py` -> **PASS 54/54**, run against the local copies.
- `python code/scripts/tahoe_metadata_representation_analysis.py` -> re-ran locally against the copied parquet; all output CSV/JSON md5s identical to the reviewed versions.
- `python code/scripts/recount_tahoe_lung_histology.py` -> 11 LUAD / 1 SCLC / 9 Other NSCLC / 1 Other lung (SMARCA4-dUT) among 22 matched lines.
- `python code/scripts/audit_tahoe_drug_targets_annotation.py` -> 115 null, 0 blank, 264 non-blank.
- `tahoe_round2_probe.py` was **not** re-run because it contacts the Hugging Face Hub; its saved outputs were copied and checksummed.

## Not changed (and why)

- No DE query was attempted; the MCP failure is unchanged and no Tahoe differential-expression evidence exists.
- No new biological claim is made. The metadata-scope results (CD276 in the vocabulary; no B7-H3 agent in the annotated panel) are unchanged.
