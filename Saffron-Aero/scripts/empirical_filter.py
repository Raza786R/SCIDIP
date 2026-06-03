"""
Apply Miedema's Empirical Rules for thermodynamic stability filtering.
Filters: δ (size mismatch), ΔHmix, VEC, ΔSmix
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Elemental properties for Mo, Nb, Ta, W, Cr
# Data from: Senkov et al., Takeuchi & Inoue, various sources
ELEMENT_DATA = {
    'Mo': {'r': 1.39, 'X': 2.16, 'VEC': 6, 'Tm': 2896},  # r in Å, X = electronegativity
    'Nb': {'r': 1.46, 'X': 1.60, 'VEC': 5, 'Tm': 2750},
    'Ta': {'r': 1.46, 'X': 1.50, 'VEC': 5, 'Tm': 3290},
    'W':  {'r': 1.39, 'X': 2.36, 'VEC': 6, 'Tm': 3695},
    'Cr': {'r': 1.28, 'X': 1.66, 'VEC': 6, 'Tm': 2180},
}

# Binary mixing enthalpies (kJ/mol) from Miedema's model
# Symmetric matrix: H_ij = H_ji
BINARY_ENTHALPY = {
    ('Mo', 'Nb'): -6,  ('Mo', 'Ta'): -5,  ('Mo', 'W'): 0,   ('Mo', 'Cr'): 0,
    ('Nb', 'Ta'): 0,   ('Nb', 'W'): -8,   ('Nb', 'Cr'): -7,
    ('Ta', 'W'): -7,   ('Ta', 'Cr'): -7,
    ('W', 'Cr'): 1,
}

ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr']
R_GAS = 8.314  # J/(mol·K)

INPUT_FILE = Path(__file__).parent.parent / 'data' / 'all_compositions-generated.csv'
OUTPUT_FILE = Path(__file__).parent.parent / 'data' / 'stable_compositions.csv'

# Stability criteria thresholds
DELTA_MAX = 6.6        # Atomic size mismatch (%)
HMIX_MIN = -15         # Min mixing enthalpy (kJ/mol)
HMIX_MAX = 5           # Max mixing enthalpy (kJ/mol)
VEC_MIN = 4.0          # Min VEC for BCC
VEC_MAX = 6.8          # Max VEC for BCC (>8 favors FCC)
OMEGA_MIN = 1.1        # Ω parameter (ΔSmix·Tm/|ΔHmix|) - higher favors solid solution

def get_binary_enthalpy(el1, el2):
    """Get binary mixing enthalpy (symmetric)."""
    if el1 == el2:
        return 0
    key = (el1, el2) if (el1, el2) in BINARY_ENTHALPY else (el2, el1)
    return BINARY_ENTHALPY.get(key, 0)

def calculate_delta(fracs):
    """Calculate atomic size mismatch δ (%)."""
    r_avg = sum(f * ELEMENT_DATA[el]['r'] for el, f in zip(ELEMENTS, fracs) if f > 0)
    if r_avg == 0:
        return 0
    
    delta_sq = sum(
        f * (1 - ELEMENT_DATA[el]['r'] / r_avg)**2 
        for el, f in zip(ELEMENTS, fracs) if f > 0
    )
    return 100 * np.sqrt(delta_sq)

def calculate_hmix(fracs):
    """Calculate mixing enthalpy ΔHmix (kJ/mol)."""
    hmix = 0
    for i, (el1, f1) in enumerate(zip(ELEMENTS, fracs)):
        for j, (el2, f2) in enumerate(zip(ELEMENTS, fracs)):
            if i < j and f1 > 0 and f2 > 0:
                hmix += 4 * get_binary_enthalpy(el1, el2) * f1 * f2
    return hmix

def calculate_smix(fracs):
    """Calculate mixing entropy ΔSmix (J/(mol·K))."""
    smix = 0
    for f in fracs:
        if f > 0:
            smix -= R_GAS * f * np.log(f)
    return smix

def calculate_vec(fracs):
    """Calculate valence electron concentration."""
    return sum(f * ELEMENT_DATA[el]['VEC'] for el, f in zip(ELEMENTS, fracs) if f > 0)

def calculate_tm_avg(fracs):
    """Calculate average melting temperature (K)."""
    return sum(f * ELEMENT_DATA[el]['Tm'] for el, f in zip(ELEMENTS, fracs) if f > 0)

def calculate_omega(fracs):
    """Calculate Ω parameter (dimensionless)."""
    smix = calculate_smix(fracs)
    hmix = calculate_hmix(fracs)
    tm = calculate_tm_avg(fracs)
    
    if abs(hmix) < 0.01:  # Avoid division by zero
        return 999  # Very favorable
    return (smix * tm) / (abs(hmix) * 1000)  # Convert kJ to J

def apply_filters(df):
    """Apply all stability filters to composition DataFrame."""
    print("Calculating thermodynamic parameters...")
    
    # Extract fraction columns
    frac_cols = ['Mo_frac', 'Nb_frac', 'Ta_frac', 'W_frac', 'Cr_frac']
    
    # Calculate all parameters
    df['delta'] = df[frac_cols].apply(lambda row: calculate_delta(row.values), axis=1)
    df['Hmix'] = df[frac_cols].apply(lambda row: calculate_hmix(row.values), axis=1)
    df['Smix'] = df[frac_cols].apply(lambda row: calculate_smix(row.values), axis=1)
    df['VEC'] = df[frac_cols].apply(lambda row: calculate_vec(row.values), axis=1)
    df['Tm_avg'] = df[frac_cols].apply(lambda row: calculate_tm_avg(row.values), axis=1)
    df['omega'] = df[frac_cols].apply(lambda row: calculate_omega(row.values), axis=1)
    
    print(f"\nTotal compositions: {len(df):,}")
    
    # Apply filters
    print("\n--- Applying Filters ---")
    
    # Filter 1: Atomic size mismatch
    mask_delta = df['delta'] <= DELTA_MAX
    print(f"δ ≤ {DELTA_MAX}%: {mask_delta.sum():,} pass ({100*mask_delta.mean():.1f}%)")
    
    # Filter 2: Mixing enthalpy
    mask_hmix = (df['Hmix'] >= HMIX_MIN) & (df['Hmix'] <= HMIX_MAX)
    print(f"ΔHmix ∈ [{HMIX_MIN}, {HMIX_MAX}] kJ/mol: {mask_hmix.sum():,} pass ({100*mask_hmix.mean():.1f}%)")
    
    # Filter 3: VEC for BCC
    mask_vec = (df['VEC'] >= VEC_MIN) & (df['VEC'] <= VEC_MAX)
    print(f"VEC ∈ [{VEC_MIN}, {VEC_MAX}]: {mask_vec.sum():,} pass ({100*mask_vec.mean():.1f}%)")
    
    # Filter 4: Ω parameter
    mask_omega = df['omega'] >= OMEGA_MIN
    print(f"Ω ≥ {OMEGA_MIN}: {mask_omega.sum():,} pass ({100*mask_omega.mean():.1f}%)")
    
    # Combined filter
    mask_all = mask_delta & mask_hmix & mask_vec & mask_omega
    print(f"\n✅ All filters passed: {mask_all.sum():,} compositions ({100*mask_all.mean():.1f}%)")
    
    return df[mask_all].copy()

def main():
    print("=" * 60)
    print("EMPIRICAL STABILITY FILTER FOR HEA COMPOSITIONS")
    print("=" * 60)
    
    # Load compositions
    if not INPUT_FILE.exists():
        print(f"ERROR: {INPUT_FILE} not found. Run generate_compositions.py first.")
        return None
    
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} compositions from {INPUT_FILE}")
    
    # Apply filters
    df_stable = apply_filters(df)
    
    # Save filtered results
    df_stable.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved {len(df_stable):,} stable compositions to {OUTPUT_FILE}")
    
    # Show top candidates by Ω (most likely to form solid solution)
    print("\n--- Top 10 by Ω Parameter ---")
    top10 = df_stable.nlargest(10, 'omega')[['formula', 'delta', 'Hmix', 'VEC', 'omega']]
    print(top10.to_string(index=False))
    
    # Summary by composition type
    print("\n--- Stable Compositions by Type ---")
    for n in range(1, 6):
        count = len(df_stable[df_stable['n_elements'] == n])
        print(f"{n}-element: {count:,}")
    
    return df_stable

if __name__ == "__main__":
    df = main()
