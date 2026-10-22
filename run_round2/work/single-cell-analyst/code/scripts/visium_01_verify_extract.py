#!/usr/bin/env python
"""
Visium Panel 4E part 1 -- Step 1: integrity verification and per-section staging.

For each of the 22 E-MTAB-13530 LUAD sections:
  1. Verify the filtered_feature_bc_matrix.h5 (opens with h5py, required 10x
     matrix fields present, internally consistent shapes/indices, non-negative
     integer counts).
  2. Verify the -spatial.tar (readable POSIX tar, all 6 Space Ranger spatial
     files present).
  3. Build <extracted>/<section>/filtered_feature_bc_matrix.h5 and
     <extracted>/<section>/spatial/<spatial files>.
  4. Confirm barcode matching between the filtered matrix and the spatial
     tissue_positions_list.csv.

All failures are logged with the exact error and whether a retry succeeded;
no section is silently dropped. Writes:
  results/tables/visium_file_verification.csv
  results/tables/visium_barcode_matching.csv
  logs/visium_01_verify_extract.log
"""
import os
import sys
import json
import csv
import shutil
import tarfile
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import h5py

import scanpy as sc

RUN = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35")
WORK = RUN / "work/single-cell-analyst"
RAW = Path("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/b7h3_round2_20261021/data/visium_raw")
EXTRACT = WORK / "data/raw/visium_extracted"
TABLES = WORK / "results/tables"
LOGS = WORK / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

SECTIONS = [
    "P10_T1", "P10_T2", "P10_T3", "P10_T4",
    "P15_T1", "P15_T2", "P16_T1", "P16_T2",
    "P24_T1", "P24_T2", "P25_T1", "P25_T2",
    "P10_B1", "P10_B2", "P15_B1", "P15_B2",
    "P16_B1", "P16_B2", "P24_B1", "P24_B2",
    "P25_B1", "P25_B2",
]
REQUIRED_SPATIAL = [
    "aligned_fiducials.jpg",
    "detected_tissue_image.jpg",
    "scalefactors_json.json",
    "tissue_hires_image.png",
    "tissue_lowres_image.png",
    "tissue_positions_list.csv",
]

LOG_LINES = []


def log(msg):
    print(msg, flush=True)
    LOG_LINES.append(str(msg))


def verify_h5(path):
    """Return (ok, info dict, error string)."""
    info = {}
    try:
        with h5py.File(path, "r") as f:
            if "matrix" not in f:
                raise KeyError("no 'matrix' group")
            m = f["matrix"]
            for key in ["barcodes", "data", "indices", "indptr", "shape"]:
                if key not in m:
                    raise KeyError(f"matrix/{key} missing")
            for key in ["id", "name", "feature_type"]:
                if key not in m["features"]:
                    raise KeyError(f"matrix/features/{key} missing")

            n_bar = m["barcodes"].shape[0]
            shape = tuple(int(x) for x in m["shape"][:])
            n_feat, n_bar_shape = shape
            indptr = m["indptr"][:]
            indices = m["indices"][:]
            data = m["data"][:]
            feat_id = m["features/id"][:]
            feat_name = m["features/name"][:]
            feat_type = m["features/feature_type"][:]

            checks = {
                "n_barcodes": n_bar,
                "shape_features": n_feat,
                "shape_barcodes": n_bar_shape,
                "n_features_id": len(feat_id),
                "indptr_len": len(indptr),
                "indptr_last_equals_nnz": int(indptr[-1]) == len(data),
                "indptr_len_ok": len(indptr) == n_bar + 1,
                "indices_max_lt_nfeat": int(indices.max()) < n_feat,
                "data_nonnegative": bool(np.all(data >= 0)),
                "data_integer": bool(np.all(np.mod(data, 1) == 0)),
                "n_nonzero": int(len(data)),
                "feature_type_counts": pd.Series(
                    [x.decode() if isinstance(x, bytes) else str(x) for x in feat_type]
                ).value_counts().to_dict(),
            }
            bad = []
            if n_feat != len(feat_id):
                bad.append("shape[0] != len(features/id)")
            if n_bar != n_bar_shape:
                bad.append("barcodes != shape[1]")
            if len(indptr) != n_bar + 1:
                bad.append("indptr length != n_barcodes+1")
            if not checks["indptr_last_equals_nnz"]:
                bad.append("indptr[-1] != nnz(data)")
            if not checks["indices_max_lt_nfeat"]:
                bad.append("indices out of feature range")
            if not checks["data_nonnegative"] or not checks["data_integer"]:
                bad.append("counts not non-negative integers")
            info.update(checks)
            if bad:
                return False, info, "; ".join(bad)
            return True, info, ""
    except Exception as e:
        return False, info, f"{type(e).__name__}: {e}"


def verify_tar(path):
    try:
        with tarfile.open(path, "r:") as t:
            names = t.getnames()
        base = {os.path.basename(n) for n in names if os.path.basename(n)}
        missing = [f for f in REQUIRED_SPATIAL if f not in base]
        err = "" if not missing else f"missing spatial files: {missing}"
        return (len(missing) == 0), {"tar_members": len(names), "missing": missing,
                                     "members": sorted(base)}, err
    except Exception as e:
        return False, {"error": f"{type(e).__name__}: {e}"}, f"{type(e).__name__}: {e}"


def extract_section(section, h5_src, tar_src):
    """Build EXTRACT/<section>/{filtered_feature_bc_matrix.h5, spatial/*}."""
    sec_dir = EXTRACT / section
    spatial_dir = sec_dir / "spatial"
    if sec_dir.exists():
        shutil.rmtree(sec_dir)
    sec_dir.mkdir(parents=True)
    spatial_dir.mkdir()
    # Copy (do not symlink) so the staged tree is self-contained.
    shutil.copy2(h5_src, sec_dir / "filtered_feature_bc_matrix.h5")
    # -spatial.tar is actually an uncompressed POSIX tar -> tar -xf (NOT -xzf).
    import subprocess
    res = subprocess.run(["tar", "-xf", str(tar_src), "-C", str(spatial_dir)],
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"tar -xf failed rc={res.returncode}: {res.stderr.strip()}")
    # Files may be extracted at top level (expected) -- verify.
    got = {p.name for p in spatial_dir.iterdir() if p.is_file()}
    missing = [f for f in REQUIRED_SPATIAL if f not in got]
    if missing:
        raise RuntimeError(f"spatial extraction missing files: {missing}")
    return got


def read_positions(path):
    """Space Ranger 1.1 tissue_positions_list.csv is headerless."""
    df = pd.read_csv(path, header=None)
    if df.shape[1] == 6:
        df.columns = ["barcode", "in_tissue", "array_row", "array_col",
                      "pxl_row_in_fullres", "pxl_col_in_fullres"]
    elif df.shape[1] == 7:
        # newer format with a leading blank/0 index column
        df = df.iloc[:, 1:]
        df.columns = ["barcode", "in_tissue", "array_row", "array_col",
                      "pxl_row_in_fullres", "pxl_col_in_fullres"]
    else:
        raise ValueError(f"unexpected tissue_positions_list columns: {df.shape[1]}")
    return df


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    EXTRACT.mkdir(parents=True, exist_ok=True)

    ver_rows, bc_rows = [], []

    # sdrf metadata for every section
    sdrf = pd.read_csv(RAW / "E-MTAB-13530.sdrf.txt", sep="\t", low_memory=False)
    meta_cols = ["Source Name", "Characteristics[individual]", "Characteristics[age]",
                 "Characteristics[sex]", "Characteristics[disease]",
                 "Characteristics[disease staging]", "Characteristics[sampling site]"]
    sdrf_meta = sdrf[meta_cols].drop_duplicates("Source Name").set_index("Source Name")

    for section in SECTIONS:
        h5_path = RAW / f"{section}-filtered_feature_bc_matrix.h5"
        tar_path = RAW / f"{section}-spatial.tar"
        row = {"section": section}
        if section in sdrf_meta.index:
            sm = sdrf_meta.loc[section]
            row.update({
                "patient": str(sm["Characteristics[individual]"]).replace("Patient ", "P"),
                "age": sm["Characteristics[age]"],
                "sex": sm["Characteristics[sex]"],
                "disease": sm["Characteristics[disease]"],
                "stage": sm["Characteristics[disease staging]"],
                "sampling_site": sm["Characteristics[sampling site]"],
            })
        else:
            row["meta_error"] = "section not in sdrf"

        log(f"\n=== {section} ===")
        # existence / size
        for label, p in [("h5", h5_path), ("tar", tar_path)]:
            exists = p.exists()
            row[f"{label}_exists"] = exists
            row[f"{label}_size_bytes"] = p.stat().st_size if exists else 0
            if not exists:
                log(f"  FAIL {label} missing: {p}")
                row[f"{label}_error"] = "file missing"

        h5_ok, h5_info, h5_err = verify_h5(h5_path) if h5_path.exists() else (False, {}, "missing")
        row["h5_ok"] = h5_ok
        row["h5_error"] = h5_err
        if h5_info:
            row["n_spots_raw"] = h5_info.get("n_barcodes")
            row["n_genes"] = h5_info.get("shape_features")
            row["n_nonzero"] = h5_info.get("n_nonzero")
            row["feature_type_counts"] = json.dumps(h5_info.get("feature_type_counts", {}))
        log(f"  h5 ok={h5_ok} err='{h5_err}' spots={row.get('n_spots_raw')} genes={row.get('n_genes')}")

        tar_ok, tar_info, tar_err = verify_tar(tar_path) if tar_path.exists() else (False, {}, "missing")
        row["tar_ok"] = tar_ok
        row["tar_error"] = tar_err
        log(f"  tar ok={tar_ok} err='{tar_err}'")

        barcode = {"section": section}
        # Retry logic: one retry for a failed extraction before giving up.
        extracted = False
        for attempt in (1, 2):
            if not (h5_ok and tar_ok):
                break
            try:
                got = extract_section(section, h5_path, tar_path)
                extracted = True
                row["extract_ok"] = True
                row["extract_attempts"] = attempt
                if attempt > 1:
                    log(f"  EXTRACTION RETRY {attempt} SUCCEEDED")
                break
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                log(f"  EXTRACTION attempt {attempt} FAILED: {err}")
                if attempt == 2:
                    row["extract_ok"] = False
                    row["extract_error"] = err
                    row["extract_traceback"] = traceback.format_exc().replace("\n", " | ")
        if not (h5_ok and tar_ok):
            row["extract_ok"] = False
            row["extract_error"] = "skipped: upstream verification failed"
        elif "extract_ok" not in row:
            row["extract_ok"] = False

        # Barcode matching against spatial positions
        if extracted:
            try:
                pos = read_positions(EXTRACT / section / "spatial/tissue_positions_list.csv")
                with h5py.File(h5_path, "r") as f:
                    raw_bc = f["matrix/barcodes"][:]
                mat_bc = pd.Series([
                    x.decode("utf-8") if isinstance(x, (bytes, np.bytes_)) else str(x)
                    for x in raw_bc
                ])
                pos_bc = pos["barcode"].astype(str)
                mat_set, pos_set = set(mat_bc), set(pos_bc)
                in_tissue = pos_bc[pos["in_tissue"] == 1]
                tissue_set = set(in_tissue)
                barcode.update({
                    "n_barcodes_matrix": len(mat_bc),
                    "n_positions_total": len(pos_bc),
                    "n_positions_in_tissue": int((pos["in_tissue"] == 1).sum()),
                    "matrix_bc_not_in_positions": len(mat_set - pos_set),
                    "positions_bc_not_in_matrix": len(pos_set - mat_set),
                    "in_tissue_bc_not_in_matrix": len(tissue_set - mat_set),
                    "matrix_bc_not_in_tissue": len(mat_set - tissue_set),
                    "n_matched_matrix_to_in_tissue": len(mat_set & tissue_set),
                })
                # sample unmatched barcodes (first 10) for the log
                barcode["example_unmatched"] = json.dumps(sorted(mat_set - tissue_set)[:5])
                log("  barcode match: " + json.dumps(
                    {k: barcode[k] for k in barcode if k.startswith(("n_", "matrix_", "positions_", "in_tissue_"))}))
                if barcode["matrix_bc_not_in_positions"] > 0:
                    log(f"  WARNING {barcode['matrix_bc_not_in_positions']} matrix barcodes absent from positions file")
                if barcode["in_tissue_bc_not_in_matrix"] > 0:
                    log(f"  WARNING {barcode['in_tissue_bc_not_in_matrix']} in-tissue positions absent from matrix")
            except Exception as e:
                barcode["barcode_match_error"] = f"{type(e).__name__}: {e}"
                log(f"  BARCODE MATCH FAILED: {e}")
        bc_rows.append(barcode)
        ver_rows.append(row)

    ver = pd.DataFrame(ver_rows)
    vpath = TABLES / "visium_file_verification.csv"
    ver.to_csv(vpath, index=False)
    bc = pd.DataFrame(bc_rows)
    bpath = TABLES / "visium_barcode_matching.csv"
    bc.to_csv(bpath, index=False)

    log("\n=== SUMMARY ===")
    log(f"sections processed: {len(ver)}")
    log(f"h5 ok: {int(ver['h5_ok'].sum())}/{len(ver)}")
    log(f"tar ok: {int(ver['tar_ok'].sum())}/{len(ver)}")
    log(f"extract ok: {int(ver['extract_ok'].sum())}/{len(ver)}")
    log(f"total raw spots: {int(ver['n_spots_raw'].sum())}")
    log(f"saved {vpath}")
    log(f"saved {bpath}")

    with open(LOGS / "visium_01_verify_extract.log", "w") as fh:
        fh.write("\n".join(LOG_LINES) + "\n")

    # Non-zero exit if anything failed, so the caller notices.
    n_fail = int((~ver["h5_ok"]).sum() + (~ver["tar_ok"]).sum() + (~ver["extract_ok"]).sum())
    if n_fail:
        log(f"FAILURES PRESENT: {n_fail}")
        sys.exit(2)


if __name__ == "__main__":
    main()
