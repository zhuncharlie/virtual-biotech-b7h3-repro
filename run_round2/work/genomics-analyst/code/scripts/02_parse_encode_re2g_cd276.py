#!/usr/bin/env python
"""
Panel 4A stream 2: ENCODE-rE2G lung regulatory-element evidence at the CD276 locus.

Revision 2 (2026-10-22): BASE now resolves to THIS run's LIVE workspace, the
input md5 is recorded, and the delivered tables explicitly carry their filter so
that the 77-element within-window distribution is fully re-derivable.

Input (read-only shared staging area; path and md5 written to the summary):
  /mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/
      data/encode_e2g/ENCFF459TXD_lung_e2g_predictions.bed.gz
  Dataset ENCSR985HNP; DNase-only full predictions; biosample = lung.

Two orthogonal selections, kept distinct:
  (a) GENE-LINKED: TargetGeneEnsemblID == ENSG00000103855 (CD276), all distances
  (b) LOCUS-OVERLAPPING: element interval overlaps CD276 TSS +/- 500 kb
      (chr15:73,184,383-74,184,383, GRCh38)

The E2G Score is the ENCODE-rE2G/ABC-style predicted regulatory link score.
It is a regulatory-annotation score, NOT a genetic association statistic.

Outputs
  results/tables/cd276_e2g_regulatory_elements.csv                  (7,332 rows)
  results/tables/cd276_e2g_cd276_linked_all_839.csv                 (839 rows)
  results/tables/cd276_e2g_within_500kb_77_elements.csv             (77 rows)
  results/tables/cd276_e2g_within_window_score_distance_distribution.csv (77 rows)
  results/tables/cd276_e2g_within_window_score_distance_summary.csv
  results/tables/cd276_e2g_summary.csv
  data/processed/cd276_e2g_parse_log.txt
"""
import os
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

# Workspace root = .../work/genomics-analyst (script lives in code/scripts/)
BASE = str(Path(__file__).resolve().parents[2])
SRC = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/"
       "data/encode_e2g/ENCFF459TXD_lung_e2g_predictions.bed.gz")

CD276_ENSG = "ENSG00000103855"
GENE_START, GENE_END, TSS = 73_683_966, 73_714_514, 73_684_383
WIN_LO, WIN_HI = TSS - 500_000, TSS + 500_000
CHR = "chr15"

COLS = ["#chr", "start", "end", "name", "class", "TargetGene", "TargetGeneEnsemblID",
        "TargetGeneTSS", "isSelfPromoter", "CellType", "numTSSEnhGene.Feature",
        "distanceToTSS.Feature", "normalizedDNase_enh.Feature", "normalizedDNase_prom.Feature",
        "numNearbyEnhancers.Feature", "sumNearbyEnhancers.Feature", "ubiquitousExpressedGene.Feature",
        "numCandidateEnhGene.Feature", "3DContactAvgHicTrack2.Feature",
        "3DContactAvgHicTrack2_squared.Feature", "activityEnhDNaseOnlyAvgHicTrack2_squared.Feature",
        "activityPromDNaseOnlyAvgHicTrack2.Feature", "ABCScoreDNaseOnlyAvgHicTrack2.Feature", "Score"]

FILTER_LINKED = ("TargetGeneEnsemblID == ENSG00000103855 (CD276); all element-gene "
                 "link records, no distance restriction")
FILTER_WINDOW = (f"TargetGeneEnsemblID == ENSG00000103855 (CD276) AND element interval "
                 f"overlaps {CHR}:{WIN_LO}-{WIN_HI} (CD276 TSS +/-500 kb); "
                 f"one row per distinct element, 839-of-839 gene-linked records are unique elements")

LOG = []


def log(msg):
    print(msg)
    LOG.append(str(msg))


def md5_file(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs(os.path.join(BASE, "results", "tables"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "data", "processed"), exist_ok=True)

    src_md5 = md5_file(SRC)
    src_size = os.path.getsize(SRC)
    log(f"Source: {SRC}")
    log(f"Source md5: {src_md5}; size_bytes: {src_size}")
    log(f"Selection A (gene-linked): TargetGeneEnsemblID == {CD276_ENSG}")
    log(f"Selection B (locus): #chr == {CHR} and element overlaps [{WIN_LO},{WIN_HI}] (TSS +/-500 kb)")

    kept = []
    n_rows = 0
    n_chunks = 0
    reader = pd.read_csv(
        SRC, sep="\t", header=0, names=COLS, comment=None,
        dtype={"#chr": str, "name": str, "class": str, "TargetGene": str,
               "TargetGeneEnsemblID": str, "isSelfPromoter": str, "CellType": str},
        chunksize=1_000_000, low_memory=False,
    )
    for chunk in reader:
        n_chunks += 1
        n_rows += len(chunk)
        gene_m = chunk["TargetGeneEnsemblID"] == CD276_ENSG
        s = pd.to_numeric(chunk["start"], errors="coerce")
        e = pd.to_numeric(chunk["end"], errors="coerce")
        locus_m = (chunk["#chr"] == CHR) & (s <= WIN_HI) & (e >= WIN_LO)
        m = gene_m | locus_m
        if m.any():
            sub = chunk.loc[m].copy()
            sub["selection_gene_linked"] = gene_m[m].values
            sub["selection_locus_overlap"] = locus_m[m].values
            kept.append(sub)
        if n_chunks % 2 == 0:
            log(f"  processed {n_rows:,} rows; retained so far {sum(len(x) for x in kept):,}")

    df = pd.concat(kept, ignore_index=True)
    log(f"Processed {n_rows:,} data rows in {n_chunks} chunks; retained {len(df):,} rows")

    # numeric coercion
    for c in ["start", "end", "TargetGeneTSS", "distanceToTSS.Feature", "normalizedDNase_enh.Feature",
              "normalizedDNase_prom.Feature", "numNearbyEnhancers.Feature", "sumNearbyEnhancers.Feature",
              "ABCScoreDNaseOnlyAvgHicTrack2.Feature", "Score"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["isSelfPromoter"] = df["isSelfPromoter"].astype(str).str.upper().eq("TRUE")

    # annotate relative to CD276
    df["element_length_bp"] = df["end"] - df["start"]
    df["element_midpoint"] = (df["start"] + df["end"]) / 2
    df["midpoint_distance_to_CD276_TSS_bp"] = df["element_midpoint"] - TSS
    df["overlaps_CD276_gene_body"] = (df["start"] <= GENE_END) & (df["end"] >= GENE_START)
    df["overlaps_TSS_250kb"] = (df["start"] <= TSS + 250_000) & (df["end"] >= TSS - 250_000)
    df["overlaps_TSS_500kb"] = (df["start"] <= TSS + 500_000) & (df["end"] >= TSS - 500_000)
    df["is_CD276_target_gene"] = df["TargetGeneEnsemblID"] == CD276_ENSG

    def scope(r):
        if r["is_CD276_target_gene"] and r["overlaps_TSS_500kb"]:
            return "gene_linked_and_locus_overlap"
        if r["is_CD276_target_gene"]:
            return "gene_linked_outside_locus_window"
        return "locus_overlap_not_linked_to_CD276"
    df["link_scope"] = df.apply(scope, axis=1)
    df["filter"] = np.where(
        df["is_CD276_target_gene"] & df["overlaps_TSS_500kb"], FILTER_WINDOW,
        np.where(df["is_CD276_target_gene"], FILTER_LINKED,
                 f"element interval overlaps {CHR}:{WIN_LO}-{WIN_HI}; target gene != CD276"))

    out_cols = ["#chr", "start", "end", "name", "class", "TargetGene", "TargetGeneEnsemblID",
                "TargetGeneTSS", "isSelfPromoter", "CellType", "normalizedDNase_enh.Feature",
                "normalizedDNase_prom.Feature", "numNearbyEnhancers.Feature", "ABCScoreDNaseOnlyAvgHicTrack2.Feature",
                "Score", "distanceToTSS.Feature", "element_length_bp", "element_midpoint",
                "midpoint_distance_to_CD276_TSS_bp", "overlaps_CD276_gene_body", "overlaps_TSS_250kb",
                "overlaps_TSS_500kb", "is_CD276_target_gene", "selection_gene_linked",
                "selection_locus_overlap", "link_scope", "filter"]
    out = df[out_cols].sort_values(["link_scope", "Score"], ascending=[True, False])
    out_path = os.path.join(BASE, "results", "tables", "cd276_e2g_regulatory_elements.csv")
    out.to_csv(out_path, index=False)
    log(f"Wrote {out_path} ({len(out)} rows)")

    linked = df[df.is_CD276_target_gene].copy()
    locus = df[df.overlaps_TSS_500kb].copy()
    linked_locus = df[df.is_CD276_target_gene & df.overlaps_TSS_500kb].copy()

    # Dedicated, explicitly filtered deliverable tables.
    linked_out_cols = ["#chr", "start", "end", "name", "class", "Score",
                       "distanceToTSS.Feature", "isSelfPromoter", "overlaps_CD276_gene_body",
                       "overlaps_TSS_500kb", "filter"]
    linked_out = linked[linked_out_cols].sort_values("Score", ascending=False)
    linked_path = os.path.join(BASE, "results", "tables", "cd276_e2g_cd276_linked_all_839.csv")
    linked_out.to_csv(linked_path, index=False)
    log(f"Wrote {linked_path} ({len(linked_out)} rows)")

    win_out = linked_locus[linked_out_cols].sort_values("Score", ascending=False)
    win_path = os.path.join(BASE, "results", "tables", "cd276_e2g_within_500kb_77_elements.csv")
    win_out.to_csv(win_path, index=False)
    log(f"Wrote {win_path} ({len(win_out)} rows)")

    dist = linked_locus.sort_values("Score", ascending=False).copy()
    dist_out = pd.DataFrame({
        "element": dist["name"],
        "chr": dist["#chr"],
        "start_grch38": dist["start"].astype("int64"),
        "end_grch38": dist["end"].astype("int64"),
        "class": dist["class"],
        "isSelfPromoter": dist["isSelfPromoter"],
        "e2g_score": dist["Score"],
        "distance_to_CD276_TSS_bp": dist["distanceToTSS.Feature"],
        "filter": FILTER_WINDOW,
    })
    dist_path = os.path.join(BASE, "results", "tables",
                             "cd276_e2g_within_window_score_distance_distribution.csv")
    dist_out.to_csv(dist_path, index=False)
    log(f"Wrote {dist_path} ({len(dist_out)} rows)")

    summ = pd.DataFrame([
        {"metric": "n_elements", "value": len(dist_out), "definition": FILTER_WINDOW},
        {"metric": "e2g_score_median", "value": float(dist_out.e2g_score.median()), "definition": FILTER_WINDOW},
        {"metric": "e2g_score_min", "value": float(dist_out.e2g_score.min()), "definition": FILTER_WINDOW},
        {"metric": "e2g_score_max", "value": float(dist_out.e2g_score.max()), "definition": FILTER_WINDOW},
        {"metric": "distance_to_CD276_TSS_bp_median", "value": float(dist_out.distance_to_CD276_TSS_bp.median()), "definition": FILTER_WINDOW},
        {"metric": "distance_to_CD276_TSS_bp_min", "value": float(dist_out.distance_to_CD276_TSS_bp.min()), "definition": FILTER_WINDOW},
        {"metric": "distance_to_CD276_TSS_bp_max", "value": float(dist_out.distance_to_CD276_TSS_bp.max()), "definition": FILTER_WINDOW},
        {"metric": "distance_to_CD276_TSS_kb_median", "value": float(dist_out.distance_to_CD276_TSS_bp.median()) / 1000.0, "definition": FILTER_WINDOW},
        {"metric": "source_file", "value": SRC, "definition": "read-only shared staging input"},
        {"metric": "source_file_md5", "value": src_md5, "definition": "md5 of the gzipped BED input"},
        {"metric": "source_file_size_bytes", "value": src_size, "definition": "gzipped BED size"},
    ])
    summ_path = os.path.join(BASE, "results", "tables",
                             "cd276_e2g_within_window_score_distance_summary.csv")
    summ.to_csv(summ_path, index=False)
    log(f"Wrote {summ_path} ({len(summ)} metrics)")

    log("")
    log(f"CD276-linked elements: {len(linked)} (unique element names: {linked['name'].nunique()})")
    log(f"Locus-overlapping elements (TSS +/-500 kb): {len(locus)} (unique names: {locus['name'].nunique()})")
    log(f"Both gene-linked and locus-overlapping: {len(linked_locus)} (unique names: {linked_locus['name'].nunique()})")
    log(f"Gene-linked but outside +/-500 kb: {int((df.is_CD276_target_gene & ~df.overlaps_TSS_500kb).sum())}")
    log(f"Locus-overlapping but target gene != CD276: {int((df.overlaps_TSS_500kb & ~df.is_CD276_target_gene).sum())}")
    log(f"Within-window score: median {dist_out.e2g_score.median():.6f} "
        f"(range {dist_out.e2g_score.min():.6f}-{dist_out.e2g_score.max():.6f}), n={len(dist_out)}")
    log(f"Within-window distance to TSS: median {dist_out.distance_to_CD276_TSS_bp.median():.1f} bp "
        f"({dist_out.distance_to_CD276_TSS_bp.median()/1000:.1f} kb; "
        f"range {dist_out.distance_to_CD276_TSS_bp.min():.1f}-{dist_out.distance_to_CD276_TSS_bp.max():.1f} bp)")

    summary = []
    def add(metric, value, notes=""):
        summary.append({"metric": metric, "value": value, "notes": notes})

    add("source_file", os.path.basename(SRC), "ENCODE-rE2G DNase-only lung predictions; dataset ENCSR985HNP")
    add("source_file_full_path", SRC, "read-only shared staging input")
    add("source_file_md5", src_md5, "md5 of the gzipped BED input")
    add("total_rows_in_file", n_rows, "number of element-gene link records scanned")
    add("locus_window", f"{CHR}:{WIN_LO}-{WIN_HI}", "CD276 TSS +/-500 kb, GRCh38")
    add("gene_body", f"{CHR}:{GENE_START}-{GENE_END}", "CD276 GRCh38 gene span")
    add("n_CD276_linked_elements", len(linked), "TargetGeneEnsemblID == ENSG00000103855")
    add("n_CD276_linked_unique_elements", linked["name"].nunique(), "distinct element intervals")
    add("n_locus_overlapping_elements", len(locus), "element interval overlaps TSS +/-500 kb")
    add("n_locus_overlapping_unique_elements", locus["name"].nunique(), "distinct element intervals")
    add("n_both_gene_linked_and_locus", len(linked_locus), "")
    add("n_within_window_unique_elements", linked_locus["name"].nunique(),
        "CD276-linked and within TSS +/-500 kb; the 77-element within-window set")
    add("within_window_score_median", float(dist_out.e2g_score.median()), FILTER_WINDOW)
    add("within_window_score_min", float(dist_out.e2g_score.min()), FILTER_WINDOW)
    add("within_window_score_max", float(dist_out.e2g_score.max()), FILTER_WINDOW)
    add("within_window_distance_to_TSS_bp_median", float(dist_out.distance_to_CD276_TSS_bp.median()), FILTER_WINDOW)
    add("within_window_distance_to_TSS_kb_median", float(dist_out.distance_to_CD276_TSS_bp.median()) / 1000.0, FILTER_WINDOW)
    add("filter_link_table", FILTER_LINKED, "filter recorded in cd276_e2g_cd276_linked_all_839.csv")
    add("filter_window_table", FILTER_WINDOW, "filter recorded in cd276_e2g_within_500kb_77_elements.csv")

    add("class_taxonomy_note",
        "promoter/genic/intergenic",
        "This ENCODE-rE2G file has no 'enhancer' or 'intronic' class labels; distal candidate "
        "elements are labelled 'genic' or 'intergenic' and promoter elements 'promoter'.")
    add("primary_score_threshold", 0.02,
        "Pre-declared primary threshold: above the 95th percentile of CD276-linked scores (0.0148); "
        "isolates the upper tail; sensitivity at 0.05 and 0.1 also reported. Not calibrated to any paper count.")
    for group_name, g in [("CD276_linked", linked), ("locus_overlapping", locus)]:
        for cls, n in g["class"].value_counts(dropna=False).items():
            add(f"{group_name}__n_class_{cls}", int(n), "rows (element-gene links)")
            add(f"{group_name}__n_unique_class_{cls}", int(g.loc[g['class'] == cls, 'name'].nunique()),
                "distinct element intervals")
        add(f"{group_name}__n_isSelfPromoter_TRUE", int(g["isSelfPromoter"].sum()), "rows")
        add(f"{group_name}__score_min", float(g["Score"].min()), "")
        add(f"{group_name}__score_median", float(g["Score"].median()), "")
        add(f"{group_name}__score_mean", float(g["Score"].mean()), "")
        add(f"{group_name}__score_p90", float(g["Score"].quantile(0.90)), "")
        add(f"{group_name}__score_p95", float(g["Score"].quantile(0.95)), "")
        add(f"{group_name}__score_max", float(g["Score"].max()), "")
        for thr in [0.1, 0.05, 0.02, 0.01, 0.005]:
            add(f"{group_name}__n_score_ge_{thr}", int((g["Score"] >= thr).sum()), "rows")
            add(f"{group_name}__n_unique_elements_score_ge_{thr}",
                int(g.loc[g["Score"] >= thr, "name"].nunique()), "distinct element intervals")
        add(f"{group_name}__distanceToTSS_min_bp", float(g["distanceToTSS.Feature"].min()), "")
        add(f"{group_name}__distanceToTSS_median_bp", float(g["distanceToTSS.Feature"].median()), "")
        add(f"{group_name}__distanceToTSS_max_bp", float(g["distanceToTSS.Feature"].max()), "")

    # class x score threshold cross-tab for linked set
    for thr in [0.1, 0.05, 0.02]:
        for cls in sorted(linked["class"].dropna().unique()):
            add(f"CD276_linked__class_{cls}__n_score_ge_{thr}",
                int(((linked["class"] == cls) & (linked["Score"] >= thr)).sum()), "")

    # top elements by score
    top = linked.sort_values("Score", ascending=False).head(20).reset_index(drop=True)
    for i in range(len(top)):
        r = top.loc[i]
        add(f"top_linked_{i+1:02d}", f"{r['name']}|{r['class']}|{r['Score']:.6g}",
            f"distanceToTSS={r['distanceToTSS.Feature']}; isSelfPromoter={r['isSelfPromoter']}")

    sm = pd.DataFrame(summary)
    sm_path = os.path.join(BASE, "results", "tables", "cd276_e2g_summary.csv")
    sm.to_csv(sm_path, index=False)
    log(f"Wrote {sm_path} ({len(sm)} metrics)")

    log("")
    log("CD276-linked class breakdown:")
    log(linked["class"].value_counts(dropna=False).to_string())
    log("")
    log("CD276-linked score distribution:")
    log(linked["Score"].describe(percentiles=[0.5, 0.75, 0.9, 0.95, 0.99]).to_string())
    log("")
    log("CD276-linked counts at thresholds:")
    for thr in [0.1, 0.05, 0.02, 0.01, 0.005]:
        log(f"  Score >= {thr}: {int((linked['Score'] >= thr).sum())}")
    log("")
    log("Locus-overlapping class breakdown:")
    log(locus["class"].value_counts(dropna=False).to_string())
    log("")
    log("Locus-overlapping counts at thresholds:")
    for thr in [0.1, 0.05, 0.02, 0.01, 0.005]:
        log(f"  Score >= {thr}: {int((locus['Score'] >= thr).sum())}")
    log("")
    log("CD276-linked distanceToTSS describe:")
    log(linked["distanceToTSS.Feature"].describe().to_string())
    log(f"CD276-linked elements overlapping gene body: {int(linked['overlaps_CD276_gene_body'].sum())}")
    log(f"CD276-linked elements with isSelfPromoter TRUE: {int(linked['isSelfPromoter'].sum())}")

    with open(os.path.join(BASE, "data", "processed", "cd276_e2g_parse_log.txt"), "w") as fh:
        fh.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
