# FLAWS — Critical Audit of v1 Model (Pre-Fix)

> Honest, prioritized assessment of the **v1 HE-MCGA pipeline output**, as flagged
> in the original Bohrium/SciMaster critique. This is the *before* state — every
> item in this document is addressed in `fixes.md`.

Audit pass date: Phase 0 (pre-rerun)
Reviewer source: independent Bohrium technical critique (`flaws.txt`)
Severity scale: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low

---

## TL;DR — Priority Stack

| # | Flaw | Severity | Failure mode if shipped | Phase fixed |
|---|------|----------|-------------------------|-------------|
| 1 | 80% Nb composition — not a true HEA | 🔴 Critical | Rejected by any Safran materials reviewer in <2 min | Phase 1 |
| 2 | Catastrophic oxidation of Nb at 1100°C | 🔴 Critical | Blade fails in minutes if LZO spalls | Phase 4, 9 |
| 3 | Safety factor 96.19 — unrealistic | 🔴 Critical | Missing centrifugal + gas-pressure loads → SF collapses | Phase 2, 6 |
| 4 | 5% Cr — insufficient for Cr₂O₃ scale | 🟠 High | No backup oxidation protection | Phase 4 |
| 5 | Density / cost / oxidation rate absent | 🟠 High | Safran reviewer cannot evaluate weight or manufacturability | Phase 5, 10 |
| 6 | 62,016 configurations — grid not Bayesian | 🟡 Medium | Acceptable for screening, not for final claim | Phase 3 |
| 7 | Thermal-conductivity reported at surface only | 🟡 Medium | Misleading single number; needs gradient profile | Phase 8 |

---

## 🔴 Flaw 1 — Composition is not a true HEA

**v1 output:** `Mo0.05 Nb0.80 Ta0.05 W0.05 Cr0.05`

This is a **Nb-rich refractory alloy with minor additions**, not a high-entropy
alloy. HEA classification requires *each principal element between 5–35 at%*.
Nb at 80% violates the definition outright.

The v1 optimizer correctly searched the energy landscape but had **no compositional
bounds**, so it collapsed into a Nb-dominated minimum (Nb has good CTE and ductility).
Any Safran materials expert would reject the "HEA" framing on the first page.

**Why this matters for the application:** the entire Challenge 2 ("Intelligence for
Materials") positioning relies on demonstrating that the platform discovers genuine
HEAs. Submitting a Nb-rich alloy labelled as HEA would damage credibility for the
whole proposal.

---

## 🔴 Flaw 2 — Catastrophic oxidation risk (Nb-dominated chemistry)

Nb oxidizes aggressively above 700°C in air, forming **Nb₂O₅** — a porous,
non-protective oxide. At 80% Nb the alloy will oxidize uncontrollably the moment
the LZO ceramic spalls or cracks. In real turbines, ceramic top-coats *do* spall.

Cr at 5% is far below the ~15% threshold required to form a continuous Cr₂O₃
backup scale. No Al was present in the v1 composition, so no α-Al₂O₃ self-healing
mechanism exists either. The blade has **zero independent oxidation defense**
if the ceramic fails.

**Missing test (v1):** isothermal oxidation at 1100°C for 100 h, target mass-gain
< 10 mg/cm²·h, benchmarked against equimolar MoNbTaWCr.

---

## 🔴 Flaw 3 — Safety factor 96.19 is not believable

A safety factor of **96** means yield strength is 96× the applied stress. For
aerospace turbine blades under combined thermal + centrifugal (15,000 RPM) +
gas-pressure loading, real SFs sit between **1.5 and 3.0**.

The v1 3D FEA only simulated **thermal stress from cooling**. It did *not* include:

- Centrifugal stress at 15,000 RPM
- Hot-gas pressure loading on the airfoil
- Combined-load superposition
- Blade-root stress concentration

Once those load cases are added, the apparent 96 collapses to a realistic single-
digit value — and *then* the question becomes whether the design still clears
SF > 1.5.

---

## 🟠 Flaw 4 — Cr content too low for backup oxidation protection

Standard refractory-alloy practice requires **≥ 15% Cr** to form a continuous,
adherent Cr₂O₃ scale. The v1 alloy carried only **5% Cr**, which produces a
discontinuous, non-protective oxide. Combined with Flaw 2, the alloy has **no
chemical line of defense** of any kind.

---

## 🟠 Flaw 5 — Missing engineering metrics

Four numbers that any Safran reviewer asks for on page one are absent from the
v1 result:

| Missing metric | Why Safran needs it |
|----------------|---------------------|
| Oxidation rate at 1100°C | Direct service-life indicator |
| Density of final alloy | Weight = fuel burn; constrained ≤ ~13.5 g/cm³ |
| Cost per kg | Ta, Hf, Nb are expensive — manufacturability check |
| Competing-composition benchmark | "Why not equimolar MoNbTaWCr?" — must be answered |

---

## 🟡 Flaw 6 — Search was a discretized grid, not full Bayesian optimization

The v1 run evaluated **62,016 configurations** over a 5-element grid. That is
acceptable as a *first-pass screening* but is too small and too coarse to be
called "Bayesian optimization" in the application. Honest framing: *combinatorial
screening, followed by gradient validation.*

---

## 🟡 Flaw 7 — Thermal-conductivity number is surface-only

The reported **1.5 W/m·K** corresponds to pure LZO at the topcoat surface — that
value is correct for LZO but **misleading on its own**. Safran will ask for the
effective thermal resistance across the full 5 mm gradient. The v1 report doesn't
provide the gradient-position profile.

---

## What was actually *correct* in v1 (do not throw away)

These items survived the audit unchanged and are reused in the post-fix model:

- **LZO ceramic choice** — correct, and superior to YSZ for CMAS resistance (forms an
  apatite barrier layer; experimentally verified in published literature).
- **Linear gradient n=1.0, h=5 mm** — valid starting point; later refined to n=1.1
  in the fixed model.
- **Interface stress ~12 MPa** — physically plausible for this gradient class.
- **CALPHAD TCP-phase screening** — correct methodology; reused as Phase 1 of the
  fixed pipeline.
- **R² = 0.958 on the yield-strength surrogate** — strong; carried forward into
  the fixed pipeline (now R² = 0.958 yield, R² = 0.977 bulk modulus).
- **LENS / gradient-deposition route** — correct manufacturing process choice.

---

## Action plan (input to fixes.md)

The three highest-priority actions, in order:

1. **Reconstrain the optimizer** — every element 0.05 ≤ x ≤ 0.35. Rerun.
2. **Force oxidation chemistry into the search space** — explicit Al content,
   minimum Cr; require Al ≥ 2% for α-Al₂O₃ self-healing.
3. **Rerun 3D FEA with combined loading** — thermal + centrifugal + gas pressure +
   blade-root geometry. Report SF ∈ [1.5, 3.0] only.

These three actions define `fixes.md`.
