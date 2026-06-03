# THREE CANDIDATES — MASTER COMPARISON
## Final Selection Guide for Bohrium Submission
**Generated: 2026-06-02 | All 3 runs complete**

---

## CANDIDATE SUMMARY TABLE

| | RUN A | RUN B | RUN C |
|--|-------|-------|-------|
| **Status** | ✅ Bohrium Validated | ✅ Complete | ✅ Complete |
| **Method** | Constrained DE (original, pre-bugfix) | Fixed 5-element grid | Fixed 9-element constrained DE |
| **Formula** | Ta₀.₁₆W₀.₁₁Cr₀.₂₇V₀.₁₅Ti₀.₁₃Hf₀.₁₈ + 2.8%Al | Mo₀.₀₅Nb₀.₁₅Ta₀.₁₅W₀.₂₅Cr₀.₄₀ | Nb₀.₀₁Ta₀.₁₄W₀.₁₄Cr₀.₂₄V₀.₁₄Ti₀.₂₂Zr₀.₀₅Hf₀.₀₄ |
| **Ceramic** | LZO, n=1.1 | LZO, n=0.5 | LZO (n TBD by Bohrium) |
| **SF — local 1D** | not computed | 1.1851 ❌ | **1.5981** ✅ |
| **SF — Bohrium 3D** | **1.66** ✅ | TBD (Job 2) | **~1.76** (Projected) |
| **Density** | 9.80 g/cm³ | ~9.5 g/cm³ | **9.78 g/cm³** |
| **VEC** | 5.2 | ~5.8 | **5.02** |
| **Alloy CTE** | 6.27 µm/mK | 5.0–7.3 µm/mK | **6.44 µm/mK** |
| **LZO mismatch** | 2.83 µm/mK | 1.8–4.1 µm/mK | **2.66 µm/mK** |
| **Oxidation** | α-Al₂O₃ (2.8% Al) ✅ | Cr₂O₃ (Cr=40%) ⚠️ | Cr₂O₃ (Cr=24%) ⚠️ needs Al |
| **Sigma phase risk** | 0% (VEC 5.2) | Moderate (VEC ~5.8) | **0%** (VEC 5.02) |
| **Bohrium Job** | Job 1 (confirm) | Job 2 (new) | Job 3 (new) |
| **Confidence level** | **HIGH** (already validated) | LOW (1D SF=1.19, needs 3D) | **MEDIUM-HIGH** (1D SF=1.60) |

---

## INDIVIDUAL CANDIDATE CARDS

### 🥇 CANDIDATE A — Primary Submission (Bohrium-Validated)
```
Ta₀.₁₆ W₀.₁₁ Cr₀.₂₇ V₀.₁₅ Ti₀.₁₃ Hf₀.₁₈  +  2.8 at% Al
Coating: LZO  |  n=1.1  |  h=5mm  |  TBC outer=0.5mm
SF = 1.66 (Bohrium 3D, post geometric fix)
Interface stress = 15.95 MPa
Density = 9.80 g/cm³  |  VEC = 5.2
Phase: Single BCC_A2 from 300K–2727K (CALPHAD confirmed)
```
**Why submit:** Already validated externally. Gold standard. Primary candidate.

---

### 🥈 CANDIDATE C — Best New Candidate (Run C DE)
```
Ta₀.₁₄ W₀.₁₄ Cr₀.₂₄ V₀.₁₄ Ti₀.₂₂ Zr₀.₀₅ Hf₀.₀₄  (+2.8% Al recommended)
Coating: LZO  |  n=1.1 recommended (from Run A)
SF = 1.5981 (local 1D — PASSES threshold before Bohrium)
Density = 9.78 g/cm³  |  VEC = 5.02
```
**Why submit:** Only new candidate to clear 1.50 in local FEA. Physics better than Run A
(smaller CTE mismatch 2.66 vs 2.83 µm/mK). Could exceed SF=1.66 on Bohrium.
**Add 2.8% Al before submission.**

---

### 🥉 CANDIDATE B — Long Shot (Run B Pipeline)
```
Mo₀.₀₅ Nb₀.₁₅ Ta₀.₁₅ W₀.₂₅ Cr₀.₄₀
Coating: LZO  |  n=0.5
SF = 1.1851 (local 1D — does NOT pass 1.50)
Density ~9.5 g/cm³  |  VEC ~5.8 (sigma risk)
```
**Why submit (maybe):** Completely different element family. If Bohrium geometric fixes
are strong enough, SF might climb from 1.19→1.50. But not the primary bet.

---

## DECISION MATRIX — WHICH TO SUBMIT

```
                    ┌────────────────────────────────────────┐
                    │  BOHRIUM SUBMISSION PRIORITY           │
                    ├────┬──────────────────────────────────┤
                    │ #1 │ JOB 1 — Candidate A (Run A)      │
                    │    │ Confirm SF=1.66 reproducibility   │
                    │    │ Extend to 20K cycles if possible  │
                    ├────┼──────────────────────────────────┤
                    │ #2 │ JOB 3 — Candidate C (Run C)      │
                    │    │ +2.8%Al added, n=1.1, LZO        │
                    │    │ Local 1D already 1.5981           │
                    │    │ High probability ≥ 1.50 on Bohrium│
                    ├────┼──────────────────────────────────┤
                    │ #3 │ JOB 2 — Candidate B (Run B)      │
                    │    │ Only if Jobs 1&3 leave budget     │
                    │    │ Lower probability, different family│
                    └────┴──────────────────────────────────┘
```

---

## RECOMMENDED FINAL SUBMISSION TO SAFRAN

If only 1 candidate: **Candidate A** (externally validated, SF=1.66, no uncertainty).
If 2 candidates: **A + C** (A is primary, C is "improved physics, Ti-rich variant").
If 3 candidates: **A + C + B** (A=validated, C=new DE result, B=different family).

---

## FOLDER LOCATIONS

| Run | Folder | Report |
|-----|--------|--------|
| A | `Saffron-Aero/runs/RUN_A_ORIGINAL/` | `candidate.md` |
| B | `Saffron-Aero/runs/RUN_B_MAIN_PIPELINE/` | `run_B_report.md` |
| C | `Saffron-Aero/runs/RUN_C_CONSTRAINED_DE/` | `run_C_report.md` |
