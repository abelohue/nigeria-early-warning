# nigeria-early-warning: pilot studies 1 and 2

State-week forecasting of abduction and civilian-targeting violence in Nigeria from ACLED aggregated data, with a pre-registered protocol, a baseline ladder and rolling-origin evaluation.

Waterways Internet Ltd research centre, September 2026. Part of the programme *Explainable Multimodal Machine Learning for Spatiotemporal Early Warning of Terrorist Violence and Kidnapping in Nigeria*.

**Pilot 2 (11 Sep 2026, LGA-week, Nigeria Security Tracker).** At LGA-week the 4-week kidnapping base rate is 4.5%; logistic regression reaches PR-AUC 0.191 (4.3x base) and the top 20 LGAs each week go on to see a kidnapping 29% of the time (6.6x base). Gradient boosting again trails logistic regression. Cross-source check: NST and ACLED agree on whether an abduction happened in a state-week only 19% of the time. Write-up: `docs/research-note-pilot2.md`.

**Pilot 1 headline.** Logistic regression on lagged event counts gives a small, robust improvement over a historical-rate baseline (abductions, 4-week horizon: PR-AUC 0.815 vs 0.793, base rate 0.536). Gradient boosting on the same inputs does worse than both and calibrates worse; the protocol's H1 is not supported. State-level base rates are high enough (Kaduna 85% of 4-week windows) that the useful question is LGA-level, which this data cannot answer. Full write-up: `docs/research-note.md`.

```
docs/
  protocol.md        pre-registered protocol (hypotheses, outcomes, features, models, folds, metrics, decision rule)
  data-card.md       what the data is, what it is not, licensing
  research-note.md   pilot 1 results
  protocol-pilot2.md, data-card-pilot2.md, research-note-pilot2.md   pilot 2
src/
  panel.py           builds the state-week panel, outcomes and backward-looking features
  evaluate.py        models, rolling-origin folds, metrics, paired bootstrap, ablations
  figures.py         pilot 1 figures
  panel2.py, evaluate2.py, figures2.py   pilot 2 (LGA-week, NST)
outputs/
  results.csv, results_by_year_h4.csv, bootstrap_h4.json, p2_results.csv, p2_bootstrap_h4.json, p2_cross_source_state.csv, figures/
data/                place your own ACLED aggregated exports and NST-Main_Sheet.xlsx here (not redistributed); lga_ref.csv and lga_mapping.csv are included
```

## Reproduce

Requires Python 3.10+, pandas, numpy, scikit-learn, lightgbm, matplotlib.

```
pip install pandas numpy scikit-learn lightgbm matplotlib
# put ACLED aggregated CSV exports for Nigeria in data/
python src/panel.py
for o in A B; do for h in 1 2 3 4; do for m in hist logit lgbm; do PYTHONPATH=src python src/evaluate.py $o $h $m; done; done; done
for o in A B; do for v in no_neighbours no_season no_state; do PYTHONPATH=src python src/evaluate.py $o 4 lgbm $v; done; done
PYTHONPATH=src python src/evaluate.py summarise
python src/figures.py
```

## Data

ACLED aggregated data, Nigeria, weeks ending 6 Jan 2018 to 29 Aug 2026, exported 10 Sep 2026 from acleddata.com under a registered account. Raw exports are not included; see `docs/data-card.md`.

## Pilot 2 reproduce

```
# place NST-Main_Sheet.xlsx in data/ (CFR Nigeria Security Tracker, via the Internet Archive copy of the tracker page)
python src/clean_nst.py          # -> data/nst_clean.pkl and data/lga_mapping.csv
python src/panel2.py
for o in A B; do for h in 1 2 4; do for m in hist logit lgbm; do PYTHONPATH=src python src/evaluate2.py $o $h $m; done; done; done
for o in A B; do for v in no_neighbours no_season no_state; do PYTHONPATH=src python src/evaluate2.py $o 4 lgbm $v; done; done
PYTHONPATH=src python src/evaluate2.py summarise
python src/cross_source.py && python src/figures2.py
```
