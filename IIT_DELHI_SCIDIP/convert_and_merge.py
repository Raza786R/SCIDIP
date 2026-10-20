import os
import sys
import time

try:
    import comtypes.client
except ImportError:
    print("comtypes not installed")
    sys.exit(1)

try:
    from pypdf import PdfWriter
except ImportError:
    print("pypdf not installed")
    sys.exit(1)

BASE_DIR = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP"
PPTX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_PitchDeck_Final.pptx")
DOCX_PATH = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix_Final.docx")
PPTX_PDF = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_PitchDeck.pdf")
DOCX_PDF = os.path.join(BASE_DIR, "CrystalParadigm_SCIDIP_TechnicalAppendix.pdf")
FINAL_PDF = os.path.join(BASE_DIR, "CrystalParadigm_IITDelhi_SCIDIP_Final_Application.pdf")

def convert_pptx_to_pdf(pptx_path, pdf_path):
    print(f"Converting PPTX to PDF: {pptx_path}")
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    # 32 is the format type for PDF in PowerPoint
    powerpoint.Visible = 1
    try:
        deck = powerpoint.Presentations.Open(pptx_path)
        deck.SaveAs(pdf_path, 32)
        deck.Close()
        print("PPTX conversion successful.")
    except Exception as e:
        print(f"Error converting PPTX: {e}")
    finally:
        powerpoint.Quit()

def convert_docx_to_pdf(docx_path, pdf_path):
    print(f"Converting DOCX to PDF: {docx_path}")
    word = comtypes.client.CreateObject("Word.Application")
    # 17 is the format type for PDF in Word
    word.Visible = False
    try:
        doc = word.Documents.Open(docx_path)
        doc.SaveAs(pdf_path, FileFormat=17)
        doc.Close()
        print("DOCX conversion successful.")
    except Exception as e:
        print(f"Error converting DOCX: {e}")
    finally:
        word.Quit()

def merge_pdfs(pdf_list, output_path):
    print(f"Merging PDFs into {output_path}")
    merger = PdfWriter()
    for pdf in pdf_list:
        if os.path.exists(pdf):
            merger.append(pdf)
        else:
            print(f"File not found for merging: {pdf}")
            return
    merger.write(output_path)
    merger.close()
    print("Merge successful.")

if __name__ == "__main__":
    if os.path.exists(PPTX_PDF):
        os.remove(PPTX_PDF)
    if os.path.exists(DOCX_PDF):
        os.remove(DOCX_PDF)
    if os.path.exists(FINAL_PDF):
        os.remove(FINAL_PDF)

    convert_pptx_to_pdf(PPTX_PATH, PPTX_PDF)
    time.sleep(2)
    convert_docx_to_pdf(DOCX_PATH, DOCX_PDF)
    time.sleep(2)
    merge_pdfs([PPTX_PDF, DOCX_PDF], FINAL_PDF)
    
    print(f"\nFinal PDF ready at: {FINAL_PDF}")
