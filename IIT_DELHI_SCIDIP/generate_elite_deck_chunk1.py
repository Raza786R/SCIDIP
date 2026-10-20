import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE

# ==========================================
# PHASE 1: THE AESTHETIC CORE ENGINE
# ==========================================

# 1. Colors (Inverted Contrast Theme)
BG_COLOR = RGBColor(248, 249, 250)      # #F8F9FA (Off-White)
DARK_NAVY = RGBColor(11, 19, 43)        # #0B132B (Deep Aerospace Navy/Black)
ELECTRIC_BLUE = RGBColor(0, 85, 255)    # #0055FF (Vibrant Accent)
TEXT_WHITE = RGBColor(255, 255, 255)    # #FFFFFF (White Text on Navy Boxes)
TEXT_DARK = RGBColor(20, 20, 30)        # Dark text for light backgrounds

def init_presentation():
    """Initializes a 16:9 presentation."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def create_base_slide(prs, title_text, subtitle_text=""):
    """Creates a slide with the Elite Light background and standard title header."""
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)
    
    # 1. Draw the global light background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_COLOR
    bg.line.fill.background() # No line
    
    # 2. Add Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.bold = True
    p.font.size = Pt(28)
    p.font.color.rgb = DARK_NAVY
    
    # 3. Add Subtitle (Optional)
    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(12), Inches(0.5))
        tf_sub = sub_box.text_frame
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.size = Pt(16)
        p_sub.font.color.rgb = ELECTRIC_BLUE
        p_sub.font.bold = True
        
    return slide

def add_rounded_box(slide, left, top, width, height, title, body_text_list, bg_color=DARK_NAVY, text_color=TEXT_WHITE):
    """Draws a premium rounded rectangle container with text inside to prevent overlaps."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.fill.background()
    shape.adjustments[0] = 0.05 
    
    tf = shape.text_frame
    tf.word_wrap = True
    
    if title:
        p = tf.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = ELECTRIC_BLUE if bg_color == DARK_NAVY else DARK_NAVY
        p.space_after = Pt(10)
    
    for i, text in enumerate(body_text_list):
        if i == 0 and not title:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(13)
        p.font.color.rgb = text_color
        p.space_after = Pt(6)
        
    return shape

def add_placeholder_frame(slide, left, top, width, height, directive_text):
    """Draws a dashed placeholder frame for complex visualizations."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(230, 235, 240)
    shape.line.color.rgb = ELECTRIC_BLUE
    shape.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    shape.line.width = Pt(2)
    shape.adjustments[0] = 0.05
    
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f"INSERT VISUALIZATION:\n{directive_text}"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = DARK_NAVY
    p.alignment = PP_ALIGN.CENTER
    return shape

def build_slides():
    prs = init_presentation()
    
    # Slide 1
    s1 = create_base_slide(prs, "Accelerating Innovation at the Intersection of AI and Material Science", "CRYSTAL PARADIGM | IIT DELHI SCIDIP APPLICATION")
    add_rounded_box(s1, Inches(0.5), Inches(1.8), Inches(6), Inches(1.5), None, 
                    ["Crystal Paradigm is an elite Deep-Tech Discovery Platform. We leverage artificial intelligence and high-performance computing to accelerate material discovery from 5 years to 4 weeks."])
    add_rounded_box(s1, Inches(0.5), Inches(3.5), Inches(6), Inches(2.2), "Our Expanding Pipeline:", 
                    ["Our AI architecture is highly scalable. We are actively advancing research across:",
                     "• Supercapacitors & Solid-State Battery Electrolytes (Li-ion & Na-ion)",
                     "• Next-Generation Solar Materials & Advanced Sensor Matrices",
                     "• Current Traction: 1 Patent Accepted, 4 Research Papers Under Review, and active industry collaborations."])
    add_rounded_box(s1, Inches(0.5), Inches(5.9), Inches(12.33), Inches(1.2), "The SCIDIP Spearhead:", 
                    ["For this application, we are deploying our most extreme, fully-validated Proof of Concept: An AI-generated, aerospace-grade Refractory High-Entropy Alloy (RHEA) engineered to solve Sona Comstar's terrestrial thermal bottlenecks."],
                    bg_color=ELECTRIC_BLUE, text_color=TEXT_WHITE)
    add_placeholder_frame(s1, Inches(6.8), Inches(1.8), Inches(6), Inches(3.9), "A sleek composite graphic showing glowing atomic structures spanning across different domains (batteries, sensors, aerospace).")
    
    # Slide 2
    s2 = create_base_slide(prs, "PROVING THE PHYSICS: THE AEROSPACE THERMAL BOTTLENECK", "Solving the 1400°C Turbine Entry Temperature Problem")
    add_rounded_box(s2, Inches(0.5), Inches(1.8), Inches(6), Inches(2.5), "The Aerothermal Fire Limit:", 
                    ["Traditional nickel-based superalloys have hit a physical ceiling. When shielded with ceramics, the massive Coefficient of Thermal Expansion (CTE) mismatch causes the protective armor to violently spall off under rapid thermal cycling."])
    add_rounded_box(s2, Inches(6.8), Inches(1.8), Inches(6), Inches(2.5), "The Crystal Paradigm AI Solution (Top Breakthrough: Candidate C):", 
                    ["Instead of laboratory trial-and-error, our proprietary 11-phase AI pipeline screened thousands of combinatorial matrices to isolate top-tier Refractory High-Entropy Alloys. Our champion candidate (Ta-W-Cr-V-Ti-Zr-Hf + 2.8% Al) proves the math:",
                     "• The Physics: By forcing a Titanium-dominant solid solution, we mathematically closed the CTE gap.",
                     "• The Manufacturing: We deployed an 11-layer Functionally Graded Material (FGM) matrix using an exact n=1.1 power-law gradient.",
                     "• The Result: Interface shear stress was dropped to an ultra-low 15.95 MPa, completely eliminating delamination."])
    add_placeholder_frame(s2, Inches(0.5), Inches(4.5), Inches(12.33), Inches(2.5), "A side-by-side comparison. Left: A traditional cracked coating on a superalloy. Right: Our 11-layer Functionally Graded Material (FGM) transition, showing a smooth power-law gradient from metallic HEA to LZO ceramic.")
    
    # Slide 3
    s3 = create_base_slide(prs, "THE SCIDIP CROSSOVER: FROM AEROSPACE TO EPIC MOBILITY", "Bridging 1400°C Turbine Tech to Sona Comstar")
    add_rounded_box(s3, Inches(0.5), Inches(1.8), Inches(12.33), Inches(1.2), None, 
                    ["If our AI architecture can prevent a jet turbine from melting at 1400°C, it can revolutionize the thermal limits of terrestrial mobility.",
                     "We are entering the IIT Delhi SCIDIP program under the Advanced Materials category because Sona Comstar’s EPIC (Electric, Personalized, Intelligent, Connected) roadmap is directly bottlenecked by thermodynamics. The exact thermal ceilings capping aerospace are capping Sona Comstar:"])
    add_rounded_box(s3, Inches(0.5), Inches(3.2), Inches(6), Inches(1.8), "1. Precision Forging Dies (Driveline):", 
                    ["Sona Comstar's legacy H13 tool steel dies suffer from rapid thermal fatigue and yield strength collapse at 1200°C during high-speed gear forging. Our HEA architectures retain over 917.7 MPa yield strength at these exact temperatures."])
    add_rounded_box(s3, Inches(6.8), Inches(3.2), Inches(6), Inches(1.8), "2. Next-Generation Traction Motors (Electric):", 
                    ["As Sona Comstar scales magnet-less Switched Reluctance Motors (SRMs), traditional metals degrade under the severe localized thermal loads generated by extreme torque densities."])
    add_placeholder_frame(s3, Inches(0.5), Inches(5.2), Inches(12.33), Inches(1.8), "A sleek arrow connecting 'AEROSPACE EXTREMES (1400°C Turbine)' on the left, pointing to 'TERRESTRIAL MOBILITY (H13 Forging Dies & EV SRMs)' on the right.")
    
    # Slide 4
    s4 = create_base_slide(prs, "DEPLOYING AEROSPACE GRADE MATERIALS AT COMMERCIAL SCALE", "Optimized for the Supply Chain")
    add_rounded_box(s4, Inches(0.5), Inches(1.8), Inches(12.33), Inches(0.8), None, 
                    ["Our AI engine does not just optimize for physics; it optimizes for the supply chain."])
    add_rounded_box(s4, Inches(0.5), Inches(2.8), Inches(3.9), Inches(4.0), "1. Raw Material Cost Reduction", 
                    ["By programmatically identifying that we could substitute highly expensive, supply-constrained Hafnium with optimized Titanium, our AI dropped the raw material cost of the alloy by 15-20% (achieving ~$170/kg), making aerospace-grade materials viable for commercial automotive forging."])
    add_rounded_box(s4, Inches(4.6), Inches(2.8), Inches(4.1), Inches(4.0), "2. ESG & Sustainability", 
                    ["Crystal Paradigm’s Candidate C is fully quantified for environmental impact, capping Embodied Energy at a highly sustainable 1680 MJ/kg—directly supporting zero-emissions manufacturing goals."])
    add_rounded_box(s4, Inches(8.9), Inches(2.8), Inches(3.9), Inches(4.0), "3. Supply Chain Resilience", 
                    ["By utilizing a 9-element multi-principal matrix, we drastically reduce reliance on single critical minerals (like Neodymium) controlled by volatile foreign supply chains. Our pipeline ensures true indigenous, self-reliant IP generation for the Indian mobility sector ('Make in India')."])

    prs.save("CrystalParadigm_Elite_Deck_Chunk1.pptx")
    print("SUCCESS: Chunk 1 generated as CrystalParadigm_Elite_Deck_Chunk1.pptx")

if __name__ == '__main__':
    build_slides()
