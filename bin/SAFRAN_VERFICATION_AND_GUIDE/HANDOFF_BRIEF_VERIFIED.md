# HANDOFF_BRIEF.md — First Thing Any New Developer Reads

---

## What This Is
An AI-driven computational pipeline that discovers the optimal Refractory High-Entropy Alloy
(RHEA) composition and ceramic gradient architecture for aerospace turbine blade coatings —
targeting the Safran Explore Smart Materials Challenge 2026. The final validated result is
Ta₀.₁₆W₀.₁₁Cr₀.₂₇V₀.₁₅Ti₀.₁₃Hf₀.₁₈ + 2.8% Al bonded to an LZO ceramic via a 5mm gradient
with Safety Factor 1.66, externally validated on the Bohrium cloud platform.

---

## Current Pipeline State

| Step | Script | Status |
|---|---|---|
| 1 — Data fetch | fetch_datasets.py | Runs. Returns 91 MP entries (JARVIS: 0 rows). |
| 2 — Property calc | calculate_properties.py | Runs. 54 rows survive (OQMD has no bulk_modulus). |
| 3 — Composition grid | generate_compositions.py | Runs but writes to wrong path. Fix TASK-2 first. |
| 4 — Empirical filter | empirical_filter.py | Reads from wrong path. Fix TASK-3. Passes 100% anyway. |
| 5 — ML training | train_composition_ml.py | Runs. R²=0.97 is self-consistency, not real accuracy. |
| 6 — FEA scoring | evaluate_candidates.py | CRASHES. np.trapz removed in NumPy 2.0 (TASK-1). |
| 7 — Recipe generation | generate_manufacturing_recipe.py | CRASHES on empty CSV (TASK-12 adds guard). |
| 8 — Constrained DE | stage1_optimizer_with_constraints.py | CRASHES (depends on run_1d_fea). Fix TASK-1. |
| Validation | phase1_calphad_phase_validation.py | Runs. Produces Gibbs proxy plot. |

**The validated Ta-W-Cr-V-Ti-Hf composition is NOT in any CSV file.** It came from
stage1_optimizer_with_constraints.py stdout, validated externally on Bohrium. That
external result is preserved in docs/final_result.md and docs/final_candidate_report.md.

---

## Read In This Order
1. **COPILOT_CONTEXT.md** — project domain, invariants, what never to touch
2. **TASK_LIST.md** — 15 ordered tasks to fix the pipeline, one per session
3. **ARCHITECTURE_VERIFIED.md** — exact pipeline execution order with bug line numbers
4. **FLAWS_REPORT_VERIFIED.md** — all 28 confirmed flaws with severity
5. **FIXES_PLAN_VERIFIED.md** — same fixes as TASK_LIST but with full rationale
6. **DATA_GUIDE_VERIFIED.md** — every CSV column explained with quality flags
7. **MANIFEST_VERIFIED.md** — every script's inputs, outputs, key functions

Do NOT treat docs/HE_MCGA_Master_Document.md or docs/PROJECT_HANDOFF.md as ground
truth. They are aspirational planning documents. The verified files above supersede them.

---

## Do Not Touch Yet
- **active_learning_bo.py** — scaffold only, not connected to anything. Fix last (TASK-13).
- **stage5_sustainability.py** — requires AlloySustainability package not on pip. Skip.
- **calphad_validation.py** — requires TCHEA4.TDB proprietary licence. Fix code (TASK-9) but do not expect it to run until TDB is obtained.
- **execute_phases_2_to_5.py and execute_phases_6_to_11.py** — hardcoded Bohrium reporter scripts. Do not edit. They are documentation artifacts, not live simulations.
- **The ELEMENT_DATA dict and ALL_ELEMENTS list** — these are the physical ground truth of the entire pipeline. Changing them invalidates every model and CSV.

---

## Key Decisions: Do Not Undo These

**Why SF threshold is 1.50 not 1.45:** Safran's stated requirement. The code uses 1.45 (a bug — TASK-5B). 1D FEA already overstates SF by ~30% (thermal load only, no centrifugal), so 1.50 is the minimum defensible number for a submission.

**Why 9-element space (not 5):** The original Mo-Nb-Ta-W-Cr proposal failed computationally — Mo+Nb combinations breach 11.0 g/cm³ density limit, and W+Cr+Mo > 40% risks brittle sigma phase. The constrained optimizer correctly dropped Mo and Nb and substituted Ti/Hf for density reduction. Reverting to 5-element would reintroduce these failures.

**Why surrogate FEA not full FEniCS:** FEniCS 3D simulations take hours each; the pipeline evaluates ~62,000 composition-ceramic-exponent combinations. The 1D surrogate runs in milliseconds. Full 3D FEA (Bohrium) is reserved for the final top 5-10 candidates. This is correct architecture — do not swap them.

**Why LZO not YSZ:** LZO reacts with CMAS (sand/ash ingested by engines at >1240°C) to form an apatite barrier layer, blocking the primary failure mode of current YSZ coatings. This is experimentally confirmed in published literature. YSZ would fail above 1200°C in CMAS-rich environments — current engines already exceed this.

**Why Ta-W-Cr-V-Ti-Hf and not equimolar MoNbTaWCr:** The optimizer found this family under realistic constraints. Bohrium confirmed it: VEC=5.2 (no sigma phase), mixing enthalpy=-5.2 kJ/mol (stable), SF=1.66 after geometric fixes. The equimolar 5-element system has density ~10.9 g/cm³ (borderline) and higher sigma risk.
