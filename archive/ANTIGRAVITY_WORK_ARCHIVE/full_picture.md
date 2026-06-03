# SAFRAN_CHALLENGE_2026 — Full Ground-Truth Picture
*Derived from reading all verified files, scripts, and data. June 2026.*

---

## 1. What This Project Is

**Team:** Crystal Paradigm | **Challenge:** Safran Explore Smart Materials 2026, Challenge 2 | **Deadline: June 5, 2026**

**Goal:** Discover the optimal Refractory High-Entropy Alloy (RHEA) + Functionally Graded Material (FGM) ceramic coating that survives 10,000 thermal cycles (300K–1400K) with Safety Factor ≥ 1.50 under combined aerospace loading. Turbine blade application.

**Platform name:** HE-MCGA (High-Entropy Metal-Ceramic Gradient Architecture)

---

## 2. The Answer Already Exists (Externally Validated)

Found by `stage1_optimizer_with_constraints.py`, validated on Bohrium cloud. **NOT in any CSV file.**

```
Composition:   Ta₀.₁₆ W₀.₁₁ Cr₀.₂₇ V₀.₁₅ Ti₀.₁₃ Hf₀.₁₈  +  2.8% Al micro-addition
Coating:       LZO (Lanthanum Zirconate) ceramic
Gradient:      FGM exponent n=1.1, thickness h=5mm, pure ceramic TBC outer 0.5mm
Safety Factor: 1.66  (post geometric-fix: root smoothing r=3.5mm + film cooling)
Phase:         Single-phase BCC_A2, 300K–2727K (CALPHAD confirmed)
VEC:           5.2 (no sigma phase)
ΔHmix:         −5.2 kJ/mol (thermodynamically stable)
Density:       9.80 g/cm³ (below 11.0 g/cm³ aerospace limit)
Interface stress: 15.95 MPa at n=1.1, h=5mm
Oxidation:     2.8% Al enforces continuous α-Al₂O₃ protective scale at 1100°C
```

The problem: **the local codebase has NEVER reproduced this.** The pipeline has never produced valid output. `top_50_candidates.csv` is empty (header row only).

---

## 3. Directory Structure

```
SAFRAN_CHALLENGE_2026/
├── ANTIGRAVITY_STARTER (1).md       ← Starter context doc (not authoritative)
├── TEAM_ONBOARDING.md               ← Excellent onboarding doc — explains history
│
├── INFO FILES/                      ← READ ONLY reference material
│   ├── Draft_saf.pdf                Challenge 1 proposal PDF
│   ├── HE-MCGA.pdf                  Challenge 2 proposal PDF (PRIMARY)
│   ├── Safran Explore Smart Materials_Public.pdf
│   ├── screencapture-otter-ai-...pdf  Webinar transcript with Safran
│   ├── fixes.md                     (pre-audit fixes log, partially stale)
│   └── flaws.md                     (pre-audit flaws, superseded)
│
├── SAFRAN_VERFICATION_AND_GUIDE/    ← MOST IMPORTANT FOLDER — 11 verified files
│   ├── HANDOFF_BRIEF_VERIFIED.md    Quick orientation (read first)
│   ├── COPILOT_CONTEXT_VERIFIED.md  Domain brief + invariants (pin always)
│   ├── TASK_LIST_VERIFIED.md        15 ordered fix tasks with exact line numbers
│   ├── FIXES_PLAN_VERIFIED.md       Same fixes with rationale (WHY behind each)
│   ├── FLAWS_REPORT_VERIFIED.md     All 28 confirmed bugs (critical→low)
│   ├── ARCHITECTURE_VERIFIED.md     Exact pipeline steps + data flow diagram
│   ├── MANIFEST_VERIFIED.md         Every script: inputs, outputs, functions, bugs
│   ├── DATA_GUIDE_VERIFIED.md       Every CSV column explained
│   ├── README_VERIFIED_v2.md        Corrected top-level README
│   ├── COPILOT_WORKFLOW_VERIFIED.md Prompt template + rejection scripts
│   └── HE_MCGA_Context_Engineering_Report.pdf
│
└── Saffron-Aero/                    ← THE REPO — all work happens here
    ├── scripts/                     15 Python scripts
    ├── data/                        7 CSV files
    ├── models/                      4 model/output files
    ├── bin/                         Raw fetches + utility scripts
    ├── phase_wise_analysis/         Validation scripts + outputs
    └── docs/                        BACKGROUND ONLY — do not trust as ground truth
```

---

## 4. Current State of Every Script

| Step | Script | Real Status | Fix Tasks |
|------|---------|------------|-----------|
| 1 | `fetch_datasets.py` | ✅ Runs. 91 MP rows, JARVIS=0 | None needed now |
| 2 | `calculate_properties.py` | ✅ Runs. 54 rows (OQMD drops for no bulk_modulus) | None needed now |
| 3 | `generate_compositions.py` | ⚠️ Runs but writes to wrong path+name (`scripts/all_compositions.csv`) | TASK-2, TASK-14 |
| 4 | `empirical_filter.py` | 💥 FileNotFoundError (reads from `scripts/` not `data/`). Passes 100% anyway | TASK-3 |
| 5 | `train_composition_ml.py` | ⚠️ Runs. R²=0.97 is self-consistency only. CTE/k wrong for V/Ti/Hf. pickle.dump never called | TASK-6, TASK-7, TASK-8 |
| 6 | `evaluate_candidates.py` | 💥 CRASHES on np.trapz (NumPy 2.0). HEA filter misses Bohrium composition. SF threshold 1.45 vs 1.50 | TASK-1, TASK-4, TASK-5, TASK-5B |
| 7 | `generate_manufacturing_recipe.py` | 💥 IndexError on empty CSV. Output on disk is INVALID (Nb=80%) | TASK-12 |
| 8 | `stage1_optimizer_with_constraints.py` | 💥 CRASHES (imports run_1d_fea → np.trapz crash) | TASK-1 |
| 9 | `differential_evolution_search.py` | 💥 CRASHES + no constraints → Nb=80% risk | TASK-1, TASK-10 |
| 10 | `search_new_elements.py` | 💥 CRASHES (imports run_1d_fea) | TASK-1 |
| 11 | `phase1_calphad_phase_validation.py` | ✅ Runs. Gibbs proxy (ΔHmix hardcoded at −8500 J/mol) | No fix in task list |
| 12 | `calphad_validation.py` | ⛔ BLOCKED (no TCHEA4.TDB). Wrong composition hardcoded | TASK-9 |
| 13 | `stage2_gradient_optimization.py` | ⚠️ Runs but executes on import (no __main__ guard) | TASK-11 |
| 14 | `execute_phases_*.py` | ✅ Runs. Hardcoded Bohrium numbers — documentation only | Do NOT edit |
| 15 | `stage5_sustainability.py` | 💥 CRASHES (AlloySustainability not on pip) | Not in task list |
| 16 | `active_learning_bo.py` | Dead scaffold — never called by anything | TASK-13 (low priority) |

---

## 5. Critical Output State

| File | State |
|------|-------|
| `models/top_50_candidates.csv` | **EMPTY** — header row only |
| `models/top1_manufacturing_recipe.csv` | **INVALID** — shows Mo0.05Nb0.80Ta0.05W0.05Cr0.05 (Nb=80%) |
| `models/ml_predictions.csv` | 10,626 rows — 1,482 have negative bulk modulus (ML artefact) |
| `models/composition_model.pkl` | 365KB on disk — stale (from prior code; new training doesn't save it) |
| `data/all_compositions-generated.csv` | 10,626 rows — from manual move of a prior run |
| `data/stable_compositions.csv` | 10,626 rows — all pass Miedema filters (filter is non-discriminating) |

---

## 6. The 28 Bugs (Summary)

### Critical (Pipeline-blocking crashes)
| ID | File | Line | Issue |
|----|------|------|-------|
| B1 | `run_1d_fea.py` | 116 | `np.trapz` removed in NumPy 2.0 → hard crash, blocks 4 scripts |
| B2 | `empirical_filter.py` | 12–13 | Input/output paths resolve to `scripts/` not `data/` → FileNotFoundError |
| B3 | `generate_compositions.py` | 13 | Output writes to wrong dir + wrong filename vs what filter expects |
| N3 | `stage2_gradient_optimization.py` | 1-end | No `if __name__ == '__main__'` guard — executes on import |
| N1 | `evaluate_candidates.py` | 19 | HEA filter requires Mo+Nb+Ta+W+Cr all >0 → Bohrium composition (Mo=0, Nb=0) permanently invisible |

### High (Data corruption / wrong outputs)
| ID | Issue Summary |
|----|--------------|
| B4 | `train_composition_ml.py`: pickle.dump never called → model not saved |
| B5 | `evaluate_candidates.py`: no guard for negative bulk_modulus → nonsense FEA results |
| B6 | `calphad_validation.py`: hardcoded to Nb=80% stale composition |
| N2a | `estimate_cte()` treats V, Ti, Zr, Hf as zero (61% of Bohrium composition!) |
| N2b | `estimate_thermal_conductivity()` same — V/Ti/Zr/Hf silently contribute 0 |
| H1 | `differential_evolution_search.py`: no density/sigma/V constraints → Nb=80% prior result |
| H2-H4 | `run_1d_fea.py`: hardcoded creep (no grain_size), hardcoded SCF ×1.3, no centrifugal load |
| H5-H8 | Miedema filter passes 100%, R²=0.97 circular, dict coverage gaps, weight=10 anchor inactive |

### Medium/Low (8 medium, 4 low)
M1-M9: SF_MIN=1.45 (should be 1.50), active_learning_bo dead code, ΔHmix hardcoded, HEA upper-bound missing, LZO E inconsistency, CALPHAD comps list wrong, OQMD 5-element only, no row-count guard, SSL disabled.
L1-L3: AlloySustainability missing, LZO E inconsistency duplicate, weight=10 anchor inactive.

---

## 7. The Fix Plan — 15 Tasks in Order

### Minimum Viable Sequence (get top_50_candidates.csv non-empty)
```
TASK-1 → TASK-6 → TASK-7 → TASK-4 → TASK-5 → TASK-5B
```
Then: `python scripts/train_composition_ml.py` → `python scripts/evaluate_candidates.py`

| Task | File | One-Line Change |
|------|------|----------------|
| TASK-1 | `run_1d_fea.py:116` | `np.trapz` → `np.trapezoid` |
| TASK-2 | `generate_compositions.py:13` | Fix output path to `data/all_compositions-generated.csv` |
| TASK-3 | `empirical_filter.py:12–13` | Fix input+output paths to `data/` |
| TASK-4 | `evaluate_candidates.py:14–17` | Replace 5-element AND filter with count-based 9-element filter |
| TASK-5 | `evaluate_candidates.py:~42` | Add `if pd.isna(hea_E_Pa) or hea_E_Pa <= 0: continue` |
| TASK-5B | `evaluate_candidates.py` | `SF_MIN = 1.45` → `SF_MIN = 1.50` |
| TASK-6 | `train_composition_ml.py` | Add V(8.4), Ti(8.6), Zr(5.8), Hf(5.9) to `estimate_cte()` dict |
| TASK-7 | `train_composition_ml.py` | Add V(31), Ti(22), Zr(23), Hf(23) to `estimate_thermal_conductivity()` dict |
| TASK-8 | `train_composition_ml.py:37+main` | Fix MODEL_OUTPUT path; add `pickle.dump()` |
| TASK-9 | `calphad_validation.py:18–42` | Fix comps list + composition dict to Bohrium candidate |
| TASK-10 | `differential_evolution_search.py` | Add 35% element cap + density + sigma-former constraints |
| TASK-11 | `stage2_gradient_optimization.py` | Wrap all module-level code in `if __name__ == '__main__':` |
| TASK-12 | `generate_manufacturing_recipe.py` | Add `if len(df) == 0:` guard before `df.iloc[0]` |
| TASK-13 | `active_learning_bo.py` | Fix np.vstack crash + return type inconsistency |
| TASK-14 | `generate_compositions.py` | Add 35% upper bound to `is_true_hea` flag |

---

## 8. Invariants — NEVER Change These

```python
ALL_ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']  # ORDER IS SACRED
ELEMENT_DATA = { ... }  # Literature physical constants — never change values
solve_1d_thermoelastic_surrogate(hea_E, hea_alpha, hea_k, ...)  # Never change signature
CERAMIC_MATERIALS = { 'LZO': {'k': 1.6, 'alpha': 9.1e-6, 'E': 175e9}, ... }  # Never change
```
Never rename CSV columns. Never change ML return signatures. Never change print statements.

---

## 9. Files NOT To Trust
`docs/` folder entirely — aspirational planning docs, stale status notes, Bohrium narratives.
Also: `execute_phases_*.py` — hardcoded numbers from Bohrium, not live computation.

---

## 10. Key Design Decisions (Do Not Undo)
- **SF ≥ 1.50** not 1.45 — Safran's actual requirement
- **9-element space** not 5 — Mo+Nb push density over 11.0 g/cm³; W+Cr+Mo>40% risks sigma phase
- **LZO not YSZ** — LZO blocks CMAS (sand/ash ingestion above 1240°C) which YSZ cannot
- **1D surrogate FEA not FEniCS** — 62,016 evaluations need milliseconds each; 3D FEA for final 5-10 only
- **Ta-W-Cr-V-Ti-Hf family** — found under realistic constraints; Bohrium confirmed SF=1.66
