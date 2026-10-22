#!/usr/bin/env python
"""Context check for the paper's n=566: how many LUAD TCGA samples have a CD276
mRNA value in the alternative cBioPortal studies? Counts only; these tables are
NOT used in the survival analysis (which is pinned to the PanCancer Atlas study)."""
import os
import pandas as pd
import pybioportal.sample_lists as sl
import pybioportal.molecular_data as md

BASE = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/clinical-trialist")
TAB = os.path.join(BASE, "results/tables")

CHECKS = [
    ("luad_tcga", "luad_tcga_rna_seq_v2_mrna", "RSEM (Firehose legacy)"),
    ("luad_tcga_gdc", "luad_tcga_gdc_mrna_seq_tpm", "TPM (GDC 2025)"),
    ("luad_tcga_gdc", "luad_tcga_gdc_mrna_seq_fpkm", "FPKM (GDC 2025)"),
    ("luad_tcga_pan_can_atlas_2018", "luad_tcga_pan_can_atlas_2018_rna_seq_v2_mrna", "RSEM (PanCancer Atlas)"),
]

rows = []
for study, profile, scale in CHECKS:
    try:
        d = md.get_all_molecular_data_in_molecular_profile(
            molecular_profile_id=profile, sample_list_id=f"{study}_all",
            entrez_gene_id="80381", projection="SUMMARY")
        n = len(d)
        npat = d["patientId"].nunique() if "patientId" in d.columns else float("nan")
        rows.append(dict(study_id=study, profile=profile, scale=scale,
                         n_samples_with_CD276=n, n_patients=int(npat), status="ok"))
        print(study, profile, "->", n, "samples /", npat, "patients")
    except Exception as e:
        rows.append(dict(study_id=study, profile=profile, scale=scale,
                         n_samples_with_CD276=None, n_patients=None,
                         status=f"FAILED: {type(e).__name__}: {e}"))
        print("FAILED", study, profile, type(e).__name__, e)

out = pd.DataFrame(rows)
out.to_csv(os.path.join(TAB, "tcga_luad_alternative_study_cd276_counts.csv"), index=False)
print(out.to_string(index=False))
