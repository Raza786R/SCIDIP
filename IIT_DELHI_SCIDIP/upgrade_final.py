"""
UPGRADE Final.pptx — Add missing slides for IIT Delhi targeting.
Keeps all 14 existing slides intact. Adds 6 new slides.
Reorders so Closing stays last.
Matches the EXACT Final.pptx theme: #1A365D navy, #00B4D8 cyan, #F8FAFC light bg.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import shutil, os

# ── PALETTE (exact match to Final.pptx) ──────────────────────────────────────
BG_LIGHT  = RGBColor(0xF8, 0xFA, 0xFC)
NAVY      = RGBColor(0x1A, 0x36, 0x5D)
CYAN      = RGBColor(0x00, 0xB4, 0xD8)
CYAN2     = RGBColor(0x2B, 0xDE, 0xFD)
BODY      = RGBColor(0x11, 0x11, 0x11)
MUTED     = RGBColor(0x55, 0x80, 0xA0)
GREEN     = RGBColor(0x05, 0x96, 0x69)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
CARD_WH   = RGBColor(0xFF, 0xFF, 0xFF)
FOOTER_NV = RGBColor(0x0F, 0x20, 0x3C)
BORDER    = RGBColor(0xE2, 0xE8, 0xF0)
GOLD      = RGBColor(0xF5, 0x9E, 0x0B)
RED_SOFT  = RGBColor(0xDC, 0x26, 0x26)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def bg(slide, color=None):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color or BG_LIGHT

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

def txt(slide, text, l, t, w, h, sz=10, bold=False, color=None,
        align=PP_ALIGN.LEFT, italic=False):
    b = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = b.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = Pt(sz); r.font.bold = bold; r.font.italic = italic
    r.font.color.rgb = color or BODY
    return b

def multi_txt(slide, l, t, w, h, lines, default_sz=9, default_col=None):
    """Add multiple paragraphs with different formatting."""
    b = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = b.text_frame; tf.word_wrap = True
    for i, (text, sz, bold, col) in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.space_after = Pt(2)
        r = p.add_run(); r.text = text
        r.font.size = Pt(sz or default_sz)
        r.font.bold = bold
        r.font.color.rgb = col or default_col or BODY
    return b

def hdr_bar(slide):
    """Top navy header bar + cyan accent line — matches Final.pptx."""
    rect(slide, 0, 0, 10.0, 0.95, fill=FOOTER_NV)
    rect(slide, 0, 0.95, 10.0, 0.04, fill=CYAN)

def footer_bar(slide):
    """Bottom navy bar — matches Final.pptx slide 14."""
    rect(slide, 0, 5.0, 10.0, 0.62, fill=FOOTER_NV)

def slide_head(slide, title, subtitle=None):
    """Main title in header band."""
    txt(slide, title, 0.4, 0.15, 9.0, 0.38,
        sz=18, bold=True, color=WHITE)
    if subtitle:
        txt(slide, subtitle, 0.4, 0.55, 9.0, 0.28,
            sz=9, color=CYAN)

def decor_dots(slide, positions):
    """Add small decorative accent dots — gives the human/elite touch."""
    for x, y, col in positions:
        rect(slide, x, y, 0.08, 0.08, fill=col, rnd=50000)

def accent_line(slide, l, t, w, col=None):
    """Thin accent line."""
    rect(slide, l, t, w, 0.03, fill=col or CYAN)

def card_box(slide, l, t, w, h, accent_col=None):
    """White card with optional top accent bar — matches Final.pptx white cards."""
    rect(slide, l, t, w, h, fill=CARD_WH, bd=BORDER, bw=Pt(0.5), rnd=10000)
    if accent_col:
        rect(slide, l, t, w, 0.04, fill=accent_col, rnd=10000)

# ── FGM gradient strip ───────────────────────────────────────────────────────
FGM_COLS = [
    RGBColor(0x00,0xE5,0xA0), RGBColor(0x17,0xE6,0xA8),
    RGBColor(0x2E,0xE6,0xB1), RGBColor(0x46,0xE7,0xB9),
    RGBColor(0x5D,0xE8,0xC1), RGBColor(0x74,0xE9,0xCA),
    RGBColor(0x8B,0xE9,0xD2), RGBColor(0xA2,0xEA,0xDA),
    RGBColor(0xBA,0xEB,0xE2), RGBColor(0xD1,0xEB,0xEB),
    RGBColor(0xE8,0xEC,0xF3),
]

def fgm_strip(slide, l, t, w, h):
    cw = w / 11
    for i, col in enumerate(FGM_COLS):
        rect(slide, l + i*cw, t, cw+0.01, h, fill=col)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
src = "CrystalParadigm_SCIDIP_PitchDeck_Final.pptx"
out = "CrystalParadigm_SCIDIP_IITDelhi_FINAL.pptx"
shutil.copy2(src, out)

prs = Presentation(out)
SW = prs.slide_width.inches   # 10.00
SH = prs.slide_height.inches  # 5.62
blank_layout = prs.slide_layouts[0]  # only layout available

print(f"Original slides: {len(prs.slides)}, Size: {SW:.2f}\" x {SH:.2f}\"")

# ═══════════════════════════════════════════════════════════════════════════════
# NEW SLIDE A: THE SCIDIP CROSSOVER — FROM AEROSPACE TO MOBILITY
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s)
hdr_bar(s)
slide_head(s, "THE SCIDIP CROSSOVER: FROM AEROSPACE TO EPIC MOBILITY",
           "If our AI can prevent a jet turbine from melting at 1400°C, it can revolutionize terrestrial mobility.")

# Decorative dots
decor_dots(s, [(9.5, 0.2, CYAN2), (9.35, 0.35, CYAN), (9.2, 0.18, RGBColor(0x00,0xE5,0xA0))])

txt(s, "We are entering the IIT Delhi SCIDIP program under the Advanced Materials category "
    "because Sona Comstar's EPIC roadmap is directly bottlenecked by the same thermodynamics "
    "that cap aerospace performance.",
    0.4, 1.1, 9.2, 0.42, sz=9.5, color=MUTED)

# Three-box crossover bridge
boxes = [
    ("AEROSPACE\nEXTREMES", NAVY, "1400°C\nTurbine TET",
     "Safran RISE Program"),
    ("CRYSTAL PARADIGM\nAI ENGINE", CYAN, "Universal\nMaterials Optimizer",
     "9-Element RHEA + 11-Layer FGM"),
    ("SONA COMSTAR\nEPIC ROADMAP", GREEN, "H13 Dies &\nEV SRM Motors",
     "Electric · Personalized · Intelligent · Connected"),
]
bx = 0.3
for i, (title, col, metric, sub) in enumerate(boxes):
    bw = 2.65
    card_box(s, bx, 1.58, bw, 1.82, col)
    txt(s, title, bx+0.12, 1.66, bw-0.2, 0.32, sz=8, bold=True, color=col, align=PP_ALIGN.CENTER)
    # Metric highlight
    rect(s, bx+0.18, 2.0, bw-0.36, 0.65, fill=BG_LIGHT, bd=col, bw=Pt(0.5), rnd=8000)
    txt(s, metric, bx+0.18, 2.05, bw-0.36, 0.55, sz=14, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(s, sub, bx+0.12, 2.72, bw-0.2, 0.55, sz=7.5, color=MUTED, align=PP_ALIGN.CENTER)
    # Arrow between boxes
    if i < 2:
        txt(s, "→", bx+bw+0.06, 2.02, 0.45, 0.4, sz=20, bold=True, color=CYAN, align=PP_ALIGN.CENTER)
    bx += bw + 0.55

# Two deployment cards
txt(s, "THE TWO THERMAL BOTTLENECKS WE SOLVE FOR SONA COMSTAR",
    0.4, 3.52, 9.2, 0.22, sz=9, bold=True, color=NAVY)
accent_line(s, 0.4, 3.75, 9.2)

for i, (title, col, body) in enumerate([
    ("① PRECISION FORGING DIES (Driveline)",  GOLD,
     "Legacy H13 tool steel dies suffer rapid thermal fatigue at 1200°C during "
     "high-speed gear forging. Our HEA retains >917.7 MPa yield strength."),
    ("② NEXT-GEN TRACTION MOTORS (Electric)", GREEN,
     "As Sona Comstar scales magnet-less SRMs, traditional metals degrade under "
     "extreme localized thermal loads. Our FGM provides aerospace-grade thermal shielding."),
]):
    cx = 0.3 + i * 4.75
    card_box(s, cx, 3.85, 4.55, 1.22, col)
    txt(s, title, cx+0.12, 3.94, 4.3, 0.22, sz=8, bold=True, color=col)
    txt(s, body, cx+0.12, 4.2, 4.3, 0.78, sz=8.5, color=BODY)

# FGM strip at bottom
fgm_strip(s, 0.3, 5.15, 9.4, 0.18)
txt(s, "Layer 1: 100% Alloy → Layer 11: 100% LZO Ceramic",
    0.3, 5.35, 9.4, 0.16, sz=6.5, color=MUTED, align=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════════
# NEW SLIDE B: SCIDIP DEPLOYMENT — FORGING DIES + EV MOTORS (combined)
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s)
hdr_bar(s)
slide_head(s, "SCIDIP DEPLOYMENT: TWO PATHWAYS TO COMMERCIALIZATION",
           "Solving Sona Comstar's Thermal Bottlenecks with Aerospace-Grade Materials")

decor_dots(s, [(0.3, 1.08, CYAN), (0.42, 1.08, CYAN2)])

# Left card: Forging Dies
card_box(s, 0.3, 1.18, 4.55, 3.75, NAVY)
txt(s, "DEPLOYMENT 1", 0.42, 1.28, 1.5, 0.18, sz=7, bold=True, color=CYAN)
txt(s, "Next-Gen Forging Dies", 0.42, 1.48, 4.2, 0.26, sz=12, bold=True, color=NAVY)
txt(s, "Solving Sona Comstar's Differential Gear Bottleneck",
    0.42, 1.76, 4.2, 0.2, sz=8, color=MUTED)
accent_line(s, 0.42, 1.98, 4.2, NAVY)

# Problem vs Solution mini-cards
rect(s, 0.42, 2.08, 2.0, 0.82, fill=RGBColor(0xFF,0xF1,0xF0), bd=RED_SOFT, bw=Pt(0.5), rnd=6000)
txt(s, "LEGACY H13", 0.5, 2.12, 1.8, 0.16, sz=7, bold=True, color=RED_SOFT)
txt(s, "· Yield collapse at 1200°C\n· Rapid thermal fatigue\n· Frequent die cracking",
    0.5, 2.3, 1.8, 0.55, sz=7, color=BODY)

rect(s, 2.52, 2.08, 2.2, 0.82, fill=RGBColor(0xEC,0xFD,0xF5), bd=GREEN, bw=Pt(0.5), rnd=6000)
txt(s, "CANDIDATE C FGM", 2.6, 2.12, 2.0, 0.16, sz=7, bold=True, color=GREEN)
txt(s, "· >917.7 MPa at 1200°C\n· LZO thermal barrier\n· Zero delamination",
    2.6, 2.3, 2.0, 0.55, sz=7, color=BODY)

# Three upgrade details
upgrades = [("The Core", "HEA retains >917.7 MPa yield strength — no mechanical deformation under forging pressures."),
            ("The Surface", "LZO ceramic outer layer acts as supreme thermal barrier, preventing heat into die."),
            ("The Result", "Elimination of thermal fatigue cracking — vastly extending tooling life.")]
uy = 2.98
for title, body in upgrades:
    rect(s, 0.42, uy, 0.06, 0.52, fill=CYAN)
    txt(s, title, 0.56, uy, 1.2, 0.16, sz=7.5, bold=True, color=NAVY)
    txt(s, body, 0.56, uy+0.18, 4.1, 0.32, sz=7, color=MUTED)
    uy += 0.58

# Right card: EV Motors
card_box(s, 5.15, 1.18, 4.55, 3.75, GREEN)
txt(s, "DEPLOYMENT 2", 5.27, 1.28, 1.5, 0.18, sz=7, bold=True, color=CYAN)
txt(s, "Magnet-Less EV Motors", 5.27, 1.48, 4.2, 0.26, sz=12, bold=True, color=NAVY)
txt(s, "Enabling Rare-Earth Independence in Traction Motors",
    5.27, 1.76, 4.2, 0.2, sz=8, color=MUTED)
accent_line(s, 5.27, 1.98, 4.2, GREEN)

txt(s, "As part of Sona Comstar's EPIC roadmap, they are scaling Switched Reluctance "
    "Motors (SRMs) to eliminate dependence on imported Neodymium magnets.",
    5.27, 2.1, 4.2, 0.42, sz=8, color=BODY)

# Supply chain highlight
rect(s, 5.27, 2.58, 4.2, 0.55, fill=RGBColor(0xF0,0xFD,0xFA), bd=GREEN, bw=Pt(0.5), rnd=6000)
txt(s, "SUPPLY CHAIN IMPACT", 5.35, 2.62, 3.0, 0.16, sz=7, bold=True, color=GREEN)
txt(s, "80%+ of global Neodymium controlled by China. Crystal Paradigm eliminates "
    "this dependency with indigenous Titanium-based alloys (~$170/kg).",
    5.35, 2.78, 4.0, 0.3, sz=7.5, color=BODY)

upgrades2 = [
    ("Thermal Shielding", "FGM gradient handles rapid cycling — 15.95 MPa interface shear stress."),
    ("Make-In-India", "Hafnium→Titanium substitution drops cost to ~$170/kg for Indian EV manufacturing."),
    ("ESG Compliance", "Embodied Energy: 1680 MJ/kg — qualifies for Sona Comstar 75% Supplier Score."),
]
uy = 3.22
for title, body in upgrades2:
    rect(s, 5.27, uy, 0.06, 0.52, fill=GREEN)
    txt(s, title, 5.4, uy, 1.5, 0.16, sz=7.5, bold=True, color=NAVY)
    txt(s, body, 5.4, uy+0.18, 4.0, 0.32, sz=7, color=MUTED)
    uy += 0.58

footer_bar(s)
txt(s, "Crystal Paradigm  ·  SCIDIP Program Application", 0.4, 5.12, 5.0, 0.2, sz=7, color=CYAN)

# ═══════════════════════════════════════════════════════════════════════════════
# NEW SLIDE C: IP & SUPPLY CHAIN DE-RISKING
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s)
hdr_bar(s)
slide_head(s, "INTELLECTUAL PROPERTY & DE-RISKING THE SUPPLY CHAIN",
           "True Aatmanirbharta for the Indian Mobility Sector")

decor_dots(s, [(9.55, 0.12, CYAN2), (9.68, 0.25, GREEN), (0.18, 0.12, CYAN)])

# Dependency → Innovation bridge
rect(s, 0.3, 1.1, 4.0, 0.7, fill=RGBColor(0xFF,0xF1,0xF0), bd=RED_SOFT, bw=Pt(0.5), rnd=8000)
txt(s, "CURRENT DEPENDENCY", 0.42, 1.15, 3.7, 0.16, sz=7, bold=True, color=RED_SOFT)
txt(s, "Foreign-controlled Neodymium & Rare-Earth imports for EV motors\n(80%+ China-controlled supply chain)",
    0.42, 1.34, 3.7, 0.4, sz=7.5, color=BODY)

txt(s, "→", 4.4, 1.2, 0.5, 0.45, sz=18, bold=True, color=CYAN, align=PP_ALIGN.CENTER)

rect(s, 5.0, 1.1, 4.7, 0.7, fill=RGBColor(0xEC,0xFD,0xF5), bd=GREEN, bw=Pt(0.5), rnd=8000)
txt(s, "INDIGENOUS INDIAN INNOVATION", 5.12, 1.15, 4.4, 0.16, sz=7, bold=True, color=GREEN)
txt(s, "Powered by Crystal Paradigm AI + IIT Delhi — built on globally abundant\nTitanium & Chromium for true supply chain security",
    5.12, 1.34, 4.4, 0.4, sz=7.5, color=BODY)

# Three IP pillars
pillars = [
    ("The IP Moat", NAVY,
     "Our proprietary 11-phase AI architecture is a continuous IP generation engine. "
     "Candidate C is merely our first output — we can computationally generate bespoke "
     "materials for any thermal bottleneck Sona Comstar faces across all four EPIC verticals."),
    ("Make-in-India Reality", GREEN,
     "By engineering out exotic, foreign-controlled minerals and optimizing around "
     "globally abundant Titanium and Chromium, we guarantee a secure, indigenous supply "
     "chain for Sona Comstar's next-generation EV components."),
    ("IIT Delhi IP Framework", CYAN,
     "We are prepared to navigate the FITT incubation framework to jointly patent "
     "physical material formulations developed within the Central Research Facility (CRF), "
     "ensuring robust legal IP protection for all innovations generated during SCIDIP."),
]
px = 0.3
for title, col, body in pillars:
    pw = 3.08
    card_box(s, px, 1.95, pw, 2.65, col)
    # Numbered circle
    rect(s, px + pw/2 - 0.18, 2.04, 0.36, 0.36, fill=col, rnd=50000)
    txt(s, str(pillars.index((title,col,body))+1), px+pw/2-0.18, 2.06, 0.36, 0.3,
        sz=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s, title, px+0.12, 2.48, pw-0.2, 0.22, sz=9, bold=True, color=col, align=PP_ALIGN.CENTER)
    accent_line(s, px+0.3, 2.72, pw-0.6, col)
    txt(s, body, px+0.12, 2.82, pw-0.2, 1.65, sz=8, color=BODY)
    px += pw + 0.18

# Bottom callout — Sona Comstar acquisition pattern insight
rect(s, 0.3, 4.72, 9.4, 0.42, fill=FOOTER_NV, rnd=6000)
txt(s, "STRATEGIC INSIGHT: Sona Comstar uses a 'buy & build' strategy — they actively form JVs "
    "(DENSO, 2026) and acquire startups (NOVELIC, 2023) to plug technological gaps. "
    "Crystal Paradigm's IP is engineered for this exact corporate integration pathway.",
    0.45, 4.78, 9.0, 0.32, sz=7.5, color=CYAN)

footer_bar(s)
txt(s, "Crystal Paradigm  ·  SCIDIP Program Application", 0.4, 5.12, 5.0, 0.2, sz=7, color=CYAN)

# ═══════════════════════════════════════════════════════════════════════════════
# NEW SLIDE D: THE CORPORATE ASK (4 PILLARS)
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s)
hdr_bar(s)
slide_head(s, "THE CRYSTAL PARADIGM CORPORATE ASK",
           "Bridging the Gap Between Informatics and the Factory Floor")

txt(s, "Crystal Paradigm is completely computationally validated (TRL 3+). We are applying "
    "to the Advanced Materials track to access the precise ecosystem to cross the \"valley of death\".",
    0.4, 1.08, 9.2, 0.35, sz=8.5, color=MUTED)

# TRL progression bar
rect(s, 0.3, 1.48, 9.4, 0.38, fill=FOOTER_NV, rnd=6000)
stages = [("TRL 1-2", 0.8, MUTED), ("TRL 3+ ✓ NOW", 3.2, GREEN),
          ("TRL 4-5 (SCIDIP TARGET)", 5.8, CYAN2), ("TRL 6 COMMERCIALIZATION", 8.2, GOLD)]
for label, lx, col in stages:
    txt(s, label, lx, 1.52, 2.0, 0.28, sz=7, bold=True, color=col, align=PP_ALIGN.CENTER)
# Progress dots
for x in [2.5, 5.0, 7.3]:
    rect(s, x, 1.6, 0.14, 0.14, fill=CYAN, rnd=50000)

# Four pillar cards
ask_pillars = [
    ("1", "Technology &\nLab Support", "IIT Delhi CRF", CYAN,
     "Access NIDHI-CoE and CRF: High-Temperature XRD, SEM/EDS, "
     "Simultaneous Thermal Analysis (STA) on physical witness coupons."),
    ("2", "Sona Comstar\nMentorship", "Engineering Alignment", NAVY,
     "Direct alignment with Sona Comstar's precision forging division "
     "to match our 11-layer print matrices to factory-floor DED tolerances."),
    ("3", "SCIDIP Seed\nEcosystem", "₹80L Grant-in-Aid", GREEN,
     "Integration into the SCIDIP funding framework to finance "
     "raw material atomization and multi-hopper 3D printing of prototypes."),
    ("4", "Corporate\nMarket Connect", "Supply Chain Access", GOLD,
     "Joint integration of physical prototypes into Sona Comstar's "
     "downstream EV supply chain — forging dies and SRM stator components."),
]
px = 0.3
for num, title, subtitle, col, body in ask_pillars:
    pw = 2.28
    card_box(s, px, 1.98, pw, 2.85, col)
    # Number circle
    rect(s, px+pw/2-0.2, 2.08, 0.4, 0.4, fill=col, rnd=50000)
    txt(s, num, px+pw/2-0.2, 2.1, 0.4, 0.35,
        sz=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s, title, px+0.1, 2.55, pw-0.2, 0.38, sz=9, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    txt(s, subtitle, px+0.1, 2.95, pw-0.2, 0.18, sz=7, color=col, align=PP_ALIGN.CENTER)
    accent_line(s, px+0.25, 3.18, pw-0.5, col)
    txt(s, body, px+0.1, 3.28, pw-0.2, 1.42, sz=7.5, color=BODY, align=PP_ALIGN.CENTER)
    px += pw + 0.12

footer_bar(s)
txt(s, "Crystal Paradigm  ·  SCIDIP Program Application", 0.4, 5.12, 5.0, 0.2, sz=7, color=CYAN)

# ═══════════════════════════════════════════════════════════════════════════════
# NEW SLIDE E: 24-MONTH INCUBATION ROADMAP
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s)
hdr_bar(s)
slide_head(s, "THE 24-MONTH INCUBATION ROADMAP",
           "From Computational Validation to Sona Comstar Integration · AIC IIT Delhi")

txt(s, "Our execution strategy is strictly mapped to the 24-month SCIDIP incubation cycle at "
    "Atal Incubation Centre (AIC), IIT Delhi.",
    0.4, 1.08, 9.2, 0.28, sz=8.5, color=MUTED)

# Timeline spine
rect(s, 0.6, 1.52, 8.8, 0.04, fill=BORDER)
# Milestone dots on spine
ms_colors = [CYAN, NAVY, GREEN, GOLD]
ms_x = [1.6, 3.85, 6.1, 8.35]
for x, col in zip(ms_x, ms_colors):
    rect(s, x-0.14, 1.42, 0.28, 0.28, fill=col, rnd=50000)

milestones = [
    ("M1", "MONTHS 1–6", "Powder\nSynthesis", CYAN,
     "Procure raw metal powders (Ta, W, Cr, V, Ti, Zr, Hf, Al). "
     "IIT Delhi labs verify composition purity and atomization quality."),
    ("M2", "MONTHS 6–12", "Additive\nManufacturing", NAVY,
     "Execute 11-layer manufacturing_recipe.csv via DED (Directed Energy "
     "Deposition) to print physical witness coupons."),
    ("M3", "MONTHS 12–18", "NIDHI-CoE &\nCRF Testing", GREEN,
     "Physical yield strength, High-Temp XRD, STA thermal shock validation "
     "at IIT Delhi. Validate the 1.50 Safety Factor."),
    ("M4", "MONTHS 18–24", "Corporate\nHandover", GOLD,
     "Present fully validated TRL 5/6 hardware to Sona Comstar for direct "
     "integration into H13 forging dies and SRM stator prototypes."),
]
mx = 0.4
for tag, period, title, col, body in milestones:
    mw = 2.2
    card_box(s, mx, 1.78, mw, 3.15, col)
    txt(s, tag, mx+0.08, 1.86, 0.4, 0.16, sz=7, bold=True, color=WHITE)
    rect(s, mx+0.08, 1.84, 0.35, 0.2, fill=col, rnd=4000)
    txt(s, tag, mx+0.1, 1.86, 0.32, 0.16, sz=7, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s, period, mx+0.5, 1.86, 1.6, 0.16, sz=7, color=col)
    txt(s, title, mx+0.1, 2.08, mw-0.2, 0.38, sz=10, bold=True, color=NAVY)
    accent_line(s, mx+0.1, 2.48, mw-0.2, col)
    txt(s, body, mx+0.1, 2.58, mw-0.2, 2.2, sz=7.5, color=BODY)
    mx += mw + 0.15

footer_bar(s)
txt(s, "Crystal Paradigm  ·  SCIDIP Program Application", 0.4, 5.12, 5.0, 0.2, sz=7, color=CYAN)

# ═══════════════════════════════════════════════════════════════════════════════
# NEW SLIDE F: THE TEAM (Combined Research Leads + AI Architects)
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s)
hdr_bar(s)
slide_head(s, "THE CRYSTAL PARADIGM TEAM",
           "Guided by Elite Academic Expertise · Powered by Prodigious AI Engineering")

decor_dots(s, [(9.55, 0.15, CYAN2), (9.42, 0.28, GREEN)])

# Research Leads section header
txt(s, "RESEARCH LEADS", 0.4, 1.08, 3.0, 0.18, sz=7, bold=True, color=CYAN)
accent_line(s, 0.4, 1.28, 9.2)

# Dr. Shilpa card
card_box(s, 0.3, 1.38, 4.55, 1.55, CYAN)
rect(s, 0.42, 1.48, 0.55, 0.55, fill=BG_LIGHT, bd=CYAN, bw=Pt(0.5), rnd=50000)
txt(s, "Dr", 0.44, 1.55, 0.5, 0.35, sz=11, bold=True, color=CYAN, align=PP_ALIGN.CENTER)
txt(s, "Dr. Shilpa Choudhary", 1.05, 1.48, 3.6, 0.2, sz=9.5, bold=True, color=NAVY)
txt(s, "AI / ML Lead", 1.05, 1.68, 3.6, 0.16, sz=7.5, color=CYAN)
txt(s, "· Top 2% Scientists Worldwide — Stanford University (2024)\n"
    "· 16+ years AI & Deep Learning research · Postdoc: Singapore & Taiwan\n"
    "· 100+ papers · 1763 citations · H-index 22 · 12 books · Multiple patents\n"
    "· Leads ML Architecture, Constrained Optimization & Surrogate Model Design",
    0.42, 1.92, 4.3, 0.88, sz=7, color=BODY)

# Dr. Venkataramana card
card_box(s, 5.15, 1.38, 4.55, 1.55, NAVY)
rect(s, 5.27, 1.48, 0.55, 0.55, fill=BG_LIGHT, bd=NAVY, bw=Pt(0.5), rnd=50000)
txt(s, "Dr", 5.29, 1.55, 0.5, 0.35, sz=11, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
txt(s, "Dr. Kasarapu Venkataramana", 5.9, 1.48, 3.6, 0.2, sz=9, bold=True, color=NAVY)
txt(s, "Materials Science & Experimental Validation Lead", 5.9, 1.68, 3.6, 0.16, sz=6.5, color=NAVY)
txt(s, "· Research Associate, CSIR-IICT (DRDO sponsored project)\n"
    "· Associate Fellow, Telangana Academy of Sciences (2024)\n"
    "· 38 publications · 610+ citations · H-index 14 · Reviewer: Elsevier, Springer\n"
    "· Specialization: High Entropy Oxides, XRD, SEM/EDS characterization",
    5.27, 1.92, 4.3, 0.88, sz=7, color=BODY)

# AI Architects section header
txt(s, "CORE AI ARCHITECTS", 0.4, 3.05, 3.0, 0.18, sz=7, bold=True, color=CYAN)
accent_line(s, 0.4, 3.24, 9.2)

# Mohammed card
card_box(s, 0.3, 3.32, 4.55, 1.22, CYAN)
rect(s, 0.42, 3.42, 0.42, 0.42, fill=BG_LIGHT, bd=CYAN, bw=Pt(0.5), rnd=50000)
txt(s, "AI", 0.44, 3.48, 0.38, 0.28, sz=8, bold=True, color=CYAN, align=PP_ALIGN.CENTER)
txt(s, "Mohammed Ahmed Raza", 0.92, 3.42, 3.7, 0.18, sz=8.5, bold=True, color=NAVY)
txt(s, "AI Research Intern", 0.92, 3.6, 3.7, 0.14, sz=7, color=CYAN)
txt(s, "· CSE — NGIT · Certified AI/ML — iHub-Data, IIIT Hyderabad\n"
    "· Winter Research Intern, IIIT Hyderabad — UAV spatial awareness\n"
    "· Co-authored Attention Graph Siamese Transformer (DPT-GNN) for Li-ion prediction",
    0.42, 3.78, 4.3, 0.68, sz=6.5, color=BODY)

# Indra card
card_box(s, 5.15, 3.32, 4.55, 1.22, NAVY)
rect(s, 5.27, 3.42, 0.42, 0.42, fill=BG_LIGHT, bd=NAVY, bw=Pt(0.5), rnd=50000)
txt(s, "AI", 5.29, 3.48, 0.38, 0.28, sz=8, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
txt(s, "K. Indrasena Reddy [Indra]", 5.77, 3.42, 3.7, 0.18, sz=8.5, bold=True, color=NAVY)
txt(s, "AI Research Intern", 5.77, 3.6, 3.7, 0.14, sz=7, color=NAVY)
txt(s, "· CSE — NGIT · AI Developer Intern, Viswam.AI — NLP & LLM research\n"
    "· Materials informatics & graph neural network modeling at Crystal Paradigm\n"
    "· Specialization: Large-scale property prediction & advanced GNN architectures",
    5.27, 3.78, 4.3, 0.68, sz=6.5, color=BODY)

# Extended team banner
rect(s, 0.3, 4.62, 9.4, 0.35, fill=FOOTER_NV, rnd=6000)
txt(s, "EXTENDED TEAM: 18 specialized AI Research Interns — "
    "massive parallel execution bandwidth for multi-physics simulations & AI training pipelines",
    0.45, 4.67, 9.0, 0.24, sz=7.5, color=CYAN)

footer_bar(s)
txt(s, "Crystal Paradigm  ·  SCIDIP Program Application", 0.4, 5.12, 5.0, 0.2, sz=7, color=CYAN)

# ═══════════════════════════════════════════════════════════════════════════════
# REORDER: Move original slide 14 (Closing) to the very end
# ═══════════════════════════════════════════════════════════════════════════════
try:
    prs_element = prs.part._element
    sldIdLst = prs_element.find(qn('p:sldIdLst'))
    slide_elements = list(sldIdLst)

    # Original slide 14 is at index 13 (0-based)
    closing = slide_elements[13]
    sldIdLst.remove(closing)
    sldIdLst.append(closing)
    print(f"Reordered: Closing slide moved to last position")
except Exception as e:
    print(f"Note: Could not reorder slides ({e}). Closing may not be last.")

# ─── SAVE ────────────────────────────────────────────────────────────────────
prs.save(out)
print(f"\nSUCCESS: {out} generated with {len(prs.slides)} slides")
print("Original 14 slides preserved + 6 new slides added.")
print("Closing slide moved to last position.")
