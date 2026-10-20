import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.docx")

doc = Document(DOCX_PATH)

def replace_with_bold(paragraph, search_text):
    """Replaces a specific text in a paragraph with a bold version of it."""
    if search_text not in paragraph.text:
        return False
    
    # Simple approach: rebuild the paragraph runs
    full_text = paragraph.text
    paragraph.clear()
    
    parts = full_text.split(search_text)
    for i, part in enumerate(parts):
        if part:
            paragraph.add_run(part)
        # Add the bolded search text in between parts
        if i < len(parts) - 1:
            run = paragraph.add_run(search_text)
            run.bold = True
            # Optional: Add a slight color highlight (e.g., dark blue)
            # run.font.color.rgb = RGBColor(0, 51, 102) 
    return True

for p in doc.paragraphs:
    # 1. Dr. Venkat profile highlights
    if "Dr. Venkataramana is a Research Associate" in p.text or "38 research publications" in p.text:
        replace_with_bold(p, "38 research publications")
        replace_with_bold(p, "(610+ citations, h-index 14)")
        replace_with_bold(p, "2 book chapters")

    # 2. Dr. Shilpa profile highlights
    if "Dr. Choudhary, recognized among the Top 2%" in p.text or "100 research papers" in p.text:
        replace_with_bold(p, "Top 2% Scientists Worldwide by Stanford University (2024)")
        replace_with_bold(p, "100 research papers (1763 citations, H-index 22)")
        replace_with_bold(p, "12 academic books")
        replace_with_bold(p, "multiple patents")
        
        # Keep lines together to prevent page break mid-paragraph
        p.paragraph_format.keep_together = True
        p.paragraph_format.keep_with_next = True

    # 3. Interns highlights
    if "AI RESEARCH INTERN(CRYSTAL PARADIGM):" in p.text:
        # We want to make these stand out more.
        p.clear()
        if "MOHAMMED AHMED RAZA" in p.text or "MOHAMMED" in p.text:
            text = "AI RESEARCH INTERN (CRYSTAL PARADIGM): MOHAMMED AHMED RAZA"
        elif "KATTA INDRASENA REDDY" in p.text:
            text = "AI RESEARCH INTERN (CRYSTAL PARADIGM): KATTA INDRASENA REDDY"
        else:
            text = p.text
            
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)  # slightly larger
        run.font.color.rgb = RGBColor(0, 51, 102)  # Dark Blue

# Fix the page break issue for Dr. Shilpa's section by adding a page break before her heading if it exists
for i, p in enumerate(doc.paragraphs):
    if "AI/ML Lead: Dr. Shilpa Choudhary" in p.text:
        # Instead of a hard page break, we ensure the heading stays with the paragraph
        p.paragraph_format.keep_with_next = True
        # If it's still splitting, we can force a page break before the heading:
        # We add page_break_before to the paragraph format
        p.paragraph_format.page_break_before = True

doc.save(DOCX_PATH)
print("DOCX profiles updated successfully.")
