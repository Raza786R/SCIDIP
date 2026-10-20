import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document(r'c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP\CrystalParadigm_SCIDIP_TechnicalAppendix_Final.docx')

print('Fixing spacing and page breaks before section 12...')
for i, p in enumerate(doc.paragraphs):
    if '12. Research Leadership' in p.text:
        # Check if this paragraph has page_break_before
        if p.paragraph_format.page_break_before:
            print(f'Removing page_break_before from para {i}')
            p.paragraph_format.page_break_before = False
            
    # Remove trailing newlines from all paragraphs in this area
    if i >= 220 and i <= 240:
        if p.text.endswith('\n') or p.text.endswith('\r'):
            p.text = p.text.strip()
            
        # Also remove embedded newlines that might be causing weird spacing
        if '\n\n' in p.text:
            print(f'Found double newline in para {i}')
            
        # check runs for breaks
        for r in p.runs:
            if 'w:br w:type="page"' in r._element.xml:
                print(f'Removing page break run in para {i}')
                r.clear()

doc.save(r'c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP\CrystalParadigm_SCIDIP_TechnicalAppendix_Final.docx')
print('Fixed and saved.')
