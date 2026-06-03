"""
Continuous fractional search across 9 refractory elements
Identifies new compositions resisting 1D thermoelastic cracking
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from train_composition_ml import (
    ALL_ELEMENTS, 
    load_and_prepare_base_data, 
    train_model, 
    load_experimental_data,
    calculate_features
)
from run_1d_fea import solve_1d_thermoelastic_surrogate
from evaluate_candidates import temperature_corrected_ys

def generate_random_compositions(num_samples=10000):
    print(f"Generating {num_samples} continuous random alloy fractions...")
    # Dirichlet distribution gives fractions that sum to 1.0
    alphas = np.ones(len(ALL_ELEMENTS))
    # We heavily penalize W and Mo (high E, high density) and favor Ti, Zr, Hf (low E, high CTE mismatch) to test extremes?
    # No, pure uniform Dirichlet
    fractions = np.random.dirichlet(alphas, num_samples)
    
    data = []
    for frac in fractions:
        row = {f'{el}_frac': f for el, f in zip(ALL_ELEMENTS, frac)}
        # Formula string
        formula = "".join(f"{el}{f:.2f}" for el, f in zip(ALL_ELEMENTS, frac) if f > 0.01)
        row['formula'] = formula
        row['is_true_hea'] = sum(1 for f in frac if f >= 0.05) >= 5
        data.append(row)
        
    return pd.DataFrame(data)

def _get_k(row):
    K_thermal = {'Mo': 138, 'Nb': 53, 'Ta': 57, 'W': 173, 'Cr': 94, 'V': 31, 'Ti': 22, 'Zr': 23, 'Hf': 23}
    k_hea = sum(row.get(f'{el}_frac', 0) * K_thermal.get(el, 0) for el in ALL_ELEMENTS)
    n_el = sum(1 for el in ALL_ELEMENTS if row.get(f'{el}_frac', 0) > 0.01)
    if n_el > 2:
        k_hea *= 0.6
    return k_hea

def _get_cte(row):
    CTE = {'Mo': 4.8, 'Nb': 7.3, 'Ta': 6.3, 'W': 4.5, 'Cr': 4.9, 'V': 8.4, 'Ti': 8.6, 'Zr': 5.8, 'Hf': 5.9}
    return sum(row.get(f'{el}_frac', 0) * CTE.get(el, 0) for el in ALL_ELEMENTS)

def optimize_search():
    print("--- 9-Element MFBO Random Continuous Search ---")
    df_train = load_and_prepare_base_data()
    t_model, t_scaler = train_model(df_train)
    e_model, e_scaler = load_experimental_data()
    
    df_candidates = generate_random_compositions(10000)
    
    # Filter to at least True HEAs (5+ elements > 5% fraction)
    df_candidates = df_candidates[df_candidates['is_true_hea']].copy()
    if len(df_candidates) > 2000:
        df_candidates = df_candidates.sample(2000, random_state=42)
        
    print(f"Evaluating {len(df_candidates)} True HEA expanded candidates...")

    # Calculate features
    feature_list = []
    for _, row in df_candidates.iterrows():
        fracs = {el: row[f'{el}_frac'] for el in ALL_ELEMENTS}
        features = calculate_features(fracs)
        feature_list.append(features)
        
    X_df = pd.DataFrame(feature_list)
    
    # Just use all columns in X_df as 'X' (match what train_model uses)
    X = X_df.copy()
    X_scaled = t_scaler.transform(X)
    df_candidates['predicted_bulk_modulus'] = t_model.predict(X_scaled)
    
    X_exp_scaled = e_scaler.transform(X)
    df_candidates['predicted_yield_strength_MPa'] = e_model.predict(X_exp_scaled)
    
    df_candidates['predicted_thermal_cond'] = df_candidates.apply(_get_k, axis=1)
    df_candidates['predicted_CTE'] = df_candidates.apply(_get_cte, axis=1)
    
    results = []
    ceramics = ['LZO'] # Force LZO since it was best earlier
    
    for _, row in df_candidates.iterrows():
        hea_E_Pa = (row['predicted_bulk_modulus'] * 1.2) * 1e9
        if hea_E_Pa <= 0 or pd.isna(hea_E_Pa):
            continue
        hea_alpha = row['predicted_CTE'] * 1e-6
        hea_k = row['predicted_thermal_cond']
        ys = row['predicted_yield_strength_MPa']
        
        # Test gradient exponent 1.0 and 2.0
        for n in [1.0, 2.0]:
            try:
                stress = solve_1d_thermoelastic_surrogate(
                    hea_E=hea_E_Pa,
                    hea_alpha=hea_alpha,
                    hea_k=hea_k,
                    ceramic_type='LZO',
                    n_exponent=n
                )
                
                ys_hot = temperature_corrected_ys(ys, T=1400)
                sf = ys_hot / stress if stress > 0 else 0
                
                results.append({
                    'formula': row['formula'],
                    'gradient_exponent': n,
                    'bulk_modulus_GPa': row['predicted_bulk_modulus'],
                    'yield_strength_MPa': ys,
                    'ys_hot_MPa': ys_hot,
                    'interface_stress_MPa': stress,
                    'safety_factor': sf,
                    'Mo': row['Mo_frac'], 'Nb': row['Nb_frac'], 'Ta': row['Ta_frac'], 
                    'W': row['W_frac'], 'Cr': row['Cr_frac'], 'V': row['V_frac'],
                    'Ti': row['Ti_frac'], 'Zr': row['Zr_frac'], 'Hf': row['Hf_frac']
                })
            except Exception as e:
                pass
                
    res_df = pd.DataFrame(results)
    if len(res_df) == 0:
        print("No results calculated.")
        return
        
    print(f"\nMax Safety Factor Found: {res_df['safety_factor'].max():.3f}")
    valid = res_df[res_df['safety_factor'] >= 1.5]
    
    if len(valid) == 0:
        print("\n[ALERT] No single candidate achieved SF >= 1.5!")
        print("Here are the top 5 closest attempts:")
        best_fails = res_df.sort_values('safety_factor', ascending=False).head(5)
        print(best_fails[['formula', 'ys_hot_MPa', 'interface_stress_MPa', 'safety_factor']].to_string(index=False))
    else:
        top_winners = valid.sort_values('safety_factor', ascending=False)
        out_path = Path(__file__).parent.parent / 'models' / 'expanded_winners.csv'
        top_winners.to_csv(out_path, index=False)
        print("\n--- WINNERS FOUND ---")
        print(top_winners[['formula', 'ys_hot_MPa', 'interface_stress_MPa', 'safety_factor']].head(5).to_string(index=False))
        print(f"Saved {len(top_winners)} winning setups to expanded_winners.csv")

if __name__ == "__main__":
    optimize_search()