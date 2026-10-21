# Crystal Paradigm HE-MCGA — Phase 1 engineering and evidence repair

## Outcome

Phase 1 delivers a connected, tested inverse-screening workflow and a candid scientific evidence base for SCIDIP preparation. It replaces unreliable scoring paths, generates complete new candidate hypotheses, and implements the software path for real measurement feedback. It does **not** establish aerospace qualification, a validated material advantage, protective oxidation behavior, patentability or a completed experimental closed loop.

The original application documents in `IIT DELHI LATEST/` are preserved. Patent work and final pitch preparation remain Phases 2 and 3. Some historical claims in those documents must be reconciled before reuse.

## Why the earlier project could be rejected

| Perspective | Major rejection risk found | Phase 1 correction/upgrade | What remains unresolved |
|---|---|---|---|
| Materials science | Formula parsing could discard unsupported elements; rounded recipes lost mass; empirical phase descriptors were treated too strongly; Al was added after optimization | Strict complete compositions; correct atomic/mass/volume bases; full-precision recipes; missing binary interactions marked unknown; assessed-database CALPHAD adapter | Target-alloy phase, oxidation, segregation, ceramic reaction, bond, ductility and manufacturability evidence |
| AI / inverse design | Bulk random split overlapped compositions; yield score was measured on training data; missing data could trigger synthetic fallback; geometry was not genuinely jointly searched | Frozen composition train/calibration/test groups; median baseline; training-only group/publication stress tests; explicit uncertainty/applicability; seeded joint chemistry/exponent/thickness search; protected measurement ingestion and retraining | Small biased data, broad uncertainty, no prospective physical feedback or external lab validation |
| Aerospace | 1400 K was conflated with 1400 °C; hot alloy/cold ceramic orientation; algebraic stress labeled interface/FEA; arbitrary creep relief and ratio called safety factor | Explicit face-K profiles; cold alloy/hot ceramic; verified reduced laminate force/moment solution; flat/free boundary comparison; mesh and assumption studies | Actual substrate, transient cycles, oxidation, creep, fatigue, interfacial fracture, component loads and validated allowables |
| Startup / business | Aerospace scope and sponsor fit were not backed by customer evidence; hypothetical benefits could be presented as achieved | Specific forging-tool coupon discovery hypothesis for Sona; application-specific screen; transparent tooling economics; measurable pilot and execution gates | Sponsor requirements, signed pilot, facility/team commitments, quotations, measured value and assessed IP |

The full mapping is in [FIX_REGISTER.csv](FIX_REGISTER.csv). The [workflow](WORKFLOW_AND_MODELS.md) specifies the exact contracts, equations and objective.

## Implemented software

A small maintained package under `phase1/he_mcga/` now connects source curation, property model evaluation, joint inverse screening, thermal laminate analysis, candidate/recipe export and measurement-feedback retraining. Main commands are in [phase1/README.md](../README.md). No paid compute, credential, archived pickle or new scientific dataset download is needed for the reference pipeline.

The optimizer searches complete nine-element atomic fractions, gradient exponent and thickness together. It enforces explicit chemistry/density/heat-flux design constraints, logs rejected evaluations, exports Pareto membership and compares DE against a same-budget random search. Both stop at a fixed declared budget; no global optimum or broadly superior optimizer is claimed. The proposed six-member batch per application includes performance and uncertainty probes with composition diversity.

Historical executable entry points now fail with migration instructions instead of silently emitting old safety claims or overwriting stale recipes. Historical function bodies/reports remain audit records. The old thermal filename is a compatibility adapter to the maintained model. Hardcoded API credentials were removed from the active fetch helper and matching tracked plaintext copies. **The owner must revoke/rotate the previously exposed credential; removing it from current files does not remove Git history.**

## Executed evaluations

All **30 automated checks pass**, covering strict chemistry, material mixing bases, unknown interaction handling, thermal analytical limits, force/moment balance, mesh/recipe dimensions, protected partitions, missing-calibration behavior, hard feasibility, Pareto logic, units, scenario economics, measured-feedback validation and retraining, deterministic full-workflow outputs, legacy entry-point blocking and a real binary CALPHAD integration check. A GitHub Actions workflow has been added but has not run remotely before publication.

| New benchmark | Data actually fitted/evaluated | Protected-test result | Interpretation |
|---|---|---|---|
| Static bulk modulus | 43 source rows / 27 formula groups; 18 test rows / 8 groups | MAE 20.409 GPa; R² 0.8674 | Beats median baseline in this small split; not validation of disordered HEAs; only 3 calibration groups, so no finite nominal 90% interval |
| Compression yield | 317 curated experimental rows / 85 groups; 84 test rows / 18 groups | MAE 229.520 MPa; R² 0.4565 | Genuine held-out composition test; processing/microstructure and publication shifts remain significant |

Train/calibration/test composition overlap is zero. The yield calibration radius is about 1,648.7 MPa. The broad interval includes zero lower strength for the top candidates. This is an important negative finding, not a confidence result to hide. Full metrics, per-row predictions, rejected data and stronger publication-connected CV are committed in each run. See [DATA_MODEL_CARD.md](DATA_MODEL_CARD.md).

The thermal solver now conserves heat flux and solves laminate force/moment equilibrium. Analytical identical-material/free-curvature and zero-temperature-change limits are checked. For the leading aerospace candidate, the 80-layer stress is about 232.007 MPa and the 320-layer value about 232.525 MPa (approximately 0.22% different). The coarser 11-layer proposed recipe is separately evaluated at about 235.926 MPa. Exact layer-average fractions conserve the nominal ceramic volume.

The same alloy/geometry at 1400 K gives about 232 MPa when freely curving versus 1,384 MPa when held flat. At a 1673.15 K hot face, the corresponding values are about 290 and 1,728 MPa. These estimates show why boundary conditions and temperature units are decisive; they do not establish that either state is survivable. Analyst-selected property/boundary perturbations span about 207–258 MPa for the freely curving aerospace screen, not a measured confidence interval.

A real Al–Ni equilibrium calculation at 1000 and 1600 K exercises the pycalphad adapter and phase-fraction balance. It is a software integration fixture, **not** HE-MCGA phase evidence. No suitable target-alloy assessed TDB, new DFT, MD, 3-D FEA, physical test or fatigue-life result was available/performed.

## New leading computational hypotheses

Values below are atomic percent rounded only for reading. Use each `best_candidate.json` for the full precision vector; do not reuse the rounded table as a manufacturing composition.

| Element | Aerospace screen `d7fab57638425c7f` | Sona coupon screen `f3c7e3947af2b379` |
|---|---:|---:|
| Mo | 8.8810 | 2.4299 |
| Nb | 13.5438 | 18.3027 |
| Ta | 7.5059 | 5.1214 |
| W | 1.8102 | 5.0220 |
| Cr | 19.2201 | 23.1886 |
| V | 2.0959 | 2.6543 |
| Ti | 24.9122 | 21.6482 |
| Zr | 18.1409 | 20.9098 |
| Hf | 3.8900 | 0.7231 |

| Screening quantity | Aerospace reference | Sona coupon hypothesis |
|---|---:|---:|
| Imposed hot/cold faces | 1400 / 300 K | 873.15 / 473.15 K |
| Mechanical assumption | Free curvature | Flat, force equilibrium |
| Ceramic / gradient exponent | LZO / 0.5151 | LZO / 0.5684 |
| Thickness | 4.2299 mm | 3.8389 mm |
| Density estimate | 7.9949 g/cm3 | 7.8267 g/cm3 |
| Peak in-plane stress estimate, 80 layers | 232.007 MPa | 544.521 MPa |
| Compression YS prediction at configured K | 345.5 MPa | 890.5 MPa |
| Yield interval, nominal group calibration | 0–1,994.2 MPa | 0–2,539.2 MPa |
| DE / random evaluations | 594 / 594 | 594 / 594 |
| Feasible DE / random points | 255 / 43 | 241 / 81 |
| Best DE / random heuristic score | 0.45545 / 0.88338 | 0.77178 / 0.91078 |

Every listed candidate is **unmeasured**. No phase/oxidation advantage, strength margin, manufacture success or novelty is established. The bulk predictor is extrapolating for the leading new alloy; it is retained as a flagged diagnostic and is not used to derive Young modulus. The score comparison is a single-seed computational diagnostic, not a scientific performance improvement over an actual baseline material.

The checked directories contain two 10-candidate shortlists, six proposed measurements per application, 11-layer exact-composition coupon designs, all 2,376 total search evaluations, source/holdout tables, manifests and sensitivity studies. Source data and submitted documents were not overwritten.

## Readiness and next decisions

The project is now easier to execute, audit and defend as a research proposal. A software repair cannot move a material directly to deployment readiness or guarantee an IIT Delhi selection outcome. The highest-value next step is a narrowly specified, independently measured coupon study with a conventional baseline, phase/oxidation/bond characterization and one prospective feedback iteration.

For SCIDIP, use [CLAIMS_FOR_PANEL.md](CLAIMS_FOR_PANEL.md) and [VALIDATION_PLAN.md](VALIDATION_PLAN.md) to explain what is proven and what the proposed support will de-risk. For sponsor alignment, [SONA_PILOT_AND_BUSINESS.md](SONA_PILOT_AND_BUSINESS.md) separates public company facts from our pilot inference and ROI assumptions. Phase 2 should reconcile documents and assess IP/disclosure with qualified help; Phase 3 should build the final pitch around the actual evidence and executable milestones.

## Repository publication

The work is prepared on `codex/phase1-evidence-pipeline` from original main commit `9d47562ee59bf9c14f8873170bac662f9bc1ceff`. The connected GitHub identity was verified as `sohailhatim49`; GitHub reported read permission and `push: false` for `Raza786R/SCIDIP`. Publication status and the final commit are recorded in the handover package. No remote publication is implied by local completion.
