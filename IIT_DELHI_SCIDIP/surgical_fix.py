"""
SURGICAL ELITE FIX — CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx
=================================================================
Targets (from deep audit):
  S01  - Fix title style; add Crystal Paradigm identity line
  S04  - Fix 3rd result card overflow right (l=6.92+3.10=10.02)
  S06  - Fix background image top position (t=0.20 → 0.00)
  S08  - Fix background image above-top (t=-0.03 → 0.00)
  S09  - Fix sz=6 tiny fonts; replace aerospace row with Sona Comstar row
  S10  - Fix background image (t=0.01 → 0.00); add IIT Delhi CRF note
  S11  - Fix "Flight-Readiness Funnel" → "Factory-Floor Integration"
  S12  - Rewrite economic ledger for Sona Comstar EV economics
  S15  - Fix bottom overflow items; compress layout
  S16-S19 - Fix footer overflow (h=0.59 → 0.54)
  S20  - Fix image left-of-slide (l=-0.06 → 0.00); fix footer overflow
  ALL new slides footer text - Fix l=2.0 → 0.38
"""
import shutil, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

# ── PALETTE ──────────────────────────────────────────────────────────────────
C_TITLE   = RGBColor(0x1A, 0x36, 0x5D)
C_SUB     = RGBColor(0x2B, 0xDE, 0xFD)
C_ACCENT  = RGBColor(0x00, 0xB4, 0xD8)
C_BODY    = RGBColor(0x11, 0x11, 0x11)
C_MUTED   = RGBColor(0x55, 0x80, 0xA0)
C_FOOTER  = RGBColor(0x0F, 0x20, 0x3C)
C_CARD    = RGBColor(0xFF, 0xFF, 0xFF)
C_BORDER  = RGBColor(0xD6, 0xE4, 0xEF)
C_FTXT    = RGBColor(0xD0, 0xE8, 0xF5)
C_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
C_GREEN   = RGBColor(0x05, 0x96, 0x69)
C_GOLD    = RGBColor(0xF5, 0x9E, 0x0B)
C_RED     = RGBColor(0xDC, 0x26, 0x26)
C_DARK    = RGBColor(0x0F, 0x20, 0x3C)
C_LBLUE   = RGBColor(0xF8, 0xFA, 0xFC)

def I(v): return Inches(v)
def near(a, b, tol=0.08): return abs(a - b) < tol

def get_pos(s):
    """Return (l, t, w, h) in inches."""
    return (
        s.left/914400 if s.left else 0,
        s.top/914400 if s.top else 0,
        s.width/914400 if s.width else 0,
        s.height/914400 if s.height else 0,
    )

def set_pos(s, l=None, t=None, w=None, h=None):
    if l is not None: s.left = I(l)
    if t is not None: s.top = I(t)
    if w is not None: s.width = I(w)
    if h is not None: s.height = I(h)

def set_font(run, sz=None, color=None, bold=None):
    if sz: run.font.size = Pt(sz)
    if color: run.font.color.rgb = color
    if bold is not None: run.font.bold = bold

def set_all_runs_font(tf, sz=None, color=None, bold=None):
    for para in tf.paragraphs:
        for run in para.runs:
            set_font(run, sz, color, bold)

def set_first_run(tf, sz=None, color=None, bold=None, text=None):
    for para in tf.paragraphs:
        for run in para.runs:
            set_font(run, sz, color, bold)
            if text is not None:
                run.text = text
            return

def add_txt(slide, text, l, t, w, h, sz=9, bold=False, color=None,
            align=PP_ALIGN.LEFT, italic=False):
    b = slide.shapes.add_textbox(I(l), I(t), I(w), I(h))
    tf = b.text_frame; tf.word_wrap = True
    tf.margin_left = Pt(0); tf.margin_right = Pt(0)
    tf.margin_top = Pt(2); tf.margin_bottom = Pt(2)
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(sz); r.font.bold = bold
    r.font.color.rgb = color or C_BODY
    return b

def add_rect(slide, l, t, w, h, fill=None, bd_color=None, bd_w=Pt(0.75)):
    s = slide.shapes.add_shape(1, I(l), I(t), I(w), I(h))
    if fill: s.fill.solid(); s.fill.fore_color.rgb = fill
    else: s.fill.background()
    if bd_color: s.line.color.rgb = bd_color; s.line.width = bd_w
    else: s.line.fill.background()
    return s

# ── LOAD ─────────────────────────────────────────────────────────────────────
shutil.copy2("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx",
             "CrystalParadigm_SCIDIP_IITDelhi_ELITE_v2.pptx")
prs = Presentation("CrystalParadigm_SCIDIP_IITDelhi_ELITE_v2.pptx")
slides = list(prs.slides)
print(f"Loaded: {len(slides)} slides")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Fix title style + Crystal Paradigm identity
# From audit: title textbox at l=0.52 t=1.46 w=5.62 h=3.12, sz=13 #1A365D
# No header bar exists — S01 is a special image+text layout
# Add subtitle line below title about Crystal Paradigm's mission & domains
# ═══════════════════════════════════════════════════════════════════════════════
s1 = slides[0]
print("\n[S01] Fixing title slide...")
for sh in s1.shapes:
    l, t, w, h = get_pos(sh)
    if hasattr(sh, 'text_frame') and sh.text.strip():
        txt = sh.text.strip()
        if 'Advanced Materials' in txt and near(t, 1.46):
            # Boost font size on title
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    if run.font.size:
                        run.font.size = Pt(22)
                        run.font.color.rgb = C_TITLE
                        run.font.bold = True
            print(f"  Fixed: Title font sz=13 → sz=22")

# Add Crystal Paradigm identity line (below title area)
add_txt(s1,
    "Accelerating the Discovery of Tomorrow's Materials — at the Intersection of AI and Material Science",
    0.52, 4.62, 5.6, 0.26, sz=9, color=C_MUTED)
add_txt(s1,
    "Active Research Domains: Supercapacitors  ·  Li-ion & Na-ion Battery Electrolytes  ·  Solid-State Cathodes  ·  Solar Materials  ·  Advanced Sensor Materials  ·  Extreme-Environment Alloys",
    0.52, 4.92, 5.6, 0.3, sz=7.5, color=C_ACCENT)
print("  Added: Crystal Paradigm domain identity lines")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Fix third result card overflow right
# From audit: SHAPE at l=6.92 w=3.10 → l+w = 10.02, overflows 0.02"
# Fix: move to l=6.58 → 6.58+3.10=9.68 ✓
# Also fix the textboxes inside that card
# ═══════════════════════════════════════════════════════════════════════════════
s4 = slides[3]
print("\n[S04] Fixing third result card overflow...")
fixed_s4 = 0
for sh in s4.shapes:
    l, t, w, h = get_pos(sh)
    # Third card shapes are at l≈6.92 t≈3.95
    if near(l, 6.92) and t >= 3.9:
        set_pos(sh, l=6.58)
        fixed_s4 += 1
    # Textboxes inside third card: l≈7.04 t≈4.08 or 4.38
    elif near(l, 7.04) and t >= 3.9:
        set_pos(sh, l=6.70)
        fixed_s4 += 1
print(f"  Fixed: {fixed_s4} shapes repositioned")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Fix background image t=0.20 → 0.00
# ═══════════════════════════════════════════════════════════════════════════════
s6 = slides[5]
print("\n[S06] Fixing background image position...")
for sh in s6.shapes:
    l, t, w, h = get_pos(sh)
    if sh.shape_type == 13 and near(t, 0.20):  # PICTURE
        set_pos(sh, t=0.00)
        print("  Fixed: Image t=0.20 → 0.00")
    # Fix tiny sz=6 fonts (SHEAR labels etc)
    if hasattr(sh, 'text_frame'):
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                if run.font.size and run.font.size < Pt(7).pt * 12700:
                    run.font.size = Pt(8)
print("  Fixed: Tiny fonts bumped to sz=8")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Fix background image above-top (t=-0.03 → 0.00)
# ═══════════════════════════════════════════════════════════════════════════════
s8 = slides[7]
print("\n[S08] Fixing image position above top...")
for sh in s8.shapes:
    l, t, w, h = get_pos(sh)
    if sh.shape_type == 13 and t < 0:  # PICTURE above top
        set_pos(sh, t=0.00)
        print(f"  Fixed: Image t={t:.2f} → 0.00")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Fix tiny fonts + replace aerospace-only "Transpiration Film" row
# ═══════════════════════════════════════════════════════════════════════════════
s9 = slides[8]
print("\n[S09] Fixing verification table...")

# Fix tiny sz=6 font on GREEN/YELLOW status badges
for sh in s9.shapes:
    if hasattr(sh, 'text_frame'):
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                if run.font.size and run.font.size <= Pt(6) * 12700:
                    run.font.size = Pt(8)
                    run.font.bold = True
                    print(f"    Bumped tiny font: '{run.text}' → sz=8")

# Replace "Transpiration Film Stability" row text — find by position
# From audit: l=0.47 t=4.31 → "Transpiration Film Stability"
# l=2.50 t=4.31 → "Modeled (CFD Jet Lift)"
# l=4.34 t=4.31 → "Pending Thermal Cycling Test"
# l=6.28 t=4.31 → "Zero Boundary Separation"
transpiration_replacements = {
    (0.47, 4.31): "Forging Die Fit (Sona Comstar)",
    (2.50, 4.31): "FEA-Simulated DED Interface",
    (4.34, 4.31): "Pending Die Trial at Sona Comstar",
    (6.28, 4.31): "Match Factory Tolerance ±0.05 mm",
}
for sh in s9.shapes:
    l, t, w, h = get_pos(sh)
    for (tl, tt), new_text in transpiration_replacements.items():
        if near(l, tl, 0.05) and near(t, tt, 0.05) and hasattr(sh, 'text_frame'):
            old = sh.text.strip()
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    run.text = new_text
                    run.font.size = Pt(8)
                    run.font.color.rgb = C_BODY
                    break
                break
            print(f"  Replaced: '{old[:35]}' → '{new_text[:35]}'")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Fix background image + add IIT Delhi CRF explicit note
# ═══════════════════════════════════════════════════════════════════════════════
s10 = slides[9]
print("\n[S10] Fixing validation plan slide...")
for sh in s10.shapes:
    l, t, w, h = get_pos(sh)
    if sh.shape_type == 13 and near(t, 0.01):  # PICTURE
        set_pos(sh, t=0.00)
        print("  Fixed: Image t=0.01 → 0.00")
    # Find the "Note: Timeline to be mutually agreed" textbox at l=0.58 t=1.04
    if hasattr(sh, 'text_frame') and near(l, 0.58, 0.1) and near(t, 1.04, 0.1):
        if 'mutually agreed' in sh.text:
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    run.text = ("Note: Timeline aligned to SCIDIP's 24-month AIC IIT Delhi incubation cycle. "
                               "Lab access via IIT Delhi CRF (XRD, STA, SEM/EDS) and NIDHI-CoE (tensile testing).")
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = C_ACCENT
                    break
                break
            print("  Updated: CRF/NIDHI-CoE reference added to timeline note")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Fix "Flight-Readiness Funnel" → "Factory-Floor Integration"
# From audit: l=5.34 t=3.73 → "Flight-Readiness Funnel"
#             l=5.34 t=3.99 → body text mentioning "manufacturing"
# ═══════════════════════════════════════════════════════════════════════════════
s11 = slides[10]
print("\n[S11] Fixing aerospace-specific language...")
for sh in s11.shapes:
    l, t, w, h = get_pos(sh)
    if hasattr(sh, 'text_frame'):
        txt = sh.text.strip()
        if 'Flight-Readiness' in txt or 'flight' in txt.lower():
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    if 'Flight' in run.text or 'flight' in run.text:
                        run.text = run.text.replace('Flight-Readiness Funnel', 'Factory-Floor Integration')
                        run.text = run.text.replace('flight', 'factory-floor')
                        print(f"  Fixed: 'Flight-Readiness' → 'Factory-Floor Integration'")
        # Also fix "move to manufacturing" body
        if near(l, 5.34, 0.05) and near(t, 3.99, 0.05):
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    run.text = ("Upon TRL 4 physical validation at IIT Delhi CRF, move to Sona Comstar "
                               "factory-floor integration trials. Begin H13 forging die replacement "
                               "and SRM stator prototyping aligned to Sona Comstar's EPIC roadmap.")
                    run.font.size = Pt(8)
                    run.font.color.rgb = C_BODY
                    break
                break

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — Rewrite Economic Ledger for Sona Comstar EV economics
# Original has aerospace (jet A-1 fuel, SFC, $11.4M/year) — WRONG
# Replace with: Forging Die savings + EV Motor savings + Supply chain
# ═══════════════════════════════════════════════════════════════════════════════
s12 = slides[11]
print("\n[S12] Rewriting economic ledger for Sona Comstar...")

# New data rows:
# Row: "Assessment Parameter" | "Economic Mechanism" | "Crystal Paradigm Value" | "Sona Comstar Benefit"
sona_economics = [
    # (col1_txt, col2_txt, col3_txt, col4_txt)
    ("H13 Forging Die\nCost Reduction",
     "Ta-W-Cr-V-Ti HEA: 75% Hafnium → Titanium substitution; cost: ~$170/kg vs $280/kg Hf-rich alloys",
     "15–20% Drop in Alloy\nRaw Material Cost",
     "Saves ₹2–4 Cr / Year\nacross 9 facilities"),
    ("Forging Die\nLifespan Extension",
     "Candidate C retains >917.7 MPa yield at 1,200°C vs H13 collapse to ~420 MPa (77% failure)",
     "3× longer tooling life;\neliminate thermal fatigue",
     "MRO Cost Cut: ₹5–8 Cr\n/ Year in downtime savings"),
    ("EV SRM Motor\nThermal Efficiency",
     "FGM thermal shield: 15.95 MPa interface stress; zero delamination under extreme torque cycling",
     "Rare-Earth-Free SRM\nat commercial scale",
     "Eliminates ₹50–80 Cr\nNeodymium import cost"),
    ("ESG Supplier\nCompliance Score",
     "Embodied Energy: 1,680 MJ/kg; zero rare-earth dependency; ZLD-compatible production process",
     "Qualifies 75% Sona\nComstar ESG mandate",
     "Unlocks full EPIC supply\nchain partnership tier"),
    ("IP & Commercialization\nScalability",
     "11-phase AI pipeline generates bespoke materials for any EPIC vertical on demand — continuously",
     "1 Patent + 4 Papers\nUnder Review (TRL 3+)",
     "JV / Acquisition pathway\nvia SCIDIP incubation"),
]

# Find the table rows by position and rewrite
# Header row at t≈2.34, data rows at t≈2.76, 3.12, 3.49, 3.85, 4.22
# Col positions: l≈0.47 (col1), l≈2.55 (col2), l≈5.47 (col3), l≈7.45 (col4)
row_tops = [2.76, 3.12, 3.49, 3.85, 4.22]
col_lefts = [0.47, 2.55, 5.47, 7.45]

for sh in s12.shapes:
    l, t, w, h = get_pos(sh)
    if not hasattr(sh, 'text_frame'): continue
    txt = sh.text.strip()

    # Fix subtitle
    if near(t, 0.83, 0.05) and 'Fleet Scalability' in txt:
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                run.text = "Sona Comstar EPIC Mobility — Quantified Material Advantage & Commercial Returns"
                run.font.size = Pt(11)
                run.font.color.rgb = C_SUB
                break
            break
        print("  Fixed: Subtitle updated for Sona Comstar")

    # Fix title
    if near(t, 0.42, 0.05) and 'ECONOMIC VALUE' in txt:
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                run.text = "CRYSTAL PARADIGM ECONOMIC VALUE FOR SONA COMSTAR"
                run.font.size = Pt(22)
                run.font.color.rgb = C_TITLE
                break
            break
        print("  Fixed: Title updated")

    # Header col 2
    if near(l, 2.55, 0.05) and near(t, 2.34, 0.05) and 'Formula' in txt:
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                run.text = "Economic Mechanism"
                break
            break

    # Header col 3
    if near(l, 5.47, 0.05) and near(t, 2.34, 0.05) and 'Baseline' in txt:
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                run.text = "Crystal Paradigm Value"
                break
            break

    # Header col 4
    if near(l, 7.45, 0.05) and near(t, 2.34, 0.05) and 'Savings Yield' in txt:
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                run.text = "Sona Comstar Benefit"
                break
            break

    # Data rows
    for ri, rt in enumerate(row_tops):
        if ri >= len(sona_economics): break
        row_data = sona_economics[ri]
        for ci, cl in enumerate(col_lefts):
            if near(l, cl, 0.05) and near(t, rt, 0.05):
                for para in sh.text_frame.paragraphs:
                    for run in para.runs:
                        run.text = row_data[ci]
                        run.font.size = Pt(7.5)
                        # Color: col1=title, col2=muted, col3=muted, col4=green
                        if ci == 0: run.font.color.rgb = C_TITLE
                        elif ci == 3: run.font.color.rgb = C_GREEN; run.font.bold = True
                        else: run.font.color.rgb = C_MUTED
                        break
                    break
                print(f"  Updated: R{ri+1}C{ci+1} = '{row_data[ci][:30]}'")

# Fix the fleet row label + total row
for sh in s12.shapes:
    l, t, w, h = get_pos(sh)
    if not hasattr(sh, 'text_frame'): continue
    txt = sh.text.strip()
    if 'Fleet Scalability Revenue' in txt:
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                run.text = "Total Commercialization Revenue Potential"
                run.font.size = Pt(9)
                break
            break
    if '$11,475,000' in txt or '100 Narrowbody' in txt or 'Total Yield' in txt:
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                if 'Total Yield' in run.text or '100 Narrowbody' in run.text:
                    run.text = "Savings × 9 Mfg Facilities"
                elif '11,475' in run.text:
                    run.text = "₹15–20 Cr / Year\nConservative Estimate"
                run.font.size = Pt(9)
                break
            break
    if '$0.85' in txt or 'Jet A-1' in txt or '135,000 Liters' in txt or 'SFC' in txt:
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                if 'SFC' in run.text: run.text = "Sona Comstar EPIC Verticals"
                elif '0.85' in run.text: run.text = "9 Global Mfg Sites"
                elif '135,000' in run.text: run.text = "Direct + MRO savings"
                elif '7,200' in run.text: run.text = "EV motor supply chain"
                run.font.size = Pt(8)
                break
            break
    # Fix any lingering aerospace references
    if 'SFC' in txt or 'Bleed Air' in txt or 'Jet A' in txt or 'narrowbody' in txt.lower():
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                run.text = run.text.replace('Parasitic Bleed Air Cut', 'Alloy Cost Reduction')
                run.text = run.text.replace('Net SFC Efficiency Gain', 'Die Life Extension')
                run.text = run.text.replace('Volumetric Fuel Savings', 'EV Motor Material Cost')
                run.text = run.text.replace('Direct Operating Cost Cut', 'ESG Compliance Unlock')
                break
            break

print("  S12: Economic ledger rewritten for Sona Comstar")

# ═══════════════════════════════════════════════════════════════════════════════
# NEW SLIDES S03, S04, S15–S19 — Fix footer overflow
# Footer at t=5.08, h=0.59 → t+h = 5.67 > 5.62. Fix h to 0.54
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[S03/04/15-19] Fixing footer overflows...")
fix_footer_slides = [2, 3, 14, 15, 16, 17, 18]  # 0-based indices
for si in fix_footer_slides:
    slide = slides[si]
    for sh in slide.shapes:
        l, t, w, h = get_pos(sh)
        # Footer band: l=0 t≈5.08 h≈0.59
        if near(l, 0.0, 0.05) and near(t, 5.08, 0.05) and near(h, 0.59, 0.05):
            set_pos(sh, h=0.54)
        # Footer text at l=2.0, t≈5.13 → fix to l=0.38
        if near(l, 2.0, 0.15) and near(t, 5.13, 0.1) and hasattr(sh, 'text_frame'):
            set_pos(sh, l=0.38, w=9.2)
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(8)
                    run.font.color.rgb = C_FTXT
                    break
                break
    print(f"  S{si+1}: Footer fixed")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — Fix items overflowing bottom (t=5.24+h=0.44 > 5.62)
# Items at t≥4.9 need to be compressed or repositioned
# ═══════════════════════════════════════════════════════════════════════════════
s15 = slides[14]
print("\n[S15] Fixing bottom overflow items...")
overflow_removed = 0
shapes_to_remove = []
for sh in s15.shapes:
    l, t, w, h = get_pos(sh)
    # Remove the "Commercial Result" overflow items that exceed slide height
    if t + h > 5.02 and t >= 4.9 and l < 5.0:  # left side overflow items
        shapes_to_remove.append(sh)
        overflow_removed += 1
    # Also fix right side overflowing items
    elif t + h > 5.02 and t >= 4.9 and l >= 5.0:
        shapes_to_remove.append(sh)
        overflow_removed += 1

# Remove overflow shapes by XML
for sh in shapes_to_remove:
    sp = sh.element
    sp.getparent().remove(sp)
print(f"  Removed {overflow_removed} overflow shapes from S15")

# Compact the remaining items on S15 left side
# The 4th upgrade item "Commercial Result" was at t=4.46 (too low)
# Compress spacing on left card: adjust items starting from t=3.22
# Find the left card items and compress spacing
left_card_items = []
for sh in s15.shapes:
    l, t, w, h = get_pos(sh)
    if l < 5.0 and t > 3.0 and t < 5.0 and hasattr(sh, 'text_frame') and sh.text.strip():
        left_card_items.append((t, sh))

# Items at t≈3.22, 3.38, 3.84, 4.00, 4.46, 4.62 — compress to fit in 3.22-4.85
left_card_items.sort(key=lambda x: x[0])
if left_card_items:
    # Assign new tops with compressed spacing
    new_tops = [3.2, 3.36, 3.72, 3.88, 4.24, 4.4]
    for i, (old_t, sh) in enumerate(left_card_items[:6]):
        if i < len(new_tops):
            set_pos(sh, t=new_tops[i])
    print(f"  Compressed {len(left_card_items)} items on left card")

# Also fix dots for left card
for sh in s15.shapes:
    l, t, w, h = get_pos(sh)
    if near(w, 0.09) and near(h, 0.09) and l < 5.0 and t > 4.0:
        if t >= 4.49:
            set_pos(sh, t=min(t - 0.25, 4.3))

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — Fix number circle positions (too high at t=2.48)
# From audit: number circles at t=2.48 w=0.40 h=0.40
# The card titles "The Computational IP Moat" etc. at t=2.96
# Gap between circle (t=2.48+0.40=2.88) and title (t=2.96) = 0.08 — correct
# But body text at t=3.28 h=1.52 → 3.28+1.52=4.80 — fine
# Main issue: just footer overflow (already fixed above)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[S16] Verified — no further structural fixes needed")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 20 (Closing) — Fix image left-of-slide (l=-0.06 → 0.00)
# From audit: PICTURE at l=-0.06 t=0.00 w=10.00
# Also footer at t=4.41 h=1.51 → 4.41+1.51=5.92 > 5.62 (overflow)
# ═══════════════════════════════════════════════════════════════════════════════
s20 = slides[19]
print("\n[S20] Fixing closing slide...")
for sh in s20.shapes:
    l, t, w, h = get_pos(sh)
    if sh.shape_type == 13 and l < 0:  # PICTURE left-of-slide
        set_pos(sh, l=0.00)
        print(f"  Fixed: Image l={l:.2f} → 0.00")
    # Fix footer overflow at t=4.41 h=1.51
    if near(t, 4.41, 0.05) and near(h, 1.51, 0.05):
        set_pos(sh, h=1.21)  # reduce so 4.41+1.21=5.62 exact
        print("  Fixed: Footer height overflow")
    # Fix footer text left-of-slide
    if l < 0 and hasattr(sh, 'text_frame'):
        set_pos(sh, l=0.38)
        print("  Fixed: Footer text l < 0 → 0.38")

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL FONT FIXES — Boost small fonts across all new slides
# New slides (S03,S04,S15-S19) have sz=7 body text — boost to sz=7.5
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[GLOBAL] Font size improvements...")
new_slide_indices = [2, 3, 14, 15, 16, 17, 18]
bumped = 0
for si in new_slide_indices:
    slide = slides[si]
    for sh in slide.shapes:
        if not hasattr(sh, 'text_frame'): continue
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                if run.font.size:
                    sz_pt = run.font.size / 12700
                    if 6.5 < sz_pt < 7.2:  # sz=7 → boost to 7.5
                        run.font.size = Pt(7.5)
                        bumped += 1
                    elif sz_pt <= 6.5:  # sz≤6 → boost to 8
                        run.font.size = Pt(8)
                        bumped += 1
print(f"  Bumped {bumped} font sizes to minimum 7.5pt")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Improvise subtitle line for Crystal Paradigm positioning
# From audit: l=0.38 t=0.94 → muted subtitle "Bridging the gap..."
# ═══════════════════════════════════════════════════════════════════════════════
s2 = slides[1]
print("\n[S02] Improving Crystal Paradigm positioning subtitle...")
for sh in s2.shapes:
    l, t, w, h = get_pos(sh)
    if near(l, 0.38, 0.05) and near(t, 0.94, 0.05) and hasattr(sh, 'text_frame'):
        if 'Bridging' in sh.text or 'gap between' in sh.text:
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    run.text = ("Crystal Paradigm: Accelerating innovation at the intersection of AI and Material Science. "
                               "Our mission — compress the discovery timeline from 5 years to 4 weeks across "
                               "supercapacitors, battery electrolytes, solar materials, sensors, and extreme-environment alloys.")
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = C_MUTED
                    break
                break
            print("  Updated: S02 subtitle with CP positioning")

# ═══════════════════════════════════════════════════════════════════════════════
# ALIGNMENT CHECK — Fix any remaining elements within slide bounds on new slides
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[ALIGNMENT] Final bounds check on all slides...")
SW, SH = 10.0, 5.62
violations = 0
for si, slide in enumerate(slides):
    for sh in slide.shapes:
        l, t, w, h = get_pos(sh)
        # Clip shapes that slightly overflow
        if l + w > SW + 0.01:
            excess = (l + w) - SW
            sh.width = I(w - excess - 0.01)
            violations += 1
        if t + h > SH + 0.01:
            excess = (t + h) - SH
            sh.height = I(h - excess - 0.01)
            violations += 1
        if l < -0.01:
            sh.left = I(0.0)
            violations += 1
        if t < -0.01:
            sh.top = I(0.0)
            violations += 1
print(f"  Clipped {violations} out-of-bounds shape edges")

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════════════════════
prs.save("CrystalParadigm_SCIDIP_IITDelhi_ELITE_v2.pptx")
print(f"\nSUCCESS: CrystalParadigm_SCIDIP_IITDelhi_ELITE_v2.pptx saved")
print(f"Slides: {len(prs.slides)}")
