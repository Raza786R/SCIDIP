# Phase 1 supersedes this historical entry point; see phase1/README.md.
if __name__ == "__main__":
    from _legacy_guard import stop_legacy_entrypoint
    stop_legacy_entrypoint(__file__)

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add current dir to path to import run_1d_fea
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from run_1d_fea import solve_1d_thermoelastic_surrogate

def temperature_corrected_ys(ys_rt, T=1400):
    """
    Refractory HEAs retain ~40-60% YS at 1400K vs RT.
    Use 0.45 as conservative factor until you have actual
    high-temperature data from your MPEA dataset.
    """
    T_homologous = T / 3290  # normalize by Ta melting point (highest in system)
    knockdown = max(0.3, 1.0 - 0.8 * T_homologous)
    return ys_rt * knockdown

def run_screening():
    print("Loading ML predictions...")
    data_path = Path(__file__).parent.parent / 'models' / 'ml_predictions.csv'
    df = pd.read_csv(data_path)
    
    ALL_9 = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']
    frac_cols = [f'{el}_frac' for el in ALL_9 if f'{el}_frac' in df.columns]
    true_hea_mask = (df[frac_cols] >= 0.05).sum(axis=1) >= 5
    df_hea = df[true_hea_mask]
    print(f"Evaluating {len(df_hea)} True HEA base matrices (any 5 elements >= 5%)...")

    ceramics = ['ZrO2-HfO2', 'GZO', 'LZO', 'SrZrO3']
    exponents = [0.5, 1.0, 2.0, 4.0]
    
    results = []
    
    for _, row in df_hea.iterrows():
        # K -> E approximation assuming v=0.3. E = 3K(1-2v) = 1.2K
        hea_E_Pa = (row['predicted_bulk_modulus'] * 1.2) * 1e9
        if pd.isna(hea_E_Pa) or hea_E_Pa <= 0:
            continue
        hea_alpha = row['predicted_CTE'] * 1e-6
        hea_k = row['predicted_thermal_cond']
        ys = row.get('predicted_yield_strength_MPa', 0)
        
        for cer in ceramics:
            for n in exponents:
                stress = solve_1d_thermoelastic_surrogate(
                    hea_E=hea_E_Pa,
                    hea_alpha=hea_alpha,
                    hea_k=hea_k,
                    ceramic_type=cer,
                    n_exponent=n
                )
                
                ys_hot = temperature_corrected_ys(ys, T=1400)
                sf = ys_hot / stress if stress > 0 else 0
                results.append({
                    'formula': row['formula'],
                    'ceramic_type': cer,
                    'gradient_exponent': n,
                    'bulk_modulus_GPa': row['predicted_bulk_modulus'],
                    'yield_strength_MPa': ys,
                    'interface_stress_MPa': stress,
                    'safety_factor': sf
                })
                
    res_df = pd.DataFrame(results)
    
    # Filter valid designs
    # 1. Interface stress must be > 0
    # 2. Safety factor must be >= SF_MIN
    SF_MIN = 1.50
    valid = res_df[(res_df['interface_stress_MPa'] > 0) & (res_df['safety_factor'] >= SF_MIN)]
    
    # Sort to minimize stress
    top_50 = valid.sort_values('interface_stress_MPa').head(50)
    
    out_path = Path(__file__).parent.parent / 'models' / 'top_50_candidates.csv'
    top_50.to_csv(out_path, index=False)
    
    print("\n--- TOP 10 GRADIENT COMBINATIONS ---")
    print(top_50[['formula', 'ceramic_type', 'gradient_exponent', 'interface_stress_MPa', 'safety_factor']].head(10).to_string(index=False))
    print(f"\nSaved Top 50 configs to {out_path}")

if __name__ == '__main__':
    run_screening()
