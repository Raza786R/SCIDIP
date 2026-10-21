# Phase 1 supersedes this historical entry point; see phase1/README.md.
if __name__ == "__main__":
    from _legacy_guard import stop_legacy_entrypoint
    stop_legacy_entrypoint(__file__)

# ==============================================================================
# MANUFACTURING NOTE: TO PRESERVE COMPATIBILITY ACROSS PROPRIETARY ADDITIVE
# SYSTEMS, THIS LAYERING SCRIPT GENERATES A HARDWARE-AGNOSTIC DATA MATRIX (.CSV).
# THE GRADIENT IS PARSED INTO AN 11-LAYER DISCRETE MULTI-HOPPER POWDER PROFILE.
# ==============================================================================
import pandas as pd
import numpy as np
import os

def generate_layer_recipe():
    # Load the top candidates
    df = pd.read_csv(os.path.join('models', 'top_50_candidates.csv'))
    
    if len(df) == 0:
        print("ERROR: top_50_candidates.csv is empty.")
        print("Re-run the pipeline (Steps 1-6) before generating recipes.")
        print("See FIXES_PLAN_VERIFIED.md for the minimum viable fix sequence.")
        return
    
    # Take the absolute best candidate (#1)
    best = df.iloc[0]
    
    thickness_mm = 5.0  # Total coating thickness
    num_layers = 11     # e.g., print in 11 specific layers for manufacturing
    
    # Physical depth positions
    depths = np.linspace(0, thickness_mm, num_layers)
    
    # Calculate volume fractions using the gradient exponent
    # Formula: V_ceramic = (x / L)^n
    n = best['gradient_exponent']
    v_ceramic = (depths / thickness_mm) ** n
    v_metal = 1.0 - v_ceramic
    
    # Create the recipe dataframe
    recipe = pd.DataFrame({
        'Layer_Index': np.arange(1, num_layers + 1),
        'Depth_mm': np.round(depths, 2),
        'Alloy_Vol_Percent': np.round(v_metal * 100, 1),
        'Ceramic_Vol_Percent': np.round(v_ceramic * 100, 1),
        'Alloy_Formula': best['formula'],
        'Ceramic_Type': best['ceramic_type']
    })
    
    output_path = os.path.join('models', 'top1_manufacturing_recipe.csv')
    recipe.to_csv(output_path, index=False)
    
    print(f"--- FGM LAYER RECIPE FOR #1 CANDIDATE ---")
    print(f"Gradient Exponent Used: {n}\n")
    print(recipe.to_string(index=False))
    print(f"\nSaved detailed manufacturing recipe to: {output_path}")

if __name__ == "__main__":
    generate_layer_recipe()
