# Data and AI models in HE MCGA
Crystal Paradigm | What is learned and what is only estimated

The maintained workflow has two supervised regression models. One predicts calculated bulk modulus and the other predicts experimental compression yield strength. It does not contain an executed phase classifier, oxidation model, neural interatomic potential or trained model of coating life. CTE, conductivity, density and Young modulus used in the thermal screen come from declared mixture estimates.

## Data journey and exclusions
| Local source | Available rows | Curated rows and groups | Meaning |
| Materials Project export | 262 | 43 rows in 27 composition groups | Positive calculated bulk and shear moduli; ordered structures and elemental anchors |
| EXP MPEA export | 1545 | 317 rows in 85 composition groups | Compression YS with supported chemistry, temperature, processing and DOI |
| JARVIS export | 0 observations | Not used | No JARVIS training data may be claimed |

The algorithm reads the original formula from each source row. It rejects unsupported elements and malformed formulas. Bulk rows need finite positive bulk and shear values. Experimental rows need positive yield, a known absolute temperature, compression test mode, a supported processing category and a publication DOI. Missing temperature is not assumed to be room temperature. Synthetic fallback is disabled.

The legacy processed composition table is bypassed because some stored composition and derived values disagree with its formula. The new accepted and rejected tables preserve source row numbers, reasons and input hashes. Experimental publication provenance is retained. Materials Project structure IDs and full export query metadata were not supplied, so exact upstream reconstruction remains incomplete. Different ordered structures with the same formula can have different properties; the model does not encode their atomic structures.

The experimental collection originates from the public MPEA dataset described by Borg and colleagues. Its entire database is not our training set; only the curated subset above is. [S4]

## Features and model architecture
A feature is a numerical representation of an input. Each model receives nine atomic fractions plus mean and spread of atomic radius, VEC, melting temperature and atomic mass. That makes 17 chemistry features. The yield model adds test temperature in degrees C, converted from explicit K, and five indicators for CAST, WROUGHT, ANNEAL, OTHER and POWDER processing. It therefore has 23 features.

Both learners are ExtraTrees regressors with 96 trees, minimum leaf size two, all features available per split and seed 42. A tree partitions feature space and predicts from training observations in its leaves. The ensemble averages many randomized trees. This is different from the historical Random Forest model and from a graph neural network. It does not infer missing crystal structures or enforce a constitutive law.

Melting point and VEC descriptors are inputs, not measured service properties of a new alloy. Feature importance would describe the fitted predictor's dependence within its data, not prove a causal materials mechanism. The current bulk model is retained as a diagnostic; Young modulus in the thermal model is not derived by multiplying its output by 1.2.

## How leakage is prevented
Equivalent normalized formulas share a composition ID. The first eight decimal places are used for grouping, while exported candidate fractions retain full precision. All temperatures and processing states of the same composition remain in one partition. A fixed hash rule assigns groups to training, calibration or test. The estimator used for candidate prediction is fitted only on training rows.

A median predictor supplies a simple baseline. Training only grouped cross validation tests sensitivity to which compositions are available. A stronger yield stress test links records that share composition or publication and holds connected blocks apart. This reveals whether publication dependence contributes to apparent accuracy. It is not a new prospective experiment.

The old bulk random split overlapped formula groups, and the historical yield score was calculated on fitted training data. Those protocols are not comparable to the current protected benchmark. The new scores should not be advertised as an improvement obtained by making the old number larger.

## Current benchmark and interpretation
{{table:model_metrics}}

MAE is the average absolute prediction error in the target's units. R squared compares squared errors against variation in the test outcomes; negative values can occur when predictions are worse than a constant reference. Neither metric is a probability that a new alloy will succeed.

The compression model's 84 test rows represent only 18 compositions. Repeated temperatures and processing states are correlated. Training only composition CV has yielded fold MAEs from about 119 to 462 MPa; the publication connected stress test spans about 241 to 575 MPa. The model is useful for a research screen but is not a high temperature design allowable.

Phase 2 did not add new physical observations or tune these model hyperparameters. Repeating the same benchmark after a code repair is a regression check, not independent confirmation of generalization. Materials ML research documents why database performance can degrade under distribution shift. [S3]

## Calibration uncertainty and applicability
Calibration is separate from fitting. For each calibration composition we take the largest absolute error across its available observations, then choose the specified finite sample nominal 90 percent order statistic. Bulk has only three calibration groups, which is insufficient for a finite bound at that level; its radius is exported as null.

Yield has 13 calibration groups and a radius of roughly 1648.7 MPa. This gives very broad intervals and zero lower bounds for the leading candidates. Observed test row coverage is 100 percent, but wide coverage on a small correlated sample does not establish useful precision for a new lab or manufacturing route.

Tree disagreement is a separate heuristic for selecting informative measurements. It is not a calibrated posterior uncertainty. The software also checks distance from training compositions, unseen elements, unseen processing categories and yield temperatures outside the training range. Passing these checks does not prove prospective exchangeability. In Phase 2, a flagged interval cannot earn an optimization strength reward.

## What would improve the scientific model
The next useful data should describe actual candidate chemistry, processing, grain size, impurities, phase state and the relevant test protocol. Add temperature dependent thermophysical measurements before claiming the thermal model represents an alloy rather than an elemental mixture assumption. Compression data alone cannot establish tensile ductility, creep, fatigue, adhesion or ceramic fracture.

Use a prospective external set and equal test budget to compare model guided selection with expert or random selection. Retain failed experiments. Avoid repeatedly choosing models against a familiar test score. The code and files make that evaluation possible; they do not replace it.

## Files to inspect and commands
Read bulk_curated.csv, yield_curated.csv, metrics.json and the held out prediction CSVs within either Phase 2 result directory. The two applications share the same property models and benchmark but differ in thermal and mechanical assumptions. Model parameters, source hashes, code hashes and dependency versions appear in the run manifest.

From the repository root, install the package using pyproject.toml and the tested constraints file, then run the selected Phase 2 JSON profile with python module he_mcga. The full runnable commands are in phase2/README.md. Reading these tables while explaining the model is more reliable than quoting a score from an old slide.
