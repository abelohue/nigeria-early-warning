# Data card: ACLED aggregated export, Nigeria, 2018 to 2026

**Source.** Armed Conflict Location & Event Data (ACLED), aggregated data export from the ACLED Data Export Tool, downloaded 10 September 2026 under a registered myACLED account (open access level). Nine yearly exports (2018 to 2026) concatenated; 49 rows duplicated across year-boundary weeks were removed.

**Grain.** One row per week (ending Saturday) x Admin1 (state) x event type x sub-event type, with event count, reported fatalities, population exposure and the state centroid.

**Coverage used.** Weeks ending 6 January 2018 to 29 August 2026 (452 weeks). 36 states plus the Federal Capital Territory. One maritime unit ("South Atlantic Ocean") excluded.

**Size.** 24,209 non-zero rows after deduplication, expanded to a complete panel of 16,724 state-weeks (37 x 452) with zeros where no events were recorded.

**Totals in the period.** 43,433 events; 88,737 reported fatalities; 5,031 events coded "Abduction/forced disappearance"; 17,592 "Violence against civilians"; 11,866 "Battles"; 1,724 "Explosions/Remote violence".

**What is not in this data.** Actor names; event coordinates; LGA; event notes; anything below state level. Terrorist violence by named groups cannot be identified. The pilot's outcome B (violence against civilians plus explosions/remote violence) is a civilian-targeting proxy, not a terrorism measure.

**Known limitations.** ACLED counts reported events; reporting intensity varies by state and over time, and ACLED's own coverage of Nigeria has expanded since 2018, so part of the upward trend in counts reflects reporting as well as violence. Weekly aggregation removes within-week timing. Fatality figures are ACLED's conservative reported estimates.

**Licensing.** ACLED terms of use for registered users. Raw exports are not redistributed with this repository; the code re-creates the panel from a user's own export placed in `data/`. Derived aggregate results and figures are released.

**Citation.** Raleigh, C., Kishi, R. and Linke, A. (2023). Political instability patterns are obscured by conflict dataset scope conditions, sources, and coding choices. Humanities and Social Sciences Communications, 10, 74. Data: acleddata.com.
