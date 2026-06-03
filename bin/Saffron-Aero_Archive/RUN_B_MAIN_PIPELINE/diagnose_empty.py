import pandas as pd, numpy as np, sys
sys.path.insert(0,'scripts')
from run_1d_fea import solve_1d_thermoelastic_surrogate

ml = pd.read_csv('models/ml_predictions.csv')
print('=== ML PREDICTIONS QUALITY CHECK ===')
print(f'Total rows: {len(ml)}')
print(f'Positive bulk modulus: {(ml.predicted_bulk_modulus > 0).sum()}')
print(f'Negative bulk modulus: {(ml.predicted_bulk_modulus <= 0).sum()} <- skipped by TASK-5 guard')
print(f'Bulk modulus range: {ml.predicted_bulk_modulus.min():.1f} to {ml.predicted_bulk_modulus.max():.1f} GPa')
print(f'YS range: {ml.predicted_yield_strength_MPa.min():.0f} to {ml.predicted_yield_strength_MPa.max():.0f} MPa')
print(f'CTE range: {ml.predicted_CTE.min():.3f} to {ml.predicted_CTE.max():.3f}')

ALL_9 = ['Mo','Nb','Ta','W','Cr','V','Ti','Zr','Hf']
frac_cols = [c for c in [f'{el}_frac' for el in ALL_9] if c in ml.columns]
hea_mask = (ml[frac_cols] >= 0.05).sum(axis=1) >= 5
df_hea = ml[hea_mask]
print(f'\nTrue HEA rows: {len(df_hea)}')

print('\n=== SAMPLE FEA CALLS (5 sample true HEAs with LZO n=1.0) ===')
knockdown = max(0.3, 1.0 - 0.8 * 1400/3290)
print(f'YS knockdown at 1400K: {knockdown:.3f}')

results = []
for i, (_, row) in enumerate(df_hea.head(5).iterrows()):
    hea_E_Pa = (row['predicted_bulk_modulus'] * 1.2) * 1e9
    hea_alpha = row['predicted_CTE'] * 1e-6
    hea_k = row['predicted_thermal_cond']
    ys = row.get('predicted_yield_strength_MPa', 0)
    ys_hot = ys * knockdown
    stress = solve_1d_thermoelastic_surrogate(hea_E=hea_E_Pa, hea_alpha=hea_alpha, hea_k=hea_k, ceramic_type='LZO', n_exponent=1.0)
    sf = ys_hot / stress if stress > 0 else 0
    results.append(sf)
    formula = row['formula']
    print(f'  K={row["predicted_bulk_modulus"]:.0f}GPa  YS_RT={ys:.0f}  YS_hot={ys_hot:.0f}  stress={stress:.1f}MPa  SF={sf:.3f}  [{formula}]')

print(f'\n=== ROOT CAUSE ANALYSIS ===')
max_sf = max(results)
print(f'Max SF seen in sample: {max_sf:.3f}')
if max_sf < 1.50:
    # Check if YS is the problem or stress is the problem
    avg_ys = df_hea['predicted_yield_strength_MPa'].mean()
    avg_ys_hot = avg_ys * knockdown
    print(f'Average YS_RT: {avg_ys:.0f} MPa')
    print(f'Average YS_hot (at 1400K): {avg_ys_hot:.0f} MPa')
    print(f'For SF=1.50, need stress <= {avg_ys_hot/1.5:.0f} MPa')
    print(f'Issue: YS_hot is too low OR stress is too high')
    print(f'Best 5 YS_RT values: {sorted(df_hea["predicted_yield_strength_MPa"])[-5:]}')
