# Crystal Paradigm — HE-MCGA / SCIDIP

**Current computational work:** [Phase 1 implementation, results and documentation](phase1/README.md).

**Start with:** [Phase 1 report](phase1/docs/PHASE1_REPORT.md), [workflow and models](phase1/docs/WORKFLOW_AND_MODELS.md), and [fix register](phase1/docs/FIX_REGISTER.csv).

The maintained package performs reproducible material/gradient screening and supports real measurement ingestion and retraining. Thirty scientific/software checks pass. Current candidates are unmeasured hypotheses; aerospace qualification, target-alloy CALPHAD, oxidation protection, physical closed-loop improvement and customer ROI are not established.

`IIT DELHI LATEST/` preserves the submitted/current Office document versions. Their historical claims must be reconciled with the Phase 1 evidence before final pitching. Patent/document refinement and pitch preparation remain later phases.

## Repository map

| Path | Authority and purpose |
|---|---|
| `phase1/` | Maintained computational implementation, tests, configs, checked results and evidence/validation documents |
| `IIT DELHI LATEST/` | Preserved submission documents; not executable proof of their claims |
| `Saffron-Aero/data/` | Existing source exports; curated reads/hashes recorded by Phase 1 |
| `Saffron-Aero/scripts/` | Historical entry points; most stop with migration instructions; thermal adapter retained |
| `Saffron-Aero/runs/`, `models/`, `phase_wise_analysis/` | Historical artifacts; not Phase 1 validation evidence |
| `IIT_DELHI_SCIDIP/`, `references_and_guides/`, `archive/` | Earlier submissions, references and audit history |

## Reproduce Phase 1

```bash
python -m pip install -e . -c phase1/constraints-tested.txt
python -m unittest discover -s phase1/tests -v
python -m he_mcga run --config phase1/configs/aerospace_legacy_K.json --output phase1/results/my_run
```

See [phase1/README.md](phase1/README.md) for a virtual environment, Sona coupon profile, optional CALPHAD, measured feedback, exact results and limits. Use a new output directory for each run. Existing submitted Office files and source CSVs were not overwritten.
