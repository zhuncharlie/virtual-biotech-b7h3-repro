# Tahoe-100M Round-2 Status: B7-H3 (CD276) Drug-Perturbation Track

**Agent:** functional-genomics-analyst
**Original analysis run:** 20261021-080518 (Round 2, B7-H3 / CD276, LUAD + SCLC)
**Revision 2 run:** 20261021-204038 (`a9b7a6f8`), documentation corrections after scientific review
**Date:** 2026-10-21 (Revision 2)
**Track status:** `BLOCKED` for differential-expression queries (data-availability failure); `PARTIAL SUCCESS` for metadata-level scope questions.
**Materiality:** **not assessable / no evidence either way.** This is not a zero-result query and not evidence of absence. Whether the missing DE evidence could have changed the therapeutic assessment is a synthesis-level judgement left to the CSO.

---

## 1. Bottom line

The Tahoe-100M drug-perturbation tools remain unavailable in this run. All three MCP calls failed before reading any data with the same server-level error:

> `Query failed: TAHOE_DATA_PATH not set in environment. Set it to the directory containing Tahoe pseudobulk parquet files.`

I confirmed this is a server-configuration gap, not a query problem. The availability probe selected two PIDs (**35177**, **35204**) by matching `functional_genomics_mcp/server.py` in `/proc/<pid>/cmdline`; for both, the readable `/proc/<pid>/environ` contained `OPEN_TARGETS_DATA_PATH` but **no** `TAHOE_DATA_PATH`. The saved diagnostic records each PID and its selected environment variables, **not** the command line, so the process identity rests on the probe's selection rule rather than on a stored cmdline. No prepared Tahoe pseudobulk directory was found in the searched project/data tree (depth 4). The MCP server environment is fixed at launch and cannot be modified per call from this agent.

An alternative route through the official Hugging Face release (the source named in `docs/TAHOE_SETUP.md`, pinned revision `2dc57900`) was reachable for the four small **metadata** tables. That allowed two narrow, positive-scope checks (Section 4). The differential-expression payload is 1,026 shards totalling **82.76 GiB**, and the official viewer filter index was still loading (HTTP 500) after repeated retries, so **no CD276 perturbation effect was retrieved**.

---

## 2. Exact MCP attempts (verbatim errors)

| Timestamp (run-local) | Tool | Parameters | Error | Tool-use ID |
|---|---|---|---|---|
| 2026-10-21T08:11:59 | `find_drugs_affecting_gene` | `gene_name="CD276"`, `min_abs_log2fc=0.5`, `max_padj=0.1`, `top_n=20` | `TAHOE_DATA_PATH not set in environment` | `call_00_QOwTuGG0ASqvlmNaDdZ47100` |
| 2026-10-21T08:13:34 | `query_drug_perturbation` | `drug_name="Enoblituzumab"`, `top_n=10` | `TAHOE_DATA_PATH not set in environment` | `call_00_wxpLp5EAl1TkeqIlZopg8474` |
| 2026-10-21T08:13:37 | `query_drug_perturbation` | `drug_name="Ifinatamab deruxtecan"`, `top_n=10` | `TAHOE_DATA_PATH not set in environment` | `call_00_ET_MG07lgYnHElLXjHKsqDS7995` |

Full attempt-by-attempt record, including diagnostics and alternative endpoints: `results/tables/tahoe_round2_attempt_log.csv`.

---

## 3. What was tried to fix it

1. **Environment inspection.** `TAHOE_DATA_PATH=None` in the agent process. The probe identified two server PIDs (35177, 35204) by cmdline match; the saved diagnostic records only their PIDs and the selected environment variables (`OPEN_TARGETS_DATA_PATH` present, `TAHOE_DATA_PATH` absent). The server environment is fixed at launch; it cannot be restarted from this agent.
2. **Local data search.** Project tree and `/mnt/beegfs/xqinag/data` searched to depth 3-4: only `docs/TAHOE_SETUP.md` and `tools/prepare_tahoe.py` exist; no prepared parquet shards.
3. **Alternative tool/endpoint.** Hugging Face Hub API and `hf_hub_download` (official client, documented in `TAHOE_SETUP.md`) were available. The four metadata tables were downloaded; the dataset-viewer `/filter` and `/search` endpoints were tested for server-side filtering of `gene_name='CD276'`.
4. **Retry outcomes.** Metadata route: success. Viewer filter: HTTP 502 on first call, then HTTP 500 `"the dataset index is loading, this may take longer than usual"` on two subsequent attempts (last at 08:24:03). This was not resolved within the non-blocking track.
5. **Bulk download considered and rejected.** The DE release is 1,026 unlabeled shards (48-99 MB each; median 84.6 MB), 82.76 GiB total, with no manifest mapping a gene or drug to a shard. A random subset would not give a focused B7-H3 analysis. Download was not attempted.

Diagnostic JSON: `data/processed/tahoe_environment_diagnostic.json`
Shard inventory: `data/raw/tahoe_de_shard_inventory.csv`

---

## 4. Bounded metadata-level results (partial success)

**Data source:** Tahoe-100M metadata tables, `tahoebio/Tahoe-100M`, revision `2dc57900b7981cfcf5e211527169a0b006546a95`, official Hugging Face release. **Cancer cell lines only.** This is metadata scope, **not** differential expression.

1. **CD276 is represented in the Tahoe-100M gene vocabulary.** `gene_symbol = CD276`, `ensembl_id = ENSG00000103855`, `token_id = 2859`, in a 62,710-gene vocabulary. A DE query for CD276 is therefore well-defined once the shards are accessible.
2. **No B7-H3-targeted agent is in the Tahoe-100M drug panel.** Of 379 unique drugs in `drug_metadata` (380 distinct drug names in `sample_metadata`), **none** annotate CD276 as a target and **none** match any of 12 B7-H3 agent aliases (enoblituzumab/MGA271, ifinatamab/DS-7300, vobramitamab/MGC018, omburtamab/8H9, B7-H3/B7H3/CD276) in any text field. The `targets` field is null for **115** drugs and non-null for **264**. A direct audit of the parquet found **0** empty or whitespace-only strings among the 379 values, so in this release `targets.notna()` (264) happens to equal the number of non-blank annotations; the equality is verified here, not assumed. The 115 unannotated drugs are the scope limit: this is a statement about the annotated panel, not proof that no B7-H3 molecule was screened.
3. **Lung-line context for a future DE analysis.** 27 Tahoe-100M cell lines are lung; 22 map to the Round-1 DepMap table, and all 22 have CD276 expression: **11 LUAD, 1 SCLC, and 10 other** (9 "Other NSCLC" + SW 1271, annotated "Other lung (SMARCA4-dUT)"). The other 5 lung lines are unmatched to Round-1 DepMap. CD276 is expressed across these lines (DepMap relative units, range 3.45-7.25), consistent with Round 1.

**What this does NOT establish:** whether any drug changes CD276 expression; the direction, magnitude, or significance of any perturbation effect; or anything about B7-H3-targeted agent activity. Those require the DE shards and remain **unassessed**.

Artifacts:
- `results/tables/tahoe_drug_panel_b7h3_check.csv`
- `results/tables/tahoe_drug_targets_annotation_audit.csv`
- `results/tables/tahoe_metadata_scope_summary.json`
- `results/tables/tahoe_lung_cell_lines_cd276_context.csv`
- `results/tables/tahoe_lung_histology_recount.csv`
- `results/tables/tahoe_cell_lines_cd276_context.csv`
- `results/figures/tahoe_lung_lines_cd276_expression.png`

---

## 5. Materiality: not assessable / no evidence either way

This is a **DATA GAP / failed query**, not a zero result. The correct statements are:

- **Not established / not assessable:** whether any Tahoe-100M perturbation modulates CD276 expression. No DE rows were read, so the effect-size question has no answer in this run.
- **No evidence either way:** this analysis provides no evidence for or against CD276 modulatability. It neither supports nor excludes a perturbation effect.
- **Unknown:** the transcriptional consequences of B7-H3-directed agents in these models (no such agent appears in the annotated panel metadata).
- **Not evidence of absence:** the failure says nothing about CD276 biology.

**What the data can support:** (i) CD276 is present in the Tahoe-100M gene vocabulary (ENSG00000103855, token 2859), so a DE query is well-defined; (ii) the annotated 379-drug panel contains no B7-H3-targeted agent under 12 aliases.

**What the data cannot support:** any statement about whether a drug changes CD276 expression, in either direction or at any effect size; any claim that Tahoe-100M lacks such an effect; or any claim that a CD276 perturbation effect would not alter a therapeutic conclusion.

Whether this gap is material to the therapeutic recommendation is a synthesis-level judgement that this dataset cannot make. It is left to the CSO. The gap must not be converted into a negative claim about CD276 modulatability.

---

## 6. Round-1 DepMap artifacts: independently re-confirmed and citable

I re-verified the Round-1 DepMap artifacts against their own saved files (no DepMap re-query; no defect found). All **54/54** checks pass (`results/tables/round1_depmap_verification.csv`):

| Group | n | Mean gene effect | Median |
|---|---:|---:|---:|
| LUAD | 46 | -0.230341 | -0.244609 |
| SCLC | 25 | -0.203976 | -0.181303 |
| Other NSCLC | 52 | -0.238402 | -0.246530 |
| Other lineages | 1,041 | -0.220980 | -0.212492 |
| Non-cancerous | 16 | -0.163260 | -0.142390 |

**Essentiality framing for synthesis (threshold stated explicitly).** CD276 mean gene effect is **−0.230 in LUAD (n = 46)** and **−0.204 in SCLC (n = 25)**. Using the standard threshold (gene effect < −0.5 = essential; −0.5 to 0 = weak/neutral; > 0 = not essential), **1/46 LUAD lines and 0/25 SCLC lines fall below −0.5**. Any statement that CD276 is "not essential" must carry these values, the line counts and the threshold. DepMap covers **cancer cell lines only**; it cannot assess normal-tissue essentiality, and these values say nothing about safety in normal cells.

Checks include: 71-row LUAD+SCLC table (46 + 25) with 71 unique DepMap IDs and no missing gene effect; 1,183-row all-lines table with 1,183 unique IDs; group counts sum to 1,183, matching the raw JSON `num_cell_lines` and the sum of tissue counts; every group mean/median reproduced to 1e-9 against the saved summary; 78 disease-comparator rows summing to 1,183; all nine tables and both figure files present and non-empty. **The Round-1 DepMap tables are citable as-is.** Limitation unchanged: DepMap is cancer cell lines only.

Recomputed summary: `results/tables/round1_depmap_recomputed_group_summary.csv`

---

## 7. Reproduction

The three scripts were re-pointed in Revision 2: they now resolve all input and output paths from their own location (`Path(__file__).resolve().parents[2]`), so they run from this workspace and no longer write into an older run directory.

```bash
source /mnt/beegfs/xqinag/projects/TheVirtualBiotech/activate.sh
cd /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8/work/functional-genomics-analyst
python code/scripts/verify_round1_depmap.py                    # local; 54/54 checks
python code/scripts/tahoe_metadata_representation_analysis.py  # local; reads copied metadata parquet
python code/scripts/audit_tahoe_drug_targets_annotation.py     # local; null-vs-blank targets audit
python code/scripts/recount_tahoe_lung_histology.py            # local; lung histology recount
# python code/scripts/tahoe_round2_probe.py                    # network: re-lists the HF shard tree
```

Note: `source activate.sh` returns status 1 when `setup_mcp.py` is absent, so use `;` rather than `&&` before the Python command. The probe was **not** re-run for Revision 2 (it contacts the Hugging Face Hub); its saved outputs are the byte-identical copies described in Section 8. Re-running the three local scripts reproduced every CSV and JSON with unchanged md5 checksums.

---

## 8. Provenance and data availability (Revision 2)

All inputs needed by the scripts are now present in this workspace. Nothing must be read from the source run at execution time. Files were copied byte-for-byte from the read-only source run `20261021-113551-...-ef6e8b35` (Tahoe inputs) and from the Round-1 run `20261020-085513-...-a03f0a23` (DepMap inputs); no download was performed for any of them.

| Local path | Origin | md5 |
|---|---|---|
| `data/processed/tahoe_environment_diagnostic.json` | SOURCE `ef6e8b35` | `bde6397f160e3ca56315af033351c80f` |
| `data/raw/tahoe_de_shard_inventory.csv` | SOURCE `ef6e8b35` | `95f08b5442e7e79750cbd0637824888b` |
| `data/raw/tahoe_metadata/metadata/cell_line_metadata.parquet` | SOURCE `ef6e8b35`; HF revision `2dc57900` | `c12c62f1fa52aa64ff386b85f20b2e7c` |
| `data/raw/tahoe_metadata/metadata/drug_metadata.parquet` | SOURCE `ef6e8b35`; HF revision `2dc57900` | `5fbfd0673ef41adf55ab86fa9ad43fc4` |
| `data/raw/tahoe_metadata/metadata/gene_metadata.parquet` | SOURCE `ef6e8b35`; HF revision `2dc57900` | `81ba69ebfe1e0471e508ed2c8851ea5d` |
| `data/raw/tahoe_metadata/metadata/sample_metadata.parquet` | SOURCE `ef6e8b35`; HF revision `2dc57900` | `bcb607a7af1bbcf94aa5726eb1ecc35c` |
| `data/raw/round1_depmap_inputs/` (9 tables, 1 raw JSON, 2 figures) | Round-1 run `20261020-085513` | copy of originals; see directory |

Source-run path for reference: `/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/functional-genomics-analyst/`.

The figure `results/figures/tahoe_lung_lines_cd276_expression.png` plots round-1 DepMap CD276 expression for the Tahoe lung lines; its title says so and it is **not** a Tahoe-100M expression measurement.

---

## 9. Revision 2 changelog (old → new)

| # | Location (old) | Old | New | Reason |
|---|---|---|---|---|
| 1 | Header, `Materiality` | "**NON-MATERIAL data gap.** ... not a limitation of the therapeutic recommendation." | "**not assessable / no evidence either way.** ... materiality left to the CSO." | Reviewer: materiality is an effect-size judgement; DE was never assessed. |
| 2 | §5 bullet "Non-material" | "the Round-1/Round-2 DepMap essentiality conclusion and the therapeutic assessment are independent of Tahoe." | Removed. Replaced by explicit "what the data can support / cannot support" statements. | The independence claim is synthesis-level, not a data claim. |
| 3 | §4.3 | "10 LUAD, 1 SCLC, 11 other NSCLC" | "**11 LUAD, 1 SCLC, 10 other** (9 Other NSCLC + SW 1271, 'Other lung (SMARCA4-dUT)'); 22 matched, 5 unmatched" | Recounted from `tahoe_lung_cell_lines_cd276_context.csv`. |
| 4 | §1 and §3.1 | "both running `functional_genomics_mcp/server.py` processes (PIDs 35177, 35204)" | "two PIDs (35177, 35204) selected by a cmdline match on `functional_genomics_mcp/server.py`; the diagnostic stores PIDs and selected env vars, not cmdlines" | The artifact does not store command lines; state only what is evidenced. |
| 5 | §3.1 | "170 inherited variables checked" | Removed | Not recorded in any saved artifact. |
| 6 | §4.2 | "`n_drugs_with_annotated_target` ... target annotation is absent for 115/379" without defining the metric | "`targets` null for 115, non-null for 264; audit found 0 empty/whitespace strings, so `notna()` equals non-blank annotations in this release" | `notna()` alone does not distinguish null from `""`; now audited directly. |
| 7 | §6 | No explicit essentiality numbers in the narrative | Added: mean gene effect −0.230 LUAD (n=46), −0.204 SCLC (n=25); 1/46 and 0/25 below −0.5; threshold defined; cancer-cell-line-only caveat | Prevents the synthesis from making an unsupported "not essential" claim. |
| 8 | §7 | `cd` into run `20261021-080518-...-27ef6dcf` | `cd` into this run `20261021-204038-...-a9b7a6f8` | Reproduction must target the live workspace. |
| 9 | Scripts | `WORK`/`OUT_T` hardcoded to run `20261021-080518-...-27ef6dcf` and Round-1 path `20261020-085513` | Paths resolved from `__file__`; inputs copied into `data/raw/` and `data/raw/round1_depmap_inputs/` | Self-containment; no writing into another run. |
| 10 | Report | Cited `data/processed/...` and `data/raw/...` files absent from the live run | Files materialized in this workspace; paths and md5s tabulated in §8 | Dangling citations. |
