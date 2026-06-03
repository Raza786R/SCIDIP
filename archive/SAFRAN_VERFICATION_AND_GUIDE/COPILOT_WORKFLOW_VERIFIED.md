# COPILOT_WORKFLOW.md — How to Operate VS Code Copilot for This Repo

---

## 1. Setup — Before Every Session

**Always have these open in VS Code:**
- `COPILOT_CONTEXT.md` — pin this tab (right-click tab → Pin). Copilot reads it via #file: reference.
- `TASK_LIST.md` — keep open to know which task you're on.
- The specific file being fixed (e.g. `scripts/run_1d_fea.py` for TASK-1).
- A terminal pane at repo root (all commands run from there).

**Verify your environment first:**
```bash
python --version              # Confirm Python 3.10+
pip show numpy | grep Version # Confirm NumPy version (2.0+ requires trapezoid fix)
git status                    # Confirm clean working tree before starting
```

**Never start a task on a dirty git tree.** Commit or stash first so you can revert if Copilot goes off-script.

---

## 2. Universal Copilot Chat Prompt Template

Use this exact structure for every task. Copy it, fill in the task details, paste into Copilot Chat.

```
#file:COPILOT_CONTEXT.md #file:scripts/<file being fixed>

Fix [TASK-N] exactly as written below.

Rules:
- Edit ONLY the line(s) specified. Do not refactor anything else.
- Do not rename any variable, function, or class.
- Do not add any new imports unless the task explicitly requires it.
- Do not change any print statements or logging.
- Show me the complete unified diff (--- original, +++ modified) before applying.
- Wait for my approval before making any file change.

Task:
<paste the full [TASK-N] block from TASK_LIST.md here, verbatim>
```

**Example for TASK-1:**
```
#file:COPILOT_CONTEXT.md #file:scripts/run_1d_fea.py

Fix [TASK-1] exactly as written below.

Rules:
- Edit ONLY line 116. Do not refactor anything else.
- Do not rename any variable, function, or class.
- Do not add any new imports unless the task explicitly requires it.
- Do not change any print statements or logging.
- Show me the complete unified diff before applying.
- Wait for my approval before making any file change.

Task:
[TASK-1]
File: scripts/run_1d_fea.py
Line(s): 116
Action: Replace
    C = -np.trapz(sigma_free, x) / L_GRADIENT
with
    C = -np.trapezoid(sigma_free, x) / L_GRADIENT
Verify: Run python scripts/run_1d_fea.py from repo root. Confirm it prints
    "Predicted Max Interface Stress (Cooling): <some number> MPa"
    with no AttributeError.
```

---

## 3. Verification Steps After Each Task

Run these exact commands and check the expected outputs before moving on.

**After TASK-1 (np.trapz fix):**
```bash
python scripts/run_1d_fea.py
```
Expected: `Predicted Max Interface Stress (Cooling): <number between 50-500> MPa`
Fail signal: `AttributeError: module 'numpy' has no attribute 'trapz'`

**After TASK-2 (generate_compositions.py path fix):**
```bash
python scripts/generate_compositions.py
python -c "import pandas as pd; df=pd.read_csv('data/all_compositions-generated.csv'); print(len(df))"
```
Expected: `10626`
Fail signal: FileNotFoundError or wrong row count.

**After TASK-3 (empirical_filter.py path fix):**
```bash
python scripts/empirical_filter.py
python -c "import pandas as pd; df=pd.read_csv('data/stable_compositions.csv'); print(len(df), list(df.columns))"
```
Expected: `10626` and columns including `delta`, `Hmix`, `VEC`, `omega`.

**After TASK-4 (HEA filter fix) + TASK-5 (negative E guard) + TASK-6 + TASK-7 (thermal physics):**
```bash
python scripts/train_composition_ml.py
python scripts/evaluate_candidates.py
python -c "import pandas as pd; df=pd.read_csv('models/top_50_candidates.csv'); print(f'{len(df)} candidates found')"
```
Expected: At least 1 row. The number may be small due to tight SF threshold.
Fail signal: `0 candidates found` still (check if negative E guard is working).

**After TASK-6 (CTE fix) — spot check the Bohrium composition:**
```bash
python -c "
import sys; sys.path.insert(0, 'scripts')
from train_composition_ml import estimate_cte
import pandas as pd
row = pd.Series({'Mo_frac':0,'Nb_frac':0,'Ta_frac':0.16,'W_frac':0.11,
    'Cr_frac':0.27,'V_frac':0.15,'Ti_frac':0.13,'Hf_frac':0.18})
print(f'CTE = {estimate_cte(row):.3f} um/mK')
"
```
Expected: ~7.1 µm/mK (pre-fix was ~5.8, a 22% underestimate).

**After TASK-8 (pickle.dump fix):**
```bash
python scripts/train_composition_ml.py
ls -la models/composition_model.pkl
```
Expected: File exists with today's timestamp.

**After ALL tasks — full pipeline run:**
```bash
python scripts/generate_compositions.py
python scripts/empirical_filter.py
python scripts/train_composition_ml.py
python scripts/evaluate_candidates.py
python scripts/generate_manufacturing_recipe.py
```
Then check:
```bash
python -c "
import pandas as pd
recipe = pd.read_csv('models/top1_manufacturing_recipe.csv')
formula = recipe['Alloy_Formula'].iloc[0]
print(f'Top candidate formula: {formula}')
import re
fracs = {el: float(v) for el, v in re.findall(r'([A-Z][a-z]?)(\d+\.\d+)', formula)}
max_el = max(fracs, key=fracs.get)
print(f'Max element: {max_el} at {fracs[max_el]:.2f}')
assert fracs[max_el] <= 0.35, 'FAIL: element exceeds 35% HEA upper bound!'
print('PASS: All elements within HEA bounds.')
"
```

---

## 4. What To Do If Copilot Goes Off-Script

**If it edits more lines than specified:**
```
Reject the diff.
Reprompt: "Revert all changes. I only want to change line [N] of [file].
The only change is replacing [exact old text] with [exact new text]. Nothing else."
```

**If it rewrites a function instead of patching it:**
```
Reject. Say: "Do not rewrite the function. Surgical edit only.
Replace exactly this text: [old] with exactly this text: [new].
All other lines in the function stay identical."
```

**If it introduces a new import not required by the task:**
```
Reject. Say: "Remove the import you added. The task does not require any new imports."
```

**If it changes a variable name:**
```
Reject. Say: "You changed a variable name. Revert. Variable names must be preserved
exactly as they are. I did not ask you to rename anything."
```

**If it claims a task is already done / not needed:**
Always manually verify against the actual file. Copilot can hallucinate that a bug is
already fixed. Run the verify command from TASK_LIST.md. Trust the output, not the claim.

**If it produces a diff that looks correct but the verify step fails:**
```bash
git diff scripts/<file>    # See exactly what changed
git checkout scripts/<file>  # Revert if needed
```
Then reprompt with more specific line-level instructions.

---

## 5. Session Discipline

**One task per session. No exceptions.**

The workflow for each session:
1. Check `git status` — must be clean.
2. Open COPILOT_CONTEXT.md, TASK_LIST.md, and the target file.
3. Paste the prompt using the template above.
4. Review the diff carefully.
5. Approve and apply.
6. Run the verify command from TASK_LIST.md.
7. If verify passes: `git add <file> && git commit -m "Fix TASK-N: <one line description>"`
8. If verify fails: `git checkout <file>` and repeat from step 3 with tighter instructions.
9. Close the session. Start a new session for the next task.

**Never ask Copilot to do TASK-2 while verifying TASK-1.** Copilot maintains context
within a session — batching tasks causes it to lose track of which specific lines to
edit and produces over-broad changes.

**Commit message format:**
```
Fix TASK-N: <what was wrong> → <what was fixed>
Examples:
Fix TASK-1: np.trapz removed in NumPy 2.0 → np.trapezoid
Fix TASK-4: HEA filter required Mo/Nb > 0 → count-based 9-element filter
Fix TASK-6: CTE estimator ignored V/Ti/Zr/Hf → added all 9 elements
```

---

## 6. Quick Reference — Task to File Mapping

| Task | File | What It Fixes |
|---|---|---|
| TASK-1 | scripts/run_1d_fea.py | np.trapz → np.trapezoid (NumPy 2.0 crash) |
| TASK-2 | scripts/generate_compositions.py | Wrong output path and filename |
| TASK-3 | scripts/empirical_filter.py | Wrong input and output paths |
| TASK-4 | scripts/evaluate_candidates.py | HEA filter excludes 9-element compositions |
| TASK-5 | scripts/evaluate_candidates.py | No guard against negative bulk modulus |
| TASK-5B | scripts/evaluate_candidates.py | SF threshold 1.45 → 1.50 (Safran requirement) |
| TASK-6 | scripts/train_composition_ml.py | CTE estimator ignores V/Ti/Zr/Hf |
| TASK-7 | scripts/train_composition_ml.py | Thermal conductivity ignores V/Ti/Zr/Hf |
| TASK-8 | scripts/train_composition_ml.py | Model never saved (pickle.dump missing) |
| TASK-9 | scripts/calphad_validation.py | Hardcoded to wrong composition (Nb=80%) |
| TASK-10 | scripts/differential_evolution_search.py | No density/35% cap → Nb=80% trap |
| TASK-11 | scripts/stage2_gradient_optimization.py | No __main__ guard (runs on import) |
| TASK-12 | scripts/generate_manufacturing_recipe.py | Crashes on empty top_50 (no guard) |
| TASK-13 | scripts/active_learning_bo.py | np.vstack crash + return type inconsistency |
| TASK-14 | scripts/generate_compositions.py | is_true_hea missing 35% upper bound |
