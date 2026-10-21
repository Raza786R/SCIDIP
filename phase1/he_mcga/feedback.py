"""Real measurement ingestion; explicit provenance and protected benchmark groups."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .composition import fractions,composition_id,encode
from .data import partition

REQUIRED = {'measurement_id','atomic_fractions','property','value','unit','temperature_K',
            'test_mode','processing','source','specimen_id','evidence_path','evidence_sha256',
            'measurement_uncertainty','is_synthetic'}


def ingest(path,ledger_path,root,seed=42):
    import hashlib
    from .data import curate
    path=Path(path); ledger_path=Path(ledger_path); root=Path(root).resolve()
    records=json.loads(path.read_text())
    if not isinstance(records,list) or not records: raise ValueError('expected nonempty JSON list')
    old=json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    ids={r['measurement_id'] for r in old}; output=[]
    for raw in records:
        if not REQUIRED<=set(raw): raise ValueError(f'missing fields: {sorted(REQUIRED-set(raw))}')
        if raw['is_synthetic'] is not False: raise ValueError('synthetic measurements cannot enter the real feedback ledger')
        if not all(isinstance(raw[k],str) and raw[k].strip() for k in ['measurement_id','source','specimen_id','evidence_path','evidence_sha256']):
            raise ValueError('measurement, specimen and evidence provenance required')
        if raw['measurement_id'] in ids: raise ValueError('duplicate measurement_id')
        comp=fractions(raw['atomic_fractions']); cid=composition_id(comp)
        if partition([cid],seed)[0] != 'train':
            raise ValueError('protected test/calibration composition; retain as external evidence, not training feedback')
        if raw['property'] not in ('compression_yield','bulk_modulus'): raise ValueError('unsupported property')
        target='yield' if raw['property']=='compression_yield' else 'bulk'
        unit='MPa' if target=='yield' else 'GPa'
        if raw['unit']!=unit: raise ValueError(f'unit must be {unit}; convert explicitly')
        value=float(raw['value']); temp=float(raw['temperature_K']); uncertainty=float(raw['measurement_uncertainty'])
        if not np.isfinite([value,temp,uncertainty]).all() or min(value,temp)<=0 or uncertainty<0:
            raise ValueError('invalid measured value, temperature or uncertainty')
        if target=='yield' and (raw['test_mode']!='compression' or raw['processing'] not in ('CAST','WROUGHT','ANNEAL','OTHER','POWDER')):
            raise ValueError('compression test and supported processing required')
        if target=='bulk' and (raw['test_mode']!='elasticity' or not 273.15<=temp<=323.15):
            raise ValueError('bulk feedback requires near-ambient elasticity; model has no bulk temperature dependence')
        evidence=(root/raw['evidence_path']).resolve()
        if not evidence.is_relative_to(root) or not evidence.is_file(): raise ValueError('evidence file must exist inside repository')
        digest=hashlib.sha256(evidence.read_bytes()).hexdigest()
        if digest!=raw['evidence_sha256']: raise ValueError('evidence checksum mismatch')
        source_data,_,_=curate(root,target)
        # Same specimen/source/temp/property cannot masquerade as an independent repeat.
        if any(r['specimen_id']==raw['specimen_id'] and r['property']==raw['property']
               and r['temperature_K']==temp for r in old+output): raise ValueError('duplicate specimen/property/temperature')
        if ((source_data.composition_id==cid)&(source_data.source==raw['source'])&
            np.isclose(source_data.temperature_K,temp)).any(): raise ValueError('measurement already represented by source export')
        record={**raw,'atomic_fractions':comp,'composition_id':cid,'target_name':target,
                'value':value,'temperature_K':temp,'measurement_uncertainty':uncertainty}
        output.append(record); ids.add(raw['measurement_id'])
    ledger_path.parent.mkdir(parents=True,exist_ok=True)
    # Atomic replacement only after every record passes validation.
    temp_path=ledger_path.with_suffix('.tmp')
    temp_path.write_text(json.dumps(old+output,indent=2)+'\n'); temp_path.replace(ledger_path)
    return len(output)


def augment(data,ledger,target,seed=42,root=None):
    if not ledger: return data
    records=json.loads(Path(ledger).read_text()); additions=[]
    for r in records:
        if r['target_name']!=target: continue
        if r['is_synthetic'] is not False: raise ValueError('synthetic feedback rejected')
        comp=fractions(r['atomic_fractions']); cid=composition_id(comp)
        if root is not None:
            from .data import sha256
            evidence=(Path(root)/r['evidence_path']).resolve()
            if not evidence.is_relative_to(Path(root).resolve()) or not evidence.is_file() or sha256(evidence)!=r['evidence_sha256']:
                raise ValueError('feedback evidence missing or changed since ingestion')
        if partition([cid],seed)[0]!='train': raise ValueError('feedback would contaminate protected benchmark')
        additions.append({'row_id':'measurement:'+r['measurement_id'],'composition_id':cid,
               'formula_source':'measured_atomic_fractions','atomic_fractions':encode(comp),
               'target':r['value'],'temperature_K':r['temperature_K'],
               'processing':r['processing'] if target=='yield' else 'not_applicable',
               'source':r['source'],'source_row_1based':None})
    return pd.concat([data,pd.DataFrame(additions)],ignore_index=True) if additions else data
