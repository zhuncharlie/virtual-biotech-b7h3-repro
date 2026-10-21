#!/usr/bin/env python3
"""Apply revision-3 review corrections to the existing B7-H3 safety tables.

No analysis is rerun. This script reads the revision-2 CSVs, applies targeted
wording/attribution corrections, and writes the same filenames.

Corrections implemented:
  1. CD276 LoF: report o/e 0.667 with "moderate LoF tolerance" only. The raw
     record does not label a confidence level for its interval and carries more
     than one bin field, so no CI and no bin are quoted anywhere.
  2. Target-level versus payload/modality-level attribution kept explicit in
     every row; payload toxicity is labelled as NOT B7-H3 biology.
  3. Broad expression is described as HPA bulk RNA plus prior knowledge, not
     protein density; normal-lung protein is level 2 and cell-level transcript
     is comparatively low.
  4. Zero records are evidence gaps, not clean profiles; unapproved-agent zero
     warnings may reflect unapproved status.
  5. SCLC risk-benefit is carried in the report, tied to the staged clinical
     decision (feasibility established, efficacy unproven, risk tolerance
     conditional on a positive class-level Phase 3 readout).

Inputs/outputs (in place):
  results/tables/b7h3_safety_signals.csv
  results/tables/b7h3_agent_registry_lung_cancer.csv
  results/tables/b7h3_modality_class_toxicities.csv
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAB = ROOT / "results" / "tables"


def load(name):
    path = TAB / name
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return path, reader.fieldnames, list(reader)


def save(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# ------------------------------------------------------------------ signals
path, fields, rows = load("b7h3_safety_signals.csv")
for row in rows:
    signal = row["signal"]

    if signal == "CD276 LoF constraint":
        row["interpretation"] = (
            "34 observed vs 51.0 expected. o/e 0.667 indicates moderate LoF "
            "tolerance: partial depletion of LoF variants, not extreme "
            "constraint. Moderate tolerance is not evidence of safety and does "
            "not address acute antibody-mediated depletion."
        )
    elif signal == "CD276 LoF o/e":
        row["interpretation"] = (
            "Point estimate 0.667. The retrieved record contains o/e interval "
            "bounds and more than one bin field, but it does not label the "
            "interval's confidence level. To avoid mixing confidence levels or "
            "bins, no CI and no bin are quoted. Report o/e 0.667 with 'moderate "
            "LoF tolerance' only."
        )
    elif signal == "B7-H3 normal-tissue expression breadth":
        row["interpretation"] = (
            "TARGET-LEVEL. Broad low-level normal expression is supported by "
            "HPA bulk RNA and prior knowledge. It creates off-tumour antigen "
            "exposure, but TPM is bulk tissue RNA and is not surface protein "
            "density; this does not establish high protein on normal tissue."
        )
    elif signal == "B7-H3 in normal lung" and row["metric"].startswith("HPA"):
        row["interpretation"] = (
            "TARGET-LEVEL. Moderate bulk RNA (1,682.5 TPM, level 4) and HPA "
            "protein level 2 (reliable, ordinal) in normal lung. Level 2 does "
            "NOT indicate high protein. The bulk lung RNA is partly "
            "attributable to resident macrophages (HPA macrophage "
            "9,456-14,497 TPM; protein unreliable, so RNA-only). The "
            "cell-level normal-lung transcript is comparatively low (13.9 CPM "
            "organ weighted mean)."
        )
    elif signal == "B7-H3 in normal lung" and row["metric"].startswith("Census"):
        row["interpretation"] = (
            "TARGET-LEVEL. Cell-level normal-lung CD276 transcript is "
            "comparatively low (13.9 CPM; at the median of 19 sampled organs "
            "and well below skin 46.0 and kidney 42.6). The macrophage signal "
            "is RNA-only (HPA macrophage protein unreliable). Medians are 0 and "
            "CPM is not protein; this does not support an inference of high "
            "normal-lung protein."
        )
    elif signal == "Enoblituzumab / omburtamab warning records":
        row["interpretation"] = (
            "Zero FDA warning records for enoblituzumab and omburtamab may "
            "reflect their unapproved status (no FDA label); it does not "
            "indicate a clean safety profile. The warnings tool was verified "
            "functional with a positive control."
        )
save(path, fields, rows)

# ----------------------------------------------------------- agent registry
path, fields, rows = load("b7h3_agent_registry_lung_cancer.csv")
for row in rows:
    row["notes"] = row["notes"].replace(
        "reflects absence of an FDA label",
        "may reflect absence of an FDA label",
    )
    if row["agent"].startswith("Ifinatamab"):
        row["notes"] = (
            "EXPLICIT EVIDENCE GAP: no drug record, therefore no agent-specific "
            "OpenFDA query was possible. Zero retrievable records is NOT a clean "
            "safety profile. Prior knowledge: DXd-class ILD/pneumonitis and "
            "myelosuppression; these are payload-level, not B7-H3 biology."
        )
    elif row["agent"].startswith("Vobramitamab"):
        row["notes"] = (
            "EXPLICIT EVIDENCE GAP: no drug record, therefore no agent-specific "
            "OpenFDA query was possible. Zero retrievable records is NOT a clean "
            "safety profile. Prior knowledge: duocarmycin-class "
            "myelosuppression, fatigue, rash, infusion reactions and ocular "
            "surface toxicity; these are payload-level, not B7-H3 biology."
        )
save(path, fields, rows)

# ------------------------------------------------------- modality toxicities
path, fields, rows = load("b7h3_modality_class_toxicities.csv")
for row in rows:
    if row["toxicity"].startswith("On-target off-tumour injury"):
        row["driver"] = (
            "TARGET-LEVEL: B7-H3 expression on normal tissue plus effector "
            "potency; antigen density not measured. This is the only "
            "target-level risk among the modality-class toxicities."
        )
    elif row["risk_level"] in ("payload_level", "modality_level"):
        driver = row["driver"].replace(".;", ";").rstrip()
        if "NOT B7-H3 biology" not in driver:
            driver = driver.rstrip(".") + "; NOT B7-H3 biology"
        row["driver"] = driver
save(path, fields, rows)

print("Revision-3 corrections applied to three tables.")
