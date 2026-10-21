#!/usr/bin/env python3
"""Revision 2 of the B7-H3 (CD276) safety tables, incorporating scientific review.

Corrections implemented (see results/reports/b7h3_safety_assessment.md, section 8):
  1. CD276 LoF constraint: report o/e 0.667 only. The retrieved record does not
     label a confidence level for its o/e interval, so no CI and no constraint bin
     are quoted anywhere in this table set (the previous revision's conflicting
     CI-level and bin statements are withdrawn).
  2. Every row now carries risk_level: target_level, payload_level, modality_level,
     or evidence_gap. Payload/modality toxicities are not attributed to B7-H3.
  3. Normal-tissue expression statement is qualified against HPA bulk RNA, HPA
     protein level and Census single-cell transcript.
  4. Zero-record agents are labelled as evidence gaps, not clean profiles.
  5. SCLC risk framing carried in the report, tied to the staged clinical decision.

Inputs : data/raw/cd276_target_info_and_constraint.json (own raw query)
         data/raw/b7h3_known_drugs_raw.json (own raw query)
         Cross-stream expression evidence verified from:
           work/target-biologist/results/tables/cd276_tissue_expression_summary.csv
           work/single-cell-analyst/results/tables/cd276_normal_tissue_organ_summary.csv
           work/single-cell-analyst/results/tables/cd276_normal_tissues_celltype_expression.csv
           work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv
Outputs: results/tables/b7h3_safety_signals.csv
         results/tables/b7h3_agent_registry_lung_cancer.csv
         results/tables/b7h3_modality_class_toxicities.csv
         data/processed/b7h3_expression_evidence_for_safety.csv
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
TAB = ROOT / "results" / "tables"
PROC.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

tgt = json.load(open(RAW / "cd276_target_info_and_constraint.json"))
drugs = json.load(open(RAW / "b7h3_known_drugs_raw.json"))
lof = tgt["constraint"]["lof"]

# ---------------------------------------------------------------- Table 1
rows = []


def add(domain, signal, metric, value, interpretation, source, etype,
        record_exists="yes", risk_level="target_level"):
    rows.append(dict(signal_domain=domain, signal=signal, metric=metric, value=value,
                     interpretation=interpretation, evidence_source=source,
                     evidence_type=etype, record_exists=record_exists,
                     risk_level=risk_level))


# Genetic constraint — point estimate only; no CI, no bin (review correction 1).
add("target_genetics", "CD276 LoF constraint", "obs/exp",
    f'{lof["obs"]}/{lof["exp"]:.1f}',
    "34 observed vs 51.0 expected. o/e 0.667 indicates moderate, not extreme, LoF "
    "constraint: partial depletion of LoF variants rather than strict haploinsufficiency. "
    "This is moderate genetic constraint, not a safety-favourable 'tolerance' signal.",
    "mcp__target__get_target_info.constraint", "DATABASE")
add("target_genetics", "CD276 LoF o/e", "ratio", f'{lof["oe"]:.3f}',
    "Point estimate 0.667. The retrieved record does not label a confidence level for "
    "its o/e interval, so no CI is reported and no constraint bin is quoted. Do not "
    "quote a CI or a bin for this value.",
    "mcp__target__get_target_info.constraint", "DATABASE")
add("target_genetics", "CD276 missense constraint", "o/e",
    f'{tgt["constraint"]["missense"]["oe"]:.3f} '
    f'({tgt["constraint"]["missense"]["obs"]}/{tgt["constraint"]["missense"]["exp"]:.1f})',
    "Near-neutral missense constraint (o/e 0.866).",
    "mcp__target__get_target_info.constraint", "DATABASE")
add("target_genetics", "CD276 synonymous constraint", "o/e",
    f'{tgt["constraint"]["synonymous"]["oe"]:.3f} '
    f'({tgt["constraint"]["synonymous"]["obs"]}/{tgt["constraint"]["synonymous"]["exp"]:.1f})',
    "Synonymous o/e 0.868 may reflect sequence/annotation effects; not used for safety inference.",
    "mcp__target__get_target_info.constraint", "DATABASE")
add("target_genetics", "pLI", "value", "not returned",
    "Gap: this source did not provide pLI. No pLI should be reported for CD276 from this run.",
    "mcp__target__get_target_info.constraint", "DATABASE", "no")

# Zero-record target queries — gaps, not reassurance.
add("target_safety", "OpenFDA target-level adverse events", "count", "0",
    "No target-linked OpenFDA adverse-event record. Uninformative: absence of a target AE "
    "record is NOT evidence of safety. The same query returned zero for the target overall.",
    "mcp__target__get_target_safety_profile", "DATABASE", "no", "evidence_gap")
add("mouse_phenotype", "Cd276 knockout phenotypes", "count", "0",
    "No mouse phenotype records in this source. Cannot support or exclude LoF toxicity from "
    "database evidence.",
    "mcp__target__get_mouse_phenotype", "DATABASE", "no", "evidence_gap")
add("mouse_phenotype", "Cd276 constitutive knockout", "viability (literature)",
    "viable and fertile; no overt spontaneous phenotype reported; immune-dysregulation "
    "phenotypes reported mainly in challenge models",
    "PRIOR KNOWLEDGE. Species caveat: mouse CD276 is only 52.4% identical to human at the "
    "query region, so murine tolerability may not predict human on-target off-tumour toxicity.",
    "prior knowledge", "PRIOR_KNOWLEDGE", "n/a")
add("pharmacogenomics", "CD276 PGx relationships", "count", "0",
    "No pharmacogenomic relationships returned. No genotype-based patient-selection or "
    "toxicity biomarker is available from this database.",
    "mcp__target__get_pharmacogenomics", "DATABASE", "no", "evidence_gap")

# Cross-species.
add("cross_species", "Human-mouse CD276 identity", "% identity", "52.43",
    "Low conservation at the query region; human-targeting antibodies may not engage mouse "
    "CD276, limiting the value of mouse on-target toxicity studies.",
    "mcp__target__get_homologues", "DATABASE")
add("cross_species", "Human-macaque CD276 identity", "% identity", "94.57",
    "High conservation; macaque is the pharmacologically relevant toxicology species.",
    "mcp__target__get_homologues", "DATABASE")
add("cross_species", "Human-chimpanzee CD276 identity", "% identity", "98.88",
    "High conservation; supports non-human primate on-target off-tumour assessment.",
    "mcp__target__get_homologues", "DATABASE")

# Normal-tissue expression — qualified (review correction 3).
add("expression", "B7-H3 normal-tissue expression breadth", "HPA bulk RNA",
    "109/120 entries detected; median 834 TPM; 49/120 at RNA level 4-5",
    "TARGET-LEVEL. Broad low-level normal expression is supported by HPA bulk RNA and prior "
    "knowledge. It creates off-tumour antigen exposure, but TPM is bulk tissue RNA and is not "
    "surface protein density.",
    "work/target-biologist/results/tables/cd276_tissue_expression_summary.csv",
    "DATABASE (cross-stream artifact)", "yes")
add("expression", "B7-H3 in normal lung", "HPA bulk RNA / protein",
    "RNA 1,682.5 TPM (level 4); HPA protein level 2 (reliable)",
    "TARGET-LEVEL. Moderate bulk RNA and moderate (level 2) protein in normal lung. The bulk "
    "lung RNA is partly attributable to resident macrophages (HPA macrophage 9,456-14,497 TPM). "
    "This does NOT establish high B7-H3 protein on normal lung epithelium.",
    "work/target-biologist/results/tables/cd276_tissue_expression_summary.csv",
    "DATABASE (cross-stream artifact)", "yes")
add("expression", "B7-H3 in normal lung", "Census single-cell transcript (CPM)",
    "organ weighted mean 13.9 CPM (12,315 cells, 4 donors); epithelial 17.1 CPM; "
    "macrophage 39.6 CPM; all medians 0",
    "TARGET-LEVEL. Cell-level normal-lung CD276 transcript is comparatively low (13.9 CPM; at "
    "the median of 19 sampled organs and well below skin 46.0 and kidney 42.6). The macrophage "
    "signal is RNA-only (HPA macrophage protein unreliable). Medians are 0 and CPM is not protein.",
    "work/single-cell-analyst/results/tables/cd276_normal_tissue_organ_summary.csv; "
    "cd276_normal_tissues_celltype_expression.csv",
    "DATABASE (cross-stream artifact)", "yes")
add("expression", "B7-H3 in tumour and stroma", "Census single-cell transcript (CPM)",
    "LUAD fibroblast 75.9 > alveolar macrophage 34.1 > epithelial 28.6 > malignant 23.6; "
    "SCLC fibroblast 68.1 > macrophage 48.8 > epithelial 28.5 (no malignant label)",
    "TARGET-LEVEL. Stromal/immune transcript exceeds malignant transcript in both indications, "
    "symmetric across LUAD and SCLC. This is an antigen-sink and bystander-exposure consideration, "
    "not evidence of malignant-cell surface density. Medians are 0; transcript is not protein.",
    "work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv",
    "DATABASE (cross-stream artifact)", "yes")
add("expression", "B7-H3 tumour overexpression", "qualitative (literature assertion)",
    "asserted high in LUAD/SCLC and many carcinomas; NOT verified in this run",
    "Downgraded from 'overexpressed relative to normal'. Single-cell transcript does not show "
    "malignant-cell dominance (LUAD malignant 23.6 vs normal-region epithelial 28.6 CPM; paired "
    "donor ratios 3.26/3.40/1.09 in 2/3 >=2x, n=3). Tumour selectivity remains unproven; a "
    "protein-level tumour-to-normal density study is the decisive gate.",
    "prior knowledge + cross-stream transcript contradiction",
    "PRIOR_KNOWLEDGE", "n/a")
add("expression", "Soluble B7-H3 antigen sink", "qualitative (literature)",
    "ectodomain can be shed; magnitude not quantified in this run",
    "TARGET-LEVEL. Soluble B7-H3 may act as a decoy/sink competing with tumour binding. Neither "
    "shedding rate nor plasma concentration is retrievable from the configured databases.",
    "prior knowledge", "PRIOR_KNOWLEDGE", "n/a")

# Agent-coverage gaps (review correction 4).
add("class_agents", "Unique B7-H3 agents in known-drug database", "count", str(drugs["unique_drugs"]),
    "Only enoblituzumab and iodine-131 8H9 (omburtamab) are present. Both are unapproved. "
    "No ifinatamab deruxtecan, vobramitamab duocarmazine, or CAR-T/engager record exists.",
    "mcp__drug__search_known_drugs", "DATABASE")
add("class_agents", "Ifinatamab deruxtecan (I-DXd) safety records", "count", "0",
    "EVIDENCE GAP, not a clean safety profile. No drug record exists, so no agent-specific "
    "OpenFDA warning query was possible. DXd-class ILD/pneumonitis and myelosuppression remain "
    "prior knowledge only.",
    "mcp__drug__search_known_drugs; mcp__drug__get_drug_warnings", "DATABASE", "no", "evidence_gap")
add("class_agents", "Vobramitamab duocarmazine (MGC018) safety records", "count", "0",
    "EVIDENCE GAP, not a clean safety profile. No drug record exists, so no agent-specific "
    "OpenFDA warning query was possible. Duocarmycin-class myelosuppression and ocular surface "
    "toxicity remain prior knowledge only.",
    "mcp__drug__search_known_drugs; mcp__drug__get_drug_warnings", "DATABASE", "no", "evidence_gap")
add("class_agents", "Enoblituzumab / omburtamab warning records", "count", "0 each",
    "Zero FDA warning records is expected for unapproved agents and does not indicate a clean "
    "safety profile. The warnings tool was verified functional with a positive control.",
    "mcp__drug__get_drug_warnings", "DATABASE", "no", "evidence_gap")

with open(TAB / "b7h3_safety_signals.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# ---------------------------------------------------------------- Table 2
agents = [
    dict(agent="Enoblituzumab", synonyms="MGA-271; MGA271",
         modality="Fc-optimized anti-B7-H3 mAb (cross-linking agent)",
         chembl_id="CHEMBL3545373", in_known_drug_db="yes", fda_approved="no",
         fda_warning_record="0 records", indications_in_db="HNSCC (ph2, withdrawn); prostate cancer (ph2, recruiting/active); melanoma (ph1, terminated)",
         lung_record="none", evidence_type="DATABASE",
         risk_level="evidence_gap",
         notes="Unapproved; zero warning records reflects absence of an FDA label, not a clean safety profile. Mechanism: CD276 antigen cross-linking agent (ChEMBL)."),
    dict(agent="Omburtamab (131I-8H9)", synonyms="8H9 131I; 8H9",
         modality="Radioimmunotherapy (131I-labelled anti-B7-H3 mAb)",
         chembl_id="CHEMBL2109310", in_known_drug_db="yes", fda_approved="no",
         fda_warning_record="0 records", indications_in_db="Neuroblastoma (ph2, terminated); leptomeningeal metastasis (ph2, terminated); peritoneum cancer (ph1, terminated); DIPG (ph1, withdrawn)",
         lung_record="none", evidence_type="DATABASE",
         risk_level="evidence_gap",
         notes="Unapproved; zero warning records reflects absence of an FDA label, not a clean safety profile. Compartmental delivery limits relevance to systemic lung-cancer use."),
    dict(agent="Ifinatamab deruxtecan", synonyms="DS-7300; I-DXd", modality="DXd-payload ADC",
         chembl_id="not returned", in_known_drug_db="no", fda_approved="no",
         fda_warning_record="no record", indications_in_db="not in database",
         lung_record="none in database; prior knowledge: SCLC and other solid tumours",
         evidence_type="DATABASE (absence) / PRIOR_KNOWLEDGE (programme)",
         risk_level="evidence_gap",
         notes="EXPLICIT EVIDENCE GAP: no drug record, therefore no agent-specific OpenFDA query was possible. Zero retrievable records is NOT a clean safety profile. Prior knowledge: DXd-class ILD/pneumonitis and myelosuppression; these are payload-level, not B7-H3 biology."),
    dict(agent="Vobramitamab duocarmazine", synonyms="MGC018", modality="Duocarmycin-payload ADC",
         chembl_id="not returned", in_known_drug_db="no", fda_approved="no",
         fda_warning_record="no record", indications_in_db="not in database",
         lung_record="none in database; prior knowledge: prostate and other solid tumours",
         evidence_type="DATABASE (absence) / PRIOR_KNOWLEDGE (programme)",
         risk_level="evidence_gap",
         notes="EXPLICIT EVIDENCE GAP: no drug record, therefore no agent-specific OpenFDA query was possible. Zero retrievable records is NOT a clean safety profile. Prior knowledge: duocarmycin-class myelosuppression, fatigue, rash, infusion reactions, ocular surface toxicity; these are payload-level."),
    dict(agent="B7-H3 CAR-T / T-cell engagers", synonyms="various investigational",
         modality="Cell therapy / bispecific engager",
         chembl_id="not returned", in_known_drug_db="no", fda_approved="no",
         fda_warning_record="no record", indications_in_db="not in database",
         lung_record="none in database", evidence_type="PRIOR_KNOWLEDGE",
         risk_level="evidence_gap",
         notes="EXPLICIT EVIDENCE GAP: no record. CRS/ICANS are modality-level immune-activation risks; only the normal-tissue antigen-density component is target-level. Neither is quantified in this run."),
]
with open(TAB / "b7h3_agent_registry_lung_cancer.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(agents[0].keys()))
    w.writeheader()
    w.writerows(agents)

# ---------------------------------------------------------------- Table 3
mods = [
    dict(modality="ADC (DXd payload)", toxicity="Interstitial lung disease / pneumonitis",
         risk_level="payload_level",
         driver="payload-driven (DXd class); NOT B7-H3 biology",
         typical_severity="grade 1-2 common; grade 3-5 ILD is the dose-limiting / fatal risk",
         monitoring="baseline and serial chest imaging; hold on new dyspnoea/cough; steroids for grade >=2",
         relevance_LUAD="HIGH - baseline lung impairment and prior IO/radiation pneumonitis narrow the therapeutic window",
         relevance_SCLC="MODERATE-HIGH - competing thoracic radiation and prior IO",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="ADC (DXd payload)", toxicity="Myelosuppression (neutropenia, anaemia, thrombocytopenia)",
         risk_level="payload_level",
         driver="payload-driven (DXd class). No transcript support for on-target marrow injury: Census bone marrow 0.21 CPM, 0.12% expressing; marrow stromal max 22.4 CPM.",
         typical_severity="grade 1-3; febrile neutropenia uncommon but dose-limiting",
         monitoring="CBC before each cycle; growth-factor support as per label",
         relevance_LUAD="MODERATE", relevance_SCLC="HIGH - overlaps platinum/etoposide myelosuppression",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="ADC (DXd payload)", toxicity="Nausea, fatigue, alopecia, stomatitis",
         risk_level="payload_level", driver="payload-driven; NOT B7-H3 biology",
         typical_severity="mostly grade 1-2, manageable",
         monitoring="supportive care", relevance_LUAD="LOW-MODERATE", relevance_SCLC="LOW-MODERATE",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="ADC (duocarmycin payload)", toxicity="Myelosuppression; fatigue; rash; infusion reactions",
         risk_level="payload_level", driver="payload-driven (duocarmycin); NOT B7-H3 biology",
         typical_severity="grade 1-3; neutropenia dose-limiting",
         monitoring="CBC, premedication, skin review", relevance_LUAD="MODERATE", relevance_SCLC="MODERATE-HIGH",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="ADC (duocarmycin payload)", toxicity="Ocular surface toxicity (conjunctivitis, keratitis, dry eye)",
         risk_level="payload_level",
         driver="payload-driven (duocarmazine class); NOT B7-H3 biology",
         typical_severity="grade 1-2 usually; grade 3 reported with some duocarmazine ADCs",
         monitoring="ophthalmology co-management; lubricants; steroid drops per protocol",
         relevance_LUAD="LOW-MODERATE", relevance_SCLC="LOW-MODERATE",
         evidence_type="PRIOR_KNOWLEDGE (class effect of duocarmazine ADCs); not supported by a retrieved record in this run"),
    dict(modality="CAR-T / T-cell engager", toxicity="Cytokine release syndrome",
         risk_level="modality_level",
         driver="modality-level immune activation; NOT B7-H3 biology",
         typical_severity="grade 1-4; grade >=3 requires tocilizumab/ICU",
         monitoring="step-up dosing for engagers; CRS grading and tocilizumab availability",
         relevance_LUAD="MODERATE", relevance_SCLC="MODERATE",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="CAR-T / T-cell engager", toxicity="ICANS / neurotoxicity",
         risk_level="modality_level",
         driver="modality-level immune activation; NOT B7-H3 biology",
         typical_severity="grade 1-4; rarely fatal",
         monitoring="neurological assessment; ICE scoring",
         relevance_LUAD="MODERATE - brain metastases common, confounds assessment",
         relevance_SCLC="MODERATE-HIGH - high baseline CNS metastasis burden",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="CAR-T / T-cell engager", toxicity="On-target off-tumour injury (lung, heart, liver, GI)",
         risk_level="target_level",
         driver="target-level: B7-H3 expression on normal tissue plus effector potency; antigen density not measured",
         typical_severity="theoretical/emerging; severity depends on antigen density and effector potency",
         monitoring="organ function; antigen-expression screening where available",
         relevance_LUAD="MODERATE", relevance_SCLC="MODERATE",
         evidence_type="PRIOR_KNOWLEDGE; normal-tissue protein density NOT measured in this run"),
    dict(modality="Radioimmunotherapy (131I-8H9/omburtamab)", toxicity="Myelosuppression / marrow suppression",
         risk_level="payload_level", driver="payload-driven (ionising radiation); NOT B7-H3 biology",
         typical_severity="dose-dependent cytopenias; can be prolonged",
         monitoring="dosimetry, stem-cell support, CBC",
         relevance_LUAD="LOW (compartmental use not applicable)",
         relevance_SCLC="LOW-MODERATE",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="Radioimmunotherapy (131I-8H9/omburtamab)", toxicity="CNS toxicity when delivered intraventricularly/intrathecally",
         risk_level="payload_level", driver="payload-driven (radiation) plus route-dependent; NOT B7-H3 biology",
         typical_severity="chemical meningitis, raised ICP, leukoencephalopathy risk",
         monitoring="serial neuro-imaging and neuro-cognitive assessment",
         relevance_LUAD="LOW", relevance_SCLC="LOW-MODERATE (if leptomeningeal disease directed therapy)",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="Radioimmunotherapy (131I-8H9/omburtamab)", toxicity="Hypothyroidism / secondary malignancy",
         risk_level="payload_level", driver="payload-driven (131I) late effects; NOT B7-H3 biology",
         typical_severity="late effects", monitoring="thyroid function; long-term surveillance",
         relevance_LUAD="LOW", relevance_SCLC="LOW",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
]
with open(TAB / "b7h3_modality_class_toxicities.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(mods[0].keys()))
    w.writeheader()
    w.writerows(mods)

# ------------------------------------------- Processed expression evidence table
expr = [
    # domain, source, entity, metric, value, n_cells, n_donors, qualification, source_artifact
    ("normal_tissue_HPA_bulk", "Human Protein Atlas (via expression MCP, target-biologist)",
     "lung", "RNA TPM", "1682.5", "", "", "HPA RNA level 4; protein level 2 (reliable)",
     "work/target-biologist/results/tables/cd276_tissue_expression_summary.csv"),
    ("normal_tissue_HPA_bulk", "Human Protein Atlas (via expression MCP, target-biologist)",
     "lung", "protein level", "2", "", "", "reliable IHC level; ordinal, not molecules per cell",
     "work/target-biologist/results/tables/cd276_tissue_expression_summary.csv"),
    ("normal_tissue_HPA_bulk", "Human Protein Atlas (via expression MCP, target-biologist)",
     "macrophage", "RNA TPM", "9455.5", "", "", "protein unreliable (-1); RNA-only",
     "work/target-biologist/results/tables/cd276_tissue_expression_summary.csv"),
    ("normal_tissue_HPA_bulk", "Human Protein Atlas (via expression MCP, target-biologist)",
     "alternatively activated macrophage", "RNA TPM", "14497.0", "", "",
     "highest HPA entry; protein unreliable (-1); RNA-only",
     "work/target-biologist/results/tables/cd276_tissue_expression_summary.csv"),
    ("normal_tissue_Census", "CELLxGENE Census (single-cell-analyst)",
     "normal lung (all cells)", "weighted mean CPM", "13.901", "12315", "4",
     "median of 19 sampled organs; 9.8% cells expressing",
     "work/single-cell-analyst/results/tables/cd276_normal_tissue_organ_summary.csv"),
    ("normal_tissue_Census", "CELLxGENE Census (single-cell-analyst)",
     "normal lung epithelial cell", "mean CPM", "17.091", "851", "4",
     "6.8% expressing; median 0",
     "work/single-cell-analyst/results/tables/cd276_normal_tissues_celltype_expression.csv"),
    ("normal_tissue_Census", "CELLxGENE Census (single-cell-analyst)",
     "normal lung macrophage", "mean CPM", "39.637", "3334", "4",
     "33.0% expressing; median 0; highest lung cell type",
     "work/single-cell-analyst/results/tables/cd276_normal_tissues_celltype_expression.csv"),
    ("tumour_LUAD_Census", "CELLxGENE Census (single-cell-analyst)",
     "LUAD fibroblast", "mean CPM", "75.915", "3979", "15", "26.7% expressing; median 0",
     "work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv"),
    ("tumour_LUAD_Census", "CELLxGENE Census (single-cell-analyst)",
     "LUAD alveolar macrophage", "mean CPM", "34.088", "63656", "101", "25.9% expressing",
     "work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv"),
    ("tumour_LUAD_Census", "CELLxGENE Census (single-cell-analyst)",
     "LUAD epithelial cell", "mean CPM", "28.611", "5270", "16", "15.2% expressing",
     "work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv"),
    ("tumour_LUAD_Census", "CELLxGENE Census (single-cell-analyst)",
     "LUAD malignant cell", "mean CPM", "23.584", "26179", "92",
     "15.4% expressing; below fibroblast and epithelial mean",
     "work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv"),
    ("tumour_SCLC_Census", "CELLxGENE Census (single-cell-analyst)",
     "SCLC fibroblast", "mean CPM", "68.101", "328", "9", "26.2% expressing; median 0",
     "work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv"),
    ("tumour_SCLC_Census", "CELLxGENE Census (single-cell-analyst)",
     "SCLC macrophage", "mean CPM", "48.813", "375", "9", "7.7% expressing",
     "work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv"),
    ("tumour_SCLC_Census", "CELLxGENE Census (single-cell-analyst)",
     "SCLC epithelial cell", "mean CPM", "28.537", "25988", "9",
     "19.5% expressing; NO malignant label available for SCLC",
     "work/single-cell-analyst/results/tables/cd276_luad_sclc_celltype_expression.csv"),
]
with open(PROC / "b7h3_expression_evidence_for_safety.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["risk_domain", "source", "entity", "metric", "value", "n_cells",
                "n_donors", "qualification", "source_artifact"])
    w.writerows(expr)

print("wrote", TAB / "b7h3_safety_signals.csv", len(rows), "rows")
print("wrote", TAB / "b7h3_agent_registry_lung_cancer.csv", len(agents), "rows")
print("wrote", TAB / "b7h3_modality_class_toxicities.csv", len(mods), "rows")
print("wrote", PROC / "b7h3_expression_evidence_for_safety.csv", len(expr), "rows")
