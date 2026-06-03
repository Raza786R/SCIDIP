from AlloySustainability.computations import load_element_indicators, compute_impacts

composition_mass = [
    0.0,   # Al
    0.0,   # Co
    0.27,  # Cr
    0.0,   # Cu
    0.0,   # Fe
    0.18,  # Hf
    0.0,   # Mn
    0.0,   # Mo
    0.0,   # Nb
    0.0,   # Ni
    0.0,   # Re
    0.0,   # Ru
    0.0,   # Si
    0.16,  # Ta
    0.13,  # Ti
    0.15,  # V
    0.11,  # W
    0.0    # Zr
]

print("--- Stage 5: Sustainability Screening (Gorsse 2025 Model) ---")
element_indicators = load_element_indicators()
impacts = compute_impacts(composition_mass, element_indicators)
print(impacts)
