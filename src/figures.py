"""Regenerate the figures in outputs/figures from cached predictions and results."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
r = pd.read_csv("outputs/results.csv"); r = r[r.variant == "full"]
lab = {"hist": "Historical rate", "logit": "Logistic regression", "lgbm": "Gradient boosting"}
col = {"hist": "#64748b", "logit": "#1d4ed8", "lgbm": "#0e7490"}
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
for o, a, t in (("A", ax[0], "Outcome A: abduction"), ("B", ax[1], "Outcome B: civilian-targeting violence (proxy)")):
    d = r[r.outcome == o]
    for m in ("hist", "logit", "lgbm"):
        dd = d[d.model == m].sort_values("h"); a.plot(dd.h, dd.pr_auc - dd.base_rate, marker="o", color=col[m], label=lab[m])
    a.set_title(t, fontsize=10); a.set_xlabel("Forecast horizon (weeks)"); a.set_xticks([1, 2, 3, 4]); a.grid(alpha=.3)
ax[0].set_ylabel("PR-AUC minus base rate"); ax[0].legend(frameon=False, fontsize=8)
plt.tight_layout(); plt.savefig("outputs/figures/fig1_skill_by_horizon.png", dpi=160); plt.close()
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for o, a, t in (("A", ax[0], "Outcome A, h = 4"), ("B", ax[1], "Outcome B, h = 4")):
    for m in ("hist", "logit", "lgbm"):
        df = pd.read_pickle(f"outputs/pred_{o}_h4_{m}_full.pkl")
        bins = np.linspace(0, 1, 11); idx = np.clip(np.digitize(df.p, bins) - 1, 0, 9)
        a.plot([df.p[idx == b].mean() for b in range(10)], [df.y[idx == b].mean() for b in range(10)], marker="o", color=col[m], label=lab[m])
    a.plot([0, 1], [0, 1], "k--", lw=.8); a.set_title(t, fontsize=10); a.set_xlabel("Forecast probability"); a.grid(alpha=.3)
ax[0].set_ylabel("Observed frequency"); ax[0].legend(frameon=False, fontsize=8)
plt.tight_layout(); plt.savefig("outputs/figures/fig2_reliability_h4.png", dpi=160); plt.close()
y = pd.read_csv("outputs/results_by_year_h4.csv"); y = y[y.year >= 2021]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
for o, a, t in (("A", ax[0], "Outcome A, h = 4, by year"), ("B", ax[1], "Outcome B, h = 4, by year")):
    d = y[y.outcome == o]
    for m in ("hist", "logit", "lgbm"):
        dd = d[d.model == m].sort_values("year"); a.plot(dd.year, dd.pr_auc, marker="o", color=col[m], label=lab[m])
    dd = d[d.model == "hist"].sort_values("year"); a.plot(dd.year, dd.base_rate, ls=":", color="k", label="Base rate")
    a.set_title(t, fontsize=10); a.grid(alpha=.3)
ax[0].set_ylabel("PR-AUC"); ax[0].legend(frameon=False, fontsize=8)
plt.tight_layout(); plt.savefig("outputs/figures/fig3_by_year_h4.png", dpi=160); plt.close()
p = pd.read_pickle("data/panel.pkl"); s = p.groupby("admin1")["yA_h4"].mean().sort_values()
fig, a = plt.subplots(figsize=(10, 4)); a.bar(s.index, s.values, color="#1d4ed8"); a.set_ylabel("Share of 4-week windows with >= 1 abduction"); a.set_title("Outcome A base rate by state, 2018 to 2026", fontsize=10)
plt.xticks(rotation=90, fontsize=7); plt.tight_layout(); plt.savefig("outputs/figures/fig4_base_rate_by_state.png", dpi=160); plt.close()
