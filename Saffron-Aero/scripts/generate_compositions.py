"""
Generate all fractional HEA compositions for Mo-Nb-Ta-W-Cr system.
Uses 5% increments with constraint: sum(fractions) = 1.0
"""
import itertools
import pandas as pd
import numpy as np
from pathlib import Path

ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr']
STEP = 0.05  # 5% increments
MIN_FRAC = 0.05  # Minimum 5% of each element for true HEA
OUTPUT_FILE = Path(__file__).parent.parent / 'data' / 'all_compositions-generated.csv'

def generate_compositions(step=STEP, min_frac=MIN_FRAC, require_all_elements=False):
    """
    Generate all valid fractional compositions.
    
    Args:
        step: Increment step (0.05 = 5%)
        min_frac: Minimum fraction per element (0.05 = 5%)
        require_all_elements: If True, all 5 elements must be present (true HEA)
    """
    fractions = np.arange(0, 1.0 + step/2, step)
    fractions = np.round(fractions, 3)  # Avoid floating point issues
    
    compositions = []
    
    # Generate all combinations of 5 fractions
    for combo in itertools.product(fractions, repeat=5):
        if abs(sum(combo) - 1.0) < 1e-6:  # Sum must equal 1
            # Check minimum fraction constraint if required
            if require_all_elements:
                if all(f >= min_frac for f in combo):
                    compositions.append(combo)
            else:
                # Allow zeros (for binaries, ternaries, quaternaries)
                compositions.append(combo)
    
    return compositions

def create_formula(fracs):
    """Create formula string from fractions."""
    parts = []
    for el, f in zip(ELEMENTS, fracs):
        if f > 0:
            if f == 1.0:
                parts.append(el)
            else:
                parts.append(f"{el}{f:.2f}")
    return ''.join(parts)

def main():
    print("Generating HEA compositions...")
    print(f"Elements: {ELEMENTS}")
    print(f"Step size: {STEP*100}%")
    
    # Generate with minimum 5% per element (true HEAs only)
    compositions = generate_compositions(step=STEP, min_frac=MIN_FRAC, require_all_elements=True)
    print(f"True HEAs (all 5 elements ≥5%): {len(compositions):,}")
    
    # Also generate including binaries/ternaries/quaternaries
    all_compositions = generate_compositions(step=STEP, min_frac=0, require_all_elements=False)
    print(f"All combinations (including sub-systems): {len(all_compositions):,}")
    
    # Create DataFrame
    data = []
    for comp in all_compositions:
        row = {
            'formula': create_formula(comp),
            'Mo_frac': comp[0],
            'Nb_frac': comp[1],
            'Ta_frac': comp[2],
            'W_frac': comp[3],
            'Cr_frac': comp[4],
            'n_elements': sum(1 for f in comp if f > 0),
            'is_true_hea': all(f >= MIN_FRAC for f in comp)
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved {len(df):,} compositions to {OUTPUT_FILE}")
    
    # Summary statistics
    print("\n--- Summary ---")
    print(f"Pure elements (unary): {len(df[df['n_elements']==1])}")
    print(f"Binary alloys: {len(df[df['n_elements']==2])}")
    print(f"Ternary alloys: {len(df[df['n_elements']==3])}")
    print(f"Quaternary alloys: {len(df[df['n_elements']==4])}")
    print(f"Quinary HEAs: {len(df[df['n_elements']==5])}")
    print(f"True HEAs (all ≥5%): {len(df[df['is_true_hea']])}")
    
    return df

if __name__ == "__main__":
    df = main()
