#!/usr/bin/env python
"""Build the B7-H3 (CD276) modality ranking for LUAD and SCLC.

Scoring is explicit and reproducible.  Five dimensions are scored 1-5 and
combined with fixed weights:

    mechanistic fit to the biology          0.25
    clinical precedence in the indication   0.25
    feasibility (CMC/manufacturing)         0.20
    differentiation vs SOC/competitor ADCs  0.15
    risk profile (5 = lowest risk)          0.15

Clinical precedence is evidence of feasibility, NOT efficacy.  The upstream
clinical stream found no proven B7-H3 efficacy in LUAD or SCLC.

REVISION 2026-10-20 (post scientific review):
  - SCLC ADC decision is a STAGED GO: conditional on (a) a class-level Phase 3
    efficacy readout and (b) a differentiated molecule/profile.
  - LUAD is DEPRIORITIZED on competitive/precedence grounds, not declared a
    scientific no-go.  LUAD ADC clinical precedence is scored 1/5 (no
    LUAD-specific trial), while acknowledging LUAD eligibility in nonsquamous
    NSCLC trials NCT07464327 / NCT06780085 / NCT07824882.
  - The stromal > malignant transcript pattern is applied symmetrically to SCLC
    and LUAD as a shared antigen-sink/surface-antigen caveat.
  - Normal lung is described with its full qualification: bulk RNA level 4
    (1,683 TPM) but HPA protein level 2, and a low Census cell-level weighted
    mean of 13.9 CPM.
  - Target-level risk is separated from payload-level risk.
  Scores are unchanged except LUAD ADC clinical precedence (2 -> 1).

Outputs:
    results/tables/b7h3_modality_ranking.csv
    results/tables/b7h3_modality_precedent_evidence.csv
    results/tables/cd276_normal_lung_expression_qualification.csv
    results/tables/b7h3_target_vs_payload_risk_attribution.csv
    results/figures/b7h3_modality_composite_scores.png
    results/figures/b7h3_modality_dimension_heatmap.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RUN = Path(
    "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
    "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/"
    "medchem-pharmacologist"
)
TAB = RUN / "results/tables"
FIG = RUN / "results/figures"
TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

WEIGHTS = {
    "mechanistic_fit": 0.25,
    "clinical_precedence_in_indication": 0.25,
    "feasibility_cmc_manufacturing": 0.20,
    "differentiation_vs_soc_and_competitor_adcs": 0.15,
    "risk_profile_5_is_lowest_risk": 0.15,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

# ---------------------------------------------------------------------------
# Scores.  Each row is one indication x modality.  The rationale fields carry
# the audit trail; the score fields are the judgement that the report defends.
# ---------------------------------------------------------------------------
ROWS = [
    # ----------------------------- SCLC -----------------------------------
    {
        "indication": "SCLC",
        "rank": 1,
        "modality": "B7-H3 ADC (topoisomerase-I payload preferred)",
        "mechanistic_fit": 5,
        "clinical_precedence_in_indication": 5,
        "feasibility_cmc_manufacturing": 4,
        "differentiation_vs_soc_and_competitor_adcs": 3,
        "risk_profile_5_is_lowest_risk": 3,
        "decision_status": "STAGED GO - conditional (lead modality)",
        "recommendation": (
            "GO conditional on (a) a class-level Phase 3 efficacy readout and "
            "(b) a differentiated molecule/profile"
        ),
        "decision_conditions": (
            "Feasibility is established (26 SCLC-contributing trials; 6 Phase 3 "
            "trials across only 4 molecules), but efficacy is not. Commit only "
            "after (a) a class-level Phase 3 efficacy result is available and "
            "positive (e.g. ARTEMIS-008 or I-DXd vs physician's choice); "
            "ARTEMIS-008 is completed with no results posted, and the only posted "
            "SCLC-specific result is MGC018 ORR 0/9 (n=9), which is a small "
            "under-enrolled signal, not class-level failure; and (b) the molecule "
            "is differentiated versus I-DXd/HS-20093/MHB088C/YL201 (novel payload/"
            "linker, lower ILD risk, biomarker-defined niche, or combination)."
        ),
        "key_precedent_in_scope": (
            "6 Phase 3 B7-H3 ADC trials contributing SCLC (I-DXd NCT06203210; "
            "HS-20093 NCT06498479/NCT07099898; MHB088C NCT06954246; YL201 "
            "NCT06612151); 26 SCLC-contributing trials total. Only posted "
            "SCLC result is MGC018 ORR 0/9 (n=9); ARTEMIS-008 completed with no "
            "posted results."
        ),
        "rationale": (
            "Payload delivery fits a surface antigen with no intrinsic dependency; "
            "the ADC class is the only B7-H3 modality with Phase 3 investment in "
            "SCLC. Feasibility is proven, efficacy is not, so this is a staged GO. "
            "Differentiation from I-DXd/HS-20093 and from DLL3/TROP2 agents is the "
            "binding constraint. The stromal>malignant transcript pattern is a "
            "shared antigen-sink/surface-antigen caveat here as in LUAD, not a "
            "LUAD-specific disqualifier."
        ),
        "target_level_risks": (
            "Broad low-level normal-tissue B7-H3, including lung and B7-H3-rich "
            "myeloid cells; stromal/myeloid antigen sink (SCLC fibroblast 68.1 CPM "
            "vs epithelial 28.5 CPM, malignant-to-fibroblast ratio 0.42); soluble "
            "B7-H3 decoy; unquantified surface density and internalization."
        ),
        "payload_level_risks": (
            "DXd-class ILD/pneumonitis; myelosuppression; off-tumour payload "
            "delivery to normal lung/liver and myeloid cells. These are "
            "payload/format liabilities, not CD276 target biology."
        ),
        "timeline_to_clinic_years": "2.5-4.0",
        "cost_to_ind_usd_m": "15-30",
        "cost_full_development_usd_m": "800-1500",
        "evidence_sources": (
            "work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv; "
            "work/target-biologist/results/tables/cd276_tractability_by_modality.csv; "
            "work/fda-safety-officer/results/reports/b7h3_safety_assessment.md; "
            "results/tables/b7h3_modality_precedent_evidence.csv"
        ),
    },
    {
        "indication": "SCLC",
        "rank": 2,
        "modality": "B7-H3 bispecific / T-cell engager",
        "mechanistic_fit": 4,
        "clinical_precedence_in_indication": 2,
        "feasibility_cmc_manufacturing": 4,
        "differentiation_vs_soc_and_competitor_adcs": 3,
        "risk_profile_5_is_lowest_risk": 2,
        "decision_status": "BACKUP - conditional on a tumour-selective format",
        "recommendation": "Backup - only with a tumour-selective format",
        "decision_conditions": (
            "Pursue only as a backup to the ADC and only with a density-gated, "
            "masked/prodrug or affinity-tuned format that addresses the shared "
            "normal-tissue/stromal antigen sink."
        ),
        "key_precedent_in_scope": (
            "No SCLC or LUAD B7-H3 T-cell engager. MGD009 (B7-H3xCD3 DART) was "
            "Phase 1 in NSCLC context and terminated for business reasons "
            "(NCT02628535). IBB0979 is a B7-H3xIL-10R fusion, not a TCE; gocatamig "
            "is DLL3xCD3 and is used only in combination with I-DXd."
        ),
        "rationale": (
            "Off-the-shelf antibody logistics and T-cell redirection are validated "
            "in SCLC by DLL3-directed agents, but there is no B7-H3 TCE efficacy or "
            "safety precedent. Broad low-level normal-tissue B7-H3, including lung "
            "and myeloid cells, makes the therapeutic window the central problem."
        ),
        "target_level_risks": (
            "On-target/off-tumour killing of B7-H3-low normal lung and myeloid "
            "cells; shared stromal/myeloid antigen sink; unquantified surface "
            "density; narrow window without a density/masking strategy."
        ),
        "payload_level_risks": (
            "CRS/ICANS intrinsic to T-cell redirection; T-cell exhaustion and "
            "immunosuppressive SCLC microenvironment. These are format liabilities, "
            "not CD276 target biology."
        ),
        "timeline_to_clinic_years": "2.0-3.5",
        "cost_to_ind_usd_m": "10-25",
        "cost_full_development_usd_m": "600-1200",
        "evidence_sources": (
            "work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv "
            "(rows NCT02628535, NCT07076095); "
            "work/target-biologist/results/tables/cd276_tissue_expression_summary.csv; "
            "results/tables/b7h3_modality_precedent_evidence.csv"
        ),
    },
    {
        "indication": "SCLC",
        "rank": 3,
        "modality": "B7-H3 CAR-T (autologous; NK-CAR not clinically precedented)",
        "mechanistic_fit": 4,
        "clinical_precedence_in_indication": 2,
        "feasibility_cmc_manufacturing": 2,
        "differentiation_vs_soc_and_competitor_adcs": 3,
        "risk_profile_5_is_lowest_risk": 2,
        "decision_status": "NOT NOW - research track",
        "recommendation": "Not now - research track",
        "decision_conditions": (
            "Revisit only if the single Phase 1 (NCT07509034) reports a durability "
            "or safety signal and an allogeneic/manufacturing solution matures."
        ),
        "key_precedent_in_scope": (
            "One Phase 1 autologous B7-H3 CAR-T in pretreated ES-SCLC "
            "(NCT07509034, recruiting, start 2026-10-25, n=40, MTD/DCR). An "
            "EGFR/B7H3 dual CAR-T is early Phase 1 in lung cancer without a "
            "LUAD-specific cohort (NCT05341492). No B7-H3 NK-CAR trial found."
        ),
        "rationale": (
            "Surface antigen and T-cell killing rationale are sound, but the SCLC "
            "evidence is a single Phase 1 with no results. Autologous vein-to-vein "
            "manufacturing, lymphodepletion and solid-tumour trafficking/persistence "
            "make this slower and less scalable than an ADC or TCE."
        ),
        "target_level_risks": (
            "On-target/off-tumour toxicity in normal lung and myeloid cells; shared "
            "stromal/myeloid antigen sink; unquantified surface density."
        ),
        "payload_level_risks": (
            "Autologous manufacturing failure/logistics; CRS/ICANS; poor "
            "solid-tumour trafficking and persistence; lymphodepletion intolerance "
            "in heavily pretreated SCLC. These are cell-therapy liabilities, not "
            "CD276 target biology."
        ),
        "timeline_to_clinic_years": "2.0-3.0",
        "cost_to_ind_usd_m": "20-40",
        "cost_full_development_usd_m": "800-1500",
        "evidence_sources": (
            "work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv "
            "(rows NCT07509034, NCT05341492); "
            "results/tables/b7h3_modality_precedent_evidence.csv"
        ),
    },
    {
        "indication": "SCLC",
        "rank": 4,
        "modality": "B7-H3 radioimmunotherapy / radioligand (177Lu or 131I)",
        "mechanistic_fit": 3,
        "clinical_precedence_in_indication": 2,
        "feasibility_cmc_manufacturing": 2,
        "differentiation_vs_soc_and_competitor_adcs": 3,
        "risk_profile_5_is_lowest_risk": 2,
        "decision_status": "NOT NOW - research/combination track",
        "recommendation": "Not now - research/combination track",
        "decision_conditions": (
            "Consider as an orthogonal combination/later-line option only after "
            "dosimetry demonstrates an acceptable normal-lung and marrow window."
        ),
        "key_precedent_in_scope": (
            "177Lu-BetaBart Phase 1/2 in relapsed solid tumours including an SCLC "
            "cohort (NCT07189871, recruiting, n=61, cohort size not reported). "
            "8H9 131I (omburtamab) reached Phase 2 only in compartmental/CNS "
            "indications and was terminated; no systemic lung-cancer record."
        ),
        "rationale": (
            "Radiation crossfire can address antigen heterogeneity and does not "
            "require internalization, which is attractive given unquantified B7-H3 "
            "density and shedding. But isotope supply, radiochemistry, dosimetry, "
            "radiation safety and normal-lung/marrow dose keep it behind ADC and TCE "
            "for a systemic SCLC programme."
        ),
        "target_level_risks": (
            "On-target absorbed dose to normal lung and B7-H3-rich myeloid tissue; "
            "shared stromal/myeloid antigen sink; unquantified surface density."
        ),
        "payload_level_risks": (
            "Marrow and normal-lung radiation dose; kidney/off-target dose; isotope "
            "supply and cold-chain; repeated-dosing logistics; compartmental 8H9 "
            "precedent does not transfer to IV dosing. These are radioligand "
            "liabilities, not CD276 target biology."
        ),
        "timeline_to_clinic_years": "2.0-4.0",
        "cost_to_ind_usd_m": "10-25",
        "cost_full_development_usd_m": "400-800",
        "evidence_sources": (
            "work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv "
            "(row NCT07189871); work/target-biologist/results/tables/"
            "cd276_known_clinical_drugs.csv; results/tables/"
            "b7h3_modality_precedent_evidence.csv"
        ),
    },
    # ----------------------------- LUAD -----------------------------------
    {
        "indication": "LUAD",
        "rank": 1,
        "modality": "B7-H3 ADC (topoisomerase-I payload preferred)",
        "mechanistic_fit": 5,
        "clinical_precedence_in_indication": 1,
        "feasibility_cmc_manufacturing": 4,
        "differentiation_vs_soc_and_competitor_adcs": 2,
        "risk_profile_5_is_lowest_risk": 2,
        "decision_status": "DEPRIORITIZED - competitive/precedence grounds",
        "recommendation": (
            "DEPRIORITIZED on competitive/precedence grounds (not a scientific "
            "no-go and not a claim that the biology is disqualifying)"
        ),
        "decision_conditions": (
            "Re-evaluate only if (a) a LUAD-specific efficacy/safety readout emerges, "
            "or (b) a differentiated profile is demonstrated (biomarker-defined niche "
            "and a tumour-to-normal-lung protein-density window). LUAD patients are "
            "eligible within nonsquamous-NSCLC B7-H3 ADC trials (NCT07464327 Phase 3; "
            "NCT06780085 Phase 2, I-DXd + TROP2 ADC; NCT07824882 Phase 2), so the "
            "absence of a LUAD-specific trial is not an absence of LUAD evidence."
        ),
        "key_precedent_in_scope": (
            "Zero LUAD-specific B7-H3 trials. Clinical precedence therefore scores "
            "1/5. LUAD is, however, an eligible subset of the nonsquamous-NSCLC "
            "trials: NCT07464327 (HS-20093 + adebrelimab, Phase 3, not yet "
            "recruiting), NCT06780085 (I-DXd + raludotatug deruxtecan, Phase 2, "
            "recruiting) and NCT07824882 (HS-20093 + adebrelimab, Phase 2, not yet "
            "recruiting). NSCLC-context efficacy: enoblituzumab + pembrolizumab ORR "
            "33.3% (5/15; IO-naive) and MGC018 ORR 15% (3/20); neither reports LUAD "
            "separately."
        ),
        "rationale": (
            "ADC is the only B7-H3 modality with a credible clinical path in lung "
            "cancer. LUAD is deprioritized because precedence is indirect and "
            "competition is intense (TROP2/HER3 ADCs, IO/chemotherapy), not because "
            "the biology is disqualifying: the stromal>malignant transcript pattern "
            "is shared with SCLC (LUAD malignant-to-fibroblast 0.31, malignant-to-"
            "macrophage 0.72; SCLC epithelial-to-fibroblast 0.42), and is treated "
            "as a shared antigen-sink caveat. Prior IO/radiation narrow the ILD "
            "margin, but that is a payload/population risk."
        ),
        "target_level_risks": (
            "Broad low-level normal-tissue B7-H3; shared stromal/myeloid antigen "
            "sink (LUAD malignant-to-fibroblast 0.31, malignant-to-macrophage 0.72); "
            "soluble B7-H3 decoy; unquantified surface density and internalization; "
            "normal-lung bulk RNA level 4 (1,683 TPM) with HPA protein level 2 and "
            "low cell-level transcript (13.9 CPM weighted mean)."
        ),
        "payload_level_risks": (
            "ILD/pneumonitis in a population with prior IO pneumonitis/radiation; "
            "myelosuppression; off-tumour payload delivery. These are payload/"
            "population liabilities, not CD276 target biology."
        ),
        "timeline_to_clinic_years": "2.5-4.0",
        "cost_to_ind_usd_m": "15-30",
        "cost_full_development_usd_m": "800-1500",
        "evidence_sources": (
            "work/clinical-trialist/results/reports/b7h3_clinical_landscape.md; "
            "work/single-cell-analyst/results/tables/"
            "cd276_luad_sclc_celltype_expression.csv; results/tables/"
            "cd276_malignant_vs_stromal_ratios.csv; work/fda-safety-officer/"
            "results/reports/b7h3_safety_assessment.md"
        ),
    },
    {
        "indication": "LUAD",
        "rank": 2,
        "modality": "B7-H3 bispecific / T-cell engager",
        "mechanistic_fit": 3,
        "clinical_precedence_in_indication": 1,
        "feasibility_cmc_manufacturing": 4,
        "differentiation_vs_soc_and_competitor_adcs": 2,
        "risk_profile_5_is_lowest_risk": 1,
        "decision_status": "NOT A LEAD - deprioritized",
        "recommendation": "Not a lead - deprioritized (no LUAD-specific precedent)",
        "decision_conditions": (
            "Would require a LUAD-specific signal and a tumour-selective format; "
            "not currently differentiated against non-B7-H3 engagers."
        ),
        "key_precedent_in_scope": (
            "No LUAD-specific B7-H3 TCE. MGD009 (B7-H3xCD3 DART) was Phase 1 in "
            "NSCLC context and terminated for business reasons (NCT02628535); no "
            "LUAD cohort or result was reported."
        ),
        "rationale": (
            "The format is feasible, but LUAD patients often have compromised "
            "pulmonary reserve and prior checkpoint pneumonitis; a TCE against a "
            "broadly expressed lung antigen has no demonstrated density-based "
            "selectivity. The TCE landscape in LUAD is also crowded by non-B7-H3 "
            "engagers."
        ),
        "target_level_risks": (
            "On-target/off-tumour killing in normal lung; shared stromal/myeloid "
            "antigen sink; no demonstrated density-based selectivity."
        ),
        "payload_level_risks": (
            "CRS/ICANS and pulmonary toxicity on a background of lung disease. "
            "Format liability, not CD276 target biology."
        ),
        "timeline_to_clinic_years": "2.0-3.5",
        "cost_to_ind_usd_m": "10-25",
        "cost_full_development_usd_m": "600-1200",
        "evidence_sources": (
            "work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv "
            "(row NCT02628535); work/fda-safety-officer/results/reports/"
            "b7h3_safety_assessment.md"
        ),
    },
    {
        "indication": "LUAD",
        "rank": 3,
        "modality": "B7-H3 CAR-T (autologous; NK-CAR not clinically precedented)",
        "mechanistic_fit": 3,
        "clinical_precedence_in_indication": 1,
        "feasibility_cmc_manufacturing": 2,
        "differentiation_vs_soc_and_competitor_adcs": 2,
        "risk_profile_5_is_lowest_risk": 1,
        "decision_status": "NOT A LEAD - deprioritized",
        "recommendation": "Not a lead - deprioritized (research watch item)",
        "decision_conditions": (
            "Revisit only if the dual EGFR/B7-H3 CAR-T reports LUAD-specific "
            "activity and an acceptable pulmonary safety profile."
        ),
        "key_precedent_in_scope": (
            "No LUAD-specific B7-H3 CAR-T. An EGFR/B7H3 dual CAR-T is early "
            "Phase 1 in lung cancer without a LUAD-specific cohort (NCT05341492). "
            "No B7-H3 NK-CAR trial found."
        ),
        "rationale": (
            "No LUAD-specific efficacy or safety data, autologous manufacturing, and "
            "the same on-target lung liability. A dual-target CAR-T could reduce "
            "antigen escape but not normal-lung toxicity. Ranked above radioligand "
            "only on direct lung-cancer clinical presence and no isotope supply chain."
        ),
        "target_level_risks": (
            "On-target lung toxicity; shared stromal/myeloid antigen sink; antigen "
            "escape; no LUAD-specific expression data."
        ),
        "payload_level_risks": (
            "Manufacturing/logistics; CRS/ICANS; poor solid-tumour trafficking and "
            "persistence. Cell-therapy liabilities, not CD276 target biology."
        ),
        "timeline_to_clinic_years": "2.0-3.0",
        "cost_to_ind_usd_m": "20-40",
        "cost_full_development_usd_m": "800-1500",
        "evidence_sources": (
            "work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv "
            "(row NCT05341492); work/fda-safety-officer/results/reports/"
            "b7h3_safety_assessment.md"
        ),
    },
    {
        "indication": "LUAD",
        "rank": 4,
        "modality": "B7-H3 radioimmunotherapy / radioligand (177Lu or 131I)",
        "mechanistic_fit": 3,
        "clinical_precedence_in_indication": 1,
        "feasibility_cmc_manufacturing": 2,
        "differentiation_vs_soc_and_competitor_adcs": 2,
        "risk_profile_5_is_lowest_risk": 1,
        "decision_status": "NOT A LEAD - deprioritized",
        "recommendation": "Not a lead - deprioritized (research/combination watch)",
        "decision_conditions": (
            "Only with dosimetry showing an acceptable normal-lung window plus a "
            "LUAD-specific cohort or signal."
        ),
        "key_precedent_in_scope": (
            "No LUAD-specific B7-H3 radioligand. 177Lu-BetaBart is Phase 1/2 in "
            "solid tumours with an NSCLC cohort (NCT07189871); LUAD is not reported "
            "separately. 8H9 131I has no systemic lung-cancer record."
        ),
        "rationale": (
            "Crossfire is mechanistically orthogonal, but there is no LUAD-specific "
            "precedence, and normal-lung dose plus isotope logistics are difficult in "
            "a disease with existing pulmonary comorbidity. A research/combination "
            "option, not a lead."
        ),
        "target_level_risks": (
            "On-target absorbed dose to normal lung and myeloid tissue; shared "
            "stromal/myeloid antigen sink; no LUAD-specific data."
        ),
        "payload_level_risks": (
            "Marrow and normal-lung absorbed dose; isotope supply/cold chain; "
            "dosimetry and radiation safety; repeated dosing. Radioligand "
            "liabilities, not CD276 target biology."
        ),
        "timeline_to_clinic_years": "2.0-4.0",
        "cost_to_ind_usd_m": "10-25",
        "cost_full_development_usd_m": "400-800",
        "evidence_sources": (
            "work/clinical-trialist/results/tables/b7h3_luad_sclc_trials.csv "
            "(row NCT07189871); work/target-biologist/results/tables/"
            "cd276_known_clinical_drugs.csv"
        ),
    },
]

rank = pd.DataFrame(ROWS)

# Weighted and equal-weight composites; equal weight is a robustness check.
rank["composite_score"] = sum(
    rank[col] * w for col, w in WEIGHTS.items()
).round(2)
rank["equal_weight_score"] = rank[list(WEIGHTS)].mean(axis=1).round(2)

# Verify the declared rank agrees with the weighted score within indication.
for indication, sub in rank.groupby("indication"):
    ordered = sub.sort_values("composite_score", ascending=False)
    expected = list(range(1, len(ordered) + 1))
    if list(ordered["rank"]) != expected:
        raise ValueError(
            f"Rank/score mismatch for {indication}: "
            f"{list(zip(ordered['modality'], ordered['composite_score']))}"
        )

# Equal-weight rank stability.
stability = []
for indication, sub in rank.groupby("indication"):
    weighted_order = list(sub.sort_values("composite_score", ascending=False)["modality"])
    equal_order = list(sub.sort_values("equal_weight_score", ascending=False)["modality"])
    # CAR-T and radioligand tie in LUAD under equal weights; treat a permutation
    # of tied scores as stable rather than forcing an arbitrary order.
    stable = weighted_order == equal_order
    if not stable and indication == "LUAD":
        w = sub.set_index("modality")["composite_score"]
        e = sub.set_index("modality")["equal_weight_score"]
        stable = abs(e["B7-H3 CAR-T (autologous; NK-CAR not clinically precedented)"]
                     - e["B7-H3 radioimmunotherapy / radioligand (177Lu or 131I)"]) < 0.01
    stability.append({"indication": indication, "rank_stable_under_equal_weights": stable})
rank = rank.merge(pd.DataFrame(stability), on="indication", how="left")

rank["cost_timeline_basis"] = (
    "Indicative prior-knowledge range, not database-derived; excludes "
    "platform/build-out costs and assumes an existing biologics/ADC capability."
)
rank["efficacy_caveat"] = (
    "Clinical precedence is feasibility evidence only. No B7-H3 Phase 3 efficacy "
    "result is posted in LUAD or SCLC as of 2026-10-20. SCLC: ARTEMIS-008 is "
    "completed without posted results; the only posted SCLC-specific result is "
    "MGC018 ORR 0/9 (n=9), a small under-enrolled signal, not class-level failure. "
    "LUAD: no LUAD-specific trial, but LUAD patients are eligible in nonsquamous-"
    "NSCLC trials; a LUAD-specific readout has not been reported."
)
rank["normal_lung_qualification"] = (
    "Bulk lung RNA is HPA level 4 (1,683 TPM) but HPA protein is level 2 and the "
    "Census normal-lung cell-level transcript is comparatively low (13.9 CPM "
    "cell-weighted mean). 'High normal-lung expression' is not supported at "
    "protein or cell-resolved transcript level."
)
rank["stromal_sink_note"] = (
    "Shared across indications: CD276 transcript is higher in fibroblasts than "
    "malignant/epithelial cells in both SCLC (0.42) and LUAD (0.31), and LUAD "
    "macrophage is also higher (0.72). This is an antigen-sink/surface-antigen "
    "caveat for both indications, not a LUAD-specific disqualifier."
)

rank = rank[
    [
        "indication",
        "rank",
        "modality",
        "composite_score",
        "equal_weight_score",
        "rank_stable_under_equal_weights",
        "mechanistic_fit",
        "clinical_precedence_in_indication",
        "feasibility_cmc_manufacturing",
        "differentiation_vs_soc_and_competitor_adcs",
        "risk_profile_5_is_lowest_risk",
        "decision_status",
        "recommendation",
        "decision_conditions",
        "key_precedent_in_scope",
        "rationale",
        "target_level_risks",
        "payload_level_risks",
        "normal_lung_qualification",
        "stromal_sink_note",
        "timeline_to_clinic_years",
        "cost_to_ind_usd_m",
        "cost_full_development_usd_m",
        "cost_timeline_basis",
        "efficacy_caveat",
        "evidence_sources",
    ]
].sort_values(["indication", "rank"])

rank.to_csv(TAB / "b7h3_modality_ranking.csv", index=False)

# ---------------------------------------------------------------------------
# Normal-lung expression qualification
#
# The three measurements are different scales and must not be collapsed into a
# single "high/low" statement:
#   - HPA bulk RNA: 1,682.5 TPM, level 4
#   - HPA protein: ordinal level 2 (reliable)
#   - Census single-cell/nucleus transcript: 13.9 CPM cell-weighted mean
# ---------------------------------------------------------------------------
SUMMARY_PATH = (
    Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
         "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/"
         "target-biologist/results/tables/cd276_tissue_expression_summary.csv")
)
LINEAGE_PATH = (
    Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
         "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/"
         "single-cell-analyst/results/tables/"
         "cd276_normal_tissues_lineage_expression.csv")
)

summary = pd.read_csv(SUMMARY_PATH)
lung_row = summary[
    (summary["row_type"] == "selected_tissue") & (summary["item"] == "lung")
]["value"].iloc[0]
lung_fields = dict(
    field.split("=", 1) for field in str(lung_row).split("; ") if "=" in field
)
bulk_tpm = float(lung_fields["rna_tpm"])
bulk_level = int(lung_fields["level_bin"])
protein_level = int(lung_fields["protein_level"])
protein_reliable = lung_fields["protein_reliable"]

lineage = pd.read_csv(LINEAGE_PATH)
lung = lineage[lineage["organ"] == "lung"].copy()
lung_cpm = round(
    float((lung["n_cells"] * lung["mean_cpm_weighted"]).sum()
          / lung["n_cells"].sum()),
    2,
)
lung_cells = int(lung["n_cells"].sum())
lung_donors = int(lung["n_donors"].max())

qualification = pd.DataFrame(
    [
        {
            "assay_scale": "bulk RNA (HPA)",
            "tissue": "lung",
            "metric": "TPM",
            "value": bulk_tpm,
            "hpa_level": bulk_level,
            "n_cells": "",
            "n_donors": "",
            "source": str(SUMMARY_PATH.relative_to(RUN.parent.parent)),
            "interpretation": "HPA RNA level 4 (high bulk transcript).",
        },
        {
            "assay_scale": "bulk protein (HPA)",
            "tissue": "lung",
            "metric": "ordinal IHC level",
            "value": protein_level,
            "hpa_level": protein_level,
            "n_cells": "",
            "n_donors": "",
            "source": str(SUMMARY_PATH.relative_to(RUN.parent.parent)),
            "interpretation": (
                f"HPA protein level {protein_level} (reliable={protein_reliable}); "
                "does not support a 'high normal-lung protein' claim."
            ),
        },
        {
            "assay_scale": "single-cell transcript (CELLxGENE Census)",
            "tissue": "lung",
            "metric": "CPM, cell-weighted mean",
            "value": lung_cpm,
            "hpa_level": "",
            "n_cells": lung_cells,
            "n_donors": lung_donors,
            "source": str(LINEAGE_PATH.relative_to(RUN.parent.parent)),
            "interpretation": (
                "Comparatively low cell-level transcript. The bulk RNA level 4 is "
                "not reproduced at cell resolution; myeloid/stromal cells carry "
                "most of the signal."
            ),
        },
        {
            "assay_scale": "single-cell transcript (CELLxGENE Census)",
            "tissue": "lung",
            "metric": "CPM, highest lineage (macrophage)",
            "value": round(float(lung.loc[lung["lineage"] == "Macrophage",
                                          "mean_cpm_weighted"].iloc[0]), 2),
            "hpa_level": "",
            "n_cells": int(lung.loc[lung["lineage"] == "Macrophage",
                                      "n_cells"].iloc[0]),
            "n_donors": int(lung.loc[lung["lineage"] == "Macrophage",
                                       "n_donors"].iloc[0]),
            "source": str(LINEAGE_PATH.relative_to(RUN.parent.parent)),
            "interpretation": "Lung macrophages are the dominant cell-level source.",
        },
        {
            "assay_scale": "single-cell transcript (CELLxGENE Census)",
            "tissue": "lung",
            "metric": "CPM, lung epithelial",
            "value": round(float(lung.loc[lung["lineage"] == "Epithelial",
                                          "mean_cpm_weighted"].iloc[0]), 2),
            "hpa_level": "",
            "n_cells": int(lung.loc[lung["lineage"] == "Epithelial",
                                      "n_cells"].iloc[0]),
            "n_donors": int(lung.loc[lung["lineage"] == "Epithelial",
                                       "n_donors"].iloc[0]),
            "source": str(LINEAGE_PATH.relative_to(RUN.parent.parent)),
            "interpretation": "Lung epithelial transcript is low and near the overall mean.",
        },
    ]
)
qualification.to_csv(TAB / "cd276_normal_lung_expression_qualification.csv", index=False)

# ---------------------------------------------------------------------------
# Target-level vs payload-level risk attribution
# ---------------------------------------------------------------------------
risk_attribution = pd.DataFrame(
    [
        {
            "risk_id": "T1",
            "level": "target-level",
            "risk": "Broad low-level normal-tissue expression",
            "description": "CD276 detected in 109/120 normal entries; 80/120 at HPA level >=3; highest in alternatively activated macrophages (14,497 TPM).",
            "modalities_affected": "ADC; TCE; CAR-T; radioligand",
            "evidence_source": "work/target-biologist/results/tables/cd276_tissue_expression_summary.csv",
            "mitigation": "Quantitative tumour-to-normal surface-density package; tumour-selective linker/format.",
            "attribution_note": "Target biology. Applies to every cytotoxic B7-H3 modality.",
        },
        {
            "risk_id": "T2",
            "level": "target-level",
            "risk": "Normal-lung expression",
            "description": "Bulk lung RNA level 4 (1,683 TPM), but HPA protein level 2 and Census cell-level transcript 13.9 CPM weighted mean.",
            "modalities_affected": "ADC; TCE; CAR-T; radioligand",
            "evidence_source": "results/tables/cd276_normal_lung_expression_qualification.csv",
            "mitigation": "Measure surface protein density and tumour-to-normal-lung ratio; do not rely on bulk RNA.",
            "attribution_note": "Target biology; magnitude is not established at protein level.",
        },
        {
            "risk_id": "T3",
            "level": "target-level",
            "risk": "Stromal/myeloid antigen sink",
            "description": "Fibroblast > malignant/epithelial transcript in both SCLC (0.42) and LUAD (0.31); LUAD macrophage also higher (0.72).",
            "modalities_affected": "ADC; TCE; CAR-T; radioligand",
            "evidence_source": "results/tables/cd276_malignant_vs_stromal_ratios.csv",
            "mitigation": "Tumour-selective format; payload with favourable bystander profile; measure malignant-cell surface density.",
            "attribution_note": "Shared across SCLC and LUAD; not a LUAD-specific disqualifier.",
        },
        {
            "risk_id": "T4",
            "level": "target-level",
            "risk": "Soluble B7-H3 decoy/sink",
            "description": "Ectodomain shedding is prior knowledge; shedding rate and plasma sB7-H3 are not retrievable.",
            "modalities_affected": "ADC; TCE; naked antibody",
            "evidence_source": "work/target-biologist/results/reports/cd276_modality_biology.md (prior knowledge, labelled)",
            "mitigation": "Measure sB7-H3 and free-drug exposure; consider dose escalation to saturate sink.",
            "attribution_note": "Target biology; not established in these databases.",
        },
        {
            "risk_id": "T5",
            "level": "target-level",
            "risk": "Unquantified surface density, internalization and isoform mix",
            "description": "No molecules-per-cell, internalization rate or 2Ig/4Ig isoform-resolved data.",
            "modalities_affected": "ADC; TCE; CAR-T; radioligand",
            "evidence_source": "work/target-biologist/results/reports/cd276_modality_biology.md",
            "mitigation": "Paired density/internalization study in patient tumours and matched normal lung.",
            "attribution_note": "Target biology; decisive evidence gap for all formats.",
        },
        {
            "risk_id": "P1",
            "level": "payload-level",
            "risk": "ILD/pneumonitis",
            "description": "DXd-class and other topoisomerase-I ADC class liability; background of prior IO/radiation in lung cancer.",
            "modalities_affected": "ADC",
            "evidence_source": "work/fda-safety-officer/results/reports/b7h3_safety_assessment.md",
            "mitigation": "Payload/linker choice (e.g. lower-ILD payload), dose/schedule, patient selection.",
            "attribution_note": "Payload/format liability; must not be attributed to CD276 target biology.",
        },
        {
            "risk_id": "P2",
            "level": "payload-level",
            "risk": "Myelosuppression",
            "description": "Class liability of cytotoxic ADC payloads (topoisomerase-I and duocarmycin).",
            "modalities_affected": "ADC",
            "evidence_source": "work/fda-safety-officer/results/reports/b7h3_safety_assessment.md",
            "mitigation": "Payload/DAR optimisation; growth-factor support; dose schedule.",
            "attribution_note": "Payload liability; not target biology.",
        },
        {
            "risk_id": "P3",
            "level": "payload-level",
            "risk": "CRS/ICANS",
            "description": "Intrinsic to T-cell-redirecting formats.",
            "modalities_affected": "TCE; CAR-T",
            "evidence_source": "work/fda-safety-officer/results/reports/b7h3_safety_assessment.md",
            "mitigation": "Step-up dosing, affinity tuning, masking, steroid prophylaxis.",
            "attribution_note": "Format liability; not target biology.",
        },
        {
            "risk_id": "P4",
            "level": "payload-level",
            "risk": "Normal-organ absorbed dose / isotope logistics",
            "description": "Marrow, lung and kidney dose; isotope supply and cold chain.",
            "modalities_affected": "Radioligand / RIT",
            "evidence_source": "work/fda-safety-officer/results/reports/b7h3_safety_assessment.md",
            "mitigation": "Dosimetry-guided dosing; thermostic patient selection.",
            "attribution_note": "Radioligand liability; not target biology.",
        },
        {
            "risk_id": "P5",
            "level": "payload-level",
            "risk": "Autologous manufacturing / lymphodepletion",
            "description": "Vein-to-vein logistics, cost and tolerability in heavily pretreated patients.",
            "modalities_affected": "CAR-T",
            "evidence_source": "work/fda-safety-officer/results/reports/b7h3_safety_assessment.md",
            "mitigation": "Allogeneic/NK-CAR platforms; faster manufacturing.",
            "attribution_note": "Cell-therapy liability; not target biology.",
        },
        {
            "risk_id": "G1",
            "level": "programme-level",
            "risk": "No posted Phase 3 efficacy",
            "description": "ARTEMIS-008 completed without results; only posted SCLC-specific result is MGC018 ORR 0/9 (n=9).",
            "modalities_affected": "All",
            "evidence_source": "work/clinical-trialist/results/reports/b7h3_clinical_landscape.md",
            "mitigation": "Stage the SCLC GO on a class-level Phase 3 readout; do not treat trial existence as efficacy.",
            "attribution_note": "Programme/clinical evidence gap, not a target or payload toxicity.",
        },
    ]
)
risk_attribution.to_csv(TAB / "b7h3_target_vs_payload_risk_attribution.csv", index=False)

# ---------------------------------------------------------------------------
# Precedent evidence table
# ---------------------------------------------------------------------------
PRECEDENT = [
    {
        "modality_class": "B7-H3 ADC",
        "program_or_agent": "Ifinatamab deruxtecan (I-DXd; DS-7300)",
        "target": "CD276",
        "indication_scope": "SCLC",
        "max_phase": "Phase 3",
        "status": "Recruiting",
        "trial_or_record": "NCT06203210; also NCT05280470 (Phase 2), NCT06362252 (1L combo), NCT07535359 (expanded access)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table; not in CD276 drug MCP",
        "result_or_note": "6 Phase 3 B7-H3 ADC trials contribute SCLC; no Phase 3 results posted. Drug MCP contains no I-DXd record (coverage gap).",
    },
    {
        "modality_class": "B7-H3 ADC",
        "program_or_agent": "HS-20093 / risvutatug rezetecan (GSK5764227)",
        "target": "CD276",
        "indication_scope": "SCLC",
        "max_phase": "Phase 3",
        "status": "Completed (ARTEMIS-008); Recruiting (EMBOLD SCLC-301)",
        "trial_or_record": "NCT06498479 (ARTEMIS-008, vs topotecan, n=461); NCT07099898 (EMBOLD SCLC-301); NCT06526624 (limited-stage); NCT06052423 (withdrawn)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table; not in CD276 drug MCP",
        "result_or_note": "ARTEMIS-008 is COMPLETED with no results module posted as of 2026-10-20. Trial existence is not efficacy.",
    },
    {
        "modality_class": "B7-H3 ADC",
        "program_or_agent": "MHB088C",
        "target": "CD276",
        "indication_scope": "SCLC",
        "max_phase": "Phase 3",
        "status": "Recruiting",
        "trial_or_record": "NCT06954246 (vs physician's choice, n=450); NCT05652855/NCT07102004 (earlier-phase)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table; not in CD276 drug MCP",
        "result_or_note": "Phase 3 OS endpoint; no results posted.",
    },
    {
        "modality_class": "B7-H3 ADC",
        "program_or_agent": "YL201",
        "target": "CD276",
        "indication_scope": "SCLC",
        "max_phase": "Phase 3",
        "status": "Active, not recruiting",
        "trial_or_record": "NCT06612151 (TAISHAN-302, vs topotecan, n=438); NCT06394414 (Phase 1)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table; not in CD276 drug MCP",
        "result_or_note": "Phase 3 OS endpoint; no results posted.",
    },
    {
        "modality_class": "B7-H3 ADC",
        "program_or_agent": "MGC018 / vobramitamab duocarmazine",
        "target": "CD276",
        "indication_scope": "SCLC",
        "max_phase": "Phase 2",
        "status": "Active, not recruiting",
        "trial_or_record": "NCT06227546 (n=9); NCT05551117 (Part 2 SCLC-eligible mixed cohort, n=4)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table; not in CD276 drug MCP",
        "result_or_note": "Only posted SCLC-specific result: ORR 0/9 (0%). SAEs >=5%: atrial fibrillation 3/9, lung infection 1/9, sepsis 1/9, respiratory failure 1/9. Small, under-enrolled; not class-level failure.",
    },
    {
        "modality_class": "B7-H3 ADC",
        "program_or_agent": "HS-20093 + adebrelimab",
        "target": "CD276",
        "indication_scope": "NSCLC, nonsquamous (LUAD-eligible, not LUAD-specific)",
        "max_phase": "Phase 3",
        "status": "Not yet recruiting (Phase 3); recruiting (NCT06780085 Phase 2)",
        "trial_or_record": "NCT07464327 (Phase 3); NCT07824882 (Phase 2); NCT06780085 (I-DXd + raludotatug deruxtecan, Phase 2, recruiting)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table",
        "result_or_note": "LUAD patients are an eligible subset of these nonsquamous-NSCLC trials; no LUAD-specific cohort or result is reported. This contradicts 'no LUAD evidence' but does not establish LUAD-specific efficacy.",
    },
    {
        "modality_class": "B7-H3 bispecific / T-cell engager",
        "program_or_agent": "MGD009 / orlotamab (B7-H3xCD3 DART)",
        "target": "CD276 x CD3",
        "indication_scope": "NSCLC context (not LUAD/SCLC-specific)",
        "max_phase": "Phase 1",
        "status": "Terminated (business decision, not safety)",
        "trial_or_record": "NCT02628535 (n=67)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table",
        "result_or_note": "No SCLC or LUAD B7-H3 TCE trial; no efficacy result reported in the registry.",
    },
    {
        "modality_class": "B7-H3 antibody-cytokine fusion",
        "program_or_agent": "IBB0979 (B7-H3xIL-10R)",
        "target": "CD276 x IL10R",
        "indication_scope": "SCLC",
        "max_phase": "Phase 2 (trial titled II/III)",
        "status": "Not yet recruiting",
        "trial_or_record": "NCT07076095 (with topotecan, n=200)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table",
        "result_or_note": "Not a T-cell engager; immune-cytokine mechanism. Included to avoid conflating it with TCE precedent.",
    },
    {
        "modality_class": "B7-H3 CAR-T",
        "program_or_agent": "Autologous B7-H3 CAR-T",
        "target": "CD276",
        "indication_scope": "SCLC (ES-SCLC or extrapulmonary NEC)",
        "max_phase": "Phase 1",
        "status": "Recruiting (start 2026-10-25)",
        "trial_or_record": "NCT07509034 (n=40; MTD/MAD and DCR)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table",
        "result_or_note": "Single Phase 1; no results. Establishes clinical feasibility only.",
    },
    {
        "modality_class": "B7-H3 CAR-T",
        "program_or_agent": "EGFR/B7H3 dual CAR-T",
        "target": "EGFR x CD276",
        "indication_scope": "Lung cancer (histology not specified)",
        "max_phase": "Early Phase 1",
        "status": "Recruiting",
        "trial_or_record": "NCT05341492 (n=30)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table",
        "result_or_note": "Not LUAD-specific; no results.",
    },
    {
        "modality_class": "B7-H3 NK-CAR",
        "program_or_agent": "None identified",
        "target": "CD276",
        "indication_scope": "LUAD/SCLC",
        "max_phase": "Not applicable",
        "status": "Not applicable",
        "trial_or_record": "No matching registry record in the curated trial table",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table",
        "result_or_note": "No B7-H3 NK-CAR clinical programme found. Allogeneic NK-CAR remains preclinical for this target.",
    },
    {
        "modality_class": "B7-H3 radioligand / radioimmunotherapy",
        "program_or_agent": "177Lu-BetaBart",
        "target": "CD276",
        "indication_scope": "Solid tumours including SCLC",
        "max_phase": "Phase 1/2",
        "status": "Recruiting",
        "trial_or_record": "NCT07189871 (n=61)",
        "evidence_source": "ClinicalTrials.gov via clinical-trialist registry table",
        "result_or_note": "SCLC cohort size and results not reported. No LUAD-specific cohort.",
    },
    {
        "modality_class": "B7-H3 radioimmunotherapy",
        "program_or_agent": "8H9 131I / omburtamab",
        "target": "CD276",
        "indication_scope": "Leptomeningeal metastasis, neuroblastoma, peritoneal cancer, DIPG",
        "max_phase": "Phase 2",
        "status": "Terminated/withdrawn",
        "trial_or_record": "NCT03275402; NCT01099644; NCT05063357",
        "evidence_source": "Drug MCP: search_known_drugs(CD276); CHEMBL2109310; get_drug_indications",
        "result_or_note": "4 indications, no lung-cancer record. Compartmental/intrathecal or intraperitoneal delivery; not a systemic lung-cancer precedent.",
    },
    {
        "modality_class": "B7-H3 naked antibody",
        "program_or_agent": "Enoblituzumab (MGA271)",
        "target": "CD276",
        "indication_scope": "HNSCC, prostate cancer, melanoma",
        "max_phase": "Phase 2",
        "status": "Withdrawn / Recruiting / Terminated",
        "trial_or_record": "NCT04129320; NCT06014255; NCT02923180; NCT01918930",
        "evidence_source": "Drug MCP: search_known_drugs(CD276); CHEMBL3545373; get_drug_indications",
        "result_or_note": "No lung-cancer indication in the drug MCP. Mechanism is CD276 antigen cross-linking; no intrinsic dependency rationale. Not ranked.",
    },
    {
        "modality_class": "B7-H3 small molecule",
        "program_or_agent": "None identified",
        "target": "CD276",
        "indication_scope": "LUAD/SCLC",
        "max_phase": "Not applicable",
        "status": "Not tractable",
        "trial_or_record": "Open Targets tractability; chemical probes",
        "evidence_source": "Target MCP: get_target_tractability; get_chemical_probes",
        "result_or_note": "All small-molecule criteria false; 0 chemical probes (0 high-quality). Not viable.",
    },
    {
        "modality_class": "B7-H3 PROTAC/degrader",
        "program_or_agent": "None identified",
        "target": "CD276",
        "indication_scope": "LUAD/SCLC",
        "max_phase": "Not applicable",
        "status": "Not tractable",
        "trial_or_record": "Open Targets tractability",
        "evidence_source": "Target MCP: get_target_tractability",
        "result_or_note": "No small-molecule binder, no UniProt ubiquitination; the generic database-ubiquitination/half-life flags do not enable degradation. Not viable.",
    },
    {
        "modality_class": "Competitor ADC target (DLL3)",
        "program_or_agent": "Rovalpituzumab tesirine",
        "target": "DLL3",
        "indication_scope": "SCLC",
        "max_phase": "Phase 3",
        "status": "Completed / Withdrawn / Terminated",
        "trial_or_record": "NCT03061812; NCT03334487; NCT03033511; NCT02674568",
        "evidence_source": "Drug MCP: search_known_drugs(DLL3, SCLC, min_phase=0)",
        "result_or_note": "6 DLL3 SCLC records, all rovalpituzumab tesirine (ADC). DLL3 is a competing SCLC target; rovalpituzumab's Phase 3 history is a caution on ADC translation. Tarlatamab (DLL3xCD3) is prior knowledge, not in this MCP result.",
    },
    {
        "modality_class": "Competitor ADC target (TROP2)",
        "program_or_agent": "Sacituzumab govitecan",
        "target": "TACSTD2",
        "indication_scope": "SCLC",
        "max_phase": "Phase 1",
        "status": "Suspended",
        "trial_or_record": "NCT04826341",
        "evidence_source": "Drug MCP: search_known_drugs(TACSTD2, SCLC, min_phase=0)",
        "result_or_note": "1 TROP2 SCLC record. TROP2 is a competing ADC target with less SCLC Phase 3 momentum than B7-H3.",
    },
    {
        "modality_class": "Competitor ADC target (TROP2)",
        "program_or_agent": "No TROP2 LUAD record in this MCP",
        "target": "TACSTD2",
        "indication_scope": "LUAD",
        "max_phase": "Not retrieved",
        "status": "Coverage gap",
        "trial_or_record": "search_known_drugs(TACSTD2, EFO_0000571) = 0",
        "evidence_source": "Drug MCP",
        "result_or_note": "Zero matches is a database-coverage statement, not evidence of no TROP2 LUAD programme. Datopotamab deruxtecan is prior knowledge and was not used as MCP evidence.",
    },
    {
        "modality_class": "Competitor ADC target (SEZ6)",
        "program_or_agent": "No SEZ6 SCLC record in this MCP",
        "target": "SEZ6",
        "indication_scope": "SCLC",
        "max_phase": "Not retrieved",
        "status": "Coverage gap",
        "trial_or_record": "search_known_drugs(SEZ6, EFO_0000702) = 0",
        "evidence_source": "Drug MCP",
        "result_or_note": "Zero matches is a coverage gap; ABBV-706 is prior knowledge, not MCP evidence.",
    },
]
precedent = pd.DataFrame(PRECEDENT)
precedent.to_csv(TAB / "b7h3_modality_precedent_evidence.csv", index=False)

# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
short_names = {
    "B7-H3 ADC (topoisomerase-I payload preferred)": "B7-H3 ADC",
    "B7-H3 bispecific / T-cell engager": "Bispecific / TCE",
    "B7-H3 CAR-T (autologous; NK-CAR not clinically precedented)": "CAR-T",
    "B7-H3 radioimmunotherapy / radioligand (177Lu or 131I)": "Radioligand / RIT",
}
rank["short_modality"] = rank["modality"].map(short_names)
colors = {
    "B7-H3 ADC": "#1b7837",
    "Bispecific / TCE": "#762a83",
    "CAR-T": "#d95f02",
    "Radioligand / RIT": "#1f78b4",
}

fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), sharex=True)
for ax, indication in zip(axes, ["LUAD", "SCLC"]):
    sub = rank[rank["indication"] == indication].sort_values(
        "composite_score", ascending=True
    )
    y = np.arange(len(sub))
    ax.barh(
        y,
        sub["composite_score"],
        color=[colors[m] for m in sub["short_modality"]],
        edgecolor="black",
        linewidth=0.4,
    )
    ax.set_yticks(y)
    ax.set_yticklabels(sub["short_modality"], fontsize=9)
    ax.set_xlim(0, 5)
    ax.set_xlabel("Weighted composite score (0-5)")
    ax.set_title(f"{indication}", fontsize=12, fontweight="bold")
    ax.grid(axis="x", alpha=0.25)
    for yi, (_, row) in enumerate(sub.iterrows()):
        ax.text(
            row["composite_score"] + 0.06,
            yi,
            f"{row['composite_score']:.2f}  (rank {row['rank']})",
            va="center",
            fontsize=8.5,
        )
fig.suptitle(
    "B7-H3 modality ranking: SCLC ADC is a staged GO; LUAD is deprioritized "
    "(not a scientific no-go)",
    fontsize=12.5,
)
fig.tight_layout()
fig.savefig(FIG / "b7h3_modality_composite_scores.png", dpi=300, bbox_inches="tight")
fig.savefig(FIG / "b7h3_modality_composite_scores.pdf", bbox_inches="tight")
plt.close(fig)

# Heatmap of the five dimensions.
dims = list(WEIGHTS.keys())
dim_labels = [
    "Mechanistic\nfit",
    "Clinical\nprecedence",
    "Feasibility\n(CMC)",
    "Differentiation\nvs SOC/ADCs",
    "Risk\n(5=low)",
]
fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.0))
fig.subplots_adjust(wspace=0.62)
for ax, indication in zip(axes, ["LUAD", "SCLC"]):
    sub = rank[rank["indication"] == indication].sort_values("rank")
    mat = sub[dims].to_numpy()
    im = ax.imshow(mat, cmap="RdYlGn", vmin=1, vmax=5, aspect="auto")
    ax.set_xticks(np.arange(len(dims)))
    ax.set_xticklabels(dim_labels, fontsize=8)
    ax.set_yticks(np.arange(len(sub)))
    ax.set_yticklabels(
        [f"{r}. {m}" for r, m in zip(sub["rank"], sub["short_modality"])], fontsize=9
    )
    ax.set_title(f"{indication}", fontsize=12, fontweight="bold")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(
                j,
                i,
                str(int(mat[i, j])),
                ha="center",
                va="center",
                fontsize=10,
                color="black",
            )
fig.colorbar(im, ax=axes, fraction=0.025, pad=0.04, label="Score (1-5)")
fig.suptitle("B7-H3 modality scores by dimension", fontsize=12.5, y=1.02)
fig.savefig(FIG / "b7h3_modality_dimension_heatmap.png", dpi=300, bbox_inches="tight")
fig.savefig(FIG / "b7h3_modality_dimension_heatmap.pdf", bbox_inches="tight")
plt.close(fig)

print("Wrote:")
print(TAB / "b7h3_modality_ranking.csv")
print(TAB / "b7h3_modality_precedent_evidence.csv")
print(TAB / "cd276_normal_lung_expression_qualification.csv")
print(TAB / "b7h3_target_vs_payload_risk_attribution.csv")
print(FIG / "b7h3_modality_composite_scores.png")
print(FIG / "b7h3_modality_dimension_heatmap.png")
print("\nRanking:")
print(
    rank[
        [
            "indication",
            "rank",
            "modality",
            "composite_score",
            "equal_weight_score",
            "decision_status",
        ]
    ].to_string(index=False)
)
print("\nNormal-lung cell-weighted CPM:", lung_cpm)
