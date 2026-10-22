"""Pseudobulk differential expression (Panel 4C).

Design:
  Primary contrast  : disease vs normal within cell type, run separately for
                      LUAD and SCLC. Design ~ condition. Restricted to dataset
                      576f193c, the only dataset containing both tumour and
                      normal lung from the same study.
  Paired sensitivity: LUAD only, the 3 donors with both tumour and adjacent
                      normal (RU675/RU682/RU684). Design ~ donor + condition.

Aggregation: RAW counts summed by donor x cell type x condition. Condition is
part of the key because the three paired donors contribute the same cell type
under both tumour and normal; merging them would create one pseudobulk with an
arbitrary label. Pseudobulk retained if it has >=10 cells; a contrast is tested
only if >=3 donors per group.
Thresholds: FDR < 0.05 and |log2FC| > 0.5. Full results (all genes) are saved.
"""
import gc
import warnings
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

BASE = Path(__file__).resolve().parents[2]
PROC = BASE / "data/processed"
TAB = BASE / "results/tables"
MIN_CELLS = 10
MIN_DONORS = 3
DE_DATASET = "576f193c-75d0-4a11-bd25-8676587e6dc2"

adata = ad.read_h5ad(PROC / "scrna_luad_sclc_integrated.h5ad")
adata = adata[adata.obs.dataset_id.astype(str) == DE_DATASET].copy()
gc.collect()
adata.obs["cell_type"] = adata.obs["cell_type"].astype(str)
adata.obs["disease"] = adata.obs["disease"].astype(str)
adata.obs["donor_id"] = adata.obs["donor_id"].astype(str)
counts = adata.layers["counts"].tocsr()
genes = adata.var_names.astype(str).to_numpy()
# obs_names -> row position in the FULL counts matrix. Subsets (by disease, by
# cell type) get positions 0..n-1 locally, so positions must be resolved against
# the parent object before indexing `counts`.
POS = pd.Series(np.arange(adata.n_obs), index=adata.obs_names)
print("DE input:", adata.shape, "cell types", sorted(adata.obs.cell_type.unique()),
      flush=True)

HISTO = {"LUAD": "lung adenocarcinoma", "SCLC": "small cell lung carcinoma"}
PAIRED_LUAD = {"RU675", "RU682", "RU684"}

summary_rows, result_tables = [], []


def pseudobulk(sub):
    """Return (samples x genes DataFrame, sample metadata)."""
    rows, meta = [], []
    for (donor, ct, cond), g in sub.obs.groupby(
            ["donor_id", "cell_type", "disease"], observed=True):
        if len(g) < MIN_CELLS:
            continue
        idx = POS.loc[g.index].to_numpy()
        vec = np.asarray(counts[idx].sum(axis=0)).ravel()
        rows.append(vec)
        meta.append(dict(sample=f"{donor}__{ct}__{cond}", donor_id=donor,
                         cell_type=ct, condition=cond, n_cells=len(g)))
    if not rows:
        return None, None
    M = pd.DataFrame(meta).set_index("sample")
    X = pd.DataFrame(np.vstack(rows), columns=genes, index=M.index)
    return X, M


def run_deseq(X, M, design, contrast, histology, cell_type, analysis):
    dds = DeseqDataSet(counts=X.round().astype(int), metadata=M, design=design,
                       refit_cooks=True, quiet=True)
    dds.deseq2()
    st = DeseqStats(dds, contrast=contrast, quiet=True)
    st.summary()
    res = st.results_df.copy()
    res.index.name = "gene"
    res = res.reset_index()
    res["histology"] = histology
    res["cell_type"] = cell_type
    res["analysis"] = analysis
    res["contrast"] = "disease_vs_normal"
    res["design"] = design
    res["n_disease_donors"] = int(M[M.condition == contrast[1]].donor_id.nunique())
    res["n_normal_donors"] = int(M[M.condition == contrast[2]].donor_id.nunique())
    res["significant"] = (res["padj"] < 0.05) & (res["log2FoldChange"].abs() > 0.5)
    return res


for hist, dis in HISTO.items():
    sub = adata[adata.obs.disease.isin([dis, "normal"])].copy()
    for ct in sorted(adata.obs.cell_type.unique()):
        s = sub[sub.obs.cell_type == ct].copy()
        if len(s) == 0:
            continue
        X, M = pseudobulk(s)
        if X is None:
            summary_rows.append(dict(histology=hist, cell_type=ct, analysis="primary_all_donors",
                                     status="skipped", reason="no pseudobulk with >=10 cells",
                                     n_disease_donors=0, n_normal_donors=0,
                                     n_disease_cells=int((s.obs.disease == dis).sum()),
                                     n_normal_cells=int((s.obs.disease == "normal").sum())))
            print("SKIP", hist, ct, "no pseudobulk", flush=True)
            continue
        nd = M[M.condition == dis].donor_id.nunique()
        nn = M[M.condition == "normal"].donor_id.nunique()
        row = dict(histology=hist, cell_type=ct, analysis="primary_all_donors",
                   n_disease_donors=int(nd), n_normal_donors=int(nn),
                   n_disease_cells=int((s.obs.disease == dis).sum()),
                   n_normal_cells=int((s.obs.disease == "normal").sum()))
        if nd < MIN_DONORS or nn < MIN_DONORS:
            row.update(status="skipped",
                       reason=f"fewer than {MIN_DONORS} donors in a group (disease={nd}, normal={nn})")
            summary_rows.append(row)
            print("SKIP", hist, ct, row["reason"], flush=True)
            continue
        try:
            res = run_deseq(X, M, "~condition", ["condition", dis, "normal"],
                            hist, ct, "primary_all_donors")
            result_tables.append(res)
            row.update(status="tested", reason="", n_genes_tested=int(res["pvalue"].notna().sum()),
                       n_significant=int(res["significant"].sum()))
            summary_rows.append(row)
            print("TESTED", hist, ct, "samples", X.shape[0], "sig",
                  int(res["significant"].sum()), flush=True)
        except Exception as e:
            row.update(status="failed", reason=str(e)[:300])
            summary_rows.append(row)
            print("FAILED", hist, ct, repr(e)[:200], flush=True)

# ---- paired LUAD sensitivity (3 donors with tumour + adjacent normal) ----
sub = adata[(adata.obs.disease.isin([HISTO["LUAD"], "normal"])) &
            (adata.obs.donor_id.isin(PAIRED_LUAD))].copy()
for ct in sorted(adata.obs.cell_type.unique()):
    s = sub[sub.obs.cell_type == ct].copy()
    if len(s) == 0:
        continue
    X, M = pseudobulk(s)
    if X is None:
        continue
    # every donor must contribute both conditions
    both = M.groupby("donor_id").condition.nunique()
    if (both != 2).any() or M.condition.nunique() < 2 or len(both) < MIN_DONORS:
        summary_rows.append(dict(histology="LUAD", cell_type=ct, analysis="paired_3donors",
                                 status="skipped", reason="not all 3 paired donors have both conditions",
                                 n_disease_donors=int(M[M.condition == HISTO['LUAD']].donor_id.nunique()),
                                 n_normal_donors=int(M[M.condition == "normal"].donor_id.nunique()),
                                 n_disease_cells=int((s.obs.disease == HISTO['LUAD']).sum()),
                                 n_normal_cells=int((s.obs.disease == "normal").sum())))
        print("PAIRED SKIP", ct, flush=True)
        continue
    try:
        res = run_deseq(X, M, "~donor_id + condition", ["condition", HISTO["LUAD"], "normal"],
                        "LUAD", ct, "paired_3donors")
        result_tables.append(res)
        summary_rows.append(dict(histology="LUAD", cell_type=ct, analysis="paired_3donors",
                                 status="tested", reason="",
                                 n_disease_donors=int(M[M.condition == HISTO['LUAD']].donor_id.nunique()),
                                 n_normal_donors=int(M[M.condition == "normal"].donor_id.nunique()),
                                 n_disease_cells=int((s.obs.disease == HISTO['LUAD']).sum()),
                                 n_normal_cells=int((s.obs.disease == "normal").sum()),
                                 n_genes_tested=int(res["pvalue"].notna().sum()),
                                 n_significant=int(res["significant"].sum())))
        print("PAIRED TESTED", ct, "sig", int(res["significant"].sum()), flush=True)
    except Exception as e:
        summary_rows.append(dict(histology="LUAD", cell_type=ct, analysis="paired_3donors",
                                 status="failed", reason=str(e)[:300],
                                 n_disease_donors=int(M[M.condition == HISTO['LUAD']].donor_id.nunique()),
                                 n_normal_donors=int(M[M.condition == "normal"].donor_id.nunique()),
                                 n_disease_cells=int((s.obs.disease == HISTO['LUAD']).sum()),
                                 n_normal_cells=int((s.obs.disease == "normal").sum())))
        print("PAIRED FAILED", ct, repr(e)[:200], flush=True)

summ = pd.DataFrame(summary_rows)
summ.to_csv(TAB / "scrna_pseudobulk_de_sample_summary.csv", index=False)
print("WROTE summary", summ.shape, flush=True)

if result_tables:
    full = pd.concat(result_tables, ignore_index=True)
else:
    full = pd.DataFrame()
cols = ["histology", "cell_type", "analysis", "contrast", "design", "gene",
        "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj",
        "n_disease_donors", "n_normal_donors", "significant"]
full = full[[c for c in cols if c in full.columns]]
full.to_csv(TAB / "scrna_pseudobulk_de_luad_sclc.csv", index=False)
print("WROTE", TAB / "scrna_pseudobulk_de_luad_sclc.csv", full.shape, flush=True)
print(summ.to_string(), flush=True)
