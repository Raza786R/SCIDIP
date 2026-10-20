import sys
import zipfile
import xml.etree.ElementTree as ET

pptx_path = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\references_and_guides\FINAL_SUBMISSION_FILES\CRYSTAL PARADIGM_ FOR HOTTER, LONGER-LIVED PROPULSION MATERIALS.pptx"
z = zipfile.ZipFile(pptx_path)
slides = [f for f in z.namelist() if f.startswith('ppt/slides/slide')]
txts = []
for s in slides:
    for node in ET.fromstring(z.read(s)).iter():
        if node.text and node.text.strip():
            txts.append(node.text)

with open("pptx_extracted_new.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(txts))

print("Text extracted to pptx_extracted_new.txt")
