"""Composition invariants, explicit mixture assumptions, and screening descriptors."""
import hashlib
import json
import re
import numpy as np

# Reference elemental estimates inherited from the original project, NOT alloy
# measurements. SI except mass (g/mol), density (g/cm3), radius (angstrom), E (GPa).
# Thermal constants are deliberately not disguised as high-temperature ML outputs.
ELEMENTS = ('Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf')
# mass, density, radius, VEC, melting K, CTE 1e-6/K, k W/m/K, Young GPa
VALUES = [
 (95.95,10.2,1.39,6,2896,4.8,138,329), (92.91,8.6,1.46,5,2750,7.3,53,105),
 (180.95,16.7,1.46,5,3290,6.3,57,186), (183.84,19.3,1.39,6,3695,4.5,173,411),
 (52.,7.2,1.28,6,2180,4.9,94,279), (50.94,6.,1.34,5,2183,8.4,31,128),
 (47.87,4.5,1.47,4,1941,8.6,22,116), (91.22,6.5,1.60,4,2128,5.8,23,88),
 (178.49,13.3,1.59,4,2506,5.9,23,78)]
PROPERTIES = ('mass','density','radius','vec','tm_K','alpha_micro_K','k_W_mK','E_GPa')
DATA = {el: dict(zip(PROPERTIES, vals)) for el, vals in zip(ELEMENTS, VALUES)}
PAIRS = {frozenset(k):v for k,v in {
 ('Mo','Nb'):-6, ('Mo','Ta'):-5, ('Mo','W'):0, ('Mo','Cr'):0,
 ('Nb','Ta'):0, ('Nb','W'):-8, ('Nb','Cr'):-7,
 ('Ta','W'):-7, ('Ta','Cr'):-7, ('W','Cr'):1}.items()}
TOKEN = re.compile(r'([A-Z][a-z]?)([0-9]+(?:\.[0-9]*)?|\.[0-9]+)?')


def fractions(value):
    """Validate an explicitly atomic-fraction mapping. Never silently renormalize."""
    if not isinstance(value, dict) or not value:
        raise ValueError('composition must be an atomic-fraction mapping')
    unknown = set(value) - set(ELEMENTS)
    if unknown:
        raise ValueError(f'unsupported elements: {sorted(unknown)}')
    out = {el: float(value.get(el, 0)) for el in ELEMENTS}
    a = np.array(list(out.values()))
    if not np.isfinite(a).all() or (a < 0).any() or abs(a.sum()-1) > 1e-8:
        raise ValueError('atomic fractions must be finite, nonnegative and sum to 1 within 1e-8')
    return out


def parse_stoichiometry(formula):
    """Normalize explicit stoichiometric coefficients, e.g. NbMo or Nb1 Mo1.

    This is NOT the API for a rounded atomic-fraction recipe: use fractions().
    Parentheses, wt%, annotations, and unknown elements require manual curation.
    """
    text = re.sub(r'\s+', '', str(formula))
    tokens = list(TOKEN.finditer(text))
    if not tokens or ''.join(m.group() for m in tokens) != text:
        raise ValueError('unsupported or incomplete stoichiometric formula')
    amounts = {}
    for m in tokens:
        el, raw = m.groups()
        if el not in ELEMENTS or el in amounts:
            raise ValueError(f'unsupported or repeated element: {el}')
        amount = float(raw) if raw else 1.
        if not np.isfinite(amount) or amount <= 0:
            raise ValueError('stoichiometric coefficients must be positive')
        amounts[el] = amount
    total = sum(amounts.values())
    return fractions({el: v/total for el,v in amounts.items()})


def canonical(comp):
    c = fractions(comp)
    return '|'.join(f'{el}:{c[el]:.8f}' for el in ELEMENTS)


def composition_id(comp):
    return hashlib.sha256(canonical(comp).encode()).hexdigest()[:16]


def encode(comp):
    return json.dumps({el:v for el,v in fractions(comp).items() if v > 0}, sort_keys=True)


def vector(comp):
    c = fractions(comp)
    return np.array([c[el] for el in ELEMENTS])


def features(comp, temperature_K=298.15, processing='CAST', yield_target=False):
    x = vector(comp)
    result = list(x)
    for prop in ['radius','vec','tm_K','mass']:
        p = np.array([DATA[e][prop] for e in ELEMENTS])
        avg = x @ p
        result.extend([avg, np.sqrt(x @ (p-avg)**2)])
    if yield_target:
        if processing not in ('CAST','WROUGHT','ANNEAL','OTHER','POWDER'):
            raise ValueError('unsupported processing method')
        if not np.isfinite(temperature_K) or temperature_K <= 0:
            raise ValueError('temperature must be positive kelvin')
        result.append(temperature_K - 273.15)
        result.extend(float(processing == p) for p in ('CAST','WROUGHT','ANNEAL','OTHER','POWDER'))
    return np.array(result, dtype=float)


def descriptors(comp):
    c = fractions(comp); x = vector(c)
    mass = np.array([DATA[e]['mass'] for e in ELEMENTS])
    rho = np.array([DATA[e]['density'] for e in ELEMENTS])
    # Atomic fractions -> additive molar volumes -> density, volume and mass bases.
    volumes = x * mass/rho
    vf = volumes / volumes.sum()
    mf = x * mass / (x @ mass)
    radius = np.array([DATA[e]['radius'] for e in ELEMENTS])
    active = [e for e in ELEMENTS if c[e] > 1e-12]
    missing = [(a,b) for i,a in enumerate(active) for b in active[i+1:] if frozenset((a,b)) not in PAIRS]
    hmix = None if missing else sum(4*c[a]*c[b]*PAIRS[frozenset((a,b))]
                                  for i,a in enumerate(active) for b in active[i+1:])
    return {
      'density_g_cm3': float((x @ mass)/volumes.sum()),
      'delta_percent': float(100*np.sqrt(x @ (1-radius/(x@radius))**2)),
      'vec': float(x @ np.array([DATA[e]['vec'] for e in ELEMENTS])),
      'ideal_entropy_J_molK': float(-8.314462618*np.sum(x[x>0]*np.log(x[x>0]))),
      'hmix_kJ_mol': hmix, 'missing_binary_pairs': [list(p) for p in missing],
      'mass_fractions':dict(zip(ELEMENTS, mf.tolist())),
      'volume_fractions':dict(zip(ELEMENTS, vf.tolist())),
      'alpha_1_K':float(vf @ np.array([DATA[e]['alpha_micro_K'] for e in ELEMENTS]))*1e-6,
      'k_W_mK':float(1/(vf @ (1/np.array([DATA[e]['k_W_mK'] for e in ELEMENTS])))),
      'E_Pa':float(1/(vf @ (1/np.array([DATA[e]['E_GPa'] for e in ELEMENTS]))))*1e9,
      'phase_status':'unverified: empirical descriptors are not phase identification',
      'oxidation_status':'unverified: no oxidation kinetics or protective-scale measurement'}
