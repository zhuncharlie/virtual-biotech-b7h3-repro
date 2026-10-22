"""Summarise LUAD / SCLC / normal-lung Census metadata: datasets, donors, cell types."""
import pandas as pd

BASE = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/single-cell-analyst"

def load(path):
    df = pd.read_parquet(path)
    for c in ["dataset_id", "donor_id", "cell_type", "assay", "disease", "tissue"]:
        df[c] = df[c].astype(str)
    return df

luad = load(f"{BASE}/data/raw/luad_lung_cell_metadata.parquet")
sclc = load(f"{BASE}/data/raw/sclc_lung_cell_metadata.parquet")
norm = load(f"{BASE}/data/raw/normal_lung_cell_metadata.parquet")

for name, df in [("LUAD", luad), ("SCLC", sclc), ("NORMAL_LUNG", norm)]:
    print(f"\n=== {name}: {len(df):,} cells | {df.dataset_id.nunique()} datasets | {df.donor_id.nunique()} donors "
          f"| primary={int((df.is_primary_data == True).sum()):,} ===")
    if name != "NORMAL_LUNG":
        primary = df[df.is_primary_data == True]
        print(f"    primary-only: {len(primary):,} cells | {primary.dataset_id.nunique()} datasets | {primary.donor_id.nunique()} donors")
        g = (primary.groupby("dataset_id")
             .agg(cells=("cell_type", "size"), donors=("donor_id", "nunique"),
                  cell_types=("cell_type", "nunique"))
             .sort_values("cells", ascending=False))
        print(g.to_string())
        print("  Assays:", primary.assay.value_counts().to_dict())
        print("  Cell types (primary cells):")
        ct = (primary.groupby("cell_type")
              .agg(cells=("cell_type", "size"), donors=("donor_id", "nunique"))
              .sort_values("cells", ascending=False))
        print(ct.to_string())

luad_ds, sclc_ds, norm_ds = set(luad.dataset_id), set(sclc.dataset_id), set(norm.dataset_id)
print(f"\n=== Datasets containing BOTH LUAD and normal lung: {len(luad_ds & norm_ds)} ===")
for d in sorted(luad_ds & norm_ds):
    l, n = luad[luad.dataset_id == d], norm[norm.dataset_id == d]
    ld, nd = set(l.donor_id), set(n.donor_id)
    print(f"{d}: LUAD {len(l):,} cells/{l.donor_id.nunique()} donors | normal {len(n):,} cells/{n.donor_id.nunique()} donors | shared donor ids: {len(ld & nd)}")
print(f"\n=== Datasets containing BOTH SCLC and normal lung: {len(sclc_ds & norm_ds)} -> {sorted(sclc_ds & norm_ds)} ===")
print(f"=== SCLC datasets (all, incl non-primary): ===")
print(sclc.groupby('dataset_id').agg(cells=('cell_type','size'), donors=('donor_id','nunique'), primary=('is_primary_data', lambda s: int((s==True).sum()))).sort_values('cells', ascending=False).to_string())
print(f"\n=== LUAD datasets (all, incl non-primary): ===")
print(luad.groupby('dataset_id').agg(cells=('cell_type','size'), donors=('donor_id','nunique'), primary=('is_primary_data', lambda s: int((s==True).sum()))).sort_values('cells', ascending=False).to_string())
