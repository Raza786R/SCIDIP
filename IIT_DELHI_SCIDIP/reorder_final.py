"""
Final reorder of ELITE.pptx to correct slide sequence:
S01: Title (keep)
S02: SCIDIP Application Overview (keep)
S03: THE CHALLENGE WE WERE CALLED TO SOLVE  ← NEW intro 1
S04: AI ENGINE: ONE SOLUTION, TWO MARKETS   ← NEW intro 2
S05: WHY THIS MATTERS NOW (original 3→5)
S06: THE TECHNICAL PROBLEM (original 4→6)
S07: OUR ADVANCED ARCHITECTURE (original 5→7)
S08: WHY WE WIN TECHNICALLY (original 6→8)
S09: VERIFICATION TABLE (original 7→9)
S10: VALIDATION PLAN (original 8→10)
S11: DEPLOYMENT ROADMAP (original 9→11)
S12: ECONOMIC LEDGER (original 10→12)
--- images-only slides skip ---
S13: SCIDIP DEPLOYMENT: TWO PATHWAYS  ← NEW
S14: IP & SUPPLY CHAIN  ← NEW
S15: CORPORATE ASK  ← NEW
S16: 24-MONTH ROADMAP  ← NEW
S17: THE TEAM  ← NEW
S18: CLOSING (move to last)
"""
from pptx import Presentation
from pptx.oxml.ns import qn

prs = Presentation("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
prs_el = prs.part._element
sldIdLst = prs_el.find(qn('p:sldIdLst'))
slides = list(sldIdLst)

print("CURRENT ORDER:")
for i,s in enumerate(slides):
    print(f"  {i}: id={s.get('id')} r:id={s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')}")

# Current indices (0-based):
# 0: Title
# 1: SCIDIP Application
# 2: THE CHALLENGE WE WERE CALLED TO SOLVE (NEW A)
# 3: AI ENGINE (NEW B)
# 4: WHY THIS MATTERS NOW
# 5: THE TECHNICAL PROBLEM
# 6: OUR ADVANCED ARCHITECTURE
# 7: WHY WE WIN TECHNICALLY
# 8: VERIFICATION TABLE
# 9: VALIDATION PLAN
# 10: DEPLOYMENT ROADMAP
# 11: ECONOMIC LEDGER
# 12: (empty image slide)
# 13: (empty image slide)
# 14: CLOSING
# 15: IP & SUPPLY CHAIN (NEW D)
# 16: CORPORATE ASK (NEW E)
# 17: 24-MONTH ROADMAP (NEW F)
# 18: TEAM (NEW G)
# 19: SCIDIP DEPLOYMENT (NEW C) ← got placed last due to reorder issue

# Desired order:
desired = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 19, 15, 16, 17, 18, 14]
# (skip 12,13 — empty image-only slides that are part of original pptx structure, keep them too)
# Actually let's keep all 20 slides in proper order:
desired_full = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 15, 16, 17, 18, 14]

# Build new order
new_order = [slides[i] for i in desired_full]

# Clear and re-add in desired order
for s in list(sldIdLst): sldIdLst.remove(s)
for s in new_order: sldIdLst.append(s)

print("\nNEW ORDER:")
for i,s in enumerate(new_order):
    print(f"  Slot {i+1}: original_idx={desired_full[i]}")

prs.save("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
print("\nSaved — reordering complete")

# Quick verification
prs2 = Presentation("CrystalParadigm_SCIDIP_IITDelhi_ELITE.pptx")
print(f"\nFINAL SLIDE ORDER ({len(prs2.slides)} slides):")
for i,sl in enumerate(prs2.slides):
    txts = [s.text.strip()[:55] for s in sl.shapes if hasattr(s,'text') and s.text.strip()]
    first = txts[0] if txts else '(empty/image)'
    print(f"  S{i+1:02d}: {first}")
