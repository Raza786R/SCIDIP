"""
CALPHAD Phase Validation Script for Saffron-Aero
Designed to evaluate high-temperature stability of the 
Mo-Nb-Ta-W-Cr base alloy at 1400K.
"""
import time
import os
import pandas as pd

def run_calphad_simulation(tdb_path="TCHEA4.TDB"):
    print("--- CALPHAD Phase Stability Validation ---")
    print("Target Temperature: 1400 K (1127 C)")
    
    # Check if TDB exists
    if not os.path.exists(tdb_path):
        print(f"\n[WARNING] {tdb_path} not found in workspace.")
        print("Without a real TDB, mark all stability claims as empirical-filter-only, not CALPHAD-validated.")
        print("Returning mock phase for now.\n")
        return
        
    try:
        from pycalphad import Database, equilibrium, variables as v
    except ImportError:
        print("[ERROR] pycalphad is not installed. Run: pip install pycalphad")
        return

    print(f"Loading Database {tdb_path}...")
    db = Database(tdb_path)
    
    # Define the system
    comps = ["TA", "W", "CR", "V", "TI", "HF", "AL", "VA"]  # VA = vacancy, required
    phases = list(db.phases.keys())
    
    # Run C winner + 2.8% Al oxidation addition (Candidate C)
    # Nb0.014 Ta0.140 W0.145 Cr0.236 V0.144 Ti0.223 Zr0.047 Hf0.042 → normalised after adding 2.8% Al
    composition = {
        v.X("TA"): 0.136,
        v.X("W"):  0.141,
        v.X("CR"): 0.229,
        v.X("V"):  0.140,
        v.X("TI"): 0.217,
        v.X("HF"): 0.041,
        v.X("AL"): 0.028,
        # TI is dependent (pycalphad infers last element)
    }
    
    # Evaluate at 1400K
    conds = {
        v.T: 1400,
        v.P: 101325,
        **composition
    }
    
    result = equilibrium(db, comps, phases, conds)
    
    # Extract phase fractions
    phase_fracs = result.Phase.values.squeeze()
    phase_names = result.Phase.coords["Phase"].values
    
    print("\n--- RESULTS at 1400K ---")
    for phase, frac in zip(phase_names, phase_fracs):
        if frac > 1e-6:
            print(f"Phase: {phase}, Fraction: {frac:.4f}")
    
    return result

if __name__ == "__main__":
    run_calphad_simulation("TCHEA4.TDB")
