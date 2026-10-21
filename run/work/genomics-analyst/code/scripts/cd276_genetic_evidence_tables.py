#!/usr/bin/env python
"""Build CD276 (B7-H3) genetic-evidence tables for LUAD and SCLC.

Inputs
------
data/raw/cd276_locus_credible_sets_all_studies.parquet
    All credible sets in chr15:73.5-73.9 Mb (GRCh38), any study type.
data/raw/{luad,sclc}_*_credible_sets.parquet
    Full credible sets for the major LUAD/SCLC GWAS queried.
<tool-results>/mcp-genetics-query_l2g_predictions-*.txt
    Raw L2G output for ENSG00000103855 (copied to data/raw here).

Outputs (results/tables/)
-------------------------
cd276_disease_ids.csv
cd276_luad_sclc_study_cd276_locus_check.csv
cd276_l2g_predictions.csv
cd276_qtl_colocalization_summary.csv
cd276_region_credible_sets.csv
cd276_tractability.csv
cd276_prioritisation_scores.csv
"""
import json
import shutil
from pathlib import Path

import pandas as pd

BASE = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
            "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/genomics-analyst")
RAW = BASE / "data/raw"
TAB = BASE / "results/tables"
TAB.mkdir(parents=True, exist_ok=True)

# CD276 GRCh38 coordinates from Open Targets target info
CD276_TSS = 73684383
CD276_START, CD276_END = 73683966, 73714514
WINDOW = 500_000  # +/- 500 kb around TSS for "locus at CD276"
LO, HI = CD276_TSS - WINDOW, CD276_TSS + WINDOW

# ----------------------------------------------------------------------------
# 1. Disease IDs (verified via mcp__disease__search_diseases_by_name /
#    get_disease_info). SCLC query "small cell lung cancer" returned 0;
#    "small cell lung carcinoma" resolved EFO_0000702.
# ----------------------------------------------------------------------------
pd.DataFrame([
    {"disease": "lung adenocarcinoma", "disease_id": "EFO_0000571",
     "source_name_returned": "lung adenocarcinoma", "search_term": "lung adenocarcinoma",
     "excluded_terms": "MONDO_0000503 (adenocarcinoma in situ), MONDO_0003892 (acinar), "
                       "EFO_1000046 (papillary), EFO_0005288 (duplicate NSCLC-adeno term)",
     "used": True},
    {"disease": "small cell lung carcinoma", "disease_id": "EFO_0000702",
     "source_name_returned": "small cell lung carcinoma", "search_term": "small cell lung carcinoma",
     "excluded_terms": "MONDO_0003438 (combined SCLC); EFO_0003060 (NSCLC, out of scope)",
     "used": True},
    {"disease": "CD276 target", "disease_id": "ENSG00000103855",
     "source_name_returned": "CD276 molecule", "search_term": "CD276",
     "excluded_terms": "", "used": True},
]).to_csv(TAB / "cd276_disease_ids.csv", index=False)

# ----------------------------------------------------------------------------
# 2. Region credible sets + LUAD/SCLC study-level check
# ----------------------------------------------------------------------------
region = pd.read_parquet(RAW / "cd276_locus_credible_sets_all_studies.parquet")
region_out = region.copy()
region_out["distance_to_CD276_TSS_bp"] = (region_out["position"] - CD276_TSS).abs()
region_out["in_CD276_gene_body"] = (
    (region_out["chromosome"].astype(str) == "15")
    & region_out["position"].between(CD276_START, CD276_END)
)
region_out.sort_values(["studyType", "distance_to_CD276_TSS_bp"]).to_csv(
    TAB / "cd276_region_credible_sets.csv", index=False)

luad_ids = {
    "GCST90297563": "Lung adenocarcinoma (Shi 2023)",
    "GCST90455522": "Lung adenocarcinoma (Gorman 2024)",
    "GCST90134662": "Lung adenocarcinoma (Byun 2022)",
    "GCST008836": "Lung adenocarcinoma (Dai 2019)",
    "GCST004744": "Lung adenocarcinoma (McKay 2017)",
}
sclc_ids = {
    "GCST004746": "Small cell lung carcinoma (McKay 2017)",
    "GCST90134664": "Small cell lung carcinoma (Byun 2022)",
    "FINNGEN_R12_C3_SCLC_EXALLC": "Small cell lung cancer (FinnGen R12)",
}

rows = []
for group, ids in (("LUAD", luad_ids), ("SCLC", sclc_ids)):
    for sid, label in ids.items():
        files = sorted(RAW.glob(f"*{sid}*_credible_sets.parquet"))
        if not files:
            rows.append({"histology": group, "study_id": sid, "study_label": label,
                         "credible_sets_retrieved": 0, "chr15_credible_sets": 0,
                         "min_distance_chr15_to_CD276_TSS_bp": None,
                         "locus_within_500kb_of_CD276": False,
                         "CD276_gene_body_hit": False, "note": "no file"})
            continue
        df = pd.read_parquet(files[0])
        c15 = df[df["chromosome"].astype(str) == "15"].copy()
        if len(c15):
            c15["dist"] = (c15["position"] - CD276_TSS).abs()
            mind = int(c15["dist"].min())
            near = bool((c15["dist"] <= WINDOW).any())
        else:
            mind, near = None, False
        body = bool(
            ((df["chromosome"].astype(str) == "15")
             & df["position"].between(CD276_START, CD276_END)).any()
        ) if len(df) else False
        rows.append({
            "histology": group, "study_id": sid, "study_label": label,
            "credible_sets_retrieved": int(len(df)),
            "chr15_credible_sets": int(len(c15)),
            "min_distance_chr15_to_CD276_TSS_bp": mind,
            "locus_within_500kb_of_CD276": near,
            "CD276_gene_body_hit": body,
            "note": "" if not near else "CD276-locus credible set present",
        })
study_check = pd.DataFrame(rows)
study_check.to_csv(TAB / "cd276_luad_sclc_study_cd276_locus_check.csv", index=False)

# Cross-check: do any LUAD/SCLC study IDs appear among region credible sets?
region_gwas_studies = set(region.loc[region.studyType == "gwas", "studyId"])
lung_requested = set(luad_ids) | set(sclc_ids)
intersection = sorted(region_gwas_studies & lung_requested)
pd.DataFrame({
    "metric": ["region_gwas_studies", "luad_sclc_studies_requested",
               "intersection_count", "intersection_ids"],
    "value": [len(region_gwas_studies), len(lung_requested),
              len(intersection), ",".join(intersection) if intersection else "none"],
}).to_csv(TAB / "cd276_luad_sclc_region_overlap_check.csv", index=False)

# ----------------------------------------------------------------------------
# 3. L2G predictions with QTL features
# ----------------------------------------------------------------------------
TOOL_JSON = Path("/home/xqinag/.claude/projects/-mnt-beegfs-xqinag-projects-"
                 "TheVirtualBiotech-runs-20261020-085513-evaluate-the-therapeutic-"
                 "candida-a03f0a23/ac473c6c-4815-4a45-a884-1c979c552fa2/tool-results/"
                 "mcp-genetics-query_l2g_predictions-1792504709283.txt")
raw = json.loads(TOOL_JSON.read_text())
shutil.copy(TOOL_JSON, RAW / "cd276_l2g_predictions_raw.json")

l2g = pd.json_normalize(raw["results"], sep=".")
# `features` remains a list of {name, value, shapValue}; expand to wide.
feature_rows = []
for rec in raw["results"]:
    row = {"studyLocusId": rec["studyLocusId"]}
    for feat in rec.get("features", []):
        row[feat["name"]] = feat["value"]
    feature_rows.append(row)
feat_wide = pd.DataFrame(feature_rows)
l2g = l2g.drop(columns=["features"]).merge(feat_wide, on="studyLocusId", how="left")

# Merge variant/study info from region table
meta = region[["studyLocusId", "studyId", "studyType", "variantId", "position",
               "pValueMantissa", "pValueExponent", "beta"]].drop_duplicates("studyLocusId")
l2g = l2g.merge(meta, on="studyLocusId", how="left")
l2g["distance_to_CD276_TSS_bp"] = (l2g["position"] - CD276_TSS).abs()

traits = {
    "GCST90019492": "Alanine aminotransferase levels",
    "GCST90019498": "AST/ALT ratio",
    "GCST90018943": "Alanine aminotransferase levels",
    "GCST006019": "Gamma glutamyl transferase levels",
    "GCST90013992": "Alanine aminotransferase levels",
    "GCST90244011": "Gamma glutamyl transferase levels",
    "GCST011349": "Gamma glutamyl transferase levels",
    "GCST90479509": "Aspartate aminotransferase levels",
    "GCST90239821": "Sex hormone-binding globulin levels",
    "GCST001277": "Gamma glutamyl transferase levels",
    "GCST90011898": "Alanine aminotransferase levels",
    "GCST90310162": "Gamma glutamyl transferase levels",
    "GCST90018954": "Gamma glutamyl transpeptidase",
    "GCST90019497": "Aspartate aminotransferase levels",
    "GCST90475159": "Body mass index",
}
l2g["trait_resolved"] = l2g["studyId"].map(traits)
l2g["is_luad_or_sclc"] = l2g["studyId"].isin(lung_requested)
l2g.sort_values("score", ascending=False).to_csv(
    TAB / "cd276_l2g_predictions.csv", index=False)

# ----------------------------------------------------------------------------
# 4. QTL colocalization summary (from L2G QTL features, disease-agnostic)
# ----------------------------------------------------------------------------
qtl_rows = []
for qtl, clpp_col, h4_col in [
    ("eQTL", "eQtlColocClppMaximum", "eQtlColocH4Maximum"),
    ("pQTL", "pQtlColocClppMaximum", "pQtlColocH4Maximum"),
    ("sQTL", "sQtlColocClppMaximum", "sQtlColocH4Maximum"),
]:
    if clpp_col not in l2g.columns:
        continue
    sub = l2g.dropna(subset=[clpp_col])
    top = sub.sort_values(clpp_col, ascending=False).iloc[0] if len(sub) else None
    qtl_rows.append({
        "qtl_type": qtl,
        "n_loci_with_feature": int(len(sub)),
        "n_loci_clpp_gt_0.01": int((sub[clpp_col] > 0.01).sum()),
        "max_clpp": float(sub[clpp_col].max()) if len(sub) else None,
        "n_loci_h4_gt_0.6": int((sub[h4_col] > 0.6).sum()) if h4_col in sub else None,
        "max_h4": float(sub[h4_col].max()) if h4_col in sub and len(sub) else None,
        "top_locus_study_id": top["studyId"] if top is not None else None,
        "top_locus_trait": top["trait_resolved"] if top is not None else None,
        "top_locus_is_luad_or_sclc": bool(top["is_luad_or_sclc"]) if top is not None else None,
    })
qtl_summary = pd.DataFrame(qtl_rows)
qtl_summary.to_csv(TAB / "cd276_qtl_colocalization_summary.csv", index=False)

# ----------------------------------------------------------------------------
# 5. Tractability and prioritisation
# ----------------------------------------------------------------------------
tract = [
    ("antibody", "Approved Drug", False), ("antibody", "Advanced Clinical", True),
    ("antibody", "Phase 1 Clinical", False),
    ("antibody", "UniProt SigP or TMHMM", True),
    ("small_molecule", "Approved Drug", False),
    ("small_molecule", "Advanced Clinical", False),
    ("small_molecule", "Phase 1 Clinical", False),
    ("small_molecule", "Structure with Ligand", False),
    ("small_molecule", "High-Quality Ligand", False),
    ("small_molecule", "High-Quality Pocket", False),
    ("small_molecule", "Med-Quality Pocket", False),
    ("small_molecule", "Druggable Family", False),
    ("protac", "Approved Drug", False), ("protac", "Advanced Clinical", False),
    ("protac", "Phase 1 Clinical", False), ("protac", "Literature", False),
    ("protac", "UniProt Ubiquitination", False),
    ("protac", "Database Ubiquitination", True),
    ("protac", "Half-life Data", True),
    ("protac", "Small Molecule Binder", False),
]
pd.DataFrame(tract, columns=["modality", "tractability_bucket", "value"]).to_csv(
    TAB / "cd276_tractability.csv", index=False)

pd.DataFrame([{
    "targetId": "ENSG00000103855", "isInMembrane": 0, "isSecreted": 0,
    "hasSafetyEvent": None, "hasPocket": 0, "hasLigand": 0,
    "hasSmallMoleculeBinder": 0, "geneticConstraint": -0.14043022614451184,
    "paralogMaxIdentityPercentage": 0, "mouseOrthologMaxIdentityPercentage": 0,
    "isCancerDriverGene": None, "hasTEP": None,
    "mouseKOScore": -0.19362923273754773, "hasHighQualityChemicalProbes": None,
    "maxClinicalTrialPhase": 0.5, "tissueSpecificity": -1, "tissueDistribution": 0,
    "note": "Single global record; the tool returns no disease-stratified "
            "prioritisation for EFO_0000571 or EFO_0000702.",
}]).to_csv(TAB / "cd276_prioritisation_scores.csv", index=False)

print("Wrote tables:")
for p in sorted(TAB.glob("cd276_*.csv")):
    print(" ", p.name, p.stat().st_size, "bytes")
print("\nStudy CD276-locus check:")
print(study_check.to_string(index=False))
print("\nRegion overlap check:")
print(pd.read_csv(TAB / "cd276_luad_sclc_region_overlap_check.csv").to_string(index=False))
print("\nQTL summary:")
print(qtl_summary.to_string(index=False))
print("\nL2G: n=", len(l2g), " max score=", round(l2g.score.max(), 4),
      " n>=0.5=", int((l2g.score >= 0.5).sum()),
      " n_luad_or_sclc=", int(l2g.is_luad_or_sclc.sum()))
