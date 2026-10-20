"""
GENTLE FIX V5 - No Layout Destruction
Uses CrystalParadigm_SCIDIP_IITDelhi_FINAL.pptx as base.
"""
import shutil, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def I(v): return Inches(v)
def near(a, b, tol=0.08): return abs(a - b) < tol
def gp(s):
    return (s.left/914400 if s.left else 0, s.top/914400 if s.top else 0,
            s.width/914400 if s.width else 0, s.height/914400 if s.height else 0)
def sp(s, l=None, t=None, w=None, h=None):
    if l is not None: s.left   = I(l)
    if t is not None: s.top    = I(t)
    if w is not None: s.width  = I(w)
    if h is not None: s.height = I(h)

shutil.copy2("CrystalParadigm_SCIDIP_IITDelhi_FINAL.pptx", "CrystalParadigm_SCIDIP_Master_v5.pptx")
prs = Presentation("CrystalParadigm_SCIDIP_Master_v5.pptx")
slides = list(prs.slides)
print("Loaded base:", len(slides), "slides")

# --- 1. S1: Add precise Crystal Paradigm intro without dumping ---
s1 = slides[0]
b = s1.shapes.add_textbox(I(0.52), I(4.80), I(8.0), I(0.5))
tf = b.text_frame
tf.word_wrap = True
r = tf.paragraphs[0].add_run()
r.text = "Crystal Paradigm: Accelerating innovation and discovery at the intersection of AI and Material Science."
r.font.size = Pt(10)
r.font.bold = True
r.font.color.rgb = RGBColor(0x00, 0xB4, 0xD8)

p2 = tf.add_paragraph()
r2 = p2.add_run()
r2.text = "Active Domains: Supercapacitors | Rare-Earth Materials | Li-ion & Na-ion Cathodes/Electrolytes | Solar | Advanced Sensor Materials"
r2.font.size = Pt(8.5)
r2.font.color.rgb = RGBColor(0x55, 0x80, 0xA0)
print("[S01] Added precise CP domains text")

# --- 2. Fix Overflows safely ---
# S2: footer band t=5.08, h=0.59
for sh in slides[1].shapes:
    l, t, w, h = gp(sh)
    if near(t, 5.08) and h > 0.55 and l < 0.1: sp(sh, h=0.54)
# S5: Image t=0.20
for sh in slides[4].shapes:
    l, t, w, h = gp(sh)
    if sh.shape_type == 13 and t > 0.1 and t < 0.3: sp(sh, t=0.0)
# S6: Text w=5.07
for sh in slides[5].shapes:
    l, t, w, h = gp(sh)
    if near(l, 5.09) and l+w > 10.0: sp(sh, w=4.8)
# S17: Text w=2.0
for sh in slides[16].shapes:
    l, t, w, h = gp(sh)
    if near(l, 8.20) and l+w > 10.0: sp(sh, w=1.7)
# S20: Image l=-0.06
for sh in slides[19].shapes:
    l, t, w, h = gp(sh)
    if sh.shape_type == 13 and l < -0.01: sp(sh, l=0.0, h=5.62)

print("[Fixes] Overflow limits applied safely")

# --- 3. S12: Economic Ledger Sona Comstar text replace (No structure change) ---
s12_replacements = {
    'Fleet Scalability and Direct Operating Cost Reductions (Aerospace Case Study - Platform Applicable to Precision Forging & EV Thermal Management)': 'Quantified ROI: Forging Die Upgrades, EV Motor Materials & ESG Compliance',
    'Governing Aerospace Formula': 'Economic Mechanism',
    'Baseline Input Variable': 'Crystal Paradigm Value',
    'Net Annual Savings Yield': 'Sona Comstar Benefit',
    'Parasitic Bleed Air Cut': 'H13 Die Cost Reduction',
    'Δ m_bleed = m_baseline × 0.15': 'Ta-W-Cr-V-Ti HEA; ~$170/kg vs $280/kg Hf-alloy',
    '15% Reduction': '15–20% alloy material cost drop',
    'Frees Core Mass Flow': '₹2–4 Cr/Year saved across 9 plants',
    'Net SFC Efficiency Gain': 'Forging Die Lifespan Extension',
    'η_cycle = Δ SFC × 1.0': 'Candidate C: >917.7 MPa at 1,200°C',
    '1.5% Net Reduction': '3× longer tooling life',
    'Maximizes Core Thrust': '₹5–8 Cr/Year in MRO downtime savings',
    'Volumetric Fuel Savings': 'EV SRM Motor Thermal Material',
    'V_saved = 3,000 hr × 2,400 kg/hr × 0.015': 'FGM shield: 15.95 MPa interface',
    '7,200 Metric Tons Baseline': 'Rare-Earth-Free SRM at scale',
    '135,000 Liters / Aircraft': 'Eliminates ₹50–80 Cr Nd import cost',
    'Direct Operating Cost Cut': 'ESG Supplier Compliance',
    'Cash Savings = V_saved × $0.85 /L': 'Embodied Energy: 1,680 MJ/kg',
    '$0.85/L Jet A-1 Price': 'Qualifies 75% ESG supplier mandate',
    '$114,750 / Aircraft': 'Unlocks full EPIC tier access',
    'Fleet Scalability Revenue': 'Total Commercialization Potential',
    'Total Yield = Cash Savings × 100 Jets': 'AI pipeline → materials for all EPIC verticals',
    '100 Narrowbody Fleet': '₹15–20 Cr / Year (conservative)',
    '$11,475,000 / Year': '+ JV / Acquisition pathway',
    '*Calculations based on global average aviation fuel pricing and industry-standard propulsion metrics.': '*All INR estimates are conservative, based on current Sona Comstar manufacturing footprint.'
}

for sh in slides[10].shapes:  # S11 (0-based 10 is S11 in this deck)
    if not hasattr(sh, 'text_frame'): continue
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            for old, new in s12_replacements.items():
                if old in r.text or r.text.strip() == old:
                    r.text = r.text.replace(old, new)

# --- 4. Aerospace text in other slides ---
for sh in slides[7].shapes:  # S08: WHAT IS PROVEN TODAY
    if hasattr(sh, 'text_frame'):
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if 'Transpiration Film Stability' in r.text: r.text = 'Forging Die Thermal Fit'
                if 'Modeled (CFD Jet Lift)' in r.text: r.text = 'Simulated via 3D FEA'
                if 'Pending Thermal Cycling Test' in r.text: r.text = 'Pending Die Trial — Plant'

for sh in slides[9].shapes: # S10: TECHNOLOGY VALIDATION
    if hasattr(sh, 'text_frame'):
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if 'Flight-Readiness Funnel' in r.text: r.text = 'Factory-Floor Integration'

# --- 5. Mini font bumps (+1 pt) ONLY for very tiny fonts (sz 6-7) ---
for si, slide in enumerate(slides):
    if si < 13: continue # Only target the new slides (14-20) which the user complained about
    for sh in slide.shapes:
        if not hasattr(sh, 'text_frame'): continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size:
                    sz_pt = r.font.size / 12700
                    if 6.0 <= sz_pt < 8.0:
                        r.font.size = Pt(sz_pt + 1.0) # ONLY +1 pt ("small small like that mini")

prs.save("CrystalParadigm_SCIDIP_Master_v5.pptx")
print("Saved CrystalParadigm_SCIDIP_Master_v5.pptx successfully!")
