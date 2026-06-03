# TEAM ONBOARDING — HE-MCGA Project
**Crystal Paradigm | Safran Explore Smart Materials 2026 | Challenge 2**
Last updated: May 2026

---

## SECTION 1 — What Was Wrong Before

When this round of work began, the repo was in a functional but deeply unreliable state. The pipeline had never run end to end. `models/top_50_candidates.csv` was empty — the core output of the entire project — and `models/top1_manufacturing_recipe.csv` showed `Mo0.05Nb0.80Ta0.05W0.05Cr0.05`, a composition where Nb=80%. That violates the HEA definition (every principal element must be 5–35%), meaning the "top candidate" on disk was physically invalid and would be immediately disqualified by any Safran materials expert.

The root causes were tangled. `scripts/run_1d_fea.py` called `np.trapz()`, which was removed in NumPy 2.0 — a hard crash that silently blocked all four scripts that import the FEA solver. The composition grid writer and the empirical filter both had path mismatches (writing to `scripts/` instead of `data/`, wrong filenames), so re-running them would write to the wrong place without warning. The ML model's CTE and thermal conductivity estimators treated Vanadium, Titanium, Zirconium, and Hafnium as zero — despite those four elements making up 61% of the Bohrium-validated best candidate. The `evaluate_candidates.py` script filtered for compositions where ALL FIVE of Mo, Nb, Ta, W, Cr are present, making the actual validated composition (`Ta-W-Cr-V-Ti-Hf`, which has Mo=0 and Nb=0) permanently invisible to the main pipeline. The ML model was also trained on synthetic Rule-of-Mixtures data and reported R²=0.97, but that measured internal self-consistency, not real-world predictive accuracy; 1,482 true-HEA rows in `ml_predictions.csv` had negative bulk modulus values (minimum: −1,920,044 GPa), which are physically absurd extrapolation artefacts.

On the documentation side, there were nine separate markdown files in different folders with contradictory claims. Some were planning documents written before any code existed. Some were Bohrium cloud validation results (real, but produced externally, not by this codebase). None of them agreed on what the pipeline actually did, what files it produced, or which paths were correct. A new developer had no reliable entry point and no way to distinguish confirmed facts from aspirational plans.

---

## SECTION 2 — What Was Done and Why

The decision was made to do documentation before code fixes. This is counterintuitive but critical: if you patch bugs without a verified map of what the code actually does, you will introduce new inconsistencies or miss interdependencies. The approach was four sessions of progressive verification.

**Session 0 — Ground truth extraction.** Every `.py` file was read line by line and every `.csv` was inspected. No prior documentation was trusted. The actual behaviour of each function, the exact path each file reads from and writes to, and the precise column names each downstream script expects were all derived directly from the source. This produced the verified file register (`MANIFEST_VERIFIED.md`) and pipeline order (`ARCHITECTURE_VERIFIED.md`), both of which contradicted prior docs in multiple places.

**Session 1 — Flaw cataloguing.** With a verified map in hand, every bug was identified with file name, line number, severity, and downstream impact. This session found 28 flaws — six of which were already partially known (B1–B6) and two that were previously undiscovered and critical: the HEA filter in `evaluate_candidates.py` that makes the Bohrium candidate invisible (N1), and the ghost-zero thermal property estimators that inflate safety factors for V/Ti/Hf compositions (N2). Documenting all 28 in one place (`FLAWS_REPORT_VERIFIED.md`) prevents the trap of fixing the obvious bugs while the subtle ones continue silently corrupting results.

**Session 2 — Fix planning.** The 28 flaws were translated into 15 specific surgical tasks (`TASK_LIST_VERIFIED.md`) and a dependency-ordered repair plan (`FIXES_PLAN_VERIFIED.md`). Tasks were ordered so that each fix unblocks the next group — FIX-1 (np.trapz) unblocks the entire FEA path; FIX-4 and FIX-5 make `evaluate_candidates.py` produce real output; FIX-6 and FIX-7 make the thermal physics correct. The minimum viable sequence to get a non-empty `top_50_candidates.csv` is five tasks, not twenty-eight.

**Session 3 — Copilot workflow engineering.** A complete guide was written for operating VS Code Copilot on this repo (`COPILOT_WORKFLOW_VERIFIED.md`, `COPILOT_CONTEXT_VERIFIED.md`, `TASK_LIST_VERIFIED.md`). The key design choice was a strict prompt template that shows a diff before applying, forbids renaming, limits each session to one task, and requires a terminal verify command before committing. This matters because Copilot with a large context will tend to "helpfully" refactor surrounding code, rename variables, or batch multiple changes — all of which introduce regressions in a codebase with tight cross-script dependencies. The template enforces surgical edits only.

---

## SECTION 3 — The Files We Generated (and what each one is for)

**`README_VERIFIED_v2.md`**
The corrected top-level README. It describes the actual repo structure (6 folders), the real tech stack, the actual pipeline steps with verified run commands, and a critical issues table with the 8 most important known problems. Open this when you need a high-level orientation to the project or want to know what a script is supposed to do.

**`MANIFEST_VERIFIED.md`**
A file-by-file register of every script, every CSV, and every utility file. For each script it lists: what it reads, what it writes, key functions and their exact behaviour, and known issues. Open this when you are about to edit a script and need to know its exact inputs, outputs, and dependencies — or when you want to know where a specific column comes from.

**`ARCHITECTURE_VERIFIED.md`**
The authoritative pipeline execution order. It shows the exact command to run each step, the data flow diagram connecting all files, the six confirmed bugs with line numbers (B1–B6), and the recommended fix order. Open this when you need to understand why a step is failing or you want to run the pipeline end to end.

**`FLAWS_REPORT_VERIFIED.md`**
All 28 confirmed flaws in the codebase, each with: file, line(s), severity (critical/high/medium/low), description, and pipeline impact. Open this when you are debugging unexpected behaviour, or before starting any non-trivial edit to make sure you are not working around a known flaw without fixing it.

**`FIXES_PLAN_VERIFIED.md`**
The 14 fixes in 10 ordered groups, each with the exact text to replace, the reason the fix matters, and a verify command. This is the implementation-facing companion to TASK_LIST. Open this when you want to understand *why* a fix is structured the way it is, or when you need to implement a fix outside of the Copilot workflow.

**`DATA_GUIDE_VERIFIED.md`**
Every CSV column in every file documented with: type, materials science meaning, data source (real DFT / synthetic / experimental / ML / generated), and quality issues. Open this when a model is producing unexpected values and you need to trace which CSV column a property came from, what its known accuracy limitations are, and whether it was real data or a placeholder.

**`COPILOT_CONTEXT_VERIFIED.md`**
A concise domain brief for the AI coding agent. Contains: what the project does, the physical constants that must never change, the key engineering variables and their thresholds, what Copilot must never modify, and what Copilot must always do. Pin this tab in VS Code and reference it at the start of every Copilot session with `#file:COPILOT_CONTEXT_VERIFIED.md`.

**`TASK_LIST_VERIFIED.md`**
15 tasks in strict order, each with: the exact file and line number, the exact text to replace, the exact text to replace it with, and the exact terminal command to verify success. This is the day-to-day execution guide. Work through it one task per session. Do not skip, batch, or reorder tasks.

**`HANDOFF_BRIEF_VERIFIED.md`**
A one-page summary for a new developer: what the project does, the current pipeline state in a table, what to read first, decisions that must not be undone (and why), and the Bohrium-validated composition preserved in text. Read this before anything else — it takes five minutes and prevents a week of wrong assumptions.

**`COPILOT_WORKFLOW_VERIFIED.md`**
The complete operating guide for VS Code Copilot: setup steps, the universal prompt template, the verification commands for each task, and a rejection script for when Copilot goes off-script (refactors, renames, batches). Open this in a separate window while working through TASK_LIST — it tells you what to type into Copilot Chat and what to do when it does something wrong.

---

## SECTION 4 — How to Start Working on This Repo Right Now

### Step 1: Read in this order (before touching any code)

1. `HANDOFF_BRIEF_VERIFIED.md` — five minutes, gives you the full picture
2. `ARCHITECTURE_VERIFIED.md` Part 1 (the Pre-Flight table) — understand what is broken
3. `TASK_LIST_VERIFIED.md` — read through all 15 tasks once before starting any
4. `COPILOT_WORKFLOW_VERIFIED.md` — read the full guide before your first Copilot session
5. `COPILOT_CONTEXT_VERIFIED.md` — have it open during every session

Do NOT read `docs/HE_MCGA_Master_Document.md` or `docs/PROJECT_HANDOFF.md` as ground truth. They describe what was planned, not what exists.

### Step 2: Set up VS Code with Copilot

1. Open the repo root as your workspace (not a subfolder).
2. Install the GitHub Copilot and GitHub Copilot Chat extensions if not already present.
3. Pin `COPILOT_CONTEXT_VERIFIED.md` (right-click tab → Pin) — it stays open across all sessions.
4. Open a terminal at repo root. All `python` commands in TASK_LIST run from here.
5. Verify your NumPy version: `pip show numpy | grep Version`. NumPy 2.0+ is required for the trapezoid fix to be meaningful (and is what caused the crash).
6. Confirm Python 3.10+: `python --version`.
7. Run `git status` — must show a clean working tree before you start any task.

### Step 3: Execute fixes using TASK_LIST and COPILOT_WORKFLOW

Work through `TASK_LIST_VERIFIED.md` one task per session. For each task:

1. Open the target file in VS Code alongside `COPILOT_CONTEXT_VERIFIED.md`.
2. Copy the Universal Prompt Template from `COPILOT_WORKFLOW_VERIFIED.md`.
3. Fill in the task details from `TASK_LIST_VERIFIED.md` and paste into Copilot Chat.
4. Review the diff Copilot shows you. If it edits more than the specified lines, reject it and reprompt with tighter instructions (the rejection scripts are in `COPILOT_WORKFLOW_VERIFIED.md`).
5. Apply the change.
6. Run the exact verify command from `TASK_LIST_VERIFIED.md`. Trust the terminal output, not Copilot's claim that it is correct.
7. If verify passes: `git add <file> && git commit -m "Fix TASK-N: <description>"`.
8. If verify fails: `git checkout <file>` and reprompt.

### Step 4: The minimum viable sequence to get the pipeline working

These five tasks in this exact order will get `top_50_candidates.csv` populated for the first time:

```
TASK-1  → scripts/run_1d_fea.py         np.trapz → np.trapezoid
TASK-6  → scripts/train_composition_ml.py   CTE estimator: add V,Ti,Zr,Hf
TASK-7  → scripts/train_composition_ml.py   Thermal conductivity: add V,Ti,Zr,Hf
TASK-4  → scripts/evaluate_candidates.py    Fix HEA filter (count-based, not 5-element AND)
TASK-5  → scripts/evaluate_candidates.py    Add negative bulk_modulus guard
TASK-5B → scripts/evaluate_candidates.py    SF threshold 1.45 → 1.50
```

Then run in order:
```bash
python scripts/train_composition_ml.py
python scripts/evaluate_candidates.py
python scripts/generate_manufacturing_recipe.py
```

Check that `models/top_50_candidates.csv` has rows and that `models/top1_manufacturing_recipe.csv` shows no element above 35%.

### Step 5: What NOT to touch and why

**`ELEMENT_DATA` dict in `scripts/train_composition_ml.py`** — these are literature physical constants (atomic radius, electronegativity, VEC, melting point, mass, bulk modulus). Every feature vector in the ML pipeline is built from this dict. Changing any value invalidates all existing predictions and makes results incomparable across runs.

**`ALL_ELEMENTS` list order** — defined as `['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']` in `train_composition_ml.py` and used in the same positional order by `differential_evolution_search.py`, `stage1_optimizer_with_constraints.py`, and `search_new_elements.py`. Reordering breaks every script that does `{el: fracs[i] for i, el in enumerate(ALL_ELEMENTS)}`.

**`solve_1d_thermoelastic_surrogate()` function signature in `run_1d_fea.py`** — called by four scripts. Changing parameter names or order requires updating all four callers simultaneously.

**`phase_wise_analysis/execute_phases_2_to_5.py` and `execute_phases_6_to_11.py`** — these are documentation artefacts, not simulations. The numbers in them (SF=1.15, stress=798 MPa, etc.) are from the external Bohrium cloud platform. Do not edit them — they preserve the external validation record.

**`active_learning_bo.py`** — dead scaffold. No script calls it. Fix it with TASK-13 only when you are ready to integrate the BO loop; do not touch it before then.

**`scripts/stage5_sustainability.py`** — requires `AlloySustainability`, a non-pip package. Leave it alone until that package is obtained separately.

---

## SECTION 5 — Current State Summary

| Step | Script | Status | TASK that fixes it |
|---|---|---|---|
| 1 — Data fetch | `scripts/fetch_datasets.py` | Runs. Returns 91 MP entries; JARVIS returns 0 rows. | No fix needed now |
| 2 — Property calc | `scripts/calculate_properties.py` | Runs. 54 rows survive (OQMD has no bulk_modulus). | No fix needed now |
| 3 — Composition grid | `scripts/generate_compositions.py` | Runs but writes to wrong path and filename. | TASK-2, TASK-14 |
| 4 — Empirical filter | `scripts/empirical_filter.py` | Reads from wrong path. Passes 100% anyway (known science limitation). | TASK-3 |
| 5 — ML training | `scripts/train_composition_ml.py` | Runs. R²=0.97 is self-consistency, not real accuracy. CTE/k wrong for V/Ti/Hf. Model never saved to disk. | TASK-6, TASK-7, TASK-8 |
| 6 — FEA scoring | `scripts/evaluate_candidates.py` | **CRASHES** on import (np.trapz removed). HEA filter misses Bohrium composition. SF threshold wrong (1.45 vs 1.50). | TASK-1, TASK-4, TASK-5, TASK-5B |
| 7 — Recipe generation | `scripts/generate_manufacturing_recipe.py` | **CRASHES** on empty CSV (IndexError). Output on disk is invalid (Nb=80%). | TASK-12 |
| 8 — Constrained DE (primary optimizer) | `scripts/stage1_optimizer_with_constraints.py` | **CRASHES** (imports run_1d_fea). This is the script that found the Bohrium candidate. | TASK-1 |
| 9 — Unconstrained DE | `scripts/differential_evolution_search.py` | **CRASHES** + no element cap (can produce Nb=80%). | TASK-1, TASK-10 |
| 10 — Random search | `scripts/search_new_elements.py` | **CRASHES** (imports run_1d_fea). | TASK-1 |
| 11 — Gibbs proxy validation | `phase_wise_analysis/phase1_calphad_phase_validation.py` | Runs. Produces plot. ΔHmix is hardcoded constant (not composition-dependent). | No fix in current task list |
| 12 — Full CALPHAD | `scripts/calphad_validation.py` | Blocked (no TCHEA4.TDB). Hardcoded to wrong composition. | TASK-9 |
| 13 — Gradient sensitivity | `scripts/stage2_gradient_optimization.py` | Runs but executes on import (no `__main__` guard). Hardcoded properties. | TASK-11 |
| 14 — Bohrium reporters | `phase_wise_analysis/execute_phases_*.py` | Runs. Hardcoded numbers only (not live simulation). Documentation artefacts — do not edit. | No fix needed |
| 15 — Sustainability | `scripts/stage5_sustainability.py` | **CRASHES** (missing non-pip package). | Not in current task list |
| 16 — BO scaffold | `scripts/active_learning_bo.py` | Dead code. Not connected to any script. | TASK-13 (low priority) |

---

## SECTION 6 — Who Did What

- Context engineering, documentation, flaw analysis, and fix planning: [Your Name]
- Original codebase design and implementation: [Friend's Name]
- External Bohrium cloud validation (SF=1.66, Bohrium platform): [Friend's Name]
- Proposed solution PDFs (Draft_saf.pdf, HEMCGA.pdf): [Chemistry Sir's Name]
- Verified on: May 2026

---

## Quick Reference: The Bohrium-Validated Best Candidate

This composition was found by `stage1_optimizer_with_constraints.py` and validated externally on the Bohrium / SciMaster cloud platform. It is **not in any CSV file** — it exists only in the docs below and must be manually fed into any validation script.

```
Composition:   Ta₀.₁₆ W₀.₁₁ Cr₀.₂₇ V₀.₁₅ Ti₀.₁₃ Hf₀.₁₈  +  2.8% Al micro-addition
Coating:       Lanthanum Zirconate (LZO) ceramic
Gradient:      FGM exponent n=1.1, thickness h=5mm, pure ceramic TBC outer layer 0.5mm
Safety Factor: 1.66  (after root smoothing r=3.5mm + film cooling at platform intake)
Phase:         Single-phase BCC_A2, 300K–2700K (CALPHAD confirmed)
VEC:           5.2  (no sigma phase risk)
Density:       9.80 g/cm³  (well below 11.0 g/cm³ aerospace limit)
Interface stress: 15.95 MPa at n=1.1, h=5mm (Pareto-optimal)
Oxidation:     2.8% Al enforces continuous α-Al₂O₃ protective scale at 1100°C
```

Preserved from: `docs/final_result.md`, `docs/final_candidate_report.md`, `phase_wise_analysis/phases_6_to_11_output.txt`.
