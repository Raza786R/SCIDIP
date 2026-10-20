import os
from docx import Document

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.docx")

doc = Document(DOCX_PATH)

# Function to replace text in runs to preserve formatting
def replace_in_runs(paragraph, old_text, new_text):
    for run in paragraph.runs:
        if old_text in run.text:
            run.text = run.text.replace(old_text, new_text)

# We want to delete certain paragraphs entirely or clear them
paragraphs_to_clear = [
    "Document Classification: Confidential | Version: 4.0 (SCIDIP) | July 2026 | Crystal Paradigm Engineering",
    "Submitted to: Sona Comstar",
    "Focus: Advanced Materials & Manufacturing",
    "Date: July 2026 | Document Classification",
    "TEAM MEMBER 1: MOHAMMED AHMED RAZA",
    "AI Research Intern (Crystal Paradigm) – Core AI model development",
    "TEAM MEMBER 2: KATTA INDRASENA REDDY",
    "AI Research Intern (Crystal Paradigm) – Materials informatics pipeline",
    "Note :- Timeline to be mutually agreed" # Removing this if it exists, as "Note :-" looks AI/robotic
]

def should_clear(text):
    text_upper = text.upper()
    for phrase in paragraphs_to_clear:
        if phrase.upper() in text_upper:
            return True
    return False

# Replace long dashes everywhere
for p in doc.paragraphs:
    # 1. Clear AI-like meta text and footers and team members
    if should_clear(p.text):
        p.clear()
        continue
    
    # 2. Replace long dashes (em-dash and en-dash)
    replace_in_runs(p, "—", "-")
    replace_in_runs(p, "–", "-")
    replace_in_runs(p, " :-", ":")

for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                if should_clear(p.text):
                    p.clear()
                    continue
                replace_in_runs(p, "—", "-")
                replace_in_runs(p, "–", "-")
                replace_in_runs(p, " :-", ":")

# Also do this for PPTX just in case!
try:
    from pptx import Presentation
    PPTX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_PitchDeck.pptx")
    prs = Presentation(PPTX_PATH)
    
    def process_shape_for_dashes(shape):
        if getattr(shape, 'shape_type', None) == 6:  # Group
            for s in shape.shapes:
                process_shape_for_dashes(s)
        
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                for run in p.runs:
                    if "—" in run.text: run.text = run.text.replace("—", "-")
                    if "–" in run.text: run.text = run.text.replace("–", "-")
                    if " :-" in run.text: run.text = run.text.replace(" :-", ":")
                    if "Validation Plan to TRL 4+ - Incubation Milestone Framework" in run.text:
                        pass # ensure standard dash
                    
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    for p in cell.text_frame.paragraphs:
                        for run in p.runs:
                            if "—" in run.text: run.text = run.text.replace("—", "-")
                            if "–" in run.text: run.text = run.text.replace("–", "-")

    for slide in prs.slides:
        for shape in slide.shapes:
            process_shape_for_dashes(shape)
            
    prs.save(PPTX_PATH)
    print("PPTX cleaned of long dashes.")
except Exception as e:
    print(f"PPTX clean failed: {e}")

doc.save(DOCX_PATH)
print("DOCX cleaned of AI identifiers and long dashes.")
