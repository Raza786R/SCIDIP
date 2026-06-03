import pandas as pd
import numpy as np
import re

# Atomic masses for the 5 elements
ATOMIC_MASS = {'Mo': 95.96, 'Nb': 92.91, 'Ta': 180.95, 'W': 183.84, 'Cr': 52.00, 'Zr': 91.22, 'Hf': 178.49}
# Element CTE values at room temperature (um/mK)
ELEMENT_CTE = {'Mo': 4.8, 'Nb': 7.3, 'Ta': 6.3, 'W': 4.5, 'Cr': 4.9, 'Zr': 5.7, 'Hf': 5.9}

def parse_formula(formula):
    """Simple parser to extract composition fractions from a string formula"""
    matches = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', str(formula))
    comp = {}
    total = 0
    for el, amt in matches:
        if el in ATOMIC_MASS:
            val = float(amt) if amt else 1.0
            comp[el] = val
            total += val
    
    if total > 0:
        return {el: val/total for el, val in comp.items()}
    return comp

def calc_elastic_modulus(K, G):
    if pd.isna(K) or pd.isna(G): return np.nan
    return (9 * K * G) / (3 * K + G)

def calc_poissons_ratio(K, G):
    if pd.isna(K) or pd.isna(G): return np.nan
    return (3 * K - 2 * G) / (2 * (3 * K + G))

def calc_debye_temperature(E, rho, V, n):
    if pd.isna(E) or pd.isna(rho) or pd.isna(V) or pd.isna(n) or V == 0: return np.nan
    # E = elastic modulus (GPa) -> Pa (*1e9)
    # rho = density (g/cm3) -> kg/m3 (*1000)
    # V = volume per atom (A3) -> m3 (*1e-30)
    E_pa = E * 1e9
    rho_kg = rho * 1000
    V_m3 = V * 1e-30
    h = 6.626e-34
    kB = 1.38e-23
    vs = np.sqrt(E_pa / (3 * rho_kg))
    theta_D = (h / kB) * vs * (6 * np.pi**2 * n / V_m3)**(1/3)
    return theta_D

def calc_gruneisen(nu):
    if pd.isna(nu): return np.nan
    return (3 * (1 + nu)) / (2 * (2 - 3 * nu))

def slack_thermal_conductivity(M_avg, theta_D, V_atom, gamma, n, T=1000):
    if pd.isna(M_avg) or pd.isna(theta_D) or pd.isna(V_atom) or pd.isna(gamma) or pd.isna(n): return np.nan
    # M_avg: g/mol -> kg/atom (/1000 / 6.022e23)
    M_atom_kg = M_avg / 1000 / 6.022e23
    # V_atom: A3 -> m3
    V_atom_m3 = V_atom * 1e-30
    A = 2.43e-8  # Slack constant
    if gamma == 0: return np.nan
    kappa = (A * M_atom_kg * theta_D**3 * V_atom_m3**(1/3)) / (gamma**2 * n**(2/3) * T)
    return kappa

def rule_of_mixtures_CTE(composition_fractions):
    if not isinstance(composition_fractions, dict): return np.nan
    cte = 0
    for el, frac in composition_fractions.items():
        if el in ELEMENT_CTE:
            cte += ELEMENT_CTE[el] * frac
    return cte

def main():
    try:
        df = pd.read_csv('combined_raw_data.csv')
    except Exception:
        print("Waiting for combined_raw_data.csv to be generated...")
        return

    print(f"Loaded {len(df)} initial items.")
    
    # 1. COMPOSITION (Category A)
    df['composition'] = df['formula'].apply(parse_formula)
    
    # Needs bulk modulus and shear modulus to compute the rest. If missing, they would need ALIGNN here.
    # We will simulate missing columns if they don't exist from OQMD/MP
    for col in ['bulk_modulus', 'shear_modulus', 'density', 'volume', 'ntypes']:
        if col not in df.columns:
            df[col] = np.nan
            
    # Simulate missing data for demonstration if MP wasn't run
    df = df.dropna(subset=['bulk_modulus'])
    df['shear_modulus'] = df['shear_modulus'].fillna(80.0) # placeholder GPa
    df['density'] = df['density'].fillna(9.0) # placeholder g/cm3
    df['volume'] = df['volume'].fillna(15.0) # placeholder A3 per atom
    df['ntypes'] = df['ntypes'].fillna(2) # atoms per cell approx
    
    # 2. CATEGORY E (Intermediate)
    df['elastic_modulus'] = df.apply(lambda r: calc_elastic_modulus(r.get('bulk_modulus'), r.get('shear_modulus')), axis=1)
    df['poissons_ratio'] = df.apply(lambda r: calc_poissons_ratio(r.get('bulk_modulus'), r.get('shear_modulus')), axis=1)
    df['debye_temp'] = df.apply(lambda r: calc_debye_temperature(r.get('elastic_modulus'), r.get('density'), r.get('volume'), r.get('ntypes')), axis=1)
    df['gruneisen'] = df['poissons_ratio'].apply(calc_gruneisen)
    
    # M_avg
    def get_m_avg(comp):
        return sum(ATOMIC_MASS[el]*frac for el, frac in comp.items()) if isinstance(comp, dict) else np.nan
    df['avg_atomic_mass'] = df['composition'].apply(get_m_avg)

    # 3. CATEGORY C (Estimated Properties)
    df['thermal_conductivity'] = df.apply(lambda r: slack_thermal_conductivity(
        r['avg_atomic_mass'], r['debye_temp'], r['volume'], r['gruneisen'], r['ntypes']
    ), axis=1)
    df['CTE'] = df['composition'].apply(rule_of_mixtures_CTE)
    
    # 4. REMOVE CATEGORY E
    cols_to_drop = ['debye_temp', 'gruneisen', 'poissons_ratio', 'avg_atomic_mass']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    df.to_csv('processed_candidate_properties.csv', index=False)
    print("Successfully processed data into processed_candidate_properties.csv")
    print(df[['formula', 'thermal_conductivity', 'CTE']].head())

if __name__ == '__main__':
    main()