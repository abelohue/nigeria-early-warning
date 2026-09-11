# Protocol addendum: pilot study 2, LGA-week forecasting from the Nigeria Security Tracker

**Version 1.0, fixed on 11 September 2026, before any model was trained.** Extends docs/protocol.md; everything not restated here is unchanged.

## 1. Purpose

Re-run the pilot 1 design one administrative level down, using an independent event-level source, and make the first cross-source comparison of reporting between that source and ACLED at state-week.

## 2. Data

- **Source.** Council on Foreign Relations, Nigeria Security Tracker (NST), full incident dataset (14,881 incidents, 29 May 2011 to 30 June 2023), published spreadsheet, CC BY-NC-ND 4.0. Incident-level: date, state, LGA, perpetrator and victim categories, deaths, weapons, locations, sources.
- **Coverage used.** 1 January 2018 to 30 June 2023 (the NST's last week). Nigeria only; incidents coded to Cameroon, Chad and Niger are excluded.
- **LGA standardisation.** NST LGA spellings mapped to the 774-LGA reference list by exact match, then fuzzy match (cutoff 0.8) within state, then 13 manual corrections. Incidents with no LGA or an unmatchable LGA are dropped (232 of 9,554 rows in the period, 2.4%). Mapping file is released.
- **Unit.** LGA-week, 774 LGAs x weeks ending Saturday. Weeks aligned to the ACLED weekly bins used in pilot 1 so the two sources can be compared at state-week.

## 3. Outcomes (LGA s, week t, horizon h in {1, 2, 4})

- **Outcome A (kidnapping).** y = 1 if at least one NST incident in weeks t+1..t+h in LGA s has "Kidnapper" as a perpetrator or a non-zero "Kidnapee" victim count.
- **Outcome B (armed-group violence against civilians).** y = 1 if at least one incident in the window has a Boko Haram, sectarian, or other armed actor as perpetrator and at least one civilian victim. This is closer to the programme's "terrorist violence" outcome than pilot 1's proxy because perpetrator categories are coded; it still includes bandit and communal violence, which is stated wherever it is reported.
- **Descriptive only, not modelled:** incidents with Boko Haram as perpetrator, reported by year and state to show why a named-group outcome is too sparse outside Borno for LGA-week modelling in this period.

Primary horizon h = 4. Horizon 3 is dropped from this addendum to reduce run count; h = 1 and h = 2 are retained for H2.

## 4. Features

As pilot 1, computed from NST counts per LGA: trailing 1, 2, 4, 8, 13, 26, 52-week counts of kidnapping incidents, armed-group civilian incidents, all incidents and deaths; weeks since last event (capped 104); share of trailing 52 weeks with an event; week-of-year sine/cosine. **Neighbourhood** is defined without geometry as the sum of the same trailing counts over all other LGAs in the same state (LGA centroids are not reliably available in the NST). **State identity** replaces LGA identity as the categorical feature, because 774 categories with a 5.5-year panel would overfit; this is a stated design choice.

## 5. Models, folds, metrics

Historical rate, logistic regression, LightGBM, hyperparameters unchanged from pilot 1. Rolling-origin quarterly folds from **2020 Q1 to 2023 Q2** (14 quarters); training rows must have t + h before the fold start. Metrics unchanged (PR-AUC, Brier primary; ROC-AUC, log loss, ECE, precision at K secondary), with **K = 20 and K = 50 LGAs** replacing K = 5 and K = 10, since there are 774 units. Paired bootstrap over weeks, 1,000 resamples.

## 6. Hypotheses

H1 and H2 as in pilot 1, applied at LGA-week. Added:

- **H3.** At LGA-week, the base rate is low enough that forecast skill over base rate (PR-AUC minus base rate) is substantially larger in relative terms than at state-week, and precision at K identifies a set of LGAs at materially elevated risk. This is the resolution hypothesis that pilot 1 could not test.

## 7. Cross-source reporting comparison (descriptive, pre-specified)

Aggregate NST kidnapping incidents to state-week and compare with ACLED "Abduction/forced disappearance" counts for the overlapping period (Jan 2018 to Jun 2023): (i) totals by state; (ii) ratio NST/ACLED by state; (iii) week-level Pearson and Spearman correlation by state; (iv) share of state-weeks where one source records an abduction and the other records none. No correction is attempted; the aim is to characterise disagreement, per the programme's RQ2.

## 8. Decision rule and negative-result policy

As pilot 1 section 9. If gradient boosting again fails to beat logistic regression, that is reported.

## 9. Known limitations, stated in advance

NST is a single press-based source with its own coverage bias and ended in mid-2023, so the evaluation period is short (14 quarters) and includes the COVID period. 94 of 774 LGAs record no NST incident at all in 2018 to 2023; whether that is peace or non-coverage is unknown and is part of what section 7 is meant to expose. Outcome B includes non-terrorist armed groups.

## 10. Deviations

- **11 Sep 2026, after results were inspected but before write-up.** Paired bootstrap run with 300 resamples instead of 1,000 because of execution-time limits on the 225,000-row panel. Interval widths are correspondingly slightly wider; no comparison is near a zero boundary except gradient boosting minus historical on Brier for outcome B, which is reported as such.
