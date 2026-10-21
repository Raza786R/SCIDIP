# Phase 1 supersedes this historical entry point; see phase1/README.md.
if __name__ == "__main__":
    from _legacy_guard import stop_legacy_entrypoint
    stop_legacy_entrypoint(__file__)

"""
Train composition-based ML model for property prediction.
Uses elemental descriptors + Miedema parameters as features.
Targets: bulk_modulus, thermal_conductivity (from base data + physics)
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import warnings
import re
warnings.filterwarnings('ignore')

# Elemental properties for feature engineering
ELEMENT_DATA = {
    'Mo': {'r': 1.39, 'X': 2.16, 'VEC': 6, 'Tm': 2896, 'mass': 95.95, 'K': 230},
    'Nb': {'r': 1.46, 'X': 1.60, 'VEC': 5, 'Tm': 2750, 'mass': 92.91, 'K': 170},
    'Ta': {'r': 1.46, 'X': 1.50, 'VEC': 5, 'Tm': 3290, 'mass': 180.95, 'K': 200},
    'W':  {'r': 1.39, 'X': 2.36, 'VEC': 6, 'Tm': 3695, 'mass': 183.84, 'K': 310},
    'Cr': {'r': 1.28, 'X': 1.66, 'VEC': 6, 'Tm': 2180, 'mass': 52.00, 'K': 160},
    # Transfer Learning Refractory Elements (Used for ML anchor training only)
    'V':  {'r': 1.34, 'X': 1.63, 'VEC': 5, 'Tm': 2183, 'mass': 50.94, 'K': 160},
    'Ti': {'r': 1.47, 'X': 1.54, 'VEC': 4, 'Tm': 1941, 'mass': 47.87, 'K': 105},
    'Zr': {'r': 1.60, 'X': 1.33, 'VEC': 4, 'Tm': 2128, 'mass': 91.22, 'K': 83},
    'Hf': {'r': 1.59, 'X': 1.30, 'VEC': 4, 'Tm': 2506, 'mass': 178.49, 'K': 110},
}
TARGET_ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr']
ALL_ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']
ELEMENTS = TARGET_ELEMENTS  # Legacy variable for basic loops

BASE_DATA_FILE = Path(__file__).parent.parent / 'data' / 'processed_candidate_properties.csv'
STABLE_COMPOSITIONS_FILE = Path(__file__).parent.parent / 'data' / 'stable_compositions.csv'
MODEL_OUTPUT = Path(__file__).parent.parent / 'models' / 'composition_model.pkl'
PREDICTIONS_OUTPUT = Path(__file__).parent.parent / 'models' / 'ml_predictions.csv'

def parse_formula_to_fractions(formula, allowed_elements=ALL_ELEMENTS):
    """Strict stoichiometry parser; legacy model training is superseded."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'phase1'))
    from he_mcga.composition import parse_stoichiometry
    comp = parse_stoichiometry(formula)
    if any(v > 0 and el not in allowed_elements for el, v in comp.items()):
        raise ValueError("Formula contains an element outside allowed_elements")
    return {el: comp.get(el, 0.0) for el in allowed_elements}


def calculate_features(fracs_dict, test_temp_c=25):
    """Calculate composition-based features from fractions."""
    # Use ALL_ELEMENTS so the feature vector size is constant across broad/specific data
    fracs = [fracs_dict.get(el, 0.0) for el in ALL_ELEMENTS]
    
    features = {}
    
    # Add Test Temperature
    features['T_test'] = test_temp_c
    
    # Weighted average properties
    for prop in ['r', 'X', 'VEC', 'Tm', 'mass', 'K']:
        features[f'avg_{prop}'] = sum(
            f * ELEMENT_DATA[el][prop] for el, f in zip(ALL_ELEMENTS, fracs) if f > 0
        )
    
    # Standard deviation of properties (disorder measure)
    for prop in ['r', 'X', 'VEC', 'Tm']:
        avg = features[f'avg_{prop}']
        if avg > 0:
            var = sum(
                f * (ELEMENT_DATA[el][prop] - avg)**2 
                for el, f in zip(ALL_ELEMENTS, fracs) if f > 0
            )
            features[f'std_{prop}'] = np.sqrt(var)
        else:
            features[f'std_{prop}'] = 0
    
    # Number of elements
    features['n_elements'] = sum(1 for f in fracs if f > 0)
    
    # Individual fractions as features
    for el in ALL_ELEMENTS:
        features[f'{el}_frac'] = fracs_dict.get(el, 0.0)
    
    return features

def load_and_prepare_base_data():
    """Load base compound data and prepare training set."""
    if not BASE_DATA_FILE.exists():
        print(f"Warning: {BASE_DATA_FILE} not found. Using synthetic training data.")
        raise ValueError("Real training data required; synthetic fallback disabled. Use phase1/README.md")
    
    df = pd.read_csv(BASE_DATA_FILE)
    print(f"Loaded {len(df)} base compounds from {BASE_DATA_FILE}")
    
    # Filter for rows with bulk modulus
    if 'bulk_modulus' in df.columns:
        df_with_K = df[df['bulk_modulus'].notna()].copy()
        if len(df_with_K) >= 5:
            print(f"Training samples with bulk_modulus: {len(df_with_K)}")
            return df_with_K
    
    print("Insufficient bulk_modulus data. Using synthetic training data.")
    raise ValueError("Real training data required; synthetic fallback disabled. Use phase1/README.md")

def create_synthetic_training_data():
    """Create synthetic training data based on Rule of Mixtures + literature."""
    print("Creating synthetic training data from elemental properties + literature...")
    
    data = []
    # Pure elements (measured values)
    for el in ELEMENTS:
        data.append({
            'formula': el,
            'bulk_modulus': ELEMENT_DATA[el]['K'],
            **{f'{e}_frac': 1.0 if e == el else 0.0 for e in ELEMENTS}
        })
    
    # Equimolar binaries (Rule of Mixtures with ~5% deviation)
    for i, el1 in enumerate(ELEMENTS):
        for el2 in ELEMENTS[i+1:]:
            K_avg = 0.5 * (ELEMENT_DATA[el1]['K'] + ELEMENT_DATA[el2]['K'])
            data.append({
                'formula': f"{el1}0.50{el2}0.50",
                'bulk_modulus': K_avg * 0.95,
                **{f'{e}_frac': 0.5 if e in [el1, el2] else 0.0 for e in ELEMENTS}
            })
    
    # Non-equimolar binaries
    for i, el1 in enumerate(ELEMENTS):
        for el2 in ELEMENTS[i+1:]:
            for f1 in [0.25, 0.75]:
                K_mix = f1 * ELEMENT_DATA[el1]['K'] + (1-f1) * ELEMENT_DATA[el2]['K']
                data.append({
                    'formula': f"{el1}{f1:.2f}{el2}{1-f1:.2f}",
                    'bulk_modulus': K_mix * 0.96,
                    **{f'{e}_frac': f1 if e == el1 else (1-f1 if e == el2 else 0.0) for e in ELEMENTS}
                })
    
    # Equimolar ternaries
    import itertools
    for combo in itertools.combinations(ELEMENTS, 3):
        K_avg = sum(ELEMENT_DATA[el]['K'] for el in combo) / 3
        data.append({
            'formula': ''.join(f"{el}0.33" for el in combo),
            'bulk_modulus': K_avg * 0.93,
            **{f'{e}_frac': 1/3 if e in combo else 0.0 for e in ELEMENTS}
        })
    
    # Equimolar quaternaries
    for combo in itertools.combinations(ELEMENTS, 4):
        K_avg = sum(ELEMENT_DATA[el]['K'] for el in combo) / 4
        data.append({
            'formula': ''.join(f"{el}0.25" for el in combo),
            'bulk_modulus': K_avg * 0.91,
            **{f'{e}_frac': 0.25 if e in combo else 0.0 for e in ELEMENTS}
        })
    
    # Equimolar quinary HEA (literature: ~210 GPa for MoNbTaWCr)
    data.append({
        'formula': 'Mo0.20Nb0.20Ta0.20W0.20Cr0.20',
        'bulk_modulus': 210,  # Literature value for similar RHEA
        **{f'{el}_frac': 0.2 for el in ELEMENTS}
    })
    
    # Additional HEA variants (based on Senkov et al. data)
    hea_variants = [
        ({'Mo': 0.25, 'Nb': 0.25, 'Ta': 0.25, 'W': 0.25, 'Cr': 0.0}, 220),  # MoNbTaW
        ({'Mo': 0.15, 'Nb': 0.20, 'Ta': 0.20, 'W': 0.30, 'Cr': 0.15}, 215),
        ({'Mo': 0.30, 'Nb': 0.15, 'Ta': 0.15, 'W': 0.25, 'Cr': 0.15}, 225),
        ({'Mo': 0.10, 'Nb': 0.30, 'Ta': 0.30, 'W': 0.20, 'Cr': 0.10}, 195),
    ]
    for fracs, K in hea_variants:
        formula = ''.join(f"{el}{f:.2f}" for el, f in fracs.items() if f > 0)
        data.append({
            'formula': formula,
            'bulk_modulus': K,
            **{f'{el}_frac': fracs.get(el, 0) for el in ELEMENTS}
        })
    
    df = pd.DataFrame(data)
    print(f"Created {len(df)} synthetic training samples")
    return df

def train_model(df_train):
    """Train Random Forest model on base data."""
    print("\n--- Training ML Model ---")
    
    # Prepare features
    X_data = []
    y_data = []
    
    for _, row in df_train.iterrows():
        formula = row.get('formula', '')
        if not formula:
            continue
        
        fracs = parse_formula_to_fractions(formula)
        features = calculate_features(fracs)
        X_data.append(features)
        y_data.append(row['bulk_modulus'])
    
    if len(X_data) < 5:
        print("Not enough training data!")
        return None, None
    
    X = pd.DataFrame(X_data)
    y = np.array(y_data)
    
    print(f"Training features: {X.shape[1]}")
    print(f"Training samples: {len(y)}")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=3,
        random_state=42
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nTest MAE: {mae:.2f} GPa")
    print(f"Test R²: {r2:.3f}")
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\nTop 5 Important Features:")
    print(importance.head().to_string(index=False))
    
    return model, scaler

def predict_compositions(model, scaler, compositions_df, exp_model=None, exp_scaler=None):
    """Predict bulk modulus and experimental yield strength for all compositions."""
    print("\n--- Predicting Properties for All Compositions ---")
    
    X_data = []
    for _, row in compositions_df.iterrows():
        fracs = {el: row[f'{el}_frac'] for el in ELEMENTS}
        features = calculate_features(fracs)
        X_data.append(features)
    
    X = pd.DataFrame(X_data)
    X_scaled = scaler.transform(X)
    
    predictions = model.predict(X_scaled)
    compositions_df['predicted_bulk_modulus'] = predictions
    
    if exp_model and exp_scaler:
        X_exp_scaled = exp_scaler.transform(X)
        compositions_df['predicted_yield_strength_MPa'] = exp_model.predict(X_exp_scaled)
    
    # Estimate thermal conductivity using Rule of Mixtures
    compositions_df['predicted_thermal_cond'] = compositions_df.apply(
        lambda row: estimate_thermal_conductivity(row, layer_position=0.0), axis=1
    )
    
    # Estimate CTE (Coefficient of Thermal Expansion)
    compositions_df['predicted_CTE'] = compositions_df.apply(
        lambda row: estimate_cte(row), axis=1
    )
    
    print(f"Predicted properties for {len(compositions_df)} compositions")
    return compositions_df

def estimate_thermal_conductivity(row, T=1400, layer_position=0.0):
    """
    layer_position: 0 = pure HEA side, 1 = pure ceramic side
    Phonon conductivity applies to HEA fraction.
    Rosseland radiative applies to ceramic fraction only.
    """
    K_thermal_all = {
        'Mo': 138, 'Nb': 53, 'Ta': 57, 'W': 173, 'Cr': 94,
        'V': 31, 'Ti': 22, 'Zr': 23, 'Hf': 23
    }
    
    # 1. HEA phonon conductivity
    k_hea = sum(
        row.get(f'{el}_frac', 0.0) * v
        for el, v in K_thermal_all.items()
    )
    n_el = sum(1 for el in ELEMENTS if row[f'{el}_frac'] > 0)
    if n_el > 2:
        k_hea *= 0.6  # phonon scattering reduction in HEA
    
    # 2. Ceramic radiative conductivity (Rosseland) — ceramic fraction only
    # Only meaningful in ceramic-dominant region
    sigma = 5.67e-8
    n_refrac = 2.2        # refractive index of ZrO2-type ceramic
    l_r = 30e-6           # photon mean free path
    k_rad_ceramic = (16/3) * sigma * (n_refrac**2) * (T**3) * l_r
    # ~2.1 W/mK at 1400K — this is the ceramic radiative contribution
    
    # 3. Rule of mixtures SEPARATELY for each mechanism
    # ceramic_frac at this layer position
    f_cer = layer_position
    f_hea = 1.0 - f_cer
    
    k_total = f_hea * k_hea + f_cer * k_rad_ceramic
    
    # 4. Sintering degradation applies ONLY to ceramic pore closure effect
    # It increases ceramic conductivity (pores close), not HEA
    k_total_ceramic_corrected = f_cer * k_rad_ceramic * 1.6 + f_hea * k_hea
    
    return k_total_ceramic_corrected

def estimate_cte(row):
    """Estimate CTE using Rule of Mixtures."""
    # CTE (µm/m/K) for pure elements
    CTE_ALL = {
        'Mo': 4.8, 'Nb': 7.3, 'Ta': 6.3, 'W': 4.5, 'Cr': 4.9,
        'V': 8.4, 'Ti': 8.6, 'Zr': 5.8, 'Hf': 5.9
    }
    return sum(
        row.get(f'{el}_frac', 0.0) * v
        for el, v in CTE_ALL.items()
    )

def load_experimental_data():
    """Extract real experimental Yield Strength using Transfer Learning."""
    print("\n--- Loading Real Experimental Datasets (Transfer Learning Approach) ---")
    
    # Extended refractory elements for pre-training (Transfer Learning)
    EXTENDED_ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']
    
    import re
    mpea_path = Path(__file__).parent.parent / 'data' / 'EXP-MPEA_dataset.csv'
    if not mpea_path.exists():
        print("No EXP-MPEA_dataset.csv found. Skipping experimental ML.")
        return None, None
        
    df_mpea = pd.read_csv(mpea_path)
    
    exp_features = []
    exp_targets = []
    sample_weights = []
    
    for _, row in df_mpea.iterrows():
        formula = str(row['FORMULA'])
        ys = row['PROPERTY: YS (MPa)']
        test_temp = row['PROPERTY: Test temperature ($^\circ$C)']
        
        if pd.isna(formula) or pd.isna(ys):
            continue
            
        found_els = set(re.findall(r'[A-Z][a-z]?', formula))
        
        # Check if it's within the extended refractory family
        if found_els.issubset(set(EXTENDED_ELEMENTS)) and len(found_els) > 0:
            
            # Fast fraction parsing for extended elements
            fracs = {el: 0.0 for el in EXTENDED_ELEMENTS}
            if formula in EXTENDED_ELEMENTS:
                fracs[formula] = 1.0
            else:
                matches = re.findall(r'([A-Z][a-z]?)(\d*\.?\d*)', formula)
                total = sum(float(val) if val else 1.0 for el, val in matches if el in EXTENDED_ELEMENTS)
                if total > 0:
                    for el, val in matches:
                        if el in EXTENDED_ELEMENTS:
                            fracs[el] = (float(val) if val else 1.0) / total
            
            # Create basic features suitable for extended elements
            features = {
                'T_test': float(test_temp) if not pd.isna(test_temp) else 25.0
            }
            # We must output exactly the same features as ALL_ELEMENTS! 
            for prop in ['r', 'X', 'VEC', 'Tm', 'mass', 'K']:
                features[f'avg_{prop}'] = sum(fracs[el] * ELEMENT_DATA[el][prop] for el in ALL_ELEMENTS if fracs.get(el, 0) > 0)

            for prop in ['r', 'X', 'VEC', 'Tm']:
                avg = features[f'avg_{prop}']
                val_std = 0
                if avg > 0:
                    var = sum(fracs.get(el, 0) * (ELEMENT_DATA[el][prop] - avg)**2 for el in ALL_ELEMENTS if fracs.get(el, 0) > 0)
                    val_std = np.sqrt(var)
                features[f'std_{prop}'] = val_std

            features['n_elements'] = sum(1 for el in ALL_ELEMENTS if fracs.get(el, 0) > 0)

            for el in ALL_ELEMENTS:
                features[f'{el}_frac'] = fracs.get(el, 0.0)

            # Determine if this is a strict target match (Weight = 10) or transfer learning match (Weight = 1)
            is_target = found_els.issubset(set(TARGET_ELEMENTS))
            weight = 10 if is_target else 1
            
            exp_features.append(features)
            exp_targets.append(float(ys))
            sample_weights.append(weight)

    if not exp_features:
        print("No valid experimental data found for target elements.")
        return None, None
        
    X_exp = pd.DataFrame(exp_features)
    y_exp = np.array(exp_targets)
    w_exp = np.array(sample_weights)
    
    target_count = sum(1 for w in w_exp if w == 10)
    transfer_count = len(y_exp) - target_count
    
    print(f"Loaded {transfer_count} broader Refractory alloys (Transfer Learning).")
    print(f"Loaded {target_count} EXACT target alloys (Heavily weighted anchors).")
    
    # Train Experimental Gradient Boosting Regressor
    scaler = StandardScaler()
    X_exp_scaled = scaler.fit_transform(X_exp)
    
    # Let model learn from test temp and compositions
    model = GradientBoostingRegressor(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X_exp_scaled, y_exp, sample_weight=w_exp)
    
    print(f"Experimental YS Model Training R²: {model.score(X_exp_scaled, y_exp):.3f}")
    
    return model, scaler

if __name__ == '__main__':
    print("Step 1: Loading and preparing theoretical base data...")
    df_train = load_and_prepare_base_data()
    
    print("\nStep 2: Training theoretical models (Bulk Modulus)...")
    theoretical_model, theoretical_scaler = train_model(df_train)
    MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_OUTPUT, 'wb') as fout:
        pickle.dump((theoretical_model, theoretical_scaler), fout)
    print(f"Bulk modulus model saved to {MODEL_OUTPUT}")
    
    print("\nStep 3: Training experimental models (Yield Strength)...")
    exp_model, exp_scaler = load_experimental_data()
    
    print("\nStep 4: Predicting properties for all generated stable compositions...")
    if not STABLE_COMPOSITIONS_FILE.exists():
        print("stable_compositions.csv not found. Run empirical_filter.py first.")
    else:
        compositions_df = pd.read_csv(STABLE_COMPOSITIONS_FILE)
        
        # We need ALL_ELEMENTS for predict features
        # Add 0 fracs for elements missing in compositions_df
        for el in ALL_ELEMENTS:
            if f"{el}_frac" not in compositions_df.columns:
                compositions_df[f"{el}_frac"] = 0.0

        predictions_df = predict_compositions(
            theoretical_model, 
            theoretical_scaler, 
            compositions_df,
            exp_model,
            exp_scaler
        )
        
        predictions_df.to_csv(PREDICTIONS_OUTPUT, index=False)
        print(f"\nSaved extensive predictions to {PREDICTIONS_OUTPUT}")
