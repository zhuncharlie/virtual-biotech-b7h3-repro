#!/usr/bin/env python3
"""Build the curated B7-H3 (CD276) LUAD/SCLC clinical-trial table.

Registry metadata come from the saved ClinicalTrials.gov API v2 search
records in data/raw/ (fetched through the configured clinicaltrials MCP
server's own functions). Curated fields (scope, line of therapy, agent
modality, target-linkage evidence, posted-results summary) are encoded
below and reviewed against the registry text.

Outputs:
  results/tables/b7h3_luad_sclc_trials.csv      final curated table
  data/processed/b7h3_trial_selection_audit.csv  same table + query provenance
  results/tables/b7h3_posted_results_extract.csv verified posted results only
"""
import json
import glob
from pathlib import Path

import pandas as pd

RUN = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
           "20261020-085513-evaluate-the-therapeutic-candida-a03f0a23/work/clinical-trialist")
RAW = RUN / "data" / "raw"
PROC = RUN / "data" / "processed"
TAB = RUN / "results" / "tables"
TAB.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- selection
# Each row: nct, scope, indication, histology_notes, agent, modality,
# line_of_therapy, target_linkage_evidence, linkage_confidence,
# posted_results_summary (only for hasResults trials; "" otherwise)
ROWS = [
    # ---------------- SCLC-specific interventional ----------------
    dict(nct="NCT05280470", scope="SCLC-specific", indication="SCLC (extensive-stage)",
         histology="ES-SCLC; pretreated; no LUAD cohort",
         agent="Ifinatamab deruxtecan (I-DXd)", modality="B7-H3 ADC (DXd payload)",
         line="2L+ (>=1 prior platinum; >=2 prior lines from protocol v3.0)",
         linkage="Registry description: I-DXd is an anti-B7-H3 ADC", conf="high",
         posted=""),
    dict(nct="NCT06203210", scope="SCLC-specific", indication="SCLC (relapsed)",
         histology="ES-SCLC; exactly one prior platinum line",
         agent="Ifinatamab deruxtecan (I-DXd)", modality="B7-H3 ADC (DXd payload)",
         line="2L (one prior platinum line; CTFI >=30 days)",
         linkage="Registry description: I-DXd is an anti-B7-H3 ADC", conf="high",
         posted=""),
    dict(nct="NCT06362252", scope="SCLC-specific", indication="SCLC (extensive-stage, 1L)",
         histology="ES-SCLC; first-line induction/maintenance",
         agent="I-DXd + atezolizumab +/- carboplatin", modality="B7-H3 ADC + anti-PD-L1 +/- platinum",
         line="1L",
         linkage="Registry description: I-DXd is an anti-B7-H3 ADC", conf="high",
         posted=""),
    dict(nct="NCT06780137", scope="SCLC-specific", indication="SCLC (extensive-stage, R/R)",
         histology="ES-SCLC; relapsed/refractory",
         agent="Gocatamig + I-DXd +/- durvalumab", modality="DLL3xCD3 T-cell engager + B7-H3 ADC",
         line="2L+ (>=1 prior platinum line)",
         linkage="B7-H3-directed component is I-DXd (registry keyword/description)", conf="high",
         posted=""),
    dict(nct="NCT07227597", scope="SCLC-specific", indication="SCLC (extensive-stage)",
         histology="ES-SCLC; induction and maintenance cohorts",
         agent="Gocatamig + I-DXd + atezolizumab/carboplatin/etoposide",
         modality="DLL3xCD3 T-cell engager + B7-H3 ADC + anti-PD-L1/platinum",
         line="1L/maintenance (mixed)",
         linkage="B7-H3-directed component is I-DXd (registry keyword/description)", conf="high",
         posted=""),
    dict(nct="NCT06227546", scope="SCLC-specific", indication="SCLC (extensive-stage, R/R)",
         histology="ES-SCLC; relapsed/refractory; n=9 actual",
         agent="MGC018 (vobramitamab duocarmazine)", modality="B7-H3 ADC (duocarmycin payload)",
         line="2L+ (progression on/following platinum; any number of prior regimens)",
         linkage="Registry intervention description: anti-B7-H3 antibody drug conjugate", conf="high",
         posted=("ORR 0/9 (0%; primary endpoint POSTED). SAEs (>=5% threshold): atrial fibrillation "
                 "3/9, lung infection 1/9, sepsis 1/9, respiratory failure 1/9, creatinine increased "
                 "1/9, rash maculo-papular 1/9, hypotension 1/9. Study active, not recruiting; "
                 "registry gives no reason for stopping enrollment at 9.")),
    dict(nct="NCT06052423", scope="SCLC-specific", indication="SCLC (extensive-stage)",
         histology="ES-SCLC; withdrawn before enrollment (n=0)",
         agent="HS-20093", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="Not specified (withdrawn)",
         linkage="Agent identity: HS-20093 is a B7-H3 ADC; registry describes B7-H3 expression analyses", conf="high",
         posted=""),
    dict(nct="NCT06498479", scope="SCLC-specific", indication="SCLC (relapsed)",
         histology="SCLC; phase 3 vs topotecan (ARTEMIS-008)",
         agent="HS-20093 (risvutatug rezetecan)", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="2L (relapsed after 1L platinum)",
         linkage="Agent identity: HS-20093 is a B7-H3 ADC; registry describes B7-H3 expression analyses", conf="high",
         posted="NO RESULTS POSTED despite COMPLETED status (registry as of 2026-10-20)"),
    dict(nct="NCT06526624", scope="SCLC-specific", indication="SCLC (limited-stage)",
         histology="Limited-stage SCLC; phase 3 vs active surveillance",
         agent="HS-20093 (risvutatug rezetecan)", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="Consolidation/maintenance after definitive chemoradiotherapy",
         linkage="Agent identity: HS-20093 is a B7-H3 ADC; registry describes B7-H3 expression analyses", conf="high",
         posted=""),
    dict(nct="NCT07063407", scope="SCLC-specific", indication="SCLC (extensive-stage)",
         histology="ES-SCLC; combination after 1L induction",
         agent="HS-20093 + adebrelimab", modality="B7-H3 ADC + anti-PD-L1",
         line="1L maintenance after platinum/etoposide/PD-(L)1 induction",
         linkage="Agent identity: HS-20093 is a B7-H3 ADC; registry describes B7-H3 expression analyses", conf="high",
         posted=""),
    dict(nct="NCT07099898", scope="SCLC-specific", indication="SCLC (relapsed)",
         histology="SCLC; phase 3 vs topotecan (EMBOLD SCLC-301)",
         agent="Risvutatug rezetecan (GSK5764227; HS-20093)", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="2L (1 prior platinum + PD-(L)1)",
         linkage="Agent identity: GSK5764227/HS-20093 is a B7-H3 ADC; registry excludes prior B7-H3 therapy", conf="high",
         posted=""),
    dict(nct="NCT06954246", scope="SCLC-specific", indication="SCLC (extensive-stage, relapsed)",
         histology="ES-SCLC; phase 3 vs physician's choice",
         agent="MHB088C", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="2L (after platinum + PD-1/L1; <=2 prior lines)",
         linkage="Registry keyword: B7H3; intervention is an ADC", conf="high",
         posted=""),
    dict(nct="NCT07076095", scope="SCLC-specific", indication="SCLC (relapsed)",
         histology="SCLC (limited or extensive); phase 2/3 vs topotecan",
         agent="IBB0979 + topotecan", modality="B7-H3xIL-10R antibody-cytokine fusion + topoisomerase-I",
         line="2L/3L (after 1L or 2L systemic therapy)",
         linkage="Registry intervention description: bifunctional antibody-cytokine fusion targeting B7-H3 and IL-10R", conf="high",
         posted=""),
    dict(nct="NCT06612151", scope="SCLC-specific", indication="SCLC (relapsed)",
         histology="SCLC; phase 3 vs topotecan (TAISHAN-302)",
         agent="YL201", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="2L+ (progression on/after 1L platinum)",
         linkage="Agent identity: YL201 is a B7-H3 ADC; registry requires tumour B7-H3 expression testing and excludes prior B7-H3 therapy", conf="high",
         posted=""),
    dict(nct="NCT07509034", scope="SCLC-specific", indication="SCLC (extensive-stage, pretreated)",
         histology="ES-SCLC or extrapulmonary NEC; pretreated",
         agent="Autologous B7-H3 CAR-T", modality="B7-H3 CAR-T",
         line="2L+ (recurred/refractory after 1L)",
         linkage="Registry title/intervention: autologous B7-H3 CAR T cells", conf="high",
         posted=""),
    dict(nct="NCT04471727", scope="SCLC-specific", indication="SCLC / neuroendocrine carcinoma",
         histology="SCLC and NEC; includes I-DXd combination arm",
         agent="Gocatamig + atezolizumab + I-DXd", modality="DLL3xCD3 T-cell engager + anti-PD-L1 + B7-H3 ADC",
         line="2L+ (R/R after >=1 prior platinum line)",
         linkage="B7-H3-directed component is I-DXd (registry keyword/description)", conf="high",
         posted=""),
    # ---------------- SCLC expanded access ----------------
    dict(nct="NCT07535359", scope="SCLC expanded access", indication="SCLC (extensive-stage, 3L+)",
         histology="ES-SCLC; medical access program, not an interventional trial",
         agent="Ifinatamab deruxtecan (I-DXd)", modality="B7-H3 ADC (DXd payload)",
         line="3L+",
         linkage="Registry description: I-DXd is an anti-B7-H3 ADC", conf="high",
         posted=""),
    # ---------------- Pan-tumor with explicit SCLC cohort ----------------
    dict(nct="NCT03595059", scope="SCLC cohort (pan-tumor)", indication="SCLC cohort within solid tumors",
         histology="Part 2a SCLC expansion; Part 2b NSCLC/breast; SCLC cohort size not reported",
         agent="ABBV-155", modality="B7-H3 ADC (prior knowledge; target not stated in registry)",
         line="2L+ (relapsed/refractory after >=1 prior systemic chemotherapy)",
         linkage="Agent identity (prior knowledge): ABBV-155 is a B7-H3 ADC; registry silent on target", conf="moderate",
         posted=""),
    dict(nct="NCT05914116", scope="SCLC cohort (pan-tumor)", indication="SCLC cohort (Phase 2a Cohort 1)",
         histology="Advanced solid tumors; Phase 2a Cohort 1 is SCLC",
         agent="DB-1311/BNT324", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="2L+ (prior platinum for extensive-stage SCLC)",
         linkage="Registry keyword: B7-H3; DB-1311 is a B7-H3 ADC", conf="high",
         posted=""),
    dict(nct="NCT06242470", scope="SCLC cohort (pan-tumor)", indication="SCLC cohort within solid tumors",
         histology="Advanced solid tumors incl. SCLC; cohort size not reported",
         agent="MGC026", modality="B7-H3 ADC (prior knowledge; target not stated in registry)",
         line="Advanced/refractory; line not specified",
         linkage="Agent identity (prior knowledge): MGC026 is a B7-H3 ADC; registry silent on target", conf="moderate",
         posted=""),
    dict(nct="NCT06394414", scope="SCLC cohort (pan-tumor)", indication="SCLC cohort within solid tumors",
         histology="Advanced solid tumors; SCLC dose-expansion cohort",
         agent="YL201", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="Advanced; line not specified",
         linkage="Agent identity: YL201 is a B7-H3 ADC; supported by NCT06612151 B7-H3 testing requirement", conf="high",
         posted=""),
    dict(nct="NCT07189871", scope="SCLC cohort (pan-tumor)", indication="SCLC cohort within solid tumors",
         histology="Relapsed/refractory solid tumors incl. SCLC; cohort size not reported",
         agent="177Lu-BetaBart", modality="B7-H3 radioligand (177Lu)",
         line="Relapsed/refractory after most recent therapy; line not specified",
         linkage="Registry keyword/description: B7-H3-targeted 177Lu radioligand", conf="high",
         posted=""),
    dict(nct="NCT04145622", scope="SCLC cohort (pan-tumor)", indication="SCLC cohort within solid tumors",
         histology="Advanced solid tumors incl. SCLC; cohort size not reported",
         agent="Ifinatamab deruxtecan (I-DXd)", modality="B7-H3 ADC (DXd payload)",
         line="Advanced/refractory; line not specified",
         linkage="Registry description: I-DXd is an anti-B7-H3 ADC", conf="high",
         posted=""),
    dict(nct="NCT07102004", scope="SCLC cohort (pan-tumor)", indication="SCLC cohort (Phase II)",
         histology="Advanced solid tumors; Phase II is SCLC after platinum + ICI",
         agent="MHB088C", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="2L+ (after platinum + immune checkpoint inhibitor)",
         linkage="Registry keyword: B7H3; intervention is an ADC", conf="high",
         posted=""),
    dict(nct="NCT05652855", scope="SCLC cohort (pan-tumor)", indication="SCLC cohort within solid tumors",
         histology="Advanced solid tumors incl. SCLC; cohort size not reported",
         agent="MHB088C", modality="B7-H3 ADC (topoisomerase-I payload)",
         line="2L+ (after >=1 platinum + ICI)",
         linkage="Registry keyword: B7H3; intervention is an ADC", conf="high",
         posted=""),
    dict(nct="NCT06892548", scope="SCLC cohort (pan-tumor)", indication="SCLC cohort (Part 2 Cohort 2)",
         histology="Advanced lung cancer; Part 2 Cohort 2 is SCLC 2L+",
         agent="BNT324 (DB-1311) + BNT327", modality="B7-H3 ADC + PD-L1/VEGF bispecific",
         line="2L+ (Part 2 SCLC cohort); Part 1 mixed lines",
         linkage="Registry description: BNT324 is a B7-H3 ADC", conf="high",
         posted=""),
    dict(nct="NCT05551117", scope="SCLC cohort (pan-tumor)", indication="SCLC-eligible Part 2 mixed cohort",
         histology="Part 2 includes SCLC and squamous NSCLC; only 4 Part 2 participants, no SCLC breakdown",
         agent="MGC018 (vobramitamab duocarmazine)", modality="B7-H3 ADC (duocarmycin payload)",
         line="2L+ (>=1 prior systemic line; <=2 prior cytotoxic regimens)",
         linkage="Registry keyword: B7-H3; intervention description: anti-B7-H3 ADC", conf="high",
         posted=("Part 2 (SCLC-eligible mixed cohort) n=4; ORR 0%. No SCLC-specific breakdown posted. "
                 "Terminated for business reasons.")),
    # ---------------- NSCLC context (not LUAD-specific) ----------------
    dict(nct="NCT01391143", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (context)",
         histology="Refractory cancer incl. NSCLC; LUAD not separately reported",
         agent="Enoblituzumab (MGA271)", modality="B7-H3 monoclonal antibody (naked)",
         line="Advanced/refractory; line not specified",
         linkage="Drug MCP: enoblituzumab mapped to CD276 (CHEMBL3545373)", conf="high",
         posted=""),
    dict(nct="NCT02381314", scope="NSCLC context (not LUAD-specific)", indication="NSCLC / melanoma (context)",
         histology="NSCLC and melanoma cohorts; LUAD not separately reported",
         agent="Enoblituzumab + ipilimumab", modality="B7-H3 mAb + anti-CTLA-4",
         line="2L+ (NSCLC after >=1 prior systemic therapy)",
         linkage="Drug MCP: enoblituzumab mapped to CD276 (CHEMBL3545373)", conf="high",
         posted=""),
    dict(nct="NCT02475213", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (context)",
         histology="NSCLC, melanoma, SCCHN, urothelial; LUAD not separately reported",
         agent="Enoblituzumab + pembrolizumab or retifanlimab", modality="B7-H3 mAb + anti-PD-1",
         line="2L+ (NSCLC progressed on/after 1L)",
         linkage="Drug MCP: enoblituzumab mapped to CD276 (CHEMBL3545373)", conf="high",
         posted=("NSCLC PD-1/PD-L1-naive: ORR 33.3% (5/15; 95% CI 11.8-61.6), mPFS 5.1 mo, mOS 10.3 mo. "
                 "NSCLC PD-1/PD-L1-experienced: ORR 10.5% (2/19; 95% CI 1.3-33.1), mPFS 3.5 mo, mOS 6.0 mo. "
                 "NSCLC, not LUAD-specific.")),
    dict(nct="NCT02628535", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (context)",
         histology="B7-H3-expressing tumors incl. NSCLC; LUAD not separately reported",
         agent="MGD009", modality="B7-H3xCD3 DART protein",
         line="1-5 prior treatments (NSCLC)",
         linkage="Registry intervention description: B7-H3 x CD3 DART protein", conf="high",
         posted=""),
    dict(nct="NCT03729596", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (context)",
         histology="NSCLC expansion within solid tumors; LUAD not separately reported",
         agent="MGC018 (vobramitamab duocarmazine) +/- MGA012", modality="B7-H3 ADC (duocarmycin payload)",
         line="2L+ (after standard cytotoxic/targeted/checkpoint; <=2 prior chemo)",
         linkage="Registry keyword: B7-H3; intervention description: anti-B7-H3 ADC", conf="high",
         posted=("NSCLC expansion: ORR 15.0% (3/20 evaluable; 95% CI 3.2-37.9; ORR denominator 21), "
                 "mPFS 4.0 mo, mOS 7.0 mo. Terminated (business decision).")),
    dict(nct="NCT04165070", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (stage IV, 1L)",
         histology="Squamous or nonsquamous NSCLC; LUAD not separately reported",
         agent="I-DXd + pembrolizumab +/- chemotherapy", modality="B7-H3 ADC + anti-PD-1 +/- platinum",
         line="1L",
         linkage="Registry description: I-DXd is an anti-B7-H3 ADC", conf="high",
         posted=""),
    dict(nct="NCT05142189", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (context)",
         histology="Advanced NSCLC; multiple cohorts incl. anti-B7-H3 ADC combination",
         agent="BNT116 + anti-B7-H3 ADC combination", modality="Cancer vaccine + B7-H3 ADC arm",
         line="Mixed (1L and 2L+ cohorts)",
         linkage="Registry intervention description: anti-B7-H3 antibody conjugated to topoisomerase-I inhibitor", conf="high",
         posted=""),
    dict(nct="NCT06780085", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (nonsquamous, 2L+)",
         histology="Stage IV nonsquamous NSCLC; LUAD not separately reported",
         agent="I-DXd + raludotatug deruxtecan", modality="B7-H3 ADC + TROP2 ADC",
         line="2L+",
         linkage="Registry description: I-DXd is an anti-B7-H3 ADC", conf="high",
         posted=""),
    dict(nct="NCT07464327", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (nonsquamous, 2L+)",
         histology="Advanced/metastatic nonsquamous NSCLC without actionable alterations",
         agent="HS-20093 + adebrelimab", modality="B7-H3 ADC + anti-PD-L1",
         line="2L+",
         linkage="Agent identity: HS-20093 is a B7-H3 ADC; registry describes B7-H3 expression analyses", conf="high",
         posted=""),
    dict(nct="NCT07824882", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (nonsquamous, 2L+)",
         histology="Advanced/metastatic nonsquamous NSCLC without actionable alterations",
         agent="HS-20093 + adebrelimab", modality="B7-H3 ADC + anti-PD-L1",
         line="2L+",
         linkage="Agent identity: HS-20093 is a B7-H3 ADC; registry describes B7-H3 expression analyses", conf="high",
         posted=""),
    dict(nct="NCT07874984", scope="NSCLC context (not LUAD-specific)", indication="NSCLC (advanced)",
         histology="Driver-negative advanced NSCLC; LUAD not separately reported",
         agent="SPGL008 + SSGJ-706 +/- chemotherapy", modality="B7-H3 mAb-IL-15 fusion + PD-1/PD-L1 bispecific",
         line="Advanced; line not specified",
         linkage="Registry description: anti-B7-H3 mAb-IL-15 fusion (SPGL008)", conf="high",
         posted=""),
    dict(nct="NCT06621563", scope="NSCLC context (not LUAD-specific)", indication="NSCLC / solid tumors",
         histology="Solid tumors, NSCLC, CRC; LUAD not separately reported",
         agent="HS-20117 + HS-20093", modality="EGFR/c-MET bispecific + B7-H3 ADC",
         line="Advanced; line not specified",
         linkage="Registry keyword: B7H3 ADC (HS-20093) in combination", conf="high",
         posted=""),
    dict(nct="NCT06963502", scope="NSCLC context (not LUAD-specific)", indication="NSCLC / solid tumors",
         histology="KRAS G12C solid tumors, NSCLC, CRC; LUAD not separately reported",
         agent="HS-10370 + HS-20093 + adebrelimab", modality="KRAS G12C inhibitor + B7-H3 ADC + anti-PD-L1",
         line="Advanced; line not specified",
         linkage="Registry intervention description: HS-20093 is a B7-H3 ADC (combination arm)", conf="high",
         posted=""),
    dict(nct="NCT07503808", scope="NSCLC context (not LUAD-specific)", indication="NSCLC / solid tumors",
         histology="B7-H3/PTK7-expressing solid tumors incl. NSCLC; SCLC not eligible",
         agent="IDE034", modality="B7-H3/PTK7-targeted agent (modality not stated in registry)",
         line=">=1 prior line (progressed/recurred)",
         linkage="Registry keyword: B7-H3 (CD276) and PTK7", conf="high",
         posted=""),
    dict(nct="NCT07181473", scope="NSCLC context (not LUAD-specific)", indication="NSCLC / solid tumors",
         histology="Solid tumors incl. NSCLC; SCLC not listed",
         agent="TJ101", modality="EGFR/B7-H3 bispecific ADC",
         line="2L+ (exhausted standard treatment)",
         linkage="Registry description: EGFR/B7H3 bispecific ADC", conf="high",
         posted=""),
    dict(nct="NCT05341492", scope="NSCLC context (not LUAD-specific)", indication="Lung cancer / TNBC (histology not specified)",
         histology="Lung cancer and TNBC; LUAD not separately reported",
         agent="EGFR/B7H3 CAR-T", modality="EGFR/B7-H3 dual-target CAR-T",
         line="Advanced; line not specified",
         linkage="Registry title/intervention: EGFR/B7H3 CAR-T", conf="high",
         posted=""),
]

# ---------------------------------------------------------------- registry data
trials = {}
found_by = {}
for f in sorted(RAW.glob("ctgov_search_*.json")):
    if f.name.endswith("index.json") or f.name.endswith("counts.json"):
        continue
    d = json.load(open(f))
    for t in d.get("trials", []):
        nct = t.get("nctId")
        if not nct:
            continue
        trials.setdefault(nct, t)
        found_by.setdefault(nct, set()).add(f.stem.replace("ctgov_search_", ""))


def primaries(t, n=2):
    po = [o.get("measure") for o in (t.get("primaryOutcomes") or []) if o.get("measure")]
    if not po:
        return "Not applicable (expanded access)" if t.get("expandedAccess") else "Not reported"
    return "; ".join(po[:n])


records = []
for r in ROWS:
    nct = r["nct"]
    t = trials.get(nct)
    if t is None:
        raise SystemExit(f"missing registry record for {nct}")
    records.append({
        "nct_id": nct,
        "brief_title": t.get("briefTitle"),
        "scope": r["scope"],
        "indication": r["indication"],
        "histology_notes": r["histology"],
        "agent": r["agent"],
        "modality": r["modality"],
        "phase": ("N/A (expanded access)" if r["scope"] == "SCLC expanded access"
                  else "/".join(t.get("phases") or []) or "N/A"),
        "status": t.get("overallStatus"),
        "line_of_therapy": r["line"],
        "enrollment": t.get("enrollmentCount") if t.get("enrollmentCount") is not None else "NR",
        "enrollment_type": t.get("enrollmentType") or "",
        "primary_endpoint": primaries(t),
        "results_posted_in_ctgov": "Yes" if t.get("hasResults") else "No",
        "posted_results_summary": r["posted"],
        "start_date": t.get("startDate") or "",
        "primary_completion_date": t.get("primaryCompletionDate") or "",
        "completion_date": t.get("completionDate") or "",
        "why_stopped": t.get("whyStopped") or "",
        "lead_sponsor": t.get("leadSponsor") or "",
        "target_linkage_evidence": r["linkage"],
        "target_linkage_confidence": r["conf"],
        "registry_search_queries": "; ".join(sorted(found_by.get(nct, []))),
        "registry_source": "ClinicalTrials.gov API v2 via configured clinicaltrials MCP server",
        "as_of_date": "2026-10-20",
    })

df = pd.DataFrame(records)
# order: SCLC-specific, SCLC EAP, pan-tumor SCLC, NSCLC context
order = {"SCLC-specific": 0, "SCLC expanded access": 1,
         "SCLC cohort (pan-tumor)": 2, "NSCLC context (not LUAD-specific)": 3}
df["_o"] = df["scope"].map(order)
df = df.sort_values(["_o", "nct_id"]).drop(columns="_o").reset_index(drop=True)

out_final = TAB / "b7h3_luad_sclc_trials.csv"
out_audit = PROC / "b7h3_trial_selection_audit.csv"
df.to_csv(out_final, index=False)
df.to_csv(out_audit, index=False)

# ---------------------------------------------------------------- posted results
posted = pd.DataFrame([
    dict(nct_id="NCT06227546", indication="SCLC (ES-SCLC, R/R)", agent="MGC018",
         cohort="Single arm, n=9", endpoint="ORR (primary)",
         result="0/9 (0%)", comparator="None",
         additional="SAEs: atrial fibrillation 3/9; lung infection 1/9; sepsis 1/9; respiratory failure 1/9",
         source="ClinicalTrials.gov results module; fetched 2026-10-20"),
    dict(nct_id="NCT02475213", indication="NSCLC (context; not LUAD-specific)", agent="Enoblituzumab + pembrolizumab",
         cohort="PD-1/PD-L1-naive, n=15", endpoint="ORR",
         result="33.3% (5/15; 95% CI 11.8-61.6)", comparator="None (single arm)",
         additional="mPFS 5.1 mo; mOS 10.3 mo",
         source="ClinicalTrials.gov results module; fetched 2026-10-20"),
    dict(nct_id="NCT02475213", indication="NSCLC (context; not LUAD-specific)", agent="Enoblituzumab + pembrolizumab",
         cohort="PD-1/PD-L1-experienced, n=19", endpoint="ORR",
         result="10.5% (2/19; 95% CI 1.3-33.1)", comparator="None (single arm)",
         additional="mPFS 3.5 mo; mOS 6.0 mo",
         source="ClinicalTrials.gov results module; fetched 2026-10-20"),
    dict(nct_id="NCT03729596", indication="NSCLC (context; not LUAD-specific)", agent="MGC018",
         cohort="NSCLC expansion, 20 evaluable", endpoint="ORR",
         result="15.0% (3/20; 95% CI 3.2-37.9)", comparator="None (single arm)",
         additional="mPFS 4.0 mo; mOS 7.0 mo; trial terminated for business decision",
         source="ClinicalTrials.gov results module; saved raw record; fetched 2026-10-20"),
    dict(nct_id="NCT05551117", indication="SCLC-eligible Part 2 mixed cohort", agent="MGC018",
         cohort="Part 2, n=4", endpoint="ORR (primary for Part 2)",
         result="0/4 (0%)", comparator="None",
         additional="No SCLC-specific breakdown; terminated for business reasons",
         source="ClinicalTrials.gov results module via MCP server implementation; fetched 2026-10-20"),
])
posted.to_csv(TAB / "b7h3_posted_results_extract.csv", index=False)

# ---------------------------------------------------------------- query counts
counts = json.load(open(RAW / "ctgov_b7h3_search_counts.json"))
rows = []
for c in counts.get("counts", []):
    q = c.get("query", {})
    rows.append({
        "label": c.get("label"),
        "condition": q.get("condition") or "",
        "term": q.get("term") or "",
        "intervention": q.get("intervention") or "",
        "country": "global (country=None)",
        "total_count": c.get("result", {}).get("total_count"),
        "success": c.get("result", {}).get("success"),
    })
pd.DataFrame(rows).to_csv(TAB / "b7h3_ctgov_query_counts.csv", index=False)

# ---------------------------------------------------------------- LUAD audit
luad = []
for f in sorted(RAW.glob("ctgov_search_*condition_lung_adenocarcinoma.json")):
    d = json.load(open(f))
    for t in d.get("trials", []):
        luad.append(t)
seen = set()
with open(TAB / "b7h3_luad_search_hits.csv", "w") as fh:
    fh.write("nct_id,brief_title,conditions,interventions,why_not_luad_specific\n")
    for t in luad:
        n = t.get("nctId")
        if n in seen:
            continue
        seen.add(n)
        why = {
            "NCT02628535": "B7-H3 DART in B7-H3-expressing solid tumors incl. NSCLC; no LUAD-specific cohort",
            "NCT04514484": "Not B7-H3-directed (cabozantinib + nivolumab); B7-H3 only a incidental term match",
            "NCT05914116": "Pan-tumor B7-H3 ADC; SCLC cohort, no LUAD-specific cohort",
            "NCT06242470": "Pan-tumor B7-H3 ADC incl. NSCLC/SCLC; no LUAD-specific cohort",
            "NCT06953089": "Pan-tumor B7-H3 ADC combination; no LUAD-specific cohort",
            "NCT07509034": "SCLC-specific B7-H3 CAR-T; adenocarcinoma term is an exclusion match",
        }.get(n, "No LUAD-specific condition/cohort")
        fh.write('"{}","{}","{}","{}","{}"\n'.format(
            n,
            (t.get("briefTitle") or "").replace('"', "'"),
            ("; ".join(t.get("conditions") or [])).replace('"', "'"),
            ("; ".join(i.get("name") or "" for i in (t.get("interventions") or []))).replace('"', "'"),
            why))

print("wrote", out_final, len(df), "rows")
print(df["scope"].value_counts().to_string())
print(df["phase"].value_counts().to_string())
print("posted-results trials:", df[df.results_posted_in_ctgov == "Yes"][["nct_id", "scope"]].to_dict("records"))
