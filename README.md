# SAFRAN CHALLENGE 2026 — Project Repository

This repository contains all working files, documents, scripts, and references for the Crystal Paradigm project — covering both the original Safran Explore challenge and the subsequent IIT Delhi SCIDIP (Sona Comstar — IIT Delhi Innovation Program) application.

---

## Repository Structure

### 📁 `IIT_DELHI_SCIDIP/`
All files related to the IIT Delhi SCIDIP 2026 program application.

Contains:
- Final pitch deck versions (`.pptx`) prepared for the SCIDIP presentation
- Technical appendix documents (`.docx`) submitted as part of the application
- Official application PDFs submitted to FITT IIT Delhi
- Founder briefing documents, formal proposal, and mentor briefing (`.docx`) generated during prep
- Python scripts used to generate, modify, and audit the pitch deck and technical appendix files
- Research and review markdown files about the SCIDIP program, project structure, and slide content
- Extracted text dumps and analysis files from PPTX/DOCX processing
- `logo.png` — Crystal Paradigm logo used in deck generation

---

### 📁 `Saffron-Aero/`
The main working codebase for the Safran Explore challenge.

Contains:
- `data/` — datasets used during the project
- `docs/` — documentation files
- `models/` — model-related files
- `phase_wise_analysis/` — analysis organized by project phases
- `runs/` — output files from pipeline runs
- `scripts/` — Python scripts for the computational pipeline
- `README.md` — detailed readme for this sub-project

---

### 📁 `archive/`
Historical working files, previous runs, and reference material no longer in active use.

Sub-folders:
- `Saffron-Aero_Archive/` — older pipeline runs, raw database files, previous candidate reports, markdown status files, and experimental data (includes the large HEA database CSV, Bohrium run logs, and project handoff notes)
- `ANTIGRAVITY_WORK_ARCHIVE/` — working files from AI-assisted sessions
- `Previous_Flaws_and_Fixes/` — notes and fixes from earlier iterations of the project
- `SAFRAN_VERFICATION_AND_GUIDE/` — verification guides and review notes

---

### 📁 `references_and_guides/`
Reference material, submission files, and onboarding documents.

Sub-folders:
- `FINAL_SUBMISSION_FILES/` — the actual files submitted for the Safran Explore challenge (pitch deck, technical appendix, and supporting documents)
- `Bohrium_Submissions/` — files related to Bohrium cloud compute submissions
- `Literature_and_References/` — research literature and reference documents
- `Project_Onboarding/` — onboarding material for new team members

---

### 📄 Root-level files
- `generate_final_docx.py` — script used to generate the final Safran Explore submission document
- `extract_slides.py`, `extract_text.py`, `read_pptx.py` — utility scripts for reading and extracting content from PPTX files
- `verify_docx.py` — script to verify docx output
- `pptx_extracted_new.txt`, `pptx_slides_detailed.txt`, `safran_pptx_content.md` — extracted text content from PPTX files for reference
- `README.md` — this file
- `.gitignore` — excludes Office temp lock files (`~$*.pptx`, `~$*.docx`), Python cache, and OS junk files

---

## Notes for New Team Members / Collaborators

- The **most relevant final files** for the IIT Delhi SCIDIP program are in `IIT_DELHI_SCIDIP/`
- The **original Safran Explore submission files** are in `references_and_guides/FINAL_SUBMISSION_FILES/`
- The **active Saffron-Aero codebase** is in `Saffron-Aero/` — this is also separately tracked at `github.com/indra2215/Saffron-Aero`
- Large files (>50MB) exist in `archive/` — GitHub may warn about these but they are pushed successfully

---

*Crystal Paradigm Private Limited | crystalparadigm.in | khub.crystalparadigm@gmail.com*
