#!/usr/bin/env python
"""
Panel 4A revision 2: tabulate the GWAS trait-label counts used in the report.

Report claims audited here:
  - §1.3 "13/41" gene-body GWAS credible sets carry a trait label
  - G2 note "17/67" L2G loci carry a trait label

Trait labels are not present on the credible-set records themselves.  They are
taken from the round-1 L2G table (`trait_resolved`), keyed by studyId.  Every
studyId in the 41 gene-body GWAS credible sets is present in the L2G table, so
the map is complete; 13 of those 41 rows map to a non-null label.

Outputs
  results/tables/cd276_gwas_trait_label_audit.csv
  data/processed/cd276_trait_label_audit_log.txt
"""
import os
from pathlib import Path
import pandas as pd

BASE = str(Path(__file__).resolve().parents[2])
RAW = os.path.join(BASE, "data", "raw")

GENE_START, GENE_END = 73_683_966, 73_714_514

LOG = []


def log(msg):
    print(msg)
    LOG.append(str(msg))


def main():
    cs_path = os.path.join(RAW, "cd276_locus_credible_sets_all_studies.parquet")
    l2g_path = os.path.join(RAW, "cd276_l2g_predictions.csv")
    cs = pd.read_parquet(cs_path)
    l2g = pd.read_csv(l2g_path)

    # one trait label per studyId (first non-null); all labels for a study are identical
    trait_map = (l2g.dropna(subset=["trait_resolved"])
                 .groupby("studyId")["trait_resolved"].first())

    rows = []

    def emit(dataset, dataset_definition, denominator, series, source_file):
        """series = labelled trait values (NaNs included); counts include unlabelled."""
        vc = series.value_counts(dropna=False)
        for label, n in vc.items():
            rows.append({
                "dataset": dataset,
                "dataset_definition": dataset_definition,
                "trait_label": "UNLABELLED" if pd.isna(label) else str(label),
                "n_rows": int(n),
                "denominator": int(denominator),
                "numerator_definition": (
                    "count of rows in this dataset whose studyId maps to this non-null "
                    "trait_resolved value in data/raw/cd276_l2g_predictions.csv"
                    if not pd.isna(label) else
                    "count of rows in this dataset whose studyId has no non-null "
                    "trait_resolved value in data/raw/cd276_l2g_predictions.csv"),
                "source_file": source_file,
            })

    # (1) gene-body GWAS credible sets: 41
    gb = cs[(cs.position >= GENE_START) & (cs.position <= GENE_END)
            & (cs.studyType == "gwas")].copy()
    gb["studyId"] = gb["studyId"].astype(str)
    gb["trait_resolved"] = gb["studyId"].map(trait_map)
    emit("gene_body_gwas_credible_sets",
         f"GWAS credible sets with lead variant in CD276 gene body chr15:{GENE_START}-{GENE_END} "
         f"(data/raw/cd276_locus_credible_sets_all_studies.parquet, studyType == 'gwas')",
         len(gb), gb["trait_resolved"], "data/raw/cd276_locus_credible_sets_all_studies.parquet")
    log(f"gene-body GWAS credible sets: {len(gb)}; labelled {gb.trait_resolved.notna().sum()}; "
        f"unlabelled {gb.trait_resolved.isna().sum()}")

    # (2) gene-body credible sets, all study types: 65 (supporting, not a headline claim)
    gba = cs[(cs.position >= GENE_START) & (cs.position <= GENE_END)].copy()
    gba["studyId"] = gba["studyId"].astype(str)
    gba["trait_resolved"] = gba["studyId"].map(trait_map)
    emit("gene_body_all_credible_sets",
         f"all-study-type credible sets with lead variant in CD276 gene body "
         f"chr15:{GENE_START}-{GENE_END}",
         len(gba), gba["trait_resolved"], "data/raw/cd276_locus_credible_sets_all_studies.parquet")
    log(f"gene-body all-type credible sets: {len(gba)}; labelled {gba.trait_resolved.notna().sum()}; "
        f"unlabelled {gba.trait_resolved.isna().sum()}")

    # (3) L2G loci: 67
    emit("l2g_loci",
         "all L2G rows returned for ENSG00000103855 (67 distinct studyLocusId)",
         len(l2g), l2g["trait_resolved"], "data/raw/cd276_l2g_predictions.csv")
    log(f"L2G loci: {len(l2g)}; labelled {l2g.trait_resolved.notna().sum()}; "
        f"unlabelled {l2g.trait_resolved.isna().sum()}")

    out = pd.DataFrame(rows)
    out_path = os.path.join(BASE, "results", "tables", "cd276_gwas_trait_label_audit.csv")
    out.to_csv(out_path, index=False)
    log(f"Wrote {out_path} ({len(out)} rows)")

    # explicit reconciliation of the two prose claims
    n41 = int(gb.trait_resolved.notna().sum())
    n67 = int(l2g.trait_resolved.notna().sum())
    log("")
    log(f"Claim 13/41  -> recomputed {n41}/{len(gb)}  [{'MATCH' if n41 == 13 else 'MISMATCH'}]")
    log(f"Claim 17/67  -> recomputed {n67}/{len(l2g)}  [{'MATCH' if n67 == 17 else 'MISMATCH'}]")
    log(f"41 studyIds present in L2G table: {gb.studyId.isin(set(l2g.studyId)).sum()}/41")

    with open(os.path.join(BASE, "data", "processed", "cd276_trait_label_audit_log.txt"), "w") as fh:
        fh.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
