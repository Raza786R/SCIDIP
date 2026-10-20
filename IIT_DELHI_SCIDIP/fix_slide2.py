# Fix remaining PPTX Safran mentions on Slide 2
from pptx import Presentation
import os

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
PPTX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_PitchDeck.pptx")

prs = Presentation(PPTX_PATH)

# Target Slide 2 (index 1)
slide = prs.slides[1]
fixes = 0

for shape in slide.shapes:
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if "SAFRAN EXPLORE RESPONSE" in run.text:
                    run.text = run.text.replace("SAFRAN EXPLORE RESPONSE", "SCIDIP APPLICATION")
                    fixes += 1
                    print(f"Fixed: SAFRAN EXPLORE RESPONSE -> SCIDIP APPLICATION")
                if "SAFRAN EXPLORE CHALLENGES" in run.text:
                    run.text = run.text.replace("SAFRAN EXPLORE CHALLENGES", "SCIDIP FOCUS AREAS")
                    fixes += 1
                    print(f"Fixed: SAFRAN EXPLORE CHALLENGES -> SCIDIP FOCUS AREAS")
                # Catch any other case-insensitive Safran on this slide
                if "Safran" in run.text or "SAFRAN" in run.text or "safran" in run.text:
                    original = run.text
                    run.text = run.text.replace("Safran", "SCIDIP").replace("SAFRAN", "SCIDIP").replace("safran", "SCIDIP")
                    fixes += 1
                    print(f"Fixed remaining: '{original[:60]}...' -> '{run.text[:60]}...'")

prs.save(PPTX_PATH)
print(f"\nTotal fixes on Slide 2: {fixes}")

# Final verification across ALL slides
prs_check = Presentation(PPTX_PATH)
issues = []
for slide_num, slide in enumerate(prs_check.slides, 1):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.lower()
                if "safran" in text or "saffron" in text:
                    issues.append(f"  SLIDE {slide_num}: '{para.text[:80]}'")
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    text = cell.text.lower()
                    if "safran" in text or "saffron" in text:
                        issues.append(f"  SLIDE {slide_num} TABLE: '{cell.text[:80]}'")

if issues:
    print(f"\nSTILL FOUND {len(issues)} issues:")
    for i in issues:
        print(i)
else:
    print("\nFINAL VERIFICATION: PPTX is FULLY CLEAN. Zero Safran/Saffron mentions.")
