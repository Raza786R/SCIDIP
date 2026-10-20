"""Targeted fix for 4 remaining overflow issues in v3."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pptx import Presentation
from pptx.util import Inches, Pt

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

prs = Presentation("CrystalParadigm_SCIDIP_IITDelhi_FINAL_v3.pptx")
slides = list(prs.slides)

# S2: footer band still at h=0.59 (was the one at l=0.00)
for sh in slides[1].shapes:
    l, t, w, h = gp(sh)
    if near(t, 5.08, 0.03) and h > 0.55 and near(l, 0.0, 0.05):
        sp(sh, h=0.54); print(f"[S02] Footer h={h:.2f} → 0.54")

# S7: text box overflows right at l=5.09+w=5.07=10.16
# This is from the original PPTX — just clip the width
for sh in slides[6].shapes:
    l, t, w, h = gp(sh)
    if near(l, 5.09, 0.05) and l + w > 10.0:
        sp(sh, w=4.85); print(f"[S07] Text w={w:.2f} → 4.85 (was {l:.2f}+{w:.2f}={l+w:.2f})")

# S15: shape at t=5.24 h=0.44 overflows — clip height
for sh in slides[14].shapes:
    l, t, w, h = gp(sh)
    if t + h > 5.62 and t < 5.0 and l < 5.0:
        new_h = max(0.1, 5.60 - t)
        sp(sh, h=new_h); print(f"[S15] Clip t={t:.2f}+h={h:.2f} → h={new_h:.2f}")

# S20: background image at t=0 h=5.92 — clip to 5.62
for sh in slides[19].shapes:
    l, t, w, h = gp(sh)
    if sh.shape_type == 13 and near(t, 0.0, 0.05) and h > 5.65:
        sp(sh, h=5.62); print(f"[S20] BG image h={h:.2f} → 5.62")

# Final validation
SW, SH = 10.0, 5.62
issues = []
for si, slide in enumerate(prs.slides):
    for sh in slide.shapes:
        l, t, w, h = gp(sh)
        if l+w > SW+0.03: issues.append(f"S{si+1} RIGHT l={l:.2f}+{w:.2f}={l+w:.2f}")
        if t+h > SH+0.03: issues.append(f"S{si+1} BOTTOM t={t:.2f}+{h:.2f}={t+h:.2f}")
        if l < -0.03:     issues.append(f"S{si+1} LEFT l={l:.2f}")
        if t < -0.03:     issues.append(f"S{si+1} TOP t={t:.2f}")

prs.save("CrystalParadigm_SCIDIP_IITDelhi_FINAL_v3.pptx")
print(f"\nSaved. Issues: {len(issues)}")
for x in issues: print(f"  {x}")
if not issues: print("CLEAN: Zero overflows")
