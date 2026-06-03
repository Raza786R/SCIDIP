# Safran HE-MCGA Project: Critical Bottlenecks & Low-Compute Mitigation Strategy

## Document Purpose
This document serves as a comprehensive context file for any higher-end AI models (e.g., Bohrium, Claude 3.5 Sonnet) assisting with the Safran Explore Smart Materials Program (HE-MCGA). It breaks down the critical bottlenecks identified by the AI analysis and outlines the exact strategies we will use to achieve our goals under strict **low-computation-cost constraints**. 

**Core Question:** Can we achieve the HE-MCGA discovery for Safran on a low compute budget?
**Answer:** **Yes, absolutely.** If we implement a rigid, funnel-based Multi-Fidelity optimization pipeline, we can bypass the impossible computational burden of simulating millions of structures.

---

## 1. ML Model Selection & Structural Data Bottleneck
### The Bottleneck
We cannot use Graph Neural Networks like ALIGNN for broad screening. ALIGNN requires exact 3D `.cif` configurations. Generating Special Quasi-random Structures (SQS) for continuous fractional 5-element Refractory High Entropy Alloys (RHEAs) to feed into ALIGNN takes immense compute and time per material.

### The Low-Compute Mitigation Strategy (Tiered Screening)
We will adopt a multi-stage funnel to narrow down from millions to a handful computationally cheaply.
*   **Tier 1 (Cost: Extremely Low):** **High-Throughput Compositional Screening**
    *   We generate millions of compositions mathematically based on fractions.
    *   Filter using empirical thermodynamics: *Miedema's Empirical Rules* ($\Delta H_{mix}$, Atomic Size Mismatch $\delta$). This is pure math and costs almost zero compute.
    *   Use Composition-Only ML (e.g., CrabNet or Roost) trained on existing Mo-Nb-Ta-W-Cr data to estimate basic bulk parameters without needing 3D structures.
*   **Tier 2 (Cost: Moderate):** **Virtual Crystal Approximation (VCA)**
    *   For the thousands that pass Tier 1, map them to surrogate Body-Centered Cubic (BCC) lattices scaled using Vegard's law. VCA gives a physically informed check against phase separation.
*   **Tier 3 (Cost: High, but restricted):** **Fidelity Verification (SQS + DFT)**
    *   We run expensive SQS and DFT *only* on the top 0.1% (tens of candidates).

---

## 2. Bayesian Optimization Under Extreme Data Scarcity
### The Bottleneck
Since fractional HEAs do not natively exist in datasets, we suffer from extreme data scarcity. Standard Gaussian Processes (GPs) struggle with high-dimensional spaces that mix categorical crystal data with continuous fractional compositions.

### The Low-Compute Mitigation Strategy
We must use **Multi-Fidelity Bayesian Optimization (MFBO)**. 
*   **Latent Variable Gaussian Process (LVGP):** The surrogate model will map categorical and compositional data into a continuous latent space for efficient learning.
*   **Cost-Aware Sampling:** The acquisition function (like Expected Improvement) will focus purely on selecting candidates that provide maximum information for the absolute minimum compute (using algorithms like Cost-Aware Gradient Entropy Search or Expected Hypervolume Improvement).
*   **Active Learning:** Every single FEniCS FEA run is fed back into the surrogate model.

---

## 3. FEniCS FEA: Simulating 10,000 Thermal Cycles
### The Bottleneck
Running 10,000 thermal cycles spanning 300K to 1400K across a full 5mm HEA-ceramic gradient creates major numerical divergence, singularities at interfaces due to sudden CTE shifts, and impossible computing times for local machines.

### The Low-Compute Mitigation Strategy
We *cannot* and *will not* simulate all 10,000 cycles for every candidate natively in full-scale 3D FEniCS while searching.
1.  **Reduce FEniCS dimensionality during search:** Use 1D or 2D axisymmetric reduced-order models during the Bayesian Optimization loop to establish the interface Von Mises stresses rapidly.
2.  **Surrogate the Simulator:** Train the MFBO surrogate model to predict FEniCS output (Stress max). We only spin up the actual FEniCS solver when the surrogate identifies an ultra-promising candidate.
3.  **Halt on Early Failure:** If thermal stresses exceed the yield point in the first 3 cycles, terminate the simulation immediately to save compute.

---

## Final Project Verdict for Safran
By implementing this Multi-Fidelity Active Learning approach, we isolate the expensive computing (ALIGNN/FEniCS/DFT) only to the absolute apex candidates. The vast majority of the discovery happens via zero-cost algorithms (Miedema rules) and low-cost composition models (CrabNet). **This confirms the feasibility of achieving Safran's HE-MCGA objective within practical, low-compute bounds.**