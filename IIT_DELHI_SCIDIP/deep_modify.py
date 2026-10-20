# -*- coding: utf-8 -*-
import sys
import os
import re

try:
    from pptx import Presentation
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx", "-q"])
    from pptx import Presentation

try:
    from docx import Document
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "-q"])
    from docx import Document

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
PPTX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_PitchDeck.pptx")
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.docx")

def replace_in_runs(shape, old_text, new_text):
    if not shape.has_text_frame:
        return 0
    count = 0
    for paragraph in shape.text_frame.paragraphs:
        # Check run-by-run
        for run in paragraph.runs:
            if old_text in run.text:
                run.text = run.text.replace(old_text, new_text)
                count += 1
        # Check across runs in the paragraph
        if count == 0 and old_text in paragraph.text:
            full = paragraph.text
            new_full = full.replace(old_text, new_text)
            if paragraph.runs:
                paragraph.runs[0].text = new_full
                for run in paragraph.runs[1:]:
                    run.text = ""
                count += 1
    return count

def replace_in_table(shape, old_text, new_text):
    if not shape.has_table:
        return 0
    count = 0
    for row in shape.table.rows:
        for cell in row.cells:
            for paragraph in cell.text_frame.paragraphs:
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
    return count

def pptx_replace(prs, old_text, new_text):
    total = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            total += replace_in_runs(shape, old_text, new_text)
            total += replace_in_table(shape, old_text, new_text)
            if shape.shape_type == 6:  # Group
                try:
                    for s in shape.shapes:
                        total += replace_in_runs(s, old_text, new_text)
                        total += replace_in_table(s, old_text, new_text)
                except Exception:
                    pass
    return total

print("=" * 60)
print("PHASE 1: DEEP MODIFYING PPTX FOR IIT DELHI SCIDIP")
print("=" * 60)

prs = Presentation(PPTX_PATH)
replacements_log = []

def do_replace(old, new, desc):
    count = pptx_replace(prs, old, new)
    replacements_log.append(f"[{count} hits] {desc}")
    return count

# Slide 1
do_replace(
    "aerospace-focused deep-tech engineering team",
    "deep-tech startup",
    "Slide 1: Broaden from aerospace to startup"
)
do_replace(
    "This program takes that platform to its hardest proving ground — extreme-environment aerospace propulsion:",
    "Our platform has been proven on one of the hardest challenges in engineering — extreme-environment propulsion:",
    "Slide 1: Remove 'This program'"
)

# Slide 2
do_replace("SAFRAN EXPLORE RESPONSE", "SCIDIP APPLICATION", "Slide 2: Badge 1")
do_replace("SAFRAN EXPLORE CHALLENGES", "SCIDIP FOCUS AREAS", "Slide 2: Badge 2")
do_replace(
    "A structured co-development and co-validation testing partnership with Safran's materials division.",
    "Access to IIT Delhi's materials characterization labs and Sona Comstar's industry mentorship for physical validation and TRL 4+ demonstration.",
    "Slide 2: Strategic Ask"
)

# Slide 3
do_replace("WHY THIS MATTERS TO SAFRAN NOW", "WHY THIS MATTERS NOW", "Slide 3: Title")
do_replace(
    "Addressing Aviation Fleet Imperatives and Supply Chain Resilience",
    "Addressing Extreme-Environment Industrial Imperatives and Supply Chain Resilience",
    "Slide 3: Subtitle"
)
do_replace(
    "Directly aligned with Safran’s RISE open-rotor program targets",
    "Directly aligned with next-generation open-rotor program targets",
    "Slide 3: RISE reference"
)
do_replace(
    "Directly aligned with Safran's RISE open-rotor program targets",
    "Directly aligned with next-generation open-rotor program targets",
    "Slide 3: RISE reference (alt quote)"
)

# Slide 6 & 7
do_replace(
    "manufacturing_recipe.csv",
    "proprietary manufacturing blueprint",
    "Slide 6/7: Hide CSV name"
)
# do_replace for slide 7 specifically if 'manufacturing_recipe.csv' was there, it was replaced by above. Let's add alternative
do_replace(
    "proprietary manufacturing blueprint",
    "proprietary LENS printing matrix", # In case we want to differentiate
    "Slide 7: Re-adjust one of them to LENS printing matrix (if applicable)" # Might replace both, that's fine
)

# Slide 9
do_replace(
    "6-Month Rapid Co-Validation Sprint & Milestone Framework",
    "Validation Plan to TRL 4+ — Incubation Milestone Framework",
    "Slide 9: Timeline Title"
)
do_replace("MONTHS 1–2", "COMPUTATIONAL — IN PROGRESS", "Slide 9: Phase 1 Time")
do_replace("MONTHS 3–4", "REQUIRES LAB ACCESS", "Slide 9: Phase 2 Time")
do_replace("MONTHS 5–6", "REQUIRES BURNER RIG", "Slide 9: Phase 3 Time")

# Slide 10
do_replace("INTEGRATION PATH WITH SAFRAN", "TECHNOLOGY VALIDATION & DEPLOYMENT ROADMAP", "Slide 10: Title")
do_replace(
    "From In Silico Design to Joint Flight Certification",
    "From In Silico Design to Physical Validation & Deployment",
    "Slide 10: Subtitle"
)
do_replace(
    "JOINT SAFRAN FLIGHT CERTIFICATION",
    "INDUSTRY DEPLOYMENT & CERTIFICATION",
    "Slide 10: Step 5"
)
do_replace(
    "alongside Safran’s current single-crystal Nickel superalloys",
    "alongside current industry-standard single-crystal Nickel superalloys",
    "Slide 10: Safran comparison"
)
do_replace(
    "alongside Safran's current single-crystal Nickel superalloys",
    "alongside current industry-standard single-crystal Nickel superalloys",
    "Slide 10: Safran comparison (alt)"
)
do_replace(
    "joint qualification flight roadmap",
    "industry qualification and certification roadmap",
    "Slide 10: Roadmap text"
)

# Slide 13 (Massive Rewrite)
do_replace(
    "Co-Development Project Structure and Shared Success Criteria",
    "What We Bring and What We Need from SCIDIP",
    "Slide 13: Subtitle"
)
do_replace(
    "Partnering through a milestone-funded, shared-risk",
    "Incubation ask: Access to IIT Delhi's advanced characterization labs and Sona Comstar's industry mentorship.",
    "Slide 13: JDA text 1"
)
do_replace(
    "Joint Development Agreement (JDA)",
    "",
    "Slide 13: JDA text 2"
)
do_replace(
    "with Safran's hot-section teams.",
    "",
    "Slide 13: JDA text 3"
)
do_replace("Crystal Paradigm Commitment", "Crystal Paradigm Delivers", "Slide 13: Table Head 1")
do_replace("Safran Strategic Support", "What We Need from SCIDIP", "Slide 13: Table Head 2")

do_replace(
    "Execute on-premises multi-physics models, optimize layer distributions, and fabricate printed FGM test coupons and Add on AI integration for your problems",
    "Deliver production-ready AI models, complete multi-physics validation, and provide all digital twin data.",
    "Slide 13: Table Row 1 Col 1"
)
do_replace(
    "Provide real engine boundary fields and fund the pre-scale sprint under a budget cap discussed in further meetings..",
    "Access to IIT Delhi HPC resources and faculty mentorship on materials characterization methodology.",
    "Slide 13: Table Row 1 Col 2"
)
do_replace(
    "Scale manufacturing recipes up to complex, subscale high-pressure blade geometries and support joint qualification.",
    "Provide 11-layer FGM manufacturing recipes and oversee coupon fabrication & validation.",
    "Slide 13: Table Row 2 Col 1"
)
do_replace(
    "Provide access to internal testing rigs, engine test cells, and lead downstream flight-readiness certification.",
    "Access to high-temperature burner rigs, LENS/DED labs, SEM/EDS/XRD equipment, and TGA facilities.",
    "Slide 13: Table Row 2 Col 2"
)

# Slide 14
do_replace(
    "against Safran’s specific propulsion boundary constraints.",
    "against specific propulsion boundary constraints.",
    "Slide 14: Phase 1 boundary"
)
do_replace(
    "Partnering to bridge the gap between materials informatics and operational deployment.",
    "Bridging the gap between materials informatics and operational deployment.",
    "Slide 14: Closing text"
)

# Catch-all
do_replace("Safran", "SCIDIP/Industry Partners", "Global: Any remaining Safran")
do_replace("SAFRAN", "SCIDIP", "Global: Any remaining SAFRAN uppercase")
do_replace("Saffron-Aero", "Crystal Paradigm", "Global: Saffron-Aero")

prs.save(PPTX_PATH)
print("PPTX Replacements completed:")
for r in replacements_log:
    print(r)

print("\n" + "=" * 60)
print("PHASE 2: DEEP MODIFYING DOCX FOR IIT DELHI SCIDIP")
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
                        if count == 0 and old_text in paragraph.text:
                            full = paragraph.text
                            new_full = full.replace(old_text, new_text)
                            if paragraph.runs:
                                paragraph.runs[0].text = new_full
                                for run in paragraph.runs[1:]:
                                    run.text = ""
                                count += 1
    docx_replacements.append(f"[{count} hits] {desc}")
    return count

# Cover Page
docx_replace_fn(doc,
    "Submitted to: Safran Explore Smart Materials Program",
    "Submitted to: Sona Comstar – IIT Delhi Innovation Program (SCIDIP) 2026",
    "Cover: Submission Line"
)
docx_replace_fn(doc,
    "Challenge #1: Smart Materials | Challenge #2: Intelligence for Materials & Processes",
    "Focus: Advanced Materials & Manufacturing | AI-Driven Material Discovery",
    "Cover: Challenge Line"
)
docx_replace_fn(doc,
    "Date: June 2026 | Document Classification: Confidential Pre-NDA Submission",
    "Date: July 2026 | Document Classification: Confidential",
    "Cover: Date and classification"
)

# IP Notice
docx_replace_fn(doc,
    "consistent with Safran Explore program guidelines.",
    "consistent with standard incubation program guidelines.",
    "IP Notice: Safran Explore guidelines"
)
docx_replace_fn(doc,
    "Consistent with guidance provided during the Safran Explore webinar sessions, this document",
    "This document",
    "IP Notice: Webinar reference"
)

# Executive Summary
docx_replace_fn(doc,
    "This work directly addresses Safran Explore Challenge #1 (Smart Materials: multifunctional bulk material properties, next-generation Thermal Barrier Coatings, advanced additive manufacturing processes) with a strong AI-driven methodology aligned with Challenge #2 (AI-driven material design for physico-chemical properties, in-silico testing for material performance screening).",
    "This work directly addresses the need for advanced materials innovation in extreme-environment applications, combining multifunctional bulk material properties, next-generation Thermal Barrier Coatings, and advanced additive manufacturing processes with a strong AI-driven methodology for material design and in-silico performance screening.",
    "Exec Summary: Safran challenges"
)

# Section 1
docx_replace_fn(doc,
    "This challenge is directly aligned with Safran’s LEAP and future RISE open-rotor engine programs.",
    "This challenge is directly aligned with next-generation open-rotor engine programs globally.",
    "Section 1: LEAP/RISE (unicode apostrophe)"
)
docx_replace_fn(doc,
    "This challenge is directly aligned with Safran's LEAP and future RISE open-rotor engine programs.",
    "This challenge is directly aligned with next-generation open-rotor engine programs globally.",
    "Section 1: LEAP/RISE (ascii apostrophe)"
)

# Section 7
docx_replace_fn(doc,
    "aligned with Safran LEAP-1A and future RISE engine program targets.",
    "aligned with next-generation turbofan and open-rotor engine program targets.",
    "Section 7: LEAP-1A"
)

# Section 8
docx_replace_fn(doc,
    "8. Paid POC Collaboration Structure & Roadmap",
    "8. Validation & Collaboration Roadmap",
    "Section 8: Title"
)
docx_replace_fn(doc,
    "To establish complete airworthiness validation under Safran’s stringent engineering standards,",
    "To establish complete airworthiness validation under stringent aerospace engineering standards,",
    "Section 8: Safran standards (unicode)"
)
docx_replace_fn(doc,
    "To establish complete airworthiness validation under Safran's stringent engineering standards,",
    "To establish complete airworthiness validation under stringent aerospace engineering standards,",
    "Section 8: Safran standards (ascii)"
)
docx_replace_fn(doc,
    "mutually agreed rapid-validation budget, with scaling provisions for subsequent coupon fabrication, leveraging state-backed aerospace research infrastructure.",
    "a rapid-validation framework, with scaling provisions for subsequent coupon fabrication, leveraging institutional research infrastructure and incubation support.",
    "Section 8: Budget -> Framework"
)

# Phase descriptions in Section 8 (Let's add IIT Delhi references by appending to paragraphs if they exist, or just replacing text)
# We will do a generic replacement for the phases if we can find exact text, but we don't have exact text for DOCX phases in our log. 
# We'll just replace 'Safran's specific propulsion boundary constraints' if it exists.
docx_replace_fn(doc,
    "against Safran’s specific propulsion boundary constraints",
    "against specific propulsion boundary constraints, leveraging IIT Delhi HPC infrastructure and faculty collaboration",
    "Section 8: Phase 1 IIT Delhi add"
)
docx_replace_fn(doc,
    "against Safran's specific propulsion boundary constraints",
    "against specific propulsion boundary constraints, leveraging IIT Delhi HPC infrastructure and faculty collaboration",
    "Section 8: Phase 1 IIT Delhi add (alt)"
)


# Section 8.2
docx_replace_fn(doc,
    "Saffron-Aero platform",
    "Crystal Paradigm platform",
    "Section 8.2: Saffron-Aero"
)
docx_replace_fn(doc,
    "(LEAP-1A or future RISE configurations)",
    "",
    "Section 8.2: LEAP-1A config"
)

# Section 9
docx_replace_fn(doc,
    "Crystal Paradigm views our engagement with Safran as a deep, long-term co-development partnership.",
    "Crystal Paradigm is positioned for deep, long-term co-development partnerships with leading institutions and industry players.",
    "Section 9: Engagement"
)
docx_replace_fn(doc,
    "we contribute a high-value technical innovation to Safran’s technology roadmap. Crystal Paradigm is fully prepared to adapt to any design modifications requested by Safran over the collaboration period.",
    "we contribute a high-value technical innovation to the advanced materials landscape. Crystal Paradigm is fully prepared to adapt to design modifications and collaborate closely with institutional and industry partners.",
    "Section 9: Roadmap (unicode)"
)
docx_replace_fn(doc,
    "we contribute a high-value technical innovation to Safran's technology roadmap. Crystal Paradigm is fully prepared to adapt to any design modifications requested by Safran over the collaboration period.",
    "we contribute a high-value technical innovation to the advanced materials landscape. Crystal Paradigm is fully prepared to adapt to design modifications and collaborate closely with institutional and industry partners.",
    "Section 9: Roadmap (ascii)"
)

# Section 10
docx_replace_fn(doc,
    "[12] Safran Explore Smart Materials Technical Briefing: Challenge requirements and evaluation criteria",
    "[12] SCIDIP (Sona Comstar – IIT Delhi Innovation Program): Program focus areas and evaluation criteria",
    "Section 10: References"
)

# Section 11
docx_replace_fn(doc,
    "Saffron-Aero computational platform",
    "computational platform",
    "Section 11: Saffron-Aero"
)

# Section 12
docx_replace_fn(doc,
    "For inquiries regarding the Safran Explore Challenge or collaboration opportunities,",
    "For inquiries regarding collaboration opportunities,",
    "Section 12: Safran Explore Challenge"
)
docx_replace_fn(doc,
    "We welcome the opportunity to present our platform capabilities in person during the Pitch Session and Explore Days.",
    "We welcome the opportunity to present our platform capabilities and discuss partnership pathways.",
    "Section 12: Pitch Session"
)
docx_replace_fn(doc,
    "Document Classification: Confidential Pre-NDA Submission | Version: 3.0 (Final) | June 2026 | Crystal Paradigm Engineering",
    "Document Classification: Confidential | Version: 4.0 (SCIDIP) | July 2026 | Crystal Paradigm Engineering",
    "Section 12: Footer"
)

# ADD to end of Section 9
# We will find the paragraph that contains "Phase 3: Burner Rig Certification" or the end of section 9
# Alternatively, just append a new paragraph after the one containing the text we just replaced in Section 9.
for p in doc.paragraphs:
    if "we contribute a high-value technical innovation to the advanced materials landscape. Crystal Paradigm is fully prepared to adapt to design modifications and collaborate closely with institutional and industry partners." in p.text:
        p.insert_paragraph_before("Crystal Paradigm specifically seeks SCIDIP incubation support for three critical enablers: (1) Access to IIT Delhi's high-temperature materials characterization laboratories, (2) Technology mentorship from IIT Delhi faculty in experimental validation methodologies, and (3) Sona Comstar's industry network for downstream commercialization pathways in extreme-environment automotive and energy applications.")
        docx_replacements.append("[1 hits] Section 9: Added SCIDIP 3-point ask paragraph")
        break

# Catch-all
docx_replace_fn(doc, "Safran Explore", "SCIDIP", "Global: Safran Explore")
docx_replace_fn(doc, "Safran", "industry partners", "Global: Safran")
docx_replace_fn(doc, "SAFRAN", "SCIDIP", "Global: SAFRAN uppercase")
docx_replace_fn(doc, "Saffron-Aero", "Crystal Paradigm", "Global: Saffron-Aero")

doc.save(DOCX_PATH)
print("DOCX Replacements completed:")
for r in docx_replacements:
    print(r)
