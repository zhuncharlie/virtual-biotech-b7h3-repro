#!/usr/bin/env python3
"""Build B7-H3 (CD276) safety evidence tables for the LUAD/SCLC candidacy review.

Inputs : data/raw/cd276_target_info_and_constraint.json
         data/raw/b7h3_known_drugs_raw.json
Outputs: results/tables/b7h3_safety_signals.csv
         results/tables/b7h3_agent_registry_lung_cancer.csv
         results/tables/b7h3_modality_class_toxicities.csv

Every row carries an explicit evidence_type:
  DATABASE      = value returned by a configured MCP query (MCP drug/target)
  PRIOR_KNOWLEDGE = model knowledge, not retrieved from any database this run
"""
import csv
import json
from pathlib import Path

# SUPERSEDED — revision 1, retained for provenance only.
# Revision 2 (revise_b7h3_safety_tables_for_review.py, 2026-10-20) withdrew the
# unverified confidence-level/bin statements below, added risk_level attribution,
# and corrected the expression and evidence-gap wording. Do not re-run this file:
# it would overwrite the corrected results tables.
raise SystemExit(
    "Superseded by revise_b7h3_safety_tables_for_review.py; not re-running."
)

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
TAB = ROOT / "results" / "tables"
TAB.mkdir(parents=True, exist_ok=True)

tgt = json.load(open(RAW / "cd276_target_info_and_constraint.json"))
drugs = json.load(open(RAW / "b7h3_known_drugs_raw.json"))

# ---------------------------------------------------------------- Table 1
rows = []


def add(domain, signal, metric, value, interpretation, source, etype, record_exists="yes"):
    rows.append(dict(signal_domain=domain, signal=signal, metric=metric, value=value,
                     interpretation=interpretation, evidence_source=source,
                     evidence_type=etype, record_exists=record_exists))


c = tgt["constraint"]
add("target_genetics", "CD276 LoF constraint", "obs/exp", f'{c["lof"]["obs"]}/{c["lof"]["exp"]}',
    "LoF observed below expectation (o/e 0.667); consistent with partial LoF tolerance, not haploinsufficiency",
    "mcp__target__get_target_info.constraint", "DATABASE")
add("target_genetics", "CD276 LoF o/e", "ratio (90% CI)",
    f'{c["lof"]["oe"]:.3f} ({c["lof"]["oeLower"]:.3f}-{c["lof"]["oeUpper"]:.3f})',
    "90% CI excludes 1.0, but upperBin 4 / upperBin6 2 indicates moderate (not extreme) constraint",
    "mcp__target__get_target_info.constraint", "DATABASE")
add("target_genetics", "CD276 LoF upper rank/bin", "rank; bin", "7792; upperBin 4; upperBin6 2",
    "Rank 7792 among genes by LoF tolerance; moderate constraint. No pLI field returned by this source.",
    "mcp__target__get_target_info.constraint", "DATABASE")
add("target_genetics", "CD276 missense constraint", "o/e", f'{c["missense"]["oe"]:.3f} ({c["missense"]["obs"]}/{c["missense"]["exp"]:.1f})',
    "Near-neutral missense constraint (o/e 0.866)",
    "mcp__target__get_target_info.constraint", "DATABASE")
add("target_genetics", "CD276 synonymous constraint", "o/e", f'{c["synonymous"]["oe"]:.3f} ({c["synonymous"]["obs"]}/{c["synonymous"]["exp"]:.1f})',
    "Synonymous o/e < 1 may reflect sequence/annotation effects; not used for safety inference",
    "mcp__target__get_target_info.constraint", "DATABASE")
add("target_genetics", "pLI", "value", "not returned",
    "Gap: this source did not provide pLI. Do not report a pLI for CD276 from this run.",
    "mcp__target__get_target_info.constraint", "DATABASE", "no")

add("target_safety", "OpenFDA target-level adverse events", "count", "0",
    "No target-linked OpenFDA AE record. Uninformative: absence of a target AE record is NOT evidence of safety.",
    "mcp__target__get_target_safety_profile", "DATABASE", "no")
add("mouse_phenotype", "Cd276 knockout phenotypes", "count", "0",
    "No mouse phenotype records in this source. Cannot support or exclude LOF toxicity from database evidence.",
    "mcp__target__get_mouse_phenotype", "DATABASE", "no")
add("mouse_phenotype", "Cd276 constitutive knockout", "viability (literature)",
    "viable and fertile; no overt spontaneous phenotype reported; reported immune-dysregulation phenotypes in challenge models",
    "Prior knowledge, not retrieved this run. Species caveat: mouse CD276 is only 52.4% identical to human (see homologue rows), so murine tolerability may not predict human on-target off-tumor toxicity.",
    "prior knowledge", "PRIOR_KNOWLEDGE", "n/a")
add("pharmacogenomics", "CD276 PGx relationships", "count", "0",
    "No pharmacogenomic relationships returned. No genotype-based patient-selection or toxicity biomarker available from this database.",
    "mcp__target__get_pharmacogenomics", "DATABASE", "no")

add("cross_species", "Human-mouse CD276 identity", "% identity", "52.43",
    "Low ligand-binding-domain conservation; human-targeting antibodies may not engage mouse CD276, limiting value of mouse on-target toxicity studies",
    "mcp__target__get_homologues", "DATABASE")
add("cross_species", "Human-chimpanzee CD276 identity", "% identity", "98.88",
    "High conservation; non-human primate is the appropriate species for on-target off-tumor assessment",
    "mcp__target__get_homologues", "DATABASE")
add("cross_species", "Human-macaque CD276 identity", "% identity", "94.57",
    "High conservation; supports macaque toxicity studies as pharmacologically relevant",
    "mcp__target__get_homologues", "DATABASE")

add("expression", "B7-H3 normal-tissue expression", "qualitative (literature)",
    "broad, low-level: lung epithelium, liver, heart, kidney, GI tract, prostate, endometrium/placenta, adrenal, pancreas",
    "Broad low-level expression creates on-target off-tumor exposure for any B7-H3-directed agent. NOT retrieved from a database in this run; no expression table was queried.",
    "prior knowledge", "PRIOR_KNOWLEDGE", "n/a")
add("expression", "B7-H3 tumour expression", "qualitative (literature)",
    "high in LUAD and SCLC; also high in many other carcinomas",
    "Tumour-selective overexpression relative to normal tissue is moderate, not absolute; therapeutic index depends on antigen density and payload potency",
    "prior knowledge", "PRIOR_KNOWLEDGE", "n/a")

add("class_agents", "Unique B7-H3 agents in known-drug database", "count", str(drugs["unique_drugs"]),
    "Only enoblituzumab and iodine-131 8H9 (omburtamab) are present; no ifinatamab deruxtecan or vobramitamab duocarmazine record",
    "mcp__drug__search_known_drugs", "DATABASE")

with open(TAB / "b7h3_safety_signals.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# ---------------------------------------------------------------- Table 2
agents = [
    dict(agent="Enoblituzumab", synonyms="MGA-271; MGA271", modality="Fc-optimized anti-B7-H3 mAb (cross-linking agent)",
         chembl_id="CHEMBL3545373", in_known_drug_db="yes", fda_approved="no",
         fda_warning_record="0 records", indications_in_db="HNSCC (ph2, withdrawn); prostate cancer (ph2, recruiting/active); melanoma (ph1, terminated)",
         lung_record="none", evidence_type="DATABASE",
         notes="Mechanism CD276 antigen cross-linking agent (ChEMBL). No approved indication, so a zero warning count is expected and does not indicate a clean safety profile."),
    dict(agent="Omburtamab (131I-8H9)", synonyms="8H9 131I; 8H9", modality="Radioimmunotherapy (131I-labelled anti-B7-H3 mAb)",
         chembl_id="CHEMBL2109310", in_known_drug_db="yes", fda_approved="no",
         fda_warning_record="0 records", indications_in_db="Neuroblastoma (ph2, terminated); leptomeningeal metastasis (ph2, terminated); peritoneum cancer (ph1, terminated); DIPG (ph1, withdrawn)",
         lung_record="none", evidence_type="DATABASE",
         notes="Mechanism CD276 antigen binding agent (ChEMBL). BLA for CNS/leptomeningeal neuroblastoma was not approved (prior knowledge); no FDA label exists, so zero warnings is uninformative."),
    dict(agent="Ifinatamab deruxtecan", synonyms="DS-7300; I-DXd", modality="DXd-payload ADC",
         chembl_id="not returned", in_known_drug_db="no", fda_approved="no",
         fda_warning_record="no record", indications_in_db="not in database",
         lung_record="none in database; prior knowledge: SCLC and other solid tumours",
         evidence_type="DATABASE (absence) / PRIOR_KNOWLEDGE (programme)",
         notes="EXPLICIT GAP: no FDA or known-drug record in this database. No safety conclusion can be drawn from the absence. Prior knowledge: DXd-class ILD/pneumonitis and myelosuppression are the principal risks."),
    dict(agent="Vobramitamab duocarmazine", synonyms="MGC018", modality="Duocarmycin-payload ADC",
         chembl_id="not returned", in_known_drug_db="no", fda_approved="no",
         fda_warning_record="no record", indications_in_db="not in database",
         lung_record="none in database; prior knowledge: prostate and other solid tumours",
         evidence_type="DATABASE (absence) / PRIOR_KNOWLEDGE (programme)",
         notes="EXPLICIT GAP: no record. Prior knowledge: duocarmycin-class myelosuppression, fatigue, rash, infusion reactions; ocular surface toxicity is a duocarmazine class signal."),
    dict(agent="B7-H3 CAR-T / T-cell engagers", synonyms="various investigational", modality="Cell therapy / bispecific engager",
         chembl_id="not returned", in_known_drug_db="no", fda_approved="no",
         fda_warning_record="no record", indications_in_db="not in database",
         lung_record="none in database", evidence_type="PRIOR_KNOWLEDGE",
         notes="EXPLICIT GAP: no record. Class risk is CRS/ICANS plus on-target injury to B7-H3-low normal tissue."),
]
with open(TAB / "b7h3_agent_registry_lung_cancer.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(agents[0].keys()))
    w.writeheader()
    w.writerows(agents)

# ---------------------------------------------------------------- Table 3
mods = [
    dict(modality="ADC (DXd payload)", toxicity="Interstitial lung disease / pneumonitis",
         driver="payload-driven (DXd class)", typical_severity="grade 1-2 common; grade 3-5 ILD is the dose-limiting / fatal risk",
         monitoring="baseline and serial chest imaging; hold on new dyspnoea/cough; steroids for grade >=2",
         relevance_LUAD="HIGH - baseline lung impairment and prior IO/radiation pneumonitis narrow the therapeutic window",
         relevance_SCLC="MODERATE-HIGH - competing thoracic radiation and prior IO",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="ADC (DXd payload)", toxicity="Myelosuppression (neutropenia, anaemia, thrombocytopenia)",
         driver="payload-driven; partly on-target off-tumour if B7-H3 is on marrow progenitors", typical_severity="grade 1-3; febrile neutropenia uncommon but dose-limiting",
         monitoring="CBC before each cycle; growth-factor support as per label",
         relevance_LUAD="MODERATE", relevance_SCLC="HIGH - overlaps platinum/etoposide myelosuppression",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="ADC (DXd payload)", toxicity="Nausea, fatigue, alopecia, stomatitis",
         driver="payload-driven", typical_severity="mostly grade 1-2, manageable",
         monitoring="supportive care", relevance_LUAD="LOW-MODERATE", relevance_SCLC="LOW-MODERATE",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="ADC (duocarmycin payload)", toxicity="Myelosuppression; fatigue; rash; infusion reactions",
         driver="payload-driven (duocarmycin)", typical_severity="grade 1-3; neutropenia dose-limiting",
         monitoring="CBC, premedication, skin review", relevance_LUAD="MODERATE", relevance_SCLC="MODERATE-HIGH",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="ADC (duocarmycin payload)", toxicity="Ocular surface toxicity (conjunctivitis, keratitis, dry eye)",
         driver="payload-driven (duocarmazine class)", typical_severity="grade 1-2 usually; grade 3 reported with some duocarmazine ADCs",
         monitoring="ophthalmology co-management; lubricants; steroid drops per protocol",
         relevance_LUAD="LOW-MODERATE", relevance_SCLC="LOW-MODERATE",
         evidence_type="PRIOR_KNOWLEDGE (class effect of duocarmazine ADCs); not supported by a retrieved record in this run"),
    dict(modality="CAR-T / T-cell engager", toxicity="Cytokine release syndrome",
         driver="payload-independent (immune activation)", typical_severity="grade 1-4; grade >=3 requires tocilizumab/ICU",
         monitoring="step-up dosing for engagers; CRS grading and tocilizumab availability",
         relevance_LUAD="MODERATE", relevance_SCLC="MODERATE",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="CAR-T / T-cell engager", toxicity="ICANS / neurotoxicity",
         driver="payload-independent (immune activation)", typical_severity="grade 1-4; rarely fatal",
         monitoring="neurological assessment; ICE scoring",
         relevance_LUAD="MODERATE - brain metastases common, confounds assessment",
         relevance_SCLC="MODERATE-HIGH - high baseline CNS metastasis burden",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="CAR-T / T-cell engager", toxicity="On-target off-tumour injury (lung, heart, liver, GI)",
         driver="payload-independent (B7-H3 expression on normal tissue)",
         typical_severity="theoretical/emerging; severity depends on antigen density and effector potency",
         monitoring="organ function; antigen-expression screening where available",
         relevance_LUAD="MODERATE", relevance_SCLC="MODERATE",
         evidence_type="PRIOR_KNOWLEDGE; normal-tissue expression was NOT measured in this run"),
    dict(modality="Radioimmunotherapy (131I-8H9/omburtamab)", toxicity="Myelosuppression / marrow suppression",
         driver="payload-driven (ionising radiation)", typical_severity="dose-dependent cytopenias; can be prolonged",
         monitoring="dosimetry, stem-cell support, CBC",
         relevance_LUAD="LOW (compartmental use not applicable)",
         relevance_SCLC="LOW-MODERATE",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="Radioimmunotherapy (131I-8H9/omburtamab)", toxicity="CNS toxicity when delivered intraventricularly/intrathecally",
         driver="payload-driven + route-dependent", typical_severity="chemical meningitis, raised ICP, leukoencephalopathy risk",
         monitoring="serial neuro-imaging and neuro-cognitive assessment",
         relevance_LUAD="LOW", relevance_SCLC="LOW-MODERATE (if leptomeningeal disease directed therapy)",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
    dict(modality="Radioimmunotherapy (131I-8H9/omburtamab)", toxicity="Hypothyroidism / secondary malignancy",
         driver="payload-driven (131I)", typical_severity="late effects", monitoring="thyroid function; long-term surveillance",
         relevance_LUAD="LOW", relevance_SCLC="LOW",
         evidence_type="PRIOR_KNOWLEDGE (modality class); not supported by a retrieved record in this run"),
]
with open(TAB / "b7h3_modality_class_toxicities.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(mods[0].keys()))
    w.writeheader()
    w.writerows(mods)

print("wrote", TAB / "b7h3_safety_signals.csv", len(rows), "rows")
print("wrote", TAB / "b7h3_agent_registry_lung_cancer.csv", len(agents), "rows")
print("wrote", TAB / "b7h3_modality_class_toxicities.csv", len(mods), "rows")
