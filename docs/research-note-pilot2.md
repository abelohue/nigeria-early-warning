# Pilot study 2: LGA-week forecasting of kidnapping and armed-group violence in Nigeria from the Nigeria Security Tracker, with a cross-source reporting comparison against ACLED

Waterways Internet Ltd research centre. Research note, 11 September 2026. Protocol addendum fixed before modelling (docs/protocol-pilot2.md). Companion to pilot 1 (docs/research-note.md).

## Summary

Pilot 1 showed that at state-week resolution, abduction risk in Nigeria is close to saturated: most state-months contain an abduction, so a forecast tells a security committee little. Pilot 2 re-runs the same protocol one administrative level down, using the Council on Foreign Relations' Nigeria Security Tracker (NST), an independent, press-based, LGA-coded incident dataset that ran from 2011 to mid-2023, and then compares the NST and ACLED at state-week over their overlapping five and a half years.

Four findings.

1. **At LGA-week the problem becomes a real rare-event forecasting task, and forecasts are informative.** The four-week base rate for a kidnapping incident is 4.5% per LGA-week (against 54% per state-week). Logistic regression reaches PR-AUC 0.191, 4.3 times the base rate, with ROC-AUC 0.78 and expected calibration error 0.005. Ranking all 768 LGAs each week by forecast probability, the top 20 experience a kidnapping in the following four weeks 29% of the time, 6.6 times the base rate. At state level the equivalent lift was 1.7. **H3 is supported.**
2. **H1 is again not supported.** Gradient boosting beats the historical-rate baseline at LGA level (unlike at state level), but it is still below logistic regression on PR-AUC and Brier for both outcomes, with paired-bootstrap intervals excluding zero. Given only lagged counts of the same source, a regularised linear model is the best of the three at both resolutions.
3. **Skill falls with lead time (H2 supported) but stays well above chance at four weeks**, which is the horizon a local security committee can plan around.
4. **The two sources disagree far more than the forecasting results might suggest.** Over January 2018 to June 2023 the NST records 2,435 kidnapping incidents and ACLED 1,838 abduction events. Nationally the weekly series correlate at 0.51; within states the correlation is 0.05 to 0.30. Of all state-weeks in which either source records an abduction, both record one in only 19%. The NST counts more than ACLED in 30 of 37 states but fewer in Zamfara, Borno and Sokoto, the three states hardest to report from. A model trained on either source alone is learning that source's coverage as much as the violence beneath it. This is the programme's RQ2, now with numbers attached.

## Data

NST full dataset, 14,881 incidents, 29 May 2011 to 30 June 2023, published under CC BY-NC-ND 4.0. Nigeria only, 1 January 2018 onward: 9,554 incidents, of which 9,322 (97.6%) were mapped to one of the 774 reference LGAs (exact match, then fuzzy match within state, then 13 manual corrections; 232 rows with no locatable LGA were dropped and the mapping file is released). Panel: 768 LGAs with reference names x 287 weeks aligned to ACLED's Saturday-ending bins.

Outcome A, kidnapping: an incident with "Kidnapper" as perpetrator or a non-zero kidnapee count (2,435 incidents in the period). Outcome B, armed-group violence against civilians: an incident with a Boko Haram, sectarian or other armed actor as perpetrator and at least one civilian victim (2,324 incidents). Boko Haram as a named perpetrator falls from 167 incidents in 2018 to 38 in the first half of 2023 and is concentrated in Borno; it is reported descriptively and not modelled at LGA-week.

Features are the pilot 1 set computed from NST counts, with two stated changes: neighbourhood is the sum over other LGAs in the same state (no reliable LGA centroids in the NST), and the categorical identity feature is the state, not the LGA. Rolling-origin quarterly folds, 2020 Q1 to 2023 Q2 (14 quarters). Precision at K uses K = 20 and K = 50.

## Results

### Primary horizon, h = 4, pooled

| Outcome | Model | Base rate | PR-AUC | PR-AUC / base | ROC-AUC | Brier | ECE | P@20 | P@50 |
|---|---|---|---|---|---|---|---|---|---|
| A kidnapping | Historical rate | 0.0445 | 0.155 | 3.5 | 0.746 | 0.0404 | 0.015 | 0.280 | 0.207 |
| A kidnapping | Logistic regression | 0.0445 | **0.191** | **4.3** | **0.781** | **0.0394** | **0.005** | **0.292** | **0.220** |
| A kidnapping | Gradient boosting | 0.0445 | 0.166 | 3.7 | 0.765 | 0.0402 | 0.009 | 0.273 | 0.204 |
| B armed-group violence | Historical rate | 0.0428 | 0.165 | 3.8 | 0.777 | 0.0385 | 0.014 | 0.271 | 0.220 |
| B armed-group violence | Logistic regression | 0.0428 | **0.209** | **4.9** | 0.792 | **0.0376** | **0.007** | **0.294** | 0.215 |
| B armed-group violence | Gradient boosting | 0.0428 | 0.189 | 4.4 | **0.796** | 0.0383 | 0.011 | 0.267 | 0.207 |

### Paired bootstrap, h = 4 (95% interval over evaluation weeks, 300 resamples)

| Comparison | Outcome | PR-AUC difference | Brier difference |
|---|---|---|---|
| Logistic minus historical | A | [+0.030, +0.042] | [-0.0012, -0.0008] |
| Gradient boosting minus historical | A | [+0.006, +0.018] | [-0.0005, -0.0000] |
| Gradient boosting minus logistic | A | [-0.031, -0.019] | [+0.0005, +0.0009] |
| Logistic minus historical | B | [+0.033, +0.054] | [-0.0012, -0.0006] |
| Gradient boosting minus historical | B | [+0.015, +0.034] | [-0.0005, +0.0001] |
| Gradient boosting minus logistic | B | [-0.029, -0.010] | [+0.0004, +0.0010] |

### Horizons (H2)

For kidnapping, PR-AUC relative to base rate for logistic regression is 5.5 at one week, 4.9 at two and 4.3 at four; ROC-AUC 0.79, 0.79, 0.78. For armed-group violence, 8.5, 6.4 and 4.9. Skill decays with lead time, as hypothesised, and remains far above the state-week values at every horizon (figure 5).

### Ablations (gradient boosting, h = 4)

Removing state identity costs the most for kidnapping (PR-AUC 0.166 to 0.160; P@20 0.273 to 0.251); removing the same-state neighbourhood or seasonality changes PR-AUC by less than 0.003 for A. For outcome B, removing neighbourhood or seasonality slightly improves PR-AUC (0.189 to 0.191 and 0.195), so neither carries signal in this crude form. Real neighbourhood, defined by shared borders and roads, is a later study and needs geometry the NST lacks.

### Cross-source comparison, state-week, January 2018 to June 2023

| | NST kidnapping incidents | ACLED abduction events |
|---|---|---|
| National total | 2,435 | 1,838 |
| Ratio NST / ACLED, median across states (IQR) | 1.44 (1.14 to 1.56) | |
| National weekly correlation | 0.51 | |
| Within-state weekly correlation, range | 0.05 to 0.30 | |
| Share of "active" state-weeks (either source records one) where both do | 19% | |
| States where ACLED counts more than the NST | Zamfara (147 vs 118), Borno (96 vs 68), Sokoto (54 vs 40), and four others | |

Agreement is lowest in the South-East and South-South (Cross River, Anambra, Ebonyi: 3 to 4% of active weeks) and highest in Kaduna (41%). 89 of 768 LGAs have no NST incident of any kind in five and a half years; the NST's own methodology note says under-reporting in remote areas is expected, and Nigeria Watch reports the same pattern for its own data.

## Interpretation

The resolution result is clear-cut. At state level, forecasting mostly reproduces the map of where violence already is. At LGA level, the same modest models identify a short list of areas each week that go on to experience kidnapping at six to seven times the average rate. That is a product a local security committee could act on, and it is obtainable from a single press-based source with a regularised linear model.

The cross-source result matters more for the programme. Two careful, independent monitors of Nigerian press disagree on the week-by-week occurrence of abductions in the same state four times out of five. Some of that is definitional (NST "kidnapping" versus ACLED "abduction/forced disappearance"), some is date assignment, but the geographic pattern, with ACLED ahead in the North-West and Borno and the NST ahead in the South, points to differences in which outlets each monitor reads. Any forecast trained on one source inherits that source's blind spots, and a forecast that looks well calibrated against its own source can still be wrong about the world. The programme's plan to model reporting explicitly (RQ2), and to use the NBS household survey as an external check on both event sources, is not a refinement; on this evidence it is a precondition for trusting anything the models say.

On modelling, the same pattern as pilot 1: with lagged counts of one source as inputs, gradient boosting does not beat a regularised linear model. It now beats the naive baseline, so non-linearity is worth something at LGA level, but the additional signal the programme is looking for is not in the same series lagged further. It has to come from other modalities and from combining sources.

## Limitations

The NST ended in June 2023, so the evaluation window is 14 quarters and does not cover the 2024 to 2026 escalation. Single source for the LGA panel; the ACLED comparison is at state level only because ACLED event-level data was not available to this study. Outcome B includes bandit and communal violence, not only groups designated as terrorist. Neighbourhood is same-state, not geographic. Bootstrap intervals use 300 resamples for compute reasons (protocol specified 1,000; recorded as a deviation).

## What comes next

1. Geometry: LGA boundaries and road networks (GRID3, OpenStreetMap) to replace same-state neighbourhood with border- and road-based neighbourhood, and to test whether that is where the extra signal lives.
2. A second LGA-level source (Nigeria Watch, 2006 to present) to extend coverage past 2023 and to make the reporting comparison at LGA level rather than state level.
3. Reporting-completeness modelling: treat the NST and ACLED as two noisy observers of a latent process and estimate coverage by state and period, then test whether forecasts conditioned on coverage are better calibrated (H2 of the programme).
4. ACLED event-level data on enrolment, giving a third source at LGA level.

## Reproducibility

`python src/panel2.py` builds the LGA-week panel from `data/nst_clean.pkl` (produced by the cleaning steps documented in docs/data-card-pilot2.md, with the LGA mapping in `data/lga_mapping.csv`). `PYTHONPATH=src python src/evaluate2.py <outcome> <h> <model> [variant]` runs one configuration; `summarise` builds the tables. Figures 5 to 7 come from `src/figures2.py`.
