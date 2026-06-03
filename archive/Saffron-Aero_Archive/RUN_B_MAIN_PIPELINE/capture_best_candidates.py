"""
Run B — Best Candidates Capture (No SF Threshold)
Records top 50 by highest SF AND top 50 by lowest stress
for Bohrium submission, regardless of local 1D FEA threshold.
"""
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, 'scripts')
from run_1d_fea import solve_1d_thermoelastic_surrogate

def temperature_corrected_ys(ys_rt, T=1400):
    T_homologous = T / 3290
    knockdown = max(0.3, 1.0 - 0.8 * T_homologous)
    return ys_rt * knockdown

print("=== RUN B — FULL CANDIDATE CAPTURE (No SF Threshold) ===\n")

ml = pd.read_csv('models/ml_predictions.csv')

# Apply 9-element HEA filter
ALL_9 = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']
frac_cols = [f'{el}_frac' for el in ALL_9 if f'{el}_frac' in ml.columns]
hea_mask = (ml[frac_cols] >= 0.05).sum(axis=1) >= 5
df_hea = ml[hea_mask]
print(f"True HEA compositions: {len(df_hea)}")

# Skip negative/NaN bulk modulus
df_hea = df_hea[df_hea['predicted_bulk_modulus'] > 0]
print(f"After removing negative bulk modulus: {len(df_hea)}")

ceramics   = ['ZrO2-HfO2', 'GZO', 'LZO', 'SrZrO3']
exponents  = [0.5, 1.0, 2.0, 4.0]

results = []
total = len(df_hea) * len(ceramics) * len(exponents)
print(f"Running {total:,} FEA evaluations...")

for idx, (_, row) in enumerate(df_hea.iterrows()):
    if idx % 500 == 0:
        print(f"  Progress: {idx}/{len(df_hea)} compositions...")
    hea_E_Pa  = (row['predicted_bulk_modulus'] * 1.2) * 1e9
    hea_alpha = row['predicted_CTE'] * 1e-6
    hea_k     = row['predicted_thermal_cond']
    ys        = row.get('predicted_yield_strength_MPa', 0)
    ys_hot    = temperature_corrected_ys(ys)

    for cer in ceramics:
        for n in exponents:
            stress = solve_1d_thermoelastic_surrogate(
                hea_E=hea_E_Pa, hea_alpha=hea_alpha, hea_k=hea_k,
                ceramic_type=cer, n_exponent=n
            )
            sf = ys_hot / stress if stress > 0 else 0
            results.append({
                'formula': row['formula'],
                'ceramic_type': cer,
                'gradient_exponent': n,
                'bulk_modulus_GPa': row['predicted_bulk_modulus'],
                'yield_strength_MPa': ys,
                'yield_strength_hot_MPa': round(ys_hot, 1),
                'interface_stress_MPa': round(stress, 2),
                'safety_factor': round(sf, 4),
                'Mo_frac': row.get('Mo_frac', 0),
                'Nb_frac': row.get('Nb_frac', 0),
                'Ta_frac': row.get('Ta_frac', 0),
                'W_frac':  row.get('W_frac', 0),
                'Cr_frac': row.get('Cr_frac', 0),
            })

res_df = pd.DataFrame(results)
print(f"\nTotal evaluations completed: {len(res_df)}")

# --- Table 1: Top 50 by HIGHEST Safety Factor (no threshold) ---
top_by_sf = res_df[res_df['interface_stress_MPa'] > 0].sort_values(
    'safety_factor', ascending=False).head(50)
top_by_sf.to_csv('runs/RUN_B_MAIN_PIPELINE/top50_by_highest_SF.csv', index=False)
print(f"\n=== TOP 10 BY HIGHEST SAFETY FACTOR ===")
print(top_by_sf[['formula','ceramic_type','gradient_exponent',
                  'interface_stress_MPa','safety_factor']].head(10).to_string(index=False))

# --- Table 2: Top 50 by LOWEST Interface Stress ---
top_by_stress = res_df[res_df['interface_stress_MPa'] > 0].sort_values(
    'interface_stress_MPa').head(50)
top_by_stress.to_csv('runs/RUN_B_MAIN_PIPELINE/top50_by_lowest_stress.csv', index=False)
print(f"\n=== TOP 10 BY LOWEST INTERFACE STRESS ===")
print(top_by_stress[['formula','ceramic_type','gradient_exponent',
                      'interface_stress_MPa','safety_factor']].head(10).to_string(index=False))

# --- Summary Stats ---
print(f"\n=== SUMMARY ===")
print(f"Max SF across all evaluations:  {res_df['safety_factor'].max():.4f}")
print(f"Min stress (MPa):               {res_df['interface_stress_MPa'].min():.2f}")
print(f"Compositions passing SF>=1.50:  {(res_df['safety_factor']>=1.50).sum()}")
print(f"Compositions passing SF>=1.20:  {(res_df['safety_factor']>=1.20).sum()}")
print(f"Compositions passing SF>=1.00:  {(res_df['safety_factor']>=1.00).sum()}")
print(f"\nTop candidate for Bohrium Job 2:")
best = top_by_sf.iloc[0]
print(f"  Formula:        {best['formula']}")
print(f"  Ceramic:        {best['ceramic_type']}")
print(f"  Gradient (n):   {best['gradient_exponent']}")
print(f"  Stress:         {best['interface_stress_MPa']} MPa")
print(f"  SF (1D local):  {best['safety_factor']}")
print(f"  Note: 1D FEA is conservative — no geometric optimization, no centrifugal load compensating.")
print(f"        Bohrium 3D FEA with geometric fixes may produce significantly different SF.")
print("\nFiles saved:")
print("  runs/RUN_B_MAIN_PIPELINE/top50_by_highest_SF.csv")
print("  runs/RUN_B_MAIN_PIPELINE/top50_by_lowest_stress.csv")
