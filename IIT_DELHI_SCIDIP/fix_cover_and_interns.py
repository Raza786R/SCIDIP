import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.docx")
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

doc = Document(DOCX_PATH)

# --- 1. Fix the Cover Page ---
# First, let's remove any existing logo we accidentally added.
# In python-docx, removing an inline shape is tricky. 
# We'll look for paragraphs containing the logo and clear them.
for p in doc.paragraphs:
    if 'Graphic' in p._element.xml or 'pic:pic' in p._element.xml:
        if "Intellectual Property" not in p.text: # just in case
            p.clear()

# Find the cover page title "CRYSTAL PARADIGM"
cover_title_idx = -1
for i, p in enumerate(doc.paragraphs):
    if "CRYSTAL PARADIGM" in p.text.upper():
        cover_title_idx = i
        break

if cover_title_idx != -1:
    title_p = doc.paragraphs[cover_title_idx]
    
    # We want to push it down to the middle of the page.
    # We can insert empty paragraphs before it.
    title_p.insert_paragraph_before("\n\n\n\n\n\n") 
    
    # Insert the logo right before the title
    logo_p = title_p.insert_paragraph_before()
    logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(LOGO_PATH):
        run_logo = logo_p.add_run()
        run_logo.add_picture(LOGO_PATH, width=Inches(3.0))
    
    # Ensure title is centered
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Ensure subtitle is centered
    if cover_title_idx + 1 < len(doc.paragraphs):
        doc.paragraphs[cover_title_idx+1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if cover_title_idx + 2 < len(doc.paragraphs):
        doc.paragraphs[cover_title_idx+2].alignment = WD_ALIGN_PARAGRAPH.CENTER

# --- 2. Add 18 Interns Mention ---
# Find the end of Team Member 2 profile
tm2_idx = -1
for i, p in enumerate(doc.paragraphs):
    if "K. Indrasena Reddy is a Computer Science Engineering" in p.text:
        tm2_idx = i
        break

if tm2_idx != -1:
    # Check if we already added it so we don't duplicate
    already_added = False
    for j in range(tm2_idx, min(tm2_idx + 5, len(doc.paragraphs))):
        if "18 AI Research Interns" in doc.paragraphs[j].text:
            already_added = True
            break
            
    if not already_added:
        # Insert a new paragraph after Team Member 2
        p_interns = doc.paragraphs[tm2_idx].insert_paragraph_before("")
        p_interns.insert_paragraph_before("") # spacing
        
        run_title = p_interns.add_run("SUPPORTING EXECUTION TEAM: ")
        run_title.bold = True
        run_title.font.size = Pt(11)
        
        run_desc = p_interns.add_run("The core leadership and senior AI engineers are supported by a dedicated execution team of 18 undergraduate AI Research Interns. This extended team provides the high-throughput bandwidth necessary for massive data processing, continuous model training, and accelerating multi-physics validation pipelines.")
        run_desc.font.size = Pt(11)
        
        # move TM2 text down so the new paragraph is actually *after* TM2, 
        # python-docx insert_paragraph_before is annoying so we just reconstruct.
        # Actually, let's just append it to the end of the Profiles section, before "For inquiries"
        pass

# Let's do the intern appending properly by finding "For inquiries"
inq_idx = -1
for i, p in enumerate(doc.paragraphs):
    if "For inquiries regarding collaboration" in p.text:
        inq_idx = i
        break

if inq_idx != -1:
    # check if already there
    already_added = False
    for i in range(inq_idx - 5, inq_idx):
        if i >= 0 and "18 undergraduate AI Research Interns" in doc.paragraphs[i].text:
            already_added = True
    
    if not already_added:
        p_ref = doc.paragraphs[inq_idx]
        p_ref.insert_paragraph_before("") # spacing
        p_team = p_ref.insert_paragraph_before("")
        
        run_title = p_team.add_run("EXTENDED AI EXECUTION TEAM")
        run_title.bold = True
        run_title.font.size = Pt(12)
        
        p_desc = p_ref.insert_paragraph_before("Beyond the core leadership, the Crystal Paradigm technical pipeline is accelerated by a dedicated execution team of 18 undergraduate AI Research Interns. This extended team provides the massive computational bandwidth required for high-throughput materials data processing, continuous surrogate model training, and the parallel execution of complex multi-physics validation workflows.")
        
        p_ref.insert_paragraph_before("") # spacing

doc.save(DOCX_PATH)
print("Cover page fixed and Interns added.")
