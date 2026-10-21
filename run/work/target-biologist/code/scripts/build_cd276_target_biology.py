#!/usr/bin/env python3
"""
Build CD276 (B7-H3) target-biology artifacts for the LUAD/SCLC therapeutic
candidacy evaluation.

Inputs are the verbatim results of MCP calls (target, drug, interaction,
pathway, expression) transcribed below, so the run is reproducible without
re-querying. Nothing here is imputed.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/target-biologist"
RAW = os.path.join(BASE, "data", "raw")
TAB = os.path.join(BASE, "results", "tables")
FIG = os.path.join(BASE, "results", "figures")
REP = os.path.join(BASE, "results", "reports")
for d in (RAW, TAB, FIG, REP):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Normal-tissue expression, verbatim from expression MCP
#    query_expression_by_gene(ENSG00000103855): 120 tissue / cell-type entries.
#    level = HPA expression level bin (-1 = not detected, 1..5 increasing).
#    protein_level = HPA protein level; protein_reliable = HPA reliability flag.
# ---------------------------------------------------------------------------
TISSUE = [
    ("effector memory CD8-positive, alpha-beta T cell", "NOT_AN_UBERON_3", 13, -1, 1, False, -1),
    ("CD8-positive, alpha-beta thymocyte", "CL_0000811", 19, -1, 1, False, -1),
    ("C1 segment of cervical spinal cord", "UBERON_0006469", 503, -1, 3, False, -1),
    ("heart", "UBERON_0000948", 2465, 1, 4, False, -1),
    ("effector memory CD4-positive, alpha-beta T cell", "CL_0000905", 8, -1, 1, False, -1),
    ("stomach", "UBERON_0000945", 1711.5, 0, 4, True, 2),
    ("CD4-positive, alpha-beta thymocyte", "CL_0000810", 27, -1, 1, False, -1),
    ("aorta", "UBERON_0000947", 4041.5, 1, 4, False, -1),
    ("parathyroid gland", "UBERON_0001132", 0, -1, -1, True, 2),
    ("mature neutrophil", "NOT_AN_UBERON_4", 70, -1, 2, False, -1),
    ("tonsil", "UBERON_0002372", 560, 0, 3, True, 2),
    ("tibial artery", "UBERON_0007610", 4664.5, 1, 4, False, -1),
    ("esophagogastric junction", "UBERON_0007650", 2017.5, 1, 4, False, -1),
    ("bone marrow", "UBERON_0002371", 31, -1, 1, True, 1),
    ("vermiform appendix", "UBERON_0001154", 1199, 0, 3, True, 2),
    ("erythroblast", "CL_0000765", 77, -1, 2, False, -1),
    ("seminal vesicle", "UBERON_0000998", 0, -1, -1, True, 2),
    ("cerebellar hemisphere", "UBERON_0002245", 550, 0, 3, False, -1),
    ("hematopoietic multipotent progenitor cell", "CL_0000837", 72, -1, 2, False, -1),
    ("frontal lobe", "UBERON_0016525", 988.5, 0, 3, False, -1),
    ("heart muscle", "UBERON_0002349", 0, -1, -1, True, 0),
    ("CD38-negative naive B cell", "CL_0002102", 18.5, -1, 1, False, -1),
    ("nucleus accumbens", "UBERON_0001882", 590, 0, 3, False, -1),
    ("megakaryocyte-erythroid progenitor cell", "CL_0000050", 23.5, -1, 1, False, -1),
    ("central memory CD8-positive, alpha-beta T cell", "CL_0000907", 6, -1, 1, False, -1),
    ("rectum", "UBERON_0001052", 1364.5, 0, 4, True, 2),
    ("lymph node", "UBERON_0000029", 596.5, 0, 3, True, 2),
    ("hippocampus proper", "UBERON_0001954", 409, -1, 3, False, -1),
    ("substantia nigra", "UBERON_0002038", 618, 0, 3, False, -1),
    ("tibial nerve", "UBERON_0001323", 1596, 0, 4, False, -1),
    ("spleen", "UBERON_0002106", 1043, 0, 3, True, 1),
    ("central memory CD4-positive, alpha-beta T cell", "NOT_AN_UBERON_2", 16, -1, 1, False, -1),
    ("suprapubic skin", "UBERON_0036149", 2105.5, 1, 4, False, -1),
    ("common myeloid progenitor", "CL_0000049", 22, -1, 1, False, -1),
    ("leukocyte", "CL_0000738", 15, -1, 1, False, -1),
    ("alternatively activated macrophage", "CL_0000890", 14497, 3, 5, False, -1),
    ("CD8-positive, alpha-beta T cell", "CL_0000625", 15.5, -1, 1, False, -1),
    ("inflammatory macrophage", "CL_0000863", 11950, 2, 5, False, -1),
    ("putamen", "UBERON_0001874", 497, -1, 3, False, -1),
    ("transverse colon", "UBERON_0001157", 1546, 0, 4, False, -1),
    ("ectocervix", "UBERON_0012249", 3891, 1, 4, False, -1),
    ("cytotoxic CD56-dim natural killer cell", "CL_0000939", 10, -1, 1, False, -1),
    ("abdomen", "abdomen", 0, -1, -1, True, 2),
    ("Brodmann (1909) area 24", "UBERON_0006101", 677, 0, 3, False, -1),
    ("minor salivary gland", "UBERON_0001830", 2095, 1, 4, False, -1),
    ("heart left ventricle", "UBERON_0002084", 2858.5, 1, 4, False, -1),
    ("esophagus muscularis mucosa", "UBERON_0004648", 1959.5, 0, 4, False, -1),
    ("regulatory T cell", "CL_0000815", 3, -1, -1, False, -1),
    ("testis", "UBERON_0000473", 560, 0, 3, True, 2),
    ("bronchus", "UBERON_0002185", 0, -1, -1, True, 2),
    ("endothelial cell of umbilical vein (proliferating)", "CL_0002618", 1646.5, 0, 4, False, -1),
    ("lung", "UBERON_0002048", 1682.5, 0, 4, True, 2),
    ("common lymphoid progenitor", "CL_0000051", 48, -1, 2, False, -1),
    ("colon", "UBERON_0001155", 1450, 0, 4, True, 2),
    ("thyroid gland", "UBERON_0002046", 1315.5, 0, 4, True, 1),
    ("cerebral cortex", "UBERON_0000956", 873.5, 0, 3, True, 1),
    ("caudate nucleus", "UBERON_0001873", 534, -1, 3, False, -1),
    ("class switched memory B cell", "CL_0000972", 20, -1, 1, False, -1),
    ("liver", "UBERON_0002107", 2925, 1, 4, True, 2),
    ("small intestine", "UBERON_0002108", 947, 0, 3, True, 2),
    ("lower leg skin", "UBERON_0004264", 2817, 1, 4, False, -1),
    ("blood", "UBERON_0000178", 114.5, -1, 2, False, -1),
    ("CD3-positive, CD4-positive, CD8-positive, double positive thymocyte", "NOT_AN_UBERON_1", 16, -1, 1, False, -1),
    ("kidney", "UBERON_0002113", 794.5, 0, 3, True, 1),
    ("prefrontal cortex", "UBERON_0000451", 714, 0, 3, False, -1),
    ("vagina", "UBERON_0000996", 1986, 0, 4, True, 2),
    ("atrium auricular region", "UBERON_0006618", 2618.5, 1, 4, False, -1),
    ("fallopian tube", "UBERON_0003889", 1372, 0, 4, True, 1),
    ("CD34-negative, CD41-positive, CD42-positive megakaryocyte cell", "CL_0002026", 352, -1, 3, False, -1),
    ("sigmoid colon", "UBERON_0001159", 2178.5, 1, 4, False, -1),
    ("gall bladder", "UBERON_0002110", 2585, 1, 4, True, 2),
    ("CD4-positive, alpha-beta T cell", "CL_0000624", 13, -1, 1, False, -1),
    ("subcutaneous adipose tissue", "UBERON_0002190", 4354, 1, 4, False, -1),
    ("nasopharynx", "UBERON_0001728", 0, -1, -1, True, 2),
    ("temporal lobe", "UBERON_0001871", 2251, 1, 4, False, -1),
    ("transformed skin fibroblast", "CL_0000057", 10172.5, 2, 5, False, -1),
    ("endocervix", "UBERON_0000458", 3236, 1, 4, False, -1),
    ("endothelial cell of umbilical vein (resting)", "CL_0002618", 1095.5, 0, 3, False, -1),
    ("duodenum", "UBERON_0002114", 1155, 0, 3, True, 2),
    ("placenta", "UBERON_0001987", 5914, 1, 4, True, 2),
    ("esophagus mucosa", "UBERON_0002469", 931, 0, 3, False, -1),
    ("amygdala", "UBERON_0001876", 590, 0, 3, False, -1),
    ("pituitary gland", "UBERON_0000007", 939, 0, 3, False, -1),
    ("adrenal gland", "UBERON_0002369", 4092, 1, 4, True, 2),
    ("hypothalamus", "UBERON_0001898", 597, 0, 3, False, -1),
    ("macrophage", "CL_0000235", 9455.5, 2, 5, False, -1),
    ("epididymis", "UBERON_0001301", 0, -1, -1, True, 2),
    ("urinary bladder", "UBERON_0001255", 1971, 0, 4, True, 2),
    ("hematopoietic stem cell", "CL_0000037", 207, -1, 2, False, -1),
    ("cortex of kidney", "UBERON_0001225", 1134.5, 0, 3, False, -1),
    ("esophagus", "UBERON_0001043", 793.5, 0, 3, True, 2),
    ("zone of skin", "UBERON_0000014", 2306.5, 1, 4, True, 2),
    ("cerebellum", "UBERON_0002037", 598, 0, 3, True, 1),
    ("greater omentum", "UBERON_0005448", 2034, 1, 4, False, -1),
    ("conventional dendritic cell", "CL_0000990", 1559, 0, 4, False, -1),
    ("pancreas", "UBERON_0001264", 1772, 0, 4, True, 2),
    ("segmented neutrophil of bone marrow", "CL_0011114", 34, -1, 1, False, -1),
    ("smooth muscle tissue", "UBERON_0001135", 4181, 1, 4, True, 0),
    ("prostate gland", "UBERON_0002367", 2228, 1, 4, True, 3),
    ("breast", "UBERON_0000310", 2428, 1, 4, True, 2),
    ("coronary artery", "UBERON_0001621", 2919, 1, 4, False, -1),
    ("skeletal muscle tissue", "UBERON_0001134", 1512.5, 0, 4, True, 0),
    ("CD14-positive, CD16-negative classical monocyte", "CL_0002057", 35.5, -1, 1, False, -1),
    ("granulocyte monocyte progenitor cell", "CL_0000557", 42, -1, 2, False, -1),
    ("neutrophilic metamyelocyte", "CL_0000582", 21, -1, 1, False, -1),
    ("brain", "UBERON_0000955", 1538.5, 0, 4, False, -1),
    ("ovary", "UBERON_0000992", 2465, 1, 4, True, 2),
    ("EBV-transformed lymphocyte", "CL_0000542", 375, -1, 3, False, -1),
    ("mature eosinophil", "CL_0000041", 56, -1, 2, False, -1),
    ("Brodmann (1909) area 9", "UBERON_0013540", 693, 0, 3, False, -1),
    ("hippocampus", "UBERON_0002421", 0, -1, -1, True, 1),
    ("caudate-putamen", "UBERON_0005383", 0, -1, -1, True, 1),
    ("oral mucosa", "UBERON_0003729", 0, -1, -1, True, 2),
    ("plasma cell", "NOT_AN_UBERON_5", 84.5, -1, 2, False, -1),
    ("saliva-secreting gland", "UBERON_0001044", 1741.5, 0, 4, True, 1),
    ("memory B cell", "CL_0000787", 13, -1, 1, False, -1),
    ("small intestine Peyer's patch", "UBERON_0003454", 905, 0, 3, False, -1),
    ("endometrium", "UBERON_0001295", 3218, 1, 4, True, 2),
    ("uterus", "UBERON_0000995", 2451.5, 1, 4, False, -1),
    ("adipose tissue", "UBERON_0001013", 2169, 1, 4, True, 2),
]

tissue_df = pd.DataFrame(
    TISSUE,
    columns=[
        "tissue_label", "efo_code", "rna_tpm", "rna_zscore",
        "rna_level_bin", "protein_reliable", "protein_level",
    ],
)
tissue_df.insert(0, "gene", "CD276")
tissue_df.insert(1, "ensembl_id", "ENSG00000103855")
tissue_df.to_csv(os.path.join(RAW, "cd276_tissue_expression_raw.csv"), index=False)

# ---------------------------------------------------------------------------
# 2. Target identity / biology table
# ---------------------------------------------------------------------------
biology = [
    ("identity", "Ensembl gene ID", "ENSG00000103855", "Open Targets target info"),
    ("identity", "Approved symbol", "CD276", "Open Targets / HGNC"),
    ("identity", "Approved name", "CD276 molecule", "Open Targets / HGNC"),
    ("identity", "Common synonyms", "B7-H3; B7H3; 4Ig-B7-H3; B7RP-2; CD276 antigen; costimulatory molecule", "Open Targets / HGNC / UniProt"),
    ("identity", "Gene biotype", "protein_coding", "Open Targets"),
    ("identity", "Chromosome", "15", "Open Targets"),
    ("identity", "Genomic location (GRCh38)", "15:73683966-73714514 (+ strand)", "Open Targets"),
    ("identity", "Canonical transcript", "ENST00000318443 (15:73684383-73714514)", "Open Targets"),
    ("identity", "UniProt (Swiss-Prot)", "Q5ZPR3", "Open Targets / UniProt"),
    ("identity", "ChEMBL target ID", "CHEMBL3712879", "Open Targets"),
    ("identity", "DrugBank ID", "DB15635", "Open Targets"),
    ("protein_class", "ChEMBL target class (L1)", "Surface antigen", "ChEMBL via target MCP"),
    ("protein_class", "UniProt protein family (prior knowledge)", "Immunoglobulin superfamily, B7/CD28 co-signalling family; type I transmembrane glycoprotein", "PRIOR KNOWLEDGE - not returned by MCP"),
    ("localization", "Subcellular localization (UniProt)", "Membrane", "UniProt via target MCP"),
    ("localization", "Subcellular localization (HPA)", "Vesicles", "HPA via target MCP"),
    ("localization", "Signal peptide / TM prediction", "UniProt SigP or TMHMM = TRUE (antibody tractability criterion)", "Open Targets tractability"),
    ("localization", "SignalP annotation", "SignalP-noTM (secretory signal peptide; no TM predicted by SignalP alone)", "Open Targets dbXrefs"),
    ("function", "UniProt function description", "May regulate T-cell-mediated immune response; may protect tumour cells by inhibiting NK-mediated lysis; proposed marker for neuroblastoma detection; may modulate lymphocytic activity at mucosal surfaces", "UniProt via Open Targets"),
    ("function", "Reactome pathways", "None returned (0 pathways)", "Reactome via pathway MCP"),
    ("chemistry", "Chemical probes", "None (0 total, 0 high-quality)", "Open Targets chemical probes"),
    ("constraint", "gnomAD LoF observed/expected", "34 observed vs 51.0 expected; o/e 0.667; LOEUF bin 4 (rank 7792)", "gnomAD via Open Targets"),
    ("constraint", "gnomAD missense observed/expected", "634 observed vs 732.0 expected; o/e 0.866", "gnomAD via Open Targets"),
    ("homologue", "Chimpanzee ortholog", "CD276; 98.88% identity; one-to-one; high confidence", "Ensembl via Open Targets"),
    ("homologue", "Macaque ortholog", "CD276; 94.57% query identity; one-to-one; high confidence", "Ensembl via Open Targets"),
    ("homologue", "Mouse ortholog", "Cd276; 52.43% query identity (88.61% target identity); one-to-one; high confidence", "Ensembl via Open Targets"),
    ("homologue", "Rat ortholog", "Cd276; 52.81% query identity; one-to-one; high confidence", "Ensembl via Open Targets"),
    ("homologue", "Guinea pig ortholog", "CD276; 89.70% query identity; one-to-one", "Ensembl via Open Targets"),
    ("homologue", "Dog ortholog", "CD276; 93.63% query identity; one-to-one", "Ensembl via Open Targets"),
    ("homologue", "Pig ortholog", "CD276; 90.07% query identity; one-to-one", "Ensembl via Open Targets"),
    ("paralogue", "HHLA2 (closest human paralogue)", "12.92% query / 16.67% target identity", "Ensembl via Open Targets"),
    ("paralogue", "VTCN1 (B7-H4)", "11.99% query / 22.70% target identity", "Ensembl via Open Targets"),
    ("paralogue", "BTN/BTNL family paralogues", "8.99-16.48% query identity across BTN1A1, BTN2A1/2, BTN3A1/2/3, BTNL2/3/8/9, MOG, ERMAP, ICOSLG", "Ensembl via Open Targets"),
    ("interactions", "IntAct protein interactions", "40 interactions; reported scores 0.27-0.53 (low confidence); includes LGALS1, LGALS3, LGALS8, LGALS9, CD9, CD81, TNF, KRAS/HRAS/NRAS", "IntAct via interaction MCP"),
]
bio_df = pd.DataFrame(biology, columns=["category", "attribute", "value", "source"])
bio_df.to_csv(os.path.join(TAB, "cd276_target_biology.csv"), index=False)

# ---------------------------------------------------------------------------
# 3. Tractability by modality (verbatim Open Targets flags)
# ---------------------------------------------------------------------------
tract = [
    ("Small molecule", "Approved drug", False),
    ("Small molecule", "Advanced clinical", False),
    ("Small molecule", "Phase 1 clinical", False),
    ("Small molecule", "Structure with ligand", False),
    ("Small molecule", "High-quality ligand", False),
    ("Small molecule", "High-quality pocket", False),
    ("Small molecule", "Medium-quality pocket", False),
    ("Small molecule", "Druggable family", False),
    ("Antibody", "Approved drug", False),
    ("Antibody", "Advanced clinical", True),
    ("Antibody", "Phase 1 clinical", False),
    ("Antibody", "UniProt localization high confidence", False),
    ("Antibody", "GO cellular component high confidence", False),
    ("Antibody", "UniProt localization medium confidence", False),
    ("Antibody", "UniProt signal peptide or TMHMM", True),
    ("Antibody", "GO cellular component medium confidence", False),
    ("Antibody", "Human Protein Atlas localization", False),
    ("PROTAC/degrader", "Approved drug", False),
    ("PROTAC/degrader", "Advanced clinical", False),
    ("PROTAC/degrader", "Phase 1 clinical", False),
    ("PROTAC/degrader", "Literature", False),
    ("PROTAC/degrader", "UniProt ubiquitination", False),
    ("PROTAC/degrader", "Database ubiquitination", True),
    ("PROTAC/degrader", "Half-life data", True),
    ("PROTAC/degrader", "Small-molecule binder", False),
    ("Other/unknown", "Approved drug", False),
    ("Other/unknown", "Advanced clinical", False),
    ("Other/unknown", "Phase 1 clinical", False),
]
tract_df = pd.DataFrame(tract, columns=["modality", "criterion", "value"])
tract_df.to_csv(os.path.join(TAB, "cd276_tractability_by_modality.csv"), index=False)

# ---------------------------------------------------------------------------
# 4. Known clinical-stage drugs annotated to CD276
# ---------------------------------------------------------------------------
drugs = [
    ("ENOBLITUZUMAB", "CHEMBL3545373", "Antibody", "CD276 antigen cross-linking agent",
     "head and neck squamous cell carcinoma", "EFO_0000181", 2, "Withdrawn", "NCT04129320"),
    ("ENOBLITUZUMAB", "CHEMBL3545373", "Antibody", "CD276 antigen cross-linking agent",
     "prostate cancer", "MONDO_0008315", 2, "Recruiting", "NCT06014255"),
    ("ENOBLITUZUMAB", "CHEMBL3545373", "Antibody", "CD276 antigen cross-linking agent",
     "prostate cancer", "MONDO_0008315", 2, "Active, not recruiting", "NCT02923180"),
    ("ENOBLITUZUMAB", "CHEMBL3545373", "Antibody", "CD276 antigen cross-linking agent",
     "head and neck malignant neoplasia", "EFO_0006859", 2, "Withdrawn", "NCT04129320"),
    ("ENOBLITUZUMAB", "CHEMBL3545373", "Antibody", "CD276 antigen cross-linking agent",
     "melanoma", "EFO_0000756", 1, "Terminated", "NCT01918930"),
    ("8H9 131I", "CHEMBL2109310", "Antibody (radiolabelled)", "CD276 antigen binding agent",
     "leptomeningeal metastasis", "EFO_1001012", 2, "Terminated", "NCT03275402"),
    ("8H9 131I", "CHEMBL2109310", "Antibody (radiolabelled)", "CD276 antigen binding agent",
     "neuroblastoma", "EFO_0000621", 2, "Terminated", "NCT03275402"),
    ("8H9 131I", "CHEMBL2109310", "Antibody (radiolabelled)", "CD276 antigen binding agent",
     "diffuse intrinsic pontine glioma", "EFO_1000026", 1, "Withdrawn", "NCT05063357"),
    ("8H9 131I", "CHEMBL2109310", "Antibody (radiolabelled)", "CD276 antigen binding agent",
     "peritoneum cancer", "MONDO_0002087", 1, "Terminated", "NCT01099644"),
]
drug_df = pd.DataFrame(drugs, columns=[
    "pref_name", "chembl_id", "drug_type", "mechanism_of_action",
    "indication", "disease_id", "max_phase", "status", "trial_id",
])
drug_df.to_csv(os.path.join(TAB, "cd276_known_clinical_drugs.csv"), index=False)

# Explicit negative result: no CD276 drug annotated to LUAD or SCLC
lung_neg = pd.DataFrame([
    ("lung adenocarcinoma", "EFO_0000571", 0, "query with target_id=ENSG00000103855, min_phase=0"),
    ("small cell lung carcinoma", "EFO_0000702", 0, "query with target_id=ENSG00000103855, min_phase=0"),
], columns=["indication", "disease_id", "n_cd276_drugs_returned", "query_scope"])
lung_neg.to_csv(os.path.join(TAB, "cd276_lung_indication_drug_query_result.csv"), index=False)

# ---------------------------------------------------------------------------
# 5. Expression summary
# ---------------------------------------------------------------------------
stats = {
    "n_tissue_entries": len(tissue_df),
    "n_detected_level_ge_1": int((tissue_df["rna_level_bin"] >= 1).sum()),
    "n_not_detected_level_minus1": int((tissue_df["rna_level_bin"] == -1).sum()),
    "n_level_ge_3": int((tissue_df["rna_level_bin"] >= 3).sum()),
    "n_level_4_or_5": int((tissue_df["rna_level_bin"] >= 4).sum()),
    "median_tpm_all_entries": float(tissue_df["rna_tpm"].median()),
    "mean_tpm_all_entries": float(round(tissue_df["rna_tpm"].mean(), 2)),
    "max_tpm": float(tissue_df["rna_tpm"].max()),
    "max_tpm_tissue": tissue_df.loc[tissue_df["rna_tpm"].idxmax(), "tissue_label"],
    "min_tpm": float(tissue_df["rna_tpm"].min()),
}
summary_rows = [("statistic", k, v) for k, v in stats.items()]

selected = [
    "lung", "bronchus", "heart", "heart left ventricle", "liver", "kidney",
    "brain", "cerebellum", "pancreas", "adrenal gland", "stomach", "colon",
    "skin", "zone of skin", "skeletal muscle tissue", "smooth muscle tissue",
    "blood", "bone marrow", "lymph node", "spleen", "thymocyte", "CD4-positive, alpha-beta T cell",
    "CD8-positive, alpha-beta T cell", "regulatory T cell", "macrophage",
    "inflammatory macrophage", "alternatively activated macrophage", "conventional dendritic cell",
    "mature neutrophil", "placenta", "testis", "uterus", "prostate gland",
]
for label in selected:
    sub = tissue_df[tissue_df["tissue_label"] == label]
    if len(sub):
        r = sub.iloc[0]
        summary_rows.append((
            "selected_tissue",
            label,
            f"rna_tpm={r.rna_tpm}; level_bin={r.rna_level_bin}; protein_reliable={r.protein_reliable}; protein_level={r.protein_level}",
        ))
summary_df = pd.DataFrame(summary_rows, columns=["row_type", "item", "value"])
summary_df.to_csv(os.path.join(TAB, "cd276_tissue_expression_summary.csv"), index=False)

# ---------------------------------------------------------------------------
# 6. Figure: breadth of normal expression
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(15, 6.5), gridspec_kw={"width_ratios": [1, 1.25]})

ax = axes[0]
vals = tissue_df["rna_tpm"].clip(lower=0.1)
ax.hist(vals, bins=30, color="#4C72B0", edgecolor="white")
ax.set_xscale("log")
ax.set_xlabel("CD276 RNA (TPM, log scale; 0 clipped to 0.1)")
ax.set_ylabel("Number of tissues / cell types")
ax.set_title("A  Breadth across 120 normal tissue and\nimmune cell-type samples (expression MCP)")
ax.axvline(1682.5, color="#C44E52", linestyle="--", linewidth=1.5)
ax.text(1900, ax.get_ylim()[1] * 0.85, "lung\n1683 TPM", color="#C44E52", fontsize=8)

ax = axes[1]
plot_labels = [
    "alternatively activated macrophage", "inflammatory macrophage", "macrophage",
    "placenta", "adrenal gland", "tibial artery", "aorta", "subcutaneous adipose tissue",
    "smooth muscle tissue", "coronary artery", "liver", "heart left ventricle",
    "lower leg skin", "prostate gland", "uterus", "breast", "pancreas", "lung",
    "stomach", "skeletal muscle tissue", "colon", "thyroid gland", "kidney",
    "cerebral cortex", "lymph node", "cerebellum", "testis", "spleen", "blood",
    "bone marrow", "CD4-positive, alpha-beta T cell", "CD8-positive, alpha-beta T cell",
    "regulatory T cell", "mature neutrophil", "bronchus",
]
sub = tissue_df[tissue_df["tissue_label"].isin(plot_labels)].copy()
sub = sub.drop_duplicates("tissue_label").sort_values("rna_tpm", ascending=True)
colors = ["#C44E52" if x == "lung" else ("#DD8452" if x == "bronchus" else "#4C72B0") for x in sub["tissue_label"]]
ax.barh(sub["tissue_label"], sub["rna_tpm"], color=colors)
ax.set_xlabel("CD276 RNA (TPM)")
ax.set_title("B  Selected normal tissues; lung (red), bronchus (orange)")
ax.tick_params(axis="y", labelsize=7)
ax.set_xlim(0, max(sub["rna_tpm"].max() * 1.08, 1))

plt.tight_layout()
fig.savefig(os.path.join(FIG, "cd276_normal_tissue_expression.png"), dpi=200)
fig.savefig(os.path.join(FIG, "cd276_normal_tissue_expression.pdf"))
plt.close(fig)

print("Wrote:")
for p in [
    os.path.join(RAW, "cd276_tissue_expression_raw.csv"),
    os.path.join(TAB, "cd276_target_biology.csv"),
    os.path.join(TAB, "cd276_tractability_by_modality.csv"),
    os.path.join(TAB, "cd276_known_clinical_drugs.csv"),
    os.path.join(TAB, "cd276_lung_indication_drug_query_result.csv"),
    os.path.join(TAB, "cd276_tissue_expression_summary.csv"),
    os.path.join(FIG, "cd276_normal_tissue_expression.png"),
]:
    print(" ", p)
print("\nExpression stats:", stats)
