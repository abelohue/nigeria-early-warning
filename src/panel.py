"""Build the state-week panel, outcomes and features from ACLED aggregated exports.

Implements protocol sections 3 (data), 4 (outcomes) and 5 (features). Every feature
uses information from week t or earlier only.
"""
import glob
import numpy as np
import pandas as pd

HORIZONS = (1, 2, 3, 4)
LAGS = (1, 2, 4, 8, 13, 26, 52)
EXCLUDE_ADMIN1 = {"South Atlantic Ocean"}


def load_raw(pattern="data/ACLED*.csv"):
    frames = [pd.read_csv(f, encoding="utf-8-sig", thousands=",") for f in sorted(glob.glob(pattern))]
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(["week", "admin1", "event_type", "sub_event_type"])
    df["week"] = pd.to_datetime(df["week"])
    df = df[~df["admin1"].isin(EXCLUDE_ADMIN1)].copy()
    df = df[df["week"] >= "2018-01-06"]
    return df


def weekly_counts(df):
    """Collapse to state-week with one column per outcome-relevant series."""
    pv = df["disorder_type"].eq("Political violence")
    df = df.assign(
        abduction=df["sub_event_type"].eq("Abduction/forced disappearance") * df["events"],
        vac=df["event_type"].eq("Violence against civilians") * df["events"],
        battles=df["event_type"].eq("Battles") * df["events"],
        explosions=df["event_type"].eq("Explosions/Remote violence") * df["events"],
        pv_events=pv * df["events"],
        pv_fatalities=pv * df["fatalities"],
    )
    g = df.groupby(["admin1", "week"])[["abduction", "vac", "battles", "explosions", "pv_events", "pv_fatalities"]].sum()
    states = sorted(df["admin1"].unique())
    weeks = pd.date_range(df["week"].min(), df["week"].max(), freq="7D")
    idx = pd.MultiIndex.from_product([states, weeks], names=["admin1", "week"])
    panel = g.reindex(idx, fill_value=0).reset_index()
    panel["civ"] = panel["vac"] + panel["explosions"]  # outcome B series
    cent = df.groupby("admin1")[["centroid_latitude", "centroid_longitude"]].first()
    return panel, cent


def neighbours(cent, k=4):
    lat = np.radians(cent["centroid_latitude"].values)
    lon = np.radians(cent["centroid_longitude"].values)
    d = np.arccos(np.clip(np.sin(lat)[:, None] * np.sin(lat)[None, :] + np.cos(lat)[:, None] * np.cos(lat)[None, :] * np.cos(lon[:, None] - lon[None, :]), -1, 1))
    np.fill_diagonal(d, np.inf)
    order = np.argsort(d, axis=1)[:, :k]
    return {cent.index[i]: [cent.index[j] for j in order[i]] for i in range(len(cent))}


def add_outcomes(panel):
    panel = panel.sort_values(["admin1", "week"]).copy()
    for series, name in (("abduction", "A"), ("civ", "B")):
        for h in HORIZONS:
            fut = panel.groupby("admin1")[series].transform(lambda s: s[::-1].rolling(h, min_periods=h).sum()[::-1].shift(-1))
            panel[f"y{name}_h{h}"] = (fut >= 1).astype("float").where(fut.notna())
    return panel


def add_features(panel, cent):
    panel = panel.sort_values(["admin1", "week"]).copy()
    g = panel.groupby("admin1")
    base = ["abduction", "vac", "battles", "explosions", "pv_events", "pv_fatalities", "civ"]
    for col in base:
        for lag in LAGS:
            panel[f"{col}_l{lag}"] = g[col].transform(lambda s: s.rolling(lag, min_periods=1).sum())
    for col, name in (("abduction", "abd"), ("civ", "civ")):
        occurred = panel[col].gt(0)
        wk = panel.groupby("admin1").cumcount()
        last = wk.where(occurred).groupby(panel["admin1"]).ffill()
        panel[f"weeks_since_{name}"] = (wk - last).fillna(104).clip(upper=104)
        panel[f"{name}_share52"] = g[col].transform(lambda s: s.gt(0).rolling(52, min_periods=1).mean())
    nb = neighbours(cent)
    for col in ("abduction", "civ", "pv_events"):
        for lag in (4, 13):
            src = panel.pivot(index="week", columns="admin1", values=f"{col}_l{lag}")
            nbsum = pd.DataFrame({s: src[nb[s]].sum(axis=1) for s in src.columns})
            panel[f"nb_{col}_l{lag}"] = nbsum.stack().reindex(pd.MultiIndex.from_frame(panel[["week", "admin1"]])).values
    woy = panel["week"].dt.isocalendar().week.astype(float)
    panel["woy_sin"] = np.sin(2 * np.pi * woy / 52.0)
    panel["woy_cos"] = np.cos(2 * np.pi * woy / 52.0)
    panel["state"] = panel["admin1"].astype("category")
    return panel


FEATURE_GROUPS = {
    "lags": [f"{c}_l{l}" for c in ("abduction", "vac", "battles", "explosions", "pv_events", "pv_fatalities") for l in LAGS]
    + ["weeks_since_abd", "weeks_since_civ", "abd_share52", "civ_share52"],
    "neighbours": [f"nb_{c}_l{l}" for c in ("abduction", "civ", "pv_events") for l in (4, 13)],
    "season": ["woy_sin", "woy_cos"],
    "state": ["state"],
}


def build(pattern="data/ACLED*.csv"):
    raw = load_raw(pattern)
    panel, cent = weekly_counts(raw)
    panel = add_outcomes(panel)
    panel = add_features(panel, cent)
    return panel


if __name__ == "__main__":
    p = build()
    p.to_pickle("data/panel.pkl")
    print(p.shape, p["week"].min().date(), p["week"].max().date(), p["admin1"].nunique())
    for h in HORIZONS:
        print(f"h={h}  base rate A={p[f'yA_h{h}'].mean():.3f}  B={p[f'yB_h{h}'].mean():.3f}")
