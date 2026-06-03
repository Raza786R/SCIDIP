"""
Differential Evolution script to find the optimal 9-part alloy.
"""
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
    print("--- 9-Element Differential Evolution ---")
    df_train = load_and_prepare_base_data()
    t_model, t_scaler = train_model(df_train)
    e_model, e_scaler = load_experimental_data()
    
    # We want to MAXIMIZE safety factor. differential_evolution MINIMIZES by default.
    def objective(x):
        # x is array of 9 continuous unbounded values
        # Softmax it so it sums to 1.0!
        e_x = np.exp(x - np.max(x))
        fracs = e_x / e_x.sum()
        
        # We need at least 5 elements > 0.05 to be a true HEA.
        # Let's apply a severe penalty if it's not a true HEA.
        if sum(1 for f in fracs if f >= 0.05) < 5:
            return 100.0 # Huge penalty
        
        # HEA upper bound: no single element > 35% (Miracle & Senkov 2017)
        if any(f > 0.35 for f in fracs):
            return 100.0
        # Density constraint: keep below 11.0 g/cm3 for aerospace weight budget
        element_density = {
            'Mo': 10.2, 'Nb': 8.6, 'Ta': 16.7, 'W': 19.3, 'Cr': 7.2,
            'V': 6.0, 'Ti': 4.5, 'Zr': 6.5, 'Hf': 13.3
        }
        frac_dict_tmp = {el: fracs[i] for i, el in enumerate(ALL_ELEMENTS)}
        density = sum(frac_dict_tmp.get(el, 0.0) * element_density.get(el, 10.0)
                      for el in ALL_ELEMENTS)
        if density > 11.0:
            return 50.0
        
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
        if hea_E_Pa <= 0 or pd.isna(hea_E_Pa):
            return 100.0
            
        stress = solve_1d_thermoelastic_surrogate(
            hea_E=hea_E_Pa,
            hea_alpha=row_cte * 1e-6,
            hea_k=row_k,
            ceramic_type='LZO',
            n_exponent=1.0
        )
        
        ys_hot = temperature_corrected_ys(ys, T=1400)
        sf = ys_hot / stress if stress > 0 else 0
        
        return -sf # Minimizing negative SF = Maximizing SF

    # Bounds for the pre-softmax vector (any real numbers work, bound between -10 and 10 is fine)
    bounds = [(-10, 10) for _ in range(9)]
    
    print("Beginning actively guided optimization loop...")
    result = differential_evolution(objective, bounds, strategy='best1bin', maxiter=50, popsize=15, tol=0.01)
    
    print("\n--- OPTIMIZATION COMPLETE ---")
    
    x_opt = result.x
    e_x = np.exp(x_opt - np.max(x_opt))
    fracs = e_x / e_x.sum()
    
    sf_final = -result.fun
    formula = "".join(f"{el}{f:.2f}" for el, f in zip(ALL_ELEMENTS, fracs) if f > 0.01)
    
    print(f"Optimal Formula found: {formula}")
    print(f"Max achieved Safety Factor: {sf_final:.4f}")
    
    if sf_final >= 1.5:
        print("[SUCCESS] We breached the SF >= 1.5 barrier!")
    else:
        print("Still slightly short of the 1.5 hard parameter barrier.")
        
    print("\nFractions:")
    for el, f in zip(ALL_ELEMENTS, fracs):
        if f > 0.01:
            print(f"  {el}: {f:.3f}")

if __name__ == "__main__":
    main()