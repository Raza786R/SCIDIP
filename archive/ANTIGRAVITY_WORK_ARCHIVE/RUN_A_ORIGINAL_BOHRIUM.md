# RUN A — Original Bohrium-Validated Candidate
## Architecture & Pipeline Document
**Status: COMPLETE — No code execution required**
**Independence: 100% — Does NOT depend on Run B or Run C**
**Deadline-safe: Can be done RIGHT NOW**

---

## What This Run Is

RUN A preserves and packages the composition that was:
1. Found by `stage1_optimizer_with_constraints.py` on a prior run (before NumPy upgrade broke it)
2. Independently validated by the **Bohrium/SciMaster cloud platform** using full 3D FEA
3. Confirmed with geometric fixes (root smoothing + film cooling)

This run requires **ZERO code execution**. The composition is fully validated and documented.
The job here is to assemble all existing evidence into one clean, standalone folder.

---

## Why This Candidate is Trustworthy Despite Pipeline Bugs

The bugs in the codebase did NOT affect this result because:

| Bug | Did it affect RUN A? | Reason |
|-----|---------------------|--------|
| B1 (np.trapz crash) | ❌ NO | Script ran on older NumPy before the crash was introduced |
| N2a/N2b (CTE/k wrong in train_composition_ml.py) | ❌ NO | `stage1_optimizer_with_constraints.py` has its OWN `_get_cte()` and `_get_k()` functions that already use the correct 9-element dict |
| N1 (HEA filter misses 9-element compositions) | ❌ NO | The constrained DE does not use `evaluate_candidates.py` at all |
| B4 (pickle.dump never called) | ❌ NO | Constrained DE trains models in-memory, never loads pkl |
| Bohrium 3D validation | ✅ FULLY INDEPENDENT | Runs on Bohrium's own physics engine, not local code |

**Conclusion: This result is scientifically valid and trustworthy.**

---

## The Validated Composition (Preserve Exactly)

```
Composition:     Ta₀.₁₆ W₀.₁₁ Cr₀.₂₇ V₀.₁₅ Ti₀.₁₃ Hf₀.₁₈  +  2.8 at% Al micro-addition
Ceramic:         LZO (Lanthanum Zirconate, La₂Zr₂O₇)
Gradient:        FGM power-law exponent n = 1.1
Thickness:       h = 5.0 mm total, TBC outer layer 0.5 mm pure ceramic
Safety Factor:   1.66 (post geometric-fix)
Phase:           Single-phase BCC_A2 confirmed 300K–2727K (CALPHAD)
VEC:             ~5.2 (no sigma phase risk)
ΔHmix:           −5.2 kJ/mol (thermodynamically stable)
Density:         9.80 g/cm³ (well below 11.0 g/cm³ aerospace limit)
Interface stress: 15.95 MPa at n=1.1, h=5mm (Pareto-optimal)
Oxidation:       2.8% Al → continuous α-Al₂O₃ protective scale at 1100°C
```

**Bohrium Validation Journey:**
- Phase 2 3D FEA: von Mises stress = 798 MPa, SF = 1.15 → FAIL (thermal + centrifugal combined)
- Phase 3 Gradient optimisation: optimal n=1.1, h=5mm, interface stress=15.95 MPa → PASS
- Phase 4 Oxidation: 1% Al → FAIL; 2.8% Al → PASS
- Phase 6 Geometric fix: root smoothing r=3.5mm + platform film cooling
- Phase 8 Post-fix: SF = **1.66** → PASS ✅

---

## Source Files (Already Exist — Just Copy/Reference)

| Source File | Contains |
|-------------|---------|
| `Saffron-Aero/docs/final_result.md` | Full narrative of Bohrium-validated result |
| `Saffron-Aero/docs/final_candidate_report.md` | Engineering proposal write-up |
| `Saffron-Aero/phase_wise_analysis/phases_2_5_output.txt` | Phases 2–5 Bohrium output |
| `Saffron-Aero/phase_wise_analysis/phases_6_to_11_output.txt` | Phases 6–11 Bohrium output (SF=1.66) |
| `Saffron-Aero/phase_wise_analysis/day1_calphad_validation_curve.png` | Gibbs proxy validation plot |
| `Saffron-Aero/docs/BOHRIUM_RESPONSE_AND_PROJECT_STATUS.md` | Bohrium platform response |

---

## Output Folder Structure

```
Saffron-Aero/
└── runs/
    └── RUN_A_ORIGINAL/
        ├── candidate.md                    ← Master composition record (write from above)
        ├── validation_evidence/
        │   ├── final_result.md             (copy from docs/)
        │   ├── final_candidate_report.md   (copy from docs/)
        │   ├── phases_2_5_output.txt       (copy from phase_wise_analysis/)
        │   ├── phases_6_to_11_output.txt   (copy from phase_wise_analysis/)
        │   └── calphad_validation_curve.png (copy from phase_wise_analysis/)
        └── bohrium_submission_input.md     ← What to feed Bohrium for Job 1
```

---

## Pipeline Steps (This Run)

```
Step 1: Create runs/RUN_A_ORIGINAL/ folder
Step 2: Write candidate.md (composition record above — exact text)
Step 3: Copy evidence files from docs/ and phase_wise_analysis/
Step 4: Write bohrium_submission_input.md
Step 5: DONE — no scripts to run
```

**Commands:**
```bash
# From Saffron-Aero/ root
mkdir -p runs\RUN_A_ORIGINAL\validation_evidence

copy docs\final_result.md runs\RUN_A_ORIGINAL\validation_evidence\
copy docs\final_candidate_report.md runs\RUN_A_ORIGINAL\validation_evidence\
copy phase_wise_analysis\phases_2_5_output.txt runs\RUN_A_ORIGINAL\validation_evidence\
copy phase_wise_analysis\phases_6_to_11_output.txt runs\RUN_A_ORIGINAL\validation_evidence\
copy phase_wise_analysis\day1_calphad_validation_curve.png runs\RUN_A_ORIGINAL\validation_evidence\
```

---

## Bohrium Submission Input (Job 1)

When submitting to Bohrium for the next round of validation:
```
Alloy:       Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18 Al0.028
Ceramic:     La2Zr2O7 (LZO)
Gradient:    Power-law n=1.1, thickness=5.0mm, TBC outer=0.5mm
Geometry:    Root smoothing radius r=3.5mm, platform film cooling active
Test:        10,000 thermal cycles 300K–1400K, 15,000 RPM centrifugal, 2.5 MPa gas pressure
Target:      SF ≥ 1.50 (confirm SF=1.66 result)
Prior SF:    1.66 (Bohrium Phase 8, May 2026)
```

---

## Dependencies on Other Runs

- **Does NOT depend on Run B** ✅
- **Does NOT depend on Run C** ✅
- **Does NOT require any bug fixes** ✅
- **Does NOT require any script execution** ✅

**This run can be completed in under 15 minutes RIGHT NOW.**
