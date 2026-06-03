"""
1D Reduced-Order Finite Element Analysis (FEA) for HE-MCGA
Solves thermo-elasticity across a 5mm gradient with Coble creep approximation.

To be executed on a Bohrium FEniCS container or local WSL instance.
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Placeholder for FEniCS modules
try:
    import dolfin as df
    FENICS_AVAILABLE = True
except ImportError:
    FENICS_AVAILABLE = False
    print("WARNING: FEniCS (dolfin) not found. This script will only run via numpy surrogate or in a dedicated container.")

# --- Constants & Boundaries ---
L_GRADIENT = 5e-3  # 5 mm thickness
NODES = 51         # 0.1 mm spacing down the gradient
T_COLD = 300       # Kelvin
T_HOT = 1400       # Kelvin (Operating peak)

CERAMIC_MATERIALS = {
    'ZrO2-HfO2': {'k': 2.0, 'alpha': 11.0e-6, 'E': 200e9},
    'GZO': {'k': 1.5, 'alpha': 11.6e-6, 'E': 180e9},
    'LZO': {'k': 1.6, 'alpha': 9.1e-6, 'E': 175e9},
    'SrZrO3': {'k': 2.1, 'alpha': 10.9e-6, 'E': 210e9}
}

def generate_gradient_mesh(n_nodes=NODES):
    """Generates the 1D mesh array over the 5mm gradient."""
    return np.linspace(0, L_GRADIENT, n_nodes)

def get_component_fractions(x, exponent=1.0):
    """
    Returns (ceramic_frac, hea_frac) at position x.
    n=1 is linear, n=2 pushes HEA toward hot side.
    """
    ceramic_frac = (x / L_GRADIENT) ** exponent
    return ceramic_frac, 1.0 - ceramic_frac

def extract_coble_creep_stress(T, t, sigma, grain_size=1e-6):
    """
    Paper A constraint: ε̇_c = (C · ω_gb · D_gb · Ω / kT·d³) · σ_eq
    Simplified approximation for the surrogate solver.
    Outputs the relieved stress due to grain boundary diffusion.
    """
    # ... Placeholder for complex constitutive creep rate integrations
    creep_modifier = 0.85 # Assume 15% stress relaxation at 1400K due to Coble mechanism
    return sigma * creep_modifier

def solve_1d_thermoelastic_surrogate(hea_E, hea_alpha, hea_k, ceramic_type='ZrO2-HfO2', n_exponent=1.0, grain_size=1e-6):
    """
    Solves a 1D surrogate matrix to predict interface stress without FEniCS boundary overhead.
    Returns: maximum tensile stress upon cooling.
    """
    x = generate_gradient_mesh()  # shape (N,)
    N = len(x)
    dx = x[1] - x[0]
    cer = CERAMIC_MATERIALS[ceramic_type]

    # Build property arrays at each node
    E_x = np.zeros(N)
    alpha_x = np.zeros(N)
    k_x = np.zeros(N)

    for i, xi in enumerate(x):
        f_c, f_m = get_component_fractions(xi, n_exponent)
        # Hashin-Shtrikman lower bound for E (more realistic than Voigt)
        E_x[i] = 1.0 / (f_c / cer['E'] + f_m / hea_E)  # Reuss bound
        alpha_x[i] = f_c * cer['alpha'] + f_m * hea_alpha  # ROM for CTE
        k_x[i] = 1.0 / (f_c / cer['k'] + f_m / hea_k)    # Reuss for k

    # Step 1: Solve steady-state heat conduction
    # d/dx [k(x) dT/dx] = 0 with T(0)=T_HOT, T(L)=T_COLD
    # Discretize: k_{i+1/2} * (T_{i+1} - T_i) = k_{i-1/2} * (T_i - T_{i-1})
    T = np.zeros(N)
    T[0] = T_HOT
    T[-1] = T_COLD

    # Build tridiagonal system for interior nodes
    A = np.zeros((N-2, N-2))
    b = np.zeros(N-2)

    for i in range(1, N-1):
        k_plus = 0.5 * (k_x[i] + k_x[i+1]) if i < N-1 else k_x[i]
        k_minus = 0.5 * (k_x[i] + k_x[i-1])

        ii = i - 1
        A[ii, ii] = -(k_plus + k_minus)
        if ii > 0:
            A[ii, ii-1] = k_minus
        if ii < N-3:
            A[ii, ii+1] = k_plus

        # Boundary contributions
        if i == 1:
            b[ii] = -k_minus * T_HOT
        elif i == N-2:
            b[ii] = -k_plus * T_COLD

    T[1:-1] = np.linalg.solve(A, b)

    # Step 2: Compute thermal stress using compatibility
    # For 1D constrained layer (plane stress assumption):
    # sigma(x) = -E(x) * alpha(x) * (T(x) - T_ref) + C
    # C enforces zero net force: integral(sigma * dx) = 0
    T_ref = T_COLD
    sigma_free = -E_x * alpha_x * (T - T_ref)

    # Enforce equilibrium: find C such that integral of sigma = 0
    # C = -integral(sigma_free) / L
    C = -np.trapezoid(sigma_free, x) / L_GRADIENT
    sigma = sigma_free + C

    # Step 3: Coble creep relaxation at hot side
    sigma_relaxed = np.where(T > 1200, sigma * 0.85, sigma)

    # Step 4: Edge stress concentration
    peak_stress = np.max(np.abs(sigma_relaxed)) / 1e6  # Pa -> MPa
    return peak_stress * 1.3

if __name__ == "__main__":
    print("--- 1D Reduced-Order FEA Environment Loaded ---")
    print("Testing 1D Gradient Constraints without FEniCS...")
    
    # Ex: test Mo0.2Nb0.2Ta0.2W0.2Cr0.2 estimated properties
    test_stress = solve_1d_thermoelastic_surrogate(
        hea_E=210e9, 
        hea_alpha=5.5e-6, 
        hea_k=50.0, 
        ceramic_type='LZO', 
        n_exponent=2.0
    )
    print(f"Predicted Max Interface Stress (Cooling): {test_stress:.2f} MPa")
