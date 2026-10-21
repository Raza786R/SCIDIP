# Inverse design and the measurement loop
Crystal Paradigm | From requirements to the next experiment

Inverse design starts with desired behavior and searches design inputs. Our workflow currently searches nine atomic fractions, gradient exponent and thickness. A closed experimental loop additionally requires manufacturing, measurement, learning from discrepancies and a new proposal. The software path exists; no new physical cycle has yet been completed.

## Define requirements before choosing a candidate
An application profile sets the ceramic, imposed hot and cold face temperatures, stress free reference, mechanical constraint, strength screening temperature and processing category. It also sets design bounds. These are analyst chosen assumptions until agreed with a customer and lab. The aerospace profile uses 1400 K hot and 300 K cold faces; the Sona hypothesis uses 873.15 K and 473.15 K with flat constraint. Neither is a verified service envelope.

Hard screening rules require five elements at or above 5 atomic percent, no element above 35 percent, a configured Cr minimum and V maximum, estimated density at most 11 g per cubic centimetre and heat flux at most 2 MW per square metre. The element thresholds are search choices, not thermodynamic or oxidation certificates. The system must be allowed to fail when no candidate satisfies the chosen rules.

## Search mechanics
Differential evolution, DE, maintains a population of trial designs and generates new designs by combining and comparing them. It does not compute a physical gradient of a material's performance. Nine numerical design coordinates, called logits, pass through softmax: exponentiate each coordinate and divide by their total to obtain fractions summing to one. All nine fractions remain positive in the current bounds; selecting the necessary number of elements is a separate unresolved design question.

The exponent is searched between 0.5 and 3.0, and thickness between 0.5 and 5 mm. The ceramic type is fixed per profile. Each point gets chemistry checks, thermophysical estimates, property predictions, a reduced thermal calculation and explicit applicability flags. Full vectors and rejected evaluations are logged. There is no post optimization Al addition and no omission of low percentage elements from the authoritative recipe.

{{equation:objective.png|The current dimensionless search score with declared scaling and weights}}

Stress is in MPa, density in g per cubic centimetre and areal mass in kg per square metre. D is the nearest training composition L1 distance, F is the count of yield applicability flags, and Lc is the nonnegative lower compression yield bound only when applicability checks pass. We minimize the score. These weights are heuristic preferences, not fitted customer economics or a safety factor.

Phase 2 adds areal mass so thinner feasible designs have an explicit benefit. With imposed face temperatures and a geometrically similar elastic laminate, stress alone does not identify an optimal thickness. Heat flux supplies a feasibility constraint; the added mass term supplies a thickness tradeoff. The ceramic density used in this conversion is an explicit 6 g per cubic centimetre assumption.

## Compare and propose
Each checked profile evaluates 594 DE points and 594 seeded random baseline points using the same parameter bounds and hard rules. DE stops at its iteration budget rather than a proven optimum. A Pareto flag identifies points not dominated simultaneously in estimated stress, density, areal mass and eligible strength lower bound. The final shortlist is ordered by the stated scalar score, which is a separate choice from Pareto membership.

The proposed measurement batch combines low score points and points with high tree disagreement while enforcing a composition diversity distance. This is a batch selection heuristic, not an implemented Bayesian expected improvement calculation or proof of information gain. A simpler composition and the incumbent application material should also be considered as experimental controls even if they sit outside this project's HEA search rules.

{{figure:feedback_workflow.png|Proposals become learning only after external manufacture and valid measurement evidence}}

## Measurement contract and protected evidence
A genuine feedback record includes the measurement and specimen IDs, complete atomic fractions, supported property and unit, absolute K temperature, test mode, processing, source, uncertainty and an existing report file with matching checksum. Compression YS uses MPa. Bulk modulus uses GPa and is restricted to near ambient elasticity because the bulk model has no temperature dependence.

The record must declare that it is not synthetic. Ingestion is atomic: if any item fails validation, none of the batch is appended. Duplicate specimen property temperature combinations and measurement IDs are rejected. Phase 2 revalidates the complete ledger when it is read for retraining, including target metadata and units, rather than trusting an edited JSON file.

Every proposal now states its benchmark partition and intended feedback role. Only training partition compositions are eligible for the training ledger. A calibration or test partition proposal is for protected validation only. Do not pay for a measurement expecting it to update the model without checking that role first. Preserve a true external validation path rather than moving difficult results into training to improve a score.

## One complete prospective iteration
First agree the application and test protocol, select a manageable batch and obtain a manufacturability review. Record feedstock and process history, verify actual chemistry and specimen identity, then measure the relevant properties with uncertainties. Unsupported properties such as oxidation and bond strength belong in the evidence register until an appropriate validated model is built; they are not coerced into the yield target.

Next ingest eligible measurements and create a new immutable output directory. The models fit the allowed training rows, recalibrate using the protected calibration rows and evaluate on the unchanged test groups. Compare prediction errors, uncertainty, chosen designs and actual cost and time with the previous generation. A changed proposal demonstrates software response; measured progress against a baseline demonstrates useful discovery.

The automated tests use temporary labeled fixtures to check this behavior and remove them afterward. They do not count as new experiments in any reported scientific run. The reference runs contain zero new physical feedback records.

## Questions that expose a weak loop
Which observation changed the model? Was it independent, with a traceable report and actual chemistry? Did it alter the next candidate or reduce a relevant error? Were failed specimens retained? Did a protected test result leak into training? Can a lab repeat the result? Until these questions have concrete answers, describe the project as an implemented feedback capable screen rather than a completed autonomous discovery experiment.
