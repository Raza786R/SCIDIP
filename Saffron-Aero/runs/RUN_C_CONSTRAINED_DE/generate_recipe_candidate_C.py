"""
Generate 11-layer FGM Manufacturing Recipe for Candidate C (Run C winner)
Directly injects the Candidate C composition — does not depend on top_50_candidates.csv
Output goes to runs/RUN_C_CONSTRAINED_DE/manufacturing_recipe.csv
"""
import pandas as pd
import numpy as np
import os

# ─── Candidate C composition (from Run C DE output + 2.8% Al added) ───────────
# Original DE output: Nb0.014 Ta0.140 W0.145 Cr0.236 V0.144 Ti0.223 Zr0.047 Hf0.042
# After +2.8% Al (normalise remaining 97.2%):
CANDIDATE_C = {
    'formula':           'Ta0.136W0.141Cr0.229V0.140Ti0.217Zr0.046Hf0.041Al0.028Nb0.014',
    'ceramic_type':      'LZO',
    'gradient_exponent': 1.1,        # Use Run A optimal (Pareto-confirmed)
    'total_thickness_mm': 5.0,
    'tbc_outer_mm':      0.5,        # Pure ceramic outer TBC layer
    'safety_factor_1D':  1.5981,     # Local 1D FEA result
    'density_gcm3':      9.78,
    'VEC':               5.02,
    'CTE_alloy_um_mK':   6.44,
    'CTE_LZO_um_mK':     9.10,
    'CTE_mismatch':      2.66,
}

# ─── FGM Layer Recipe ──────────────────────────────────────────────────────────
thickness_mm = CANDIDATE_C['total_thickness_mm']
n            = CANDIDATE_C['gradient_exponent']
num_layers   = 11

depths    = np.linspace(0, thickness_mm, num_layers)
v_ceramic = (depths / thickness_mm) ** n
v_metal   = 1.0 - v_ceramic

recipe = pd.DataFrame({
    'Layer_Index':          np.arange(1, num_layers + 1),
    'Depth_mm':             np.round(depths, 2),
    'Alloy_Vol_Percent':    np.round(v_metal * 100, 1),
    'Ceramic_Vol_Percent':  np.round(v_ceramic * 100, 1),
    'Alloy_Formula':        CANDIDATE_C['formula'],
    'Ceramic_Type':         CANDIDATE_C['ceramic_type'],
    'Gradient_Exponent':    n,
})

out_dir  = os.path.join('runs', 'RUN_C_CONSTRAINED_DE')
out_path = os.path.join(out_dir, 'manufacturing_recipe.csv')
recipe.to_csv(out_path, index=False)

print("=" * 65)
print("  FGM MANUFACTURING RECIPE — CANDIDATE C (Run C DE Winner)")
print("=" * 65)
print(f"\nAlloy:    {CANDIDATE_C['formula']}")
print(f"Ceramic:  {CANDIDATE_C['ceramic_type']} (La2Zr2O7)")
print(f"Gradient: Power-law n={n}, Total={thickness_mm}mm, TBC outer={CANDIDATE_C['tbc_outer_mm']}mm")
print(f"\nPhysics summary:")
print(f"  SF (local 1D FEA):   {CANDIDATE_C['safety_factor_1D']}")
print(f"  Density:             {CANDIDATE_C['density_gcm3']} g/cm³")
print(f"  VEC:                 {CANDIDATE_C['VEC']} (BCC stable, no sigma phase)")
print(f"  CTE alloy:           {CANDIDATE_C['CTE_alloy_um_mK']} µm/mK")
print(f"  CTE LZO:             {CANDIDATE_C['CTE_LZO_um_mK']} µm/mK")
print(f"  CTE mismatch:        {CANDIDATE_C['CTE_mismatch']} µm/mK (best achieved)")
print(f"\n{'-'*65}")
print(f"{'Layer':>6} {'Depth(mm)':>10} {'Alloy%':>8} {'Ceramic%':>9}")
print(f"{'-'*65}")
for _, row in recipe.iterrows():
    print(f"  {int(row['Layer_Index']):>4}   {row['Depth_mm']:>8.2f}   {row['Alloy_Vol_Percent']:>7.1f}%  {row['Ceramic_Vol_Percent']:>8.1f}%")
print(f"{'-'*65}")
print(f"\nNote: Layer 1 = pure alloy side (hot face, blade substrate)")
print(f"      Layer 11 = pure ceramic TBC (cold face, gas flow)")
print(f"\nSaved to: {out_path}")
print("\n[DONE] Candidate C manufacturing recipe COMPLETE")
