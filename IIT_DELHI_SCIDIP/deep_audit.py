"""
DEEP AUDIT of CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx
Extract EVERY shape, its position, size, text, font size, color.
Look for: overlaps, tiny fonts, empty spaces, inconsistencies.
"""
from pptx import Presentation
from pptx.util import Inches
import io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

prs = Presentation("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
SW = prs.slide_width.inches
SH = prs.slide_height.inches
print(f"DECK: {len(prs.slides)} slides | {SW:.2f}\" x {SH:.2f}\"")

for si, slide in enumerate(prs.slides):
    texts = []
    for s in slide.shapes:
        if hasattr(s,'text') and s.text.strip():
            texts.append(s.text.strip()[:50])
    first = texts[0] if texts else '(image/empty)'
    print(f"\n{'='*75}")
    print(f"SLIDE {si+1:02d} | {first}")
    print(f"{'='*75}")
    
    for s in slide.shapes:
        l = round(s.left/914400, 2) if s.left is not None else 0
        t = round(s.top/914400, 2) if s.top is not None else 0
        w = round(s.width/914400, 2) if s.width is not None else 0
        h = round(s.height/914400, 2) if s.height is not None else 0
        
        # Out of bounds check
        oob = ""
        if t + h > SH: oob = " !! OVERFLOWS BOTTOM"
        if l + w > SW: oob = " !! OVERFLOWS RIGHT"
        if t < 0: oob = " !! ABOVE TOP"
        if l < 0: oob = " !! LEFT OF SLIDE"
        
        fill_str = ""
        try:
            f = s.fill
            if f.type == 1:  # SOLID
                fill_str = f" bg=#{f.fore_color.rgb}"
        except: pass
        
        if hasattr(s, 'text_frame') and s.text.strip():
            # Get ALL text with font details
            for pi, para in enumerate(s.text_frame.paragraphs):
                ptxt = para.text.strip()
                if not ptxt: continue
                for ri, run in enumerate(para.runs):
                    rtxt = run.text.strip()
                    if not rtxt: continue
                    sz = round(run.font.size/12700) if run.font.size else '?'
                    try: col = f"#{run.font.color.rgb}"
                    except: col = 'inherit'
                    bold = 'B' if run.font.bold else ''
                    # Flag very small fonts
                    flag = " << TINY" if isinstance(sz, int) and sz < 7 else ""
                    flag += " << INHERIT_COLOR" if col == 'inherit' else ""
                    print(f"  l={l:5.2f} t={t:5.2f} w={w:5.2f} h={h:5.2f}{fill_str}{oob}")
                    print(f"    p{pi}r{ri}: sz={sz:3} {col} {bold:1}  '{rtxt[:55]}'{flag}")
                    break  # just show first run per para
                break  # just first para for now
        elif not hasattr(s, 'text_frame') or not s.text.strip():
            stype = {1:'SHAPE',13:'PICTURE',6:'GROUP'}.get(s.shape_type, str(s.shape_type))
            print(f"  [{stype}] l={l:5.2f} t={t:5.2f} w={w:5.2f} h={h:5.2f}{fill_str}{oob}")
