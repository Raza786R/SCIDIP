import os
import zipfile
import shutil

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
INPUT_PPTX = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_PitchDeck_Final.pptx")
OUTPUT_PPTX = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_PitchDeck_Upgraded.pptx")
TEMP_DIR = os.path.join(BASE_DIR, "temp_pptx_extract")

# REPLACEMENTS
replacements = {
    # Slide 1 Body
    b"turbine blade material": b"turbine blade material and extreme-environment mobility components",
    
    # Slide 2/3 Title
    b"HOTTER, LONGER-LIVED PROPULSION MATERIALS": b"EXTREME-ENVIRONMENT ADVANCED MATERIALS",
    
    # Slide 5 Bridge
    b"must be optimized as a single system to prevent failure.": b"must be optimized as a single system to prevent failure. Same physics govern forging die failure, EV motor thermal cycling, and railway brake degradation.",
    
    # Slide 7 Business translation
    b"zero sigma phase risk up to its solidus limit": b"zero sigma phase risk up to its solidus limit (What this means: 3x longer component life).",
    b"(exceptional 7.5 mg/cm\xc2\xb2 achieved).": b"(exceptional 7.5 mg/cm\xc2\xb2 achieved - Survives at 200\xc2\xb0C higher temperatures).",
    
    # Slide 8 Table
    b"Pending Burner Rig": b"Pending Thermal Cycling Test",
    
    # Slide 9
    b"automated Automated": b"Automated",
    
    # Slide 10 SmartArt
    b"JET BURNER RIG SHOCK VALIDATION": b"THERMAL CYCLING VALIDATION",
    b"SUBSCALE BLADE COMPONENTS": b"SUBSCALE COMPONENT VALIDATION",
    
    # Slide 11
    b"Fleet Scalability and Direct Operating Cost Reductions": b"Fleet Scalability and Direct Operating Cost Reductions (Aerospace Case Study - Platform Applicable to Precision Forging &amp; EV Thermal Management)",
    
    # Slide 13
    b"*Transitioning to a structured technology licensing model or direct material supply partnership upon POC validation.": b"*Transitioning to a structured technology licensing model upon POC validation. Platform Application: Precision Forging, EV Thermal Management, and Railway Systems.",
    
    # Slide 14
    b"2. Sona Comstar Incubation": b"2. Sona Comstar Technology Mentorship &amp; Market Connect",
    b"For collaborative downstream application mapping in precision forging and EV thermal management.": b"Industry mentorship and access to corporate market connect for downstream application mapping in precision forging, EV thermal management, and railway systems.",
    b"Bridging the gap between materials informatics and operational deployment.": b"From computational design to physical validation \xe2\x80\x94 in advanced mobility and aerospace."
}

def process_pptx():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)
    
    with zipfile.ZipFile(INPUT_PPTX, 'r') as zip_ref:
        zip_ref.extractall(TEMP_DIR)
        
    for root, dirs, files in os.walk(TEMP_DIR):
        for file in files:
            if file.endswith(".xml"):
                filepath = os.path.join(root, file)
                with open(filepath, 'rb') as f:
                    content = f.read()
                
                modified = False
                for old_val, new_val in replacements.items():
                    if old_val in content:
                        content = content.replace(old_val, new_val)
                        modified = True
                
                if modified:
                    with open(filepath, 'wb') as f:
                        f.write(content)
                        
    # Re-zip
    with zipfile.ZipFile(OUTPUT_PPTX, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(TEMP_DIR):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, TEMP_DIR)
                zipf.write(filepath, arcname)
                
    shutil.rmtree(TEMP_DIR)
    print("Successfully processed PPTX via XML replacement.")

if __name__ == "__main__":
    process_pptx()
