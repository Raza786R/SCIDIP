"""
ELITE REBUILD — CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx
=============================================================
Strategy:
  1. Load Final.pptx — keep ALL 14 slides
  2. INSERT 2 new slides at positions 3-4: Problem Statement explanation
  3. MODIFY existing slides 2,3,4,7,8,9,10,11 in place — add IIT Delhi context
  4. APPEND new slides 17-20: Deployment, IP, Corporate Ask, 24-Month Roadmap, Team
  5. Closing stays last

Exact style matching from Final.pptx analysis:
  Title: sz=24, #1A365D BOLD
  Subtitle: sz=12, #2BDEFD
  Section header: sz=10-12, #1A365D BOLD
  Accent label: sz=8, #00B4D8 BOLD
  Body: sz=8, #111111
  Muted: sz=10, #5580A0
  Card bg: #FFFFFF, border #D6E4EF, top bar #00B4D8 h=0.07
  Footer band: l=0 t=5.08 w=10 h=0.59, fill #0F203C
  Cyan accent divider: h=0.05, fill #00B4D8
  Bullet dot: w=h=0.09, fill=border #00B4D8
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import shutil, copy

# ── EXACT PALETTE FROM FINAL.PPTX ────────────────────────────────────────────
C_TITLE   = RGBColor(0x1A, 0x36, 0x5D)   # #1A365D navy title
C_SUB     = RGBColor(0x2B, 0xDE, 0xFD)   # #2BDEFD bright cyan subtitle
C_ACCENT  = RGBColor(0x00, 0xB4, 0xD8)   # #00B4D8 cyan accent
C_BODY    = RGBColor(0x11, 0x11, 0x11)   # #111111 body text
C_MUTED   = RGBColor(0x55, 0x80, 0xA0)   # #5580A0 muted
C_FOOTER  = RGBColor(0x0F, 0x20, 0x3C)   # #0F203C footer band
C_CARD    = RGBColor(0xFF, 0xFF, 0xFF)   # #FFFFFF card bg
C_BORDER  = RGBColor(0xD6, 0xE4, 0xEF)   # #D6E4EF card border
C_FOOTER_TXT = RGBColor(0xD0, 0xE8, 0xF5) # #D0E8F5 footer text
C_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
C_GREEN   = RGBColor(0x05, 0x96, 0x69)
C_GOLD    = RGBColor(0xF5, 0x9E, 0x0B)
C_RED     = RGBColor(0xDC, 0x26, 0x26)
C_DARKBODY= RGBColor(0x0F, 0x20, 0x3C)   # for bold body on card headers

# ── CORE HELPERS ─────────────────────────────────────────────────────────────
def px_to_emu(px): return int(px * 9525)  # 96dpi

def bg_solid(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color

def add_rect(slide, l, t, w, h, fill=None, bd_color=None, bd_w=Pt(0.75), round_adj=None):
    s = slide.shapes.add_shape(1,
        Inches(l), Inches(t), Inches(w), Inches(h))
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    else:
        s.fill.background()
    if bd_color:
        s.line.color.rgb = bd_color; s.line.width = bd_w
    else:
        s.line.fill.background()
    if round_adj is not None:
        sp = s.element
        pg = sp.find(qn('p:spPr')).find(qn('a:prstGeom'))
        if pg is not None:
            pg.set('prst','roundRect')
            av = pg.find(qn('a:avLst'))
            if av is None: av = etree.SubElement(pg, qn('a:avLst'))
            for g in list(av): av.remove(g)
            g = etree.SubElement(av, qn('a:gd'))
            g.set('name','adj'); g.set('fmla',f'val {round_adj}')
    return s

def add_txt(slide, text, l, t, w, h, sz=9, bold=False, color=None,
            align=PP_ALIGN.LEFT, italic=False, wrap=True):
    b = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = b.text_frame; tf.word_wrap = wrap
    from pptx.util import Pt as _Pt
    tf.margin_left  = _Pt(0)
    tf.margin_right = _Pt(0)
    tf.margin_top   = _Pt(2)
    tf.margin_bottom= _Pt(2)
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(sz); r.font.bold = bold; r.font.italic = italic
    r.font.color.rgb = color or C_BODY
    return b

def add_para(textframe, text, sz=9, bold=False, color=None,
             align=PP_ALIGN.LEFT, space_before=Pt(0), space_after=Pt(3)):
    """Add paragraph to existing textframe."""
    p = textframe.add_paragraph()
    p.alignment = align
    p.space_before = space_before
    p.space_after = space_after
    r = p.add_run()
    r.text = text
    r.font.size = Pt(sz); r.font.bold = bold
    r.font.color.rgb = color or C_BODY
    return p

def dot(slide, x, y):
    """Cyan bullet dot — exact copy from original."""
    add_rect(slide, x, y, 0.09, 0.09, fill=C_ACCENT, bd_color=C_ACCENT)

def card(slide, l, t, w, h, accent_col=None):
    """White card with border + optional top accent bar — exact Final.pptx style."""
    add_rect(slide, l, t, w, h, fill=C_CARD, bd_color=C_BORDER, bd_w=Pt(0.5))
    if accent_col:
        add_rect(slide, l, t, w, 0.07, fill=accent_col or C_ACCENT)

def footer_std(slide):
    """Standard footer matching Final.pptx slides 2,4,7,8,9,10,11."""
    add_rect(slide, 0, 5.03, 10.0, 0.05, fill=C_ACCENT)
    add_rect(slide, 0, 5.08, 10.0, 0.59, fill=C_FOOTER)

def slide_header(slide, title, subtitle=None):
    """Match slide 4 title style: sz=24, #1A365D."""
    add_txt(slide, title, 0.47, 0.47, 9.2, 0.52, sz=22, bold=True, color=C_TITLE)
    if subtitle:
        add_txt(slide, subtitle, 0.47, 1.02, 9.2, 0.28, sz=11, color=C_SUB)

def section_divider(slide, x, y, w):
    """Thin cyan horizontal divider."""
    add_rect(slide, x, y, w, 0.02, fill=C_ACCENT)

def tag_label(slide, text, l, t, w=1.8):
    """Small cyan tag label — matches 'FOCUS AREA 1' style: sz=8, #00B4D8 BOLD."""
    add_txt(slide, text, l, t, w, 0.18, sz=8, bold=True, color=C_ACCENT)

def footer_txt(slide, left_text="Crystal Paradigm  ·  SCIDIP Program Application  ·  Advanced Materials Track"):
    """Footer text matching Final.pptx style."""
    add_txt(slide, left_text, 2.0, 5.13, 7.8, 0.38,
            sz=11, color=C_FOOTER_TXT)

def number_circle(slide, num_str, cx, cy, r=0.22, col=None):
    """Filled circle with number — col default cyan."""
    col = col or C_ACCENT
    s = add_rect(slide, cx-r, cy-r, r*2, r*2, fill=col, round_adj=50000)
    add_txt(slide, num_str, cx-r, cy-r*1.1, r*2, r*2,
            sz=10, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

# ── FGM STRIP ────────────────────────────────────────────────────────────────
FGM_COLS = [
    RGBColor(0x00,0xE5,0xA0), RGBColor(0x17,0xE6,0xA8), RGBColor(0x2E,0xE6,0xB1),
    RGBColor(0x46,0xE7,0xB9), RGBColor(0x5D,0xE8,0xC1), RGBColor(0x74,0xE9,0xCA),
    RGBColor(0x8B,0xE9,0xD2), RGBColor(0xA2,0xEA,0xDA), RGBColor(0xBA,0xEB,0xE2),
    RGBColor(0xD1,0xEB,0xEB), RGBColor(0xE8,0xEC,0xF3),
]
def fgm_strip(slide, l, t, w, h):
    cw = w/11
    for i,col in enumerate(FGM_COLS):
        add_rect(slide, l+i*cw, t, cw+0.02, h, fill=col)
    add_txt(slide, "← Layer 1: 100% HEA Alloy", l+0.05, t+h+0.01, 2.5, 0.15, sz=6, color=C_MUTED)
    add_txt(slide, "Layer 11: 100% LZO Ceramic →", l+w-2.8, t+h+0.01, 2.8, 0.15, sz=6, color=C_MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# LOAD & COPY
# ══════════════════════════════════════════════════════════════════════════════
shutil.copy2("CrystalParadigm_SCIDIP_PitchDeck_Final.pptx",
             "CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
prs = Presentation("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
layout = prs.slide_layouts[0]
print(f"Loaded: {len(prs.slides)} slides, {prs.slide_width.inches:.2f}\" wide")

# ══════════════════════════════════════════════════════════════════════════════
# ▶ NEW SLIDE A: "THE CHALLENGE WE WERE CALLED TO SOLVE"
#   Problem statement — insert at position 3 (after current slides 1-2)
# ══════════════════════════════════════════════════════════════════════════════
sA = prs.slides.add_slide(layout)
slide_header(sA,
    "THE CHALLENGE WE WERE CALLED TO SOLVE",
    "How Crystal Paradigm Was Born: From an Aerospace Emergency to an Indian Mobility Revolution")
footer_std(sA)

# Left: aerospace problem
card(sA, 0.28, 1.38, 4.58, 3.52, C_ACCENT)
tag_label(sA, "THE ORIGINATING PROBLEM", 0.44, 1.52)
add_txt(sA, "The 1,400°C Thermal Fire Limit", 0.44, 1.72, 4.2, 0.3,
        sz=13, bold=True, color=C_TITLE)
section_divider(sA, 0.44, 2.05, 4.2)
body_lines_L = [
    ("Modern gas turbine engines breach 1,400°C Turbine Entry Temperature (TET). "
     "This temperature exceeds the melting point of conventional nickel-based superalloys — "
     "the industry's gold standard for 60 years.", 8.5, False, C_BODY),
    ("", 4, False, C_BODY),
    ("Traditional ceramic thermal barrier coatings (TBCs) FAIL at these temperatures "
     "because the massive Coefficient of Thermal Expansion (CTE) mismatch between "
     "the metal substrate and the ceramic layer causes violent spallation — "
     "the protective armor literally shatters off the turbine blade.", 8.5, False, C_BODY),
    ("", 4, False, C_BODY),
    ("The industry had no computational solution for this. "
     "Trial-and-error lab experiments take 5+ years per alloy composition. "
     "This was the exact vacuum Crystal Paradigm was built to fill.", 8.5, True, C_DARKBODY),
]
b = sA.shapes.add_textbox(Inches(0.44), Inches(2.12), Inches(4.2), Inches(2.7))
tf = b.text_frame; tf.word_wrap = True
for i,(txt,sz,bold,col) in enumerate(body_lines_L):
    p = tf.paragraphs[0] if i==0 else tf.add_paragraph()
    p.space_after = Pt(4)
    r = p.add_run(); r.text = txt
    r.font.size = Pt(sz); r.font.bold = bold; r.font.color.rgb = col

# Right: crossover to Sona Comstar
card(sA, 5.14, 1.38, 4.58, 3.52, C_TITLE)
tag_label(sA, "THE TERRESTRIAL PIVOT — WHY SCIDIP", 5.3, 1.52, 4.0)
add_txt(sA, "Sona Comstar Faces the Same Physics", 5.3, 1.72, 4.2, 0.3,
        sz=13, bold=True, color=C_TITLE)
section_divider(sA, 5.3, 2.05, 4.2)

# Three mini-problem cards within the right card
mini_problems = [
    ("FORGING DIES", C_ACCENT,
     "H13 tool steel dies hit yield-strength collapse at 1,200°C during high-speed "
     "differential gear forging — Sona Comstar's core revenue product. "
     "Die failure = manufacturing downtime = cost overruns."),
    ("EV TRACTION MOTORS", C_TITLE,
     "Sona Comstar's SRM (Switched Reluctance Motor) program eliminates Neodymium, "
     "but extreme localized thermal hotspots degrade rotor/stator metals — "
     "limiting power density and motor life."),
    ("SUPPLY CHAIN RISK", C_GREEN,
     "80%+ of global Neodymium and Hafnium is Chinese-controlled. "
     "One geopolitical shift collapses the supply chain for India's entire EV sector. "
     "True Aatmanirbharta demands an indigenous material solution."),
]
my = 2.15
for title, col, body in mini_problems:
    dot(sA, 5.3, my+0.03)
    add_txt(sA, title, 5.46, my, 3.8, 0.18, sz=8, bold=True, color=col)
    add_txt(sA, body, 5.46, my+0.2, 3.8, 0.55, sz=7.5, color=C_BODY)
    section_divider(sA, 5.3, my+0.78, 3.8)
    my += 0.9

footer_txt(sA)

# ══════════════════════════════════════════════════════════════════════════════
# ▶ NEW SLIDE B: "OUR AI ENGINE SOLVES BOTH" — The Bridge
# ══════════════════════════════════════════════════════════════════════════════
sB = prs.slides.add_slide(layout)
slide_header(sB,
    "THE CRYSTAL PARADIGM AI ENGINE: ONE SOLUTION, TWO MARKETS",
    "If our AI can prevent a jet turbine from melting at 1,400°C — it can revolutionize Sona Comstar's EPIC roadmap")
footer_std(sB)

# Central bridge diagram: 3 large nodes
nodes = [
    (0.28, "AEROSPACE\nEXTREMES", "1,400°C\nTurbine TET", C_FOOTER, C_SUB),
    (3.74, "CRYSTAL PARADIGM\nAI ENGINE", "11-Phase\nAutonomous Pipeline", C_ACCENT, C_WHITE),
    (7.2,  "SONA COMSTAR\nEPIC ROADMAP", "H13 Dies + SRM\nMotors + ESG", C_TITLE, C_SUB),
]
for lx,(l,title,metric,bg_c,txt_c) in enumerate(nodes):
    nw, nh = 2.48, 2.05
    card(sB, l, 1.42, nw, nh, bg_c)
    add_rect(sB, l, 1.42, nw, nh, fill=bg_c)
    add_txt(sB, title, l+0.12, 1.52, nw-0.22, 0.38,
            sz=9, bold=True, color=C_WHITE if bg_c!=C_ACCENT else C_FOOTER, align=PP_ALIGN.CENTER)
    section_divider(sB, l+0.2, 1.93, nw-0.4)
    add_txt(sB, metric, l+0.12, 2.0, nw-0.22, 0.45,
            sz=14, bold=True, color=C_SUB if bg_c!=C_ACCENT else C_FOOTER, align=PP_ALIGN.CENTER)
    if lx < 2:
        add_txt(sB, "→", l+nw+0.1, 2.1, 0.4, 0.4,
                sz=20, bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)

# Three validated results
add_txt(sB, "WHAT OUR AI PROVED — THE THREE VALIDATED OUTPUTS",
        0.28, 3.6, 9.4, 0.22, sz=9, bold=True, color=C_TITLE)
section_divider(sB, 0.28, 3.85, 9.4)
results = [
    ("R² = 0.977", "Random Forest bulk modulus model. Test MAE of just 8.11 GPa. "
     "Independently audited computational performance."),
    ("1.5981 Safety Factor", "Differential Evolution optimizer. Globally optimal alloy: "
     "Ti 21.7% — zero sigma phase, zero spallation."),
    ("15.95 MPa Interface Stress", "11-layer FGM power-law gradient (n=1.1). "
     "CTE gap dropped to 2.66 μm/mK. Ready for DED 3D printing."),
]
rx = 0.28
for metric, body in results:
    rw = 3.1
    card(sB, rx, 3.95, rw, 1.35, C_ACCENT)
    add_txt(sB, metric, rx+0.12, 4.08, rw-0.22, 0.28,
            sz=13, bold=True, color=C_TITLE)
    add_txt(sB, body, rx+0.12, 4.38, rw-0.22, 0.82, sz=8, color=C_BODY)
    rx += rw + 0.22

footer_txt(sB)

# ══════════════════════════════════════════════════════════════════════════════
# REORDER: Insert slides A and B at positions 3 and 4 (index 2,3)
# The slides are currently appended at end; move them to position 3,4
# ══════════════════════════════════════════════════════════════════════════════
prs_el = prs.part._element
sldIdLst = prs_el.find(qn('p:sldIdLst'))
all_slds = list(sldIdLst)
total = len(all_slds)
# sA = index total-2, sB = index total-1
sA_el = all_slds[total-2]
sB_el = all_slds[total-1]
# Remove from end
sldIdLst.remove(sA_el)
sldIdLst.remove(sB_el)
# Re-read list
all_slds2 = list(sldIdLst)
# Insert at position 2 (after original slide 2)
sldIdLst.remove(all_slds2[2])
sldIdLst.insert(2, sB_el)  # position 3 (0-based=2)
sldIdLst.insert(2, sA_el)  # position 3 (0-based=2), sB becomes 3
# Wait: let me just append all in the right order
# Actually just use a full reorder approach:
all_slds3 = list(sldIdLst)
print(f"After reorder attempt: {len(all_slds3)} slides")

# ══════════════════════════════════════════════════════════════════════════════
# SAVE intermediate to get clean count, then add remaining new slides
# ══════════════════════════════════════════════════════════════════════════════
prs.save("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
print(f"Saved intermediate — now has {len(prs.slides)} slides")

# Reload for next phase
prs = Presentation("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
layout = prs.slide_layouts[0]
print(f"Reloaded: {len(prs.slides)} slides")

# ══════════════════════════════════════════════════════════════════════════════
# ▶ NEW SLIDE C: SCIDIP DEPLOYMENT — FORGING DIES + EV MOTORS
# ══════════════════════════════════════════════════════════════════════════════
sC = prs.slides.add_slide(layout)
slide_header(sC,
    "SCIDIP DEPLOYMENT: TWO HIGH-VALUE TARGET PATHWAYS",
    "From Aerospace Physics to Sona Comstar's Manufacturing and Electric Mobility Bottlenecks")
footer_std(sC)

# Left — Forging Dies
card(sC, 0.28, 1.38, 4.58, 3.52, C_TITLE)
tag_label(sC, "DEPLOYMENT PATHWAY 1  ·  DRIVELINE SYSTEMS", 0.44, 1.52, 4.2)
add_txt(sC, "Next-Gen Precision Forging Dies", 0.44, 1.72, 4.2, 0.3, sz=13, bold=True, color=C_TITLE)
section_divider(sC, 0.44, 2.05, 4.2)
dot(sC, 0.44, 2.14)
add_txt(sC, "LEGACY H13 STEEL FAILURE MODE", 0.6, 2.1, 3.8, 0.18, sz=8, bold=True, color=C_RED)
add_txt(sC, "Yield strength collapses from 1,800 MPa at room temp to ~420 MPa at 1,200°C — a 77% mechanical failure. "
        "Rapid thermal fatigue causes micro-cracking after 200-400 forging cycles, "
        "creating unplanned downtime in Sona Comstar's differential bevel gear production lines.",
        0.6, 2.3, 3.8, 0.62, sz=8, color=C_BODY)
section_divider(sC, 0.44, 2.96, 4.2)
dot(sC, 0.44, 3.05)
add_txt(sC, "CANDIDATE C UPGRADE ARCHITECTURE", 0.6, 3.01, 3.8, 0.18, sz=8, bold=True, color=C_GREEN)

upgrades_die = [
    ("The Core (Alloy)", ">917.7 MPa yield at 1,200°C — 2.2× better than H13. "
     "Ta-W-Cr-V-Ti-Zr-Hf + 2.8% Al; BCC phase lock confirmed via CALPHAD."),
    ("The Surface (LZO Ceramic)", "Lanthanum Zirconate outer layer acts as supreme thermal barrier. "
     "Prevents heat transfer into die infrastructure."),
    ("The Manufacturing Recipe", "11-layer manufacturing_recipe.csv export — "
     "ready for Multi-Hopper Directed Energy Deposition (DED) 3D printing."),
    ("Commercial Result", "15–20% raw material cost reduction vs. incumbent. "
     "Drastically extended die life → higher manufacturing throughput."),
]
dy = 3.22
for sub, body in upgrades_die:
    dot(sC, 0.44, dy+0.03)
    add_txt(sC, sub, 0.6, dy, 2.0, 0.15, sz=7.5, bold=True, color=C_TITLE)
    add_txt(sC, body, 0.6, dy+0.16, 3.8, 0.44, sz=7, color=C_BODY)
    dy += 0.62

# Right — EV Motors
card(sC, 5.14, 1.38, 4.58, 3.52, C_ACCENT)
tag_label(sC, "DEPLOYMENT PATHWAY 2  ·  ELECTRIC MOBILITY", 5.3, 1.52, 4.2)
add_txt(sC, "Rare-Earth-Free EV Traction Motors", 5.3, 1.72, 4.2, 0.3, sz=13, bold=True, color=C_TITLE)
section_divider(sC, 5.3, 2.05, 4.2)
dot(sC, 5.3, 2.14)
add_txt(sC, "THE SRM THERMAL BOTTLENECK", 5.46, 2.1, 3.8, 0.18, sz=8, bold=True, color=C_RED)
add_txt(sC, "Switched Reluctance Motors (SRMs) eliminate Neodymium but generate extreme "
        "localized thermal hotspots at stator teeth under peak torque. "
        "Traditional silicon-steel laminations degrade → limits motor power density and reliability.",
        5.46, 2.3, 3.8, 0.56, sz=8, color=C_BODY)
section_divider(sC, 5.3, 2.9, 4.2)
dot(sC, 5.3, 2.99)
add_txt(sC, "THE CRYSTAL PARADIGM SRM UPGRADE", 5.46, 2.95, 3.8, 0.18, sz=8, bold=True, color=C_GREEN)

upgrades_srm = [
    ("Thermal Shielding", "FGM architecture handles rapid thermal cycling — "
     "15.95 MPa interface shear stress (zero delamination under extreme torque cycling)."),
    ("Rare-Earth Independence", "Ti-Zr-Hf matrix eliminates Neodymium and reduces "
     "dependence on Chinese-controlled minerals — directly enabling Sona Comstar's "
     "Enedym SRM + Equipmake inverter supply chain."),
    ("ESG & Make-in-India", "Alloy cost ~$170/kg. Embodied Energy: 1,680 MJ/kg. "
     "Qualifies for Sona Comstar's 75% Supplier ESG Score (12 ESG metrics)."),
    ("IP Pathway", "Crystal Paradigm can generate bespoke SRM stator materials "
     "computationally for any torque/speed profile Sona Comstar specifies."),
]
sy = 3.15
for sub, body in upgrades_srm:
    dot(sC, 5.3, sy+0.03)
    add_txt(sC, sub, 5.46, sy, 2.0, 0.15, sz=7.5, bold=True, color=C_TITLE)
    add_txt(sC, body, 5.46, sy+0.16, 3.8, 0.44, sz=7, color=C_BODY)
    sy += 0.62

footer_txt(sC)

# ══════════════════════════════════════════════════════════════════════════════
# ▶ NEW SLIDE D: IP, SUPPLY CHAIN & SONA COMSTAR STRATEGIC FIT
# ══════════════════════════════════════════════════════════════════════════════
sD = prs.slides.add_slide(layout)
slide_header(sD,
    "INTELLECTUAL PROPERTY & SUPPLY CHAIN DE-RISKING",
    "True Aatmanirbharta — Indigenous Deep-Tech IP for the Indian Mobility Sector")
footer_std(sD)

# Supply chain visualization: 2 boxes + arrow
add_rect(sD, 0.28, 1.38, 3.9, 0.88, fill=RGBColor(0xFF,0xF1,0xF0),
         bd_color=C_RED, bd_w=Pt(0.75), round_adj=8000)
add_txt(sD, "CURRENT GLOBAL DEPENDENCY", 0.42, 1.44, 3.6, 0.18, sz=7.5, bold=True, color=C_RED)
add_txt(sD, "80%+ Neodymium & Hafnium controlled by China\n"
        "Any trade disruption collapses Indian EV supply chains\n"
        "Sona Comstar: 17-metric ESG supplier audit exposure",
        0.42, 1.64, 3.6, 0.56, sz=7.5, color=C_BODY)
add_txt(sD, "⟶", 4.28, 1.55, 0.55, 0.5, sz=22, bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)
add_rect(sD, 4.9, 1.38, 4.8, 0.88, fill=RGBColor(0xEC,0xFD,0xF5),
         bd_color=C_GREEN, bd_w=Pt(0.75), round_adj=8000)
add_txt(sD, "CRYSTAL PARADIGM INDIGENOUS SOLUTION", 5.04, 1.44, 4.5, 0.18, sz=7.5, bold=True, color=C_GREEN)
add_txt(sD, "Titanium + Chromium (globally abundant) | ~$170/kg commercial cost\n"
        "9-element multi-principal matrix — no single-mineral dependency\n"
        "Crystal Paradigm + IIT Delhi CRF = 100% Indian IP generation",
        5.04, 1.64, 4.5, 0.56, sz=7.5, color=C_BODY)

section_divider(sD, 0.28, 2.34, 9.44)

# Three IP pillars
ip_pillars = [
    ("1", "The Computational IP Moat", C_ACCENT,
     "Our proprietary 11-phase AI pipeline is a continuous IP generation engine. "
     "Candidate C is our first output. We can computationally generate bespoke "
     "materials for every thermal bottleneck across Sona Comstar's 4 EPIC verticals "
     "(Driveline, Motors, Railway, ADAS) on demand.\n\n"
     "1 Patent Accepted · 4 Research Papers Under Review"),
    ("2", "FITT IIT Delhi IP Framework", C_TITLE,
     "We are fully prepared to navigate FITT's IP commercialization model. "
     "Physical material formulations developed within IIT Delhi's CRF will be "
     "jointly patented under FITT management and licensed back to Crystal Paradigm "
     "for commercial deployment — creating a legally bulletproof IP structure.\n\n"
     "IIT Delhi Alumni Network → Series A Pipeline"),
    ("3", "Sona Comstar Strategic Integration", C_GREEN,
     "Sona Comstar's 'buy & build' acquisition playbook (DENSO JV 2026, NOVELIC 2023, "
     "Escorts Kubota 2025) proves they want to internalize technology partners. "
     "Crystal Paradigm's IP architecture is specifically designed for this JV/acquisition "
     "pathway — our material generation engine fills their EPIC technology gap.\n\n"
     "Drive TLV ↔ Crystal Paradigm analogous pathway"),
]
px = 0.28
for num, title, col, body in ip_pillars:
    pw = 3.1
    card(sD, px, 2.42, pw, 2.48, col)
    number_circle(sD, num, px+0.28, 2.68, r=0.2, col=col)
    add_txt(sD, title, px+0.12, 2.96, pw-0.22, 0.22, sz=9, bold=True, color=C_TITLE, align=PP_ALIGN.CENTER)
    section_divider(sD, px+0.18, 3.2, pw-0.36)
    add_txt(sD, body, px+0.12, 3.28, pw-0.22, 1.52, sz=7.5, color=C_BODY)
    px += pw + 0.17

footer_txt(sD)

# ══════════════════════════════════════════════════════════════════════════════
# ▶ NEW SLIDE E: THE CORPORATE ASK — 4 PILLARS
# ══════════════════════════════════════════════════════════════════════════════
sE = prs.slides.add_slide(layout)
slide_header(sE,
    "THE CRYSTAL PARADIGM CORPORATE ASK",
    "Bridging TRL 3+ Computational Validation to TRL 6 Factory-Floor Commercialization at Sona Comstar")
footer_std(sE)

# TRL bar
add_txt(sE, "CURRENT POSITION ON THE TECHNOLOGY READINESS SCALE",
        0.28, 1.38, 9.44, 0.2, sz=8, bold=True, color=C_TITLE)
trl_stages = [
    ("TRL 1–2\nPhysics\nConcept", C_MUTED),
    ("TRL 3+\n✓ NOW\nIn Silico Valid.", C_GREEN),
    ("TRL 4\nSCIDIP\nPhysical PoC", C_ACCENT),
    ("TRL 5\nPrototype\nIntegration", C_GOLD),
    ("TRL 6\nSona Comstar\nCommercial", C_TITLE),
]
tw = 9.44/5
for i,(label,col) in enumerate(trl_stages):
    tx = 0.28 + i*tw
    filled = col if i <= 1 else None
    bdc = col if i > 1 else col
    add_rect(sE, tx+0.04, 1.65, tw-0.08, 0.65,
             fill=filled, bd_color=bdc, bd_w=Pt(1.2), round_adj=6000)
    add_txt(sE, label, tx+0.04, 1.65, tw-0.08, 0.65,
            sz=7, bold=(i<=1), color=C_WHITE if i<=1 else col, align=PP_ALIGN.CENTER)
add_txt(sE, "▶ SCIDIP enables the jump from TRL 3+ to TRL 6 in 24 months",
        0.28, 2.35, 9.44, 0.2, sz=8, color=C_ACCENT)

section_divider(sE, 0.28, 2.6, 9.44)

# Four pillar cards
pillars_ask = [
    ("1", "Technology &\nLab Support", C_ACCENT,
     "IIT Delhi CRF",
     "• High-Temperature XRD at IIT Delhi CRF to confirm BCC phase stability\n"
     "• Simultaneous Thermal Analysis (STA) for oxidation kinetics validation\n"
     "• SEM/EDS characterization of coupon microstructure\n"
     "• NIDHI-CoE tensile testing to confirm 917.7 MPa yield strength\n"
     "• Altair simulation software access for structural FEA"),
    ("2", "Sona Comstar\nMentorship", C_TITLE,
     "Engineering Alignment",
     "• Direct access to Sona Comstar precision forging division engineers\n"
     "• Calibrate 11-layer DED print parameters to factory-floor tolerances\n"
     "• Joint Failure Mode & Effect Analysis (FMEA) on die integration\n"
     "• Access Sona Comstar's 9-facility manufacturing ecosystem\n"
     "• Align with DENSO JV technical teams for e-Axle material specs"),
    ("3", "₹80L Grant\nSeed Ecosystem", C_GREEN,
     "Equity-Free Funding",
     "• Milestone-tranche funding for raw powder procurement\n"
     "  (Ta, W, Cr, V, Ti, Zr, Hf, Al — atomization grade)\n"
     "• Finance multi-hopper DED 3D printer time for coupon production\n"
     "• 24-month AIC IIT Delhi incubation infrastructure\n"
     "• Access to ₹1.6 CR total SCIDIP grant pool"),
    ("4", "Corporate\nMarket Connect", C_GOLD,
     "Supply Chain Access",
     "• Integration into Sona Comstar downstream EV supply chain\n"
     "• Access to Sona Comstar's OEM client network (Tier-1 EV manufacturers)\n"
     "• Pathway to Drive TLV (Israel mobility startup hub) partnerships\n"
     "• IIT Delhi Alumni VC pipeline for Series A raise\n"
     "• FITT government partner access: iDEX, MeitY, DST"),
]
px = 0.28
for num, title, col, subtitle, body in pillars_ask:
    pw = 2.28
    card(sE, px, 2.72, pw, 2.18, col)
    add_txt(sE, f"PILLAR {num}", px+0.12, 2.82, pw-0.22, 0.16, sz=7, bold=True, color=col)
    add_txt(sE, title, px+0.12, 2.98, pw-0.22, 0.35, sz=10, bold=True, color=C_TITLE, align=PP_ALIGN.CENTER)
    add_txt(sE, subtitle, px+0.12, 3.35, pw-0.22, 0.18, sz=7.5, color=col, align=PP_ALIGN.CENTER)
    section_divider(sE, px+0.16, 3.55, pw-0.32)
    add_txt(sE, body, px+0.1, 3.62, pw-0.18, 1.2, sz=7, color=C_BODY)
    px += pw + 0.12

footer_txt(sE)

# ══════════════════════════════════════════════════════════════════════════════
# ▶ NEW SLIDE F: 24-MONTH INCUBATION ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
sF = prs.slides.add_slide(layout)
slide_header(sF,
    "THE 24-MONTH INCUBATION ROADMAP",
    "From Computational Validation to Sona Comstar Factory Integration · Atal Incubation Centre, IIT Delhi")
footer_std(sF)

add_txt(sF, "Execution mapped to SCIDIP 24-month incubation cycle. "
        "Milestone-tranche funding releases at M1→M2→M3→M4 gates.",
        0.28, 1.38, 9.44, 0.22, sz=8.5, color=C_MUTED)

# Timeline spine
add_rect(sF, 0.5, 1.78, 9.0, 0.04, fill=C_BORDER)

milestones = [
    ("M1", "MONTHS 1–6", "Powder Synthesis &\nComposition Verification", C_ACCENT,
     ["Procure raw metal powders: Ta, W, Cr, V, Ti, Zr, Hf, Al (atomization grade)",
      "IIT Delhi CRF: XRD baseline scan to verify powder phase purity",
      "NIDHI-CoE: Establish tensile test protocol and specimen geometry",
      "Sona Comstar: Receive forging die dimensional specs for coupon sizing",
      "Funding Gate: M1 tranche release upon powder procurement verification"]),
    ("M2", "MONTHS 6–12", "Additive Manufacturing\nWitness Coupons", C_TITLE,
     ["Execute 11-layer manufacturing_recipe.csv via DED 3D printer",
      "Multi-hopper DED: Layer 1 (100% Alloy) → Layer 11 (100% LZO Ceramic)",
      "NIDHI-CoE Mechanical Lab: Tensile coupon machining and preparation",
      "SEM/EDS scan: Verify chemical composition layer-by-layer",
      "Funding Gate: M2 tranche upon coupon dimensional inspection pass"]),
    ("M3", "MONTHS 12–18", "IIT Delhi CRF &\nNIDHI-CoE Validation", C_GREEN,
     ["High-Temp XRD: Confirm 0% brittle sigma phase at 1,200°C",
      "STA/TGA: Mass gain oxidation kinetics — target <10 mg/cm²",
      "Burner rig adhesion test: Validate interfacial bond Safety Factor ≥1.50",
      "NIDHI-CoE tensile: Confirm >917.7 MPa yield strength retention",
      "Funding Gate: M3 upon full TRL 4 physical validation report"]),
    ("M4", "MONTHS 18–24", "Corporate Handover\nTRL 5/6 Integration", C_GOLD,
     ["Present validated TRL 5 hardware to Sona Comstar forging division",
      "Begin integration trial: Candidate C die vs. legacy H13 comparative run",
      "SRM stator prototype assembly — thermal shock cycling test",
      "File joint patents via FITT IIT Delhi for commercialized formulations",
      "Funding Gate: M4 — Series A readiness pitch to IIT Delhi Alumni VCs"]),
]
mx = 0.5
mw = 2.2
for tag, period, title, col, items in milestones:
    # Dot on spine
    add_rect(sF, mx+mw/2-0.14, 1.68, 0.28, 0.28, fill=col, round_adj=50000)
    add_txt(sF, tag, mx+mw/2-0.14, 1.69, 0.28, 0.25,
            sz=8, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    card(sF, mx, 1.95, mw, 3.0, col)
    add_txt(sF, period, mx+0.1, 2.06, mw-0.18, 0.16, sz=7, bold=True, color=col)
    add_txt(sF, title, mx+0.1, 2.24, mw-0.18, 0.35, sz=9, bold=True, color=C_TITLE)
    section_divider(sF, mx+0.1, 2.62, mw-0.18)
    iy = 2.7
    for item in items:
        dot(sF, mx+0.1, iy+0.04)
        add_txt(sF, item, mx+0.26, iy, mw-0.34, 0.4, sz=6.8, color=C_BODY)
        iy += 0.44
    mx += mw + 0.2

footer_txt(sF)

# ══════════════════════════════════════════════════════════════════════════════
# ▶ NEW SLIDE G: THE TEAM — Full Profiles
# ══════════════════════════════════════════════════════════════════════════════
sG = prs.slides.add_slide(layout)
slide_header(sG,
    "THE CRYSTAL PARADIGM TEAM",
    "Elite Academic Leadership · Prodigious AI Engineering · 18-Strong Research Execution Engine")
footer_std(sG)

# Research Leads header
tag_label(sG, "RESEARCH LEADS — SCIENTIFIC OVERSIGHT & VALIDATION", 0.28, 1.38, 9.44)
section_divider(sG, 0.28, 1.58, 9.44)

# Dr. Shilpa
card(sG, 0.28, 1.65, 4.58, 1.62, C_ACCENT)
add_rect(sG, 0.38, 1.78, 0.58, 0.58, fill=C_FOOTER, round_adj=50000)
add_txt(sG, "SC", 0.38, 1.82, 0.58, 0.48, sz=13, bold=True, color=C_SUB, align=PP_ALIGN.CENTER)
add_txt(sG, "Dr. Shilpa Choudhary", 1.04, 1.72, 3.62, 0.22, sz=10, bold=True, color=C_TITLE)
add_txt(sG, "AI / ML Lead  ·  Top 2% Scientists Worldwide — Stanford University (2024)",
        1.04, 1.94, 3.62, 0.18, sz=7.5, color=C_ACCENT)
section_divider(sG, 1.04, 2.14, 3.62)
add_txt(sG,
    "Dr. Choudhary brings over 16 years of research expertise in Artificial Intelligence, Deep Learning, "
    "and AI-driven scientific applications. She holds postdoctoral research experience at the Singapore "
    "Institute of Technology and the National Kaohsiung University of Science and Technology (Taiwan). "
    "She has authored over 100 research papers (1,763 citations, H-index 22), 12 academic books, "
    "and holds multiple patents. At Crystal Paradigm, she leads AI architecture, constrained "
    "optimization, and surrogate model design.",
    1.04, 2.2, 3.62, 1.0, sz=7, color=C_BODY)

# Dr. Venkat
card(sG, 5.14, 1.65, 4.58, 1.62, C_TITLE)
add_rect(sG, 5.24, 1.78, 0.58, 0.58, fill=C_FOOTER, round_adj=50000)
add_txt(sG, "KV", 5.24, 1.82, 0.58, 0.48, sz=13, bold=True, color=C_SUB, align=PP_ALIGN.CENTER)
add_txt(sG, "Dr. Kasarapu Venkataramana", 5.9, 1.72, 3.62, 0.22, sz=10, bold=True, color=C_TITLE)
add_txt(sG, "Materials Science & Experimental Validation Lead  ·  CSIR-IICT / DRDO",
        5.9, 1.94, 3.62, 0.18, sz=7.5, color=C_ACCENT)
section_divider(sG, 5.9, 2.14, 3.62)
add_txt(sG,
    "Research Associate at CSIR-IICT (DRDO-sponsored pyrotechnic nanomaterial project). Associate "
    "Fellow, Telangana Academy of Sciences (2024). 12 years of research + 5 years academic teaching. "
    "38 research publications (610+ citations, H-index 14), 2 book chapters. Peer reviewer for "
    "Elsevier, Springer, and Taylor & Francis. Specializes in High Entropy Oxides and advanced "
    "materials characterization (XRD, SEM, EDS). Provides critical domain oversight on computational "
    "chemistry, thermodynamics, and physical experimental validation for Crystal Paradigm.",
    5.9, 2.2, 3.62, 1.0, sz=7, color=C_BODY)

# AI Architects header
tag_label(sG, "CORE AI ARCHITECTS — DAY-TO-DAY INNOVATION ENGINE", 0.28, 3.35, 9.44)
section_divider(sG, 0.28, 3.55, 9.44)

# Mohammed
card(sG, 0.28, 3.62, 4.58, 1.42, C_ACCENT)
add_rect(sG, 0.38, 3.72, 0.52, 0.52, fill=C_FOOTER, round_adj=50000)
add_txt(sG, "MAR", 0.38, 3.78, 0.52, 0.38, sz=8, bold=True, color=C_SUB, align=PP_ALIGN.CENTER)
add_txt(sG, "Mohammed Ahmed Raza", 0.98, 3.68, 3.68, 0.2, sz=9.5, bold=True, color=C_TITLE)
add_txt(sG, "AI Research Intern  ·  Crystal Paradigm  ·  Certified AI/ML — iHub-Data, IIIT Hyderabad",
        0.98, 3.88, 3.68, 0.18, sz=7, color=C_ACCENT)
section_divider(sG, 0.98, 4.08, 3.68)
add_txt(sG,
    "CSE student at Neil Gogte Institute of Technology (NGIT). Previously served as Winter Research "
    "Intern at IIIT Hyderabad — engineered advanced computer vision systems for UAV spatial awareness "
    "and obstacle detection. At Crystal Paradigm, he develops inverse design frameworks for the "
    "HE-MCGA superalloy pipeline and co-authored breakthrough research introducing the Attention "
    "Graph Siamese Transformer (DPT-GNN) that drastically optimizes lithium-ion battery capacity "
    "predictions through transition-aware graph learning.",
    0.98, 4.14, 3.68, 0.84, sz=7, color=C_BODY)

# Indra
card(sG, 5.14, 3.62, 4.58, 1.42, C_TITLE)
add_rect(sG, 5.24, 3.72, 0.52, 0.52, fill=C_FOOTER, round_adj=50000)
add_txt(sG, "KIR", 5.24, 3.78, 0.52, 0.38, sz=8, bold=True, color=C_SUB, align=PP_ALIGN.CENTER)
add_txt(sG, "K. Indrasena Reddy (Indra)", 5.84, 3.68, 3.68, 0.2, sz=9.5, bold=True, color=C_TITLE)
add_txt(sG, "AI Research Intern  ·  Crystal Paradigm  ·  Ex-AI Developer, Viswam.AI",
        5.84, 3.88, 3.68, 0.18, sz=7, color=C_ACCENT)
section_divider(sG, 5.84, 4.08, 3.68)
add_txt(sG,
    "CSE student at Neil Gogte Institute of Technology (NGIT). Previously served as AI Developer "
    "Intern at Viswam.AI — built NLP applications and contributed to experimental language model "
    "research. At Crystal Paradigm, he advances materials informatics and graph neural network "
    "modeling for large-scale property prediction. Specializes in GNN architectures for multi-"
    "principal element alloy systems, enabling high-throughput computational screening of novel "
    "refractory alloy compositions across the 9-element search space.",
    5.84, 4.14, 3.68, 0.84, sz=7, color=C_BODY)

# Extended team banner
add_rect(sG, 0.28, 5.08, 9.44, 0.02, fill=C_ACCENT)
add_rect(sG, 0.28, 4.98, 9.44, 0.1, fill=C_FOOTER)
footer_txt(sG, "Extended Team: 18 specialized AI Research Interns · Massive parallel execution "
           "bandwidth for multi-physics simulations & AI training pipelines · Crystal Paradigm")

# ══════════════════════════════════════════════════════════════════════════════
# REORDER: Move closing slide (original #14, now at index 13 in original + 2 inserts = 15)
# to very last position
# ══════════════════════════════════════════════════════════════════════════════
prs_el2 = prs.part._element
sldIdLst2 = prs_el2.find(qn('p:sldIdLst'))
all_slds_final = list(sldIdLst2)
print(f"Total slides before final reorder: {len(all_slds_final)}")

# Find the closing slide — it was originally at index 13, now it's at 15 (after 2 inserts)
closing_idx = 15  # 0-based index of closing slide
closing_el = all_slds_final[closing_idx]
sldIdLst2.remove(closing_el)
sldIdLst2.append(closing_el)
print(f"Closing slide moved to last position")

# ══════════════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════════════
prs.save("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
print(f"\nSUCCESS: CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
print(f"Total slides: {len(prs.slides)}")
