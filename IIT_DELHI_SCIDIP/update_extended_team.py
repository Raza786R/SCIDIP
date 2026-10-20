import os
from docx import Document

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.docx")

doc = Document(DOCX_PATH)

for p in doc.paragraphs:
    if "The core leadership is supported by a dedicated extended cohort" in p.text:
        p.text = "The core leadership is supported by an extended team of AI Research Interns advancing research at the intersection of Artificial Intelligence and Materials Science."
        p.paragraph_format.keep_together = True
        break

doc.save(DOCX_PATH)
print("Updated extended team description.")
