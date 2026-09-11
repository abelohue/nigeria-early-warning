"""Rolling-origin evaluation of historical-rate, logistic and gradient-boosting forecasts.

Implements protocol sections 6 (models), 7 (evaluation), 8 (ablations) and 9 (decision rule).
"""
import json
import warnings
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score, log_loss

from panel import FEATURE_GROUPS, HORIZONS

warnings.filterwarnings("ignore")
RNG = np.random.default_rng(20260910)
LGB_PARAMS = dict(n_estimators=400, learning_rate=0.03, num_leaves=31, min_child_samples=50, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=1)
QUARTERS = pd.period_range("2021Q1", "2026Q3", freq="Q")


def all_features(groups=("lags", "neighbours", "season", "state")):
    return [f for g in groups for f in FEATURE_GROUPS[g]]


def historical_rate(train, test, series, h):
    """P(>=1 event in an h-week window) per state: mean of realised h-week windows that ended at or before
    the forecast week, over the trailing 104 such windows. Vectorised; uses the precomputed column."""
    return test[f"hist_{series}_h{h}"].values


def fit_predict(train, test, y, feats, model):
    Xtr, Xte = train[feats], test[feats]
    if model == "logit":
        Xtr = pd.get_dummies(Xtr, columns=[c for c in feats if c == "state"], dtype=float)
        Xte = pd.get_dummies(Xte, columns=[c for c in feats if c == "state"], dtype=float).reindex(columns=Xtr.columns, fill_value=0)
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))
        clf.fit(Xtr, train[y])
        return clf.predict_proba(Xte)[:, 1]
    clf = lgb.LGBMClassifier(**LGB_PARAMS)
    clf.fit(Xtr, train[y], categorical_feature=[c for c in feats if c == "state"])
    return clf.predict_proba(Xte)[:, 1]


def rolling(panel, outcome, h, model, feats=None, series=None):
    y = f"y{outcome}_h{h}"
    data = panel.dropna(subset=[y])
    preds = []
    for q in QUARTERS:
        start, end = q.start_time, q.end_time
        # target window of a row at week t is t+1..t+h; train rows must have t+h < start of Q
        train = data[data["week"] + pd.Timedelta(weeks=h) < start]
        test = data[(data["week"] + pd.Timedelta(weeks=1) >= start) & (data["week"] + pd.Timedelta(weeks=h) <= end)]
        if len(test) == 0:
            continue
        if model == "hist":
            p = historical_rate(train, test, series, h)
        else:
            p = fit_predict(train, test, y, feats, model)
        preds.append(pd.DataFrame({"admin1": test["admin1"].values, "week": test["week"].values, "y": test[y].values, "p": p, "quarter": str(q)}))
    return pd.concat(preds, ignore_index=True).dropna()


def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    total = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(y[m].mean() - p[m].mean())
    return total


def precision_at_k(df, k):
    """Each week, rank states by p; precision among the top k. Averaged over weeks."""
    vals = []
    for _, g in df.groupby("week"):
        top = g.nlargest(k, "p")
        vals.append(top["y"].mean())
    return float(np.mean(vals))


def metrics(df):
    y, p = df["y"].values, np.clip(df["p"].values, 1e-6, 1 - 1e-6)
    return {
        "n": int(len(df)), "base_rate": float(y.mean()),
        "pr_auc": float(average_precision_score(y, p)), "roc_auc": float(roc_auc_score(y, p)),
        "brier": float(brier_score_loss(y, p)), "log_loss": float(log_loss(y, p)), "ece": float(ece(y, p)),
        "p_at_5": precision_at_k(df, 5), "p_at_10": precision_at_k(df, 10),
    }


def paired_bootstrap(a, b, n=1000):
    """95% interval for metric(a) - metric(b), resampling evaluation weeks."""
    weeks = a["week"].unique()
    a = a.set_index(["week", "admin1"]); b = b.set_index(["week", "admin1"])
    b = b.reindex(a.index)
    d_pr, d_br = [], []
    for _ in range(n):
        sw = RNG.choice(weeks, size=len(weeks), replace=True)
        ia = a.loc[sw]; ib = b.loc[sw]
        d_pr.append(average_precision_score(ia["y"], ia["p"]) - average_precision_score(ib["y"], ib["p"]))
        d_br.append(brier_score_loss(ia["y"], ia["p"]) - brier_score_loss(ib["y"], ib["p"]))
    return {"d_pr_auc": [float(np.percentile(d_pr, 2.5)), float(np.percentile(d_pr, 97.5))], "d_brier": [float(np.percentile(d_br, 2.5)), float(np.percentile(d_br, 97.5))]}


def prepare():
    panel = pd.read_pickle("data/panel.pkl").sort_values(["admin1", "week"])
    series = {"A": "abduction", "B": "civ"}
    for o, col in series.items():
        for h in HORIZONS:
            known = panel.groupby("admin1")[f"y{o}_h{h}"].shift(h)
            panel[f"hist_{col}_h{h}"] = known.groupby(panel["admin1"]).transform(lambda x: x.rolling(104, min_periods=8).mean())
    return panel, series


def run_config(outcome, h, model, variant="full"):
    import os
    path = f"outputs/pred_{outcome}_h{h}_{model}_{variant}.pkl"
    if os.path.exists(path):
        return pd.read_pickle(path)
    panel, series = prepare()
    groups = {"full": ("lags", "neighbours", "season", "state"), "no_neighbours": ("lags", "season", "state"),
              "no_season": ("lags", "neighbours", "state"), "no_state": ("lags", "neighbours", "season")}[variant]
    df = rolling(panel, outcome, h, model, all_features(groups), series[outcome])
    df.to_pickle(path)
    m = metrics(df)
    print(f"{outcome} h={h} {model} {variant}: PR-AUC={m['pr_auc']:.3f} (base {m['base_rate']:.3f}) Brier={m['brier']:.3f} P@5={m['p_at_5']:.3f}", flush=True)
    return df


def summarise():
    import glob, re
    results, preds = [], {}
    for f in sorted(glob.glob("outputs/pred_*.pkl")):
        o, h, model, variant = re.match(r"outputs/pred_(\w)_h(\d)_(\w+?)_(\w+)\.pkl", f).groups()
        df = pd.read_pickle(f); preds[(o, int(h), model, variant)] = df
        m = metrics(df); m.update(outcome=o, h=int(h), model=model, variant=variant); results.append(m)
    pd.DataFrame(results).sort_values(["outcome", "h", "variant", "model"]).to_csv("outputs/results.csv", index=False)
    rows = []
    for (o, h, mdl, var), df in preds.items():
        if h != 4 or var != "full":
            continue
        for yr, g in df.groupby(pd.to_datetime(df["week"]).dt.year):
            m = metrics(g); m.update(outcome=o, model=mdl, year=int(yr)); rows.append(m)
    pd.DataFrame(rows).to_csv("outputs/results_by_year_h4.csv", index=False)
    boots = {}
    for o in ("A", "B"):
        for mdl in ("logit", "lgbm"):
            for base in ("hist", "logit"):
                if mdl == base or (o, 4, mdl, "full") not in preds or (o, 4, base, "full") not in preds:
                    continue
                boots[f"{o}_h4_{mdl}_minus_{base}"] = paired_bootstrap(preds[(o, 4, mdl, "full")], preds[(o, 4, base, "full")])
    json.dump(boots, open("outputs/bootstrap_h4.json", "w"), indent=2)
    return pd.DataFrame(results), boots


if __name__ == "__main__":
    import sys
    if sys.argv[1] == "summarise":
        r, b = summarise(); print(r.to_string()); print(json.dumps(b, indent=1))
    else:
        run_config(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "full")
