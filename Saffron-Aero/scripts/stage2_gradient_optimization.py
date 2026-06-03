import numpy as np
from scipy.optimize import minimize_scalar
import sys

def calculate_interface_stress(n, total_thickness=5.0):
    positions = np.arange(0, total_thickness+0.1, 0.1)
    
    alloy_CTE = 6.27
    LZO_CTE   = 9.1
    E_metal   = 280e9
    E_ceramic = 210e9
    delta_T   = 1100
    
    max_stress = 0
    
    for i in range(len(positions)-1):
        pos1 = positions[i]
        pos2 = positions[i+1]
        
        cf1 = (pos1/total_thickness) ** n
        cf2 = (pos2/total_thickness) ** n
        
        cte1 = alloy_CTE*(1-cf1) + LZO_CTE*cf1
        cte2 = alloy_CTE*(1-cf2) + LZO_CTE*cf2
        E1   = E_metal*(1-cf1)   + E_ceramic*cf1
        
        stress = E1 * abs(cte2 - cte1) * delta_T * 1e-6
        max_stress = max(max_stress, stress)
    
    return max_stress

if __name__ == '__main__':
    exponents = np.arange(0.1, 4.1, 0.1)
    stresses  = [calculate_interface_stress(n) for n in exponents]

    optimal_n   = exponents[np.argmin(stresses)]
    min_stress  = min(stresses)

    print(f"Optimal gradient exponent: n = {optimal_n:.1f}")
    print(f"Minimum interface stress:  {min_stress:.4f} MPa")
    print(f"Your current n=1.0 stress: {calculate_interface_stress(1.0):.4f} MPa")
    print(f"Improvement: {calculate_interface_stress(1.0)/min_stress:.2f}x")

    print('\nTesting gradient thicknesses...')
    thicknesses = [2, 3, 4, 5, 6, 7, 8]
    for t in thicknesses:
        stress = calculate_interface_stress(n=optimal_n, total_thickness=t)
        print(f"Thickness: {t}mm -> Stress: {stress:.2f} MPa")
