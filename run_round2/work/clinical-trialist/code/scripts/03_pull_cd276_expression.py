#!/usr/bin/env python
"""Pull per-sample CD276 mRNA expression from cBioPortal for TCGA LUAD
PanCancer Atlas using the same pybioportal.molecular_data client the MCP
server imports.

Study:    luad_tcga_pan_can_atlas_2018 (confirmed via MCP get_all_cancer_types
          -> search_studies(cancer_type='luad') -> get_study_details)
Profile:  luad_tcga_pan_can_atlas_2018_rna_seq_v2_mrna
          (MRNA_EXPRESSION, datatype CONTINUOUS, "mRNA Expression, RSEM
          (Batch normalized from Illumina HiSeq_RNASeqV2)")
Gene:     CD276, Entrez 80381 (ENSG00000103855 confirmed via target MCP)

Saves the complete per-sample table, unfiltered, to data/raw/.
"""
import os
import json
import pandas as pd
import pybioportal.sample_lists as sl
import pybioportal.molecular_data as md

BASE = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/clinical-trialist")
RAW = os.path.join(BASE, "data/raw")
os.makedirs(RAW, exist_ok=True)

STUDY = "luad_tcga_pan_can_atlas_2018"
PROFILE = f"{STUDY}_rna_seq_v2_mrna"
ENTREZ = "80381"

lists = sl.get_all_sample_lists_in_study(STUDY)
print("sample lists type:", type(lists))
print(lists if not hasattr(lists, "head") else lists.head(20).to_string())
if hasattr(lists, "columns"):
    lists.to_csv(os.path.join(RAW, "cbioportal_luad_tcga_pancancer_sample_lists.csv"), index=False)
    ids = lists["sampleListId"].tolist() if "sampleListId" in lists.columns else []
else:
    ids = []

candidates = [x for x in ids if x.endswith("_all")]
sample_list_id = candidates[0] if candidates else f"{STUDY}_all"
print("using sample_list_id:", sample_list_id)

sample_ids = sl.get_all_sample_ids_in_sample_list(sample_list_id)
print("n samples in sample list:", len(sample_ids))
print("first ids:", list(sample_ids)[:5] if not hasattr(sample_ids, "tolist") else sample_ids[:5])
if hasattr(sample_ids, "to_csv"):
    sample_ids.to_csv(os.path.join(RAW, "cbioportal_luad_tcga_pancancer_sample_list_ids.csv"), index=False)

expr = md.get_all_molecular_data_in_molecular_profile(
    molecular_profile_id=PROFILE,
    sample_list_id=sample_list_id,
    entrez_gene_id=ENTREZ,
    projection="SUMMARY",
)
print("expression type:", type(expr))
print(expr.head().to_string() if hasattr(expr, "head") else str(expr)[:1000])
if hasattr(expr, "shape"):
    print("expression shape:", expr.shape)
    print("columns:", expr.columns.tolist())

out = os.path.join(RAW, "cbioportal_luad_tcga_pancancer_cd276_mrna_raw.csv")
expr.to_csv(out, index=False)
print("wrote", out)

# Also pull the two z-score profiles for reference (scale cross-check)
for extra in [f"{STUDY}_rna_seq_v2_mrna_median_Zscores",
              f"{STUDY}_rna_seq_v2_mrna_median_all_sample_Zscores"]:
    try:
        z = md.get_all_molecular_data_in_molecular_profile(
            molecular_profile_id=extra, sample_list_id=sample_list_id,
            entrez_gene_id=ENTREZ, projection="SUMMARY")
        if hasattr(z, "to_csv"):
            fn = os.path.join(RAW, f"cbioportal_luad_tcga_pancancer_cd276_{extra.split('_')[-2]}_zscores_raw.csv")
            z.to_csv(fn, index=False)
            print("wrote", fn, z.shape)
    except Exception as e:  # log, do not fail the main pull
        print(f"FAILED extra profile {extra}: {type(e).__name__}: {e}")
