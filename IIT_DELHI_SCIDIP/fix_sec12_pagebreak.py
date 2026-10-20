import os
from docx import Document

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.docx")

doc = Document(DOCX_PATH)

for i, p in enumerate(doc.paragraphs):
    if "12." in p.text and "Leadership" in p.text:
        p.paragraph_format.page_break_before = True
        break

doc.save(DOCX_PATH)
print("Section 12 pushed to fresh page.")
