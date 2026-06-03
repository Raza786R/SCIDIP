# HE-MCGA Project: Current State & Architecture Handoff

*Notice to future AI / Claude 3.5 Sonnet: Read this file FIRST. It contains all context, decisions, and files created to save your context window tokens.*

## 1. Project Goal
Build a dataset mapping material properties for a **High-Entropy Metal-Ceramic Gradient Architecture (HE-MCGA)** using a 5-element space: **Mo, Nb, Ta, W, Cr**. Final outputs must include thermomechanical properties across a 5mm spatial gradient, tested against thermal cycling via FEniCS (FEA).

## 2. Directory & Tools Created
- `fetch_datasets.py`: Queries Materials Project (MP), OQMD, AFLOW, and JARVIS. Strictly filters out any material containing elements outside the target 5. 
- `calculate_properties.py`: Computes Category E (Elastic Modulus, Poisson's, Debye Temp, Grüneisen) and calculates Category C predictions (Thermal Conductivity via Slack Model, CTE via Rule of Mixtures). Cleans intermediate data.
- `combined_raw_data.csv`: The pure metals, binary, and ternary alloys fetched from the APIs.
- `processed_candidate_properties.csv`: The mathematically enriched versions of the raw data.
- `/memories/repo/`: Contains hidden memory states tracking our pipeline hurdles.

## 3. The Core Complication (The HEA Missing Data Problem)
Public databases (MP, OQMD) use DFT, meaning they only store small crystalline unit cells (pure metals, binaries, ternaries like TaCr2). **True continuous fractional 5-element HEAs (e.g., 20% Mo, 20% Nb...) do not exist in these databases** because modeling random solid solutions requires massive Special Quasirandom Structure (SQS) supercells that take months to compute. 

Because we lack experimental database priors for these specific 5-element HEAs, the pipeline relies on:
1. **Machine Learning Extrapolation**: Using ML (like ALIGNN for bulk modulus) trained on general Jarvis/MP databases to interpolate behavior.
2. **Physics-based Equations**: Rule of Mixtures, Vegard's Law, and the Slack model.
3. **Miedema's Empirical Rules**: Calculating Mixing Enthalpy ($\Delta H_{mix}$), Atomic Size Mismatch ($\delta$), and VEC to prove thermodynamic phase stability.

## 4. Current Pipeline Bottlenecks & Drawbacks
1. **ALIGNN CIF Requirement**: The pipeline dictates predicting missing bulk moduli using ALIGNN. ALIGNN is a Graph Neural Network that strictly requires a 3D `.cif` structure file. We are generating abstract fractions mathematically, so we don't have CIFs to pass it. We must either generate virtual BCC crystals or bypass ALIGNN for a composition-only model (like Roost or CrabNet).
2. **Combinatorial Explosion**: Testing 1% fractional increments of 5 elements equals ~4.5 million HEA variants. 
3. **FEA Scaling**: FEniCS simulations are too slow to run on millions of generated variations. We must use Bayesian Optimization to downselect to a Top 50 before running gradients.

## 5. Next Planned Action
Build a Bayesian Optimization (BO) active learning loop that generates stable HEA fractions, filters them via empirical thermodynamics, predicts modulus, and funnels only the best candidates into the gradient simulation.