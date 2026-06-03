# 🧭 START HERE: The Ultimate Project Guidebook
**Welcome to the Antigravity AI & Safran Aerospace Challenge 2026 Repository.**

If you have just stepped into this project, this document is your compass. It will guide you exactly on what to read, in what order, to fully understand the technology, the physics, and the business application.

---

## 📖 Reading Order: How to Navigate This Project

Please follow this sequence to understand the project from end to end without getting overwhelmed.

### STEP 1: The High-Level Overview
**Goal:** Understand what we built and why it matters.
*   👉 **Read:** `Saffron-Aero/README.md`
*   *Why?* This is the executive summary. It explains the core challenge (turbine blade delamination), our AI inverse-design pipeline, and reveals the ultimate winner: **Candidate C** (SF = 1.71).

### STEP 2: The Core Physics & Architecture
**Goal:** Understand the deep science behind the alloy and the gradient.
*   👉 **Read:** `Saffron-Aero/docs/ARCHITECTURE_FINAL.md`
*   *Why?* This explains the 11-phase workflow, why we used Constrained Differential Evolution, and why we replaced Hafnium with Titanium and Aluminum. It explains the math behind the `n=1.1` power-law gradient that prevents cracking.

### STEP 3: The Validation Evidence
**Goal:** See the hardcore supercomputing proof.
*   👉 **Read/View:** `INFO FILES/Literature_and_References/Phase1_Computational_Validation_Report.pdf`
*   *Why?* This is the independent Bohrium/SciMaster validation report. Look at the 3D FEniCS FEA stress heatmaps and the MACE Molecular Dynamics oxidation graphs. This proves our AI's predictions are physically sound.

### STEP 4: The Manufacturing Handoff
**Goal:** Understand how to physically build this in the real world.
*   👉 **Read:** `Saffron-Aero/docs/PROJECT_HANDOFF_FINAL.md`
*   *Why?* This document transitions from digital to physical (TRL 4). It explains how Safran can use Laser Engineered Net Shaping (LENS) to 3D print the graded alloy-ceramic powder.

### STEP 5: The Business & Application Pitch (For the Safran Submission)
**Goal:** Understand how we are pitching this technology to Safran's Explore Smart Materials Challenge.
*   👉 **Read:** `INFO FILES/Project_Onboarding/SAFRAN_APPLICATION_AND_PITCH_GUIDE.md`
*   *Why?* This contains the exact copy-paste answers for the application portal, our startup's key differentiators, and a slide-by-slide blueprint for the technical Pitch Deck.

---

## 📂 Directory Structure Cheat Sheet

If you get lost, here is a quick map of the parent folder (`SAFRAN_CHALLENGE_2026/`):

*   📁 **`Saffron-Aero/`** — **The Active Codebase.** This is the main Git repository. It contains our AI Python scripts, the `README.md`, and the `runs/` folder with the actual execution logs for Candidate C.
*   📁 **`INFO FILES/`** — **The Reference Library.** This is where all massive PDFs, scientific papers, meeting transcripts, and onboarding guides live, keeping the main codebase lightweight.
*   📁 **`bin/`** — **The Archive Vault.** Nothing is ever permanently deleted. If a script crashed, an old candidate failed, or a markdown file became obsolete, it was moved here for historical reference. Ignore this folder unless you are doing forensics.

---
*Maintained by the Antigravity AI Engineering Team*
