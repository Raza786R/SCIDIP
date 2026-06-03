# Project Handoff: TRL 4 Manufacturing Pathway

This document outlines the transition of the theoretically verified **Candidate C High-Entropy Metal-Ceramic Gradient Architecture (HE-MCGA)** into physical, Technology Readiness Level (TRL) 4 prototype manufacturing.

## 1. The Verified Architecture

**Target Components:**
*   **Alloy Substrate:** Ta₀.₁₃₆ W₀.₁₄₁ Cr₀.₂₂₉ V₀.₁₄₀ Ti₀.₂₁₇ Zr₀.₀₄₆ Hf₀.₀₄₁ Nb₀.₀₁₄ + 2.8 at% Al
*   **Ceramic Top-Coat:** Lanthanum Zirconate Oxide (LZO)
*   **Gradient Profile:** Power-law FGM, `n=1.1`, total transition depth 5.0mm (inclusive of 0.5mm outer pure ceramic).

**Validation Status:**
Bohrium 3D FEA has confirmed a **Safety Factor of 1.71**, maximum Von Mises stress of **798 MPa**, and an oxidation mass gain of **7.5 mg/cm²** at 1100°C. 

---

## 2. Recommended Manufacturing Pathway

To realize the complex 11-layer compositional gradient modeled in `runs/RUN_C_CONSTRAINED_DE/manufacturing_recipe.csv`, traditional casting methods are insufficient. We recommend localized additive manufacturing.

### Primary Methodology: Laser Engineered Net Shaping (LENS)
LENS or Directed Energy Deposition (DED) is uniquely suited for building FGMs.
1.  **Powder Feed:** The system must support multi-hopper powder feeding.
2.  **Hopper A:** Pre-alloyed powder of the Candidate C metallic composition.
3.  **Hopper B:** LZO ceramic powder.
4.  **Deposition:** The build must modulate the feed rate of Hopper A vs Hopper B continuously to achieve the `n=1.1` volume fraction curve over the outer 5.0mm of the turbine blade geometry.

### Budget & Prototyping Geography
Our business model indicates that low-volume prototype manufacturing can be achieved highly cost-effectively through partnerships with Indian aerospace research facilities (e.g., ISRO-affiliated labs or HAL R&D centers). 

*   **Estimated Alloy Cost:** ~$201 / kg (Significantly reduced due to high Ti/low Hf content relative to baseline HEAs).
*   **Pre-Scale Budget Cap:** Prototype execution can be constrained under INR 20,00,000.

---

## 3. Physical Validation Goals (TRL 4)

Once the physical coupon/blade is printed, it must undergo experimental validation to corroborate the Bohrium simulations.

1.  **Thermogravimetric Analysis (TGA):** Expose the sample to 1100°C for 100 hours to experimentally verify the predicted 7.5 mg/cm² mass gain and confirm the presence of the α-Al₂O₃ scale.
2.  **X-Ray Diffraction (XRD):** Verify the substrate remains a single-phase BCC solid solution and that no brittle sigma-phase intermetallics have precipitated during the cooling cycle of the LENS process.
3.  **Thermal Cycling:** Subject the FGM sample to burner rig testing (300K ↔ 1400K) to verify resistance to delamination and crack propagation at the metal/ceramic interface.

---

## 4. Next Steps for Safran

1.  **Procure Powders:** Source high-purity elemental powders and initiate mechanical alloying, or contract a specialty powder manufacturer for the pre-alloyed Candidate C mixture.
2.  **LENS Trial:** Execute a flat-coupon print of the FGM gradient to dial in laser power, scan speed, and powder flow rates before attempting the full 3D turbine blade geometry with root smoothing.
3.  **Proceed to Testing.**
