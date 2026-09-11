"""Pilot 2 figures (5 to 7). Run after evaluate2.py summarise and the cross-source script."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
lab = {"hist": "Historical rate", "logit": "Logistic regression", "lgbm": "Gradient boosting"}; col = {"hist": "#64748b", "logit": "#1d4ed8", "lgbm": "#0e7490"}
r1 = pd.read_csv("outputs/results.csv"); r1 = r1[r1.variant == "full"]; r2 = pd.read_csv("outputs/p2_results.csv"); r2 = r2[r2.variant == "full"]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
for o, a in (("A", ax[0]), ("B", ax[1])):
    for m in ("hist", "logit", "lgbm"):
        d1 = r1[(r1.outcome == o) & (r1.model == m) & (r1.h.isin([1, 2, 4]))].sort_values("h"); d2 = r2[(r2.outcome == o) & (r2.model == m)].sort_values("h")
        a.plot(d2.h, d2.pr_auc / d2.base_rate, marker="o", color=col[m], label=f"{lab[m]}, LGA-week (NST)")
        a.plot(d1.h, d1.pr_auc / d1.base_rate, marker="s", ls="--", color=col[m], alpha=.6, label=f"{lab[m]}, state-week (ACLED)")
    a.axhline(1, color="k", lw=.8, ls=":"); a.set_xticks([1, 2, 4]); a.set_xlabel("Forecast horizon (weeks)"); a.grid(alpha=.3); a.set_title(f"Outcome {o}: PR-AUC relative to base rate", fontsize=10)
ax[0].set_ylabel("PR-AUC / base rate"); ax[0].legend(frameon=False, fontsize=7)
plt.tight_layout(); plt.savefig("outputs/figures/fig5_relative_skill_state_vs_lga.png", dpi=160); plt.close()
cs = pd.read_csv("outputs/p2_cross_source_state.csv", index_col=0)
fig, a = plt.subplots(figsize=(6.2, 5.4)); a.scatter(cs.acled, cs.nst, color="#1d4ed8", s=28); m = max(cs.acled.max(), cs.nst.max()); a.plot([0, m], [0, m], "k--", lw=.8)
for s, row in cs.iterrows():
    if row.acled > 50 or row.nst > 90: a.annotate(s.replace("Federal Capital Territory", "FCT"), (row.acled, row.nst), fontsize=7, xytext=(3, 3), textcoords="offset points")
a.set_xlabel("ACLED abduction events, Jan 2018 to Jun 2023"); a.set_ylabel("NST kidnapping incidents, same period"); a.set_title("Two press-based sources, same states, same weeks", fontsize=10); a.grid(alpha=.3)
plt.tight_layout(); plt.savefig("outputs/figures/fig6_cross_source_by_state.png", dpi=160); plt.close()
cs["agree"] = cs.weeks_both / (cs.weeks_both + cs.weeks_acled_only + cs.weeks_nst_only); d = cs.sort_values("agree")
fig, a = plt.subplots(figsize=(10, 4)); a.bar(d.index.str.replace("Federal Capital Territory", "FCT"), d.agree, color="#0e7490"); a.set_ylabel("Share of active weeks both sources record an abduction"); a.set_title("Agreement between NST and ACLED at state-week, 2018 to mid-2023", fontsize=10)
plt.xticks(rotation=90, fontsize=7); plt.tight_layout(); plt.savefig("outputs/figures/fig7_cross_source_agreement.png", dpi=160); plt.close()
