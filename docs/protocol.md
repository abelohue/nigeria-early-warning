# Research protocol: state-week forecasting of abduction and civilian-targeting violence in Nigeria from ACLED aggregated data

**Version 1.0, fixed on 10 September 2026, before any model was trained.**
Waterways Internet Ltd research centre. Pilot study 1 of the programme
"Explainable Multimodal Machine Learning for Spatiotemporal Early Warning of Terrorist Violence and Kidnapping in Nigeria".

Any departure from this protocol is recorded in section 11 with the date and the reason.

## 1. Research question

Can historical conflict-event data alone forecast whether a Nigerian state will record at least one abduction event, and separately at least one civilian-targeting violence event, within the following one to four weeks, and does a machine-learning model add forecast skill over simple statistical baselines?

## 2. Hypotheses (falsifiable)

- **H1.** A gradient-boosted model using lagged event features will show higher out-of-sample forecast skill (PR-AUC) and better calibration (Brier score) than the local historical-rate baseline and than logistic regression on the same features.
- **H2.** Forecast skill degrades with lead time: one-week-ahead skill exceeds four-week-ahead skill for every model.
- **H0 (negative-result policy).** This study does not assume that machine learning outperforms simpler baselines. If H1 is not supported, the finding is reported as such and is treated as a result, not a failure.

## 3. Data

- **Source.** ACLED aggregated data export (week x country x Admin1 x event type x sub-event type), Nigeria, exported 10 September 2026 under a registered myACLED account. Weekly bins end on Saturdays. Coverage used: weeks ending 6 January 2018 to 29 August 2026.
- **Unit of analysis.** State-week: the 36 states plus the Federal Capital Territory (37 units). Maritime rows ("South Atlantic Ocean") are excluded.
- **Not available at this grain and therefore not used.** Actor identities, event coordinates, LGA, notes. Consequently "terrorist violence" cannot be attributed to named groups in this pilot; see outcome B.
- **Licensing.** ACLED terms of use; raw data are not redistributed. Code, derived aggregate results and figures are released.

## 4. Outcomes

For state s and week t, with horizon h in {1, 2, 3, 4} weeks:

- **Outcome A (abduction).** y = 1 if the ACLED sub-event type "Abduction/forced disappearance" has events >= 1 in state s during weeks t+1 .. t+h; else 0.
- **Outcome B (civilian-targeting violence, proxy).** y = 1 if any of the following has events >= 1 in state s during weeks t+1 .. t+h: event type "Violence against civilians" (all sub-events), or event type "Explosions/Remote violence". This follows ACLED's civilian-targeting grouping and is a proxy: without actor data it cannot separate terrorist groups from other perpetrators. This limitation is stated in every table that reports outcome B.

The primary horizon is h = 4. Horizons 1 to 3 are secondary (H2).

## 5. Features (all computed from weeks <= t only)

For each state: counts over the trailing 1, 2, 4, 8, 13, 26 and 52 weeks of (i) abduction events, (ii) violence-against-civilians events, (iii) battles, (iv) explosions/remote violence, (v) all political-violence events, (vi) political-violence fatalities; weeks since the last abduction event and since the last civilian-targeting event (capped at 104); the share of the trailing 52 weeks with >= 1 abduction event; the same trailing-4-week and trailing-13-week counts summed over the 4 nearest neighbouring states by centroid distance; week-of-year as sine and cosine; state identity as a categorical feature.

No feature uses information from week t+1 or later. No feature uses population, geography beyond centroids, text, or calendars beyond week-of-year: those are reserved for later studies.

## 6. Models (in the order they are compared)

1. **Historical rate (baseline 1).** For each state, the empirical probability that a window of h weeks starting after week t contains >= 1 event, estimated from the trailing 104 weeks. No fitting.
2. **Logistic regression (baseline 2).** L2-regularised, on the standardised feature set of section 5.
3. **Gradient boosting (candidate).** LightGBM binary classifier, fixed hyperparameters chosen before seeing test results: 400 trees, learning rate 0.03, 31 leaves, min 50 observations per leaf, feature and bagging fraction 0.8, no early stopping on test data.

Models 2 and 3 are fitted separately for each outcome and each horizon.

## 7. Evaluation design

- **Rolling-origin, quarterly.** For each evaluation quarter Q from 2021 Q1 to 2026 Q3 inclusive (23 quarters), fit on all state-weeks with t + h strictly before the start of Q (so no label leaks across the boundary), and forecast every state-week whose target window lies inside Q. No random splits.
- **Metrics (primary):** PR-AUC (average precision) and Brier score. **Secondary:** ROC-AUC, log loss, expected calibration error (10 bins), precision at K = 5 states and K = 10 states (the states an analyst could act on), pooled over all evaluation weeks.
- **Reporting.** Metrics are reported pooled over the evaluation period and per year, with the base rate alongside every PR-AUC. Differences between models are accompanied by a paired bootstrap over evaluation weeks (1,000 resamples) giving a 95% interval for the difference in PR-AUC and Brier.
- **Calibration.** Reliability diagrams for the primary horizon.

## 8. Ablations

For the gradient-boosting model at h = 4: remove neighbour features; remove seasonality; remove state identity. Each ablation is reported next to the full model.

## 9. What would count as support for H1

H1 is supported for an outcome if, at h = 4, the gradient-boosting model's PR-AUC exceeds both baselines and its Brier score is lower than both, and the 95% bootstrap intervals for both differences against the historical-rate baseline exclude zero. Partial support (one metric, or one baseline) is reported as partial.

## 10. Known limitations, stated in advance

- State-week is one administrative level coarser than the programme's target (LGA-week). This pilot establishes the pipeline and baselines, not the final resolution.
- Event data reflect reporting as well as violence. This pilot does not correct for reporting bias; it documents where it likely matters.
- 37 units by roughly 450 weeks is not 16,000 independent observations. Spatial and temporal dependence are why evaluation is by forward time blocks and why intervals are bootstrapped over weeks, not rows.
- Outcome B is a proxy for civilian-targeting violence, not for terrorism by named groups.

## 11. Deviations from protocol

- **10 Sep 2026, before results were inspected.** The historical-rate baseline was re-implemented as a vectorised trailing mean of realised h-week windows (identical quantity, faster computation) after the row-wise implementation proved too slow to run. Minimum history reduced from 104 to 8 realised windows so that early 2021 rows are not dropped; the window length remains 104.
- **10 Sep 2026, before results were inspected.** Rolling-origin folds were run per configuration and cached to disk rather than in a single process, because of execution-time limits. The fold definitions are unchanged.
- **Note on reporting.** Rows whose forecast week falls in the last days of December 2020 have target windows inside 2021 Q1 and are labelled "2020" in the per-year table; they are included in the pooled results as specified.
