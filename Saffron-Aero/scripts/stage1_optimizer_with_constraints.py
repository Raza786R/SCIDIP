# Phase 1 supersedes this historical entry point; see phase1/README.md.
if __name__ == "__main__":
    from _legacy_guard import stop_legacy_entrypoint
    stop_legacy_entrypoint(__file__)

import sys
import os
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

warnings.filterwarnings('ignore')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from train_composition_ml import ALL_ELEMENTS, load_and_prepare_base_data, train_model, load_experimental_data, calculate_features
from run_1d_fea import solve_1d_thermoelastic_surrogate
from evaluate_candidates import temperature_corrected_ys

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

def main():
    print('--- 9-Element Differential Evolution with Constraints ---')
    df_train = load_and_prepare_base_data()
    t_model, t_scaler = train_model(df_train)
    e_model, e_scaler = load_experimental_data()
    
    def objective(x):
        e_x = np.exp(x - np.max(x))
        fracs = e_x / e_x.sum()
        
        if sum(1 for f in fracs if f >= 0.05) < 5:
            return 1000.0
            
        frac_dict = {el: fracs[i] for i, el in enumerate(ALL_ELEMENTS)}
        W = frac_dict.get('W', 0)
        V = frac_dict.get('V', 0)
        Cr = frac_dict.get('Cr', 0)
        Nb = frac_dict.get('Nb', 0)
        Ta = frac_dict.get('Ta', 0)
        Mo = frac_dict.get('Mo', 0)

        sigma_formers = W + Cr + Mo
        sigma_penalty = 5.0 if sigma_formers > 0.50 else 2.5 if sigma_formers > 0.40 else 0
        
        v_penalty = 5.0 if V > 0.20 else 2.0 if V > 0.15 else 0
        cr_shortage_penalty = 5.0 if Cr < 0.15 else 0

        element_density = {'W': 19.3, 'V': 6.0, 'Cr': 7.2, 'Nb': 8.6, 'Ta': 16.7, 'Mo': 10.2, 'Hf': 13.3, 'Zr': 6.5, 'Ti': 4.5}
        density = sum(frac_dict.get(el, 0) * element_density.get(el, 10.0) for el in ALL_ELEMENTS)
        weight_penalty = 2.0 if density > 11.0 else 0
        
        features = calculate_features(frac_dict)
        X_df = pd.DataFrame([features])
        X_scaled = t_scaler.transform(X_df)
        bulk_mod = t_model.predict(X_scaled)[0]
        
        X_exp_scaled = e_scaler.transform(X_df)
        ys = e_model.predict(X_exp_scaled)[0]
        
        row = {f'{el}_frac': fracs[i] for i, el in enumerate(ALL_ELEMENTS)}
        row_cte = _get_cte(row)
        row_k = _get_k(row)
        
        hea_E_Pa = (bulk_mod * 1.2) * 1e9
        if hea_E_Pa <= 0 or pd.isna(hea_E_Pa):
            return 1000.0
            
        stress = solve_1d_thermoelastic_surrogate(
            hea_E=hea_E_Pa, hea_alpha=row_cte * 1e-6, hea_k=row_k, ceramic_type='LZO', n_exponent=1.0
        )
        
        ys_hot = temperature_corrected_ys(ys, T=1400)
        sf = ys_hot / stress if stress > 0 else 0
        
        return -sf + sigma_penalty + v_penalty + weight_penalty + cr_shortage_penalty

    bounds = [(-10, 10) for _ in range(9)]
    
    print('Beginning actively guided optimization loop with constraints...')
    result = differential_evolution(objective, bounds, strategy='best1bin', maxiter=200, popsize=20, tol=0.01)
    
    print('\n--- OPTIMIZATION COMPLETE ---')
    x_opt = result.x
    e_x = np.exp(x_opt - np.max(x_opt))
    fracs = e_x / e_x.sum()
    
    formula = ''.join(f'{el}{f:.2f}' for el, f in zip(ALL_ELEMENTS, fracs) if f > 0.01)
    
    frac_dict = {el: fracs[i] for i, el in enumerate(ALL_ELEMENTS)}
    features = calculate_features(frac_dict)
    X_df = pd.DataFrame([features])
    X_scaled = t_scaler.transform(X_df)
    bulk_mod = t_model.predict(X_scaled)[0]
    X_exp_scaled = e_scaler.transform(X_df)
    ys = e_model.predict(X_exp_scaled)[0]
    row = {f'{el}_frac': fracs[i] for i, el in enumerate(ALL_ELEMENTS)}
    row_cte = _get_cte(row)
    row_k = _get_k(row)
    hea_E_Pa = (bulk_mod * 1.2) * 1e9
    stress = solve_1d_thermoelastic_surrogate(hea_E=hea_E_Pa, hea_alpha=row_cte * 1e-6, hea_k=row_k, ceramic_type='LZO', n_exponent=1.0)
    ys_hot = temperature_corrected_ys(ys, T=1400)
    sf_final = ys_hot / stress if stress > 0 else 0

    print(f'Optimal Formula found: {formula}')
    print(f'Max achieved Safety Factor: {sf_final:.4f}')
    
    element_density = {'W': 19.3, 'V': 6.0, 'Cr': 7.2, 'Nb': 8.6, 'Ta': 16.7, 'Mo': 10.2, 'Hf': 13.3, 'Zr': 6.5, 'Ti': 4.5}
    density = sum(frac_dict.get(el, 0) * element_density.get(el, 10.0) for el in ALL_ELEMENTS)
    print(f'Density: {density:.2f} g/cm3')
    print(f'Sigma Formers (W+Cr+Mo): {frac_dict.get("W", 0) + frac_dict.get("Cr", 0) + frac_dict.get("Mo", 0):.2f}')
    print(f'Vanadium: {frac_dict.get("V", 0):.2f}')
    print('\nFractions:')
    for el, f in zip(ALL_ELEMENTS, fracs):
        if f > 0.01:
            print(f'  {el}: {f:.3f}')

if __name__ == "__main__":
    main()
