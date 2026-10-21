# Crystal Paradigm — HE-MCGA / SCIDIP

**Current work:** [Phase 2 documentation, second audit and updated results](phase2/README.md).

**Start with:** [Project handbook](phase2/docs/00_Project_Handbook.docx), then the ten-document reading order in [Phase 2](phase2/README.md). The [Phase 1 report](phase1/docs/PHASE1_REPORT.md) preserves the first repair history.

The maintained package performs reproducible material/gradient screening and supports real measurement ingestion and retraining. **37 scientific/software checks pass.** Version 0.2.0 adds applicability-gated strength reward, an areal-mass objective term, stronger feedback validation and matched architecture controls. Current candidates are unmeasured hypotheses; aerospace qualification, target-alloy CALPHAD, oxidation protection, physical closed-loop improvement and customer ROI are not established.

`IIT DELHI LATEST/` preserves the submitted Office document versions. Use the Phase 2 claim reconciliation before repeating historical claims. Patent drafting and the final pitch deck follow the current documentation phase.

## Repository map

| Path | Authority and purpose |
|---|---|
| `phase1/` | Maintained computational implementation, tests, configs, checked results and evidence/validation documents |
| `phase2/` | Current 0.2.0 results, DOCX teaching pack, second audit, controls, budget and source records |
| `IIT DELHI LATEST/` | Preserved submission documents; not executable proof of their claims |
| `Saffron-Aero/data/` | Existing source exports; curated reads/hashes recorded by Phase 1 |
| `Saffron-Aero/scripts/` | Historical entry points; most stop with migration instructions; thermal adapter retained |
| `Saffron-Aero/runs/`, `models/`, `phase_wise_analysis/` | Historical artifacts; not Phase 1 validation evidence |
| `IIT_DELHI_SCIDIP/`, `references_and_guides/`, `archive/` | Earlier submissions, references and audit history |

## Run the current workflow

```bash
python -m pip install -e . -c phase1/constraints-tested.txt
python -m unittest discover -s phase1/tests -v
python -m he_mcga run --config phase2/sources/aerospace_legacy_K_v2.json --output phase2/results/my_run
```

See [phase2/README.md](phase2/README.md) for current runs and documentation. The package remains under `phase1/he_mcga` to preserve imports. Phase 1 result files are frozen; reproducing those exact historical results requires commit `2bd2885`, since current code uses a revised objective. Use a new output directory for every run. Existing submitted Office files and source CSVs were not overwritten.
