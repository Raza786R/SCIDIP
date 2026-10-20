"""
CRYSTAL PARADIGM — ELITE HYBRID v2
====================================
Theme: Light (Final.pptx reference)
  BG:      #F5F7FA (almost white, slight cool tint)
  Cards:   #FFFFFF with #E8EEF6 border
  Header:  #0F203C (deep navy — from Final)
  Accent:  #00B4D8 (cyan — from Final)
  Teal:    #00C896 (slightly richer teal accent)
  Gold:    #F5A623
  Text:    #1A2B4A (dark navy for body)
  Muted:   #64748B

Elements: Faithfully ported from (by claude):
  - Gradient FGM color strip (slides 2, 9)
  - 4-param gating mini-card grid (slide 5)
  - Numbered constraint rows with penalty badge (slide 7)
  - Big metric boxes (slide 6)
  - Milestone dots on timeline (slide 15)
  - 3-card bottom row layout (slides 4, 11, 13)
  - 2-column comparison (slides 2, 6, 11, 12, 16, 17)
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import os

# ── PALETTE ──────────────────────────────────────────────────────────────────
BG          = RGBColor(0xF5, 0xF7, 0xFA)   # slide background — near white
CARD_BG     = RGBColor(0xFF, 0xFF, 0xFF)   # card fill — pure white
CARD_BD     = RGBColor(0xD0, 0xDC, 0xF0)   # card border — periwinkle
HEADER_BAND = RGBColor(0x0F, 0x20, 0x3C)   # top header band — deep navy (Final ref)
NAVY        = RGBColor(0x1A, 0x36, 0x5D)   # headings
CYAN        = RGBColor(0x00, 0xB4, 0xD8)   # primary accent (Final ref)
TEAL        = RGBColor(0x00, 0xC8, 0x96)   # secondary teal
GOLD        = RGBColor(0xF5, 0xA6, 0x23)   # highlights / warnings
RED_SOFT    = RGBColor(0xE5, 0x50, 0x50)   # problem / danger
GREEN       = RGBColor(0x05, 0x96, 0x69)   # verified / positive
YELLOW_ST   = RGBColor(0xF5, 0x9E, 0x0B)   # pending
TEXT        = RGBColor(0x1A, 0x2B, 0x4A)   # primary body text (dark navy)
MUTED       = RGBColor(0x55, 0x70, 0x90)   # secondary text
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
BLACK       = RGBColor(0x11, 0x11, 0x11)

# FGM gradient strip — 11 steps from teal to near-white (by claude ref)
FGM_COLS = [
    RGBColor(0x00, 0xE5, 0xA0),
    RGBColor(0x17, 0xE6, 0xA8),
    RGBColor(0x2E, 0xE6, 0xB1),
    RGBColor(0x46, 0xE7, 0xB9),
    RGBColor(0x5D, 0xE8, 0xC1),
    RGBColor(0x74, 0xE9, 0xCA),
    RGBColor(0x8B, 0xE9, 0xD2),
    RGBColor(0xA2, 0xEA, 0xDA),
    RGBColor(0xBA, 0xEB, 0xE2),
    RGBColor(0xD1, 0xEB, 0xEB),
    RGBColor(0xE8, 0xEC, 0xF3),
]

W = Inches(13.33)
H = Inches(7.50)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def new_prs():
    p = Presentation()
    p.slide_width = W
    p.slide_height = H
    return p

def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def bg(slide, color=None):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color or BG

def rect(slide, l, t, w, h, fill=None, bd=None, bw=Pt(0.75), rnd=None):
    s = slide.shapes.add_shape(1,
        Inches(l), Inches(t), Inches(w), Inches(h))
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    else:
        s.fill.background()
    if bd:
        s.line.color.rgb = bd; s.line.width = bw
    else:
        s.line.fill.background()
    if rnd:
        sp = s.element
        pg = sp.find(qn('p:spPr')).find(qn('a:prstGeom'))
        if pg is not None:
            pg.set('prst','roundRect')
            av = pg.find(qn('a:avLst'))
            if av is None: av = etree.SubElement(pg, qn('a:avLst'))
            for g in av.findall(qn('a:gd')): av.remove(g)
            g = etree.SubElement(av, qn('a:gd'))
            g.set('name','adj'); g.set('fmla',f'val {rnd}')
    return s

def txt(slide, text, l, t, w, h, sz=11, bold=False, color=None,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    b = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = b.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = Pt(sz); r.font.bold = bold; r.font.italic = italic
    r.font.color.rgb = color or TEXT
    return b

def hdr_band(slide):
    """Top navy header band — matches Final.pptx style."""
    rect(slide, 0, 0, 13.33, 1.22, fill=HEADER_BAND)
    rect(slide, 0, 1.22, 13.33, 0.06, fill=CYAN)

def slide_tag(slide, tag, num, total=18):
    """Label + slide counter in header."""
    txt(slide, tag, 0.5, 0.18, 10, 0.3, sz=9, bold=True, color=CYAN)
    txt(slide, f"{num} / {total}", 12.1, 0.18, 1.1, 0.3,
        sz=9, color=RGBColor(0x8B,0xBF,0xD8), align=PP_ALIGN.RIGHT)

def title_block(slide, main, sub=None):
    """White title + sub in header band."""
    txt(slide, main, 0.5, 0.5, 12.0, 0.55, sz=22, bold=True, color=WHITE)
    if sub:
        txt(slide, sub, 0.5, 0.93, 12.0, 0.3, sz=12, color=CYAN)

def logo_footer(slide):
    """Logo text + subtle footer line."""
    rect(slide, 0, 7.2, 13.33, 0.04, fill=CARD_BD)
    txt(slide, "CRYSTAL PARADIGM", 0.4, 7.25, 3.0, 0.22,
        sz=8, bold=True, color=CYAN)

def card(slide, l, t, w, h, accent_col=None):
    """White rounded card with optional left accent bar."""
    rect(slide, l, t, w, h, fill=CARD_BG, bd=CARD_BD, bw=Pt(0.75), rnd=18000)
    if accent_col:
        rect(slide, l, t, 0.06, h, fill=accent_col, rnd=18000)
    return (l+0.18, t+0.15)  # inner content start

def metric_box(slide, l, t, w, h, val, lbl, col=None):
    """Big number + small label — from by claude slide 6."""
    c = col or CYAN
    rect(slide, l, t, w, h, fill=CARD_BG, bd=c, bw=Pt(1.0), rnd=18000)
    txt(slide, val, l+0.08, t+0.08, w-0.16, h*0.55,
        sz=22, bold=True, color=c, align=PP_ALIGN.CENTER)
    txt(slide, lbl, l+0.08, t+h*0.58, w-0.16, h*0.35,
        sz=8, color=MUTED, align=PP_ALIGN.CENTER)

def fgm_strip(slide, l, t, w, h):
    """11-color FGM gradient strip — from by claude slides 2 & 9."""
    cw = w / 11
    for i, col in enumerate(FGM_COLS):
        rect(slide, l + i*cw, t, cw, h, fill=col)

def num_row(slide, l, t, num, heading, body, penalty=None, pcol=None):
    """Numbered constraint row — from by claude slide 7."""
    # Green teal number circle
    rect(slide, l, t+0.04, 0.36, 0.36, fill=TEAL, rnd=50000)
    txt(slide, str(num), l, t+0.05, 0.36, 0.3,
        sz=12, bold=True, color=HEADER_BAND, align=PP_ALIGN.CENTER)
    txt(slide, heading, l+0.44, t+0.05, 4.8, 0.25,
        sz=11, bold=True, color=TEXT)
    txt(slide, body, l+0.44, t+0.32, 5.0, 0.28,
        sz=9, color=MUTED)
    if penalty:
        pc = pcol or GOLD
        rect(slide, l+5.55, t+0.04, 1.3, 0.36, fill=RGBColor(0xFF,0xF3,0xD0),
             bd=pc, bw=Pt(0.75), rnd=12000)
        txt(slide, penalty, l+5.55, t+0.06, 1.3, 0.3,
            sz=10, bold=True, color=pc, align=PP_ALIGN.CENTER)

def milestone_col(slide, l, t, tag, period, title, body, col):
    """Milestone column card — from by claude slide 15."""
    cw = 2.95
    # Timeline node dot
    nx = l + cw/2 - 0.2
    rect(slide, nx, t-0.24, 0.4, 0.4, fill=col, rnd=50000)
    txt(slide, tag, nx, t-0.23, 0.4, 0.32,
        sz=10, bold=True, color=HEADER_BAND, align=PP_ALIGN.CENTER)
    # Card
    rect(slide, l+0.05, t, cw-0.1, 4.5, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=18000)
    rect(slide, l+0.05, t, cw-0.1, 0.06, fill=col, rnd=18000)
    txt(slide, period, l+0.2, t+0.12, cw-0.35, 0.24,
        sz=8, bold=True, color=col)
    txt(slide, title, l+0.2, t+0.4, cw-0.35, 0.42,
        sz=13, bold=True, color=TEXT)
    rect(slide, l+0.2, t+0.88, cw-0.5, 0.04, fill=CARD_BD)
    txt(slide, body, l+0.2, t+1.0, cw-0.35, 3.3,
        sz=9.5, color=MUTED)

# ─────────────────────────────────────────────────────────────────────────────
# BUILD SLIDES
# ─────────────────────────────────────────────────────────────────────────────
prs = new_prs()

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title (by claude layout + light theme)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)

# Left half: navy background panel (like by claude's circular elements concept
# but clean rectangular, from Final's professional style)
rect(s, 0, 0, 6.5, 7.5, fill=HEADER_BAND)
rect(s, 6.5, 0, 0.06, 7.5, fill=CYAN)

# Badge
rect(s, 0.45, 0.4, 3.2, 0.32, fill=RGBColor(0x00,0x44,0x60), bd=CYAN, bw=Pt(0.75), rnd=20000)
txt(s, "SCIDIP PROGRAM APPLICATION", 0.55, 0.43, 3.0, 0.26,
    sz=8, bold=True, color=CYAN)

txt(s, "Advanced Materials  ·  Advanced Batteries  ·  Electric Mobility  ·  Sustainability",
    0.45, 0.82, 5.8, 0.28, sz=9, color=RGBColor(0x8B,0xBF,0xD8))

# Main headline
txt(s, "Accelerating Innovation\nat the Intersection of\nAI and Material Science",
    0.45, 1.25, 5.8, 2.5, sz=30, bold=True, color=WHITE)

rect(s, 0.45, 3.65, 2.5, 0.06, fill=CYAN)

txt(s, "Crystal Paradigm is an elite Deep-Tech Discovery Platform. We leverage "
    "artificial intelligence and high-performance computing to accelerate "
    "material discovery from 5 years to 4 weeks.",
    0.45, 3.8, 5.7, 0.9, sz=11, color=RGBColor(0xAA,0xB4,0xC6))

# Three pipeline pills
pills = [("1 Patent Accepted", CYAN), ("4 Papers Under Review", GOLD),
         ("Active Industry Collaborations", TEAL)]
px = 0.45
for lbl, col in pills:
    pw = 1.92
    rect(s, px, 4.82, pw, 0.38, fill=RGBColor(0x0D,0x2A,0x42), bd=col, bw=Pt(0.75), rnd=25000)
    txt(s, lbl, px+0.1, 4.87, pw-0.18, 0.28, sz=8, bold=True, color=col, align=PP_ALIGN.CENTER)
    px += pw + 0.12

# SCIDIP spearhead callout
rect(s, 0.45, 5.35, 5.8, 1.35, fill=RGBColor(0x00,0x2A,0x40), bd=GOLD, bw=Pt(0.9), rnd=15000)
rect(s, 0.45, 5.35, 0.06, 1.35, fill=GOLD, rnd=15000)
txt(s, "SCIDIP SPEARHEAD", 0.62, 5.42, 4.0, 0.24, sz=8, bold=True, color=GOLD)
txt(s, "For this application, we deploy our most extreme, fully-validated Proof of Concept: "
    "An AI-generated aerospace-grade Refractory High-Entropy Alloy (RHEA) engineered "
    "to solve Sona Comstar's terrestrial thermal bottlenecks.",
    0.62, 5.7, 5.45, 0.88, sz=10, color=RGBColor(0xCC,0xDD,0xEE))

# Right panel — light side with metric boxes
txt(s, "CRYSTAL PARADIGM", 7.1, 0.38, 5.8, 0.4, sz=11, bold=True, color=NAVY)
txt(s, "Key Metrics", 7.1, 0.76, 4.0, 0.28, sz=9, color=MUTED)
rect(s, 7.1, 0.98, 5.8, 0.04, fill=CARD_BD)

# 2x2 metric grid
mdata = [("9", "Elements\nOptimized"), ("11", "FGM\nLayers"),
         ("1.71", "3D Safety\nFactor"), ("4 Wks", "Discovery\nTime")]
mx, my = 7.1, 1.12
for i, (val, lbl) in enumerate(mdata):
    cx = mx + (i % 2) * 2.95
    cy = my + (i // 2) * 1.82
    metric_box(s, cx, cy, 2.75, 1.65, val, lbl, CYAN)

# Expanding pipeline
rect(s, 7.1, 4.82, 5.8, 2.3, fill=CARD_BG, bd=CARD_BD, bw=Pt(0.75), rnd=15000)
txt(s, "OUR EXPANDING PIPELINE", 7.28, 4.92, 5.4, 0.26, sz=9, bold=True, color=NAVY)
rect(s, 7.28, 5.22, 5.3, 0.03, fill=CARD_BD)
pipeline_items = [
    "·  Supercapacitors & Solid-State Battery Electrolytes (Li-ion & Na-ion)",
    "·  Next-Generation Solar Materials & Advanced Sensor Matrices",
    "·  1 Patent Accepted, 4 Research Papers Under Review, Active Industry Collaborations",
]
py = 5.3
for item in pipeline_items:
    txt(s, item, 7.28, py, 5.4, 0.32, sz=9.5, color=MUTED)
    py += 0.42

logo_footer(s)
txt(s, "1 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Aerospace Proof (by claude gradient strip + 3 evidence boxes)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "AEROSPACE PROOF OF CONCEPT", 2)
title_block(s, "PROVING THE PHYSICS: THE AEROSPACE THERMAL BOTTLENECK",
            "Our AI engine was built to solve the hardest thermal problem in modern engineering.")

# Body intro
txt(s, "Turbine Entry Temperatures (TET) exceeding 1400°C. Traditional nickel-based superalloys "
    "have hit a physical ceiling — the massive CTE mismatch causes protective ceramic armor to "
    "violently spall off under rapid thermal cycling.",
    0.5, 1.4, 12.3, 0.52, sz=10.5, color=MUTED)

# Problem card (left)
rect(s, 0.5, 2.05, 5.9, 2.05, fill=CARD_BG, bd=RED_SOFT, bw=Pt(1.0), rnd=15000)
rect(s, 0.5, 2.05, 5.9, 0.05, fill=RED_SOFT, rnd=15000)
txt(s, "THE AEROTHERMAL FIRE LIMIT", 0.68, 2.15, 5.5, 0.26, sz=10, bold=True, color=RED_SOFT)
txt(s, "· Traditional superalloy ceiling: ~1000°C\n"
    "· Target TET: > 1400°C — massive gap\n"
    "· CTE mismatch: High → Coating spallation\n"
    "· Consequence: Catastrophic blade failure\n"
    "· Legacy approach: Trial-and-error in lab (5 years per cycle)",
    0.68, 2.45, 5.5, 1.5, sz=10, color=MUTED)

# FGM gradient strip (from by claude slide 2 — 11 boxes)
txt(s, "FGM GRADIENT — 11-LAYER TRANSITION (Metallic HEA → LZO Ceramic, n=1.1)",
    6.55, 2.12, 6.5, 0.26, sz=8, bold=True, color=NAVY)
fgm_strip(s, 6.55, 2.42, 6.55, 0.5)
txt(s, "Layer 1: 100% Alloy                                           Layer 11: 100% LZO Ceramic",
    6.55, 2.95, 6.55, 0.22, sz=7.5, color=MUTED)

# Solution card (right)
rect(s, 6.55, 3.25, 6.55, 0.82, fill=CARD_BG, bd=TEAL, bw=Pt(1.0), rnd=15000)
txt(s, "THE CRYSTAL PARADIGM AI SOLUTION — CANDIDATE C",
    6.72, 3.33, 6.2, 0.26, sz=9, bold=True, color=TEAL)
txt(s, "Interface shear stress dropped to ultra-low 15.95 MPa — delamination eliminated. "
    "3D FEA Safety Factor: 1.71 ≥ 1.50 threshold.",
    6.72, 3.6, 6.25, 0.42, sz=9.5, color=MUTED)

# Three evidence boxes (from by claude slide 2 bottom)
evidence = [
    ("THE PHYSICS", CYAN,
     "Ti-dominant solid solution (21.7%) mathematically closed the CTE gap to 2.66 μm/mK."),
    ("THE MANUFACTURING", TEAL,
     "11-layer FGM matrix using exact n=1.1 power-law gradient — ready for multi-hopper DED printing."),
    ("THE RESULT", GREEN,
     "Interface shear stress: 15.95 MPa ultra-low. 3D Safety Factor: 1.71. Delamination eliminated."),
]
bx = 0.5
for title, col, body in evidence:
    bw_c = 4.1
    rect(s, bx, 4.18, bw_c, 2.65, fill=CARD_BG, bd=col, bw=Pt(0.75), rnd=15000)
    rect(s, bx, 4.18, bw_c, 0.05, fill=col, rnd=15000)
    # Icon dot
    rect(s, bx+0.18, 4.3, 0.32, 0.32, fill=col, rnd=50000)
    txt(s, title, bx+0.58, 4.3, bw_c-0.72, 0.28, sz=10, bold=True, color=col)
    txt(s, body, bx+0.18, 4.68, bw_c-0.32, 1.98, sz=10, color=MUTED)
    bx += bw_c + 0.22

logo_footer(s)
txt(s, "2 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — The Crossover (by claude 2-panel layout + light)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "FROM AEROSPACE TO MOBILITY", 3)
title_block(s, "THE SCIDIP CROSSOVER: FROM AEROSPACE TO EPIC MOBILITY",
            "If our AI can prevent a jet turbine from melting at 1400°C, it can revolutionize terrestrial mobility.")

txt(s, "We are entering the IIT Delhi SCIDIP program under the Advanced Materials category because "
    "Sona Comstar's EPIC roadmap is directly bottlenecked by the same thermodynamics.",
    0.5, 1.42, 12.3, 0.42, sz=10.5, color=MUTED)

# Crossover bridge — 3 boxes + arrows (by claude pattern)
boxes = [
    ("AEROSPACE EXTREME", RED_SOFT, "1400°C\nTurbine\nEntry Temp", "Safran RISE Open-Rotor Program"),
    ("CRYSTAL PARADIGM AI", CYAN, "Universal\nMaterials\nOptimizer", "Refractory HEA + 11-Layer FGM"),
    ("SONA COMSTAR EPIC", GOLD, "H13 Dies\n& EV SRMs", "Electric, Personalized, Intelligent, Connected"),
]
bx = 0.5
for i, (title, col, metric, sub) in enumerate(boxes):
    bw = 3.5
    rect(s, bx, 2.0, bw, 2.35, fill=CARD_BG, bd=col, bw=Pt(1.5), rnd=18000)
    rect(s, bx, 2.0, bw, 0.05, fill=col, rnd=18000)
    txt(s, title, bx+0.18, 2.1, bw-0.3, 0.26, sz=9, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(s, metric, bx+0.18, 2.4, bw-0.3, 1.1, sz=22, bold=True, color=TEXT, align=PP_ALIGN.CENTER)
    txt(s, sub, bx+0.18, 3.5, bw-0.3, 0.55, sz=9, color=MUTED, align=PP_ALIGN.CENTER)
    if i < 2:
        txt(s, "→", bx+bw+0.1, 2.6, 0.6, 0.7, sz=28, bold=True, color=CYAN, align=PP_ALIGN.CENTER)
    bx += bw + 0.72

# Two deployment cards
txt(s, "THE TWO THERMAL BOTTLENECKS WE SOLVE FOR SONA COMSTAR:",
    0.5, 4.52, 12.3, 0.3, sz=10, bold=True, color=NAVY)

cards2 = [
    ("① PRECISION FORGING DIES (DRIVELINE)", GOLD,
     "Sona Comstar's legacy H13 tool steel dies suffer rapid thermal fatigue and "
     "yield strength collapse at 1200°C during high-speed gear forging. "
     "Our HEA architectures retain >917.7 MPa yield strength at these exact temperatures."),
    ("② NEXT-GENERATION TRACTION MOTORS (ELECTRIC)", TEAL,
     "As Sona Comstar scales magnet-less Switched Reluctance Motors (SRMs), "
     "traditional metals degrade under severe localized thermal loads generated "
     "by extreme torque densities. Our FGM architecture provides the thermal shielding needed."),
]
cx = 0.5
for title, col, body in cards2:
    cw = 6.1
    rect(s, cx, 4.9, cw, 2.12, fill=CARD_BG, bd=col, bw=Pt(0.75), rnd=15000)
    rect(s, cx, 4.9, 0.06, 2.12, fill=col, rnd=15000)
    txt(s, title, cx+0.2, 4.98, cw-0.35, 0.28, sz=10, bold=True, color=col)
    txt(s, body, cx+0.2, 5.3, cw-0.35, 1.58, sz=10, color=MUTED)
    cx += cw + 0.13

logo_footer(s)
txt(s, "3 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Commercial Strategy (by claude 3-col card grid + light)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "COMMERCIAL STRATEGY", 4)
title_block(s, "DEPLOYING AEROSPACE GRADE MATERIALS AT COMMERCIAL SCALE",
            "Our AI engine does not just optimize for physics; it optimizes for the supply chain.")

txt(s, "By bridging aerospace IP into Sona Comstar's EPIC mobility framework, "
    "we generate massive downstream financial and strategic returns.",
    0.5, 1.42, 12.3, 0.35, sz=10.5, color=MUTED)

cols = [
    ("RAW MATERIAL\nCOST REDUCTION", CYAN, "15–20%\nCost Drop\n~$170/kg",
     "By programmatically substituting supply-constrained Hafnium with optimized "
     "Titanium (21.7%), our AI dropped raw material cost to ~$170/kg — "
     "enabling aerospace-grade materials for high-volume commercial automotive forging."),
    ("ESG &\nSUSTAINABILITY", TEAL, "1680 MJ/kg\nEmbodied\nEnergy",
     "Crystal Paradigm's Candidate C is fully quantified for environmental impact. "
     "Capped at a highly sustainable 1680 MJ/kg — directly supporting zero-emissions "
     "manufacturing goals and Sona Comstar's Scope 1/2 carbon reduction mandate."),
    ("SUPPLY CHAIN\nRESILIENCE", GOLD, "Make in\nIndia IP\n(9-Element)",
     "By utilizing a 9-element multi-principal matrix, we drastically reduce reliance "
     "on single critical minerals (Neodymium) controlled by volatile foreign supply chains. "
     "True indigenous, self-reliant IP for the Indian mobility sector."),
]
cx = 0.5
for title, col, metric, body in cols:
    cw = 4.08
    rect(s, cx, 1.88, cw, 5.32, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=18000)
    rect(s, cx, 1.88, cw, 0.06, fill=col, rnd=18000)
    txt(s, title, cx+0.18, 1.98, cw-0.3, 0.45, sz=10, bold=True, color=col)
    # Metric box inset
    rect(s, cx+0.18, 2.48, cw-0.36, 1.12, fill=BG, bd=col, bw=Pt(0.75), rnd=12000)
    txt(s, metric, cx+0.18, 2.54, cw-0.36, 1.0, sz=16, bold=True, color=col, align=PP_ALIGN.CENTER)
    rect(s, cx+0.3, 3.66, cw-0.6, 0.04, fill=CARD_BD)
    txt(s, body, cx+0.18, 3.78, cw-0.3, 3.2, sz=10, color=MUTED)
    cx += cw + 0.14

logo_footer(s)
txt(s, "4 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — AI Engine Step 1: Thermodynamic Gating (by claude 4-param grid)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "AI ENGINE · STEP 1 OF 3", 5)
title_block(s, "THE CRYSTAL PARADIGM AI ENGINE: STEP 1",
            "Secure Ingestion & Empirical Thermodynamic Gating")

txt(s, "Before a single ML model is trained, our pipeline strictly enforces the laws of physics "
    "and commercial viability. We ingest massive combinatorial spaces (Materials Project, AFLOW), "
    "ruthlessly filtering using Miedema's Empirical Rules — ensuring day-one compliance with "
    "Sona Comstar's 75% Supplier ESG mandate.",
    0.5, 1.42, 10.5, 0.62, sz=10.5, color=MUTED)

# ESG compliance stamp (top right — from by claude)
rect(s, 10.8, 1.42, 2.15, 0.62, fill=RGBColor(0xE8,0xF8,0xF3), bd=TEAL, bw=Pt(1.0), rnd=15000)
txt(s, "✓ SONA COMSTAR\n75% ESG COMPLIANCE", 10.88, 1.48, 2.0, 0.52,
    sz=8, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

# Flow visualization (by claude slide 5 process flow)
flow = [("Raw Combinatorial\nDatabase", NAVY, "(Materials Project,\nAFLOW)"),
        ("Thermodynamic\nGating Filter", CYAN, "(Miedema's Rules)"),
        ("ESG-Compliant\nCandidates", TEAL, "(for ML training)")]
fx = 0.5
for title, col, sub in flow:
    fw = 3.2
    rect(s, fx, 2.18, fw, 0.9, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=15000)
    txt(s, title, fx+0.15, 2.25, fw-0.25, 0.42, sz=11, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(s, sub, fx+0.15, 2.65, fw-0.25, 0.36, sz=8, color=MUTED, align=PP_ALIGN.CENTER)
    if fx < 7.0:
        txt(s, "→", fx+fw+0.08, 2.4, 0.52, 0.4, sz=20, bold=True, color=CYAN, align=PP_ALIGN.CENTER)
    fx += fw + 0.55

# 4 gating parameter cards (from by claude slide 5 — exact layout ported)
gating = [
    ("Atomic Size Mismatch (δ)", "≤ 6.6%",
     "Prevents lattice distortion under high torque. Ensures mechanical stability during high-speed gear forging operations."),
    ("Enthalpy of Mixing (ΔH_mix)", "−15 to +5 kJ/mol",
     "Ensures thermodynamically favorable mixing. Outside this band, the alloy phase-separates under thermal stress."),
    ("Valence Electron Concentration (VEC)", "4.0 – 6.8",
     "Guarantees a stable BCC matrix. VEC < 6.8 explicitly eliminates risk of brittle Sigma phase formation."),
    ("Omega Parameter (Ω)", "≥ 1.1",
     "Guarantees dominant solid solution stability over intermetallic compound formation at target temperatures."),
]
gx, gy = 0.5, 3.28
for i, (title, val, body) in enumerate(gating):
    col_off = (i % 2) * 6.42
    row_off = (i // 2) * 1.95
    gl, gt, gw, gh = gx+col_off, gy+row_off, 6.2, 1.78
    rect(s, gl, gt, gw, gh, fill=CARD_BG, bd=CARD_BD, bw=Pt(0.75), rnd=15000)
    # Accent top bar
    rect(s, gl, gt, gw, 0.05, fill=CYAN, rnd=15000)
    txt(s, title, gl+0.18, gt+0.12, gw-0.3, 0.26, sz=10, bold=True, color=TEXT)
    # Value box inset
    rect(s, gl+0.18, gt+0.44, gw-0.36, 0.42, fill=BG, bd=CYAN, bw=Pt(0.75), rnd=10000)
    txt(s, val, gl+0.18, gt+0.47, gw-0.36, 0.36,
        sz=13, bold=True, color=CYAN, align=PP_ALIGN.CENTER)
    txt(s, body, gl+0.18, gt+0.94, gw-0.3, 0.72, sz=9, color=MUTED)

logo_footer(s)
txt(s, "5 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — AI Engine Step 2: ML Surrogates (by claude big metric boxes)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "AI ENGINE · STEP 2 OF 3", 6)
title_block(s, "THE CRYSTAL PARADIGM AI ENGINE: STEP 2",
            "Dual-Stream Machine Learning Surrogates")

txt(s, "To predict material behavior for Sona Comstar's extreme-environment SRMs and H13 forging "
    "dies, we engineered a dual-stream surrogate architecture mapping both theoretical physics "
    "and real-world experimental variance.",
    0.5, 1.42, 12.3, 0.52, sz=10.5, color=MUTED)

for idx, (model, col, mets, arch_txt) in enumerate([
    ("MODEL 1 — THEORETICAL BULK MODULUS", CYAN,
     [("0.977", "AUDITED TEST R²"), ("8.11 GPa", "MEAN ABS ERROR"), ("100", "ESTIMATORS")],
     "Architecture & Features: 100 Estimators predicting across atomic radius (r), "
     "electronegativity (X), VEC, melting temperature (Tm), and mass standard deviations. "
     "Delivers bulk property predictions with near-perfect accuracy for the theoretical design space."),
    ("MODEL 2 — EXPERIMENTAL YIELD STRENGTH", GOLD,
     [("0.45×", "THERMAL KNOCKDOWN"), ("~1200°C", "FORGING DIE TEMP"), ("10×", "TARGET WEIGHT")],
     "Transfer Learning Logic: Trained on experimental MPEA dataset. Heavily weighted exact "
     "5-element target alloys (Weight=10) while leveraging broader refractory alloys (Weight=1). "
     "Homologous temperature knockdown factor (0.45) — assumes alloy retains 45% of RT yield strength."),
]):
    off = idx * 6.55
    rect(s, 0.5+off, 2.08, 6.3, 5.0, fill=CARD_BG, bd=col, bw=Pt(0.75), rnd=15000)
    rect(s, 0.5+off, 2.08, 6.3, 0.05, fill=col, rnd=15000)
    # Icon dot
    rect(s, 0.68+off, 2.2, 0.32, 0.32, fill=col, rnd=50000)
    txt(s, model, 1.1+off, 2.22, 5.5, 0.28, sz=10, bold=True, color=col)
    # Three metric boxes (from by claude slide 6 — big numbers)
    mx = 0.68+off
    for val, lbl in mets:
        metric_box(s, mx, 2.65, 1.85, 1.0, val, lbl, col)
        mx += 1.98
    rect(s, 0.68+off, 3.72, 5.9, 0.04, fill=CARD_BD)
    txt(s, arch_txt, 0.68+off, 3.85, 5.9, 3.0, sz=10, color=MUTED)

logo_footer(s)
txt(s, "6 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — AI Engine Step 3: DE Optimizer (by claude numbered constraint rows)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "AI ENGINE · STEP 3 OF 3", 7)
title_block(s, "THE CRYSTAL PARADIGM AI ENGINE: STEP 3",
            "Constrained Differential Evolution (DE) Optimizer")

txt(s, "To discover completely novel alloys, our AI sweeps a continuous 9-element space "
    "using a Softmax activation function to generate perfect sum-to-one fractional matrices. "
    "The objective function maximizes thermomechanical Safety Factor, penalized by strict commercial limits.",
    0.5, 1.42, 12.3, 0.52, sz=10.5, color=MUTED)

# Left: optimization landscape visualization placeholder (from by claude slide 7 concept)
rect(s, 0.5, 2.08, 5.6, 3.05, fill=CARD_BG, bd=CARD_BD, bw=Pt(0.75), rnd=15000)
# Concentric gradient rings (ported from by claude's topographic map concept)
ring_cols = [
    (RGBColor(0xE8,0xF8,0xF3), 5.2, 2.75),
    (RGBColor(0xC8,0xF0,0xE5), 4.2, 3.15),
    (RGBColor(0xA0,0xE5,0xD2), 3.2, 3.55),
    (RGBColor(0x60,0xD4,0xB4), 2.2, 3.95),
    (RGBColor(0x00,0xC8,0x96), 1.2, 4.35),
]
for col, w, cx in ring_cols:
    h = w * 0.5
    rect(s, cx - w/2, 2.25 + (5.6-w)*0.18, w, h,
         fill=col, bd=None, rnd=50000)
# Global optimum dot
rect(s, 2.7, 4.22, 0.2, 0.2, fill=WHITE, bd=NAVY, bw=Pt(1.0), rnd=50000)
txt(s, "GLOBAL\nOPTIMUM", 2.5, 4.45, 1.5, 0.42, sz=7.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
txt(s, "SAFETY-FACTOR OPTIMIZATION LANDSCAPE", 0.68, 2.14, 5.2, 0.26,
    sz=8, bold=True, color=MUTED)
# Result callout
rect(s, 0.5, 5.22, 5.6, 0.9, fill=RGBColor(0xE8,0xF8,0xF3), bd=TEAL, bw=Pt(0.75), rnd=12000)
txt(s, "Candidate C Result: Fitness Score 1.5981 — Ti=21.7% — Every Penalty Cleared — CTE Gap: 2.66 μm/mK",
    0.65, 5.35, 5.3, 0.62, sz=9.5, bold=True, color=TEAL)

# Right: 4 constraint rows (from by claude slide 7 — numbered rows with penalty badges)
txt(s, "OBJECTIVE PENALTIES — SONA COMSTAR COMMERCIAL LIMITS",
    6.3, 2.14, 6.7, 0.26, sz=9, bold=True, color=NAVY)
rect(s, 6.3, 2.42, 6.7, 0.04, fill=CARD_BD)

constraints = [
    ("1", "Sigma Phase Mitigation",
     "if Sigma Formers (W+Cr+Mo) exceed 50%", "Penalty × 5.0"),
    ("2", "Vanadium Volatility",
     "prevents toxic outgassing during high-temp operation", "V ≤ 20%"),
    ("3", "ESG Weight Budget",
     "aligns with EV lightweighting goals — hard density ceiling", "≤ 11.0 g/cm³"),
    ("4", "Oxidation Barrier",
     "minimum chromium requirement for α-Al₂O₃ formation", "≥ 15% Cr"),
]
ry = 2.55
for num, heading, body, penalty in constraints:
    num_row(s, 6.3, ry, num, heading, body, penalty, GOLD)
    ry += 0.82

# Candidate C composition banner
rect(s, 6.3, 5.92, 6.7, 0.7, fill=CARD_BG, bd=TEAL, bw=Pt(0.75), rnd=12000)
txt(s, "CANDIDATE C: Ta – W – Cr – V – Ti (21.7%) – Zr – Hf + 2.8% Al",
    6.5, 5.98, 6.4, 0.28, sz=10, bold=True, color=TEAL)
txt(s, "VEC: 5.02 (BCC stable) · Safety Factor: 1.71 · Cost: ~$170/kg",
    6.5, 6.25, 6.4, 0.28, sz=9.5, color=MUTED)

logo_footer(s)
txt(s, "7 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Verification Table (Final.pptx slide 8 reference — elite table)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "VERIFICATION & TRL STATUS", 8)
title_block(s, "WHAT IS PROVEN TODAY AND WHAT IS NOT",
            "High-Fidelity Verification Metrics and TRL Maturity Status")

# TRL badge
rect(s, 10.5, 1.42, 2.45, 0.62, fill=RGBColor(0xE8,0xF8,0xF3), bd=TEAL, bw=Pt(0.75), rnd=12000)
txt(s, "CURRENT TRL: 3+\n→ Target: TRL 4 via SCIDIP", 10.58, 1.48, 2.3, 0.52,
    sz=8, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

txt(s, "All computational physics fully confirmed in-silico via PyCalphad, 1D/3D FEA, and MACE MD. "
    "Applying to SCIDIP to execute physical TRL 4 lab validation using IIT Delhi CRF and NIDHI-CoE.",
    0.5, 1.42, 9.8, 0.52, sz=10.5, color=MUTED)

# Table header (from Final.pptx slide 8 styling — clean professional audit table)
headers = [("Evaluation Vector", 2.8), ("Model / In Silico Status", 2.6),
           ("Lab Validation Target", 2.35), ("SCIDIP Test Equipment", 2.65), ("Status", 0.85)]
hx = 0.5
for hdr, hw in headers:
    rect(s, hx, 2.1, hw-0.04, 0.38, fill=HEADER_BAND)
    txt(s, hdr, hx+0.1, 2.14, hw-0.18, 0.3, sz=8, bold=True, color=WHITE)
    hx += hw

rows = [
    ("BCC Phase Security", "Verified (CALPHAD / PyCalphad)", "0% Brittle Sigma Phase", "High-Temp XRD — IIT Delhi CRF", "VERIFIED"),
    ("Elastic Modulus Surface", "Audited — Test R² = 0.977\nMAE = 8.11 GPa", "MAE ≤ 8.11 GPa", "NIDHI-CoE Tensile Tester", "VERIFIED"),
    ("Oxidation Scale Kinetics", "Verified via 2.8% Al Pivot\n(α-Al₂O₃ formation)", "Mass Gain < 10 mg/cm²", "STA / TGA — IIT Delhi CRF", "VERIFIED"),
    ("Interfacial Bond Safety", "Verified — 1D & 3D FEA\n(SF = 1.71 ≥ 1.50)", "Safety Factor ≥ 1.50", "Burner Rig Adhesion Test", "VERIFIED"),
    ("Physical Prototyping", "Fully Formulated\n(11-layer recipe exported)", "TRL 4 Coupon Assembly", "DED 3D Printer — SCIDIP Fund", "PENDING"),
]
widths = [hw for _, hw in headers]
ry = 2.52
for i, row in enumerate(rows):
    row_bg = WHITE if i % 2 == 0 else BG
    rx = 0.5
    for j, (cell, cw) in enumerate(zip(row[:4], widths[:4])):
        rect(s, rx, ry, cw-0.04, 0.8, fill=row_bg, bd=CARD_BD, bw=Pt(0.5))
        txt(s, cell, rx+0.1, ry+0.06, cw-0.2, 0.68,
            sz=8.5, color=NAVY if j == 0 else MUTED, bold=(j == 0))
        rx += cw
    # Status col
    status = row[4]
    sc = GREEN if status == "VERIFIED" else YELLOW_ST
    st_txt = "● VERIFIED" if status == "VERIFIED" else "○ PENDING"
    rect(s, rx, ry, widths[4]-0.04, 0.8, fill=row_bg, bd=CARD_BD, bw=Pt(0.5))
    txt(s, st_txt, rx+0.04, ry+0.22, widths[4]-0.1, 0.34,
        sz=8, bold=True, color=sc, align=PP_ALIGN.CENTER)
    ry += 0.84

logo_footer(s)
txt(s, "8 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Final Architecture Candidate C (by claude FGM strip + 3 boxes)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "FROM CHEMISTRY TO MANUFACTURING", 9)
title_block(s, "THE FINAL ARCHITECTURE (CANDIDATE C)",
            "From In-Silico Chemistry to Print-Ready Manufacturing")

txt(s, "Through 11 phases of autonomous generation, our AI produced Candidate C — "
    "a hyper-optimized Refractory High-Entropy Alloy designed specifically for extreme thermal shock.",
    0.5, 1.42, 12.3, 0.42, sz=10.5, color=MUTED)

# Three breakthrough cards
bdata = [
    ("① THE TITANIUM PIVOT", CYAN, "CTE Gap: 2.66 μm/mK",
     "Our AI intentionally substituted heavy Hafnium for Titanium (21.7%). Because Titanium has the "
     "highest CTE (8.6 µm/mK) in the refractory space, it aggressively closed the mismatch "
     "with the ceramic coating, dropping the gap to just 2.66 μm/mK."),
    ("② THE ALUMINUM ARMOR", GOLD, "Mass Gain: 7.5 mg/cm²",
     "The AI identified that standard Chromium oxidizes above 1100°C. We executed a micro-addition "
     "of 2.8 at% Aluminum to force formation of a highly stable α-Al₂O₃ protective armor scale, "
     "capping oxidation mass gain at 7.5 mg/cm²."),
    ("③ THE MANUFACTURING RECIPE", TEAL, "11-Layer Print-Ready",
     "We directly exported the continuous FGM physics curves into a discrete, print-ready "
     "11-layer manufacturing_recipe.csv (0.0mm = 100% alloy → 5.0mm = 100% LZO ceramic). "
     "Ready for immediate Multi-Hopper DED 3D printing."),
]
bx = 0.5
for title, col, metric, body in bdata:
    bw = 4.08
    rect(s, bx, 1.95, bw, 3.28, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=18000)
    rect(s, bx, 1.95, bw, 0.06, fill=col, rnd=18000)
    txt(s, title, bx+0.18, 2.06, bw-0.3, 0.26, sz=10, bold=True, color=col)
    rect(s, bx+0.18, 2.38, bw-0.36, 0.48, fill=BG, bd=col, bw=Pt(0.75), rnd=12000)
    txt(s, metric, bx+0.18, 2.41, bw-0.36, 0.42,
        sz=12, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(s, body, bx+0.18, 2.95, bw-0.3, 2.16, sz=10, color=MUTED)
    bx += bw + 0.14

# FGM strip (from by claude slide 9)
txt(s, "11-LAYER PRINT MATRIX CROSS-SECTION:", 0.5, 5.3, 5.0, 0.25, sz=8.5, bold=True, color=NAVY)
fgm_strip(s, 0.5, 5.58, 12.33, 0.62)
txt(s, "Layer 1 (0.0mm): 100% Alloy                                Layer 11 (5.0mm): 100% LZO Ceramic",
    0.5, 6.24, 12.33, 0.24, sz=8, color=MUTED)

# Composition banner
rect(s, 0.5, 6.52, 12.33, 0.52, fill=CARD_BG, bd=CYAN, bw=Pt(0.75), rnd=12000)
txt(s, "Alloy: Ta – W – Cr – V – Ti(21.7%) – Zr – Hf + 2.8% Al  |  VEC: 5.02  |  "
    "3D Safety Factor: 1.71  |  Cost: ~$170/kg  |  Density: < 11.0 g/cm³",
    0.65, 6.6, 12.0, 0.36, sz=9.5, bold=True, color=NAVY)

logo_footer(s)
txt(s, "9 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Commercial Impact Table (by claude row layout + Final table style)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "COMMERCIAL IMPACT", 10)
title_block(s, "THE COMMERCIAL IMPACT FOR SONA COMSTAR",
            "Fleet Scalability and Direct Operating Cost Reductions")

txt(s, "By bridging aerospace materials into Sona Comstar's EPIC mobility framework, "
    "we generate massive downstream financial and strategic returns.",
    0.5, 1.42, 12.3, 0.4, sz=10.5, color=MUTED)

iheads = [("Impact Area", 2.8), ("The Physics Trigger", 4.3), ("The Commercial Result", 5.8)]
hx = 0.5
for hdr, hw in iheads:
    rect(s, hx, 1.9, hw-0.04, 0.38, fill=HEADER_BAND)
    txt(s, hdr, hx+0.1, 1.94, hw-0.2, 0.3, sz=9, bold=True, color=WHITE)
    hx += hw

irows = [
    ("Raw Material\nProcurement", "75% reduction in Hafnium, substituted with Ti (21.7% achieved).",
     "15–20% Drop in Alloy Cost — Achieves ~$170/kg, enabling high-volume EV commercialization."),
    ("Tooling &\nForging Uptime", "H13 Dies retain 917.7 MPa yield strength at 1200°C, no mechanical deformation.",
     "Drastic MRO Reduction — Eliminates thermal fatigue cracking, vastly extending tooling life."),
    ("Next-Gen EV\nMotors (SRM)", "Elimination of localized thermal hotspots in Switched Reluctance Motor stator/rotors.",
     "Rare-Earth Independence — High-power magnet-less motors without thermal degradation."),
    ("Supply Chain\nResilience", "9-element multi-principal matrix drastically reduces single mineral dependency.",
     "True Aatmanirbharta — Indigenous IP generation for Indian mobility sector."),
    ("ESG &\nSustainability", "Embodied Energy capped at 1680 MJ/kg, zero toxic heavy elements in composition.",
     "Qualifies for Sona Comstar 75% Supplier Score — 12 of 17 ESG metrics on day one."),
]
widths = [hw for _, hw in iheads]
ry = 2.32
for i, (area, physics, result) in enumerate(irows):
    row_bg = WHITE if i % 2 == 0 else BG
    rx = 0.5
    for cell, cw in zip([area, physics, result], widths):
        rect(s, rx, ry, cw-0.04, 0.82, fill=row_bg, bd=CARD_BD, bw=Pt(0.5))
        txt(s, cell, rx+0.12, ry+0.08, cw-0.24, 0.66,
            sz=9, color=NAVY if rx < 0.8 else MUTED, bold=(rx < 0.8))
        rx += cw
    ry += 0.86

logo_footer(s)
txt(s, "10 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — SCIDIP Deployment 1: Forging Dies
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "SCIDIP DEPLOYMENT 1", 11)
title_block(s, "SCIDIP DEPLOYMENT 1: NEXT-GEN FORGING DIES",
            "Solving Sona Comstar's Differential Gear Bottleneck")

txt(s, "Sona Comstar's core competitive advantage lies in precision forging of differential bevel gears. "
    "Legacy H13 tool steel dies suffer massive yield strength collapse and thermal fatigue when "
    "operating near 1200°C, causing costly manufacturing downtime.",
    0.5, 1.42, 12.3, 0.52, sz=10.5, color=MUTED)

# Two comparison cards (from by claude slide 11)
for i, (title, col, body) in enumerate([
    ("LEGACY H13 TOOL STEEL DIE", RED_SOFT,
     "· Rapid thermal fatigue & yield strength collapse at 1200°C\n"
     "· < 500 MPa yield strength at operating temperature\n"
     "· Frequent die cracking causing costly manufacturing downtime\n"
     "· Limits Sona Comstar's throughput for EV driveline components"),
    ("CANDIDATE C FGM FORGING DIE", TEAL,
     "· Ta-W-Cr-V-Ti-Zr-Hf alloy retains >917.7 MPa at 1200°C\n"
     "· LZO ceramic outer layer acts as supreme thermal barrier\n"
     "· 11-layer FGM architecture eliminates thermal fatigue cracking\n"
     "· Vastly extends tooling life, accelerates manufacturing throughput"),
]):
    off = i * 6.55
    rect(s, 0.5+off, 2.08, 6.3, 2.15, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=15000)
    rect(s, 0.5+off, 2.08, 6.3, 0.05, fill=col, rnd=15000)
    rect(s, 0.68+off, 2.2, 0.32, 0.32, fill=col, rnd=50000)
    txt(s, title, 1.1+off, 2.22, 5.5, 0.26, sz=10, bold=True, color=col)
    txt(s, body, 0.68+off, 2.6, 5.9, 1.5, sz=10, color=MUTED)

# Three upgrade detail cards (from by claude slide 11 bottom row)
upgrade3 = [
    ("The Core", NAVY,
     "The Ta-W-Cr-V-Ti-Zr-Hf alloy retains >917.7 MPa yield strength at 1200°C, "
     "preventing mechanical deformation under massive forging pressures."),
    ("The Surface", CYAN,
     "The LZO (Lanthanum Zirconate) ceramic outer layer acts as a supreme thermal "
     "barrier, preventing heat transfer from the hot-forged blank into the die."),
    ("The Result", TEAL,
     "Elimination of rapid thermal fatigue cracking, vastly extending tooling life "
     "and accelerating manufacturing throughput for EV gearbox components."),
]
txt(s, "THE CRYSTAL PARADIGM UPGRADE: 11-LAYER FGM ARCHITECTURE",
    0.5, 4.32, 12.3, 0.28, sz=10, bold=True, color=NAVY)
bx = 0.5
for title, col, body in upgrade3:
    bw = 4.08
    rect(s, bx, 4.68, bw, 2.45, fill=CARD_BG, bd=col, bw=Pt(0.75), rnd=15000)
    rect(s, bx, 4.68, 0.06, 2.45, fill=col, rnd=15000)
    txt(s, title, bx+0.2, 4.76, bw-0.35, 0.28, sz=10, bold=True, color=col)
    txt(s, body, bx+0.2, 5.1, bw-0.35, 1.85, sz=10, color=MUTED)
    bx += bw + 0.14

logo_footer(s)
txt(s, "11 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — SCIDIP Deployment 2: EV Motors
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "SCIDIP DEPLOYMENT 2", 12)
title_block(s, "SCIDIP DEPLOYMENT 2: MAGNET-LESS EV MOTORS",
            "Enabling Rare-Earth Independence in Traction Motors")

txt(s, "As part of the 'EPIC' roadmap, Sona Comstar is heavily investing in Switched Reluctance "
    "Motors (SRMs) to eliminate reliance on imported Neodymium magnets.",
    0.5, 1.42, 12.3, 0.42, sz=10.5, color=MUTED)

# Two comparison panels
for i, (title, col, body) in enumerate([
    ("THE ENGINEERING BOTTLENECK", RED_SOFT,
     "SRMs generate extreme, localized thermal hotspots that degrade traditional "
     "stator/rotor metals.\n\n"
     "① Supply Chain Risk: 80%+ of global Neodymium controlled by China — severe "
     "geopolitical supply vulnerability for Indian EV manufacturing.\n\n"
     "② Thermal Degradation: At extreme torque densities, traditional metals rapidly "
     "lose mechanical integrity, limiting SRM power density and lifespan."),
    ("THE CRYSTAL PARADIGM UPGRADE", TEAL,
     "By deploying our aerospace-derived Candidate C, we provide Sona Comstar with a "
     "structural material capable of surviving localized high-temperature spikes.\n\n"
     "① Thermal Shielding: The FGM gradient handles rapid thermal cycling without "
     "delamination (15.95 MPa interface shear stress).\n\n"
     "② Make-In-India Supply Chain: Titanium substitution drops alloy cost to ~$170/kg, "
     "making aerospace-grade protection viable for high-volume Indian EV manufacturing."),
]):
    off = i * 6.55
    rect(s, 0.5+off, 2.05, 6.3, 5.1, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=15000)
    rect(s, 0.5+off, 2.05, 6.3, 0.06, fill=col, rnd=15000)
    rect(s, 0.68+off, 2.18, 0.32, 0.32, fill=col, rnd=50000)
    txt(s, title, 1.1+off, 2.2, 5.5, 0.28, sz=10, bold=True, color=col)
    txt(s, body, 0.68+off, 2.6, 5.9, 4.3, sz=10.5, color=MUTED)

logo_footer(s)
txt(s, "12 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — IP Strategy & Aatmanirbharta (by claude 3-card pattern)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "DE-RISKING THE SUPPLY CHAIN", 13)
title_block(s, "INTELLECTUAL PROPERTY & DE-RISKING THE SUPPLY CHAIN",
            "True Aatmanirbharta for the Indian Mobility Sector")

txt(s, "Sona Comstar's strategic reliance on rare-earth elements for EV motors is a massive "
    "supply chain vulnerability. Crystal Paradigm offers a computational pathway to complete import substitution.",
    0.5, 1.42, 12.3, 0.42, sz=10.5, color=MUTED)

# Dependency vs Innovation bridge (from by claude slide 13)
rect(s, 0.5, 2.0, 5.5, 1.05, fill=CARD_BG, bd=RED_SOFT, bw=Pt(0.75), rnd=12000)
txt(s, "CURRENT DEPENDENCY", 0.68, 2.08, 5.0, 0.24, sz=9, bold=True, color=RED_SOFT)
txt(s, "Foreign-controlled Neodymium & Rare-Earth imports for EV motor magnets "
    "(80%+ China-controlled supply chain)",
    0.68, 2.36, 5.0, 0.6, sz=9.5, color=MUTED)

txt(s, "→", 6.1, 2.2, 0.8, 0.6, sz=24, bold=True, color=CYAN, align=PP_ALIGN.CENTER)

rect(s, 7.0, 2.0, 5.9, 1.05, fill=RGBColor(0xE8,0xF8,0xF3), bd=TEAL, bw=Pt(0.75), rnd=12000)
txt(s, "INDIGENOUS INDIAN INNOVATION", 7.18, 2.08, 5.5, 0.24, sz=9, bold=True, color=TEAL)
txt(s, "Powered by Crystal Paradigm AI + IIT Delhi — built on globally abundant "
    "Titanium & Chromium for true supply chain security",
    7.18, 2.36, 5.5, 0.6, sz=9.5, color=MUTED)

# Three IP cards
ip3 = [
    ("THE IP MOAT", CYAN,
     "Our proprietary 11-phase AI architecture is a continuous IP generation engine. "
     "Candidate C is merely our first output; we can computationally generate bespoke "
     "materials for any thermal bottleneck Sona Comstar faces across all four EPIC verticals."),
    ("MAKE-IN-INDIA REALITY", GOLD,
     "By engineering out exotic, foreign-controlled minerals and optimizing around globally "
     "abundant Titanium and Chromium, we guarantee a secure, indigenous supply chain for "
     "Sona Comstar's next-gen components — critical for true Aatmanirbharta."),
    ("IIT DELHI IP FRAMEWORK", TEAL,
     "We are prepared to navigate the FITT incubation framework to jointly patent physical "
     "material formulations developed within the Central Research Facility (CRF), ensuring "
     "robust legal IP protection for all innovations generated during the SCIDIP incubation."),
]
cx = 0.5
for title, col, body in ip3:
    cw = 4.08
    rect(s, cx, 3.2, cw, 3.95, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=18000)
    rect(s, cx, 3.2, cw, 0.06, fill=col, rnd=18000)
    txt(s, title, cx+0.18, 3.32, cw-0.3, 0.28, sz=10, bold=True, color=col)
    rect(s, cx+0.18, 3.66, cw-0.36, 0.04, fill=CARD_BD)
    txt(s, body, cx+0.18, 3.78, cw-0.3, 3.2, sz=10.5, color=MUTED)
    cx += cw + 0.14

logo_footer(s)
txt(s, "13 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — Corporate Ask (4 pillars)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "THE CORPORATE ASK", 14)
title_block(s, "THE CRYSTAL PARADIGM CORPORATE ASK",
            "Bridging the Gap Between Informatics and the Factory Floor")

txt(s, "Crystal Paradigm is completely computationally validated (TRL 3+). We are applying to the "
    "Advanced Materials track of the SCIDIP program to access the precise ecosystem to cross the "
    "'valley of death'.",
    0.5, 1.42, 12.3, 0.42, sz=10.5, color=MUTED)

# TRL progression banner
rect(s, 0.5, 1.95, 12.33, 0.55, fill=HEADER_BAND, rnd=12000)
stages = [("TRL 1-2", 1.5), ("TRL 3+ ✓ NOW", 4.5), ("TRL 4-5 (SCIDIP)", 8.0), ("TRL 6 COMMERCIALIZATION", 11.0)]
for label, lx in stages:
    txt(s, label, lx-0.5, 2.05, 2.5, 0.35, sz=9, bold=True, color=CYAN, align=PP_ALIGN.CENTER)

# Four pillars
pillars = [
    ("1", "TECHNOLOGY & LAB SUPPORT", "IIT Delhi CRF", CYAN,
     "Immediate access to the NIDHI-CoE and CRF to execute High-Temperature XRD, SEM, and "
     "Simultaneous Thermal Analysis (STA) on physical witness coupons."),
    ("2", "SONA COMSTAR MENTORSHIP", "Engineering Alignment", GOLD,
     "Direct engineering alignment with Sona Comstar's precision forging division to ensure "
     "our 11-layer print matrices match factory-floor DED manufacturing tolerances."),
    ("3", "SCIDIP SEED ECOSYSTEM", "₹ Incubation Grant", TEAL,
     "Integration into the SCIDIP funding framework to finance raw material atomization "
     "and multi-hopper 3D printing of the physical witness coupon prototypes."),
    ("4", "CORPORATE MARKET CONNECT", "Supply Chain Integration", RGBColor(0xE0,0x70,0x30),
     "Joint integration of the physical prototypes into Sona Comstar's downstream EV "
     "supply chain — forging dies and SRM stator components."),
]
px = 0.5
for num, title, subtitle, col, body in pillars:
    pw = 2.98
    rect(s, px, 2.65, pw, 4.5, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=18000)
    rect(s, px, 2.65, pw, 0.06, fill=col, rnd=18000)
    # Number circle
    rect(s, px+pw/2-0.28, 2.78, 0.56, 0.56, fill=col, rnd=50000)
    txt(s, num, px+pw/2-0.28, 2.8, 0.56, 0.48, sz=16, bold=True,
        color=WHITE, align=PP_ALIGN.CENTER)
    txt(s, title, px+0.15, 3.44, pw-0.3, 0.42, sz=10, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(s, subtitle, px+0.15, 3.88, pw-0.3, 0.26, sz=8.5, color=MUTED, align=PP_ALIGN.CENTER)
    rect(s, px+0.3, 4.2, pw-0.6, 0.04, fill=CARD_BD)
    txt(s, body, px+0.15, 4.32, pw-0.3, 2.65, sz=9.5, color=MUTED, align=PP_ALIGN.CENTER)
    px += pw + 0.13

logo_footer(s)
txt(s, "14 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — 24-Month Roadmap (by claude milestone pattern)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "EXECUTION ROADMAP", 15)
title_block(s, "THE 24-MONTH INCUBATION ROADMAP",
            "From Computational Validation to Sona Comstar Integration")

txt(s, "Our execution strategy is strictly mapped to the 24-month SCIDIP incubation cycle "
    "at Atal Incubation Centre (AIC), IIT Delhi.",
    0.5, 1.42, 12.3, 0.38, sz=10.5, color=MUTED)

# Timeline spine (by claude slide 15)
rect(s, 0.9, 2.05, 11.5, 0.06, fill=CARD_BD, rnd=10000)

mstones = [
    ("M1", "Months 1–6", "POWDER SYNTHESIS", CYAN,
     "Procure raw metal powders (Ta, W, Cr, V, Ti, Zr, Hf, Al). Utilize IIT Delhi labs "
     "to verify composition purity and atomization quality."),
    ("M2", "Months 6–12", "ADDITIVE MANUFACTURING", GOLD,
     "Execute the 11-layer manufacturing_recipe.csv via DED (Directed Energy Deposition) "
     "to print physical witness coupons."),
    ("M3", "Months 12–18", "NIDHI-CoE & CRF TESTING", TEAL,
     "Conduct physical yield strength and thermal shock validation at IIT Delhi "
     "to physically validate the 1.50 Safety Factor (XRD + STA)."),
    ("M4", "Months 18–24", "CORPORATE HANDOVER", RGBColor(0xE0,0x70,0x30),
     "Present fully validated TRL 5/6 hardware to Sona Comstar for direct integration "
     "into H13 forging dies and SRM stator prototypes."),
]
mx = 0.5
for tag, period, title, col, body in mstones:
    milestone_col(s, mx, 2.2, tag, period, title, body, col)
    mx += 3.08

logo_footer(s)
txt(s, "15 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — Research Leads (by claude 2-profile layout)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "THE RESEARCH LEADS", 16)
title_block(s, "THE RESEARCH LEADS",
            "Guided by Elite Academic and Scientific Expertise")

leads = [
    ("DR. SHILPA CHOUDHARY", "AI / ML Lead", CYAN,
     [("Recognition", "Top 2% Scientists Worldwide — Stanford University (2024)"),
      ("Experience", "16+ years in AI, Deep Learning & AI-driven scientific applications"),
      ("Postdoctoral", "Singapore Institute of Technology & National Kaohsiung University of Science and Technology (Taiwan)"),
      ("Output", "100+ research papers · 1763 citations · H-index 22 · 12 academic books · Multiple patents"),
      ("At Crystal Paradigm", "Leads AI innovation, ML Architecture, Constrained Optimization & Surrogate Model Design")]),
    ("DR. KASARAPU VENKATARAMANA", "Materials Science & Experimental Validation Lead", GOLD,
     [("Position", "Research Associate at CSIR-IICT — DRDO sponsored project"),
      ("Recognition", "Associate Fellow, Telangana Academy of Sciences (2024)"),
      ("Experience", "12 years research + 5 years academic teaching"),
      ("Output", "38 publications · 610+ citations · H-index 14 · Reviewer: Elsevier, Springer, Taylor & Francis"),
      ("Specialization", "High Entropy Oxides, XRD, SEM/EDS, advanced materials characterization")]),
]
lx = 0.5
for name, role, col, items in leads:
    lw = 6.1
    rect(s, lx, 1.55, lw, 5.68, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=18000)
    rect(s, lx, 1.55, lw, 0.06, fill=col, rnd=18000)
    # Avatar
    rect(s, lx+0.2, 1.68, 1.05, 1.05, fill=BG, bd=col, bw=Pt(0.75), rnd=50000)
    txt(s, "DR", lx+0.22, 1.82, 1.01, 0.6, sz=18, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(s, name, lx+1.38, 1.72, lw-1.55, 0.42, sz=12, bold=True, color=NAVY)
    txt(s, role, lx+1.38, 2.16, lw-1.55, 0.3, sz=9.5, color=col)
    rect(s, lx+0.2, 2.82, lw-0.4, 0.04, fill=CARD_BD)
    iy = 2.96
    for key, val in items:
        txt(s, f"· {key}:", lx+0.22, iy, 1.65, 0.26, sz=9, bold=True, color=col)
        txt(s, val, lx+1.88, iy, lw-2.08, 0.26, sz=9, color=MUTED)
        iy += 0.52
    lx += lw + 0.13

logo_footer(s)
txt(s, "16 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — Core AI Architects
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)
hdr_band(s)
slide_tag(s, "THE AI ENGINEERING ENGINE", 17)
title_block(s, "THE CORE AI ARCHITECTS",
            "The Prodigious Engine Driving the Day-to-Day AI Innovation")

engineers = [
    ("MOHAMMED AHMED RAZA", "AI Research Intern", CYAN,
     [("Education", "CSE — Neil Gogte Institute of Technology (NGIT)"),
      ("Certification", "Certified AI/ML Professional — iHub-Data, IIIT Hyderabad"),
      ("Research Intern", "Winter Intern at IIIT Hyderabad — UAV spatial awareness & obstacle detection"),
      ("Current Role", "AI Research Intern at Crystal Paradigm — inverse design frameworks for HE-MCGA"),
      ("Recent Work", "Co-authored breakthrough Attention Graph Siamese Transformer (DPT-GNN) for Li-ion battery prediction")]),
    ("K. INDRASENA REDDY [INDRA]", "AI Research Intern", GOLD,
     [("Education", "CSE — Neil Gogte Institute of Technology (NGIT)"),
      ("Previous Role", "AI Developer Intern at Viswam.AI — NLP applications & LLM research"),
      ("Current Role", "Materials informatics & graph neural network modeling at Crystal Paradigm"),
      ("Specialization", "Large-scale property prediction & advanced GNN architectures"),
      ("Focus", "AI-driven materials discovery & multi-physics simulation pipelines")]),
]
lx = 0.5
for name, role, col, items in engineers:
    lw = 6.1
    rect(s, lx, 1.55, lw, 4.7, fill=CARD_BG, bd=col, bw=Pt(1.0), rnd=18000)
    rect(s, lx, 1.55, lw, 0.06, fill=col, rnd=18000)
    rect(s, lx+0.2, 1.68, 1.05, 1.05, fill=BG, bd=col, bw=Pt(0.75), rnd=50000)
    txt(s, "AI", lx+0.22, 1.82, 1.01, 0.6, sz=18, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(s, name, lx+1.38, 1.72, lw-1.55, 0.42, sz=11, bold=True, color=NAVY)
    txt(s, role, lx+1.38, 2.16, lw-1.55, 0.3, sz=9.5, color=col)
    rect(s, lx+0.2, 2.82, lw-0.4, 0.04, fill=CARD_BD)
    iy = 2.96
    for key, val in items:
        txt(s, f"· {key}:", lx+0.22, iy, 1.65, 0.26, sz=9, bold=True, color=col)
        txt(s, val, lx+1.88, iy, lw-2.08, 0.26, sz=9, color=MUTED)
        iy += 0.48
    lx += lw + 0.13

# Extended team banner (from by claude slide 17)
rect(s, 0.5, 6.35, 12.33, 0.72, fill=RGBColor(0xE8,0xF8,0xF3), bd=TEAL, bw=Pt(0.75), rnd=12000)
txt(s, "EXTENDED CRYSTAL PARADIGM ENGINEERING TEAM",
    0.7, 6.42, 9.0, 0.26, sz=9, bold=True, color=TEAL)
txt(s, "The core architecture is rapidly scaled and supported by a dedicated extended team of "
    "18 specialized AI Research Interns, ensuring massive parallel execution bandwidth for "
    "complex multi-physics simulations and AI training pipelines.",
    0.7, 6.68, 11.8, 0.32, sz=9, color=MUTED)

logo_footer(s)
txt(s, "17 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — Closing (Final.pptx closing style + by claude centered logo area)
# ══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BG)

# Large navy left panel
rect(s, 0, 0, 7.2, 7.5, fill=HEADER_BAND)
rect(s, 7.2, 0, 0.06, 7.5, fill=CYAN)

# Left side content
rect(s, 0.5, 0.4, 0.06, 6.5, fill=CYAN)

txt(s, "CRYSTAL PARADIGM", 0.72, 0.45, 6.3, 0.42,
    sz=12, bold=True, color=CYAN)

txt(s, "Accelerating\nDeep-Tech Materials\nfrom 5 Years\nto 4 Weeks.",
    0.72, 1.05, 6.1, 2.8, sz=30, bold=True, color=WHITE)

rect(s, 0.72, 3.82, 3.0, 0.06, fill=CYAN)

txt(s, "We have completely solved the computational bottleneck.",
    0.72, 3.98, 6.1, 0.35, sz=12, color=RGBColor(0xAA,0xB4,0xC6))
txt(s, "We are ready to build the physical reality.",
    0.72, 4.38, 6.1, 0.35, sz=12, bold=True, color=WHITE)

txt(s, "Join us at the SCIDIP Advanced Materials Track.",
    0.72, 4.95, 6.1, 0.35, sz=11, bold=True, color=CYAN)

txt(s, "crystalparadigm.in  |  khub.crystalparadigm@gmail.com",
    0.72, 5.55, 6.1, 0.28, sz=9.5, color=RGBColor(0x8B,0xBF,0xD8))

# Right panel — QR placeholder + final kicker
rect(s, 7.5, 1.2, 5.4, 5.4, fill=CARD_BG, bd=CARD_BD, bw=Pt(0.75), rnd=15000)
# QR visual mockup
rect(s, 8.8, 1.8, 2.8, 2.8, fill=BG, bd=NAVY, bw=Pt(1.5), rnd=8000)
rect(s, 9.0, 2.0, 0.6, 0.6, fill=NAVY, rnd=5000)
rect(s, 10.4, 2.0, 0.6, 0.6, fill=NAVY, rnd=5000)
rect(s, 9.0, 3.4, 0.6, 0.6, fill=NAVY, rnd=5000)
rect(s, 9.5, 2.5, 1.4, 1.4, fill=CARD_BD, rnd=5000)
txt(s, "[ QR CODE ]", 8.8, 4.2, 2.8, 0.35, sz=9, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, "Scan to access the\n50+ Page Technical Appendix",
    8.8, 4.55, 2.8, 0.55, sz=9, color=MUTED, align=PP_ALIGN.CENTER)

txt(s, "CRYSTAL PARADIGM", 7.65, 1.38, 5.0, 0.32,
    sz=10, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
txt(s, "Advanced Materials · Artificial Intelligence\nDeep-Tech Materials Platform",
    7.65, 5.52, 5.0, 0.55, sz=9, color=MUTED, align=PP_ALIGN.CENTER)

logo_footer(s)
txt(s, "18 / 18", 12.6, 7.26, 0.7, 0.2, sz=7, color=MUTED, align=PP_ALIGN.RIGHT)

# ─── SAVE ────────────────────────────────────────────────────────────────────
out = "CrystalParadigm_SCIDIP_v3_FINAL.pptx"
prs.save(out)
print(f"\nSUCCESS: {out} generated with {len(prs.slides)} slides")
