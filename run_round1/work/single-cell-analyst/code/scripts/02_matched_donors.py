"""Inspect donor-level tumor/normal matching for LUAD and SCLC datasets."""
import pandas as pd
BASE = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/single-cell-analyst"
def load(p):
    df = pd.read_parquet(p)
    for c in ["dataset_id", "donor_id", "cell_type", "assay", "disease"]:
        df[c] = df[c].astype(str)
    return df
luad, sclc, norm = (load(f"{BASE}/data/raw/{n}_lung_cell_metadata.parquet") for n in ["luad", "sclc", "normal"])
for df in (luad, sclc, norm):
    df.drop(df[df.is_primary_data != True].index, inplace=True)

matched = sorted(set(luad.dataset_id) & set(norm.dataset_id))
print("=== matched datasets: donor overlap (donor x disease cell counts) ===")
for d in matched:
    l = luad[luad.dataset_id == d]
    n = norm[norm.dataset_id == d]
    shared = sorted(set(l.donor_id) & set(n.donor_id))
    print(f"\n-- dataset {d}: {l.donor_id.nunique()} LUAD donors, {n.donor_id.nunique()} normal donors, shared={shared}")
    if shared:
        sub = pd.concat([l[l.donor_id.isin(shared)].assign(cond="LUAD"),
                         n[n.donor_id.isin(shared)].assign(cond="normal")])
        tab = sub.pivot_table(index="donor_id", columns="cond", values="cell_type", aggfunc="size", fill_value=0)
        print(tab.to_string())
        print("  cell types per shared-donor normal sample:")
        for don, grp in n[n.donor_id.isin(shared)].groupby("donor_id"):
            print(f"    {don}: " + ", ".join(f"{k}({v})" for k, v in grp.cell_type.value_counts().items()))

print("\n=== SCLC dataset donor check ===")
for d in sorted(set(sclc.dataset_id) & set(norm.dataset_id)):
    l, n = sclc[sclc.dataset_id == d], norm[norm.dataset_id == d]
    print(f"{d}: SCLC donors={sorted(set(l.donor_id))} normal donors={sorted(set(n.donor_id))} shared={sorted(set(l.donor_id)&set(n.donor_id))}")

# Does any single dataset contain both LUAD and SCLC primary cells?
both = set(luad.dataset_id) & set(sclc.dataset_id)
print(f"\n=== Datasets with primary LUAD AND primary SCLC cells: {sorted(both)} ===")
for d in sorted(both):
    print(f"  {d}: LUAD donors={sorted(set(luad[luad.dataset_id==d].donor_id))}, SCLC donors={sorted(set(sclc[sclc.dataset_id==d].donor_id))}")
