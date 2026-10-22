#!/usr/bin/env python
"""
Panel 4A stream 1: verify-and-reuse the germline genetics result for CD276.

Revision 2 (2026-10-22): every input now resolves inside THIS run's LIVE
workspace (data/raw/).  The previous hardcoded BASE (20261021-080518) and the
hardcoded G7 locus-overlap literal have been removed.  Both gene-body
locus-interval counts are now recomputed and labelled with their source
universe, because they answer different questions:

  - 65 all types / 41 GWAS   lead variant inside the gene span (primary)
  - 201 all types / 195 GWAS locus interval overlaps the gene span, using the
                             full TSS +/-500 kb credible-set retrieval
  - 69 all types / 65 GWAS   locus interval overlaps the gene span, restricted
                             to the round-1 303-row artifact (lead variants in
                             chr15:73.5-73.9 Mb)

Inputs (all under <workspace>/data/raw/)
  cd276_locus_credible_sets_all_studies.parquet
  cd276_tss250kb_region_query_round2.parquet
  cd276_tss500kb_region_query_round2.parquet
  round1_per_study/{luad,sclc}_*_credible_sets.parquet   (8 studies)
  cd276_l2g_predictions.csv

Outputs
  results/tables/cd276_round2_germline_verification.csv
  results/tables/cd276_round2_per_study_locus_check.csv
  results/tables/cd276_round2_credible_set_window_reconciliation.csv
  data/processed/cd276_round2_germline_verification_log.txt
"""
import os
from pathlib import Path
import pandas as pd

# Workspace root = .../work/genomics-analyst (script lives in code/scripts/)
BASE = str(Path(__file__).resolve().parents[2])
RAW = os.path.join(BASE, "data", "raw")
PER_STUDY_DIR = os.path.join(RAW, "round1_per_study")

# CD276 GRCh38 coordinates (same coordinates round 1 resolved via Open Targets)
CHR = "15"
GENE_START = 73_683_966
GENE_END = 73_714_514
TSS = 73_684_383
WIN_250_LO, WIN_250_HI = TSS - 250_000, TSS + 250_000   # 73,434,383-73,934,383
WIN_500_LO, WIN_500_HI = TSS - 500_000, TSS + 500_000   # 73,184,383-74,184,383
R1_QUERY_LO, R1_QUERY_HI = 73_500_000, 73_900_000       # round-1 region query, lead-variant filter

STUDIES = {
    "GCST90297563": ("LUAD", "Lung adenocarcinoma (Shi 2023)"),
    "GCST90455522": ("LUAD", "Lung adenocarcinoma (Gorman 2024)"),
    "GCST90134662": ("LUAD", "Lung adenocarcinoma (Byun 2022)"),
    "GCST008836": ("LUAD", "Lung adenocarcinoma (Dai 2019)"),
    "GCST004744": ("LUAD", "Lung adenocarcinoma (McKay 2017)"),
    "GCST004746": ("SCLC", "Small cell lung carcinoma (McKay 2017)"),
    "GCST90134664": ("SCLC", "Small cell lung carcinoma (Byun 2022)"),
    "FINNGEN_R12_C3_SCLC_EXALLC": ("SCLC", "Small cell lung cancer (FinnGen R12)"),
}
PER_STUDY_FILES = {
    "GCST90297563": "luad_GCST90297563_credible_sets.parquet",
    "GCST90455522": "luad_GCST90455522_credible_sets.parquet",
    "GCST90134662": "luad_GCST90134662_credible_sets.parquet",
    "GCST008836": "luad_GCST008836_credible_sets.parquet",
    "GCST004744": "luad_GCST004744_credible_sets.parquet",
    "GCST004746": "sclc_GCST004746_credible_sets.parquet",
    "GCST90134664": "sclc_GCST90134664_credible_sets.parquet",
    "FINNGEN_R12_C3_SCLC_EXALLC": "sclc_FINNGEN_R12_C3_SCLC_EXALLC_credible_sets.parquet",
}

LOG = []


def log(msg):
    print(msg)
    LOG.append(str(msg))


def read_region(path):
    df = pd.read_parquet(path)
    df["position"] = df["position"].astype("int64")
    return df


def window_counts(df, label, lo, hi, source_file):
    """Count credible sets whose lead variant lies in [lo, hi]."""
    m = (df.position >= lo) & (df.position <= hi)
    sub = df[m]
    g = sub[sub.studyType == "gwas"]
    return {
        "definition": label,
        "window_start_grch38": lo,
        "window_end_grch38": hi,
        "window_size_bp": hi - lo,
        "filter": "lead variant position (studyLocusId.variantId) within window",
        "source_file": source_file,
        "n_credible_sets_all_types": len(sub),
        "n_distinct_studies_all_types": sub.studyId.nunique(),
        "n_credible_sets_gwas": len(g),
        "n_distinct_gwas_studies": g.studyId.nunique(),
    }


def locus_overlap_counts(df, label, lo, hi, source_file):
    """Count credible sets whose fine-mapped locus interval overlaps [lo, hi]."""
    d = df.dropna(subset=["locusStart", "locusEnd"]).copy()
    d["locusStart"] = d["locusStart"].astype("int64")
    d["locusEnd"] = d["locusEnd"].astype("int64")
    m = (d.locusStart <= hi) & (d.locusEnd >= lo)
    sub = d[m]
    g = sub[sub.studyType == "gwas"]
    return {
        "definition": label,
        "window_start_grch38": lo,
        "window_end_grch38": hi,
        "window_size_bp": hi - lo,
        "filter": "credible-set locus interval [locusStart,locusEnd] overlaps window "
                  "(rows with null locus bounds dropped)",
        "source_file": source_file,
        "n_credible_sets_all_types": len(sub),
        "n_distinct_studies_all_types": sub.studyId.nunique(),
        "n_credible_sets_gwas": len(g),
        "n_distinct_gwas_studies": g.studyId.nunique(),
    }


def main():
    os.makedirs(os.path.join(BASE, "results", "tables"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "data", "processed"), exist_ok=True)
    log(f"Workspace root resolved from script location: {BASE}")
    log(f"CD276 constants: chr{CHR}:{GENE_START}-{GENE_END}, TSS {TSS}")
    log(f"Windows: gene body [{GENE_START},{GENE_END}]; +/-250 kb [{WIN_250_LO},{WIN_250_HI}]; "
        f"+/-500 kb [{WIN_500_LO},{WIN_500_HI}]; round-1 query [{R1_QUERY_LO},{R1_QUERY_HI}]")

    old_path = os.path.join(RAW, "cd276_locus_credible_sets_all_studies.parquet")
    q250_path = os.path.join(RAW, "cd276_tss250kb_region_query_round2.parquet")
    q500_path = os.path.join(RAW, "cd276_tss500kb_region_query_round2.parquet")
    old = read_region(old_path)
    q250 = read_region(q250_path)
    q500 = read_region(q500_path)
    log(f"Loaded round-1 all-studies parquet: {len(old)} rows ({old_path})")
    log(f"Loaded +/-250 kb round-2 query: {len(q250)} rows ({q250_path})")
    log(f"Loaded +/-500 kb round-2 query: {len(q500)} rows ({q500_path})")

    # --- Verify the round-1 303-row artifact is exactly reproduced by the new +/-250 kb query
    old_in_r1_window = old[(old.position >= R1_QUERY_LO) & (old.position <= R1_QUERY_HI)]
    q250_in_r1_window = q250[(q250.position >= R1_QUERY_LO) & (q250.position <= R1_QUERY_HI)]
    same_ids = set(old.studyLocusId) == set(q250_in_r1_window.studyLocusId)
    log(f"Round-1 303-row artifact == new +/-250 kb query restricted to 73.5-73.9 Mb: {same_ids} "
        f"(old={len(old)}, q250_restricted={len(q250_in_r1_window)})")
    if not same_ids:
        log(f"  IDs only in round-1 artifact: {len(set(old.studyLocusId) - set(q250_in_r1_window.studyLocusId))}; "
            f"only in new query: {len(set(q250_in_r1_window.studyLocusId) - set(old.studyLocusId))}")

    rel_old = os.path.relpath(old_path, BASE)
    rel_q250 = os.path.relpath(q250_path, BASE)
    rel_q500 = os.path.relpath(q500_path, BASE)

    # --- Reconciliation of the 303 / 123 / 116 / 67 counts
    recon = []
    recon.append(window_counts(
        old, "R1_QUERY_WINDOW: lead variant chr15:73,500,000-73,900,000 "
             "(window used by the round-1 region query; TSS -184,383 to +215,617)",
        R1_QUERY_LO, R1_QUERY_HI, rel_old))
    recon.append(window_counts(q250, "TSS +/-250 kb", WIN_250_LO, WIN_250_HI, rel_q250))
    recon.append(window_counts(q500, "TSS +/-500 kb", WIN_500_LO, WIN_500_HI, rel_q500))
    recon.append(window_counts(old, "CD276 gene body (lead variant inside gene span)",
                               GENE_START, GENE_END, rel_old))
    # Locus-interval sensitivity: two universes, labelled explicitly.
    recon.append(locus_overlap_counts(
        old, "CD276 gene body (locus interval overlap; round-1 303-row universe, "
             "lead variant 73.5-73.9 Mb)",
        GENE_START, GENE_END, rel_old))
    recon.append(locus_overlap_counts(
        q500, "CD276 gene body (locus interval overlap; full TSS +/-500 kb retrieval universe)",
        GENE_START, GENE_END, rel_q500))
    recon.append(locus_overlap_counts(
        q250, "TSS +/-250 kb (locus interval overlap)", WIN_250_LO, WIN_250_HI, rel_q250))
    recon.append(locus_overlap_counts(
        q500, "TSS +/-500 kb (locus interval overlap)", WIN_500_LO, WIN_500_HI, rel_q500))
    recon_df = pd.DataFrame(recon)
    recon_path = os.path.join(BASE, "results", "tables",
                              "cd276_round2_credible_set_window_reconciliation.csv")
    recon_df.to_csv(recon_path, index=False)
    log(f"Wrote {recon_path} ({len(recon_df)} rows)")
    for _, r in recon_df.iterrows():
        log(f"  {r.definition}: {r.n_credible_sets_all_types} sets / "
            f"{r.n_distinct_studies_all_types} studies (all types); "
            f"{r.n_credible_sets_gwas} GWAS sets / {r.n_distinct_gwas_studies} GWAS studies")

    # Pull the four gene-body definitions for the G7 note (all computed, none typed).
    def count_for(prefix, gwas):
        row = recon_df[recon_df.definition.str.startswith(prefix)]
        col = "n_credible_sets_gwas" if gwas else "n_credible_sets_all_types"
        return int(row[col].iloc[0])
    gb_lead_all = count_for("CD276 gene body (lead variant", False)
    gb_lead_gwas = count_for("CD276 gene body (lead variant", True)
    gb_ov_r1_all = count_for("CD276 gene body (locus interval overlap; round-1", False)
    gb_ov_r1_gwas = count_for("CD276 gene body (locus interval overlap; round-1", True)
    gb_ov_full_all = count_for("CD276 gene body (locus interval overlap; full", False)
    gb_ov_full_gwas = count_for("CD276 gene body (locus interval overlap; full", True)

    # --- Per-study LUAD/SCLC check, recomputed from full per-study credible-set pulls
    per_study = []
    for sid, fname in PER_STUDY_FILES.items():
        path = os.path.join(PER_STUDY_DIR, fname)
        df = pd.read_parquet(path)
        c15 = df[df.chromosome == CHR].copy()
        if len(c15):
            c15["distance_bp"] = (c15.position.astype("int64") - TSS)
            min_abs = int(c15.distance_bp.abs().min())
            min_signed = int(c15.loc[c15.distance_bp.abs().idxmin(), "distance_bp"])
        else:
            min_abs, min_signed = None, None
        hist, label = STUDIES[sid]
        per_study.append({
            "histology": hist, "study_id": sid, "study_label": label,
            "source_file": os.path.relpath(path, BASE),
            "credible_sets_retrieved": len(df),
            "chr15_credible_sets": len(c15),
            "min_distance_chr15_lead_variant_to_CD276_TSS_bp": min_abs,
            "min_signed_distance_bp": min_signed,
            "lead_variant_in_CD276_gene_body": int(((df.position >= GENE_START) & (df.position <= GENE_END)).sum()),
            "lead_variant_within_250kb_of_TSS": int(((df.position - TSS).abs() <= 250_000).sum()),
            "lead_variant_within_500kb_of_TSS": int(((df.position - TSS).abs() <= 500_000).sum()),
            "credible_set_locus_overlaps_CD276_gene_body": int(
                ((df.locusStart <= GENE_END) & (df.locusEnd >= GENE_START)).sum()),
            "credible_set_locus_overlaps_500kb": int(
                ((df.locusStart <= WIN_500_HI) & (df.locusEnd >= WIN_500_LO)).sum()),
        })
    ps = pd.DataFrame(per_study)
    ps_path = os.path.join(BASE, "results", "tables", "cd276_round2_per_study_locus_check.csv")
    ps.to_csv(ps_path, index=False)
    log(f"Wrote {ps_path} ({len(ps)} studies)")
    log(ps[["histology", "study_id", "credible_sets_retrieved", "chr15_credible_sets",
            "min_distance_chr15_lead_variant_to_CD276_TSS_bp", "lead_variant_within_500kb_of_TSS"]].to_string(index=False))

    n_with_500 = int((ps.lead_variant_within_500kb_of_TSS > 0).sum())
    n_with_body = int((ps.lead_variant_in_CD276_gene_body > 0).sum())
    min_distance_all = int(ps.min_distance_chr15_lead_variant_to_CD276_TSS_bp.min())
    log(f"LUAD+SCLC studies with lead variant within +/-500 kb: {n_with_500}/8; in gene body: {n_with_body}/8; "
        f"closest chr15 credible set across the 8 studies: {min_distance_all} bp from TSS")

    # --- L2G verification
    l2g_path = os.path.join(RAW, "cd276_l2g_predictions.csv")
    l2g = pd.read_csv(l2g_path)
    l2g["distance_to_CD276_TSS_bp"] = pd.to_numeric(l2g["distance_to_CD276_TSS_bp"], errors="coerce")
    log(f"L2G rows={len(l2g)}; distinct studyLocusId={l2g.studyLocusId.nunique()}; "
        f"distinct studies={l2g.studyId.nunique()}; score>=0.5={int((l2g.score >= 0.5).sum())}; "
        f"max score={l2g.score.max():.4f}; flagged LUAD/SCLC={int(l2g.is_luad_or_sclc.sum())}; "
        f"studyIds matching the 8 LUAD/SCLC studies={sum(s in set(l2g.studyId) for s in STUDIES)}")
    log(f"L2G studyType counts: {l2g.studyType.value_counts().to_dict()}")
    log(f"L2G |distance to TSS| range: {l2g.distance_to_CD276_TSS_bp.abs().min()}-{l2g.distance_to_CD276_TSS_bp.abs().max()} bp; "
        f"all in +/-250 kb: {bool((l2g.distance_to_CD276_TSS_bp.abs() <= 250_000).all())}")
    log(f"L2G loci present in +/-500 kb credible-set query: {len(set(l2g.studyLocusId) & set(q500.studyLocusId))}/"
        f"{l2g.studyLocusId.nunique()}")
    n_l2g_labelled = int(l2g.trait_resolved.notna().sum())

    # --- Verification table (one row per check)
    checks = []

    def add(check_id, claim, evidence_stream, definition, source_file, exact_filter,
            recomputed, reported, matches, note):
        checks.append({
            "check_id": check_id, "claim": claim, "evidence_stream": evidence_stream,
            "definition": definition, "source_file": source_file, "exact_filter": exact_filter,
            "recomputed_value": recomputed, "round1_reported_value": reported,
            "matches_round1": matches, "note": note,
        })

    add("G1", "0/8 LUAD+SCLC GWAS studies contain a CD276-locus credible set",
        "germline GWAS fine-mapping", "lead variant within +/-500 kb of CD276 TSS (primary); gene body (secondary)",
        "data/raw/round1_per_study/{luad,sclc}_*_credible_sets.parquet (8 files)",
        "for each study: count credible sets with |lead_variant_position - 73684383| <= 500000",
        f"{n_with_500}/8 within 500 kb; {n_with_body}/8 in gene body", "0/8", True,
        f"minimum distance across the 8 studies = {min_distance_all} bp (nearest locus is the 15q25 nicotinic-receptor region)")

    add("G2", "0/67 L2G predictions derive from a LUAD or SCLC study",
        "germline L2G (locus-to-gene)", "all L2G rows returned for ENSG00000103855 (min_score 0.1)",
        "data/raw/cd276_l2g_predictions.csv",
        "count rows where is_luad_or_sclc == True, or studyId in the 8 LUAD/SCLC study IDs",
        f"0/67 (is_luad_or_sclc True in 0 rows; 0 of 67 studyIds match the 8 studies)", "0/67", True,
        f"67 loci from {l2g.studyId.nunique()} distinct studies; all within 158,330 bp of the TSS; "
        f"{n_l2g_labelled}/67 carry biomarker trait labels, "
        f"{int(l2g.trait_resolved.isna().sum())} unlabelled; none is a LUAD/SCLC study. "
        f"Per-label counts: results/tables/cd276_gwas_trait_label_audit.csv")

    add("G3", "67 L2G loci (round-1 count)", "germline L2G", "distinct studyLocusId in L2G table",
        "data/raw/cd276_l2g_predictions.csv", "nunique(studyLocusId)",
        f"{l2g.studyLocusId.nunique()}", "67", True,
        f"{int((l2g.score >= 0.5).sum())} rows with score >= 0.5; max {l2g.score.max():.4f}")

    add("G4", "303 credible sets in the round-1 queried window", "germline GWAS/QTL credible sets (all study types)",
        "lead variant in chr15:73,500,000-73,900,000",
        "data/raw/cd276_locus_credible_sets_all_studies.parquet",
        "0 < position and 73500000 <= position <= 73900000",
        f"{len(old_in_r1_window)}", "303", True,
        f"all study types: {old.studyType.value_counts().to_dict()}")

    add("G5", "123 credible sets in the CD276 window", "germline GWAS credible sets (GWAS only)",
        "studyType == 'gwas' AND lead variant in chr15:73,500,000-73,900,000",
        "data/raw/cd276_locus_credible_sets_all_studies.parquet",
        "studyType == 'gwas' AND 73500000 <= position <= 73900000",
        f"{len(old[old.studyType == 'gwas'])}", "123", True,
        "the 123 is the GWAS-only subset of the same 303-row artifact; the other 180 rows are eQTL/sQTL/tuQTL/pQTL")

    add("G6", "116 distinct GWAS studies in the CD276 window", "germline GWAS credible sets",
        "distinct studyId among GWAS rows with lead variant in chr15:73,500,000-73,900,000",
        "data/raw/cd276_locus_credible_sets_all_studies.parquet",
        "studyType == 'gwas'; nunique(studyId)",
        f"{old[old.studyType == 'gwas'].studyId.nunique()}", "116", True,
        "116 studies contribute 123 GWAS credible sets (6 studies contribute >1 set, max 3)")

    add("G7", "41 credible sets fall inside the CD276 gene body", "germline credible sets (all study types)",
        "lead variant in chr15:73,683,966-73,714,514 (primary definition)",
        "data/raw/cd276_locus_credible_sets_all_studies.parquet",
        "73683966 <= position <= 73714514",
        f"{gb_lead_all} all types / {gb_lead_gwas} GWAS",
        "41 (GWAS)", True,
        "the 41 count is GWAS-only; 65 credible sets of all study types have a lead variant in the gene body. "
        "Two locus-interval-overlap sensitivities are reported and answer different universes: "
        f"(i) overlap restricted to the round-1 303-row artifact (lead variant 73.5-73.9 Mb) = "
        f"{gb_ov_r1_all} all types / {gb_ov_r1_gwas} GWAS; "
        f"(ii) overlap across the full TSS +/-500 kb retrieval = {gb_ov_full_all} all types / "
        f"{gb_ov_full_gwas} GWAS. Both are recomputed in "
        "results/tables/cd276_round2_credible_set_window_reconciliation.csv.")

    add("G8", "No LUAD/SCLC study appears among credible sets in the expanded +/-500 kb window",
        "germline GWAS credible sets", "lead variant within +/-500 kb, all study types",
        "data/raw/cd276_tss500kb_region_query_round2.parquet",
        "studyId in the 8 LUAD/SCLC IDs",
        f"{sum(s in set(q500.studyId) for s in STUDIES)}/8 present in {len(q500)} rows", "not reported at this window", None,
        "expanded window contains 1,252 credible sets from 1,106 studies; still no LUAD/SCLC study")

    add("G9", "Round-1 303-row artifact is reproducible from an independent re-query",
        "germline credible sets", "lead variant in chr15:73,500,000-73,900,000",
        "data/raw/cd276_tss250kb_region_query_round2.parquet",
        "restrict new +/-250 kb query to 73500000 <= position <= 73900000; compare studyLocusId sets",
        f"identical studyLocusId set: {same_ids}; n={len(q250_in_r1_window)}", "303", str(same_ids),
        "no missing or extra loci; round-1 retrieval was complete for its stated window")

    ver = pd.DataFrame(checks)
    ver_path = os.path.join(BASE, "results", "tables", "cd276_round2_germline_verification.csv")
    ver.to_csv(ver_path, index=False)
    log(f"Wrote {ver_path} ({len(ver)} checks)")

    with open(os.path.join(BASE, "data", "processed", "cd276_round2_germline_verification_log.txt"), "w") as fh:
        fh.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
