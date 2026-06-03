import sys

with open('train_composition_ml.py', 'a', encoding='utf-8') as f:
    text = """def load_experimental_data():
    \"\"\"Extract real experimental Yield Strength using Transfer Learning.\"\"\"
    print("\\n--- Loading Real Experimental Datasets (Transfer Learning Approach) ---")
    
    # Extended refractory elements for pre-training (Transfer Learning)
    EXTENDED_ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']
    
    import re
    mpea_path = Path(__file__).parent / 'EXP-MPEA_dataset.csv'
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
    
    print("\\nStep 2: Training theoretical models (Bulk Modulus)...")
    theoretical_model, theoretical_scaler = train_model(df_train)
    
    print("\\nStep 3: Training experimental models (Yield Strength)...")
    exp_model, exp_scaler = load_experimental_data()
    
    print("\\nStep 4: Predicting properties for all generated stable compositions...")
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
        print(f"\\nSaved extensive predictions to {PREDICTIONS_OUTPUT}")
"""
    f.write(text)
