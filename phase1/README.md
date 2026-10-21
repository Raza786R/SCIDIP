# Crystal Paradigm — HE-MCGA Phase 1

This is the maintained, reproducible computational workflow. It replaces the historical executable pipeline in `Saffron-Aero/scripts/`. The submitted Office files in `IIT DELHI LATEST/` are preserved as submission records; their scientific claims have **not** all been reconciled with this implementation.

**Current result:** a tested inverse-screening and measurement-feedback implementation, with new unmeasured candidates. It is not a qualified aerospace material, a validated coating, a completed experimental closed loop, or demonstrated customer ROI.

## Read in this order

1. [Phase 1 report](docs/PHASE1_REPORT.md): actual fixes, results and rejection risks.
2. [Workflow and equations](docs/WORKFLOW_AND_MODELS.md): inputs, models, optimization, outputs and feedback.
3. [Data and model card](docs/DATA_MODEL_CARD.md): sample counts, protected splits and uncertainty.
4. [Fix register](docs/FIX_REGISTER.csv): every substantive correction and its evidence.
5. [Validation plan](docs/VALIDATION_PLAN.md): what remains to be measured or simulated.
6. [Sona pilot and business case](docs/SONA_PILOT_AND_BUSINESS.md): a specific sponsor hypothesis and assumptions.
7. [Panel claim guide](docs/CLAIMS_FOR_PANEL.md): what the current evidence supports.
8. [Primary sources](docs/SOURCES.md).

## Install and reproduce

Run from the repository root with Python 3.12. No API credentials, paid services, GPU, archived pickle or new dataset download is needed for the main run.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e . -c phase1/constraints-tested.txt
python -m unittest discover -s phase1/tests -v
python -m he_mcga run --config phase1/configs/aerospace_legacy_K.json --output phase1/results/my_aerospace_run
python -m he_mcga run --config phase1/configs/sona_tooling_hypothesis.json --output phase1/results/my_sona_run
```

Without installation, prefix commands with `PYTHONPATH=phase1`. The CLI refuses an existing output directory. Use a new directory for each generation. Tested direct dependency versions are recorded in `constraints-tested.txt`; each run also records actual versions, input hashes, code hashes and its base commit. Platform differences may cause small numerical differences; deterministic equality was checked twice in this environment.

Checked outputs are in [aerospace reference](results/aerospace_reference/) and [Sona coupon reference](results/sona_coupon_reference/). Each contains metrics, accepted/rejected source rows, held-out predictions, all search evaluations, feasible candidates, a shortlist, a diverse proposed measurement batch, exact-composition coupon recipe, sensitivity and mesh studies, readiness gates and a manifest. Two seeded searches evaluate **594 DE + 594 random points each**. The optimizer reaches its declared iteration budget; it does not establish a global optimum.

## Measured feedback and retraining

1. Use `proposed_measurement_batch.csv` to specify specimens; agree the test protocol and processing with a lab. The CSV is a proposal, not evidence that specimens exist.
2. Create real reports inside a suitable repository-relative evidence directory (respect data ownership before publication). Complete the fields in [measurement template](configs/measurement_template.json); replace every placeholder and set `is_synthetic` to `false` only for genuine measurements.
3. Ingest and run a new generation:

```bash
python -m he_mcga ingest --measurements my_lab_measurements.json --ledger phase1/measurements/ledger.json
python -m he_mcga run --config phase1/configs/aerospace_legacy_K.json --feedback phase1/measurements/ledger.json --output phase1/results/generation_2
```

Only supported, provenance-backed bulk-modulus or compression-yield measurements can enter training. Composition hash partitions protect the calibration and test groups. A protected-group measurement must remain external validation evidence; the CLI rejects it as training feedback. Evidence files must exist and match their SHA-256 checksum. Atomic fractions, units, positive absolute temperature, specimen identity, processing and duplicate measurements are checked. A batch is committed to the ledger only if every record passes. Evidence checksums are verified again on retraining.

No real new lab feedback was available in Phase 1. Automated temporary fixtures verify software behavior; they are not included in reported scientific runs. This closes the **software path**, not the experimental loop.

## CALPHAD

```bash
python -m pip install -e '.[calphad]' -c phase1/constraints-tested.txt
python phase1/tools/run_calphad_adapter_check.py --output phase1/results/my_adapter_check.json
python -m he_mcga calphad --database /path/to/assessed_licensed_database.tdb --composition my_atomic_fractions.json --temperatures-K 1000 1400 --provenance 'database citation, version, license and assessed applicability' --output my_equilibrium.json
```

The bundled integration check performs real Al–Ni equilibrium calculations using pycalphad's distributed test database. **It is not a target-alloy CALPHAD result.** No suitable assessed target-alloy database has been supplied. The adapter refuses absent databases, missing components, unbalanced compositions and failed phase-fraction balance; it includes all compatible database phases and leaves one chemical component dependent. Presence of elements in a TDB is necessary but does not establish adequate multicomponent assessment.

## Historical paths

Legacy report/optimizer/training entry points now stop with a migration command, preventing old scripts from overwriting recipes or emitting unsupported safety claims. Historical function bodies and output files remain for audit; they are not maintained APIs. `run_1d_fea.py` is a compatibility adapter to the revised laminate model and explicitly returns **in-plane** stress. The API-key fetch helper reads only `MP_API_KEY`; online dataset refresh is outside the checked run and requires a separate curated export with provenance.
