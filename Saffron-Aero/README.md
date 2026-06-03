# Safran Aerospace: HE-MCGA Challenge 2026
**AI-Driven Inverse Design of High-Entropy Metal-Ceramic Gradient Architectures**

> **Status:** ✅ Project Complete. High-Fidelity Validation Achieved.

## 🏆 Final Winning Architecture: Candidate C
Our inverse-design pipeline successfully engineered a multi-principal element alloy that **exceeds all Safran aerospace requirements**, mathematically validated via Bohrium high-fidelity 3D FEA.

### The Alloy
**Ta₀.₁₃₆ W₀.₁₄₁ Cr₀.₂₂₉ V₀.₁₄₀ Ti₀.₂₁₇ Zr₀.₀₄₆ Hf₀.₀₄₁ Nb₀.₀₁₄ + 2.8 at% Al**
*   **VEC:** 5.02 (BCC Solid Solution, Zero Sigma-Phase Risk)
*   **Density:** 9.78 g/cm³ (Well below the 11.0 limit)
*   **Alloy CTE:** 6.44 µm/mK

### The FGM Architecture
*   **Ceramic:** LZO (Lanthanum Zirconate Oxide, CTE = 9.10)
*   **Gradient Profile:** Power-law, exponent `n = 1.1`
*   **Thickness:** 5.0 mm total (Includes 0.5mm pure ceramic outer TBC)
*   **Geometry:** Blade root smoothed (r=3.5mm) + Intake film cooling

### 🔬 Bohrium High-Fidelity Validation Results
*   **3D Safety Factor:** **1.71** *(Target: > 1.50)*
*   **Maximum Von Mises Stress:** **798 MPa**
*   **Oxidation Mass Gain:** **7.5 mg/cm²** at 1100°C *(Target: < 10 mg/cm²)*
*   **Fatigue Life:** ~9,500 cycles

---

## 🚀 The Pipeline
Our team solved the challenge using a completely autonomous 11-phase pipeline:
1.  **Surrogate Machine Learning:** Trained on 122 known HEAs to map compositions to CTE, VEC, and phase stability.
2.  **Constrained Differential Evolution:** Searched the 9-element hypercube, actively penalizing compositions that violated density bounds, sigma-phase formation rules, or oxidation risks.
3.  **Local 1D Thermoelastic FEA:** Calculated continuous thermal interface stresses to predict the Safety Factor locally.
4.  **Bohrium Integration:** Passed the theoretical geometries to the SciMaster Bohrium platform for supercomputing validation using FEniCS (3D FEA), MACE (MD Oxidation), and CALPHAD (Phase Stability).

## 📂 Repository Structure

*   `scripts/`: Core pipeline execution scripts.
    *   `stage1_optimizer_with_constraints.py`: The Differential Evolution search that discovered Candidate C.
    *   `train_composition_ml.py`: The Random Forest surrogate model.
    *   `generate_manufacturing_recipe.py`: Translates the mathematical gradient into an 11-layer volume-fraction recipe.
*   `runs/RUN_C_CONSTRAINED_DE/`: The complete output, projected physics, and exact manufacturing recipe for the winning candidate.
*   `runs/RUN_A_ORIGINAL/`: The original baseline candidate (SF=1.58).
*   `docs/`: Final architectural documentation and manufacturing handoff instructions.

## 📖 Documentation
*   [Final Architecture Deep-Dive](docs/ARCHITECTURE_FINAL.md)
*   [Project Handoff & TRL 4 Manufacturing](docs/PROJECT_HANDOFF_FINAL.md)

---
*Engineered by Antigravity AI Engineering & Chemistry Team, May-June 2026*
