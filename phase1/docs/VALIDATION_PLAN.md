# Materials, aerospace and inverse-loop validation plan

This plan specifies the evidence still required. It is not a record that these experiments, facilities or partners are secured. Acceptance limits must be agreed with the application owner before experiments, not selected after observing results.

## Immediate decision gates

| Priority | Question | Evidence needed | Current status | Stop/revise condition |
|---|---|---|---|---|
| 1 | Is the candidate chemically and thermodynamically plausible? | Assessed composition-specific CALPHAD over manufacture/service temperatures; phase database assessment review | Adapter tested; target database absent | Unsupported elements/interactions, unstable unwanted phases or liquid fraction at intended exposure |
| 1 | Can a reproducible alloy coupon be made? | Process route, powder/ingot availability, oxygen control, mass balance, shrinkage and porosity measurements | Exact composition and nominal layer recipe only | Uncontrolled segregation, cracks, contamination or composition drift |
| 1 | Is the manufactured structure what was designed? | XRD with documented refinement; SEM/EDS across gradient; density/porosity; EBSD if needed | No new measurements | Brittle continuous phases, unexpected phase distribution or poor bonding |
| 1 | Does it resist the actual environment? | Cyclic/isothermal oxidation mass change per area, atmosphere/humidity control, scale cross-section and chemistry | Unverified | Nonprotective scale, spallation, pesting or unacceptable mass change |
| 1 | Does the ceramic/alloy interface remain compatible? | Diffusion couple and exposure cross-sections; bond tests appropriate to the deposition route; fracture morphology | Unverified | Reaction layers, delamination or inadequate adhesion |
| 2 | Are the model constants credible? | Temperature-dependent dilatometry, laser-flash thermal diffusivity plus density/heat capacity, elastic modulus measurement | Pure-element mixture assumptions | Measured constants invalidate thermal ranking or heat-flux budget |
| 2 | Is the strength model transferable? | Controlled compression tests at configured K and processing; separate tensile ductility/toughness tests | Public-data benchmark only | Lower strength/ductility than application baseline or large prediction errors |
| 2 | Is cycling survivable? | Instrumented thermal cycles with crack/spallation mapping and documented failure criterion | Quasi-static screen only | Early cracking, oxide growth or thermal fatigue |
| 3 | Is an aerospace component plausible? | Actual substrate/geometry, gas/cooling boundary conditions, loads, defect population, temperature-dependent constitutive properties and transient 3-D validation | Not qualified | Failure of creep, fatigue, bond, fracture, oxidation or load allowables |
| 3 | Does the sponsor gain value? | Customer-confirmed failure mode, baseline tool comparison, wear/contact data, reproducible cost per accepted part | Hypothesis only | No improvement at equal quality or unacceptable coating/manufacture cost |

The initial material set should include the current application baseline, an ungraded control and a graded candidate. Agree replicate counts and statistical acceptance with the lab; as a starting experiment proposal, use at least three independently made specimens per screening condition and explicitly distinguish manufacturing repeats from multiple measurements on one specimen. More samples may be needed for variability and qualification. Do not consume all experimental budget on the best surrogate score; retain independent validation and informative uncertainty probes.

## CALPHAD and atomistic work

The new adapter performs Gibbs-energy equilibrium with one dependent chemical component, all compatible entered phases, database fingerprint and phase-fraction balance. It cannot create missing multicomponent interaction assessments. Obtain a legally usable, applicable database and have a thermodynamics expert review phase descriptions and extrapolation. Element presence in a TDB is insufficient. Equilibrium also does not predict oxidation kinetics, segregation during a particular cooling history or metastable retained phases.

DFT was not performed in this repair. It should be commissioned only for a concrete uncertainty: e.g. compare relevant competing phases/chemical ordering or ceramic/alloy reaction products. Specify representative structures or SQS, composition, magnetic treatment, pseudopotentials, convergence tests, reference states and uncertainty before interpreting formation energies. Oxidation and interface reaction calculations require appropriate chemical potentials and structures. A single relaxed structure or an AI-generated input file is not validation of an entire nine-element graded component. No fictional DFT energy, molecular-dynamics trajectory or cloud job is included as evidence.

## Thermal and mechanical progression

The current implementation verifies conduction, layer volume conservation, force/moment balance and analytical limiting cases. It compares mesh sizes and flat/free curvature boundary assumptions, and perturbs elemental mixture constants and boundary temperature. These are **verification** of a reduced model plus assumption sensitivity, not validation against specimens.

Next, measure the specimen thermal response under known heating/cooling boundary conditions. Fit only physically identifiable parameters. Add the actual substrate and bond layers, measured temperature-dependent k/CTE/E, process stress-free temperature and porosity. Model transient heating/cooling, creep/plasticity and oxidation only with defensible constitutive data. Progress to 2-D/3-D contact, interfacial fracture and component loading after coupon evidence supports that expense. Keep a simpler analytical check for each numerical model.

The 1-D model cannot resolve interface shear, delamination energy release, edge effects, fatigue life or component safety factor. A compression-yield prediction divided by ceramic-dominated in-plane stress is not an allowable or a valid qualification factor.

## Operational closed loop

1. Freeze an application requirement sheet and benchmark split before selection.
2. Select a small diverse batch from the proposed screen; obtain manufacturability review.
3. Manufacture with recorded feedstock, process parameters, actual chemistry and specimen identity.
4. Characterize phases, environment resistance and relevant properties with uncertainty.
5. Store genuine reports and ingest supported measured targets; route unsupported targets to the evidence register rather than inventing a model.
6. Retrain eligible training groups, recalibrate on the unchanged calibration groups, and evaluate once on the protected test groups.
7. Compare prediction error and next-batch choices with the previous generation. Preserve failed experiments and negative results.
8. Promote a claim only when independent evidence meets its predeclared gate.

Protected-group new measurements should remain external validation, not be moved into training to improve a score. When the benchmark becomes too familiar, create a prospectively collected external validation set; do not repeatedly optimize against a published test score.

## SCIDIP execution and team

The program asks for technical strength, entrepreneurial intent, IP, team and business plan. Phase 1 improves reproducibility and candor of the technical evidence; it cannot supply missing partner commitments or founder qualifications. Assign named owners for metallurgy/thermodynamics, coatings/manufacturing, mechanical validation, ML/data governance and customer development. Obtain facility access letters and quotations before presenting a laboratory milestone as secured. Confirm the program's actual eligibility, budget and milestone terms directly with FITT; no grant outcome is guaranteed.
