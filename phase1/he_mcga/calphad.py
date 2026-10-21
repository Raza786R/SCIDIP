"""Optional assessed-database equilibrium adapter. Missing evidence fails closed."""
import hashlib
from pathlib import Path
import numpy as np


def equilibrate(database,comp,temperatures_K,provenance):
    # Generic mapping allows binary integration tests beyond the search alphabet.
    path=Path(database)
    if not path.is_file(): raise ValueError('CALPHAD database absent; no phase result can be claimed')
    if not isinstance(provenance,str) or not provenance.strip():
        raise ValueError('database citation/license/assessment provenance is required')
    c={str(k).upper():float(v) for k,v in comp.items() if float(v)>0}
    if 'VA' in c: raise ValueError('vacancy is not an independent alloy mole-fraction component')
    if len(c)!=len([v for v in comp.values() if float(v)>0]) or not c:
        raise ValueError('duplicate or empty component mapping')
    if any(not np.isfinite(float(v)) or float(v)<0 for v in comp.values()) or abs(sum(c.values())-1)>1e-8:
        raise ValueError('CALPHAD atomic fractions must sum to one')
    temps=np.array(temperatures_K,dtype=float)
    if temps.size==0 or not np.isfinite(temps).all() or (temps<=0).any(): raise ValueError('positive K temperatures required')
    from pycalphad import Database,equilibrium,variables as v
    from pycalphad.core.utils import filter_phases
    import pycalphad
    db=Database(str(path))
    if set(c)-db.elements: raise ValueError(f'database lacks components: {sorted(set(c)-db.elements)}')
    comps=sorted(c)+(['VA'] if 'VA' in db.elements else [])
    phases=sorted(filter_phases(db,comps))
    if not phases: raise ValueError('database contains no compatible phases')
    dependent=sorted(c)[-1]
    conditions={v.P:101325,v.N:1,v.T:temps.tolist()}
    conditions.update({v.X(e):f for e,f in c.items() if e!=dependent})
    eq=equilibrium(db,comps,phases,conditions)
    results=[]
    for temp in temps:
        point=eq.sel(T=temp)
        names=np.asarray(point.Phase.values).ravel(); amounts=np.asarray(point.NP.values).ravel()
        if names.size!=amounts.size: raise ValueError('unexpected equilibrium dimensions')
        totals={}
        for phase,amount in zip(names,amounts):
            if phase and np.isfinite(amount) and amount>1e-10:
                totals[str(phase)]=totals.get(str(phase),0)+float(amount)
        if not totals or abs(sum(totals.values())-1)>1e-5: raise ValueError('equilibrium failed phase-fraction balance')
        results.append({'temperature_K':float(temp),'phase_mole_fractions':totals})
    return {'database_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'database_provenance':provenance,'pycalphad_version':pycalphad.__version__,
            'components':comps,'dependent_component':dependent,'entered_phases':phases,
            'results':results,'limit':'Equilibrium within supplied database/phase descriptions, not kinetic or experimental validation.'}
