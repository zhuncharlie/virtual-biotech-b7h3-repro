#!/usr/bin/env python
"""
Visium Panel 4E part 1 -- Step 2: load 22 staged sections, spot QC, and build
a combined AnnData.

Outputs
-------
data/raw/visium_sections_all_spots_raw_counts.h5ad     all 54,650 in-tissue
                                                       spots, raw counts, no QC
                                                       (nothing discarded)
data/processed/visium_sections_qc.h5ad                 QC-passed spots; X = raw
                                                       counts; layers['lognorm']
results/tables/visium_section_qc_inventory.csv         per-section inventory
results/tables/visium_spot_qc_metrics.csv              per-spot QC metrics
results/tables/visium_qc_threshold_sensitivity.csv     retained counts at
                                                       alternative thresholds
results/figures/visium_qc_*.png                        QC figures
logs/visium_02_qc_combine.log

QC thresholds (stated a priori, conventional, NOT tuned to any reported count):
  total_counts >= 500 UMIs
  n_genes_by_counts >= 200
  pct_counts_mt <= 20 %
Rationale documented in the report.
"""
import os
import sys
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
import scipy.sparse as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

RUN = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35")
WORK = RUN / "work/single-cell-analyst"
EXTRACT = WORK / "data/raw/visium_extracted"
PROC = WORK / "data/processed"
RAWOUT = WORK / "data/raw"
TABLES = WORK / "results/tables"
FIGS = WORK / "results/figures"
LOGS = WORK / "logs"
for d in (PROC, RAWOUT, TABLES, FIGS, LOGS):
    d.mkdir(parents=True, exist_ok=True)

SECTIONS = [
    "P10_T1", "P10_T2", "P10_T3", "P10_T4",
    "P15_T1", "P15_T2", "P16_T1", "P16_T2",
    "P24_T1", "P24_T2", "P25_T1", "P25_T2",
    "P10_B1", "P10_B2", "P15_B1", "P15_B2",
    "P16_B1", "P16_B2", "P24_B1", "P24_B2",
    "P25_B1", "P25_B2",
]

MIN_COUNTS, MIN_GENES, MAX_MT = 500, 200, 20.0

np.random.seed(42)
LOG = []


def log(msg):
    print(msg, flush=True)
    LOG.append(str(msg))


def histology_of(section):
    return "tumor" if "_T" in section else "adjacent-normal"


def patient_of(section):
    return section.split("_")[0]


def make_gene_names(adata):
    """Symbols as var_names, deterministic uniqueness, keep Ensembl IDs."""
    adata.var["gene_symbols"] = adata.var_names.astype(str)
    adata.var_names_make_unique()
    return adata


def add_qc(adata, section):
    adata.var["mt"] = adata.var_names.astype(str).str.startswith("MT-")
    adata.var["ribo"] = adata.var_names.astype(str).str.startswith(("RPS", "RPL"))
    adata.var["hb"] = adata.var_names.astype(str).str.match(r"^HB[AB]")
    sc.pp.calculate_qc_metrics(
        adata, qc_vars=["mt", "ribo", "hb"], percent_top=None,
        log1p=False, inplace=True,
    )
    return adata


def main():
    # ---- sdrf metadata -------------------------------------------------
    sdrf = pd.read_csv(
        Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/data/visium_raw/E-MTAB-13530.sdrf.txt"),
        sep="\t", low_memory=False)
    mc = ["Source Name", "Characteristics[individual]", "Characteristics[age]",
          "Characteristics[sex]", "Characteristics[disease]",
          "Characteristics[disease staging]", "Characteristics[sampling site]"]
    smeta = sdrf[mc].drop_duplicates("Source Name").set_index("Source Name")

    adatas = []
    spatial_meta = {}
    load_errors = {}

    for section in SECTIONS:
        sec_dir = EXTRACT / section
        log(f"\n=== {section} ===")
        try:
            a = sc.read_visium(sec_dir, library_id=section)
        except Exception as e:
            load_errors[section] = f"{type(e).__name__}: {e}"
            log(f"  LOAD FAILED: {load_errors[section]}")
            raise
        a = make_gene_names(a)
        # raw counts -> int32 (read_visium returns float32)
        a.X = a.X.tocsr()
        a.X.data = np.rint(a.X.data).astype(np.int32)
        assert np.all(a.X.data >= 0)

        # metadata from sdrf
        sm = smeta.loc[section]
        a.obs["section"] = section
        a.obs["patient"] = patient_of(section)
        a.obs["histology"] = histology_of(section)
        a.obs["sampling_site"] = str(sm["Characteristics[sampling site]"])
        a.obs["disease"] = str(sm["Characteristics[disease]"])
        a.obs["stage"] = str(sm["Characteristics[disease staging]"])
        a.obs["age"] = str(sm["Characteristics[age]"])
        a.obs["sex"] = str(sm["Characteristics[sex]"])
        a.obs["individual_sdrf"] = str(sm["Characteristics[individual]"])
        a.obs["array_row"] = a.obs["array_row"].astype(int)
        a.obs["array_col"] = a.obs["array_col"].astype(int)
        a.obs["in_tissue"] = a.obs["in_tissue"].astype(int)

        # QC metrics on the full (raw) spot set
        a = add_qc(a, section)

        # spatial image metadata: keep lowres + scalefactors, drop hires image
        sp = a.uns["spatial"][section]
        hires_path = sec_dir / "spatial" / "tissue_hires_image.png"
        spatial_meta[section] = {
            "library_id": section,
            "scalefactors": {k: float(v) for k, v in sp["scalefactors"].items()},
            "n_spots": int(a.n_obs),
            "array_row_range": [int(a.obs["array_row"].min()), int(a.obs["array_row"].max())],
            "array_col_range": [int(a.obs["array_col"].min()), int(a.obs["array_col"].max())],
            "hires_image_path": str(hires_path),
            "lowres_image_shape": list(sp["images"]["lowres"].shape),
            "spot_diameter_fullres": float(sp["scalefactors"].get("spot_diameter_fullres")),
            "obs_names_unique": True,
        }
        sp["images"].pop("hires", None)
        sp["metadata"] = {"source_image_path": str(hires_path)}
        sp["section_metadata"] = spatial_meta[section]

        # unique obs names across sections (identical array barcodes recur)
        a.obs_names = [f"{section}_{bc}" for bc in a.obs_names]
        log(f"  loaded {a.n_obs} spots x {a.n_vars} genes; "
            f"median counts={a.obs['total_counts'].median():.0f}, "
            f"median genes={a.obs['n_genes_by_counts'].median():.0f}, "
            f"median mito={a.obs['pct_counts_mt'].median():.2f}%")
        adatas.append(a)

    # ---- combined raw (no QC) -----------------------------------------
    log("\n=== concatenating ===")
    raw = ad.concat(adatas, axis=0, join="outer", merge="same",
                    label=None, index_unique=None)
    # rebuild per-section spatial uns (concat cannot merge nested dicts)
    raw.uns["spatial"] = {s: adatas[i].uns["spatial"][s] for i, s in enumerate(SECTIONS)}
    log(f"combined raw: {raw.n_obs} spots x {raw.n_vars} genes")
    log(f"gene names identical across sections: {len({tuple(a.var_names) for a in adatas}) == 1}")

    # ---- QC flags ------------------------------------------------------
    fail_counts = raw.obs["total_counts"] < MIN_COUNTS
    fail_genes = raw.obs["n_genes_by_counts"] < MIN_GENES
    fail_mt = raw.obs["pct_counts_mt"] > MAX_MT
    qc_pass = ~(fail_counts | fail_genes | fail_mt)
    raw.obs["qc_pass"] = qc_pass.values

    reasons = []
    for c, g, m in zip(fail_counts, fail_genes, fail_mt):
        r = []
        if c:
            r.append("low_counts")
        if g:
            r.append("low_genes")
        if m:
            r.append("high_mito")
        reasons.append(";".join(r) if r else "pass")
    raw.obs["qc_fail_reason"] = reasons

    log("\n=== QC results (thresholds: counts>=%d, genes>=%d, mito<=%.0f%%) ==="
        % (MIN_COUNTS, MIN_GENES, MAX_MT))
    log(f"spots before QC: {raw.n_obs}")
    log(f"spots after QC : {int(qc_pass.sum())} ({100*qc_pass.mean():.2f}%)")
    log(f"  fail low_counts: {int(fail_counts.sum())}")
    log(f"  fail low_genes : {int(fail_genes.sum())}")
    log(f"  fail high_mito : {int(fail_mt.sum())}")
    log(f"  fail >1 reason : {int((fail_counts.astype(int)+fail_genes.astype(int)+fail_mt.astype(int) > 1).sum())}")

    # ---- per-spot metrics table ---------------------------------------
    spot_cols = ["section", "patient", "histology", "sampling_site",
                 "total_counts", "n_genes_by_counts", "pct_counts_mt",
                 "pct_counts_ribo", "pct_counts_hb", "array_row", "array_col",
                 "qc_pass", "qc_fail_reason"]
    spot = raw.obs[spot_cols].copy()
    spot.insert(0, "barcode_section", spot.index)
    spot.to_csv(TABLES / "visium_spot_qc_metrics.csv", index=False)
    log(f"saved spot QC metrics: {spot.shape}")

    # ---- threshold sensitivity ----------------------------------------
    grids = [(300, 100, 15.0), (300, 100, 20.0), (500, 200, 20.0),
             (500, 200, 15.0), (500, 200, 30.0), (1000, 300, 20.0)]
    srows = []
    for mc, mg, mm in grids:
        p = ((raw.obs["total_counts"] >= mc) &
             (raw.obs["n_genes_by_counts"] >= mg) &
             (raw.obs["pct_counts_mt"] <= mm))
        srows.append({"min_counts": mc, "min_genes": mg, "max_pct_mt": mm,
                      "spots_retained": int(p.sum()),
                      "pct_retained": round(100 * p.mean(), 2),
                      "primary": (mc, mg, mm) == (MIN_COUNTS, MIN_GENES, MAX_MT)})
    sens = pd.DataFrame(srows)
    sens.to_csv(TABLES / "visium_qc_threshold_sensitivity.csv", index=False)

    # ---- per-section inventory ----------------------------------------
    inv_rows = []
    for s in SECTIONS:
        m = raw.obs["section"] == s
        rm = raw.obs.loc[m]
        qm = rm[rm["qc_pass"]]
        inv_rows.append({
            "section": s,
            "patient": patient_of(s),
            "histology": histology_of(s),
            "sampling_site": rm["sampling_site"].iloc[0],
            "n_spots_raw": int(m.sum()),
            "n_spots_qc": int(len(qm)),
            "pct_retained": round(100 * len(qm) / m.sum(), 2),
            "median_counts_raw": float(rm["total_counts"].median()),
            "median_genes_raw": float(rm["n_genes_by_counts"].median()),
            "median_pct_mt_raw": round(float(rm["pct_counts_mt"].median()), 2),
            "median_counts_qc": float(qm["total_counts"].median()) if len(qm) else np.nan,
            "median_genes_qc": float(qm["n_genes_by_counts"].median()) if len(qm) else np.nan,
            "median_pct_mt_qc": round(float(qm["pct_counts_mt"].median()), 2) if len(qm) else np.nan,
            "n_fail_low_counts": int((rm["qc_fail_reason"].str.contains("low_counts")).sum()),
            "n_fail_low_genes": int((rm["qc_fail_reason"].str.contains("low_genes")).sum()),
            "n_fail_high_mito": int((rm["qc_fail_reason"].str.contains("high_mito")).sum()),
        })
    inv = pd.DataFrame(inv_rows)
    inv.to_csv(TABLES / "visium_section_qc_inventory.csv", index=False)
    log(f"saved inventory: {inv.shape}")
    log(f"tumor raw/QC spots: {inv[inv.histology=='tumor'].n_spots_raw.sum()}/{inv[inv.histology=='tumor'].n_spots_qc.sum()}")
    log(f"adjacent-normal raw/QC spots: {inv[inv.histology=='adjacent-normal'].n_spots_raw.sum()}/{inv[inv.histology=='adjacent-normal'].n_spots_qc.sum()}")

    # ---- save all-spots raw counts (nothing discarded) ----------------
    raw_path = RAWOUT / "visium_sections_all_spots_raw_counts.h5ad"
    raw.write_h5ad(raw_path, compression="gzip")
    log(f"saved ALL raw spots: {raw_path} ({raw_path.stat().st_size/1e6:.1f} MB)")

    # ---- QC-filtered AnnData ------------------------------------------
    qc = raw[qc_pass.values].copy()
    # keep X = raw counts; add log-normalized layer
    qc.layers["lognorm"] = qc.X.copy()
    sc.pp.normalize_total(qc, target_sum=1e4, layer="lognorm")
    sc.pp.log1p(qc, layer="lognorm")
    # convenient per-spot log1p total counts for QC plots
    qc.obs["log1p_total_counts"] = np.log1p(qc.obs["total_counts"])
    qc.uns["visium_section_metadata"] = spatial_meta
    qc.uns["qc_thresholds"] = {"min_total_counts": MIN_COUNTS,
                               "min_genes": MIN_GENES,
                               "max_pct_mt": MAX_MT}
    qc.uns["provenance"] = {
        "accession": "E-MTAB-13530",
        "source": "De Zuani et al. Nat Commun 2024 (PMID 38782901)",
        "space_ranger": "spaceranger-1.1.0, GRCh38-2020-A",
        "n_sections": len(SECTIONS),
    }
    qc_path = PROC / "visium_sections_qc.h5ad"
    qc.write_h5ad(qc_path, compression="gzip")
    log(f"saved QC AnnData: {qc_path} ({qc_path.stat().st_size/1e6:.1f} MB); "
        f"X=raw counts, layers=lognorm")

    # ---- figures -------------------------------------------------------
    plt.rcParams.update({"figure.dpi": 130, "font.size": 8})

    # 1. QC metric distributions by section with thresholds
    fig, axes = plt.subplots(3, 1, figsize=(15, 10), sharex=True)
    order = SECTIONS
    data = raw.obs
    for ax, col, thr, tlabel in [
        (axes[0], "total_counts", MIN_COUNTS, f"min={MIN_COUNTS}"),
        (axes[1], "n_genes_by_counts", MIN_GENES, f"min={MIN_GENES}"),
        (axes[2], "pct_counts_mt", MAX_MT, f"max={MAX_MT:g}%"),
    ]:
        vals = [data.loc[data["section"] == s, col].values for s in order]
        bp = ax.boxplot(vals, positions=range(len(order)), widths=0.7,
                        showfliers=False, patch_artist=True)
        for i, patch in enumerate(bp["boxes"]):
            patch.set_facecolor("#d95f02" if histology_of(order[i]) == "tumor" else "#1b9e77")
            patch.set_alpha(0.7)
        ax.axhline(thr, color="red", ls="--", lw=1, label=tlabel)
        ax.set_ylabel(col)
        ax.legend(loc="upper right", fontsize=7)
        ax.grid(axis="y", alpha=0.3)
    axes[-1].set_xticks(range(len(order)))
    axes[-1].set_xticklabels(order, rotation=90)
    axes[0].set_title("Visium spot QC metrics by section (orange=tumor, green=adjacent-normal)")
    fig.tight_layout()
    fig.savefig(FIGS / "visium_qc_metrics_by_section.png")
    plt.close(fig)

    # 2. raw vs retained per section
    fig, ax = plt.subplots(figsize=(13, 5))
    x = np.arange(len(inv))
    ax.bar(x - 0.2, inv["n_spots_raw"], width=0.4, label="raw", color="#bbbbbb")
    ax.bar(x + 0.2, inv["n_spots_qc"], width=0.4, label="QC-passed", color="#2166ac")
    for i, (r, q) in enumerate(zip(inv["n_spots_raw"], inv["n_spots_qc"])):
        ax.text(i, max(r, q) + 30, f"{100*q/r:.0f}%", ha="center", fontsize=6)
    ax.set_xticks(x)
    ax.set_xticklabels(inv["section"], rotation=90)
    ax.set_ylabel("spots")
    ax.set_title(f"Raw vs QC-retained spots per section (total {inv.n_spots_raw.sum():,} -> {inv.n_spots_qc.sum():,})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGS / "visium_qc_raw_vs_retained.png")
    plt.close(fig)

    # 3. spatial map of retained spots for two representative sections
    reps = ["P10_T1", "P10_B1"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, s in zip(axes, reps):
        m = raw.obs["section"] == s
        xy = raw.obsm["spatial"][m.values]
        passed = raw.obs.loc[m, "qc_pass"].values
        ax.scatter(xy[~passed, 1], xy[~passed, 0], s=2, c="#cccccc", label="failed QC")
        ax.scatter(xy[passed, 1], xy[passed, 0], s=2, c="#b2182b", label="QC-passed")
        ax.invert_yaxis()
        ax.set_aspect("equal")
        ax.set_title(f"{s} ({histology_of(s)})")
        ax.set_xlabel("pxl_col_in_fullres")
        ax.set_ylabel("pxl_row_in_fullres")
        ax.legend(markerscale=4, fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS / "visium_qc_spatial_retained_example.png")
    plt.close(fig)

    # 4. summary table figure
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.axis("off")
    show = inv[["section", "patient", "histology", "n_spots_raw", "n_spots_qc",
                "pct_retained", "median_counts_qc", "median_genes_qc", "median_pct_mt_qc"]]
    t = ax.table(cellText=show.values, colLabels=show.columns, loc="center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(6)
    t.scale(1, 1.1)
    ax.set_title("Visium section QC inventory")
    fig.tight_layout()
    fig.savefig(FIGS / "visium_qc_inventory_table.png")
    plt.close(fig)

    log("saved figures: visium_qc_metrics_by_section.png, visium_qc_raw_vs_retained.png, "
        "visium_qc_spatial_retained_example.png, visium_qc_inventory_table.png")
    log("\n=== FINAL ===")
    log(json.dumps({
        "raw_spots": int(raw.n_obs),
        "qc_spots": int(qc_pass.sum()),
        "tumor_qc": int(inv[inv.histology == "tumor"].n_spots_qc.sum()),
        "normal_qc": int(inv[inv.histology == "adjacent-normal"].n_spots_qc.sum()),
    }))

    with open(LOGS / "visium_02_qc_combine.log", "w") as fh:
        fh.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
