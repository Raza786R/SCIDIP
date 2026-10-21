"""Prevent old scripts from overwriting recipes or emitting unvalidated claims."""
def stop_legacy_entrypoint(path):
    from pathlib import Path
    raise SystemExit(
        f'{Path(path).name} is a historical entry point and has been superseded.\n'
        'From the repository root run:\n'
        '  PYTHONPATH=phase1 python -m he_mcga run '
        '--config phase1/configs/aerospace_legacy_K.json --output phase1/results/my_run\n'
        'See phase1/README.md for evidence limits, CALPHAD and measured feedback.'
    )
