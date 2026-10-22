#!/usr/bin/env python
"""
Extract CAF-source interactions from the LIANA rank_aggregate output and compare
CAF_B7H3_high vs CAF_B7H3_low, for SCLC (panel 4D) and LUAD (panel S5A).

FILTERS (identical for both diseases; timing stated precisely)
  Filter values were fixed in this script at 2026-10-21T14:53:15Z (file mtime),
  i.e. BEFORE the main 1,000-permutation SCLC run started at 14:54:43Z, but
  AFTER a 20-permutation timing probe had been run (probe log written
  14:50:06Z) and its output was available.  They are therefore fixed with
  respect to the main run, NOT with respect to all LIANA output.  The separate
  metadata file results/tables/liana_pre_registered_filters.csv was materialised
  at 14:55:09Z, during the main run.  Values were never changed after seeing
  the main-run results.
  step 0  all    : source is CAF_B7H3_high or CAF_B7H3_low
  step 1  top10  : specificity_rank <= 0.1
                   (LIANA consensus RRA specificity score, 0 = best, so "top 10%"
                   is read on its native 0-1 scale; the empirical percentile is
                   also recorded in specificity_rank_percentile)
  step 2  p<0.01 : cellphone_pvals < 0.01
                   (CellPhoneDB permutation p-value with n_perms=1000; it is the
                   only permutation p-value emitted by the 5-method consensus)
  step 3  >=3 methods : n_methods_finite_rank >= 3
                   (count of the 5 consensus methods - CellPhoneDB, Connectome,
                   log2FC, NATMI, SingleCellSignalR - with a finite score)
  step 4  differential : enriched_high  := high passes steps 1-3 AND low does not
                                      AND specificity_rank_high < specificity_rank_low
                         enriched_low   := low passes steps 1-3 AND high does not
                                      AND specificity_rank_low < specificity_rank_high
                         both / neither otherwise

Outputs
  results/tables/liana_caf_b7h3_sclc_4d.csv
  results/tables/liana_caf_b7h3_luad_s5a.csv
  results/tables/liana_high_vs_low_differential_summary.csv
  results/tables/liana_filter_cascade.csv
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
WORK = os.path.join(ROOT, "work/single-cell-analyst")
TAB = os.path.join(WORK, "results/tables")

SPEC_RANK_CUT = 0.1
PVAL_CUT = 0.01
MIN_METHODS = 3

# method -> (magnitude column, specificity column, both higher-is-better?)
METHODS = {
    "CellPhoneDB": ("lr_means", "cellphone_pvals", (True, False)),
    "Connectome": ("expr_prod", "scaled_weight", (True, True)),
    "log2FC": (None, "lr_logfc", (None, True)),
    "NATMI": ("expr_prod", "spec_weight", (True, True)),
    "SingleCellSignalR": ("lrscore", None, (True, None)),
}

OUT = {"SCLC": "liana_caf_b7h3_sclc_4d.csv", "LUAD": "liana_caf_b7h3_luad_s5a.csv"}


def method_support(res):
    """Per-row: which of the 5 methods have a finite score, and top-decile counts."""
    n = len(res)
    finite = pd.DataFrame(index=res.index)
    top10 = pd.DataFrame(index=res.index)
    for m, (mag, spec, (mag_asc, spec_asc)) in METHODS.items():
        cols = [c for c in (mag, spec) if c is not None]
        vals = res[cols].apply(pd.to_numeric, errors="coerce")
        finite[m] = np.isfinite(vals).any(axis=1)
        # top-decile support uses each method's specificity score when it exists,
        # else its magnitude score; rank 1 = best
        col = spec if spec is not None else mag
        asc = spec_asc if spec is not None else mag_asc
        v = pd.to_numeric(res[col], errors="coerce").values
        r = np.full(n, np.nan)
        ok = np.isfinite(v)
        if ok.sum() > 0:
            rr = rankdata(v[ok], method="average")
            if not asc:  # higher is better -> invert
                rr = rankdata(-v[ok], method="average")
            r[ok] = rr
        pct = (n - r + 1) / n  # 1.0 = best
        top10[m] = pct >= 0.9
    res["n_methods_finite_rank"] = finite.sum(axis=1).astype(int)
    res["methods_finite"] = finite.apply(lambda r: ";".join(r.index[r.values]), axis=1)
    res["n_methods_top10pct"] = top10.sum(axis=1).astype(int)
    res["methods_top10pct"] = top10.apply(lambda r: ";".join(r.index[r.values]), axis=1)
    return res


def process(short, raw_suffix="", out_suffix=""):
    raw_path = os.path.join(TAB, f"liana_raw_{short.lower()}{raw_suffix}.parquet")
    raw = pd.read_parquet(raw_path)
    raw = method_support(raw)
    raw["specificity_rank_percentile"] = raw["specificity_rank"].rank(pct=True, ascending=False)

    caf = raw[raw["source"].isin(["CAF_B7H3_high", "CAF_B7H3_low"])].copy()
    cascade = [("0_all_CAF_source", len(caf),
                 "all interactions whose source is CAF_B7H3_high or CAF_B7H3_low")]
    step = caf
    step = step[step["specificity_rank"] <= SPEC_RANK_CUT]
    cascade.append(("1_top10pct_specificity_rank", len(step),
                    f"specificity_rank <= {SPEC_RANK_CUT}"))
    step = step[step["cellphone_pvals"] < PVAL_CUT]
    cascade.append(("2_pval_lt_0.01", len(step),
                    f"cellphone_pvals < {PVAL_CUT} (CellPhoneDB, {1000} permutations)"))
    step = step[step["n_methods_finite_rank"] >= MIN_METHODS]
    cascade.append(("3_ge3_methods_finite", len(step),
                    f"n_methods_finite_rank >= {MIN_METHODS}"))
    casc_df = pd.DataFrame(cascade, columns=["step", "n_interactions", "rule"])
    casc_df.insert(0, "disease", short)
    casc_df["pct_of_all_caf_source"] = (casc_df["n_interactions"] / casc_df["n_interactions"].iloc[0] * 100).round(2)

    # per group within the CAF-source table
    grp_counts = caf["source"].value_counts().rename_axis("source").reset_index(name="n_all")
    grp_pass = step["source"].value_counts().rename_axis("source").reset_index(name="n_pass_all_filters")
    grp_counts = grp_counts.merge(grp_pass, on="source", how="left").fillna(0)

    # ---------------- high vs low comparison -------------------------------
    keys = ["target", "ligand_complex", "receptor_complex"]
    cols = keys + ["lr_means", "cellphone_pvals", "specificity_rank", "magnitude_rank",
                   "n_methods_finite_rank", "methods_finite", "n_methods_top10pct"]
    hi = caf[caf["source"] == "CAF_B7H3_high"][cols].add_suffix("_high")
    hi = hi.rename(columns={f"{k}_high": k for k in keys})
    lo = caf[caf["source"] == "CAF_B7H3_low"][cols].add_suffix("_low")
    lo = lo.rename(columns={f"{k}_low": k for k in keys})
    cmp = hi.merge(lo, on=keys, how="outer")

    for side, pre in (("high", "_high"), ("low", "_low")):
        cmp[f"passes_{side}"] = (
            (cmp[f"specificity_rank{pre}"] <= SPEC_RANK_CUT)
            & (cmp[f"cellphone_pvals{pre}"] < PVAL_CUT)
            & (cmp[f"n_methods_finite_rank{pre}"] >= MIN_METHODS)
        ).fillna(False)
    cmp["delta_specificity_rank"] = cmp["specificity_rank_low"] - cmp["specificity_rank_high"]
    eps = 1e-9
    cmp["log2_lr_means_high_over_low"] = np.log2(
        (cmp["lr_means_high"].fillna(0) + eps) / (cmp["lr_means_low"].fillna(0) + eps)
    )

    def call(r):
        if r["passes_high"] and not r["passes_low"] and (
                pd.isna(r["specificity_rank_low"]) or r["specificity_rank_high"] < r["specificity_rank_low"]):
            return "enriched_high"
        if r["passes_low"] and not r["passes_high"] and (
                pd.isna(r["specificity_rank_high"]) or r["specificity_rank_low"] < r["specificity_rank_high"]):
            return "enriched_low"
        if r["passes_high"] and r["passes_low"]:
            return "both_pass"
        return "neither"

    cmp["differential_call"] = cmp.apply(call, axis=1)
    # a rank delta only means "more specific in high" when it is negative
    cmp["delta_direction"] = np.sign(cmp["delta_specificity_rank"])

    n_lr = cmp.assign(pair=cmp["ligand_complex"].astype(str) + "^" + cmp["receptor_complex"].astype(str))
    n_up = int((cmp["differential_call"] == "enriched_high").sum())
    n_down = int((cmp["differential_call"] == "enriched_low").sum())
    n_both = int((cmp["differential_call"] == "both_pass").sum())
    n_neither = int((cmp["differential_call"] == "neither").sum())

    # order comparison table: enriched first, then by delta
    order = {"enriched_high": 0, "enriched_low": 1, "both_pass": 2, "neither": 3}
    cmp["_o"] = cmp["differential_call"].map(order)
    cmp = cmp.sort_values(["_o", "delta_specificity_rank"], ascending=[True, False]).drop(columns="_o")

    # write the per-disease CAF-source table with the full comparison attached
    source_tab = caf.merge(
        cmp[keys + ["differential_call", "delta_specificity_rank", "passes_high", "passes_low",
                    "log2_lr_means_high_over_low"]],
        on=keys, how="left")
    source_tab["passes_top10pct"] = source_tab["specificity_rank"] <= SPEC_RANK_CUT
    source_tab["passes_pval"] = source_tab["cellphone_pvals"] < PVAL_CUT
    source_tab["passes_3methods"] = source_tab["n_methods_finite_rank"] >= MIN_METHODS
    source_tab = source_tab.sort_values(
        ["differential_call", "specificity_rank"], na_position="last")
    source_tab.to_csv(
        os.path.join(TAB, OUT[short]) if not out_suffix
        else os.path.join(TAB, f"liana_caf_b7h3_{short.lower()}{out_suffix}.csv"),
        index=False)

    # one row per target / ligand / receptor pair (the differential unit);
    # source_tab has one row per source group, so each pair appears twice
    cmp_out = cmp.copy()
    cmp_out["disease"] = short
    cmp_out.to_csv(os.path.join(TAB, f"liana_pair_level_comparison_{short.lower()}{out_suffix}.csv"),
                   index=False)

    summary = {
        "disease": short,
        "panel": {"SCLC": "4D", "LUAD": "S5A"}[short],
        "n_caf_source_interactions_all": len(caf),
        "n_after_top10pct": int(casc_df.iloc[1]["n_interactions"]),
        "n_after_pval": int(casc_df.iloc[2]["n_interactions"]),
        "n_after_3methods": int(casc_df.iloc[3]["n_interactions"]),
        "n_unique_target_lr_pairs_compared": len(cmp),
        "n_enriched_high": n_up,
        "n_enriched_low": n_down,
        "n_both_pass": n_both,
        "n_neither": n_neither,
        "n_methods_score_all_finite_is_5": bool((caf["n_methods_finite_rank"] == 5).all()),
        "raw_input": os.path.basename(raw_path),
        "caf_definition": "sens_a_median_positive" if raw_suffix else "primary_detection_gt0",
    }
    return source_tab, cmp, casc_df, grp_counts, summary


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-suffix", default="",
                    help="e.g. _sens_a; appended to liana_raw_<disease>")
    ap.add_argument("--out-suffix", default="",
                    help="e.g. _sens_a; appended to every output table name")
    a = ap.parse_args()
    all_sum, all_casc, all_grp = [], [], []
    for short in ["SCLC", "LUAD"]:
        pq = os.path.join(TAB, f"liana_raw_{short.lower()}{a.raw_suffix}.parquet")
        if not os.path.exists(pq):
            print(f"SKIP {short}: {pq} missing")
            continue
        st, cmp, casc, grp, summ = process(short, a.raw_suffix, a.out_suffix)
        all_sum.append(summ)
        all_casc.append(casc)
        grp.insert(0, "disease", short)
        all_grp.append(grp)
        print(f"\n=== {short} ===")
        print(casc.to_string(index=False))
        print(grp.to_string(index=False))
        print({k: v for k, v in summ.items() if k not in ("disease", "panel")})
        print("top enriched_high:")
        print(cmp[cmp.differential_call == "enriched_high"]
              .head(15)[["target", "ligand_complex", "receptor_complex", "lr_means_high",
                         "specificity_rank_high", "cellphone_pvals_high",
                         "delta_specificity_rank"]].to_string(index=False))
        print("top enriched_low:")
        print(cmp[cmp.differential_call == "enriched_low"]
              .head(15)[["target", "ligand_complex", "receptor_complex", "lr_means_low",
                         "specificity_rank_low", "cellphone_pvals_low",
                         "delta_specificity_rank"]].to_string(index=False))

    if all_sum:
        pd.DataFrame(all_sum).to_csv(
            os.path.join(TAB, f"liana_high_vs_low_differential_summary{a.out_suffix}.csv"), index=False)
    if all_casc:
        pd.concat(all_casc, ignore_index=True).to_csv(
            os.path.join(TAB, f"liana_filter_cascade{a.out_suffix}.csv"), index=False)
    if all_grp:
        pd.concat(all_grp, ignore_index=True).to_csv(
            os.path.join(TAB, f"liana_caf_source_group_counts{a.out_suffix}.csv"), index=False)
    print("\ndone")
