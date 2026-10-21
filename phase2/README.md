# Crystal Paradigm — HE-MCGA Phase 2

This is the current technical reference for the SCIDIP preparation. It combines a second strict audit, six focused computational repairs, new traceable screening runs and a ten-document teaching pack. Patent drafting and the final pitch deck are subsequent tasks.

## Read in this order

| File | Purpose |
|---|---|
| [00 Project Handbook](docs/00_Project_Handbook.docx) | Start here: problem, workflow, current evidence and version authority |
| [01 Materials Science Deep Dive](docs/01_Materials_Science_Deep_Dive.docx) | Composition, phases, microstructure, processing and failure mechanisms |
| [02 Data and AI Models](docs/02_Data_and_AI_Models.docx) | Actual datasets, features, benchmark and uncertainty |
| [03 Inverse Design and Closed Loop](docs/03_Inverse_Design_and_Closed_Loop.docx) | Objective, constraints, selection and real feedback rules |
| [04 Simulation and Evidence](docs/04_Simulation_and_Evidence.docx) | Executed equations, matched controls and verification limits |
| [05 Manufacturing and Recipe](docs/05_Manufacturing_and_Recipe.docx) | Metal recipe, eleven layers and process feasibility |
| [06 Validation and IIT Delhi Collaboration](docs/06_Validation_and_IIT_Delhi_Collaboration.docx) | Proposed experiments, realistic facility inquiries and responsibilities |
| [07 Business Budget and Milestones](docs/07_Business_Budget_and_Milestones.docx) | Customer hypothesis, INR 65 lakh estimate and expenditure gates |
| [08 Founder Preparation and Program Call](docs/08_Founder_Preparation_and_Program_Call.docx) | Call interpretation and panel rehearsal |
| [09 Strict Audit and IP Handover](docs/09_Strict_Audit_and_IP_Handover.docx) | Repairs, remaining rejection risks and next-phase disclosure records |

Editable text sources are under `sources/`. The generated documents use actual result files rather than manually retyped candidate tables. Historical submitted Office files were preserved.

## What changed

1. An inapplicable strength lower bound earns no search reward.
2. A declared areal-mass term makes thickness/mass preference explicit.
3. Reading a feedback ledger revalidates its measurement and evidence records before retraining.
4. Duplicate checks handle static bulk records without a measured temperature.
5. Proposed measurements state their benchmark partition and whether they may enter training.
6. A sharp bilayer control matches chemistry, thickness and phase volumes under both mechanical constraints.

The maintained package is **0.2.0**, still located at `phase1/he_mcga`. The 37 checks pass with no skips; see [verification record](results/verification_tests.txt). GitHub Actions watches both phases, but no remote CI success is claimed before publication.

## Current results and limits

| Screen | Candidate | Thickness mm | Peak in-plane stress MPa | Areal mass kg/m2 |
|---|---|---:|---:|---:|
| Aerospace illustrative free-curvature case | `f7e518dab2c27fee` | 1.494 | 236.7 | 10.183 |
| Sona tooling coupon hypothesis, flat case | `9e679fd6960bf72a` | 0.835 | 554.1 | 6.043 |

Each screen evaluates 594 differential-evolution and 594 seeded random points. Neither establishes a global optimum. The protected compression-yield benchmark is unchanged: MAE 229.5 MPa, R² 0.457. Both selected candidates have **zero eligible strength lower bound**. No strength advantage is established.

The aerospace graded/sharp peaks are 236.7/406.3 MPa when free to curve and 1389.9/1475.0 MPa when flat. Equal phase volume gives identical thermal resistance under the current harmonic/series assumptions. The comparison concerns calculated mechanical redistribution; it is not a measured lifetime improvement.

No new physical measurements, target-alloy DFT, target-alloy assessed CALPHAD result, 3D component validation, creep life or production tooling approval were generated. The Al–Ni CALPHAD fixture verifies the adapter only. Sona relevance is a proposed tooling research discussion, not a signed pilot. All budget amounts are estimates requiring quotations; milestone expenditure is not an approved grant release schedule.

## Reproduce

From the repository root, use Python 3.12 and a fresh environment:

```bash
python -m pip install -e '.[calphad]' -c phase1/constraints-tested.txt
python -m unittest discover -s phase1/tests -v
python -m he_mcga run --config phase2/sources/aerospace_legacy_K_v2.json --output phase2/results/my_aerospace_run
python -m he_mcga run --config phase2/sources/sona_tooling_hypothesis_v2.json --output phase2/results/my_sona_run
python phase2/tools/build_control_study.py
```

`build_control_study.py` reads the committed reference runs. Use a new output directory for each CLI run. Main screening does not require CALPHAD installation; the optional dependency enables the adapter verification test without a skip. Feedback commands and schema remain documented in `phase1/README.md` and `phase1/docs/WORKFLOW_AND_MODELS.md`; all current eligibility checks apply.

Each run's `manifest.json` records exact source/config/code/output hashes, dependency versions and the base commit. The run occurred on an uncommitted working tree based on Phase 1; its code hashes identify the implementation. Phase 1 outputs remain immutable, and older objective scores must not be mixed with new candidate chemistry.

## Evidence and document generation

- `results/aerospace_v2/` and `results/sona_v2/`: full new runs, candidate vectors, protected predictions, measurement batches, eleven-layer recipes and assumption studies.
- `results/graded_bilayer_controls.csv`: matched architecture controls.
- `results/claim_reconciliation.csv`: 20 historical assertions, present status and required evidence.
- `results/milestone_budget_INR_lakh.csv`: head and milestone reconciliation to INR 65 lakh.
- `results/second_review_register.csv`: correction-to-code-and-test mapping.
- `results/document_QA.json`: final document page counts and review record.
- `sources/references.json`: source registry, including supplied call notes and limitations on live retrieval.

Document generation additionally requires `python-docx`, `pandas`, `Pillow` and Matplotlib. Equation rendering uses Node with `mathjax-full` and `sharp`; point `HEMCGA_DOC_NODE_MODULES` to the directory containing `mathjax-full` and `CODEX_PRIMARY_RUNTIME_NODE_MODULES` to the directory containing `sharp`, or adapt these environment paths to your installation.

```bash
node phase2/tools/build_equations.cjs
python phase2/tools/build_figures.py
python phase2/tools/build_documents.py
```

Generated equation PNGs are committed, so regenerating prose alone needs only `build_documents.py`. DOCX files were rendered and visually checked page by page before delivery. Raw user attachments and internal render previews are not added to Git.

## Publication status

Prepared on branch `codex/phase2-documentation`, including the Phase 1 implementation commit. The connected account `Mahaboob-Ashraf` can read `Raza786R/SCIDIP` but the repository reports `push: false`. A branch creation attempt returned HTTP 403, Resource not accessible by integration. Publication remains pending collaborator/integration write access. The delivery bundle allows an authorized owner to fetch this exact branch; no main-branch overwrite is required.
