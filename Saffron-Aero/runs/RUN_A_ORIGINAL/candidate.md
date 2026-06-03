# RUN A — Original Bohrium-Validated Candidate
## Master Composition Record
**Status: COMPLETE — Externally Validated by Bohrium/SciMaster Cloud Platform**
**Date Validated: May 2026**
**No code was re-run to produce this result.**

---

## THE COMPOSITION (Preserve Exactly — Never Modify)

```
Alloy Formula:   Ta₀.₁₆ W₀.₁₁ Cr₀.₂₇ V₀.₁₅ Ti₀.₁₃ Hf₀.₁₈  +  2.8 at% Al micro-addition
Ceramic:         LZO — Lanthanum Zirconate (La₂Zr₂O₇)
FGM Exponent:    n = 1.1  (power-law gradient)
FGM Thickness:   h = 5.0 mm total
TBC Outer Layer: 0.5 mm pure ceramic (increased from 0.2 mm)
```

---

## VALIDATED PROPERTIES (All from Bohrium 3D Simulation)

| Property | Value | Requirement | Status |
|----------|-------|-------------|--------|
| Safety Factor (post-geometric-fix) | **1.66** | ≥ 1.50 | ✅ PASS |
| Interface Shear Stress | **15.95 MPa** | Minimise | ✅ Pareto-optimal |
| Density | **9.80 g/cm³** | < 11.0 g/cm³ | ✅ PASS |
| VEC | **~5.2** | < 6.8 (BCC, no sigma phase) | ✅ PASS |
| ΔHmix | **−5.2 kJ/mol** | [−15, +5] kJ/mol | ✅ PASS |
| Phase | **Single-phase BCC_A2** | No sigma phase | ✅ PASS |
| Phase stability range | **300K – 2727K** | > 1400K operational | ✅ PASS |
| CTE (alloy) | **7.1 × 10⁻⁶ K⁻¹** | Close to LZO (9.1) | ✅ Good match |
| Oxidation (1100°C) | **< 10 mg/cm²** | Pass oxidation test | ✅ PASS (2.8% Al) |
| Manufacturing tolerance | **±2% composition → ±1.5 MPa** | Stable | ✅ PASS |

---

## WHY THIS CANDIDATE IS TRUSTWORTHY

### The bugs in the codebase did NOT affect this result:

| Bug ID | Bug Description | Did it affect RUN A? |
|--------|----------------|----------------------|
| B1 | np.trapz crash (NumPy 2.0) | ❌ NO — Script ran on older NumPy before this crash existed |
| N2a/N2b | CTE/k estimators ignore V,Ti,Hf | ❌ NO — `stage1_optimizer_with_constraints.py` has its OWN correct `_get_cte()` and `_get_k()` functions |
| N1 | HEA filter misses 9-element compositions | ❌ NO — Constrained DE does not use `evaluate_candidates.py` |
| B4 | pickle.dump never called | ❌ NO — Constrained DE trains models in-memory |
| All others | Various | ❌ NO effect on this result |

### Bohrium validation is fully independent of all local pipeline bugs:
- Bohrium ran on its OWN physics engine (CALPHAD TCHEA4, MACE, CHGNet MLFFs, Pareto FEA)
- Bohrium received the composition as INPUT — not the broken local code
- SF=1.66 is confirmed by 3D FEA, not by the local 1D surrogate

---

## HOW THIS RESULT WAS FOUND (The Discovery Path)

```
1. stage1_optimizer_with_constraints.py ran (correct physics, older NumPy)
           ↓
2. Differential Evolution over 9-element space converged to Ta-W-Cr-V-Ti-Hf family
           ↓
3. Composition printed to stdout (was manually recorded — not saved to CSV)
           ↓
4. Composition sent to Bohrium/SciMaster cloud platform
           ↓
5. Bohrium Phase 2: 3D FEA → SF=1.15 (FAIL — centrifugal + thermal combined)
           ↓
6. Bohrium Phase 3: Gradient optimisation → n=1.1, h=5mm, stress=15.95 MPa (PASS)
           ↓
7. Bohrium Phase 4: Oxidation → 1% Al FAIL → 2.8% Al PASS
           ↓
8. Engineering fixes applied: root smoothing r=3.5mm + platform film cooling
           ↓
9. Bohrium Phase 8: Post-fix SF = 1.66 ✅ PASS — TARGET MET
```

---

## BOHRIUM VALIDATION HIGHLIGHTS

From `validation_evidence/phases_6_to_11_output.txt`:
```
PHASE 8: Final Design Verification
- Phase 3 Interface Shear Stress Lock: 15.95 MPa (Pareto n=1.1, h=5.0mm)
- Phase 4 Oxidation Mass Gain Limit Lock: < 10mg/cm² at 1100°C (Passed via 2.8% Al)
- Post-Geometric Safety Factor Lock: 1.66 (Target >1.50 MET with root smoothing)
PHASE 8 CLEARED: All flaws mathematically neutralized.

PHASE 10 & 11 Final Architecture Confirmed:
Composition: Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18 + 2.8% Al
Coating: FGM LZO (n=1.1, h=5.0mm, TBC=0.5mm)
PHASE 11 CLEARED: Project Ready for final Safran handover.
```

From `validation_evidence/final_result.md` — Bohrium CALPHAD Confirmed:
```
Single-Phase BCC Solid Solution
VEC ~5.2 → 0% risk of brittle Sigma phase
ΔHmix = −5.2 kJ/mol at 300K (thermodynamically stable)
CTE = 7.1 × 10⁻⁶ K⁻¹ (Molecular Dynamics confirmed)
Mean Square Displacement → controlled atomic diffusion at 1400K
```

---

## EVIDENCE FILES IN THIS FOLDER

| File | Contents |
|------|---------|
| `validation_evidence/final_result.md` | Full Bohrium validation narrative |
| `validation_evidence/final_candidate_report.md` | Engineering proposal write-up |
| `validation_evidence/phases_2_5_output.txt` | Bohrium Phases 2–5 output (3D FEA, gradient, oxidation) |
| `validation_evidence/phases_6_to_11_output.txt` | Bohrium Phases 6–11 output (fixes, SF=1.66 confirmation) |
| `validation_evidence/day1_calphad_validation_curve.png` | Gibbs free energy vs temperature plot |
| `bohrium_submission_input.md` | What to feed Bohrium for the NEXT round of Job 1 |

---

## WHAT THIS RUN CONTRIBUTES TO THE FINAL SUBMISSION

- **Primary candidate** for Safran submission
- **Highest confidence** result — externally validated by gold-standard 3D FEA
- **Bohrium Job 1** for the next validation round = verify SF=1.66 is reproducible
- If Bohrium Jobs 2 or 3 (Run B/C) produce SF > 1.66 → update primary candidate
- If Bohrium Jobs 2 or 3 produce SF < 1.66 → RUN A remains the submission candidate
