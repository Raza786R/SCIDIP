"""Curate source rows without synthetic fallback or room-temperature imputation."""
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from .composition import parse_stoichiometry, composition_id, encode, features


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def curate(root, target):
    root = Path(root)
    name = 'raw_materials_project.csv' if target=='bulk' else 'EXP-MPEA_dataset.csv'
    path = root/'Saffron-Aero/data'/name
    raw = pd.read_csv(path); accepted = []; rejected = []
    temp_col = next((c for c in raw.columns if 'Test temperature' in c),None)
    for i,row in raw.iterrows():
        try:
            formula = row['formula' if target=='bulk' else 'FORMULA']
            comp = parse_stoichiometry(formula)
            y = float(row['bulk_modulus' if target=='bulk' else 'PROPERTY: YS (MPa)'])
            if not np.isfinite(y) or y<=0:
                raise ValueError('missing/nonpositive target')
            if target=='bulk':
                shear = float(row['shear_modulus'])
                if not np.isfinite(shear) or shear<=0:
                    raise ValueError('missing/nonpositive shear modulus: unstable or unverified elasticity')
                temp = None; processing = 'not_applicable'; source = 'materials_project_local_export_static_DFT'
            else:
                if row['PROPERTY: Type of test'] != 'C':
                    raise ValueError('compression-only model: tensile/unknown test mode excluded')
                temp = float(row[temp_col])+273.15
                if not np.isfinite(temp) or temp<=0:
                    raise ValueError('missing/invalid test temperature; no imputation')
                processing = str(row['PROPERTY: Processing method'])
                if processing not in ('CAST','WROUGHT','ANNEAL','OTHER','POWDER'):
                    raise ValueError('missing/unknown processing method')
                source = str(row['REFERENCE: doi'])
                if source in ('nan',''):
                    raise ValueError('missing publication provenance')
            accepted.append({'row_id':f'{name}:{i+2}','composition_id':composition_id(comp),
                             'formula_source':formula,'atomic_fractions':encode(comp),
                             'target':y,'temperature_K':temp,'processing':processing,
                             'source':source,'source_row_1based':i+2})
        except (ValueError,TypeError,KeyError) as exc:
            rejected.append({'row_id':f'{name}:{i+2}','reason':str(exc)})
    data = pd.DataFrame(accepted)
    if data.empty or data.composition_id.nunique()<10:
        raise ValueError('insufficient real composition groups; synthetic fallback disabled')
    return data, pd.DataFrame(rejected), {'path':str(path.relative_to(root)), 'sha256':sha256(path),
            'source_rows':len(raw),'accepted_rows':len(data),'rejected_rows':len(rejected)}


def matrix(data, target):
    import json
    return np.array([features(json.loads(r.atomic_fractions),r.temperature_K,
                             r.processing,target=='yield') for r in data.itertuples()])


def partition(groups, seed=42):
    """Stable hash partition, independent of targets and future feedback rows."""
    def one(g):
        n = int(hashlib.sha256(f'{seed}:{g}'.encode()).hexdigest()[:8],16)%10
        return 'test' if n<2 else ('calibration' if n<4 else 'train')
    return np.array([one(g) for g in groups])
