"""
CRYSTAL PARADIGM - ELITE HYBRID PITCH DECK GENERATOR
=====================================================
Strategy:
- Background: Deep Slate (#1A1F35) - Premium mid-tone, not pitch black, not white
- Accent: Electric Teal (#00E5A0) - Crystal Paradigm brand accent
- Data boxes: Navy (#0D1628) with subtle borders
- Text: Off-White (#F5F7FA) on dark, Dark Navy on light elements
- Visualization style: Recreates the 'by claude' multi-column card layout
  but with PERFECT padding/sizing to eliminate all overlaps
- Logo: Extracted position/usage pattern from Final.pptx slide 1
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from lxml import etree
import copy
import os

# ─── COLOR PALETTE ────────────────────────────────────────────────────────────
BG_DARK       = RGBColor(0x14, 0x1A, 0x2E)   # Deep Space Blue (background)
BG_CARD       = RGBColor(0x1E, 0x27, 0x45)   # Card background
BG_CARD2      = RGBColor(0x0D, 0x13, 0x28)   # Deeper card
ACCENT_TEAL   = RGBColor(0x00, 0xE5, 0xA0)   # Crystal Paradigm Teal
ACCENT_GOLD   = RGBColor(0xF5, 0xA6, 0x23)   # Gold for highlights
TEXT_PRIMARY  = RGBColor(0xF5, 0xF7, 0xFA)   # Off-White main text
TEXT_SECONDARY= RGBColor(0xAA, 0xB4, 0xC6)   # Muted secondary text
TEXT_ACCENT   = RGBColor(0x00, 0xE5, 0xA0)   # Teal for labels
BORDER_COLOR  = RGBColor(0x2D, 0x3A, 0x5E)   # Subtle border
GREEN_STATUS  = RGBColor(0x00, 0xC8, 0x7A)   # Status green
YELLOW_STATUS = RGBColor(0xF5, 0xA6, 0x23)   # Status yellow
RED_ALERT     = RGBColor(0xFF, 0x4D, 0x6D)   # Alert red

# ─── SLIDE DIMENSIONS (Widescreen 13.33 x 7.5 inches) ─────────────────────────
W = Inches(13.33)
H = Inches(7.5)

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def new_prs():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    return prs

def blank_slide(prs):
    blank_layout = prs.slide_layouts[6]  # completely blank
    return prs.slides.add_slide(blank_layout)

def set_bg(slide, color: RGBColor):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_rect(slide, l, t, w, h, fill_color=None, border_color=None, border_width=Pt(0.5), radius=None):
    """Add a rectangle (optionally rounded) with fill and/or border."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(l), Inches(t), Inches(w), Inches(h)
    )
    # Fill
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    # Border
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = border_width
    else:
        shape.line.fill.background()
    # Rounded corners
    if radius:
        sp = shape.element
        prstGeom = sp.find(qn('p:spPr')).find(qn('a:prstGeom'))
        if prstGeom is not None:
            prstGeom.set('prst', 'roundRect')
            avLst = prstGeom.find(qn('a:avLst'))
            if avLst is None:
                avLst = etree.SubElement(prstGeom, qn('a:avLst'))
            else:
                for gd in avLst.findall(qn('a:gd')):
                    avLst.remove(gd)
            gd = etree.SubElement(avLst, qn('a:gd'))
            gd.set('name', 'adj')
            gd.set('fmla', f'val {radius}')
    return shape

def add_text(slide, text, l, t, w, h,
             font_size=12, bold=False, italic=False,
             color=None, align=PP_ALIGN.LEFT,
             v_anchor='middle', wrap=True):
    """Add a text box with precise settings."""
    txBox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = txBox.text_frame
    tf.word_wrap = wrap
    # Vertical anchor
    if v_anchor == 'top':
        tf.auto_size = None
    
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color if color else TEXT_PRIMARY
    return txBox

def add_label(slide, text, l, t, w=3.0, h=0.25, color=None):
    """Small uppercase label in teal."""
    return add_text(slide, text.upper(), l, t, w, h,
                    font_size=8, bold=True,
                    color=color or ACCENT_TEAL,
                    align=PP_ALIGN.LEFT)

def add_heading(slide, text, l, t, w, h, size=20, color=None):
    return add_text(slide, text, l, t, w, h,
                    font_size=size, bold=True,
                    color=color or TEXT_PRIMARY,
                    align=PP_ALIGN.LEFT)

def add_body(slide, text, l, t, w, h, size=11, color=None, align=PP_ALIGN.LEFT):
    return add_text(slide, text, l, t, w, h,
                    font_size=size, color=color or TEXT_SECONDARY,
                    align=align)

def add_slide_number(slide, num, total=18):
    add_text(slide, f"{num} / {total}",
             12.1, 7.1, 1.1, 0.28,
             font_size=8, color=RGBColor(0x6E,0x7A,0x90),
             align=PP_ALIGN.RIGHT)

def add_logo_text(slide, x=0.25, y=7.1):
    """Crystal Paradigm wordmark in corner."""
    add_text(slide, "CRYSTAL PARADIGM",
             x, y, 2.5, 0.3,
             font_size=8, bold=True,
             color=ACCENT_TEAL, align=PP_ALIGN.LEFT)

def add_footer_line(slide):
    """Horizontal separator line above footer."""
    line = add_rect(slide, 0, 6.88, 13.33, 0.01,
                    fill_color=BORDER_COLOR)

def add_card(slide, l, t, w, h, title=None, body=None,
             title_color=None, body_color=None, accent_bar=True):
    """Standard data card: rounded rect + optional accent bar + title + body."""
    add_rect(slide, l, t, w, h,
             fill_color=BG_CARD, border_color=BORDER_COLOR,
             border_width=Pt(0.75), radius=20000)
    if accent_bar:
        add_rect(slide, l, t, 0.04, h,
                 fill_color=ACCENT_TEAL, radius=20000)
    if title:
        add_text(slide, title, l+0.15, t+0.1, w-0.25, 0.28,
                 font_size=10, bold=True,
                 color=title_color or TEXT_PRIMARY)
    if body:
        add_text(slide, body, l+0.15, t+0.42, w-0.25, h-0.55,
                 font_size=10, color=body_color or TEXT_SECONDARY)

def add_metric_box(slide, l, t, w, h, metric, label, color=None):
    """A big number + small label metric box."""
    add_rect(slide, l, t, w, h,
             fill_color=BG_CARD2, border_color=color or ACCENT_TEAL,
             border_width=Pt(1.0), radius=20000)
    add_text(slide, metric, l+0.1, t+0.1, w-0.2, h*0.55,
             font_size=22, bold=True,
             color=color or ACCENT_TEAL, align=PP_ALIGN.CENTER)
    add_text(slide, label, l+0.1, t+h*0.58, w-0.2, h*0.35,
             font_size=9, color=TEXT_SECONDARY, align=PP_ALIGN.CENTER)

def add_step_chip(slide, l, t, number, label):
    """Numbered step chip."""
    add_rect(slide, l, t, 0.35, 0.35,
             fill_color=ACCENT_TEAL, radius=50000)
    add_text(slide, str(number), l, t+0.01, 0.35, 0.3,
             font_size=12, bold=True,
             color=RGBColor(0x14,0x1A,0x2E), align=PP_ALIGN.CENTER)
    add_text(slide, label, l+0.42, t+0.04, 3.0, 0.28,
             font_size=10, bold=True, color=TEXT_PRIMARY)

def add_status_row(slide, l, t, row_w, cols, status_color):
    """Render a table row for the validation table."""
    col_widths = [2.8, 2.4, 2.4, 2.1, 0.8]
    x = l
    for i, (txt, cw) in enumerate(zip(cols, col_widths)):
        bg = BG_CARD2 if i == 0 else BG_CARD
        add_rect(slide, x, t, cw-0.03, 0.38,
                 fill_color=bg, border_color=BORDER_COLOR,
                 border_width=Pt(0.5))
        if i == 4:  # status dot
            dot_color = GREEN_STATUS if "GREEN" in txt else YELLOW_STATUS
            add_rect(slide, x+cw/2-0.08, t+0.12, 0.15, 0.15,
                     fill_color=dot_color, radius=50000)
        else:
            add_text(slide, txt, x+0.08, t+0.06, cw-0.18, 0.28,
                     font_size=9, color=TEXT_SECONDARY if i>0 else TEXT_PRIMARY)
        x += cw

# ─────────────────────────────────────────────────────────────────────────────
# SLIDES
# ─────────────────────────────────────────────────────────────────────────────

prs = new_prs()

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 - Title & Introduction
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

# Large background geometric accent - top right quadrant
add_rect(slide, 7.8, -0.5, 6.0, 5.0,
         fill_color=RGBColor(0x1E,0x27,0x45), border_color=None)
add_rect(slide, 8.5, 0.3, 4.8, 4.2,
         fill_color=RGBColor(0x0D,0x13,0x28), border_color=BORDER_COLOR,
         border_width=Pt(0.75), radius=30000)

# Program badges
add_rect(slide, 0.5, 0.4, 2.5, 0.28,
         fill_color=RGBColor(0x00,0x3D,0x2B), border_color=ACCENT_TEAL,
         border_width=Pt(0.75), radius=30000)
add_text(slide, "SCIDIP PROGRAM APPLICATION", 0.55, 0.42, 2.4, 0.24,
         font_size=8, bold=True, color=ACCENT_TEAL)

add_text(slide, "Advanced Materials  ·  Advanced Batteries  ·  Electric Mobility  ·  Sustainability",
         0.5, 0.78, 9.0, 0.28, font_size=9, color=TEXT_SECONDARY)

# Main title
add_text(slide,
         "Accelerating Innovation\nat the Intersection of\nAI and Material Science",
         0.5, 1.2, 7.5, 2.4,
         font_size=32, bold=True, color=TEXT_PRIMARY)

# Teal accent underline
add_rect(slide, 0.5, 3.5, 2.5, 0.05, fill_color=ACCENT_TEAL)

# Tagline body
add_text(slide,
         "Crystal Paradigm is an elite Deep-Tech Discovery Platform. We leverage "
         "artificial intelligence and high-performance computing to accelerate "
         "material discovery from 5 years to 4 weeks.",
         0.5, 3.65, 7.2, 0.9, font_size=12, color=TEXT_SECONDARY)

# Three pipeline pills
pills = [
    ("1 Patent Accepted", ACCENT_TEAL),
    ("4 Papers Under Review", ACCENT_GOLD),
    ("Active Industry Collaborations", RGBColor(0x6E,0x9D,0xFF)),
]
px = 0.5
for label, col in pills:
    pw = 2.3
    add_rect(slide, px, 4.65, pw, 0.38,
             fill_color=RGBColor(0x1E,0x27,0x45),
             border_color=col, border_width=Pt(1.0), radius=30000)
    add_text(slide, label, px+0.12, 4.7, pw-0.2, 0.28,
             font_size=9, bold=True, color=col, align=PP_ALIGN.CENTER)
    px += pw + 0.18

# SCIDIP spearhead callout box
add_rect(slide, 0.5, 5.15, 7.2, 1.35,
         fill_color=BG_CARD2, border_color=ACCENT_GOLD,
         border_width=Pt(1.0), radius=20000)
add_rect(slide, 0.5, 5.15, 0.06, 1.35,
         fill_color=ACCENT_GOLD, radius=20000)
add_text(slide, "SCIDIP SPEARHEAD", 0.7, 5.2, 3.0, 0.25,
         font_size=8, bold=True, color=ACCENT_GOLD)
add_text(slide,
         "For this application, we deploy our most extreme, fully-validated Proof of Concept: "
         "An AI-generated, aerospace-grade Refractory High-Entropy Alloy (RHEA) engineered to "
         "solve Sona Comstar's terrestrial thermal bottlenecks.",
         0.7, 5.46, 6.8, 0.95, font_size=10, color=TEXT_SECONDARY)

# Right panel - metric boxes
metrics = [
    ("9", "Elements\nOptimized"),
    ("11", "FGM\nLayers"),
    ("1.71", "3D Safety\nFactor"),
    ("4 Wks", "Discovery\nTime"),
]
mx, my = 8.7, 0.55
for i, (val, lbl) in enumerate(metrics):
    cx = mx + (i % 2) * 2.0
    cy = my + (i // 2) * 2.0
    add_metric_box(slide, cx, cy, 1.75, 1.7, val, lbl)

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 1)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 - Aerospace Proof of Concept
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "AEROSPACE PROOF OF CONCEPT", 0.5, 0.28)
add_heading(slide, "PROVING THE PHYSICS: THE AEROSPACE THERMAL BOTTLENECK",
            0.5, 0.55, 11.0, 0.55, size=18)
add_rect(slide, 0.5, 1.08, 2.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide,
         "Our AI engine was built to solve the hardest thermal problem in modern engineering: "
         "Turbine Entry Temperatures (TET) exceeding 1400°C.",
         0.5, 1.2, 12.3, 0.45, font_size=11, color=TEXT_SECONDARY)

# Left column: The Problem
add_rect(slide, 0.5, 1.75, 5.9, 4.85,
         fill_color=BG_CARD, border_color=BORDER_COLOR,
         border_width=Pt(0.75), radius=20000)
add_rect(slide, 0.5, 1.75, 0.06, 4.85,
         fill_color=RGBColor(0xFF,0x4D,0x6D), radius=20000)
add_text(slide, "THE AEROTHERMAL FIRE LIMIT", 0.7, 1.85, 5.5, 0.28,
         font_size=10, bold=True, color=RGBColor(0xFF,0x4D,0x6D))
add_text(slide,
         "Traditional nickel-based superalloys have hit a physical ceiling. When shielded "
         "with ceramics, the massive Coefficient of Thermal Expansion (CTE) mismatch causes "
         "the protective armor to violently spall off under rapid thermal cycling.\n\n"
         "The Problem in Numbers:\n"
         "  ·  TET Target: > 1400°C\n"
         "  ·  Legacy Superalloy Limit: ~1000°C\n"
         "  ·  CTE Mismatch (Traditional): High → Coating Spallation\n"
         "  ·  Consequence: Catastrophic turbine blade failure",
         0.7, 2.2, 5.5, 4.2, font_size=10, color=TEXT_SECONDARY)

# Right column: The Solution
add_rect(slide, 6.93, 1.75, 5.9, 4.85,
         fill_color=BG_CARD, border_color=BORDER_COLOR,
         border_width=Pt(0.75), radius=20000)
add_rect(slide, 6.93, 1.75, 0.06, 4.85,
         fill_color=ACCENT_TEAL, radius=20000)
add_text(slide, "CRYSTAL PARADIGM AI SOLUTION — CANDIDATE C",
         7.13, 1.85, 5.5, 0.28, font_size=10, bold=True, color=ACCENT_TEAL)

solution_items = [
    ("The Physics",
     "By forcing a Titanium-dominant solid solution (21.7% Ti), we mathematically "
     "closed the CTE gap to just 2.66 μm/mK."),
    ("The Manufacturing",
     "Deployed an 11-layer Functionally Graded Material (FGM) matrix using an exact "
     "n=1.1 power-law gradient — ready for multi-hopper DED 3D printing."),
    ("The Result",
     "Interface shear stress dropped to an ultra-low 15.95 MPa, completely "
     "eliminating delamination under extreme thermal shock."),
    ("3D FEA Validation",
     "FEniCS Finite Element Analysis confirmed a 3D Safety Factor of 1.71 — "
     "exceeding the 1.50 airworthiness threshold by 14%."),
]
sy = 2.2
for title, body in solution_items:
    add_text(slide, f"▸  {title}", 7.13, sy, 5.5, 0.25,
             font_size=10, bold=True, color=ACCENT_TEAL)
    add_text(slide, body, 7.13, sy+0.28, 5.5, 0.65,
             font_size=9.5, color=TEXT_SECONDARY)
    sy += 1.02

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 2)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 - From Aerospace to Mobility (The Crossover)
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "FROM AEROSPACE TO MOBILITY", 0.5, 0.28)
add_heading(slide, "THE SCIDIP CROSSOVER: FROM AEROSPACE TO EPIC MOBILITY",
            0.5, 0.55, 12.0, 0.55, size=18)
add_rect(slide, 0.5, 1.08, 2.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide,
         "If our AI architecture can prevent a jet turbine from melting at 1400°C, "
         "it can revolutionize the thermal limits of terrestrial mobility.",
         0.5, 1.18, 12.3, 0.45, font_size=11, color=TEXT_SECONDARY)

# Crossover bridge visualization (3 boxes + arrows)
# Box 1: Aerospace
add_rect(slide, 0.4, 1.75, 3.5, 2.2,
         fill_color=BG_CARD2, border_color=RGBColor(0xFF,0x4D,0x6D),
         border_width=Pt(1.5), radius=20000)
add_text(slide, "AEROSPACE EXTREME", 0.55, 1.82, 3.2, 0.28,
         font_size=9, bold=True, color=RGBColor(0xFF,0x4D,0x6D), align=PP_ALIGN.CENTER)
add_text(slide, "1400°C\nTurbine\nEntry Temp",
         0.55, 2.1, 3.2, 1.2, font_size=20, bold=True,
         color=TEXT_PRIMARY, align=PP_ALIGN.CENTER)
add_text(slide, "Safran RISE Open-Rotor Program",
         0.55, 3.2, 3.2, 0.55, font_size=9, color=TEXT_SECONDARY, align=PP_ALIGN.CENTER)

# Arrow
add_text(slide, "→", 4.05, 2.35, 0.9, 0.7,
         font_size=36, bold=True, color=ACCENT_TEAL, align=PP_ALIGN.CENTER)

# Box 2: Crystal Paradigm AI Bridge
add_rect(slide, 5.0, 1.75, 3.33, 2.2,
         fill_color=RGBColor(0x00,0x3D,0x2B), border_color=ACCENT_TEAL,
         border_width=Pt(1.5), radius=20000)
add_text(slide, "CRYSTAL PARADIGM AI ENGINE", 5.1, 1.82, 3.1, 0.28,
         font_size=9, bold=True, color=ACCENT_TEAL, align=PP_ALIGN.CENTER)
add_text(slide, "The Universal\nMaterials\nOptimizer",
         5.1, 2.1, 3.1, 1.2, font_size=18, bold=True,
         color=TEXT_PRIMARY, align=PP_ALIGN.CENTER)
add_text(slide, "Refractory HEA + 11-Layer FGM",
         5.1, 3.2, 3.1, 0.55, font_size=9, color=TEXT_SECONDARY, align=PP_ALIGN.CENTER)

# Arrow
add_text(slide, "→", 8.45, 2.35, 0.9, 0.7,
         font_size=36, bold=True, color=ACCENT_TEAL, align=PP_ALIGN.CENTER)

# Box 3: Terrestrial Mobility
add_rect(slide, 9.4, 1.75, 3.5, 2.2,
         fill_color=BG_CARD2, border_color=ACCENT_GOLD,
         border_width=Pt(1.5), radius=20000)
add_text(slide, "SONA COMSTAR EPIC MOBILITY", 9.5, 1.82, 3.2, 0.28,
         font_size=9, bold=True, color=ACCENT_GOLD, align=PP_ALIGN.CENTER)
add_text(slide, "H13 Dies\n& EV SRMs",
         9.5, 2.1, 3.2, 1.2, font_size=20, bold=True,
         color=TEXT_PRIMARY, align=PP_ALIGN.CENTER)
add_text(slide, "Electric, Personalized, Intelligent, Connected",
         9.5, 3.2, 3.2, 0.55, font_size=9, color=TEXT_SECONDARY, align=PP_ALIGN.CENTER)

# Two deployment cards below
add_text(slide, "THE TWO THERMAL BOTTLENECKS WE SOLVE FOR SONA COMSTAR:",
         0.5, 4.08, 12.3, 0.3, font_size=10, bold=True, color=TEXT_PRIMARY)

# Card 1: Forging Dies
add_rect(slide, 0.5, 4.45, 6.1, 2.1,
         fill_color=BG_CARD, border_color=BORDER_COLOR,
         border_width=Pt(0.75), radius=20000)
add_rect(slide, 0.5, 4.45, 0.06, 2.1, fill_color=ACCENT_GOLD, radius=20000)
add_text(slide, "① PRECISION FORGING DIES (DRIVELINE)",
         0.7, 4.52, 5.7, 0.28, font_size=10, bold=True, color=ACCENT_GOLD)
add_text(slide,
         "Legacy H13 tool steel dies suffer rapid thermal fatigue and yield strength "
         "collapse at 1200°C during high-speed gear forging. Our HEA architectures "
         "retain >917.7 MPa yield strength at these exact temperatures.",
         0.7, 4.83, 5.7, 1.5, font_size=10, color=TEXT_SECONDARY)

# Card 2: EV Motors
add_rect(slide, 6.73, 4.45, 6.1, 2.1,
         fill_color=BG_CARD, border_color=BORDER_COLOR,
         border_width=Pt(0.75), radius=20000)
add_rect(slide, 6.73, 4.45, 0.06, 2.1, fill_color=ACCENT_TEAL, radius=20000)
add_text(slide, "② NEXT-GENERATION TRACTION MOTORS (ELECTRIC)",
         6.93, 4.52, 5.7, 0.28, font_size=10, bold=True, color=ACCENT_TEAL)
add_text(slide,
         "As Sona Comstar scales magnet-less Switched Reluctance Motors (SRMs), "
         "traditional metals degrade under severe localized thermal loads generated "
         "by extreme torque densities. Our FGM architecture provides thermal shielding.",
         6.93, 4.83, 5.7, 1.5, font_size=10, color=TEXT_SECONDARY)

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 3)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 - Strategic Commercialization
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "COMMERCIAL STRATEGY", 0.5, 0.28)
add_heading(slide, "DEPLOYING AEROSPACE GRADE MATERIALS AT COMMERCIAL SCALE",
            0.5, 0.55, 12.0, 0.55, size=18)
add_rect(slide, 0.5, 1.08, 2.5, 0.04, fill_color=ACCENT_TEAL)
add_text(slide,
         "Our AI engine does not just optimize for physics; it optimizes for the supply chain.",
         0.5, 1.18, 12.3, 0.35, font_size=11, color=TEXT_SECONDARY)

# Three-column impact grid
cols_data = [
    ("RAW MATERIAL COST", ACCENT_TEAL,
     "15-20%\nCost Drop",
     "By programmatically substituting supply-constrained Hafnium with optimized Titanium, "
     "our AI dropped raw material cost to ~$170/kg — enabling aerospace-grade materials "
     "viable for high-volume commercial automotive forging."),
    ("ESG & SUSTAINABILITY", ACCENT_GOLD,
     "1680\nMJ/kg",
     "Crystal Paradigm's Candidate C is fully quantified for environmental impact. "
     "Embodied Energy is capped at a highly sustainable 1680 MJ/kg — directly supporting "
     "zero-emissions manufacturing goals and Sona Comstar's Scope 1/2 carbon reduction mandate."),
    ("SUPPLY CHAIN RESILIENCE", RGBColor(0x6E,0x9D,0xFF),
     "Make in\nIndia IP",
     "By utilizing a 9-element multi-principal matrix, we drastically reduce reliance "
     "on single critical minerals (like Neodymium) controlled by volatile foreign supply chains. "
     "Our pipeline ensures true indigenous, self-reliant IP generation."),
]
cx = 0.5
for title, col, metric, body in cols_data:
    cw = 4.08
    # Column card
    add_rect(slide, cx, 1.65, cw, 5.3,
             fill_color=BG_CARD, border_color=col,
             border_width=Pt(1.0), radius=20000)
    # Top accent band
    add_rect(slide, cx, 1.65, cw, 0.05, fill_color=col, radius=20000)
    add_text(slide, title, cx+0.2, 1.75, cw-0.35, 0.35,
             font_size=9, bold=True, color=col)
    # Big metric
    add_text(slide, metric, cx+0.2, 2.12, cw-0.35, 1.2,
             font_size=24, bold=True, color=TEXT_PRIMARY, align=PP_ALIGN.CENTER)
    add_rect(slide, cx+0.5, 3.3, cw-1.0, 0.03, fill_color=BORDER_COLOR)
    # Body text
    add_text(slide, body, cx+0.2, 3.42, cw-0.35, 3.3,
             font_size=10, color=TEXT_SECONDARY)
    cx += cw + 0.14

# Bottom tagline
add_rect(slide, 0.5, 7.0, 12.33, 0.04, fill_color=BORDER_COLOR)

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 4)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 - AI Engine Step 1: Thermodynamic Gating
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "AI ENGINE · STEP 1 OF 3", 0.5, 0.28)
add_heading(slide, "THE CRYSTAL PARADIGM AI ENGINE: STEP 1",
            0.5, 0.55, 10.0, 0.4, size=18)
add_text(slide, "Secure Ingestion & Empirical Thermodynamic Gating",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide,
         "Before a single ML model is trained, our pipeline strictly enforces the laws of physics "
         "and commercial viability. We ingest massive combinatorial spaces (Materials Project, AFLOW), "
         "but ruthlessly filter out unstable or toxic formulations using Miedema's Empirical Rules "
         "to ensure day-one compliance with Sona Comstar's 75% Supplier ESG mandate.",
         0.5, 1.32, 12.3, 0.7, font_size=10.5, color=TEXT_SECONDARY)

# Four gating parameter cards in 2x2 grid
gating = [
    ("Atomic Size Mismatch (δ)", "≤ 6.6%",
     "Prevents lattice distortion under high torque. Ensures mechanical stability during high-speed gear forging."),
    ("Enthalpy of Mixing (ΔH_mix)", "-15 to +5 kJ/mol",
     "Ensures thermodynamically favorable mixing. Outside this band, the alloy phase-separates under thermal stress."),
    ("Valence Electron Concentration (VEC)", "4.0 – 6.8",
     "Guarantees a stable Body-Centered Cubic (BCC) matrix. VEC < 6.8 explicitly eliminates brittle Sigma phase risk."),
    ("Omega Parameter (Ω)", "≥ 1.1",
     "Guarantees dominant solid solution stability over intermetallic compound formation at target temperatures."),
]
gx, gy = 0.5, 2.1
for i, (title, val, body) in enumerate(gating):
    col_offset = (i % 2) * 6.35
    row_offset = (i // 2) * 2.42
    gw = 6.18
    gh = 2.2
    gl = gx + col_offset
    gt = gy + row_offset

    add_rect(slide, gl, gt, gw, gh,
             fill_color=BG_CARD, border_color=BORDER_COLOR,
             border_width=Pt(0.75), radius=20000)
    # Top teal bar
    add_rect(slide, gl, gt, gw, 0.05, fill_color=ACCENT_TEAL, radius=20000)
    add_text(slide, title, gl+0.18, gt+0.12, gw-0.3, 0.28,
             font_size=10, bold=True, color=TEXT_PRIMARY)
    # Big value
    add_rect(slide, gl+0.18, gt+0.45, gw-0.36, 0.48,
             fill_color=BG_CARD2, border_color=ACCENT_TEAL,
             border_width=Pt(0.75), radius=15000)
    add_text(slide, val, gl+0.18, gt+0.47, gw-0.36, 0.44,
             font_size=14, bold=True, color=ACCENT_TEAL, align=PP_ALIGN.CENTER)
    # Body
    add_text(slide, body, gl+0.18, gt+1.02, gw-0.3, 1.0,
             font_size=9.5, color=TEXT_SECONDARY)

# ESG compliance stamp
add_rect(slide, 9.8, 0.35, 3.1, 0.75,
         fill_color=RGBColor(0x00,0x3D,0x2B), border_color=ACCENT_TEAL,
         border_width=Pt(1.0), radius=20000)
add_text(slide, "✓  SONA COMSTAR 75%\n    SUPPLIER COMPLIANCE",
         9.9, 0.4, 2.9, 0.65, font_size=9, bold=True, color=ACCENT_TEAL)

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 5)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 - AI Engine Step 2: Machine Learning Surrogates
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "AI ENGINE · STEP 2 OF 3", 0.5, 0.28)
add_heading(slide, "THE CRYSTAL PARADIGM AI ENGINE: STEP 2",
            0.5, 0.55, 10.0, 0.4, size=18)
add_text(slide, "Dual-Stream Machine Learning Surrogates",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide,
         "To predict material behavior for Sona Comstar's extreme-environment SRMs and H13 forging dies, "
         "we engineered a dual-stream surrogate architecture mapping both theoretical physics and real-world variance.",
         0.5, 1.32, 12.3, 0.55, font_size=10.5, color=TEXT_SECONDARY)

# Model 1 - Left
add_rect(slide, 0.5, 2.0, 6.0, 5.0,
         fill_color=BG_CARD, border_color=BORDER_COLOR,
         border_width=Pt(0.75), radius=20000)
add_rect(slide, 0.5, 2.0, 0.06, 5.0, fill_color=ACCENT_TEAL, radius=20000)
add_text(slide, "MODEL 1", 0.7, 2.1, 5.6, 0.25, font_size=8, bold=True, color=ACCENT_TEAL)
add_text(slide, "Theoretical Bulk Modulus", 0.7, 2.33, 5.6, 0.32,
         font_size=14, bold=True, color=TEXT_PRIMARY)
add_text(slide, "Random Forest Surrogate", 0.7, 2.63, 5.6, 0.25,
         font_size=10, color=TEXT_SECONDARY)

# Performance metrics for Model 1
m1_metrics = [("Test R²", "0.977"), ("MAE", "8.11 GPa"), ("Estimators", "100")]
mx1 = 0.7
for mlabel, mval in m1_metrics:
    mw = 1.65
    add_rect(slide, mx1, 3.0, mw, 0.95,
             fill_color=BG_CARD2, border_color=ACCENT_TEAL,
             border_width=Pt(0.75), radius=20000)
    add_text(slide, mval, mx1+0.08, 3.08, mw-0.16, 0.52,
             font_size=18, bold=True, color=ACCENT_TEAL, align=PP_ALIGN.CENTER)
    add_text(slide, mlabel, mx1+0.08, 3.6, mw-0.16, 0.28,
             font_size=8, color=TEXT_SECONDARY, align=PP_ALIGN.CENTER)
    mx1 += mw + 0.12

add_text(slide, "Architecture & Features:",
         0.7, 4.08, 5.6, 0.25, font_size=10, bold=True, color=TEXT_PRIMARY)
add_text(slide,
         "100 Estimators predicting across atomic radius (r), electronegativity (X), "
         "VEC, melting temperature (Tm), and mass standard deviations. Delivers "
         "bulk property predictions with near-perfect accuracy for the theoretical design space.",
         0.7, 4.35, 5.5, 1.4, font_size=10, color=TEXT_SECONDARY)

# Model 2 - Right
add_rect(slide, 6.93, 2.0, 6.0, 5.0,
         fill_color=BG_CARD, border_color=BORDER_COLOR,
         border_width=Pt(0.75), radius=20000)
add_rect(slide, 6.93, 2.0, 0.06, 5.0, fill_color=ACCENT_GOLD, radius=20000)
add_text(slide, "MODEL 2", 7.13, 2.1, 5.6, 0.25, font_size=8, bold=True, color=ACCENT_GOLD)
add_text(slide, "Experimental Yield Strength", 7.13, 2.33, 5.6, 0.32,
         font_size=14, bold=True, color=TEXT_PRIMARY)
add_text(slide, "Gradient Boosting + Transfer Learning", 7.13, 2.63, 5.6, 0.25,
         font_size=10, color=TEXT_SECONDARY)

# Performance metrics for Model 2
m2_metrics = [("Method", "Transfer\nLearning"), ("Target Weight", "10x\nBoost"), ("Temp Knockdown", "45%\nFactor")]
mx2 = 7.13
for mlabel, mval in m2_metrics:
    mw = 1.65
    add_rect(slide, mx2, 3.0, mw, 0.95,
             fill_color=BG_CARD2, border_color=ACCENT_GOLD,
             border_width=Pt(0.75), radius=20000)
    add_text(slide, mval, mx2+0.08, 3.08, mw-0.16, 0.52,
             font_size=14, bold=True, color=ACCENT_GOLD, align=PP_ALIGN.CENTER)
    add_text(slide, mlabel, mx2+0.08, 3.6, mw-0.16, 0.28,
             font_size=8, color=TEXT_SECONDARY, align=PP_ALIGN.CENTER)
    mx2 += mw + 0.12

add_text(slide, "Transfer Learning Logic:", 7.13, 4.08, 5.6, 0.25,
         font_size=10, bold=True, color=TEXT_PRIMARY)
add_text(slide,
         "Trained on an experimental MPEA dataset. We heavily weighted exact 5-element target "
         "alloys (Weight=10) while leveraging broader refractory alloys (Weight=1) to extract "
         "underlying high-temperature physics.\n\n"
         "Thermal Knockdown Penalty: Because forging dies operate near 1200°C, we enforce "
         "a severe homologous temperature knockdown factor (0.45) — assuming the alloy retains "
         "only 45% of its Room Temperature yield strength.",
         7.13, 4.35, 5.5, 1.9, font_size=10, color=TEXT_SECONDARY)

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 6)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 - AI Engine Step 3: Differential Evolution
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "AI ENGINE · STEP 3 OF 3", 0.5, 0.28)
add_heading(slide, "THE CRYSTAL PARADIGM AI ENGINE: STEP 3",
            0.5, 0.55, 10.0, 0.4, size=18)
add_text(slide, "Constrained Differential Evolution (DE) Optimizer",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide,
         "To discover completely novel alloys, our AI sweeps a continuous 9-element space using "
         "a Softmax activation function to generate perfect sum-to-one fractional matrices.",
         0.5, 1.32, 12.3, 0.5, font_size=10.5, color=TEXT_SECONDARY)

# Center result box
add_rect(slide, 4.0, 1.95, 5.33, 1.8,
         fill_color=RGBColor(0x00,0x3D,0x2B), border_color=ACCENT_TEAL,
         border_width=Pt(1.5), radius=20000)
add_text(slide, "CANDIDATE C — OPTIMAL RESULT", 4.15, 2.05, 5.0, 0.28,
         font_size=9, bold=True, color=ACCENT_TEAL, align=PP_ALIGN.CENTER)
add_text(slide, "Fitness Score: 1.5981", 4.15, 2.35, 5.0, 0.45,
         font_size=20, bold=True, color=TEXT_PRIMARY, align=PP_ALIGN.CENTER)
add_text(slide, "Ti = 21.7%  ·  CTE Gap = 2.66 μm/mK  ·  Every Penalty Cleared",
         4.15, 2.82, 5.0, 0.7, font_size=9, color=TEXT_SECONDARY, align=PP_ALIGN.CENTER)

# Four penalty constraint boxes
constraints = [
    ("Sigma Phase Mitigation",
     "Penalty Factor: 5.0",
     "Triggered if Sigma Formers (W + Cr + Mo) exceed 50%. Prevents catastrophic "
     "brittle fracture mode in forging dies."),
    ("Vanadium Volatility",
     "V  ≤ 20%",
     "Hard upper limit on Vanadium to prevent toxic outgassing during high-temperature "
     "manufacturing operations."),
    ("ESG Weight Budget",
     "Density ≤ 11.0 g/cm³",
     "Hard penalty if alloy density exceeds limit, aligning with EV lightweighting goals "
     "and Sona Comstar's ESG mandate."),
    ("Oxidation Barrier",
     "Min 15% Chromium",
     "Demands minimum Chromium content to ensure self-healing Alumina (α-Al₂O₃) "
     "protective scale formation at operating temperatures."),
]
cx_s = 0.5
for i, (title, metric, body) in enumerate(constraints):
    col = (i % 2) * 6.42 + cx_s
    row = (i // 2) * 2.1 + 3.95
    cw, ch = 6.2, 1.92
    add_rect(slide, col, row, cw, ch,
             fill_color=BG_CARD, border_color=BORDER_COLOR,
             border_width=Pt(0.75), radius=20000)
    add_rect(slide, col, row, 0.06, ch, fill_color=ACCENT_GOLD, radius=20000)
    add_text(slide, title, col+0.2, row+0.08, cw-0.3, 0.28,
             font_size=10, bold=True, color=TEXT_PRIMARY)
    add_rect(slide, col+0.2, row+0.4, cw-0.4, 0.4,
             fill_color=BG_CARD2, border_color=ACCENT_GOLD,
             border_width=Pt(0.5), radius=15000)
    add_text(slide, metric, col+0.2, row+0.42, cw-0.4, 0.36,
             font_size=11, bold=True, color=ACCENT_GOLD, align=PP_ALIGN.CENTER)
    add_text(slide, body, col+0.2, row+0.9, cw-0.35, 0.9,
             font_size=9.5, color=TEXT_SECONDARY)

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 7)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 - Verification & TRL Table (the 'by claude' iconic slide)
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "VERIFICATION & TRL STATUS", 0.5, 0.28)
add_heading(slide, "WHAT IS PROVEN TODAY AND WHAT IS NOT",
            0.5, 0.55, 12.0, 0.45, size=20)
add_rect(slide, 0.5, 0.98, 3.0, 0.04, fill_color=ACCENT_TEAL)
add_text(slide, "High-Fidelity Verification Metrics and TRL Maturity Status",
         0.5, 1.07, 12.3, 0.35, font_size=11, color=TEXT_SECONDARY)

# TRL badge
add_rect(slide, 10.8, 0.3, 2.2, 0.6,
         fill_color=RGBColor(0x00,0x3D,0x2B), border_color=ACCENT_TEAL,
         border_width=Pt(1.0), radius=20000)
add_text(slide, "CURRENT TRL: 3+\n→ Target: TRL 4 via SCIDIP",
         10.85, 0.34, 2.1, 0.52, font_size=8, bold=True, color=ACCENT_TEAL)

add_text(slide,
         "All computational physics and validations are fully confirmed in-silico via PyCalphad, "
         "1D/3D FEA, and MACE MD. We are applying to SCIDIP to execute physical TRL 4 lab validation "
         "utilizing IIT Delhi's Central Research Facility (CRF) and NIDHI-CoE.",
         0.5, 1.45, 12.3, 0.55, font_size=10.5, color=TEXT_SECONDARY)

# Table header
headers = ["Evaluation Vector", "Model / In Silico Status", "Lab Validation Target", "SCIDIP Test Equipment", "Status"]
hwidths = [2.8, 2.9, 2.4, 2.55, 0.75]
hx = 0.5
for h, hw in zip(headers, hwidths):
    add_rect(slide, hx, 2.1, hw-0.04, 0.42,
             fill_color=RGBColor(0x0D,0x1A,0x35), border_color=ACCENT_TEAL,
             border_width=Pt(0.75))
    add_text(slide, h, hx+0.1, 2.14, hw-0.18, 0.34,
             font_size=9, bold=True, color=ACCENT_TEAL)
    hx += hw

# Table rows
rows = [
    ("BCC Phase Security",
     "Verified via CALPHAD\n(PyCalphad)",
     "0% Brittle Sigma Phase",
     "High-Temp XRD — IIT Delhi CRF",
     "GREEN"),
    ("Elastic Modulus Surface",
     "Audited — Test R² = 0.977\nMAE = 8.11 GPa",
     "MAE ≤ 8.11 GPa",
     "NIDHI-CoE Tensile Tester",
     "GREEN"),
    ("Oxidation Scale Kinetics",
     "Verified via 2.8% Al Pivot\n(α-Al₂O₃ formation)",
     "Mass Gain < 10 mg/cm²",
     "STA / TGA — IIT Delhi CRF",
     "GREEN"),
    ("Interfacial Bond Safety",
     "Verified — 1D & 3D FEA\n(SF = 1.71 ≥ 1.50 threshold)",
     "Safety Factor ≥ 1.50",
     "Burner Rig Adhesion Test",
     "GREEN"),
    ("Physical Prototyping",
     "Fully Formulated\n(11-layer recipe exported)",
     "TRL 4 Coupon Assembly",
     "DED 3D Printer — SCIDIP Fund",
     "PENDING"),
]

ry = 2.56
for row_data in rows:
    rx = 0.5
    row_bg = BG_CARD if rows.index(row_data) % 2 == 0 else RGBColor(0x1A,0x21,0x3A)
    for cell, cw in zip(row_data[:4], hwidths[:4]):
        add_rect(slide, rx, ry, cw-0.04, 0.82,
                 fill_color=row_bg, border_color=BORDER_COLOR,
                 border_width=Pt(0.5))
        add_text(slide, cell, rx+0.1, ry+0.06, cw-0.2, 0.7,
                 font_size=9, color=TEXT_SECONDARY if rx > 0.6 else TEXT_PRIMARY)
        rx += cw

    # Status indicator
    status = row_data[4]
    dot_col = GREEN_STATUS if status == "GREEN" else YELLOW_STATUS
    status_txt = "● VERIFIED" if status == "GREEN" else "○ PENDING"
    add_rect(slide, rx, ry, hwidths[4]-0.04, 0.82,
             fill_color=row_bg, border_color=BORDER_COLOR, border_width=Pt(0.5))
    add_text(slide, status_txt, rx+0.04, ry+0.22, hwidths[4]-0.1, 0.38,
             font_size=8, bold=True, color=dot_col, align=PP_ALIGN.CENTER)
    ry += 0.86

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 8)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 - The Final Architecture (Candidate C)
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "FROM CHEMISTRY TO MANUFACTURING", 0.5, 0.28)
add_heading(slide, "THE FINAL ARCHITECTURE (CANDIDATE C)",
            0.5, 0.55, 12.0, 0.4, size=18)
add_text(slide, "From In-Silico Chemistry to Print-Ready Manufacturing",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide,
         "Through 11 phases of autonomous generation, our AI produced Candidate C, "
         "a hyper-optimized Refractory High-Entropy Alloy designed specifically for extreme thermal shock.",
         0.5, 1.32, 12.3, 0.5, font_size=10.5, color=TEXT_SECONDARY)

# Three breakthrough boxes
breakthroughs = [
    ("① THE TITANIUM PIVOT", ACCENT_TEAL,
     "CTE Gap Closed to 2.66 μm/mK",
     "The AI intentionally substituted heavy Hafnium for Titanium (21.7%). Because Titanium has the "
     "highest Coefficient of Thermal Expansion (8.6 µm/mK) in the refractory space, it aggressively "
     "closed the CTE mismatch with the ceramic coating."),
    ("② THE ALUMINUM ARMOR", ACCENT_GOLD,
     "Oxidation Mass Gain: 7.5 mg/cm²",
     "The AI identified that standard Chromium oxidizes and sublimates above 1100°C. We executed a "
     "micro-addition of 2.8 at% Aluminum to force the formation of a highly stable α-Al₂O₃ "
     "protective armor scale, capping mass gain at 7.5 mg/cm²."),
    ("③ THE MANUFACTURING RECIPE", RGBColor(0x6E,0x9D,0xFF),
     "11-Layer Print-Ready Matrix",
     "We have directly exported the continuous FGM physics curves into a discrete, print-ready "
     "11-layer manufacturing_recipe.csv (ranging from 0.0mm = 100% alloy to 5.0mm = 100% LZO ceramic). "
     "Ready for immediate Multi-Hopper DED 3D printing."),
]
bx = 0.5
for title, col, metric, body in breakthroughs:
    bw = 4.08
    add_rect(slide, bx, 1.95, bw, 4.55,
             fill_color=BG_CARD, border_color=col,
             border_width=Pt(1.0), radius=20000)
    add_rect(slide, bx, 1.95, bw, 0.05, fill_color=col, radius=20000)
    add_text(slide, title, bx+0.18, 2.05, bw-0.3, 0.28,
             font_size=10, bold=True, color=col)
    add_rect(slide, bx+0.18, 2.4, bw-0.36, 0.52,
             fill_color=BG_CARD2, border_color=col,
             border_width=Pt(0.75), radius=15000)
    add_text(slide, metric, bx+0.18, 2.43, bw-0.36, 0.46,
             font_size=12, bold=True, color=col, align=PP_ALIGN.CENTER)
    add_text(slide, body, bx+0.18, 3.02, bw-0.3, 3.3,
             font_size=10, color=TEXT_SECONDARY)
    bx += bw + 0.14

# Bottom composition hint
add_rect(slide, 0.5, 6.55, 12.33, 0.55,
         fill_color=BG_CARD2, border_color=ACCENT_TEAL,
         border_width=Pt(0.75), radius=15000)
add_text(slide,
         "Alloy Composition: Ta – W – Cr – V – Ti (21.7%) – Zr – Hf + 2.8 at% Al  |  "
         "VEC: 5.02 (BCC stable)  |  3D FEA Safety Factor: 1.71  |  "
         "Cost: ~$170/kg (via Hf→Ti substitution)",
         0.65, 6.62, 12.0, 0.4, font_size=9.5, bold=True, color=ACCENT_TEAL)

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 9)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 - Commercial Impact Table
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "COMMERCIAL IMPACT", 0.5, 0.28)
add_heading(slide, "THE COMMERCIAL IMPACT FOR SONA COMSTAR",
            0.5, 0.55, 12.0, 0.4, size=18)
add_text(slide, "Fleet Scalability and Direct Operating Cost Reductions",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)
add_text(slide,
         "By bridging aerospace materials into Sona Comstar's EPIC mobility framework, "
         "we generate massive downstream financial and strategic returns.",
         0.5, 1.32, 12.3, 0.45, font_size=10.5, color=TEXT_SECONDARY)

# Impact table header
ih = ["Impact Area", "The Physics Trigger", "The Commercial Result"]
iw = [2.8, 4.5, 5.6]
ix = 0.5
for h, w in zip(ih, iw):
    add_rect(slide, ix, 1.88, w-0.04, 0.42,
             fill_color=RGBColor(0x0D,0x1A,0x35), border_color=ACCENT_TEAL,
             border_width=Pt(0.75))
    add_text(slide, h, ix+0.1, 1.91, w-0.2, 0.35,
             font_size=10, bold=True, color=ACCENT_TEAL)
    ix += w

impact_rows = [
    ("Raw Material\nProcurement",
     "75% reduction in Hafnium, substituted with Titanium (21.7% Ti achieved).",
     "15-20% Drop in Alloy Cost — Achieves ~$170/kg, enabling high-volume EV commercialization."),
    ("Tooling & Forging\nUptime",
     "H13 Dies retain 917.7 MPa yield strength at 1200°C, preventing mechanical deformation.",
     "Drastic MRO Reduction — Eliminates thermal fatigue cracking, vastly extending tooling life."),
    ("Next-Gen EV\nMotors (SRM)",
     "Elimination of localized thermal hotspots in Switched Reluctance Motor stator/rotors.",
     "Rare-Earth Independence — Enables high-power magnet-less motors without thermal degradation."),
    ("Supply Chain\nResilience",
     "9-element multi-principal matrix drastically reduces single critical mineral dependency.",
     "True Aatmanirbharta — Indigenous IP generation for Indian mobility sector."),
    ("ESG &\nSustainability",
     "Embodied Energy capped at 1680 MJ/kg with zero toxic heavy elements in composition.",
     "Qualifies for Sona Comstar's 75% Supplier Score — meets 12 of 17 ESG metrics on day one."),
]

ry = 2.34
for i, (area, physics, result) in enumerate(impact_rows):
    bg = BG_CARD if i % 2 == 0 else RGBColor(0x1A,0x21,0x3A)
    rx = 0.5
    rh = 0.86
    for cell, cw in zip([area, physics, result], iw):
        add_rect(slide, rx, ry, cw-0.04, rh,
                 fill_color=bg, border_color=BORDER_COLOR,
                 border_width=Pt(0.5))
        add_text(slide, cell, rx+0.12, ry+0.08, cw-0.24, rh-0.16,
                 font_size=9.5,
                 color=TEXT_PRIMARY if rx < 1.0 else TEXT_SECONDARY,
                 bold=(rx < 1.0))
        rx += cw
    ry += rh

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 10)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 - SCIDIP Deployment 1: Forging Dies
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "SCIDIP DEPLOYMENT 1", 0.5, 0.28)
add_heading(slide, "SCIDIP DEPLOYMENT 1: NEXT-GEN FORGING DIES",
            0.5, 0.55, 12.0, 0.4, size=18)
add_text(slide, "Solving Sona Comstar's Differential Gear Bottleneck",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_GOLD)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_GOLD)

# Left: Problem
add_rect(slide, 0.5, 1.45, 5.9, 5.2,
         fill_color=BG_CARD, border_color=RGBColor(0xFF,0x4D,0x6D),
         border_width=Pt(1.0), radius=20000)
add_rect(slide, 0.5, 1.45, 0.06, 5.2, fill_color=RGBColor(0xFF,0x4D,0x6D), radius=20000)
add_text(slide, "THE CURRENT PROBLEM", 0.7, 1.55, 5.5, 0.28,
         font_size=10, bold=True, color=RGBColor(0xFF,0x4D,0x6D))
add_text(slide,
         "Sona Comstar's core competitive advantage lies in precision forging of differential "
         "bevel gears. However, legacy H13 tool steel dies suffer:\n\n"
         "  ·  Massive yield strength collapse at operating temperatures\n"
         "  ·  Rapid thermal fatigue cracking under thermal cycling\n"
         "  ·  Costly manufacturing downtime and replacement cycles\n"
         "  ·  H13 Yield Strength: < 500 MPa at 1200°C (insufficient)\n\n"
         "This directly limits Sona Comstar's throughput for differential gear production "
         "supplied to global EV OEMs.",
         0.7, 1.9, 5.5, 4.5, font_size=10.5, color=TEXT_SECONDARY)

# Right: Solution
add_rect(slide, 6.93, 1.45, 5.9, 5.2,
         fill_color=BG_CARD, border_color=ACCENT_GOLD,
         border_width=Pt(1.0), radius=20000)
add_rect(slide, 6.93, 1.45, 0.06, 5.2, fill_color=ACCENT_GOLD, radius=20000)
add_text(slide, "THE CRYSTAL PARADIGM UPGRADE", 7.13, 1.55, 5.5, 0.28,
         font_size=10, bold=True, color=ACCENT_GOLD)

upgrade_items = [
    ("The Core",
     "The Ta-W-Cr-V-Ti-Zr-Hf alloy retains >917.7 MPa yield strength at 1200°C, "
     "preventing mechanical deformation under massive forging pressures."),
    ("The Surface",
     "The LZO (Lanthanum Zirconate) ceramic outer layer acts as a supreme thermal "
     "barrier, preventing heat transfer from the hot-forged blank into the die."),
    ("The Result",
     "Elimination of rapid thermal fatigue cracking, vastly extending tooling life "
     "and accelerating manufacturing throughput for EV gearbox components."),
]
sy = 1.95
for title, body in upgrade_items:
    add_rect(slide, 7.13, sy, 5.5, 1.45,
             fill_color=BG_CARD2, border_color=BORDER_COLOR,
             border_width=Pt(0.5), radius=15000)
    add_text(slide, f"▸  {title}", 7.28, sy+0.1, 5.1, 0.25,
             font_size=10, bold=True, color=ACCENT_GOLD)
    add_text(slide, body, 7.28, sy+0.38, 5.1, 0.95,
             font_size=9.5, color=TEXT_SECONDARY)
    sy += 1.55

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 11)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 - SCIDIP Deployment 2: EV Traction Motors
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "SCIDIP DEPLOYMENT 2", 0.5, 0.28)
add_heading(slide, "SCIDIP DEPLOYMENT 2: MAGNET-LESS EV MOTORS",
            0.5, 0.55, 12.0, 0.4, size=18)
add_text(slide, "Enabling Rare-Earth Independence in Traction Motors",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide,
         "As part of the 'EPIC' roadmap, Sona Comstar is heavily investing in Switched Reluctance Motors "
         "(SRMs) to eliminate reliance on imported Neodymium magnets.",
         0.5, 1.32, 12.3, 0.5, font_size=10.5, color=TEXT_SECONDARY)

# Left: Problem context
add_rect(slide, 0.5, 1.95, 5.9, 4.7,
         fill_color=BG_CARD, border_color=RGBColor(0xFF,0x4D,0x6D),
         border_width=Pt(1.0), radius=20000)
add_rect(slide, 0.5, 1.95, 0.06, 4.7, fill_color=RGBColor(0xFF,0x4D,0x6D), radius=20000)
add_text(slide, "THE ENGINEERING BOTTLENECK", 0.7, 2.05, 5.5, 0.28,
         font_size=10, bold=True, color=RGBColor(0xFF,0x4D,0x6D))
add_text(slide,
         "SRMs generate extreme, localized thermal hotspots that degrade traditional stator/rotor metals.\n\n"
         "The Two Core Problems:\n\n"
         "① Supply Chain Risk: 80%+ of global Neodymium controlled by China — creates "
         "severe geopolitical supply vulnerability for Indian EV manufacturing.\n\n"
         "② Thermal Degradation: At extreme torque densities, traditional metals rapidly "
         "lose mechanical integrity, limiting SRM power density and lifespan.",
         0.7, 2.42, 5.5, 4.0, font_size=10.5, color=TEXT_SECONDARY)

# Right: Solution
add_rect(slide, 6.93, 1.95, 5.9, 4.7,
         fill_color=BG_CARD, border_color=ACCENT_TEAL,
         border_width=Pt(1.0), radius=20000)
add_rect(slide, 6.93, 1.95, 0.06, 4.7, fill_color=ACCENT_TEAL, radius=20000)
add_text(slide, "THE CRYSTAL PARADIGM UPGRADE", 7.13, 2.05, 5.5, 0.28,
         font_size=10, bold=True, color=ACCENT_TEAL)
add_text(slide,
         "By deploying our aerospace-derived Candidate C, we provide Sona Comstar with a "
         "structural material capable of surviving localized high-temperature spikes without "
         "compromising mechanical integrity.",
         7.13, 2.42, 5.5, 0.85, font_size=10, color=TEXT_SECONDARY)

upgrade2 = [
    ("Thermal Shielding",
     "The FGM gradient handles rapid thermal cycling without delamination "
     "(15.95 MPa interface shear stress), acting as a physical shield for sensitive copper windings."),
    ("Make-In-India Supply Chain",
     "By substituting Hafnium for Titanium, we drop the alloy cost to ~$170/kg, "
     "making aerospace-grade thermal protection viable for high-volume Indian EV manufacturing."),
]
sy2 = 3.4
for title, body in upgrade2:
    add_rect(slide, 7.13, sy2, 5.5, 1.5,
             fill_color=BG_CARD2, border_color=BORDER_COLOR,
             border_width=Pt(0.5), radius=15000)
    add_text(slide, f"▸  {title}", 7.28, sy2+0.1, 5.1, 0.25,
             font_size=10, bold=True, color=ACCENT_TEAL)
    add_text(slide, body, 7.28, sy2+0.38, 5.1, 1.0,
             font_size=9.5, color=TEXT_SECONDARY)
    sy2 += 1.6

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 12)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 - IP Strategy & Aatmanirbharta
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "DE-RISKING THE SUPPLY CHAIN", 0.5, 0.28)
add_heading(slide, "INTELLECTUAL PROPERTY & DE-RISKING THE SUPPLY CHAIN",
            0.5, 0.55, 12.0, 0.4, size=18)
add_text(slide, "True Aatmanirbharta for the Indian Mobility Sector",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide,
         "Sona Comstar's strategic reliance on rare-earth elements for EV motors is a massive "
         "supply chain vulnerability. Crystal Paradigm offers a computational pathway to complete import substitution.",
         0.5, 1.32, 12.3, 0.5, font_size=10.5, color=TEXT_SECONDARY)

ip_cards = [
    ("THE IP MOAT", ACCENT_TEAL,
     "Our proprietary 11-phase AI architecture is a continuous IP generation engine. "
     "Candidate C is merely our first output; we can computationally generate bespoke materials "
     "for any thermal bottleneck Sona Comstar faces across all four EPIC verticals."),
    ("MAKE-IN-INDIA REALITY", ACCENT_GOLD,
     "By engineering out exotic, foreign-controlled minerals and optimizing around globally "
     "abundant Titanium and Chromium, we guarantee a secure, indigenous supply chain for "
     "Sona Comstar's next-gen components — critical for true Aatmanirbharta."),
    ("IIT DELHI IP FRAMEWORK", RGBColor(0x6E,0x9D,0xFF),
     "We are prepared to navigate the FITT incubation framework to jointly patent physical "
     "material formulations developed within the Central Research Facility (CRF), ensuring "
     "robust legal IP protection for all innovations generated during incubation."),
]
cx = 0.5
for title, col, body in ip_cards:
    cw = 4.08
    add_rect(slide, cx, 1.95, cw, 4.65,
             fill_color=BG_CARD, border_color=col,
             border_width=Pt(1.0), radius=20000)
    add_rect(slide, cx, 1.95, cw, 0.05, fill_color=col, radius=20000)
    add_text(slide, title, cx+0.18, 2.08, cw-0.3, 0.3,
             font_size=10, bold=True, color=col)
    add_rect(slide, cx+0.18, 2.45, cw-0.36, 0.04, fill_color=BORDER_COLOR)
    add_text(slide, body, cx+0.18, 2.58, cw-0.3, 3.8,
             font_size=10.5, color=TEXT_SECONDARY)
    cx += cw + 0.14

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 13)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 - The Corporate Ask (4 Pillars)
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "THE CORPORATE ASK", 0.5, 0.28)
add_heading(slide, "THE CRYSTAL PARADIGM CORPORATE ASK",
            0.5, 0.55, 12.0, 0.4, size=18)
add_text(slide, "Bridging the Gap Between Informatics and the Factory Floor",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide,
         "Crystal Paradigm is completely computationally validated (TRL 3+). We are applying to the "
         "Advanced Materials track of the SCIDIP program to access the precise ecosystem required to "
         "cross the 'valley of death'.",
         0.5, 1.32, 12.3, 0.5, font_size=10.5, color=TEXT_SECONDARY)

# Four SCIDIP pillars
pillars = [
    ("1", "TECHNOLOGY & LAB SUPPORT",
     "IIT Delhi CRF",
     ACCENT_TEAL,
     "Immediate access to the NIDHI-CoE and CRF to execute High-Temperature XRD, SEM, and "
     "Simultaneous Thermal Analysis (STA) on physical witness coupons to validate Candidate C."),
    ("2", "SONA COMSTAR MENTORSHIP",
     "Engineering Alignment",
     ACCENT_GOLD,
     "Direct engineering alignment with Sona Comstar's precision forging division to ensure our "
     "11-layer print matrices match factory-floor DED manufacturing tolerances and specifications."),
    ("3", "SCIDIP SEED ECOSYSTEM",
     "₹80 Lakh Grant",
     RGBColor(0x6E,0x9D,0xFF),
     "Integration into the SCIDIP funding and incubation framework to finance raw material "
     "atomization and multi-hopper 3D printing of the physical witness coupon prototypes."),
    ("4", "CORPORATE MARKET CONNECT",
     "Supply Chain Integration",
     RGBColor(0xFF,0x8C,0x5A),
     "Joint integration of the physical prototypes into Sona Comstar's downstream EV supply chain, "
     "including precision forging dies and SRM stator components."),
]
px = 0.5
for num, title, subtitle, col, body in pillars:
    pw = 2.98
    # Pillar card
    add_rect(slide, px, 1.95, pw, 5.05,
             fill_color=BG_CARD, border_color=col,
             border_width=Pt(1.0), radius=20000)
    # Number circle
    add_rect(slide, px+pw/2-0.3, 2.05, 0.6, 0.6,
             fill_color=col, radius=50000)
    add_text(slide, num, px+pw/2-0.3, 2.08, 0.6, 0.52,
             font_size=16, bold=True,
             color=RGBColor(0x14,0x1A,0x2E), align=PP_ALIGN.CENTER)
    add_text(slide, title, px+0.15, 2.78, pw-0.3, 0.5,
             font_size=10, bold=True, color=col, align=PP_ALIGN.CENTER)
    add_text(slide, subtitle, px+0.15, 3.28, pw-0.3, 0.28,
             font_size=9, color=TEXT_SECONDARY, align=PP_ALIGN.CENTER)
    add_rect(slide, px+0.3, 3.62, pw-0.6, 0.03, fill_color=BORDER_COLOR)
    add_text(slide, body, px+0.15, 3.72, pw-0.3, 2.95,
             font_size=9.5, color=TEXT_SECONDARY, align=PP_ALIGN.CENTER)
    px += pw + 0.13

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 14)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 - 24-Month Roadmap
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "EXECUTION ROADMAP", 0.5, 0.28)
add_heading(slide, "THE 24-MONTH INCUBATION ROADMAP",
            0.5, 0.55, 12.0, 0.4, size=18)
add_text(slide, "From Computational Validation to Sona Comstar Integration",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)
add_text(slide,
         "Our execution strategy is strictly mapped to the 24-month SCIDIP incubation cycle at "
         "Atal Incubation Centre (AIC), IIT Delhi.",
         0.5, 1.32, 12.3, 0.4, font_size=10.5, color=TEXT_SECONDARY)

# Milestones
milestones = [
    ("M1", "Months 1-6", "POWDER SYNTHESIS", ACCENT_TEAL,
     "Procure raw metal powders (Ta, W, Cr, V, Ti, Zr, Hf, Al). Utilize IIT Delhi labs "
     "to verify composition purity and atomization quality."),
    ("M2", "Months 6-12", "ADDITIVE MANUFACTURING", ACCENT_GOLD,
     "Execute the 11-layer manufacturing_recipe.csv via DED (Directed Energy Deposition) "
     "to print physical witness coupons."),
    ("M3", "Months 12-18", "NIDHI-CoE & CRF TESTING", RGBColor(0x6E,0x9D,0xFF),
     "Conduct physical yield strength testing and execute High-Temp XRD / STA thermal shock "
     "validation at IIT Delhi to physically validate the 1.50 Safety Factor."),
    ("M4", "Months 18-24", "CORPORATE HANDOVER", RGBColor(0xFF,0x8C,0x5A),
     "Present fully validated TRL 5/6 hardware to Sona Comstar for direct integration "
     "into H13 forging dies and SRM stator prototypes."),
]
# Timeline bar
add_rect(slide, 0.5, 2.05, 12.33, 0.08, fill_color=BORDER_COLOR, radius=10000)

mx = 0.5
for i, (tag, period, title, col, body) in enumerate(milestones):
    mw = 3.0
    # Node on timeline
    node_x = mx + mw/2 - 0.18
    add_rect(slide, node_x, 1.9, 0.36, 0.36,
             fill_color=col, radius=50000)
    add_text(slide, tag, node_x, 1.93, 0.36, 0.3,
             font_size=10, bold=True,
             color=RGBColor(0x14,0x1A,0x2E), align=PP_ALIGN.CENTER)

    # Card below
    add_rect(slide, mx+0.06, 2.35, mw-0.12, 4.65,
             fill_color=BG_CARD, border_color=col,
             border_width=Pt(1.0), radius=20000)
    add_rect(slide, mx+0.06, 2.35, mw-0.12, 0.05, fill_color=col, radius=20000)
    add_text(slide, period, mx+0.2, 2.45, mw-0.35, 0.25,
             font_size=8, bold=True, color=col)
    add_text(slide, title, mx+0.2, 2.73, mw-0.35, 0.45,
             font_size=12, bold=True, color=TEXT_PRIMARY)
    add_rect(slide, mx+0.2, 3.22, mw-0.45, 0.03, fill_color=BORDER_COLOR)
    add_text(slide, body, mx+0.2, 3.32, mw-0.35, 3.5,
             font_size=10, color=TEXT_SECONDARY)
    mx += mw + 0.1

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 15)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 - Research Leads
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "THE RESEARCH LEADS", 0.5, 0.28)
add_heading(slide, "THE RESEARCH LEADS",
            0.5, 0.55, 12.0, 0.4, size=18)
add_text(slide, "Guided by Elite Academic and Scientific Expertise",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)

leads = [
    ("DR. SHILPA CHOUDHARY", "AI / ML Lead", ACCENT_TEAL,
     [("Recognition", "Top 2% Scientists Worldwide — Stanford University (2024)"),
      ("Experience", "16+ years in AI, Deep Learning & AI-driven scientific applications"),
      ("Postdoctoral", "Singapore Institute of Technology & National Kaohsiung University of Science and Technology (Taiwan)"),
      ("Output", "100+ research papers | 1763 citations | H-index 22 | 12 academic books | Multiple patents"),
      ("At Crystal Paradigm", "Leads AI innovation, ML Architecture, Constrained Optimization & Surrogate Model Design")]),
    ("DR. KASARAPU VENKATARAMANA", "Materials Science & Experimental Validation Lead", ACCENT_GOLD,
     [("Position", "Research Associate at CSIR-IICT — DRDO sponsored project"),
      ("Recognition", "Associate Fellow, Telangana Academy of Sciences (2024)"),
      ("Experience", "12 years research + 5 years academic teaching"),
      ("Output", "38 publications | 610+ citations | H-index 14 | 2 book chapters | Reviewer: Elsevier, Springer, Taylor & Francis"),
      ("Specialization", "High Entropy Oxides, XRD, SEM/EDS, advanced materials characterization")]),
]

lx = 0.5
for name, role, col, items in leads:
    lw = 6.1
    add_rect(slide, lx, 1.55, lw, 5.85,
             fill_color=BG_CARD, border_color=col,
             border_width=Pt(1.0), radius=20000)
    add_rect(slide, lx, 1.55, lw, 0.05, fill_color=col, radius=20000)
    # Avatar placeholder
    add_rect(slide, lx+0.2, 1.68, 1.0, 1.0,
             fill_color=BG_CARD2, border_color=col,
             border_width=Pt(0.75), radius=50000)
    add_text(slide, "👤", lx+0.22, 1.73, 0.96, 0.85,
             font_size=28, color=col, align=PP_ALIGN.CENTER)
    add_text(slide, name, lx+1.32, 1.72, lw-1.5, 0.45,
             font_size=11, bold=True, color=TEXT_PRIMARY)
    add_text(slide, role, lx+1.32, 2.17, lw-1.5, 0.28,
             font_size=9, color=col)
    add_rect(slide, lx+0.2, 2.78, lw-0.4, 0.03, fill_color=BORDER_COLOR)
    iy = 2.88
    for key, val in items:
        add_text(slide, f"• {key}:", lx+0.2, iy, 1.5, 0.25,
                 font_size=9, bold=True, color=col)
        add_text(slide, val, lx+1.7, iy, lw-1.9, 0.25,
                 font_size=9, color=TEXT_SECONDARY)
        iy += 0.55
    lx += lw + 0.13

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 16)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 - Core AI Architects
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

add_label(slide, "THE AI ENGINEERING ENGINE", 0.5, 0.28)
add_heading(slide, "THE CORE AI ARCHITECTS",
            0.5, 0.55, 12.0, 0.4, size=18)
add_text(slide, "The Prodigious Engine Driving the Day-to-Day AI Innovation",
         0.5, 0.93, 10.0, 0.32, font_size=13, bold=True, color=ACCENT_TEAL)
add_rect(slide, 0.5, 1.23, 2.5, 0.04, fill_color=ACCENT_TEAL)

engineers = [
    ("MOHAMMED AHMED RAZA", "AI Research Intern", ACCENT_TEAL,
     [("Education", "CSE — Neil Gogte Institute of Technology (NGIT)"),
      ("Certification", "Certified AI/ML Professional — iHub-Data, IIIT Hyderabad"),
      ("Research Internship", "Winter Intern at IIIT Hyderabad — UAV spatial awareness & obstacle detection"),
      ("Current Role", "AI Research Intern at Crystal Paradigm — inverse design frameworks for HE-MCGA"),
      ("Recent Work", "Co-authored breakthrough Attention Graph Siamese Transformer (DPT-GNN) for Li-ion battery prediction")]),
    ("K. INDRASENA REDDY [INDRA]", "AI Research Intern", ACCENT_GOLD,
     [("Education", "CSE — Neil Gogte Institute of Technology (NGIT)"),
      ("Previous", "AI Developer Intern at Viswam.AI — NLP applications & LLM research"),
      ("Current Role", "Materials informatics & graph neural network modeling at Crystal Paradigm"),
      ("Specialization", "Large-scale property prediction & advanced GNN architectures"),
      ("Focus", "AI-driven materials discovery & multi-physics simulation pipelines")]),
]

lx = 0.5
for name, role, col, items in engineers:
    lw = 6.1
    add_rect(slide, lx, 1.55, lw, 4.6,
             fill_color=BG_CARD, border_color=col,
             border_width=Pt(1.0), radius=20000)
    add_rect(slide, lx, 1.55, lw, 0.05, fill_color=col, radius=20000)
    add_rect(slide, lx+0.2, 1.68, 1.0, 1.0,
             fill_color=BG_CARD2, border_color=col,
             border_width=Pt(0.75), radius=50000)
    add_text(slide, "👤", lx+0.22, 1.73, 0.96, 0.85,
             font_size=28, color=col, align=PP_ALIGN.CENTER)
    add_text(slide, name, lx+1.32, 1.72, lw-1.5, 0.45,
             font_size=11, bold=True, color=TEXT_PRIMARY)
    add_text(slide, role, lx+1.32, 2.17, lw-1.5, 0.28,
             font_size=9, color=col)
    add_rect(slide, lx+0.2, 2.72, lw-0.4, 0.03, fill_color=BORDER_COLOR)
    iy = 2.82
    for key, val in items:
        add_text(slide, f"• {key}:", lx+0.2, iy, 1.55, 0.25,
                 font_size=9, bold=True, color=col)
        add_text(slide, val, lx+1.75, iy, lw-1.95, 0.25,
                 font_size=9, color=TEXT_SECONDARY)
        iy += 0.5
    lx += lw + 0.13

# Extended team banner
add_rect(slide, 0.5, 6.22, 12.33, 0.6,
         fill_color=RGBColor(0x00,0x3D,0x2B), border_color=ACCENT_TEAL,
         border_width=Pt(1.0), radius=15000)
add_text(slide,
         "EXTENDED CRYSTAL PARADIGM ENGINEERING TEAM: The core architecture is supported by "
         "18 specialized AI Research Interns providing massive parallel execution bandwidth "
         "for complex multi-physics simulations and AI training pipelines.",
         0.7, 6.28, 11.9, 0.48, font_size=9.5, bold=True, color=ACCENT_TEAL)

add_footer_line(slide)
add_logo_text(slide)
add_slide_number(slide, 17)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 - Closing
# ══════════════════════════════════════════════════════════════════════════════
slide = blank_slide(prs)
set_bg(slide, BG_DARK)

# Large background geometric element
add_rect(slide, 0.0, 0.0, 13.33, 7.5,
         fill_color=BG_DARK)
# Decorative circles
add_rect(slide, 8.0, 1.5, 4.5, 4.5,
         fill_color=RGBColor(0x1E,0x27,0x45), border_color=ACCENT_TEAL,
         border_width=Pt(0.5), radius=50000)
add_rect(slide, 8.8, 2.2, 3.0, 3.0,
         fill_color=RGBColor(0x0D,0x13,0x28), border_color=ACCENT_TEAL,
         border_width=Pt(0.5), radius=50000)

# Teal accent bar
add_rect(slide, 0.5, 2.0, 0.08, 3.5, fill_color=ACCENT_TEAL)

add_text(slide, "CRYSTAL PARADIGM",
         0.75, 2.0, 7.0, 0.6,
         font_size=14, bold=True, color=ACCENT_TEAL)

add_text(slide, "Accelerating Deep-Tech\nMaterials from 5 Years\nto 4 Weeks.",
         0.75, 2.62, 7.5, 2.4,
         font_size=34, bold=True, color=TEXT_PRIMARY)

add_text(slide,
         "We have completely solved the computational bottleneck.",
         0.75, 5.15, 7.5, 0.38,
         font_size=13, color=TEXT_SECONDARY)
add_text(slide,
         "We are ready to build the physical reality.",
         0.75, 5.52, 7.5, 0.38,
         font_size=13, bold=True, color=TEXT_PRIMARY)

add_rect(slide, 0.75, 5.95, 3.5, 0.04, fill_color=ACCENT_TEAL)

add_text(slide, "Join us at the SCIDIP Advanced Materials Track.",
         0.75, 6.08, 7.5, 0.35,
         font_size=12, bold=True, color=ACCENT_TEAL)
add_text(slide, "crystalparadigm.in  |  khub.crystalparadigm@gmail.com",
         0.75, 6.48, 7.5, 0.28,
         font_size=10, color=TEXT_SECONDARY)

add_logo_text(slide)
add_slide_number(slide, 18)

# ─── SAVE ─────────────────────────────────────────────────────────────────────
out_path = "CrystalParadigm_SCIDIP_HYBRID_ELITE.pptx"
prs.save(out_path)
print(f"\nSUCCESS: Elite Hybrid Deck saved as '{out_path}'")
print(f"Total Slides: {len(prs.slides)}")
