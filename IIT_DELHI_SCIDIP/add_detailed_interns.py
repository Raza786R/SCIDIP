import os
from docx import Document
from docx.shared import Pt, RGBColor

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.docx")

doc = Document(DOCX_PATH)

# We want to add the profiles right before "For inquiries regarding collaboration opportunities"
insert_index = -1
for i, p in enumerate(doc.paragraphs):
    if "For inquiries regarding collaboration opportunities" in p.text:
        insert_index = i
        break

if insert_index != -1:
    p_ref = doc.paragraphs[insert_index]
    
    # Add spacing
    p_ref.insert_paragraph_before("")
    
    # Profile 1: Mohammed Ahmed Raza
    p1_title = p_ref.insert_paragraph_before("")
    run1 = p1_title.add_run("TEAM MEMBER 1: MOHAMMED AHMED RAZA")
    run1.bold = True
    run1.font.size = Pt(12)
    run1.font.color.rgb = RGBColor(0, 51, 102) # Dark Blue
    
    p1_desc = p_ref.insert_paragraph_before("Mohammed Ahmed Raza is a Computer Science and Engineering student at Neil Gogte Institute of Technology (NGIT) and a Certified AI/ML Professional from iHub-Data, IIIT Hyderabad. He previously served as a Winter Research Intern at IIIT Hyderabad, where he engineered advanced computer vision systems for UAV spatial awareness and obstacle detection. Currently, he advances materials science and deep learning innovations as an AI Research Intern at Crystal Paradigm, where he advances inverse design frameworks for HE-MCGA, computationally engineering next-generation superalloys for extreme aerospace applications. Most recently, he co-authored research introducing a breakthrough Attention Graph Siamese Transformer (DPT-GNN) that drastically optimizes lithium-ion battery capacity predictions through transition-aware learning.")
    
    p_ref.insert_paragraph_before("") # spacing
    
    # Profile 2: K. Indrasena Reddy
    p2_title = p_ref.insert_paragraph_before("")
    run2 = p2_title.add_run("TEAM MEMBER 2: KATTA INDRASENA REDDY")
    run2.bold = True
    run2.font.size = Pt(12)
    run2.font.color.rgb = RGBColor(0, 51, 102) # Dark Blue
    
    p2_desc = p_ref.insert_paragraph_before("K. Indrasena Reddy is a Computer Science Engineering student at Neil Gogte Institute of Technology (NGIT). He previously served as an AI Developer Intern at Viswam.AI, where he built natural language processing applications and contributed to experimental language model research. Currently, he advances materials informatics and graph neural network modeling for large-scale property prediction as an AI Research Intern at Crystal Paradigm.")
    
    p_ref.insert_paragraph_before("") # spacing

doc.save(DOCX_PATH)
print("Added detailed intern profiles successfully.")
