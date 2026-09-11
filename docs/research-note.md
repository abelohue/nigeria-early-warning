# Pilot study 1: forecasting abduction and civilian-targeting violence at state-week level in Nigeria from ACLED aggregated data

Waterways Internet Ltd research centre. Research note, 10 September 2026. Protocol fixed before modelling (docs/protocol.md). Code and derived results in this repository.

## Summary

Using only ACLED's freely available aggregated data (week x state x event type), we asked whether historical conflict-event counts can forecast whether a Nigerian state will record at least one abduction event, and separately at least one civilian-targeting violence event, in the following one to four weeks, and whether a gradient-boosting model adds forecast skill over a historical-rate baseline and logistic regression. Evaluation used 23 quarterly rolling-origin folds from 2021 Q1 to 2026 Q3, with no random splits.

Three findings.

1. **Past events forecast future events at state level, and a simple model is enough.** For abductions at a four-week horizon, logistic regression on lagged counts reached PR-AUC 0.815 against a base rate of 0.536, with Brier score 0.191 and expected calibration error 0.038. The historical-rate baseline alone reached PR-AUC 0.793. Ranking states by forecast probability, the five highest-ranked states recorded at least one abduction in the following four weeks 92% of the time.
2. **H1 is not supported. Gradient boosting did not beat the baselines.** At h = 4 the LightGBM model was worse than logistic regression on both primary metrics for both outcomes (abductions: PR-AUC 0.787 vs 0.815; Brier 0.210 vs 0.191), and for abductions it was worse than the historical-rate baseline on Brier score (0.210 vs 0.200). Paired bootstrap intervals over evaluation weeks exclude zero for every one of these differences. Under the protocol's negative-result policy this is reported as a finding: with lagged counts as the only inputs, a more flexible model overfits state-level history and calibrates worse.
3. **State level is close to saturated, which is the case for finer resolution.** 54% of all state-four-week windows contain an abduction; in Kaduna, Katsina and Zamfara the figure is above 75%. Forecasting "at least one abduction somewhere in Kaduna in the next month" is mostly a matter of knowing that it is Kaduna. The operational question, which local government areas within Kaduna, cannot be asked of this data. The pilot therefore establishes the pipeline, the baselines and the evaluation protocol, and demonstrates empirically why the programme targets LGA-week.

## Data

ACLED aggregated export for Nigeria, weeks ending 6 January 2018 to 29 August 2026; 37 units (36 states plus FCT); 452 weeks; 5,031 abduction events. Details, exclusions and limitations are in docs/data-card.md. Actor identities, coordinates and LGAs are not available at this grain, so terrorist violence by named groups cannot be isolated; outcome B is ACLED's civilian-targeting grouping (violence against civilians plus explosions/remote violence) and is labelled a proxy throughout.

## Outcomes and features

Outcome A: at least one abduction event in the state in weeks t+1 to t+h. Outcome B: at least one civilian-targeting event in the same window. Horizons h = 1 to 4; h = 4 primary. Features are trailing counts over 1 to 52 weeks of abductions, violence against civilians, battles, explosions, all political violence and fatalities; weeks since the last event; share of the past year with an event; the same counts summed over the four nearest states by centroid distance; week-of-year as sine and cosine; and state identity. Nothing from week t+1 or later enters any feature.

## Models and evaluation

Historical rate (trailing 104-window frequency, no fitting); L2 logistic regression; LightGBM with hyperparameters fixed in the protocol and no tuning on test data. Rolling-origin quarterly folds, 2021 Q1 to 2026 Q3, training only on rows whose target window closes before the evaluation quarter begins. Metrics: PR-AUC and Brier score (primary); ROC-AUC, log loss, expected calibration error, precision at K = 5 and K = 10 states (secondary). Differences between models are given as 95% intervals from a paired bootstrap over evaluation weeks (1,000 resamples).

## Results

### Primary horizon, h = 4, pooled 2021 Q1 to 2026 Q3

| Outcome | Model | Base rate | PR-AUC | ROC-AUC | Brier | Log loss | ECE | P@5 | P@10 |
|---|---|---|---|---|---|---|---|---|---|
| A abduction | Historical rate | 0.536 | 0.793 | 0.763 | 0.200 | 0.590 | 0.048 | 0.893 | 0.825 |
| A abduction | Logistic regression | 0.536 | **0.815** | **0.781** | **0.191** | **0.568** | **0.038** | **0.919** | **0.850** |
| A abduction | Gradient boosting | 0.536 | 0.787 | 0.746 | 0.210 | 0.612 | 0.075 | 0.888 | 0.805 |
| B civilian-targeting (proxy) | Historical rate | 0.830 | 0.951 | 0.806 | 0.117 | 0.380 | 0.039 | 0.988 | 0.992 |
| B civilian-targeting (proxy) | Logistic regression | 0.830 | **0.962** | **0.836** | **0.112** | **0.348** | **0.033** | 0.998 | 0.991 |
| B civilian-targeting (proxy) | Gradient boosting | 0.830 | 0.957 | 0.815 | 0.120 | 0.379 | 0.054 | 0.998 | 0.988 |

### Paired bootstrap, h = 4 (95% interval for the difference; negative Brier difference favours the first model)

| Comparison | Outcome | PR-AUC difference | Brier difference |
|---|---|---|---|
| Logistic minus historical | A | [+0.015, +0.028] | [-0.012, -0.005] |
| Gradient boosting minus historical | A | [-0.014, -0.000] | [+0.006, +0.013] |
| Gradient boosting minus logistic | A | [-0.035, -0.022] | [+0.015, +0.022] |
| Logistic minus historical | B | [+0.009, +0.014] | [-0.008, -0.004] |
| Gradient boosting minus historical | B | [+0.004, +0.009] | [-0.001, +0.005] |
| Gradient boosting minus logistic | B | [-0.007, -0.003] | [+0.006, +0.011] |

Decision under protocol section 9. **H1 not supported** for either outcome: gradient boosting is below logistic regression on both primary metrics with intervals excluding zero, and for outcome A it is below the historical-rate baseline on Brier. Logistic regression shows a small, consistent and statistically robust improvement over the historical rate on both outcomes.

### Horizon (H2)

Raw PR-AUC rises with horizon because the base rate rises (more weeks, more chance of at least one event). Measured as PR-AUC minus base rate (figure 1), skill for outcome A is flat to slightly falling from one to four weeks (logistic: 0.31, 0.32, 0.30, 0.28) and ROC-AUC is nearly constant (0.77 to 0.78). For outcome B, skill over base rate falls steadily with horizon (0.29 to 0.13) as the base rate approaches 0.83. **H2 is supported for outcome B and only weakly for outcome A.** At state level the persistence of abduction activity is strong enough that the four-week horizon costs little.

### Ablations (gradient boosting, h = 4)

Removing neighbour features changed PR-AUC by +0.007 (A) and -0.001 (B); removing seasonality by -0.001 and 0.000; removing state identity by +0.003 and 0.000. None of the feature groups beyond the lagged counts carries usable signal at state resolution. Neighbour counts, which the programme expects to matter at LGA level where borders are porous, add nothing when the units are whole states.

### Over time (figure 3)

All three models improve year on year for abductions (logistic PR-AUC from 0.71 in 2021 to 0.91 in 2026), tracking a rising base rate (0.49 to 0.60) and, most likely, more complete reporting. The gap between logistic regression and the historical rate is stable across years.

### Calibration (figure 2)

Logistic regression is well calibrated across the probability range for both outcomes (ECE 0.038 and 0.033). Gradient boosting is over-confident at the top of the range, which is where its Brier penalty comes from.

## Interpretation

At state-week resolution, abduction activity in Nigeria is highly persistent: the best single predictor of whether a state records an abduction next month is whether it did last month, and a regularised linear combination of lagged counts is the best of the three models tested. A flexible learner given the same inputs finds nothing further to learn and loses calibration. This is not evidence that machine learning has no role; it is evidence that lagged counts of the same series are the wrong place to look for additional signal. The programme's hypothesis is that additional signal lives in other modalities (geography, calendar effects, text) and at finer resolution, and this pilot is consistent with that: everything that can be extracted from state-level counts already has been.

The high base rates are the more important result for the programme. Nine states have an abduction in more than 60% of four-week windows. A forecast system that operates at this level tells a security committee very little it does not already know. The question that matters, which LGAs and which roads, needs event-level data.

## Limitations

State resolution, not LGA. No actor information, so outcome B is a proxy. No correction for reporting bias; the year-on-year improvement in all models is partly a reporting effect. Only one family of features (lagged counts of the same source). Hyperparameters fixed rather than tuned, by design. 37 units by 452 weeks, evaluated by forward blocks; intervals are bootstrapped over weeks, not rows, but spatial dependence between states is not modelled.

## What comes next

1. Event-level data for Nigeria (ACLED Research level requested; Nigeria Watch and the CFR Nigeria Security Tracker archive as independent LGA-coded sources) to re-run this exact protocol at LGA-week.
2. A negative-binomial and a Hawkes baseline added to the ladder, per the programme's evaluation plan.
3. Reporting-completeness diagnostics: compare state-level ACLED counts with the NBS survey and SBM Intelligence tallies to characterise where under-reporting is likely, before any correction is attempted.
4. Additional modalities in the order the programme specifies: geospatial, then calendar, then text, each evaluated by ablation against this baseline.

## Reproducibility

`python src/panel.py` builds the panel from a user's own ACLED export in `data/`; `python src/evaluate.py <outcome> <h> <model> [variant]` runs one configuration and caches predictions; `python src/evaluate.py summarise` produces the tables and bootstrap intervals in `outputs/`. Figures are produced by `src/figures.py`. All random seeds are fixed.
