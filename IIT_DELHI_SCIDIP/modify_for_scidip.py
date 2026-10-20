# -*- coding: utf-8 -*-
"""
Modify Crystal Paradigm Safran Submission Files for IIT Delhi SCIDIP Application.
- Targeted text replacements ONLY (no formatting/layout changes)
- Preserves all logos, colors, fonts, backgrounds, images
- IP-protected: no exact compositions revealed
"""
import sys

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
except ImportError:
    print("Installing python-pptx...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx", "-q"])
    from pptx import Presentation
    from pptx.util import Inches, Pt

try:
    from docx import Document
except ImportError:
    print("Installing python-docx...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "-q"])
    from docx import Document

import os
import re
import copy

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
PPTX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_PitchDeck.pptx")
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.docx")

# =====================================================
# HELPER: Safe text replacement in PPTX runs
# Preserves formatting by replacing within each run
# =====================================================
def replace_in_runs(shape, old_text, new_text):
    """Replace text across runs in a shape's text frame, preserving formatting."""
    if not shape.has_text_frame:
        return 0
    count = 0
    for paragraph in shape.text_frame.paragraphs:
        # First try: simple run-by-run replacement
        for run in paragraph.runs:
            if old_text in run.text:
                run.text = run.text.replace(old_text, new_text)
                count += 1
        # Second try: if old_text spans multiple runs, check full paragraph text
        full_text = paragraph.text
        if old_text in full_text and count == 0:
            # Rebuild: put all text in first run, clear others
            new_full = full_text.replace(old_text, new_text)
            if paragraph.runs:
                paragraph.runs[0].text = new_full
                for run in paragraph.runs[1:]:
                    run.text = ""
                count += 1
    return count

def replace_in_table(shape, old_text, new_text):
    """Replace text in table cells."""
    if not shape.has_table:
        return 0
    count = 0
    for row in shape.table.rows:
        for cell in row.cells:
            if old_text in cell.text:
                for paragraph in cell.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if old_text in run.text:
                            run.text = run.text.replace(old_text, new_text)
                            count += 1
    return count

def pptx_replace(prs, old_text, new_text):
    """Global find-and-replace across all slides."""
    total = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            total += replace_in_runs(shape, old_text, new_text)
            total += replace_in_table(shape, old_text, new_text)
            # Handle grouped shapes
            if shape.shape_type == 6:  # MSO_SHAPE_TYPE.GROUP
                try:
                    for s in shape.shapes:
                        total += replace_in_runs(s, old_text, new_text)
                        total += replace_in_table(s, old_text, new_text)
                except:
                    pass
    return total

# =====================================================
# PPTX MODIFICATIONS
# =====================================================
print("=" * 60)
print("PHASE 1: MODIFYING PPTX FOR IIT DELHI SCIDIP")
print("=" * 60)

prs = Presentation(PPTX_PATH)

# Track all replacements
replacements_log = []

def do_replace(old, new, desc):
    count = pptx_replace(prs, old, new)
    replacements_log.append(f"  [{count} hits] {desc}")
    return count

# --- SLIDE 1 (Intro) ---
do_replace(
    "This program takes that platform to its hardest proving ground",
    "Our platform has been proven on one of the hardest challenges in engineering",
    "Slide 1: Remove 'program' framing"
)

# --- SLIDE 3 (Why This Matters) ---
do_replace(
    "WHY THIS MATTERS TO SAFRAN NOW",
    "WHY THIS MATTERS NOW",
    "Slide 3: Remove Safran from title"
)
do_replace(
    "Directly aligned with Safran\u2019s RISE open-rotor program targets for TET > 1400\u00b0C and 20% SFC improvement.",
    "Directly aligned with next-generation open-rotor program targets for TET > 1400\u00b0C and 20% SFC improvement.",
    "Slide 3: Remove Safran RISE reference"
)
do_replace(
    "Directly aligned with Safran's RISE open-rotor program targets for TET > 1400\u00b0C and 20% SFC improvement.",
    "Directly aligned with next-generation open-rotor program targets for TET > 1400\u00b0C and 20% SFC improvement.",
    "Slide 3: Remove Safran RISE reference (alt apostrophe)"
)
do_replace("Safran's RISE", "next-generation", "Slide 3: Safran RISE fallback")

# --- SLIDE 8 (Validation Plan) ---
do_replace(
    "6-Month Rapid Co-Validation Sprint & Milestone Framework",
    "Rapid Validation Sprint & Milestone Framework",
    "Slide 8: Remove fixed 6-month timeline"
)

# --- SLIDE 9 (Integration Path) ---
do_replace(
    "INTEGRATION PATH WITH SAFRAN",
    "TECHNOLOGY VALIDATION & DEPLOYMENT ROADMAP",
    "Slide 9: Remove Safran integration title"
)
do_replace(
    "From In Silico Design to Joint Flight Certification",
    "From In Silico Design to Physical Validation & Deployment",
    "Slide 9: Remove Joint Flight Certification"
)
do_replace(
    "JOINT SAFRAN FLIGHT CERTIFICATION",
    "INDUSTRY DEPLOYMENT & CERTIFICATION",
    "Slide 9: Remove Joint Safran Flight Certification step"
)
do_replace(
    "alongside Safran\u2019s current single-crystal Nickel superalloys",
    "alongside current industry-standard single-crystal Nickel superalloys",
    "Slide 9: Remove Safran comparison"
)
do_replace(
    "alongside Safran's current single-crystal Nickel superalloys",
    "alongside current industry-standard single-crystal Nickel superalloys",
    "Slide 9: Remove Safran comparison (alt)"
)
do_replace(
    "a long-term, joint qualification flight roadmap",
    "a long-term industry qualification and certification roadmap",
    "Slide 9: Remove joint qualification"
)

# --- SLIDE 13 (Closing) ---
do_replace(
    "against Safran\u2019s specific propulsion boundary constraints",
    "against specific propulsion boundary constraints",
    "Slide 13: Remove Safran specific reference"
)
do_replace(
    "against Safran's specific propulsion boundary constraints",
    "against specific propulsion boundary constraints",
    "Slide 13: Remove Safran specific reference (alt)"
)
do_replace(
    "Partnering to bridge the gap between materials informatics and operational deployment.",
    "Bridging the gap between materials informatics and operational deployment.",
    "Slide 13: Remove 'Partnering'"
)

# --- BUSINESS MODEL SLIDES ---
do_replace(
    "Joint Development Agreement (JDA)",
    "Incubation & Co-Development Partnership",
    "Business: JDA -> Incubation Partnership"
)
do_replace(
    "Partnering through a milestone-funded, shared-risk",
    "Structured as a milestone-funded, shared-risk",
    "Business: Remove 'Partnering through'"
)
do_replace(
    "with Safran\u2019s hot-section teams",
    "with advanced materials research teams",
    "Business: Remove Safran hot-section"
)
do_replace(
    "with Safran's hot-section teams",
    "with advanced materials research teams",
    "Business: Remove Safran hot-section (alt)"
)
do_replace(
    "Provide real engine boundary fields and fund the pre-scale sprint under a budget cap discussed in further meetings..",
    "Provide testing infrastructure, lab access, and mentorship to validate physical prototypes.",
    "Business: Replace Safran support description"
)
do_replace(
    "Provide access to internal testing rigs, engine test cells, and lead downstream flight-readiness certification.",
    "Provide access to materials characterization labs, testing infrastructure, and support downstream certification pathways.",
    "Business: Replace Safran Phase 2 support"
)

# --- GLOBAL: Catch ANY remaining Safran/Saffron mentions ---
do_replace("Safran Explore", "SCIDIP", "Global: Safran Explore -> SCIDIP")
do_replace("Safran", "Industry Partners", "Global: Any remaining Safran mentions")
do_replace("Saffron-Aero", "Crystal Paradigm", "Global: Saffron-Aero -> Crystal Paradigm")

# Save PPTX
prs.save(PPTX_PATH)
print(f"\nPPTX saved to: {PPTX_PATH}")
print(f"Total replacement operations: {len(replacements_log)}")
for r in replacements_log:
    print(r)

# =====================================================
# DOCX MODIFICATIONS
# =====================================================
print("\n" + "=" * 60)
print("PHASE 2: MODIFYING DOCX FOR IIT DELHI SCIDIP")
print("=" * 60)

doc = Document(DOCX_PATH)
docx_replacements = []

def docx_replace_fn(doc, old_text, new_text, desc):
    count = 0
    for paragraph in doc.paragraphs:
        if old_text in paragraph.text:
            for run in paragraph.runs:
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)
                    count += 1
            if count == 0 and old_text in paragraph.text:
                full = paragraph.text
                new_full = full.replace(old_text, new_text)
                if paragraph.runs:
                    paragraph.runs[0].text = new_full
                    for run in paragraph.runs[1:]:
                        run.text = ""
                    count += 1
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if old_text in paragraph.text:
                        for run in paragraph.runs:
                            if old_text in run.text:
                                run.text = run.text.replace(old_text, new_text)
                                count += 1
    docx_replacements.append(f"  [{count} hits] {desc}")
    return count

# --- COVER PAGE ---
docx_replace_fn(doc,
    "Submitted to: Safran Explore Smart Materials Program",
    "Submitted to: Sona Comstar \u2013 IIT Delhi Innovation Program (SCIDIP) 2026",
    "Cover: Replace Safran submission line"
)
docx_replace_fn(doc,
    "Challenge #1: Smart Materials | Challenge #2: Intelligence for Materials & Processes",
    "Focus: Advanced Materials & Manufacturing | AI-Driven Material Discovery",
    "Cover: Replace challenge line"
)
docx_replace_fn(doc,
    "Date: June 2026 | Document Classification: Confidential Pre-NDA Submission",
    "Date: July 2026 | Document Classification: Confidential",
    "Cover: Update date"
)

# --- IP NOTICE ---
docx_replace_fn(doc,
    "consistent with Safran Explore program guidelines.",
    "consistent with standard incubation program guidelines.",
    "IP Notice: Remove Safran Explore"
)
docx_replace_fn(doc,
    "Consistent with guidance provided during the Safran Explore webinar sessions, this document",
    "This document",
    "IP Notice: Remove webinar reference"
)

# --- EXECUTIVE SUMMARY ---
docx_replace_fn(doc,
    "This work directly addresses Safran Explore Challenge #1",
    "This work directly addresses the need for advanced materials innovation",
    "Exec Summary: Remove Challenge #1"
)
docx_replace_fn(doc,
    "(Smart Materials: multifunctional bulk material properties, next-generation Thermal Barrier Coatings, advanced additive manufacturing processes) with a strong AI-driven methodology aligned with Challenge #2 (AI-driven material design for physico-chemical properties, in-silico testing for material performance screening).",
    "combining multifunctional bulk material properties, next-generation Thermal Barrier Coatings, and advanced additive manufacturing processes with a strong AI-driven methodology for material design and in-silico performance screening.",
    "Exec Summary: Remove Challenge #2"
)

# --- SECTION 1: SCOPE ---
docx_replace_fn(doc,
    "This challenge is directly aligned with Safran's LEAP and future RISE open-rotor engine programs.",
    "This challenge is directly aligned with next-generation open-rotor engine programs globally.",
    "Section 1: Remove Safran LEAP/RISE"
)

# --- SECTION 7: ECONOMIC ---
docx_replace_fn(doc,
    "aligned with Safran LEAP-1A and future RISE engine program targets.",
    "aligned with next-generation turbofan and open-rotor engine program targets.",
    "Section 7: Remove Safran LEAP-1A"
)

# --- SECTION 8: COLLABORATION ---
docx_replace_fn(doc,
    "8. Paid POC Collaboration Structure & Roadmap",
    "8. Validation & Collaboration Roadmap",
    "Section 8: Remove Paid POC"
)
docx_replace_fn(doc,
    "To establish complete airworthiness validation under Safran's stringent engineering standards,",
    "To establish complete airworthiness validation under stringent aerospace engineering standards,",
    "Section 8: Remove Safran standards"
)
docx_replace_fn(doc,
    "mutually agreed rapid-validation budget, with scaling provisions for subsequent coupon fabrication, leveraging state-backed aerospace research infrastructure.",
    "a rapid-validation framework, with scaling provisions for subsequent coupon fabrication, leveraging institutional research infrastructure and incubation support.",
    "Section 8: Remove budget, add incubation"
)

# --- SECTION 8.2 ---
docx_replace_fn(doc,
    "Saffron-Aero platform",
    "Crystal Paradigm platform",
    "Section 8.2: Saffron-Aero -> Crystal Paradigm"
)
docx_replace_fn(doc,
    "(LEAP-1A or future RISE configurations)",
    "",
    "Section 8.2: Remove LEAP-1A/RISE"
)

# --- SECTION 9: STRATEGIC ---
docx_replace_fn(doc,
    "Crystal Paradigm views our engagement with Safran as a deep, long-term co-development partnership.",
    "Crystal Paradigm is positioned for deep, long-term co-development partnerships with leading institutions and industry players.",
    "Section 9: Remove Safran engagement"
)
docx_replace_fn(doc,
    "we contribute a high-value technical innovation to Safran's technology roadmap. Crystal Paradigm is fully prepared to adapt to any design modifications requested by Safran over the collaboration period.",
    "we contribute a high-value technical innovation to the advanced materials landscape. Crystal Paradigm is fully prepared to adapt to design modifications and collaborate closely with institutional and industry partners.",
    "Section 9: Remove Safran roadmap"
)

# --- SECTION 10: REFERENCES ---
docx_replace_fn(doc,
    "[12] Safran Explore Smart Materials Technical Briefing: Challenge requirements and evaluation criteria",
    "[12] SCIDIP Program: Sona Comstar \u2013 IIT Delhi Innovation Program focus areas and evaluation criteria",
    "References: Replace Safran reference"
)

# --- SECTION 11: PLATFORM ---
docx_replace_fn(doc,
    "Saffron-Aero computational platform",
    "computational platform",
    "Section 11: Remove Saffron-Aero name"
)

# --- SECTION 12: CONTACT ---
docx_replace_fn(doc,
    "For inquiries regarding the Safran Explore Challenge or collaboration opportunities,",
    "For inquiries regarding collaboration opportunities,",
    "Section 12: Remove Safran Explore reference"
)
docx_replace_fn(doc,
    "We welcome the opportunity to present our platform capabilities in person during the Pitch Session and Explore Days.",
    "We welcome the opportunity to present our platform capabilities and discuss partnership pathways.",
    "Section 12: Remove Pitch Session/Explore Days"
)
docx_replace_fn(doc,
    "Document Classification: Confidential Pre-NDA Submission | Version: 3.0 (Final) | June 2026 | Crystal Paradigm Engineering",
    "Document Classification: Confidential | Version: 4.0 (SCIDIP) | July 2026 | Crystal Paradigm Engineering",
    "Footer: Update version and date"
)

# --- GLOBAL: Catch remaining ---
docx_replace_fn(doc, "Safran Explore", "SCIDIP", "Global: Safran Explore catch-all")
docx_replace_fn(doc, "Safran", "industry partners", "Global: Any remaining Safran")
docx_replace_fn(doc, "Saffron-Aero", "Crystal Paradigm", "Global: Saffron-Aero catch-all")

# Save DOCX
doc.save(DOCX_PATH)
print(f"\nDOCX saved to: {DOCX_PATH}")
print(f"Total replacement operations: {len(docx_replacements)}")
for r in docx_replacements:
    print(r)

# =====================================================
# VERIFICATION
# =====================================================
print("\n" + "=" * 60)
print("PHASE 3: VERIFICATION")
print("=" * 60)

prs_check = Presentation(PPTX_PATH)
pptx_issues = []
for slide_num, slide in enumerate(prs_check.slides, 1):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.lower()
                if "safran" in text or "saffron" in text:
                    pptx_issues.append(f"  SLIDE {slide_num}: '{para.text[:80]}...'")
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    text = cell.text.lower()
                    if "safran" in text or "saffron" in text:
                        pptx_issues.append(f"  SLIDE {slide_num} (TABLE): '{cell.text[:80]}...'")

if pptx_issues:
    print(f"\nWARNING PPTX: Found {len(pptx_issues)} remaining mentions:")
    for i in pptx_issues:
        print(i)
else:
    print("\nPPTX: CLEAN - Zero Safran/Saffron mentions remaining.")

doc_check = Document(DOCX_PATH)
docx_issues = []
for para in doc_check.paragraphs:
    text = para.text.lower()
    if "safran" in text or "saffron" in text:
        docx_issues.append(f"  PARAGRAPH: '{para.text[:80]}...'")
for table in doc_check.tables:
    for row in table.rows:
        for cell in row.cells:
            text = cell.text.lower()
            if "safran" in text or "saffron" in text:
                docx_issues.append(f"  TABLE CELL: '{cell.text[:80]}...'")

if docx_issues:
    print(f"\nWARNING DOCX: Found {len(docx_issues)} remaining mentions:")
    for i in docx_issues:
        print(i)
else:
    print("\nDOCX: CLEAN - Zero Safran/Saffron mentions remaining.")

print("\n" + "=" * 60)
print("DONE. Files ready in:", BASE_DIR)
print("=" * 60)
