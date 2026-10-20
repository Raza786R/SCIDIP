import os
from docx import Document

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

# 1. Clean up all empty paragraphs (this fixes the huge gaps)
# We iterate backwards so removal doesn't mess up indexing, although we use _element
empty_count = 0
for p in doc.paragraphs:
    if not p.text.strip():
        # Check if it has any structural importance like page breaks
        has_page_break = False
        for run in p.runs:
            if 'w:br' in run._element.xml and 'type="page"' in run._element.xml:
                has_page_break = True
        
        if not has_page_break:
            p._element.getparent().remove(p._element)
            empty_count += 1

print(f"Removed {empty_count} empty paragraphs to fix huge gaps.")

# 2. Add some controlled spacing before headers (since we removed ALL empty lines)
for p in doc.paragraphs:
    if "Technical Lead: Dr. Kasarapu Venkataramana" in p.text or \
       "AI/ML Lead: Dr. Shilpa Choudhary" in p.text or \
       "TEAM MEMBER 1: MOHAMMED AHMED RAZA" in p.text or \
       "TEAM MEMBER 2: KATTA INDRASENA REDDY" in p.text:
        p.paragraph_format.space_before = 240 # 12 pt spacing before
        p.paragraph_format.keep_with_next = True

# 3. Highlight details in Team Member profiles
for p in doc.paragraphs:
    # Team Member 1 (Raza)
    if "Mohammed Ahmed Raza is a Computer Science" in p.text:
        full_text = p.text
        p.clear()
        
        highlights = [
            "Certified AI/ML Professional from iHub-Data, IIIT Hyderabad",
            "Winter Research Intern at IIIT Hyderabad",
            "advances inverse design frameworks for HE-MCGA",
            "Attention Graph Siamese Transformer (DPT-GNN)"
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
        
    # Team Member 2 (Reddy)
    elif "K. Indrasena Reddy is a Computer Science Engineering" in p.text:
        full_text = p.text
        p.clear()
        
        highlights = [
            "AI Developer Intern at Viswam.AI",
            "natural language processing applications",
            "materials informatics and graph neural network modeling"
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

doc.save(DOCX_PATH)
print("Formatting and highlights applied successfully.")
