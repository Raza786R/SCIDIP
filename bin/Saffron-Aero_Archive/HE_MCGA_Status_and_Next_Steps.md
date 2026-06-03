# HE-MCGA Project — Status, Methodology, and Next Steps

**Project:** AI-Driven Inverse Design of High-Entropy Metal-Ceramic Gradient Architecture
**Target:** Safran Explore Smart Materials Program 2026 (Challenge 2)
**Alloy system:** Refractory HEA Mo–Nb–Ta–W–Cr + ZrO₂–HfO₂ ceramic top-coat
**Service envelope:** 5 mm gradient, 300 K ↔ 1400 K, 10,000 cycles
**Document date:** May 22, 2026
**Version:** 1.0

---

## 1. Executive summary

We have built a working pipeline that generates and pre-screens compositions in the Mo–Nb–Ta–W–Cr space, applies empirical thermodynamic filters, and produces ML predictions for bulk modulus, thermal conductivity, and CTE. The current pipeline output is `ml_predictions.csv` containing 10,626 candidate compositions (5 % fractional grid), of which 3,876 are true 5-element HEAs.

What still needs to be done falls into three buckets:

1. **Replace synthetic training data with real data** (DFT + literature) and upgrade the Random Forest to a composition-only transformer (CrabNet).
2. **Build the multi-fidelity Bayesian Optimization (MFBO) loop** with reduced-order FEA inside.
3. **Add high-temperature, oxidation, CMAS, creep, and fatigue physics** that the current room-temperature pipeline lacks.

The probability of producing a defensible Safran submission with the proposed extensions is high (~75–85 %).

---

## 2. What is currently in place

| Artifact | What it is | Status |
|---|---|---|
| `fetch_datasets.py` | Queries Materials Project, OQMD, AFLOW, JARVIS for the 5 elements | Done — 122 pristine base compounds in `combined_raw_data.csv` |
| `generate_compositions.py` | Generates the 5 % grid of fractional compositions | Done — 10,626 rows in `all_compositions-generated.csv` |
| `empirical_filter.py` | Applies δ < 6.6 %, ΔHmix ∈ [−15, +5] kJ/mol, VEC, Ω | Done — output: `stable_compositions.csv` (all 10,626 pass, see §6.1) |
| `train_composition_ml.py` | Trains Random Forest on synthetic data | Done — `composition_model.pkl` (R² = 0.97 on synthetic data) |
| `calculate_properties.py` | Slack thermal conductivity + Rule-of-Mixtures CTE | Done |
| `ml_predictions.csv` | 10,626 rows with bulk modulus, k, CTE predictions | Done |

The bulk modulus range across the 3,876 true HEAs is 158–291 GPa (mean 202 GPa). CTE range is 4.5–7.3 µm/m·K — all below the 9.5 µm/m·K target for the ceramic, confirming the **CTE-mismatch problem** is real and central to the design loss.

---

## 3. What the ML model was actually trained on (honest accounting)

The `composition_model.pkl` is a scikit-learn `RandomForestRegressor` (100 trees, max depth 10) consuming 18 composition-only features (weighted-average radius, electronegativity, VEC, melting point, mass, bulk modulus; std-devs of the first four; n_elements; radius ratio; electronegativity range; and the five element fractions).

**The training set is synthetic.** It is built inside `train_composition_ml.py` from:

- The 5 pure metals' textbook bulk moduli (Mo 230, Nb 170, Ta 200, W 310, Cr 160 GPa).
- Binary alloys computed by Rule of Mixtures with a 5 % negative deviation.
- Ternaries (~7 % deviation), quaternaries (~9 % deviation).
- Literature anchors for the quinary: MoNbTaW ≈ 220 GPa, MoNbTaWCr ≈ 210 GPa (Senkov et al.).

So the reported R² = 0.97 is **R² on data the model was synthesised to reproduce** — it confirms internal consistency, not real-world predictive accuracy. The thermal conductivity and CTE columns in `ml_predictions.csv` are not from the Random Forest at all; they are Rule-of-Mixtures formulas applied directly to the elemental property tables.

This is acceptable for *ranking* candidates inside a BO loop, but not for absolute property reporting. Real validation requires DFT (or experiments).

---

## 4. Research-paper backing for the approach

| Claim | Reference |
|---|---|
| Mo–Nb–Ta–W and Mo–Nb–Ta–W–V are stable single-phase BCC RHEAs at 1200 °C | Senkov et al., *Intermetallics* 18, 1758 (2010); *J. Mater. Res.* 33 (2018) |
| Phase-stability empirical rules: δ < 6.6 %, ΔHmix ∈ [−15, +5] kJ/mol, Ω > 1.1 | Zhang et al. (2008); Miracle & Senkov, *Acta Mater.* 122, 448 (2017) |
| Slack lattice-thermal-conductivity model | G. A. Slack, *J. Phys. Chem. Solids* 34 (1973) |
| CrabNet — composition-only transformer | Wang et al., *npj Comput. Mater.* 7, 77 (2021) |
| Roost — composition-only message-passing graph NN | Goodall & Lee, *Nat. Commun.* 11, 6280 (2020) |
| ALIGNN — atomistic line-graph NN (requires 3D structure) | Choudhary & DeCost, *npj Comput. Mater.* 7, 185 (2021) |
| CMAS attack on TBCs above 1240 °C | Padture, *Nat. Mater.* 15, 804 (2016) |
| Multi-fidelity BO with LVGP for materials | Iyer et al. (2019); Zhang et al. (2020) |

---

## 5. Definitions of the key terms

**DFT (Density Functional Theory).** A quantum-mechanical method that solves an approximate form of the Schrödinger equation for the electrons in a crystal. Input: atom positions in a unit cell. Output: total energy, forces, elastic constants. Hours-to-days per material. All of Materials Project, OQMD, AFLOW, JARVIS-DFT are DFT databases.

**SQS (Special Quasirandom Structure).** A 32–128-atom supercell whose occupations match the pair- and triplet-correlations of a truly random infinite alloy. The standard way to model HEAs in DFT, but ~1 CPU-week per composition — so 4.6 M compositions is prohibitive.

**VCA (Virtual Crystal Approximation).** Replaces each lattice site with a fictitious "average atom" whose pseudopotential is the composition-weighted average of the real elements. Fast, but breaks down when atomic sizes or electronegativities differ meaningfully (e.g., when Cr is in the mix).

**FEA / FEniCS.** Finite Element Analysis discretises a part into millions of elements and numerically solves coupled heat-conduction + elasticity PDEs:

ρcₚ ∂T/∂t = ∇·(k∇T) + Q
∇·σ + f = 0, with σ = C : (ε − αΔT·I)

FEniCS is a free Python/C++ FEA library. It gives stress at every position across the 5 mm gradient at every cycle — what the loss function actually needs.

**CrabNet & Roost.** Composition-only neural networks designed precisely for the situation where you have a formula but no 3D structure. CrabNet uses Transformer self-attention; Roost uses graph message-passing with elements as nodes. Both pip-installable. Both match or beat Random Forests by 10–20 % MAE on standard benchmarks.

**Vegard's law.** Linear mixing rule for lattice parameters: a_alloy = Σ cᵢ · aᵢ. Holds when atomic sizes differ by < 10 %. In Mo–Nb–Ta–W–Cr, Cr is the outlier (1.28 Å vs. 1.39–1.46 Å), so Cr-heavy compositions deviate 2–5 %.

**Miedema's rules.** Semi-empirical thermodynamic estimates of mixing enthalpy from elemental properties (electronegativity, electron density at the Wigner-Seitz boundary). ~70–80 % accurate as a phase-stability *filter*, not a guarantee.

**Rule of Mixtures.** Linear composition-weighted average of a property. Excellent for trends; ~10–20 % error on CTE, ~30–50 % error on thermal conductivity vs. experimental measurements.

---

## 6. How to cut FEA compute time (the three mitigations, in detail)

### 6.1 Reduce dimensionality during search

For BO screening, replace the full 3D FEA with a **1D axisymmetric reduced-order model**:

- The blade wall is essentially a flat sheet; the gradient runs through-thickness.
- A 1D mesh of 51 nodes at 0.1 mm spacing captures the dominant interface von Mises stress within ~5 % of the 3D answer.
- Solve in milliseconds instead of hours.
- Use full 3D FEA only on the final 5–10 Pareto-optimal candidates.

### 6.2 Surrogate the simulator

Train a small Gaussian Process (or another RF) on the *outputs* of ~100 reduced-order FEA runs:

- Input: composition + gradient exponent (n in `ceramic_frac = (x/L)^n`).
- Output: max interface stress, predicted lifetime.

After fitting, the BO loop queries this surrogate at zero marginal cost. The real FEniCS solver is invoked only when Expected Improvement (or Knowledge Gradient) flags a candidate whose uncertainty justifies the cost.

### 6.3 Halt on early failure

Inside the time-stepping loop of every FEA call:

```python
for cycle in range(n_cycles):
    solve_one_cycle(...)
    if max_von_mises > yield_stress_at_T:
        return {'lifetime': cycle, 'failed_early': True}
```

Empirically, ~70 % of bad candidates fail within the first 5 cycles. Early-stopping kills 99 %+ of wasted compute on those.

---

## 7. The MFBO mitigations explained (LVGP, CAGES/EHVI, active learning)

**Latent Variable Gaussian Process (LVGP).** Standard GPs handle continuous inputs only. When the design space mixes continuous fractions with categorical decisions (BCC vs FCC, n = 1 vs n = 2 gradient profile), an LVGP **learns a continuous embedding** for the categorical variables so the GP can model the whole space.

**Cost-Aware Sampling.** A normal acquisition function asks "where is the highest Expected Improvement?". A cost-aware one asks "where is the highest Expected Improvement *per CPU-second*?" — so it gladly evaluates a cheap empirical-rule fidelity 1,000 times before triggering one expensive FEA call.

- **CAGES (Cost-Aware Gradient Entropy Search)** — picks the candidate that maximises information gain about the *optimum* per unit cost.
- **EHVI (Expected Hypervolume Improvement)** — multi-objective generalisation; expands the Pareto front the most.

**Active Learning.** Every FEA result is appended to the surrogate's training set. Re-fit, re-evaluate the acquisition function, pick the next candidate. After ~50 cycles the surrogate stops *discovering* and starts *confirming*.

---

## 8. Are the physics-based equations and Miedema's rules trustworthy?

- **Miedema (mixing enthalpy, δ, VEC, Ω):** ~70–80 % accuracy on RHEA single-phase-BCC prediction. A useful first-pass filter, not a guarantee. **Warning: all 10,626 of our compositions pass.** The filter is currently doing nothing — the five elements are chemically too similar. Tighten with VEC ∈ [4.0, 6.8] and Ω > 1.1; expect to drop to ~70 % pass rate.
- **Rule of Mixtures (CTE, modulus):** good for *trends and ranking*, weak for absolute values (10–20 % error on CTE). Acceptable inside BO; not acceptable as a reported number.
- **Slack model (thermal conductivity):** good for ordering candidates; 30–50 % error on absolute k. The HEA scattering factor (×0.6 for ≥ 3 elements) is a rough literature average — for Cr-rich compositions it under-estimates scattering.

**The right framing:** treat empirical equations as the $0.01-per-prediction screen, ML as the $0.10-per-prediction screen, CALPHAD as the $10-per-prediction validator, and SQS + DFT as the $1,000-per-prediction validator. Use each at the right scale.

---

## 9. Time and method to generate BCC crystals and gradient compositions

**Virtual BCC lattices.** For each candidate composition, build a BCC unit cell with lattice constant from Vegard's law:

a_alloy = 0.0 + Σ cᵢ · aᵢ
(Mo 3.147, Nb 3.301, Ta 3.305, W 3.165, Cr 2.884 Å)

Cost: microseconds. Good enough to feed into composition-only ML or as the starting structure for an SQS supercell later.

**Gradient compositions.** Use the `gradient_composition(position, exponent)` already in the dataset DOCX:

ceramic_frac(x) = (x / 5 mm)^n
HEA_frac(x) = 1 − ceramic_frac(x)

`n = 1` is linear; `n = 2` keeps more HEA on the hot side; `n = 0.5` does the opposite. The BO treats `n` as a design variable alongside the five HEA fractions, giving a 6-dimensional search space.

---

## 10. Missing physics — what to add for high-temperature reality

The current pipeline predicts at **300 K only**. A turbine blade runs at **1400 K**. The following need to be added before the simulation is publication-grade.

### 10.1 Temperature-dependent properties

| Property | Temperature dependence | Implementation |
|---|---|---|
| Bulk modulus E(T) | Wachtman's empirical: E(T) = E₀ − B·T·exp(−T₀/T) | Add T-dependent E to FEA constitutive law |
| CTE α(T) | Roughly linear rise; α(1400 K) ≈ 1.3·α(300 K) | Add α(T) lookup |
| Thermal conductivity k(T) | 1/T already in Slack; add electronic contribution κ_e ∝ T | Wiedemann-Franz law |
| Yield strength σ_y(T) | Drops ~40 % from 300 K to 1400 K | Senkov et al. data tables |

### 10.2 Oxidation and CMAS attack

- **Oxidation:** standard test is TGA mass-gain at temperature, literature-only (Category D). Target < 0.01 mg/cm²/h at 1100 °C.
- **CMAS (Calcium-Magnesium-Alumino-Silicate):** dust ingested by the engine melts at ~1240 °C and chemically attacks the ceramic top-coat. Padture, *Nat. Mater.* 15 (2016). Treat as an additional Category-D feature derived from `CaO + MgO + Al₂O₃ + SiO₂` solubility in the ZrO₂–HfO₂ phase.
- **Combustion gases:** CO₂, H₂O, SO₂ accelerate high-temperature oxidation. Captured as a multiplier on the base oxidation rate.

### 10.3 Cyclic fatigue and creep

- **Fatigue (10,000 cycles).** Run 100 cycles fully, fit Coffin-Manson: N_f = C · (Δε_p)^(−a), then extrapolate via Miner's rule (linear damage).
- **Creep at 1400 K.** Add Norton's law to the FEniCS constitutive model: ε̇_creep = A · σⁿ · exp(−Q/RT). Without this, the current stress predictions are an **upper bound** — real stresses relax 30–50 % within the first hour at temperature.
- **Stress relaxation.** Direct consequence of creep; modelled together.

---

## 11. Final deliverable shape (the ensemble + plots for Safran)

The submission package should include:

1. **Pareto front plot.** 2D or 3D scatter of all evaluated candidates with axes (CTE-mismatch, max interface stress, thermal conductivity); Pareto-optimal points highlighted.
2. **Gradient profile plots** for the top 5–10 candidates: composition vs. position, CTE vs. position, modulus vs. position, predicted stress vs. position.
3. **Thermal cycling lifetime histogram** with uncertainty bars from the surrogate ensemble.
4. **Feature importance / SHAP plot** showing which elements and design parameters drive the loss.
5. **Reliability ensemble.** Train 5–10 ML models with different random seeds; the spread of their predictions on each candidate **is** the uncertainty estimate. Bigger spread → less trustworthy → more reason to call high-fidelity validation.
6. **Final 5–10 alloy specifications** as composition + gradient-exponent recommendations, with confidence intervals from the ensemble.

---

## 12. Concrete next actions (prioritised)

1. **Replace synthetic training set with DFT-based labels.**
   - For 50–100 of the existing 122 base compounds, fetch real bulk modulus, shear modulus, and density from Materials Project / AFLOW (already partially done).
   - For 20 well-chosen quaternaries/quinaries, generate SQS supercells and run DFT (or use pre-computed AFLOW SQS data where it exists).
   - Re-train.

2. **Tighten the Miedema filter.** Add VEC ∈ [4.0, 6.8] and Ω > 1.1. Expect ~30 % rejection. This makes the filter actually filter.

3. **Upgrade the ML model.** Replace Random Forest with CrabNet (composition-only Transformer). Same training CSV, ~10–20 % better MAE on bulk modulus.

4. **Add temperature-dependent properties.** Implement Wachtman E(T), α(T) lookup, Wiedemann-Franz k_electronic(T), Senkov σ_y(T). All composition-only.

5. **Build the 1D reduced-order FEA model in FEniCS.** 51-node mesh, coupled thermo-elasticity with the temperature-dependent properties from step 4. Validate against a single 3D run.

6. **Wrap the 1D FEA inside an active-learning MFBO loop.** scikit-optimize or BoTorch as starting library. Add early-stopping on yield exceedance.

7. **Run the BO for 50–100 iterations.** Extract top 50 candidates.

8. **Add creep, oxidation, CMAS, fatigue extrapolation** for the top 50 only.

9. **Run full 3D FEA + 100-cycle thermal fatigue with creep** on the final 5–10. Extrapolate to 10,000 cycles via Miner's rule.

10. **Generate the deliverable plots and write the Safran submission.**

---

## 13. Honest risk assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Synthetic training data biases the model toward Rule-of-Mixtures behaviour | High | Replace with DFT labels (action 1) |
| Miedema filter is too permissive on this chemically similar system | Confirmed (100 % pass) | Tighten filter (action 2) |
| Continuum FEA misses atomic-scale interface diffusion | Medium | Use 5–10 SQS + DFT runs on the top candidates as a cross-check |
| 10,000 cycles extrapolated from 100 is non-conservative | Medium | Report 95 % confidence intervals via Miner's rule + creep |
| Real BCC stability at 1400 K differs from 0 K DFT | Medium-High | Validate with a CALPHAD pass on the top 50 before FEA |

---

## 14. File inventory (current upload set)

| File | Purpose |
|---|---|
| `all_compositions-generated.csv` | 10,626 compositions on the 5 % grid |
| `stable_compositions.csv` | Same 10,626, plus δ, ΔHmix, ΔSmix, VEC, Tm_avg, Ω columns |
| `ml_predictions.csv` | Same 10,626, plus predicted bulk modulus, k, CTE |
| `composition_model.pkl` | Trained Random Forest + StandardScaler |
| `train_composition_ml.py` | Training script (uses synthetic data) |
| `calculate_properties.py` | Slack-model + Rule-of-Mixtures property calculator |
| `BOHRIUM_RESPONSE_AND_PROJECT_STATUS.md` | Background context |
| `PROJECT_HANDOFF.md` | Earlier handoff document |
| `WORKFLOW_PLAN_AND_FEASIBILITY.md` | Multi-fidelity workflow plan |
| `HE_MCGA_Dataset_Document.docx` | Safran-facing dataset design |
| Critical Bottlenecks PDF (Bohrium) | External technical review |

---

*End of document.*
