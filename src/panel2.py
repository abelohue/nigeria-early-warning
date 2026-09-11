"""Pilot 2: LGA-week panel from the cleaned Nigeria Security Tracker (docs/protocol-pilot2.md)."""
import numpy as np
import pandas as pd

HORIZONS = (1, 2, 4)
LAGS = (1, 2, 4, 8, 13, 26, 52)


def build():
    ev = pd.read_pickle("data/nst_clean.pkl")
    ref = pd.read_csv("data/lga_ref.csv")
    ref["State"] = ref["State"].str.replace(" State", "").replace({"FCT": "Federal Capital Territory"})
    # align to ACLED weekly bins (weeks end Saturday): week label = the Saturday on or after the date
    ev["week"] = ev["Date"] + pd.to_timedelta((5 - ev["Date"].dt.weekday) % 7, unit="D")
    ev["all_inc"] = 1
    g = ev.groupby(["lga_std", "week"])[["kidnap", "armed_civ", "bh", "all_inc", "deaths"]].sum()
    weeks = pd.date_range("2018-01-06", "2023-07-01", freq="7D")
    lgas = ref["LGA"].tolist()
    idx = pd.MultiIndex.from_product([lgas, weeks], names=["lga", "week"])
    p = g.reindex(idx, fill_value=0).reset_index()
    p = p.merge(ref[["LGA", "State"]].rename(columns={"LGA": "lga", "State": "state"}), on="lga", how="left")
    p = p.sort_values(["lga", "week"]).reset_index(drop=True)
    # outcomes
    for series, name in (("kidnap", "A"), ("armed_civ", "B")):
        for h in HORIZONS:
            fut = p.groupby("lga")[series].transform(lambda s: s[::-1].rolling(h, min_periods=h).sum()[::-1].shift(-1))
            p[f"y{name}_h{h}"] = (fut >= 1).astype("float").where(fut.notna())
    # features
    gl = p.groupby("lga")
    for col in ("kidnap", "armed_civ", "all_inc", "deaths"):
        for lag in LAGS:
            p[f"{col}_l{lag}"] = gl[col].transform(lambda s: s.rolling(lag, min_periods=1).sum())
    for col, name in (("kidnap", "kid"), ("armed_civ", "civ")):
        occurred = p[col].gt(0)
        wk = p.groupby("lga").cumcount()
        last = wk.where(occurred).groupby(p["lga"]).ffill()
        p[f"weeks_since_{name}"] = (wk - last).fillna(104).clip(upper=104)
        p[f"{name}_share52"] = gl[col].transform(lambda s: s.gt(0).rolling(52, min_periods=1).mean())
    # same-state neighbourhood: state total minus own
    for col in ("kidnap", "armed_civ", "all_inc"):
        for lag in (4, 13):
            tot = p.groupby(["state", "week"])[f"{col}_l{lag}"].transform("sum")
            p[f"nb_{col}_l{lag}"] = tot - p[f"{col}_l{lag}"]
    woy = p["week"].dt.isocalendar().week.astype(float)
    p["woy_sin"] = np.sin(2 * np.pi * woy / 52.0)
    p["woy_cos"] = np.cos(2 * np.pi * woy / 52.0)
    p["state_cat"] = p["state"].astype("category")
    return p


FEATURE_GROUPS = {
    "lags": [f"{c}_l{l}" for c in ("kidnap", "armed_civ", "all_inc", "deaths") for l in LAGS] + ["weeks_since_kid", "weeks_since_civ", "kid_share52", "civ_share52"],
    "neighbours": [f"nb_{c}_l{l}" for c in ("kidnap", "armed_civ", "all_inc") for l in (4, 13)],
    "season": ["woy_sin", "woy_cos"],
    "state": ["state_cat"],
}

if __name__ == "__main__":
    p = build()
    p.to_pickle("data/panel2.pkl")
    print(p.shape, p.lga.nunique(), p.week.min().date(), p.week.max().date())
    for h in HORIZONS:
        print(f"h={h} base A={p[f'yA_h{h}'].mean():.4f} B={p[f'yB_h{h}'].mean():.4f}")
