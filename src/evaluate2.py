"""Pilot 2 evaluation at LGA-week (docs/protocol-pilot2.md). Reuses the pilot 1 machinery."""
import json, os, sys, glob, re
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score, log_loss
from panel2 import FEATURE_GROUPS, HORIZONS
from evaluate import LGB_PARAMS, ece, RNG

QUARTERS = pd.period_range("2020Q1", "2023Q2", freq="Q")
SERIES = {"A": "kidnap", "B": "armed_civ"}
KS = (20, 50)


def feats(groups): return [f for g in groups for f in FEATURE_GROUPS[g]]


def prepare():
    p = pd.read_pickle("data/panel2.pkl")
    for o, col in SERIES.items():
        for h in HORIZONS:
            known = p.groupby("lga")[f"y{o}_h{h}"].shift(h)
            p[f"hist_{col}_h{h}"] = known.groupby(p["lga"]).transform(lambda x: x.rolling(104, min_periods=8).mean())
    return p


def fit_predict(train, test, y, fs, model):
    Xtr, Xte = train[fs], test[fs]
    if model == "logit":
        Xtr = pd.get_dummies(Xtr, columns=["state_cat"] if "state_cat" in fs else [], dtype=float)
        Xte = pd.get_dummies(Xte, columns=["state_cat"] if "state_cat" in fs else [], dtype=float).reindex(columns=Xtr.columns, fill_value=0)
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=3000)); clf.fit(Xtr, train[y]); return clf.predict_proba(Xte)[:, 1]
    clf = lgb.LGBMClassifier(**LGB_PARAMS); clf.fit(Xtr, train[y], categorical_feature=["state_cat"] if "state_cat" in fs else "auto"); return clf.predict_proba(Xte)[:, 1]


def rolling(p, outcome, h, model, fs):
    y = f"y{outcome}_h{h}"; data = p.dropna(subset=[y]); out = []
    for q in QUARTERS:
        start, end = q.start_time, q.end_time
        train = data[data["week"] + pd.Timedelta(weeks=h) < start]
        test = data[(data["week"] + pd.Timedelta(weeks=1) >= start) & (data["week"] + pd.Timedelta(weeks=h) <= end)]
        if not len(test): continue
        pr = test[f"hist_{SERIES[outcome]}_h{h}"].values if model == "hist" else fit_predict(train, test, y, fs, model)
        out.append(pd.DataFrame({"lga": test["lga"].values, "week": test["week"].values, "y": test[y].values, "p": pr, "quarter": str(q)}))
    return pd.concat(out, ignore_index=True).dropna()


def precision_at_k(df, k):
    return float(np.mean([g.nlargest(k, "p")["y"].mean() for _, g in df.groupby("week")]))


def metrics(df):
    y, pr = df["y"].values, np.clip(df["p"].values, 1e-6, 1 - 1e-6)
    m = {"n": int(len(df)), "base_rate": float(y.mean()), "pr_auc": float(average_precision_score(y, pr)), "roc_auc": float(roc_auc_score(y, pr)),
         "brier": float(brier_score_loss(y, pr)), "log_loss": float(log_loss(y, pr)), "ece": float(ece(y, pr))}
    for k in KS: m[f"p_at_{k}"] = precision_at_k(df, k)
    return m


def paired_bootstrap(a, b, n=300):
    weeks = a["week"].unique(); a = a.set_index(["week", "lga"]); b = b.set_index(["week", "lga"]).reindex(a.index)
    d_pr, d_br = [], []
    for _ in range(n):
        sw = RNG.choice(weeks, size=len(weeks), replace=True); ia = a.loc[sw]; ib = b.loc[sw]
        d_pr.append(average_precision_score(ia["y"], ia["p"]) - average_precision_score(ib["y"], ib["p"]))
        d_br.append(brier_score_loss(ia["y"], ia["p"]) - brier_score_loss(ib["y"], ib["p"]))
    return {"d_pr_auc": [float(np.percentile(d_pr, 2.5)), float(np.percentile(d_pr, 97.5))], "d_brier": [float(np.percentile(d_br, 2.5)), float(np.percentile(d_br, 97.5))]}


GROUPS = {"full": ("lags", "neighbours", "season", "state"), "no_neighbours": ("lags", "season", "state"), "no_season": ("lags", "neighbours", "state"), "no_state": ("lags", "neighbours", "season")}


def run_config(outcome, h, model, variant="full"):
    path = f"outputs/p2_pred_{outcome}_h{h}_{model}_{variant}.pkl"
    if os.path.exists(path): return pd.read_pickle(path)
    p = prepare(); df = rolling(p, outcome, h, model, feats(GROUPS[variant])); df.to_pickle(path)
    m = metrics(df); print(f"P2 {outcome} h={h} {model} {variant}: PR-AUC={m['pr_auc']:.3f} (base {m['base_rate']:.4f}) ROC={m['roc_auc']:.3f} Brier={m['brier']:.4f} P@20={m['p_at_20']:.3f} P@50={m['p_at_50']:.3f}", flush=True)
    return df


def summarise():
    results, preds = [], {}
    for f in sorted(glob.glob("outputs/p2_pred_*.pkl")):
        o, h, model, variant = re.match(r"outputs/p2_pred_(\w)_h(\d)_(\w+?)_(\w+)\.pkl", f).groups()
        df = pd.read_pickle(f); preds[(o, int(h), model, variant)] = df
        m = metrics(df); m.update(outcome=o, h=int(h), model=model, variant=variant); results.append(m)
    res = pd.DataFrame(results).sort_values(["outcome", "h", "variant", "model"]); res.to_csv("outputs/p2_results.csv", index=False)
    boots = {}
    for o in ("A", "B"):
        for mdl, base in (("logit", "hist"), ("lgbm", "hist"), ("lgbm", "logit")):
            if (o, 4, mdl, "full") in preds and (o, 4, base, "full") in preds:
                boots[f"{o}_h4_{mdl}_minus_{base}"] = paired_bootstrap(preds[(o, 4, mdl, "full")], preds[(o, 4, base, "full")])
    json.dump(boots, open("outputs/p2_bootstrap_h4.json", "w"), indent=2)
    return res, boots


if __name__ == "__main__":
    if sys.argv[1] == "summarise":
        r, b = summarise(); print(r.round(4).to_string()); print(json.dumps(b, indent=1))
    else:
        run_config(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "full")
