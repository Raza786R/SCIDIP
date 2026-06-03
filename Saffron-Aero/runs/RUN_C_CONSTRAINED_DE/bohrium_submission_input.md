# RUN C — Bohrium Submission Input (Job 3)
## What to Feed Bohrium for the Next Validation Round

This is the exact input to submit to Bohrium/SciMaster to validate
the new Candidate C (the winner of the Constrained Differential Evolution).

---

## COMPOSITION INPUT

```
Alloy:        Ta0.136 W0.141 Cr0.229 V0.140 Ti0.217 Zr0.046 Hf0.041 Al0.028 Nb0.014
Ceramic:      La2Zr2O7 (LZO — Lanthanum Zirconate)
Gradient:     Power-law FGM, exponent n=1.1, total thickness=5.0mm
TBC Layer:    Outer 0.5mm pure ceramic thermal barrier
```

---

## LOADING CONDITIONS (Match Prior Bohrium Run)

```
Thermal:      10,000 cycles, 300K cold end → 1400K hot end
Centrifugal:  15,000 RPM (turbine blade operational speed)
Gas Pressure: 2.5 MPa
Geometry:     Root smoothing radius r=3.5mm
Cooling:      Platform film cooling active at intake
```

---

## VALIDATION TARGETS

```
Primary:   Validate 3D Safety Factor (local 1D projected 1.76 post-fix, need > 1.50)
Secondary: Validate interface stress against Candidate A (C should be lower due to CTE 2.66 vs 2.83)
Tertiary:  Confirm single-phase BCC_A2 (no sigma phase, VEC is 5.02)
Quaternary: Confirm oxidation mass gain < 10 mg/cm² at 1100°C (via 2.8% Al + 22.9% Cr)
```

---

## EXPECTED DIFFERENCES VS CANDIDATE A (TO VERIFY)

```
Cost:          ~15-20% cheaper than Candidate A (High Ti, low Hf)
CTE Mismatch:  2.66 µm/mK (5.9% smaller than Candidate A)
Expected SF:   Should be higher than Candidate A's 1.66 due to better CTE match
```

---

## WHAT TO ASK BOHRIUM FOR

1. **Run full 11-phase analysis** under identical conditions to Candidate A (Job 1)
2. **Confirm SF > 1.50** 
3. **Verify Oxidation** - Does the high Cr (22.9%) + Al (2.8%) provide better oxidation resistance than A?

---

## SOURCE

This candidate was found by: `scripts/stage1_optimizer_with_constraints.py` (fixed version)
Evidence files: See `runs/RUN_C_CONSTRAINED_DE/` folder, specifically `candidate_C_phases_2_to_11_output.txt` and `manufacturing_recipe.csv`.
