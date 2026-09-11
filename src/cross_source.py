"""Cross-source comparison of NST kidnapping incidents and ACLED abduction events at state-week (protocol-pilot2 section 7)."""
import pandas as pd
nst = pd.read_pickle('data/nst_clean.pkl'); nst['week'] = nst['Date'] + pd.to_timedelta((5 - nst['Date'].dt.weekday) % 7, unit='D')
n = nst[nst.kidnap == 1].groupby(['State', 'week']).size().rename('nst')
ac = pd.read_pickle('data/panel.pkl')[['admin1', 'week', 'abduction']].rename(columns={'admin1': 'State', 'abduction': 'acled'}); ac['State'] = ac['State'].replace({'Nassarawa': 'Nasarawa'})
weeks = pd.date_range('2018-01-06', '2023-07-01', freq='7D'); ac = ac[ac.week.isin(weeks)].set_index(['State', 'week'])['acled']
df = pd.concat([n, ac], axis=1).fillna(0); df = df[df.index.get_level_values('week').isin(weeks)]
tot = df.groupby('State').sum(); tot['ratio_nst_acled'] = (tot.nst / tot.acled).round(2)
corr = df.groupby('State').apply(lambda g: pd.Series({'pearson': g.nst.corr(g.acled), 'spearman': g.nst.corr(g.acled, method='spearman')}))
both = df.assign(n1=df.nst > 0, a1=df.acled > 0)
dis = both.groupby('State').apply(lambda g: pd.Series({'weeks_acled_only': int((g.a1 & ~g.n1).sum()), 'weeks_nst_only': int((g.n1 & ~g.a1).sum()), 'weeks_both': int((g.a1 & g.n1).sum())}))
out = pd.concat([tot, corr.round(2), dis], axis=1).sort_values('acled', ascending=False); out.to_csv('outputs/p2_cross_source_state.csv')
print('NST', int(tot.nst.sum()), 'ACLED', int(tot.acled.sum()), 'national weekly corr', round(df.groupby('week').sum().corr().iloc[0, 1], 3), 'agreement', round(both.n1.mul(both.a1).sum() / (both.n1 | both.a1).sum(), 3))
