# Data and model card — Phase 1 reference runs

## Scope and provenance

The models predict **static calculated bulk modulus** and **experimental compression yield strength**, separately. They do not predict phase identity, oxidation kinetics, bond strength, fracture toughness, creep or fatigue life. Thermal conductivity, CTE, density and Young modulus are declared mixture estimates, not learned targets.

| Source | Source rows | Accepted | Composition groups | Important limits |
|---|---:|---:|---:|---|
| `Saffron-Aero/data/raw_materials_project.csv` | 262 | 43 | 27 | Require positive finite bulk and shear moduli; ordered structures/pure elements are not experimental HEAs; material IDs and export query metadata are absent |
| `Saffron-Aero/data/EXP-MPEA_dataset.csv` | 1,545 | 317 | 85 | Nine-element subset, compression only, positive YS, known temperature, processing category and DOI |

Every row has an accepted/rejected record, a source CSV row number and an input-file checksum. Source publication DOI is preserved for the experimental data. The Materials Project local export lacks material identifiers and structure IDs, so complete upstream reconstruction is **not** currently possible. Formula groups can contain different calculated structures; grouping prevents those formula equivalents from crossing splits but does not make composition alone a sufficient physical descriptor.

The processed legacy table is deliberately bypassed: its stored composition and derived properties can disagree with the formula, and some elastic data have nonpositive shear modulus. The new model parses the original formula and excludes missing/nonpositive elastic targets. Positive moduli alone do not establish thermodynamic stability; metastability, energy above hull and disordered-alloy transfer remain unresolved.

No JARVIS observations are claimed: the local JARVIS CSV has zero data rows. No online scientific observations were added or invented during this repair. The older archived 12,427-record collection is not counted as model training data. The source dataset publication and repository are linked in [SOURCES.md](SOURCES.md); retain their attribution and license when redistributing derived exports.

## Exact benchmark

Fixed hyperparameters: ExtraTrees, 96 trees, minimum leaf size 2, all features available per split, random seed 42. Median-prediction baseline. Test and calibration compositions are excluded from fitting. Feature design and hyperparameters were fixed before inspecting the new protected-test result; no automatic tuning uses it.

| Target | Training rows/groups | Calibration rows/groups | Test rows/groups | Test MAE | Test R² | Median baseline MAE / R² |
|---|---|---|---|---:|---:|---|
| Bulk modulus, GPa | 22 / 16 | 3 / 3 | 18 / 8 | 20.409 | 0.8674 | 63.550 / -0.0020 |
| Compression yield, MPa | 185 / 54 | 48 / 13 | 84 / 18 | 229.520 | 0.4565 | 416.583 / -0.2120 |

Composition overlap across train/calibration/test is zero. These are row-weighted scores on a small number of distinct compositions; repeated temperatures and processing states are not independent discoveries. Inspect per-row predictions and grouped cross-validation rather than relying on R² alone. The previous random-split bulk score and training-set yield score used different data/protocols and are **not** controlled before/after performance comparisons.

Training-only five-fold composition CV is deliberately retained even where R² is negative. Yield fold MAEs range from about 119 to 462 MPa. A stronger training-only stress test groups connected components of shared composition **or** publication; its fold MAEs range from about 241 to 575 MPa. This reveals publication dependence and variable generalization. No prospective independent lab validation has occurred.

## Uncertainty and applicability

Bulk has only three calibration composition groups. The specified finite-sample nominal 90% group calibration rank is unavailable, so the exported interval radius is null. No precise bulk-confidence claim is made.

Yield has 13 calibration groups. Maximum within-group residual calibration yields a symmetric radius of approximately **1,648.7 MPa**, clipped at zero on the lower side for physical display. Held-out row coverage is 100%, but that is obtained with a very wide interval and only 18 test compositions. It does not establish useful precision or coverage for a new process/lab. The leading aerospace candidate has prediction 345.5 MPa and interval approximately 0–1,994.2 MPa. Its lower bound provides **no positive strength guarantee**.

Composition L1 nearest-neighbor distance, training-element coverage, processing-category coverage and yield temperature range are checked and exported. The bulk prediction for the leading new alloy is outside the sparse bulk training composition-distance threshold. The thermal screen therefore uses declared mixture constants, not that extrapolated bulk value. Distance thresholds are diagnostics, not certification that a candidate lies within a validated distribution.

Tree-to-tree disagreement drives an exploratory measurement proposal only. It is not a calibrated Bayesian posterior, a measured error bar, or proof that an experiment will improve the model. Reported sensitivity ranges perturb analyst-selected property/boundary assumptions; they are not confidence intervals on material performance.

## Known sources of bias

Composition and broad processing labels omit grain size, impurity content, heat-treatment schedules, strain rate and detailed microstructure. Compression data are not tensile or cyclic coating allowables. Static ordered-compound calculations and manufactured disordered HEAs occupy different domains. Publication coverage is uneven, and some compositions have many temperature observations. The supplied data are not a comprehensive inventory of existing alloys or patent prior art.

## Feedback policy

A real new measurement must include complete atomic fractions, measurement/specimen IDs, property, unit, absolute K temperature, processing, test mode, source, uncertainty and a checksum-backed report file. Supported feedback targets are compression YS and near-ambient bulk modulus. Bulk feedback above 323.15 K or below 273.15 K is rejected because the bulk model has no temperature dependence. The near-ambient experimental/static-DFT transfer limitation must still be considered before interpreting a mixed training generation.

Only train-partition compositions may be appended; calibration/test groups remain protected. Report checksums are rechecked at retraining. The reference runs use **zero** newly ingested measurements. Temporary software test fixtures do not enter scientific output or persist as real evidence. No measured improvement from active learning is claimed.
