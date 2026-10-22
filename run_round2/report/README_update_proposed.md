# Proposed top-level README addition (blocked by run write policy)

The session's write hook restricts file writes to the delivery run directory, so
`/mnt/beegfs/xqinag/projects/TheVirtualBiotech/README.md` could not be edited
from this run. The exact text below is ready to paste into the repository
README.

**Insertion point:** immediately after the navigation line
`[Setup](#setup) · [CLI](#running-the-cli) · [Web interface (optional)](#running-gradio) · [Architecture](#architecture) · [Apptainer](#apptainer-linux-cluster-only)`
and before `## Setup`.

```markdown
## Case study: B7-H3 (CD276) in lung cancer

A reproducible case study re-runs the analyses behind a published B7-H3 target
assessment and compares each figure panel against the paper's claims. The
Round 2 delivery (2026-10-22) is at:

```text
runs/20261022-010102-round-2-of-the-b7-h3-cd276-case-76d40ca3/
├── report/FINAL_REPORT.md                  # synthesis and target assessment
├── report/panel_by_paper_comparison.md     # claim-by-claim comparison
├── report/workflow_diagram.svg             # analysis and review workflow
├── evidence/claims.json                    # 15 claim–evidence objects
└── work/<agent>/                           # staged evidence tables and reports
```

Headline result: CD276 is a **low-confidence, expression-defined target**. It
has no LUAD/SCLC germline genetic support (0/8 credible sets, 0/67 L2G), is not
tumour-restricted (36.5% detection in normal lung macrophages, 30.8% in LUAD
fibroblasts), is not differentially expressed in any of 15 disease-vs-normal
contrasts, and is not essential in cancer cell lines. The TCGA LUAD survival
association reproduces only unadjusted (OS HR 1.80, p = 0.0051) and is not
independent of stage (adjusted OS p = 0.106). The reported "immune-hot" spatial
niche is a capture-depth/edge artifact; the depth-robust composition signal is
malignant enrichment with endothelial and NK/macrophage depletion.

Run outputs are generated locally and are not committed (see `.gitignore`).
To inspect the run, open `report/FINAL_REPORT.md`, then `README.md` or
`audit.html` in the run directory, or verify it with
`python run_vbt.py verify <RUN_ID>`. The source paper is available at
[paper2agent.ai/virtualbiotech](https://paper2agent.ai/virtualbiotech).
```

## How to apply

From the repository root:

```bash
python tools/apply_readme_case_study.py  # if a helper is added, otherwise paste manually
```

or paste the block manually at the insertion point above, then:

```bash
git add README.md
git commit -m "Add B7-H3 (CD276) Round 2 case study to README"
git push
```

`runs/` is gitignored, so the case-study outputs themselves stay local; only
the README pointer is committed.
