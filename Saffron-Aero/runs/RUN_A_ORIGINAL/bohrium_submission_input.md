# RUN A — Bohrium Submission Input (Job 1)
## What to Feed Bohrium for the Next Validation Round

This is the exact input to submit to Bohrium/SciMaster to re-validate
or extend the analysis of the RUN A candidate.

---

## COMPOSITION INPUT

```
Alloy:        Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18 Al0.028
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
Primary:   Confirm Safety Factor ≥ 1.50 (prior result: SF=1.66)
Secondary: Confirm interface stress ≤ 15.95 MPa
Tertiary:  Confirm single-phase BCC_A2 (no sigma phase)
Quaternary: Confirm oxidation mass gain < 10 mg/cm² at 1100°C
```

---

## PRIOR BOHRIUM RESULTS (FOR REFERENCE)

```
Phase 2 FEA (without geometric fix): SF = 1.15 → FAIL
Phase 3 Gradient optimised:          Interface stress = 15.95 MPa, n=1.1, h=5mm
Phase 4 Oxidation:                   2.8% Al → PASS (< 10 mg/cm²)
Phase 8 Post-geometric-fix:          SF = 1.66 → PASS ✅
```

---

## WHAT TO ASK BOHRIUM FOR

1. **Confirm SF=1.66** under same loading conditions as prior run
2. **Extend to 20,000 cycles** if possible (demonstrate durability margin)
3. **Vary Al from 2.8% to 3.5%** — does it improve oxidation resistance further?
4. **Test at 1500K** hot end — does SF remain > 1.50 at elevated temperature?

---

## SOURCE

This candidate was found by: `scripts/stage1_optimizer_with_constraints.py`
Validated by: Bohrium/SciMaster cloud platform, May 2026
Evidence files: See `validation_evidence/` folder in this directory
