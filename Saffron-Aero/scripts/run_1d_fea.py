"""Compatibility adapter to the verified reduced laminate model.

The historical filename is retained. This is not 3-D FEA or interface shear.
Use phase1/he_mcga/thermal.py for explicit boundary conditions and layer results.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'phase1'))
from he_mcga.thermal import laminate

L_GRADIENT=.005
NODES=81
T_COLD=300.
T_HOT=1400.  # K, not degrees C


def solve_1d_thermoelastic_surrogate(hea_E,hea_alpha,hea_k,ceramic_type='ZrO2-HfO2',
                                    n_exponent=1.,grain_size=1e-6):
    """Return peak IN-PLANE stress MPa for a freely curving bonded laminate.

    Kept for source compatibility. Grain-size-dependent creep is not modeled.
    No empirical relaxation or edge concentration multiplier is applied.
    """
    if grain_size != 1e-6:
        raise ValueError('Grain size has no calibrated constitutive law; creep is not modeled')
    return laminate(hea_E,hea_alpha,hea_k,L_GRADIENT,n_exponent,ceramic_type,
                    NODES-1,T_COLD,T_HOT,T_COLD)['peak_inplane_stress_MPa']


def extract_coble_creep_stress(*args,**kwargs):
    raise NotImplementedError('Creep requires diffusion/activation/grain-size data and a time-dependent law; fixed relaxation removed')

if __name__=='__main__':
    print('Reduced laminate screening: peak in-plane stress (NOT interface stress or safety factor), MPa:')
    print(solve_1d_thermoelastic_surrogate(210e9,5.5e-6,50,ceramic_type='LZO',n_exponent=2))
