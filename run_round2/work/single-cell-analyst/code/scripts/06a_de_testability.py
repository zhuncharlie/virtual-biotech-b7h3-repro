"""Which disease-vs-normal contrasts are testable, per cell type.

For the DE dataset (576f193c) count, per cell type x disease, the cells and the
number of donors contributing a pseudobulk of >=10 cells. A contrast is testable
when >=3 donors are available in BOTH groups (the threshold used in 06).

Output: results/tables/scrna_de_testability_by_celltype.csv
"""
from pathlib import Path

import anndata as ad
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
PROC = BASE / "data/processed"
TAB = BASE / "results/tables"
DE_DATASET = "576f193c-75d0-4a11-bd25-8676587e6dc2"
MIN_CELLS, MIN_DONORS = 10, 3
DIS = ["lung adenocarcinoma", "small cell lung carcinoma", "normal"]

# The pre-integration intermediate was deleted to reclaim BeeGFS quota; the
# integrated atlas carries the same obs metadata and is read backed (obs only).
a = ad.read_h5ad(PROC / "scrna_luad_sclc_integrated.h5ad", backed="r")
obs = a.obs.copy()
a.file.close()
obs = obs[obs.dataset_id.astype(str) == DE_DATASET]

rows = []
for ct in sorted(obs.cell_type.astype(str).unique()):
    s = obs[obs.cell_type.astype(str) == ct]
    rec = {"cell_type": ct}
    for dis in DIS:
        g = s[s.disease.astype(str) == dis]
        per_donor = g.groupby("donor_id", observed=True).size()
        rec[f"n_cells_{dis}"] = int(len(g))
        rec[f"n_donors_{dis}"] = int(per_donor.shape[0])
        rec[f"n_donors_ge{MIN_CELLS}_{dis}"] = int((per_donor >= MIN_CELLS).sum())
    for hist, dis in [("LUAD", "lung adenocarcinoma"),
                      ("SCLC", "small cell lung carcinoma")]:
        nd = rec[f"n_donors_ge{MIN_CELLS}_{dis}"]
        nn = rec[f"n_donors_ge{MIN_CELLS}_normal"]
        rec[f"testable_{hist}_vs_normal"] = bool(nd >= MIN_DONORS and nn >= MIN_DONORS)
        rec[f"reason_{hist}"] = "" if rec[f"testable_{hist}_vs_normal"] else (
            f"disease donors with >= {MIN_CELLS} cells = {nd}, "
            f"normal donors with >= {MIN_CELLS} cells = {nn}")
    rows.append(rec)

out = pd.DataFrame(rows).sort_values("cell_type")
out.to_csv(TAB / "scrna_de_testability_by_celltype.csv", index=False)
print(out[["cell_type", "n_donors_ge10_lung adenocarcinoma",
           "n_donors_ge10_normal", "n_donors_ge10_small cell lung carcinoma",
           "testable_LUAD_vs_normal", "testable_SCLC_vs_normal"]].to_string(index=False))
