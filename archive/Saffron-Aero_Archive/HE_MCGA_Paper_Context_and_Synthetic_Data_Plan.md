# HE-MCGA Project — Paper-Context Handoff + Synthetic-Data Plan

**Companion to:** `HE_MCGA_Status_and_Next_Steps.md` (v1.0, May 22, 2026)
**Scope of this document:** What three newly-uploaded papers add to the project, and a concrete plan for replacing the synthetic training set.
**Date:** May 22, 2026 — Version 1.1

---

## 1. The three new papers, one paragraph each

**Paper A — Tsukamoto 2010**, *Comput. Mater. Sci.* 50, 429 (DOI 10.1016/j.commatsci.2010.08.035). Functionally graded thermal barrier coating (FG-TBC) of Ni + ZrO₂ analysed with a **mean-field micromechanical model**. Treats the gradient as spheres of one phase dispersed in a matrix of the other, with the volume fraction varying through thickness as `f_c(i) = ((i−1)/(P−1))^n`. The model goes beyond elasticity: it includes **plastic deformation** (Swift equation), **Coble grain-boundary creep** of *both* the metal and the ceramic, and **diffusional mass flow at the ceramic/metal interface**. Modified classical lamination theory propagates the micro-stresses up to plate-level forces and moments. Key numerical result for the Safran context: gradient exponent **n ≈ 0.5** minimises in-plane tensile stress for an unconstrained plate (Case 1); **n = 4** is best for a fully-constrained plate (Case 3). And the most actionable warning: **creep of the ceramic phase near the hot surface generates extremely large tensile stresses *during the cooling phase* — large enough to crack the ceramic**, and the magnitude is governed by the *grain size* of the ceramic (1 µm grain → 6 GPa tensile; 10 µm grain → manageable).

**Paper B — Mohammadzaki Goudarzi, Valefi & Zamani 2021**, *Ceram. Int.* 47, 34361 (DOI 10.1016/j.ceramint.2021.08.349). Direct **experimental** comparison of four plasma-sprayed thermal-barrier-coating architectures on Hastelloy X: (1) conventional TBC = 100 µm NiCrAlY + 280 µm YSZ, (2) thick TBC (TTBC) = 100 µm + 1000 µm YSZ, (3) FGTTBC-1 = 100 µm BC + 500 µm graded (25%/50%/75% YSZ in NiCrAlY) + 500 µm YSZ, (4) FGTTBC-2 = same graded stack + 1000 µm YSZ. Tests: bond strength (ASTM C633-01), isothermal oxidation at 1000 °C for 50–200 h, water-quench thermal shock from 1000 °C, and thermal-insulation capacity. **Bond strength** dropped from 35.6 MPa (conventional) to 15.9 MPa (TTBC) and was recovered to 26.2 MPa by adding the graded layers. **TGO grew parabolically** (2.79 µm for conv. TBC at 150 h, 2.11 µm for TTBC); the FG samples formed **no continuous TGO**, instead developing isolated Al₂O₃ "islands" around dispersed NiCrAlY splats. **Thermal-shock lifetime:** conventional 117 cycles, TTBC 50 cycles, FGTTBC-1 (same total thickness as TTBC) 104 cycles, FGTTBC-2 (1.6 mm) 70 cycles. **Thermal insulation:** ΔT = 42 °C (conventional), 82 °C (TTBC), 55 °C (FGTTBC-1), 101 °C (FGTTBC-2). The headline: a graded thick coating delivers about twice the insulation of a conventional coating *and* roughly the conventional coating's lifetime.

**Paper C — Song, Wang, Yao & Dong 2023**, *Coatings* 13, 343 (DOI 10.3390/coatings13020343). Review of TBC materials and microstructural design for high thermal insulation. Three things it nails down for us: (i) the **heat-transfer mechanism** in YSZ ceramics is overwhelmingly *phonon* up to ~1200 °C and gains a **radiative** contribution above that (≈10 % at 1250 °C, much more at 1500 °C). (ii) The **Slack model** (which our pipeline uses) misses both photon transfer and Knudsen gas conduction inside the pore network — both matter at 1400 K. (iii) A comparative table of candidate ceramic top-coat materials with **thermal conductivities and CTEs at 1000 °C**: standard YSZ ≈ 2.0 W/m·K and α ≈ 11 µm/m·K; **Gd₂Zr₂O₇** (GZO, pyrochlore) ≈ 1.5 W/m·K, α ≈ 11.6; **La₂Zr₂O₇** (LZO) ≈ 1.6, α ≈ 9.1; **SrZrO₃** ≈ 2.1, α ≈ 10.9; **LaTi₂Al₉O₁₉** ≈ 1.3, α ≈ 11.2; **LaMgAl₁₁O₁₉** ≈ 2.0, α ≈ 11.0. These are the candidate replacements for or top layers above the ZrO₂–HfO₂ in our system. The review also covers **segmentation-cracked TBCs** (2.7 mm⁻¹ crack density → >1770 cycles at 1238 °C) and **columnar SPS / EB-PVD** architectures with intracolumnar nanoporosity that gives lower-than-bulk thermal conductivity.

## 2. What each paper changes in our pipeline

### From Paper A (Tsukamoto micromechanics)

The current `WORKFLOW_PLAN_AND_FEASIBILITY.md` lists a vanilla FEniCS thermo-elastic solve with no creep and no plasticity. Tsukamoto shows three things that make that an over-simplification:

- **Creep is not negligible** at 1400 K — it *inverts* the stress state during cooling. The ceramic surface is compressive while hot, but if it has crept, it ends up in large tension when cool. Our pipeline currently looks only at peak-cycle stress, so it will systematically *miss this failure mode*.
- The **mean-field micromechanical formulation** (Eq. 2–7 in the paper) gives in-plane and out-of-plane stresses in each phase analytically once you know the bulk and shear moduli, the volume fractions, and the inelastic strain rates. This is faster than a full multi-phase FE mesh and is the natural surrogate for the BO loop.
- The **gradient exponent n is the key design knob** (already in our `gradient_composition` function) but Tsukamoto proves it interacts strongly with the *boundary condition*: the optimal n for a free plate (Case 1) is the worst n for a substrate-bonded plate (Case 3). The HE-MCGA blade is closer to Case 3, so the literature default of n ≈ 1 (linear) is probably wrong for us. **n = 2–4** is more likely.

**Action items into the next sprint:**
1. Add a Coble-creep term `ε̇_c = (C · ω_gb · D_gb · Ω / kT·d³) · σ_eq` to the FEniCS constitutive model for *both* phases. The pre-exponentials for Ni and ZrO₂ are tabulated in Tsukamoto's Table 1 — copy them as starting values, then substitute the RHEA values from Senkov / Frost-Ashby when available.
- 2. Run the BO over `n ∈ [0.25, 0.5, 1, 2, 4]` instead of treating it as continuous; this discretisation is what Tsukamoto used and it covers the relevant regime.
3. Track **maximum tensile stress at all stages of the cycle**, not just at peak temperature. The cooling-stage tensile peak is the failure-driving quantity.
4. Add **grain size of the ceramic** as a discrete design variable (1 µm vs 10 µm). Paper A is unambiguous that this matters more than most compositional choices.

### From Paper B (Goudarzi experimental data)

This is the closest experimental analogue we have to the HE-MCGA system. Three things we can use directly:

- **Quantitative ground truth** for a multi-layer FG architecture: bond strength 26 MPa, thermal shock 104 cycles, ΔT = 55 °C. These become *anchor points* the surrogate model must match within reasonable error. If the BO surrogate predicts a graded MoNbTaWCr/ZrO₂-HfO₂ stack at 200 MPa bond strength or 5000 thermal cycles, it is hallucinating.
- The **failure mechanism is independent of metallic composition**: graded coatings spall via *edge-initiated cracks at the BC/graded-layer interface* during cooling. The crack pattern in their Fig. 18 is the same pattern we should expect with NiCrAlY replaced by a RHEA. The implication: **our model must include a "free-edge stress" boundary condition** (high tensile peeling stress where the coating ends). This is a known FE pathology and is exactly the situation Sundaram et al. modelled.
- **Bond strength is a separate ML target** that we currently don't predict at all. Paper B suggests it correlates with the **number of graded layers** (more layers → higher bond strength, up to a point). For our 6-D BO we should include `n_graded_layers ∈ {1, 3, 5, 7}` as a discrete design variable.

**Action items:**
5. Add `bond_strength` as a new prediction target in our ML stack. Training data: extract from the figures in Paper B and the references it cites (Khor 2000, Khoddami 2007).
6. Add **edge-effect FE boundary conditions** to the reduced-order model. Even a 1D model can include the edge by computing the radial integral of the peeling stress.
7. Use the four Goudarzi data points as **validation anchors**: any candidate that predicts better than 26 MPa bond strength *and* longer than 117 cycles *and* lower than 1.0 W/m·K thermal conductivity should be flagged as suspicious until verified.

### From Paper C (Song review)

The big conclusion: **our choice of ZrO₂–HfO₂ as the ceramic top-coat may not be optimal**. The review's table makes it clear that:

- **Gd₂Zr₂O₇ (GZO) and La₂Zr₂O₇ (LZO)** have ~25–30 % lower thermal conductivity than YSZ, with CTEs in the same 9–12 µm/m·K range. They are the standard "second-generation" TBC replacement materials.
- **Rare-earth tantalates (YTaO₄ etc.)** are ferroelastic and toughen via domain switching — promising but immature.
- The **dual-ceramic-layer (DCL) architecture** — a thin layer of advanced material (LZO, GZO) on top of YSZ — is the practical compromise: lower thermal conductivity, better CMAS resistance, no bond-strength penalty. Cheng et al. (refs 217/218 in the review) showed 67 µm LZO + 100 µm YSZ has the same insulation as a thick YSZ alone.
- The **radiative heat-transfer contribution above 1200 °C** is *not in our Slack model*. At our 1400 K target it contributes maybe 5–10 % of total thermal conductivity for YSZ; for thinner, more porous structures it is larger.
- **Sintering at temperature** is a separate degradation mechanism we have not modelled. The 2D inter-splat pores heal over the first 5 hours at 1300 °C, raising thermal conductivity by up to 80 %.

**Action items:**
8. **Extend the ceramic material space** beyond ZrO₂–HfO₂ to include GZO, LZO, SrZrO₃, and LaTi₂Al₉O₁₉ as candidate top-coat materials. Add a categorical design variable `ceramic_material ∈ {ZrO₂-HfO₂, GZO, LZO, SrZrO₃}`.
9. Add a **photon/radiation conductivity term** `κ_r = (16/3)·σ·n²·T³·l_r` to the thermal-conductivity prediction. This is the Rosseland diffusion approximation; values of `n` (refractive index ≈ 2.2) and `l_r` (photon mean-free path ≈ 30 µm) are in the review.
10. Add a **sintering correction** that increases k by 40–80 % over 0–100 h at temperature, with the time constant governed by the porosity and the homologous temperature `T/T_m`. Use Li et al. (ref 23 in the review) for the two-stage kinetic form.

## 3. Concrete plan for replacing the synthetic training set

The prior handoff flagged that `composition_model.pkl` is trained on synthetic data and that "R² = 0.97 is internal consistency, not real-world accuracy". Here is a concrete five-track plan to replace that synthetic training set, ordered by cost-effectiveness.

### Track A — Harvest the real DFT data that already exists (highest priority, lowest cost)

The 122 base compounds in `combined_raw_data.csv` already include some real bulk moduli from Materials Project — the script just fills missing values with placeholder 150 GPa. Re-run the data pipeline keeping only the entries with *real* DFT-derived `bulk_modulus`, `shear_modulus`, `density`, `volume`. Expected yield: 40–60 compounds with real labels.

Then expand to the *full* set of binary and ternary entries in MP/AFLOW/OQMD/JARVIS covering any pair drawn from {Mo, Nb, Ta, W, Cr}. Expected total: 200–400 entries with real bulk modulus.

This alone replaces ~90 % of the synthetic anchors.

```python
# Pseudo-code to inject into train_composition_ml.py
df_real = df_train[df_train['bulk_modulus_source'] == 'database_calculated']
df_real = df_real.dropna(subset=['bulk_modulus', 'shear_modulus', 'density'])
# Use only these rows; do NOT fall back to synthetic Rule-of-Mixtures.
```

### Track B — Targeted SQS + DFT for the 5-element regime (medium priority, medium cost)

Public databases mostly contain ordered binaries/ternaries. To anchor the 4- and 5-element predictions we need **at least 10 SQS+DFT data points** in the quinary regime. The right strategy:

- Use the **ATAT toolkit** (Wei & Zunger's SQS generator) to build 32-atom BCC SQS supercells at ~10 equimolar or near-equimolar compositions: Mo₀.₂Nb₀.₂Ta₀.₂W₀.₂Cr₀.₂ (equimolar centre) plus 9 perturbations of ±0.05 around the centre. These are the points that most reduce predictive variance.
- Run with VASP-PBE or QuantumESPRESSO-PBE, GGA pseudopotentials, k-point density ~30 Å, EDIFF 10⁻⁵, ENCUT 400 eV. Each one is ~200–500 core-hours.
- 10 quinary SQS calculations ≈ 5,000 core-hours total. On a 64-core box that's ~3 days wall-clock per calc, ~30 days for the batch — manageable.
- Use the results to validate (not train) the ML model first; if predictions match within 10 %, retrain by including them.

### Track C — Augment with EFTGAN-style transfer learning (medium priority, low compute)

Published February 2025 in *npj Computational Materials*: **EFTGAN** is a GAN-based augmentation pipeline designed for HEA small-data regimes. The architecture: take all available binary/ternary DFT data for the 5 elements (Track A's ~300 points), train a generator to produce plausible 4- and 5-element compositions with correlated properties, and use a Wasserstein discriminator to keep the synthetic points statistically aligned with the real data. The authors apply it to FeNiCoCrMn/Pd; the same code transfers to our system by re-targeting the elements.

This is much better than what we currently do: synthetic data informed by *real chemistry* rather than by Rule of Mixtures.

Repository: https://github.com/idrl-lab/EFTGAN (referenced by the npj Comp Mater paper).

### Track D — Composition-only foundation model with fine-tuning (high priority, low effort)

The Sci. Rep. 2025 paper "High entropy alloy property predictions using a transformer-based language model" (DOI 10.1038/s41598-025-95170-z) found that **pre-training on the full Materials Project (≈228,000 compounds) and fine-tuning on the small HEA set** gave consistently better MAE than training from scratch on the small set alone. This is the principle Feng et al. used to get 93–94 % phase classification accuracy across two HEA datasets.

In practical terms:
- Pre-train **CrabNet** (or use the published pre-trained weights) on the full MP bulk-modulus dataset (~10,000 entries).
- Fine-tune for 100 epochs on our 300-or-so real RHEA data points.
- This will plausibly halve the MAE relative to our current Random Forest.

Repository: https://github.com/sparks-baird/CrabNet — pip-installable, well-documented, accepts the same `(formula, target)` CSV format our pipeline already produces.

### Track E — Active-learning closing of the loop (medium priority, high payoff)

Yan et al. (*Acta Mater.* 2024, NbTaZrHfMo system) used an **uncertainty-based Expected-Improvement acquisition with clustering** to design four RHEAs in NbTaZrHfMo that were experimentally validated to combine high-T strength with room-T ductility. Their dataset before active learning was about 80 alloys; after 4 iterations of "predict → make → measure → retrain" it was 80 + 4·(5–8) = ~110 alloys, and the model went from R² ≈ 0.7 to R² ≈ 0.85 on the held-out set.

The same workflow applies directly here:
- After Track A/D give us a starting model on 200–400 real data points, run the BO loop.
- Pick the top 5–10 most uncertain *and* most promising candidates per iteration.
- For each, either (a) run SQS+DFT (Track B) or (b) commission a small physical synthesis at a collaborating lab.
- Retrain. Repeat 5–10 times.

This is the same closed loop the Bohrium report recommended; the difference is the 2024 Acta Mater paper proves it works on an alloy system one step away from ours.

## 4. Updated roadmap (delta vs the v1.0 handoff)

| Item | v1.0 plan | Revised plan (this document) |
|---|---|---|
| ML training data | Synthetic (Rule of Mixtures + 5 anchors) | Track A real DFT (200–400 points) + Track C EFTGAN augmentation |
| ML architecture | Random Forest | CrabNet (pre-trained on MP, fine-tuned on Track A) |
| FEA constitutive law | Linear thermo-elasticity | Linear elasticity + Coble creep (both phases) + Swift plasticity |
| Gradient design variables | 5 fractions + n exponent (6-D) | + ceramic_material (categorical) + n_graded_layers (discrete) + ceramic_grain_size (discrete) (10-D) |
| Stress metric | Peak von Mises during heating | Maximum tensile stress at ANY point in the cycle (especially cooling) |
| Ceramic top-coat | ZrO₂–HfO₂ only | {ZrO₂–HfO₂, GZO, LZO, SrZrO₃} |
| Thermal conductivity model | Slack only | Slack + radiative κ_r + sintering correction κ(t,T) |
| Edge effect | Not modelled | Free-edge boundary condition added to 1D ROM |
| Validation anchors | None | 4 Goudarzi data points (bond strength, lifetime, ΔT, oxidation) |

## 5. New references to add to the project bibliography

- Tsukamoto, *Comput. Mater. Sci.* 50, 429 (2010). DOI 10.1016/j.commatsci.2010.08.035
- Mohammadzaki Goudarzi, Valefi, Zamani, *Ceram. Int.* 47, 34361 (2021). DOI 10.1016/j.ceramint.2021.08.349
- Song, Wang, Yao, Dong, *Coatings* 13, 343 (2023). DOI 10.3390/coatings13020343
- Yan, Lu & Wang, *Acta Mater.* (2024) — active-learning RHEA discovery in NbTaZrHfMo.
- Yang et al., "EFTGAN", *npj Comput. Mater.* 11, … (2025). DOI 10.1038/s41524-025-01548-y
- Sci. Rep. 2025, "HEA property predictions using a transformer-based language model" DOI 10.1038/s41598-025-95170-z
- Wang et al., "CrabNet", *npj Comput. Mater.* 7, 77 (2021). DOI 10.1038/s41524-021-00545-1
- Padture, *Nat. Mater.* 15, 804 (2016) — CMAS attack on TBCs (already in v1.0).
- Cheng et al. — LZO/YSZ dual-ceramic-layer TBC (refs 217/218 of Song et al. 2023).

---

*End of v1.1 addendum. The v1.0 status-and-next-steps document remains the project's master handoff; this file is its supplement covering the three new papers and the synthetic-data remediation plan.*
