# Data card: Nigeria Security Tracker (NST), Council on Foreign Relations

**Source.** CFR Africa Program, Nigeria Security Tracker, full incident dataset published as a Google Sheet linked from the tracker page (cfr.org/nigeria/nigeria-security-tracker/p29483; page retired in 2026, retrievable via the Internet Archive). Obtained 11 September 2026 as NST-Main_Sheet.xlsx. Licence CC BY-NC-ND 4.0.

**What it is.** 14,881 incidents of political violence in Nigeria (and Boko Haram-related incidents in Cameroon, Chad and Niger), 29 May 2011 to 30 June 2023, compiled weekly from Nigerian and international press. Columns: title, date, community, LGA, state, total deaths, perpetrator categories (Boko Haram, state actor, sectarian actor, other armed actor, kidnapper, robber, other, election-related), victim categories with counts (including kidnapee and civilian), weapons, location types, notes, up to three source URLs, coordinates (mostly failed formulas), country.

**Coverage used.** Nigeria, 1 January 2018 to 30 June 2023: 9,554 incidents. Cameroon, Chad and Niger rows excluded.

**Cleaning.** State names harmonised (Nassarawa/Nasarawa; FCT/Abuja). LGA names mapped to the 774-LGA reference list (arilwan/Nigeria on GitHub, cross-checked against official spellings): 9,132 rows by exact or fuzzy match within state, 190 by 13 manual rules (e.g. "Tsafe" to Chafe, "EgbadoNorth" to Yewa North, "Kotonkar" to Kogi), 232 rows (2.4%) dropped for missing or unmatchable LGA. Mapping released as data/lga_mapping.csv. Six reference LGAs never appear and a handful of NST spellings collapse onto the same reference LGA; the panel therefore has 768 units.

**Outcome definitions.** Kidnapping: "Kidnapper (P)" non-empty or "Kidnapee (V)" > 0. Armed-group violence against civilians: any of Boko Haram (P), Sectarian Actor (P), Other Armed Actor (P) non-empty and "Civilian (V)" > 0.

**Known limitations.** Single press-based source; CFR's own note says reporting is sparse in some regions and death tolls imprecise. Ended June 2023. 89 of 768 LGAs have no incident of any kind in the period used. Coordinates unusable. Perpetrator categories are coarse ("other armed actor" spans bandits, militias and unknown gunmen).

**Redistribution.** The raw spreadsheet is not included in this repository (NoDerivatives licence); the code expects it at data/NST-Main_Sheet.xlsx. Derived aggregates, mapping and results are released.
