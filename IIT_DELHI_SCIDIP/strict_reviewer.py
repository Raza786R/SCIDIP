import os
import zipfile

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
INPUT_PPTX = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_PitchDeck_Final.pptx")

checks = {
    '1. Slide 1 (Mobility components added)': b'and extreme-environment mobility components',
    '2. Slide 2/3 (Title fixed)': b'EXTREME-ENVIRONMENT ADVANCED MATERIALS',
    '3. Slide 5 (Sona Comstar bridge)': b'Same physics govern forging die failure, EV motor thermal cycling, and railway brake degradation',
    '4. Slide 7 (3x longer life translation)': b'3x longer component life',
    '4b. Slide 7 (200C higher translation)': b'Survives at 200\xc2\xb0C higher',
    '5. Slide 8 (Table fix)': b'Pending Thermal Cycling Test',
    '6. Slide 9 (Automated fix)': b'automated Automated', # WE EXPECT THIS TO BE ABSENT
    '7. Slide 10 (Thermal Cycling Validation)': b'THERMAL CYCLING VALIDATION',
    '8. Slide 10 (Subscale Component)': b'SUBSCALE COMPONENT VALIDATION',
    '9. Slide 11 (Aerospace Case Study Subtitle)': b'Aerospace Case Study - Platform Applicable to Precision Forging',
    '10. Slide 13 (Platform application)': b'Platform Application: Precision Forging',
    '11. Slide 14 (Mentorship wording)': b'Sona Comstar Technology Mentorship',
    '12. Slide 14 (Closing punchline)': b'From computational design to physical validation'
}

print("Running strict reviewer analysis on PPTX XML...")
all_xml_content = b''

with zipfile.ZipFile(INPUT_PPTX, 'r') as zip_ref:
    for file_info in zip_ref.infolist():
        if file_info.filename.endswith('.xml'):
            all_xml_content += zip_ref.read(file_info.filename)

pending_work = []

for name, target in checks.items():
    if name == '6. Slide 9 (Automated fix)':
        if target in all_xml_content:
            print(f'FAIL - {name}: Found "{target.decode("utf-8")}" (Should be removed)')
            pending_work.append(name)
        else:
            print(f'PASS - {name}')
    else:
        if target in all_xml_content:
            print(f'PASS - {name}')
        else:
            print(f'FAIL - {name}: Could not find "{target.decode("utf-8")}"')
            pending_work.append(name)

if pending_work:
    print("\nPENDING WORK DETECTED:")
    for item in pending_work:
        print(f" - {item}")
else:
    print("\nALL CHECKS PASSED. 100% IMPLEMENTED.")
