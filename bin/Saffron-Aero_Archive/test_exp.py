import pandas as pd
import re

elements = {'Mo', 'Nb', 'Ta', 'W', 'Cr'}

def is_valid(formula):
    if pd.isna(formula): return False
    found = set(re.findall(r'[A-Z][a-z]?', str(formula)))
    return found.issubset(elements) and len(found) > 0

df = pd.read_csv('EXP-MPEA_dataset.csv')
valid_df = df[df['FORMULA'].apply(is_valid)]
print(f"Found {len(valid_df)} rows matching our elements in MPEA dataset.")
print(valid_df[['FORMULA', 'PROPERTY: YS (MPa)', 'PROPERTY: Exp. Young modulus (GPa)']])

# Also check GE dataset
df_ge = pd.read_csv('EXP-GE_RefractoryAlloyScreeningDataset_FINAL.csv')
# Keep only rows where non-target elements are zero
non_target = [c for c in df_ge.columns if '(at%)' in c and c.replace('(at%)','') not in elements]

valid_ge = df_ge[df_ge[non_target].sum(axis=1) == 0]
print(f"\nFound {len(valid_ge)} rows matching our elements in GE Dataset.")
if len(valid_ge) > 0:
    print(valid_ge)
