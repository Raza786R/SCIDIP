"""Steady through-thickness conduction and bonded laminate thermoelasticity.

Cold metal face z=0; hot ceramic face z=L. Piecewise-constant properties,
perfect bonding, small strain, equibiaxial plane stress, unit width. This is
not an interfacial shear/fracture, creep, fatigue, transient or 3-D FEA model.
"""
import numpy as np

CERAMICS = {
 'LZO': {'E_Pa':175e9, 'alpha_1_K':9.1e-6, 'k_W_mK':1.6, 'nu':.25},
 'GZO': {'E_Pa':180e9, 'alpha_1_K':11.6e-6, 'k_W_mK':1.5, 'nu':.25},
 'ZrO2-HfO2': {'E_Pa':200e9, 'alpha_1_K':11e-6, 'k_W_mK':2., 'nu':.25}}


def laminate(E_Pa, alpha_1_K, k_W_mK, thickness_m=.005, exponent=1.,
             ceramic='LZO', cells=80, cold_face_K=300., hot_face_K=1400.,
             stress_free_K=300., constraint='free_curvature', metal_nu=.30,
             membrane_N_m=0., moment_N=0., ceramic_fractions=None, layer_edges_m=None):
    nums = [E_Pa, alpha_1_K, k_W_mK, thickness_m, exponent, cold_face_K,
            hot_face_K, stress_free_K, metal_nu, membrane_N_m, moment_N]
    if not np.isfinite(nums).all() or min(E_Pa,k_W_mK,thickness_m,exponent,cold_face_K,hot_face_K,stress_free_K)<=0:
        raise ValueError('invalid/nonfinite material, geometry or temperature input')
    if not isinstance(cells,int) or cells < 2 or not -1 < metal_nu < .5:
        raise ValueError('cells >=2 and -1 < Poisson ratio <0.5 required')
    if constraint not in ('free_curvature','flat_force_free'):
        raise ValueError('explicit mechanical constraint required')
    if constraint == 'flat_force_free' and moment_N != 0:
        raise ValueError('flat constraint has a reaction moment; do not prescribe moment')
    cer = CERAMICS[ceramic]
    edges = np.linspace(0,thickness_m,cells+1) if layer_edges_m is None else np.asarray(layer_edges_m,dtype=float)
    if edges.shape!=(cells+1,) or not np.isfinite(edges).all() or np.any(np.diff(edges)<=0) or not np.isclose(edges[0],0,atol=1e-12) or not np.isclose(edges[-1],thickness_m,rtol=0,atol=1e-12):
        raise ValueError('layer edges must span the positive thickness monotonically')
    dz = np.diff(edges)
    z = (edges[1:]+edges[:-1])/2
    # Exact layer-average ceramic fraction conserves the continuous gradient's
    # total ceramic volume even for coarse manufacturing layers and n < 1.
    f = ((edges[1:]/thickness_m)**(exponent+1)-(edges[:-1]/thickness_m)**(exponent+1))/((exponent+1)*dz/thickness_m)
    if ceramic_fractions is not None:
        f=np.asarray(ceramic_fractions,dtype=float)
        if f.shape!=(cells,) or not np.isfinite(f).all() or np.any((f<0)|(f>1)):
            raise ValueError('one ceramic volume fraction in [0,1] required per layer')
    E = 1/((1-f)/E_Pa+f/cer['E_Pa'])
    alpha = (1-f)*alpha_1_K+f*cer['alpha_1_K']
    k = 1/((1-f)/k_W_mK+f/cer['k_W_mK'])
    nu = (1-f)*metal_nu+f*cer['nu']; Q = E/(1-nu)
    resistance = dz/k
    flux = (hot_face_K-cold_face_K)/resistance.sum()  # magnitude toward -z
    T_edges = cold_face_K+flux*np.r_[0,np.cumsum(resistance)]
    # Two-point Gauss integration exactly integrates layerwise Q*z^2 and
    # thermal eigenstrain moments when T is linear within each layer.
    zg = z[:,None]+dz[:,None]/(2*np.sqrt(3))*np.array([-1,1])
    zz = zg-thickness_m/2
    Tg = T_edges[:-1,None]+flux/k[:,None]*(zg-edges[:-1,None])
    w = dz[:,None]/2*np.ones((1,2))
    q = Q[:,None]; eig = alpha[:,None]*(Tg-stress_free_K)
    A = np.sum(w*q); B = np.sum(w*q*zz); D = np.sum(w*q*zz**2)
    NT = np.sum(w*q*eig); MT = np.sum(w*q*eig*zz)
    if constraint == 'free_curvature':
        eps, curvature = np.linalg.solve([[A,B],[B,D]], [NT+membrane_N_m,MT+moment_N])
    else:
        eps, curvature = (NT+membrane_N_m)/A, 0.
    sg = q*(eps+curvature*zz-eig)
    N = float(np.sum(w*sg)); M = float(np.sum(w*sg*zz))
    # Evaluate both sides of each layer (stress is discontinuous across a
    # material interface). Never label these in-plane stresses interface shear.
    zs = np.stack([edges[:-1],edges[1:]],axis=1)-thickness_m/2
    Ts = np.stack([T_edges[:-1],T_edges[1:]],axis=1)
    sigma = Q[:,None]*(eps+curvature*zs-alpha[:,None]*(Ts-stress_free_K))
    return {
      'peak_inplane_stress_MPa':float(np.max(np.abs(sigma))/1e6),
      'peak_tensile_MPa':float(max(0,sigma.max())/1e6),
      'peak_compressive_MPa':float(max(0,-sigma.min())/1e6),
      'heat_flux_W_m2':float(flux), 'curvature_1_m':float(curvature),
      'membrane_strain':float(eps), 'force_residual_N_m':N-membrane_N_m,
      'moment_residual_N':M-moment_N if constraint=='free_curvature' else None,
      'flat_reaction_moment_N':M if constraint=='flat_force_free' else None,
      'metal_face_K':float(T_edges[0]), 'ceramic_face_K':float(T_edges[-1]),
      'constraint':constraint, 'model':'steady_conduction_equibiaxial_laminate',
      'layers':[{'layer':i+1,'z_start_m':float(edges[i]),'z_end_m':float(edges[i+1]),
                 'ceramic_volume_fraction':float(f[i]),'metal_volume_fraction':float(1-f[i]),
                 'temperature_center_K':float((T_edges[i]+T_edges[i+1])/2),
                 'inplane_stress_cold_side_MPa':float(sigma[i,0]/1e6),
                 'inplane_stress_hot_side_MPa':float(sigma[i,1]/1e6)} for i in range(cells)]}
