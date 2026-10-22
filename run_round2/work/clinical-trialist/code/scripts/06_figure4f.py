#!/usr/bin/env python
"""Panel 4F: CD276 expression quartile survival in TCGA LUAD PanCancer Atlas.

A: Kaplan-Meier overall survival, Q4 (top quartile) vs Q1 (bottom quartile)
B: Kaplan-Meier disease-specific survival, Q4 vs Q1
C: forest plot of Q4-vs-Q1 hazard ratios for every computable endpoint,
   unadjusted and adjusted for age, sex and AJCC stage group
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

BASE = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/clinical-trialist")
PROC = os.path.join(BASE, "data/processed")
TAB = os.path.join(BASE, "results/tables")
FIG = os.path.join(BASE, "results/figures")
os.makedirs(FIG, exist_ok=True)

co = pd.read_csv(os.path.join(PROC, "tcga_luad_cd276_analysis_cohort.csv"))
res = pd.read_csv(os.path.join(TAB, "tcga_luad_cd276_cox_models.csv"))

plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.8, "font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(12.5, 5.6))
gs = fig.add_gridspec(2, 3, height_ratios=[3.1, 1.0], width_ratios=[1, 1, 1.75],
                      hspace=0.08, wspace=0.30)
colors = {"Q1": "#2c6fbb", "Q4": "#c0392b"}

km_meta = {}
lr_rows = []
for j, ep in enumerate(["OS", "DSS"]):
    ax = fig.add_subplot(gs[0, j])
    raj = fig.add_subplot(gs[1, j], sharex=ax)
    d = co[co[f"{ep}_TIME"].notna() & co[f"{ep}_EVENT"].notna() & (co[f"{ep}_TIME"] > 0)
           & co.expression_quartile.isin(["Q1", "Q4"])]
    lr_p = np.nan
    for qq in ["Q1", "Q4"]:
        s = d[d.expression_quartile == qq]
        km = KaplanMeierFitter().fit(s[f"{ep}_TIME"], s[f"{ep}_EVENT"], label=f"{qq} (n={len(s)})")
        km.plot_survival_function(ax=ax, ci_show=True, ci_alpha=0.12, color=colors[qq],
                                  linewidth=1.8, show_censors=True,
                                  censor_styles={"ms": 3, "marker": "|"})
        km_meta[(ep, qq)] = (len(s), int(s[f"{ep}_EVENT"].sum()))
    a = d[d.expression_quartile == "Q1"]
    b = d[d.expression_quartile == "Q4"]
    lr = logrank_test(a[f"{ep}_TIME"], b[f"{ep}_TIME"],
                      event_observed_A=a[f"{ep}_EVENT"], event_observed_B=b[f"{ep}_EVENT"])
    lr_p = lr.p_value
    lr_rows.append(dict(endpoint=ep, n_q1=len(a), n_q4=len(b),
                        events_q1=int(a[f"{ep}_EVENT"].sum()), events_q4=int(b[f"{ep}_EVENT"].sum()),
                        logrank_statistic=float(lr.test_statistic), logrank_p=float(lr_p)))
    row = res[(res.endpoint == ep) & (res.model == "unadjusted_Q4_vs_Q1")].iloc[0]
    ax.text(0.03, 0.05,
            f"log-rank p = {lr_p:.3g}\nunadjusted HR {row.HR:.2f} "
            f"({row.CI_lower:.2f}-{row.CI_upper:.2f})",
            transform=ax.transAxes, fontsize=7.5, va="bottom")
    ax.set_title(f"{'Overall survival' if ep == 'OS' else 'Disease-specific survival'}",
                 fontsize=9.5, fontweight="bold", loc="left")
    ax.set_xlabel("")
    ax.set_ylabel("Survival probability" if j == 0 else "")
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.25, linewidth=0.5)
    leg = ax.legend(loc="upper right", fontsize=7, frameon=False)
    # risk table
    raj.set_ylim(-0.5, 2.0)
    raj.set_yticks([1.5, 0.5])
    raj.set_yticklabels(["Q1", "Q4"], fontsize=7)
    for i, qq in enumerate(["Q1", "Q4"]):
        s = d[d.expression_quartile == qq]
        for t in [0, 12, 24, 36, 48, 60]:
            n = int((s[f"{ep}_TIME"] >= t).sum())
            raj.text(t, 1.5 - i, str(n), ha="center", va="center", fontsize=6.5)
    raj.set_xlabel("Months since diagnosis")
    raj.set_ylabel("No. at risk", fontsize=6.5)
    raj.grid(axis="x", alpha=0.2, linewidth=0.5)
    for sp in ["top", "right"]:
        raj.spines[sp].set_visible(False)
        ax.spines[sp].set_visible(False)

# ---- forest ---------------------------------------------------------------
sub = gs[:, 2].subgridspec(1, 2, width_ratios=[1.05, 1.45], wspace=0.03)
axf = fig.add_subplot(sub[0, 0])
axt = fig.add_subplot(sub[0, 1], sharey=axf)
order = [("OS", "unadjusted_Q4_vs_Q1", "OS unadjusted"),
         ("OS", "adjusted_Q4_vs_Q1", "OS adjusted"),
         ("DSS", "unadjusted_Q4_vs_Q1", "DSS unadjusted"),
         ("DSS", "adjusted_Q4_vs_Q1", "DSS adjusted"),
         ("PFS", "unadjusted_Q4_vs_Q1", "PFS unadjusted"),
         ("PFS", "adjusted_Q4_vs_Q1", "PFS adjusted"),
         ("DFS", "unadjusted_Q4_vs_Q1", "DFS unadjusted"),
         ("DFS", "adjusted_Q4_vs_Q1", "DFS adjusted")]
ys = np.arange(len(order))[::-1]
for y, (ep, model, lab) in zip(ys, order):
    r = res[(res.endpoint == ep) & (res.model == model)]
    if len(r) == 0 or not np.isfinite(r.iloc[0].HR):
        continue
    r = r.iloc[0]
    col = "#c0392b" if r.p < 0.05 else "#555555"
    axf.plot([r.CI_lower, r.CI_upper], [y, y], color=col, lw=1.4)
    axf.plot(r.HR, y, "o", color=col, ms=5)
    axt.text(0.02, y, f"{r.HR:.2f} ({r.CI_lower:.2f}-{r.CI_upper:.2f})", va="center", fontsize=6.8)
    axt.text(0.55, y, f"{r.p:.3f}", va="center", fontsize=6.8)
    axt.text(0.80, y, f"{int(r.n)}/{int(r.events)}", va="center", fontsize=6.8)

axf.axvline(1, color="black", ls="--", lw=0.8)
axf.set_xscale("log")
axf.set_xlim(0.55, 4.2)
axf.set_xticks([0.6, 1, 1.5, 2, 3])
axf.set_xticklabels(["0.6", "1", "1.5", "2", "3"])
axf.set_yticks(ys)
axf.set_yticklabels([o[2] for o in order], fontsize=7)
axf.set_ylim(-0.7, len(order) - 0.3)
axf.set_xlabel("HR, Q4 vs Q1 (log)")
axf.set_title("Cox models", fontsize=9, fontweight="bold", loc="left", x=0.0)
for sp in ["top", "right"]:
    axf.spines[sp].set_visible(False)
axf.grid(axis="x", alpha=0.25, linewidth=0.5)

axt.set_ylim(-0.7, len(order) - 0.3)
axt.set_xlim(0, 1)
axt.axis("off")
axt.text(0.02, len(order) - 0.35, "HR (95% CI)", fontsize=7, fontweight="bold")
axt.text(0.55, len(order) - 0.35, "p", fontsize=7, fontweight="bold")
axt.text(0.80, len(order) - 0.35, "n/events", fontsize=7, fontweight="bold")

fig.text(0.01, 0.99, "Panel 4F  |  TCGA LUAD PanCancer Atlas (luad_tcga_pan_can_atlas_2018), "
         "CD276 mRNA RSEM, expression quartiles",
         ha="left", va="top", fontsize=8, color="#333333")
fig.text(0.01, 0.012,
         "Quartile cut-points (RSEM): Q1<1746, Q2 1746-2190, Q3 2190-2779, Q4>2779. "
         "Adjusted models: age (per year), sex, AJCC stage group I/II/III/IV. "
         "DSS: n=238 Q1+Q4; DFS: no stage-IV patients with follow-up (stage I/II/III modelled).",
         ha="left", va="bottom", fontsize=6.2, color="#555555")

png = os.path.join(FIG, "fig4f_tcga_luad_cd276_survival.png")
pdf = os.path.join(FIG, "fig4f_tcga_luad_cd276_survival.pdf")
fig.savefig(png, dpi=300, bbox_inches="tight")
fig.savefig(pdf, bbox_inches="tight")
print("wrote", png)
print("wrote", pdf)
print("KM meta:", km_meta)
pd.DataFrame(lr_rows).to_csv(os.path.join(TAB, "tcga_luad_cd276_logrank.csv"), index=False)
print(pd.DataFrame(lr_rows).to_string(index=False))
