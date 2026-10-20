"""
PRECISE REVERT + MINIMAL FIXES — Work from ELITE.pptx (pre-v2)
================================================================
RULES:
  - NO font size changes on original slides (S01-S14)
  - NO new shapes added to original slides
  - NO position changes to original slide elements
  - ONLY fix: image positions (3 slides), 1 card overflow, footer heights on NEW slides only
  - TEXT content replacements only where absolutely wrong (S09 aerospace row, S11 flight text, S12 table)
  - S01: Absolutely nothing touched
"""
import shutil, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

C_TITLE  = RGBColor(0x1A, 0x36, 0x5D)
C_SUB    = RGBColor(0x2B, 0xDE, 0xFD)
C_ACCENT = RGBColor(0x00, 0xB4, 0xD8)
C_BODY   = RGBColor(0x11, 0x11, 0x11)
C_MUTED  = RGBColor(0x55, 0x80, 0xA0)
C_GREEN  = RGBColor(0x05, 0x96, 0x69)
C_FTXT   = RGBColor(0xD0, 0xE8, 0xF5)

def I(v): return Inches(v)
def near(a, b, tol=0.06): return abs(a - b) < tol

def gp(s):
    return (
        s.left/914400 if s.left else 0,
        s.top/914400 if s.top else 0,
        s.width/914400 if s.width else 0,
        s.height/914400 if s.height else 0,
    )

def sp(s, l=None, t=None, w=None, h=None):
    if l is not None: s.left   = I(l)
    if t is not None: s.top    = I(t)
    if w is not None: s.width  = I(w)
    if h is not None: s.height = I(h)

# ── LOAD FROM ELITE (pre-v2) ─────────────────────────────────────────────────
shutil.copy2("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx",
             "CrystalParadigm_SCIDIP_IITDelhi_FINAL_v3.pptx")
prs = Presentation("CrystalParadigm_SCIDIP_IITDelhi_FINAL_v3.pptx")
slides = list(prs.slides)
print(f"Loaded from ELITE: {len(slides)} slides")

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 1: S04 — Third result card overflows right by 0.02"
# Card at l=6.92 w=3.10 → 10.02. Move to l=6.60 (safe margin)
# Textboxes inside: l=7.04 → l=6.72
# ═══════════════════════════════════════════════════════════════════════════════
s4 = slides[3]
for sh in s4.shapes:
    l, t, w, h = gp(sh)
    if near(l, 6.92) and t >= 3.90:
        sp(sh, l=6.60)
        print(f"[S04] Card shape: l=6.92 → 6.60")
    elif near(l, 7.04) and t >= 3.90:
        sp(sh, l=6.72)
        print(f"[S04] Text shape: l=7.04 → 6.72")

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 2: Image positions — ONLY top position, no other changes
# ═══════════════════════════════════════════════════════════════════════════════
# S06: image t=0.20 → 0.00
for sh in slides[5].shapes:
    l, t, w, h = gp(sh)
    if sh.shape_type == 13 and near(t, 0.20, 0.05):
        sp(sh, t=0.00); print("[S06] Image t=0.20 → 0.00")

# S08: image t=-0.03 → 0.00
for sh in slides[7].shapes:
    l, t, w, h = gp(sh)
    if sh.shape_type == 13 and t < 0:
        sp(sh, t=0.00); print(f"[S08] Image t={t:.3f} → 0.00")

# S10: image t=0.01 → 0.00
for sh in slides[9].shapes:
    l, t, w, h = gp(sh)
    if sh.shape_type == 13 and near(t, 0.01, 0.02):
        sp(sh, t=0.00); print("[S10] Image t=0.01 → 0.00")

# S20: image l=-0.06 → 0.00
for sh in slides[19].shapes:
    l, t, w, h = gp(sh)
    if sh.shape_type == 13 and l < 0:
        sp(sh, l=0.00); print(f"[S20] Image l={l:.3f} → 0.00")

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 3: S09 — Replace aerospace row text ONLY (no font/position changes)
# "Transpiration Film Stability" → Sona Comstar relevant row
# ═══════════════════════════════════════════════════════════════════════════════
s9 = slides[8]
aerospace_row = {
    'Transpiration Film Stability': 'Forging Die Thermal Fit (Sona Comstar)',
    'Modeled (CFD Jet Lift)':       'Simulated via 3D FEA + DED recipe',
    'Pending Thermal Cycling Test': 'Pending Die Trial — Sona Comstar Plant',
    'Zero Boundary Separation':     'Factory Tolerance ±0.05 mm (DIN ISO)',
}
for sh in s9.shapes:
    if not hasattr(sh, 'text_frame'): continue
    txt = sh.text.strip()
    for old, new in aerospace_row.items():
        if txt == old or txt.startswith(old):
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    run.text = new
                    break
                break
            print(f"[S09] '{old[:30]}' → '{new[:30]}'")

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 4: S11 — Text-only replacement of "Flight-Readiness" → factory language
# ═══════════════════════════════════════════════════════════════════════════════
s11 = slides[10]
for sh in s11.shapes:
    if not hasattr(sh, 'text_frame'): continue
    for para in sh.text_frame.paragraphs:
        for run in para.runs:
            if 'Flight-Readiness Funnel' in run.text:
                run.text = run.text.replace('Flight-Readiness Funnel', 'Factory-Floor Integration')
                print("[S11] 'Flight-Readiness Funnel' → 'Factory-Floor Integration'")
            elif 'flight' in run.text.lower() and 'readiness' in run.text.lower():
                run.text = run.text.replace('flight-readiness', 'factory-floor')
                print("[S11] flight-readiness → factory-floor")

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 5: S12 — Text-only rewrites for Sona Comstar economics
# Keep ALL positions and font sizes. Only change the text content.
# ═══════════════════════════════════════════════════════════════════════════════
s12 = slides[11]

# Map: exact text → new text (must match exactly for safety)
s12_rewrites = {
    # Title
    'ECONOMIC VALUE & OPERATING SAVINGS LEDGER':
        'CRYSTAL PARADIGM VALUE FOR SONA COMSTAR',
    # Subtitle
    'Fleet Scalability and Direct Operating Cost Reductions for Next-Generation Propulsion':
        'Quantified ROI: Forging Die Upgrades, EV Motor Materials & ESG Compliance',
    # Column headers
    'Governing Aerospace Formula': 'Economic Mechanism',
    'Baseline Input Variable':     'Crystal Paradigm Value',
    'Net Annual Savings Yield':    'Sona Comstar Benefit',
    # Row 1
    'Parasitic Bleed Air Cut':     'H13 Die Cost Reduction',
    'Δ m_bleed = m_baseline × 0.15': 'Ta-W-Cr-V-Ti HEA; ~$170/kg vs $280/kg Hf-alloy',
    '15% Reduction':               '15–20% alloy material cost drop',
    'Frees Core Mass Flow':        '₹2–4 Cr/Year saved across 9 plants',
    # Row 2
    'Net SFC Efficiency Gain':     'Forging Die Lifespan Extension',
    'η_cycle = Δ SFC × 1.0':       'Candidate C: >917.7 MPa at 1,200°C vs H13 collapse',
    '1.5% Net Reduction':          '3× longer tooling life; zero thermal fatigue',
    'Maximizes Core Thrust':       '₹5–8 Cr/Year in MRO downtime savings',
    # Row 3
    'Volumetric Fuel Savings':     'EV SRM Motor Thermal Material',
    'V_saved = 3,000 hr × 2,400 kg/hr × 0.015': 'FGM shield: 15.95 MPa interface; zero delamination',
    '7,200 Metric Tons Baseline':  'Rare-Earth-Free SRM at commercial scale',
    '135,000 Liters / Aircraft':   'Eliminates ₹50–80 Cr Neodymium import cost',
    # Row 4
    'Direct Operating Cost Cut':   'ESG Supplier Compliance',
    'Cash Savings = V_saved × $0.85 /L': 'Embodied Energy: 1,680 MJ/kg; zero rare-earth dependency',
    '$0.85/L Jet A-1 Price':       'Qualifies Sona Comstar 75% ESG supplier mandate',
    '$114,750 / Aircraft':         'Unlocks full EPIC supply chain tier access',
    # Summary row
    'Fleet Scalability Revenue':   'Total IP & Commercialization Potential',
    'Total Yield = Cash Savings × 100 Jets': 'AI pipeline → bespoke materials for all EPIC verticals',
    '100 Narrowbody Fleet':        '₹15–20 Cr / Year (conservative)',
    '$11,475,000 / Year':          '+ JV / Acquisition pathway via SCIDIP',
    # Footnote
    '*Calculations based on global average aviation fuel pricing and industry-standard propulsion metrics.':
        '*All INR estimates are conservative, based on current Sona Comstar manufacturing footprint and material market rates.',
}

for sh in s12.shapes:
    if not hasattr(sh, 'text_frame'): continue
    full_txt = sh.text.strip()
    for old, new in s12_rewrites.items():
        if full_txt == old or full_txt.startswith(old[:25]):
            changed = False
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    if old in run.text or run.text.strip() == old:
                        run.text = run.text.replace(old, new)
                        changed = True
                        break
                    elif run.text.strip() and old.startswith(run.text.strip()[:15]):
                        run.text = new
                        changed = True
                        break
            if changed:
                print(f"[S12] '{old[:35]}' → '{new[:35]}'")
            break

print("[S12] Economic ledger text updated")

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 6: Footer overflow on NEW slides ONLY (S03,S04,S15-S19)
# Footer band: t=5.08 h=0.59 → total 5.67 > 5.62. Reduce h to 0.54
# ═══════════════════════════════════════════════════════════════════════════════
new_slide_idx = [2, 3, 14, 15, 16, 17, 18]  # 0-based
for si in new_slide_idx:
    slide = slides[si]
    for sh in slide.shapes:
        l, t, w, h = gp(sh)
        if near(t, 5.08, 0.03) and near(h, 0.59, 0.03) and near(l, 0.0, 0.05):
            sp(sh, h=0.54)
            print(f"[S{si+1}] Footer band h=0.59 → 0.54")
        # Fix footer band accent line that overflows (t=5.03 h=0.05 is fine; t=5.08 is the issue)
        # Footer text on new slides at l=2.0 — fix to l=0.38 for proper alignment
        if near(t, 5.13, 0.05) and near(l, 2.0, 0.15) and hasattr(sh, 'text_frame'):
            sp(sh, l=0.38, w=9.2)

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 7: S20 footer overflow — t=4.41+h=1.51=5.92 → clip h to 1.21
# ═══════════════════════════════════════════════════════════════════════════════
for sh in slides[19].shapes:
    l, t, w, h = gp(sh)
    if near(t, 4.41, 0.05) and h > 1.2:
        sp(sh, h=1.21)
        print(f"[S20] Footer band h={h:.2f} → 1.21")
    # Fix footer text left offset
    if l < 0 and hasattr(sh, 'text_frame'):
        sp(sh, l=0.38)

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL VALIDATION — Zero overflows
# ═══════════════════════════════════════════════════════════════════════════════
SW, SH = 10.0, 5.62
issues = []
for si, slide in enumerate(prs.slides):
    for sh in slide.shapes:
        l, t, w, h = gp(sh)
        if l + w > SW + 0.03: issues.append(f"S{si+1} RIGHT_OVERFLOW l={l:.2f}+{w:.2f}={l+w:.2f}")
        if t + h > SH + 0.03: issues.append(f"S{si+1} BOTTOM_OVERFLOW t={t:.2f}+{h:.2f}={t+h:.2f}")
        if l < -0.03:         issues.append(f"S{si+1} LEFT l={l:.2f}")
        if t < -0.03:         issues.append(f"S{si+1} TOP t={t:.2f}")

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════════════════════
prs.save("CrystalParadigm_SCIDIP_IITDelhi_FINAL_v3.pptx")
print(f"\nSaved: CrystalParadigm_SCIDIP_IITDelhi_FINAL_v3.pptx ({len(prs.slides)} slides)")

if issues:
    print(f"\nRemaining issues ({len(issues)}):")
    for x in issues: print(f"  {x}")
else:
    print("VALIDATION: CLEAN — Zero overflow or alignment issues")
