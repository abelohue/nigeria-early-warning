"""Clean the NST spreadsheet: Nigeria 2018+, standardise LGA names, define outcome flags (docs/data-card-pilot2.md)."""
import re, unicodedata, difflib
import pandas as pd

MANUAL = {('Cross River', 'Calabar'): 'Calabar Municipal', ('Zamfara', 'Tsafe'): 'Chafe', ('Ogun', 'EgbadoNorth'): 'Yewa North', ('Kano', 'Kano'): 'Kano Municipal', ('Kogi', 'Kotonkar'): 'Kogi', ('Kebbi', 'Danko Wasagu'): 'Wasagu/Danko', ('Ebonyi', 'AfikpoSo'): 'Afikpo South', ('Ogun', 'EgbadoSouth'): 'Yewa South', ('Ogun', 'Egbado South'): 'Yewa South', ('Ebonyi', 'Afikpo'): 'Afikpo North', ('Niger', 'Kontogur'): 'Kontagora', ('Cross River', 'Yala Cross'): 'Yala', ('Imo', 'Ahizu-Mb'): 'Ahiazu Mbaise'}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower())


def main():
    ref = pd.read_csv('data/lga_ref.csv'); ref['State'] = ref['State'].str.replace(' State', '').replace({'FCT': 'Federal Capital Territory'})
    ref['key'] = ref.LGA.map(norm); ref['skey'] = ref.State.map(norm)
    df = pd.read_excel('data/NST-Main_Sheet.xlsx', 'NST Main Dataset'); df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df[df.Date.notna() & (df.Date >= '2018-01-01')].copy()
    df['State'] = df['State'].replace({'Nassarawa': 'Nasarawa', 'FCT': 'Federal Capital Territory', 'Abuja': 'Federal Capital Territory'})
    df = df[df.State.map(norm).isin(set(ref.skey))].copy()
    mapping = {}
    for (st, lga), _ in df.groupby(['State', 'LGA']).size().items():
        cand = ref[ref.skey == norm(st)]; k = norm(lga); hit = cand[cand.key == k]
        if len(hit): mapping[(st, lga)] = hit.LGA.iloc[0]; continue
        close = difflib.get_close_matches(k, cand.key.tolist(), n=1, cutoff=0.8)
        if close: mapping[(st, lga)] = cand[cand.key == close[0]].LGA.iloc[0]; continue
        pre = cand[cand.key.str.startswith(k[:5])] if len(k) >= 5 else cand.iloc[0:0]
        if len(pre) == 1: mapping[(st, lga)] = pre.LGA.iloc[0]
    mapping.update(MANUAL)
    df['lga_std'] = [mapping.get((s, l)) for s, l in zip(df.State, df.LGA)]
    pd.Series(mapping).to_csv('data/lga_mapping.csv')
    df = df[df.lga_std.notna()].copy()
    df['kidnap'] = (df['Kidnapper (P)'].notna() | df['Kidnapee (V)'].notna()).astype(int)
    df['bh'] = df['Boko Haram (P)'].notna().astype(int)
    df['armed'] = (df['Boko Haram (P)'].notna() | df['Other Armed Actor (P)'].notna() | df['Sectarian Actor (excluding BH) (P)'].notna()).astype(int)
    df['civ_victims'] = pd.to_numeric(df['Civilian (V)'], errors='coerce').fillna(0)
    df['armed_civ'] = ((df.armed == 1) & (df.civ_victims > 0)).astype(int)
    df['deaths'] = pd.to_numeric(df['Total Deaths'], errors='coerce').fillna(0)
    df[['Date', 'State', 'lga_std', 'kidnap', 'bh', 'armed', 'armed_civ', 'civ_victims', 'deaths']].to_pickle('data/nst_clean.pkl')
    print(len(df), 'incidents kept')


if __name__ == '__main__':
    main()
