import os
from docx import Document
from docx.shared import Pt, RGBColor

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.docx")

doc = Document(DOCX_PATH)

def replace_with_bold(paragraph, search_text):
    if search_text not in paragraph.text:
        return False
    full_text = paragraph.text
    paragraph.clear()
    parts = full_text.split(search_text)
    for i, part in enumerate(parts):
        if part:
            paragraph.add_run(part)
        if i < len(parts) - 1:
            run = paragraph.add_run(search_text)
            run.bold = True
    return True

# Delete all existing intern lines so we can reconstruct them perfectly
paragraphs_to_delete = []
for i, p in enumerate(doc.paragraphs):
    if "AI RESEARCH INTERN" in p.text.upper() or "TEAM MEMBER" in p.text.upper():
        paragraphs_to_delete.append(p)
        p.clear()

for p in doc.paragraphs:
    # Ma'am's Profile Highlights (Dr. Shilpa Choudhary)
    if "Dr. Choudhary, recognized among" in p.text:
        # Clear previous highlights by grabbing full text and starting fresh
        full_text = p.text
        p.clear()
        
        # We will manually reconstruct the paragraph with rich highlights
        highlights = [
            "Top 2% Scientists Worldwide by Stanford University (2024)",
            "16 years of research expertise in Artificial Intelligence, Deep Learning, and AI-driven scientific applications",
            "postdoctoral research experience at the Singapore Institute of Technology and the National Kaohsiung University of Science and Technology (Taiwan)",
            "100 research papers (1763 citations, H-index 22)",
            "12 academic books",
            "multiple patents"
        ]
        
        current_text = full_text
        for h in highlights:
            if h in current_text:
                parts = current_text.split(h)
                p.add_run(parts[0])
                r = p.add_run(h)
                r.bold = True
                if len(parts) > 1:
                    current_text = parts[1]
        
        if current_text:
            p.add_run(current_text)

        p.paragraph_format.keep_together = True
        p.paragraph_format.keep_with_next = True
        
    # Sir's Profile Highlights (Dr. Venkataramana)
    elif "Dr. Venkataramana is a Research Associate" in p.text:
        full_text = p.text
        p.clear()
        highlights = [
            "Associate Fellow of the Telangana Academy of Sciences (2024)",
            "12 years of research and 5 years of academic teaching experience",
            "38 research publications (610+ citations, h-index 14)",
            "2 book chapters",
            "leading DRDO-sponsored pyrotechnic nanomaterial fabrication projects"
        ]
        
        current_text = full_text
        for h in highlights:
            if h in current_text:
                parts = current_text.split(h)
                p.add_run(parts[0])
                r = p.add_run(h)
                r.bold = True
                if len(parts) > 1:
                    current_text = parts[1]
        
        if current_text:
            p.add_run(current_text)

# Find where to add the Team Members (right before Section 12 or at the end of profiles)
insert_index = -1
for i, p in enumerate(doc.paragraphs):
    if "For inquiries regarding collaboration opportunities" in p.text:
        insert_index = i
        break

if insert_index != -1:
    # Insert team members back beautifully
    p_ref = doc.paragraphs[insert_index]
    
    # Space
    p_ref.insert_paragraph_before("")
    
    # Member 1
    p1 = p_ref.insert_paragraph_before("")
    run1 = p1.add_run("TEAM MEMBER 1: MOHAMMED AHMED RAZA")
    run1.bold = True
    run1.font.size = Pt(12)
    run1.font.color.rgb = RGBColor(0, 51, 102)
    p1.add_run("\nAI Research Intern (Crystal Paradigm) – Core AI model development and constrained optimization execution.")
    
    # Member 2
    p2 = p_ref.insert_paragraph_before("")
    run2 = p2.add_run("TEAM MEMBER 2: KATTA INDRASENA REDDY")
    run2.bold = True
    run2.font.size = Pt(12)
    run2.font.color.rgb = RGBColor(0, 51, 102)
    p2.add_run("\nAI Research Intern (Crystal Paradigm) – Materials informatics pipeline and multi-physics validation mapping.")
    
    p_ref.insert_paragraph_before("")

doc.save(DOCX_PATH)
print("Updated DOCX profiles successfully.")
