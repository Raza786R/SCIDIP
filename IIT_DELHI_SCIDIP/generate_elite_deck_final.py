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

BG_COLOR = RGBColor(248, 249, 250)      # #F8F9FA
DARK_NAVY = RGBColor(11, 19, 43)        # #0B132B
ELECTRIC_BLUE = RGBColor(0, 85, 255)    # #0055FF
TEXT_WHITE = RGBColor(255, 255, 255)
TEXT_DARK = RGBColor(20, 20, 30)

def init_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def create_base_slide(prs, title_text, subtitle_text=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_COLOR
    bg.line.fill.background()
    
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.bold = True
    p.font.size = Pt(28)
    p.font.color.rgb = DARK_NAVY
    
    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(12), Inches(0.5))
        tf_sub = sub_box.text_frame
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.size = Pt(16)
        p_sub.font.color.rgb = ELECTRIC_BLUE
        p_sub.font.bold = True
        
    return slide

def add_rounded_box(slide, left, top, width, height, title, body_text_list, bg_color=DARK_NAVY, text_color=TEXT_WHITE, font_size=13):
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
        p.font.size = Pt(16)
        p.font.color.rgb = ELECTRIC_BLUE if bg_color == DARK_NAVY else DARK_NAVY
        p.space_after = Pt(8)
    
    for i, text in enumerate(body_text_list):
        if i == 0 and not title:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(font_size)
        p.font.color.rgb = text_color
        p.space_after = Pt(4)
        
    return shape

def add_placeholder_frame(slide, left, top, width, height, directive_text):
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
    
    # --- SLIDE 1 ---
    s1 = create_base_slide(prs, "Accelerating Innovation at the Intersection of AI and Material Science", "CRYSTAL PARADIGM | IIT DELHI SCIDIP APPLICATION")
    add_rounded_box(s1, Inches(0.5), Inches(1.8), Inches(6), Inches(1.3), None, 
                    ["Crystal Paradigm is an elite Deep-Tech Discovery Platform. We leverage artificial intelligence and high-performance computing to accelerate material discovery from 5 years to 4 weeks."])
    add_rounded_box(s1, Inches(0.5), Inches(3.3), Inches(6), Inches(2.3), "Our Expanding Pipeline:", 
                    ["Our AI architecture is highly scalable. We are actively advancing research across:",
                     "• Supercapacitors & Solid-State Battery Electrolytes (Li-ion & Na-ion)",
                     "• Next-Generation Solar Materials & Advanced Sensor Matrices",
                     "• Current Traction: 1 Patent Accepted, 4 Research Papers Under Review, and active collaborations."])
    add_rounded_box(s1, Inches(0.5), Inches(5.8), Inches(12.33), Inches(1.2), "The SCIDIP Spearhead:", 
                    ["For this application, we are deploying our most extreme, fully-validated Proof of Concept: An AI-generated, aerospace-grade Refractory High-Entropy Alloy (RHEA) engineered to solve Sona Comstar's terrestrial thermal bottlenecks."],
                    bg_color=ELECTRIC_BLUE, text_color=TEXT_WHITE)
    add_placeholder_frame(s1, Inches(6.8), Inches(1.8), Inches(6), Inches(3.8), "A sleek composite graphic showing glowing atomic structures spanning across different domains (batteries, sensors, aerospace).")
    
    # --- SLIDE 2 ---
    s2 = create_base_slide(prs, "PROVING THE PHYSICS: THE AEROSPACE THERMAL BOTTLENECK", "Solving the 1400°C Turbine Entry Temperature Problem")
    add_rounded_box(s2, Inches(0.5), Inches(1.8), Inches(6), Inches(2.2), "The Aerothermal Fire Limit:", 
                    ["Traditional nickel-based superalloys have hit a physical ceiling. When shielded with ceramics, the massive Coefficient of Thermal Expansion (CTE) mismatch causes the protective armor to violently spall off under rapid thermal cycling."])
    add_rounded_box(s2, Inches(6.8), Inches(1.8), Inches(6), Inches(2.2), "The AI Solution (Top Breakthrough: Candidate C):", 
                    ["Instead of laboratory trial-and-error, our proprietary 11-phase AI pipeline screened thousands of combinatorial matrices to isolate top-tier RHEAs. Our champion candidate (Ta-W-Cr-V-Ti-Zr-Hf + 2.8% Al) proves the math:",
                     "• The Physics: By forcing a Titanium-dominant solid solution, we mathematically closed the CTE gap.",
                     "• The Manufacturing: We deployed an 11-layer Functionally Graded Material (FGM) matrix using an exact n=1.1 power-law gradient.",
                     "• The Result: Interface shear stress was dropped to an ultra-low 15.95 MPa."])
    add_placeholder_frame(s2, Inches(0.5), Inches(4.2), Inches(12.33), Inches(2.8), "A side-by-side comparison. Left: A traditional cracked coating on a superalloy. Right: Our 11-layer Functionally Graded Material (FGM) transition, showing a smooth power-law gradient from metallic HEA to LZO ceramic.")
    
    # --- SLIDE 3 ---
    s3 = create_base_slide(prs, "THE SCIDIP CROSSOVER: FROM AEROSPACE TO EPIC MOBILITY", "Bridging 1400°C Turbine Tech to Sona Comstar")
    add_rounded_box(s3, Inches(0.5), Inches(1.8), Inches(12.33), Inches(1.2), None, 
                    ["If our AI architecture can prevent a jet turbine from melting at 1400°C, it can revolutionize the thermal limits of terrestrial mobility.",
                     "We are entering the IIT Delhi SCIDIP program under the Advanced Materials category because Sona Comstar’s EPIC (Electric, Personalized, Intelligent, Connected) roadmap is directly bottlenecked by thermodynamics. The exact thermal ceilings capping aerospace are capping Sona Comstar:"])
    add_rounded_box(s3, Inches(0.5), Inches(3.2), Inches(6), Inches(1.8), "1. Precision Forging Dies (Driveline):", 
                    ["Sona Comstar's legacy H13 tool steel dies suffer from rapid thermal fatigue and yield strength collapse at 1200°C during high-speed gear forging. Our HEA architectures retain over 917.7 MPa yield strength at these exact temperatures."])
    add_rounded_box(s3, Inches(6.8), Inches(3.2), Inches(6), Inches(1.8), "2. Next-Generation Traction Motors (Electric):", 
                    ["As Sona Comstar scales magnet-less Switched Reluctance Motors (SRMs), traditional metals degrade under the severe localized thermal loads generated by extreme torque densities."])
    add_placeholder_frame(s3, Inches(0.5), Inches(5.2), Inches(12.33), Inches(1.8), "A sleek arrow connecting 'AEROSPACE EXTREMES (1400°C Turbine)' on the left, pointing to 'TERRESTRIAL MOBILITY (H13 Forging Dies & EV SRMs)' on the right.")
    
    # --- SLIDE 4 ---
    s4 = create_base_slide(prs, "DEPLOYING AEROSPACE GRADE MATERIALS AT COMMERCIAL SCALE", "Optimized for the Supply Chain")
    add_rounded_box(s4, Inches(0.5), Inches(1.8), Inches(12.33), Inches(0.8), None, 
                    ["Our AI engine does not just optimize for physics; it optimizes for the supply chain."])
    add_rounded_box(s4, Inches(0.5), Inches(2.8), Inches(3.9), Inches(4.0), "1. Raw Material Cost Reduction", 
                    ["By programmatically identifying that we could substitute highly expensive, supply-constrained Hafnium with optimized Titanium, our AI dropped the raw material cost of the alloy by 15-20% (achieving ~$170/kg), making aerospace-grade materials viable for commercial automotive forging."])
    add_rounded_box(s4, Inches(4.6), Inches(2.8), Inches(4.1), Inches(4.0), "2. ESG & Sustainability", 
                    ["Crystal Paradigm’s Candidate C is fully quantified for environmental impact, capping Embodied Energy at a highly sustainable 1680 MJ/kg—directly supporting zero-emissions manufacturing goals."])
    add_rounded_box(s4, Inches(8.9), Inches(2.8), Inches(3.9), Inches(4.0), "3. Supply Chain Resilience", 
                    ["By utilizing a 9-element multi-principal matrix, we drastically reduce reliance on single critical minerals (like Neodymium) controlled by volatile foreign supply chains. Our pipeline ensures true indigenous, self-reliant IP generation for the Indian mobility sector ('Make in India')."])

    # --- SLIDE 5 ---
    s5 = create_base_slide(prs, "THE CRYSTAL PARADIGM AI ENGINE: STEP 1", "Secure Ingestion & Empirical Thermodynamic Gating")
    add_rounded_box(s5, Inches(0.5), Inches(1.8), Inches(12.33), Inches(1.2), None, 
                    ["Before a single machine learning model is trained, our pipeline strictly enforces the laws of physics and commercial viability. We ingest massive combinatorial spaces (Materials Project, AFLOW), but ruthlessly filter out unstable or toxic formulations using Miedema’s Empirical Rules to ensure day-one compliance with Sona Comstar's 75% Supplier ESG mandate."])
    add_rounded_box(s5, Inches(0.5), Inches(3.2), Inches(6), Inches(3.5), "The Thermodynamic Gating Protocol:", 
                    ["• Atomic Size Mismatch (δ): Strictly capped at ≤ 6.6% to prevent lattice distortion under high torque.",
                     "• Enthalpy of Mixing (ΔH_mix): Bounded between -15 and +5 kJ/mol.",
                     "• Valence Electron Concentration (VEC): Bounded between 4.0 and 6.8. This is critical: A VEC < 6.8 mathematically guarantees a stable Body-Centered Cubic (BCC) matrix and explicitly eliminates the risk of brittle Sigma phase formation.",
                     "• Omega Parameter (Ω): Must be ≥ 1.1 to guarantee dominant solid solution stability."])
    add_placeholder_frame(s5, Inches(6.8), Inches(3.2), Inches(6), Inches(3.5), "Process Flowchart (Left to Right) with a 'Sona Comstar 75% Supplier Rule' compliance stamp. Show raw database inputs passing through a rigid 'Thermodynamic Filter'.")

    # --- SLIDE 6 ---
    s6 = create_base_slide(prs, "THE CRYSTAL PARADIGM AI ENGINE: STEP 2", "Dual-Stream Machine Learning Surrogates")
    add_rounded_box(s6, Inches(0.5), Inches(1.8), Inches(12.33), Inches(1.0), None, 
                    ["To predict material behavior for Sona Comstar's extreme-environment SRMs and H13 forging dies, we engineered a dual-stream surrogate architecture mapping both theoretical physics and real-world variance."])
    add_rounded_box(s6, Inches(0.5), Inches(3.0), Inches(6), Inches(2.2), "Model 1: Theoretical Bulk Modulus (Random Forest)", 
                    ["• Architecture & Features: 100 Estimators predicting across atomic radius (r), electronegativity (X), VEC, melting temp (Tm), and mass standard deviations.",
                     "• Performance: Audited Test R² of 0.977 and a Mean Absolute Error (MAE) of just 8.11 GPa."])
    add_rounded_box(s6, Inches(6.8), Inches(3.0), Inches(6), Inches(2.2), "Model 2: Experimental Yield Strength (Gradient Boosting)", 
                    ["• Transfer Learning Logic: Trained on an experimental MPEA dataset. We heavily weighted exact 5-element target alloys (Weight=10) while leveraging broader refractory alloys (Weight=1).",
                     "• The Thermal Knockdown Penalty: Because forging dies operate near 1200°C, we enforce a severe homologous temperature knockdown factor (0.45)."])
    add_placeholder_frame(s6, Inches(0.5), Inches(5.4), Inches(12.33), Inches(1.8), "Left Column: Neural network graphic labeled 'Random Forest'. Right Column: Neural network graphic labeled 'Gradient Boosting: Transfer Learning'.")

    # --- SLIDE 7 ---
    s7 = create_base_slide(prs, "THE CRYSTAL PARADIGM AI ENGINE: STEP 3", "Constrained Differential Evolution (DE)")
    add_rounded_box(s7, Inches(0.5), Inches(1.8), Inches(12.33), Inches(1.0), None, 
                    ["To discover completely novel alloys, our AI sweeps a continuous 9-element space using a Softmax activation function to generate perfect sum-to-one fractional matrices. The objective function maximizes the thermomechanical Safety Factor, heavily penalized by strict terrestrial/aerospace limits:"])
    add_rounded_box(s7, Inches(0.5), Inches(3.0), Inches(6), Inches(2.2), "Commercial Penalties:", 
                    ["1. Sigma Phase Mitigation: Massive penalty (5.0) if 'Sigma Formers' (W + Cr + Mo) exceed 50%.",
                     "2. Vanadium Volatility: Penalized if V > 20%, preventing toxic outgassing.",
                     "3. ESG Weight Budget: Hard penalty if alloy density exceeds 11.0 g/cm³.",
                     "4. Oxidation Barrier: Demands a minimum of 15% Chromium."])
    add_rounded_box(s7, Inches(6.8), Inches(3.0), Inches(6), Inches(2.2), "Result (Candidate C):", 
                    ["The DE optimizer achieved a maximum fitness score of 1.5981 (Safety Factor), finding a globally optimal solution (Titanium 21.7%) that cleared every penalty and dropped the CTE mismatch to an unprecedented 2.66 μm/mK."], bg_color=ELECTRIC_BLUE)
    add_placeholder_frame(s7, Inches(0.5), Inches(5.4), Inches(12.33), Inches(1.8), "A 3D topographical optimization surface with a glowing 'Global Optimum' point calling out Sona Comstar commercial limits.")

    # --- SLIDE 8 ---
    s8 = create_base_slide(prs, "WHAT IS PROVEN TODAY AND WHAT IS NOT", "High-Fidelity Verification Metrics and TRL Maturity Status")
    add_rounded_box(s8, Inches(0.5), Inches(1.8), Inches(12.33), Inches(1.2), None, 
                    ["Our platform is currently at TRL 3+. All computational physics and validations are fully confirmed in-silico via PyCalphad, 1D/3D FEA, and MACE MD. We are applying to SCIDIP to execute physical TRL 4 lab validation utilizing IIT Delhi’s Central Research Facility (CRF) and NIDHI-CoE."])
    add_rounded_box(s8, Inches(0.5), Inches(3.2), Inches(12.33), Inches(3.8), "TRL Validation Matrix:", 
                    ["• BCC Phase Security: Verified (CALPHAD) -> Pending High-Temp XRD (IIT Delhi CRF) -> Target: 0% Brittle Sigma Phase [STATUS: GREEN]",
                     "• Elastic Modulus Surface: Audited (Test R²=0.977) -> Pending NIDHI-CoE Tensile -> Target: MAE ≤ 8.11 GPa [STATUS: GREEN]",
                     "• Oxidation Scale Kinetics: Verified (2.8% Al Pivot) -> Pending STA/TGA Weight (IIT Delhi) -> Target: Mass Gain < 10 mg/cm² [STATUS: GREEN]",
                     "• Interfacial Bond Safety: Verified (1D/3D FEA) -> Pending CRF Thermal Shock Test -> Target: Safety Factor ≥ 1.50 [STATUS: GREEN]",
                     "• Physical Prototyping: Fully Formulated -> Not Yet Tested -> Target: TRL 4 Coupon Assembly [STATUS: PENDING]"])

    # --- SLIDE 9 ---
    s9 = create_base_slide(prs, "THE FINAL ARCHITECTURE (CANDIDATE C)", "From In-Silico Chemistry to Print-Ready Manufacturing")
    add_rounded_box(s9, Inches(0.5), Inches(1.8), Inches(6), Inches(3.2), "The Crystal Paradigm Breakthrough:", 
                    ["Through 11 phases of autonomous generation, our AI produced Candidate C, a hyper-optimized RHEA designed specifically for extreme thermal shock.",
                     "1. The Titanium Pivot: Our AI substituted heavy Hafnium for Titanium (21.7%). It aggressively closed the CTE mismatch with the ceramic coating, dropping the gap to just 2.66 μm/mK.",
                     "2. The Aluminum Armor: The AI executed a micro-addition of 2.8 at% Aluminum to force the formation of a highly stable α-Al₂O₃ protective armor scale."])
    add_rounded_box(s9, Inches(0.5), Inches(5.2), Inches(6), Inches(1.8), "3. The Manufacturing Recipe:", 
                    ["We have directly exported the continuous FGM physics curves into a discrete, print-ready 11-layer `manufacturing_recipe.csv` (ranging from 0.0mm 100% alloy to 5.0mm 100% LZO ceramic). Ready for DED 3D printing."])
    add_placeholder_frame(s9, Inches(6.8), Inches(1.8), Inches(6), Inches(5.2), "Split Screen showing chemistry and manufacturing. Left: 3D render of an SRM or forging die. Right: Cross-section of the 11-layer print matrix.")

    # --- SLIDE 10 ---
    s10 = create_base_slide(prs, "THE COMMERCIAL IMPACT FOR SONA COMSTAR", "Fleet Scalability and Direct Operating Cost Reductions")
    add_rounded_box(s10, Inches(0.5), Inches(1.8), Inches(12.33), Inches(0.8), None, 
                    ["By bridging aerospace materials into Sona Comstar's EPIC mobility framework, we generate massive downstream financial returns."])
    add_rounded_box(s10, Inches(0.5), Inches(2.8), Inches(3.9), Inches(4.0), "Raw Material Procurement", 
                    ["The Physics Trigger: 75% reduction in Hafnium, substituted with Titanium.",
                     "",
                     "The Commercial Result: 15-20% Drop in Alloy Cost. Achieves ~$170/kg, enabling high-volume EV commercialization."])
    add_rounded_box(s10, Inches(4.6), Inches(2.8), Inches(4.1), Inches(4.0), "Tooling & Forging Uptime", 
                    ["The Physics Trigger: H13 Dies retain 917.7 MPa yield strength at 1200°C.",
                     "",
                     "The Commercial Result: Drastic MRO Reduction. Eliminates thermal fatigue cracking, vastly extending tooling life and manufacturing throughput."])
    add_rounded_box(s10, Inches(8.9), Inches(2.8), Inches(3.9), Inches(4.0), "Next-Gen EV Motors", 
                    ["The Physics Trigger: Elimination of localized thermal hotspots in SRMs.",
                     "",
                     "The Commercial Result: Rare-Earth Independence. Enables high-power magnet-less motors without thermal degradation."])

    # --- SLIDE 11 ---
    s11 = create_base_slide(prs, "SCIDIP DEPLOYMENT 1: NEXT-GEN FORGING DIES", "Solving Sona Comstar's Differential Gear Bottleneck")
    add_rounded_box(s11, Inches(0.5), Inches(1.8), Inches(12.33), Inches(1.2), None, 
                    ["Sona Comstar’s core competitive advantage lies in precision forging of differential bevel gears. However, legacy H13 tool steel dies suffer massive yield strength collapse and thermal fatigue when operating near 1200°C, causing costly manufacturing downtime."])
    add_rounded_box(s11, Inches(0.5), Inches(3.2), Inches(6), Inches(3.8), "The Crystal Paradigm Upgrade:", 
                    ["Our 11-layer FGM architecture replaces the traditional monolithic die.",
                     "• The Core: The Ta-W-Cr-V-Ti-Zr-Hf alloy retains >917.7 MPa yield strength at 1200°C, preventing mechanical deformation.",
                     "• The Surface: The LZO (Lanthanum Zirconate) ceramic outer layer acts as a supreme thermal barrier, preventing heat transfer from the hot-forged blank into the die.",
                     "• The Result: Elimination of rapid thermal fatigue cracking, vastly extending tooling life."])
    add_placeholder_frame(s11, Inches(6.8), Inches(3.2), Inches(6), Inches(3.8), "Show a traditional H13 tool steel die cracking under thermal fatigue vs. our Candidate C FGM die operating smoothly at 1200°C.")

    # --- SLIDE 12 ---
    s12 = create_base_slide(prs, "SCIDIP DEPLOYMENT 2: MAGNET-LESS EV MOTORS", "Enabling Rare-Earth Independence in Traction Motors")
    add_rounded_box(s12, Inches(0.5), Inches(1.8), Inches(12.33), Inches(1.2), None, 
                    ["As part of the 'EPIC' roadmap, Sona Comstar is heavily investing in Switched Reluctance Motors (SRMs) to eliminate reliance on imported Neodymium magnets. The engineering bottleneck? SRMs generate extreme, localized thermal hotspots that degrade traditional stator/rotor metals."])
    add_rounded_box(s12, Inches(0.5), Inches(3.2), Inches(6), Inches(3.8), "The Crystal Paradigm Upgrade:", 
                    ["By deploying our aerospace-derived Candidate C, we provide Sona Comstar with a structural material capable of surviving localized high-temperature spikes.",
                     "• Thermal Shielding: The FGM gradient handles rapid thermal cycling without delamination (15.95 MPa interface shear stress), acting as a physical shield for sensitive copper windings.",
                     "• Make-In-India Supply Chain: By substituting Hafnium for Titanium, we drastically drop the alloy cost to ~$170/kg."])
    add_placeholder_frame(s12, Inches(6.8), Inches(3.2), Inches(6), Inches(3.8), "A CAD-style blueprint of a Switched Reluctance Motor (SRM) with thermal heat-map hotspots.")

    # --- SLIDE 13 ---
    s13 = create_base_slide(prs, "INTELLECTUAL PROPERTY & DE-RISKING THE SUPPLY CHAIN", "True Aatmanirbharta for the Indian Mobility Sector")
    add_rounded_box(s13, Inches(0.5), Inches(1.8), Inches(12.33), Inches(0.8), None, 
                    ["Sona Comstar’s strategic reliance on rare-earth elements for EV motors is a massive supply chain vulnerability. Crystal Paradigm offers a computational pathway to complete import substitution."])
    add_rounded_box(s13, Inches(0.5), Inches(2.8), Inches(6), Inches(4.2), "The IP Framework:", 
                    ["1. The IP Moat: Our proprietary 11-phase AI architecture is a continuous IP generation engine. Candidate C is merely our first output.",
                     "2. Make-in-India Reality: By engineering out exotic, foreign-controlled minerals and optimizing around globally abundant Titanium and Chromium, we guarantee a secure, indigenous supply chain.",
                     "3. The IIT Delhi IP Framework: We are prepared to navigate the FITT incubation framework to jointly patent physical material formulations developed within the Central Research Facility (CRF)."])
    add_placeholder_frame(s13, Inches(6.8), Inches(2.8), Inches(6), Inches(4.2), "World map graphic showing supply chain vectors. Current reliance on Chinese Neodymium being replaced by an 'Indigenous Indian Innovation' node powered by Crystal Paradigm.")

    # --- SLIDE 14 ---
    s14 = create_base_slide(prs, "THE CRYSTAL PARADIGM CORPORATE ASK", "Bridging the Gap Between Informatics and the Factory Floor")
    add_rounded_box(s14, Inches(0.5), Inches(1.8), Inches(12.33), Inches(0.8), None, 
                    ["Crystal Paradigm is completely computationally validated (TRL 3+). We are applying to the Advanced Materials track of the SCIDIP program to access the precise ecosystem required to cross the 'valley of death'."])
    add_rounded_box(s14, Inches(0.5), Inches(2.8), Inches(5.8), Inches(2.0), "1. Technology & Lab Support (IIT Delhi CRF):", 
                    ["Immediate access to the NIDHI-CoE and CRF to execute High-Temperature XRD, SEM, and Simultaneous Thermal Analysis (STA) on physical witness coupons."])
    add_rounded_box(s14, Inches(6.5), Inches(2.8), Inches(5.8), Inches(2.0), "2. Sona Comstar Mentorship:", 
                    ["Direct engineering alignment with Sona Comstar’s precision forging division to ensure our 11-layer print matrices match factory-floor DED manufacturing tolerances."])
    add_rounded_box(s14, Inches(0.5), Inches(5.0), Inches(5.8), Inches(2.0), "3. SCIDIP Seed Ecosystem:", 
                    ["Integration into the SCIDIP funding and incubation framework to finance raw material atomization and multi-hopper 3D printing of the physical prototypes."])
    add_rounded_box(s14, Inches(6.5), Inches(5.0), Inches(5.8), Inches(2.0), "4. Corporate Market Connect:", 
                    ["Joint integration of the physical prototypes into Sona Comstar's downstream EV supply chain."])

    # --- SLIDE 15 ---
    s15 = create_base_slide(prs, "THE 24-MONTH INCUBATION ROADMAP", "From Computational Validation to Sona Comstar Integration")
    add_rounded_box(s15, Inches(0.5), Inches(1.8), Inches(12.33), Inches(0.8), None, 
                    ["Our execution strategy is strictly mapped to the 24-month SCIDIP incubation cycle at Atal Incubation Centre (AIC)."])
    add_rounded_box(s15, Inches(0.5), Inches(2.8), Inches(12.33), Inches(2.0), "Milestones:", 
                    ["• Months 1-6 (M1: Powder Synthesis): Procure raw metal powders and utilize IIT Delhi labs to verify composition purity.",
                     "• Months 6-12 (M2: Additive Manufacturing): Execute the 11-layer manufacturing_recipe.csv via DED to print physical witness coupons.",
                     "• Months 12-18 (M3: NIDHI-CoE & CRF Testing): Conduct physical yield strength testing and execute High-Temp XRD / STA thermal shock validation.",
                     "• Months 18-24 (M4: Corporate Handover): Present fully validated TRL 5/6 hardware to Sona Comstar."])
    add_placeholder_frame(s15, Inches(0.5), Inches(5.0), Inches(12.33), Inches(2.0), "A Gantt-style timeline graphic covering 24 months. A sleek arrow moving left to right, punctuated by major milestone nodes (M1 to M4).")

    # --- SLIDE 16 ---
    s16 = create_base_slide(prs, "THE RESEARCH LEADS", "Guided by Elite Academic and Scientific Expertise")
    add_rounded_box(s16, Inches(0.5), Inches(1.8), Inches(6), Inches(5.2), "Dr. Shilpa Choudhary (AI/ML Lead)", 
                    ["Recognized among the Top 2% Scientists Worldwide by Stanford University (2024), brings over 16 years of research expertise in Artificial Intelligence, Deep Learning, and AI-driven scientific applications.",
                     "With postdoctoral research experience at the Singapore Institute of Technology and the National Kaohsiung University of Science and Technology (Taiwan), she has authored over 100 research papers, 12 academic books, and holds multiple patents.",
                     "At Crystal Paradigm, she leads AI innovation, ML Architecture, Constrained Optimization, and Surrogate Model Design."], font_size=12)
    add_rounded_box(s16, Inches(6.8), Inches(1.8), Inches(6), Inches(5.2), "Dr. Kasarapu Venkataramana (Materials Science Lead)", 
                    ["Currently a Research Associate at CSIR-IICT working on a DRDO sponsored project. Associate Fellow of the Telangana Academy of Sciences (2024) and brings 12 years of research experience.",
                     "Authored 38 research publications (610+ citations) and serves as a recognized reviewer for Elsevier, Springer, and Taylor & Francis.",
                     "He provides critical domain oversight on computational chemistry, thermodynamics, and physical experimental validation. Specializes in High Entropy Oxides and advanced materials characterization."], font_size=12)

    # --- SLIDE 17 ---
    s17 = create_base_slide(prs, "THE CORE AI ARCHITECTS", "The Engine Driving the Day-to-Day AI Innovation")
    add_rounded_box(s17, Inches(0.5), Inches(1.8), Inches(6), Inches(4.0), "Mohammed Ahmed Raza (AI Research Intern)", 
                    ["CSE student at NGIT and Certified AI/ML Professional from iHub-Data, IIIT Hyderabad.",
                     "Previously served as a Winter Research Intern at IIIT Hyderabad, engineering advanced computer vision systems.",
                     "Advances materials science and deep learning innovations as an AI Research Intern at Crystal Paradigm, developing inverse design frameworks to computationally engineer next-generation superalloys.",
                     "Co-authored research introducing a breakthrough Attention Graph Siamese Transformer (DPT-GNN) that drastically optimizes lithium-ion battery capacity predictions."], font_size=12)
    add_rounded_box(s17, Inches(6.8), Inches(1.8), Inches(6), Inches(4.0), "K. Indrasena Reddy [Indra] (AI Research Intern)", 
                    ["CSE student at NGIT. Previously served as an AI Developer Intern at Viswam.AI, building natural language processing applications and contributing to experimental language model research.",
                     "Currently advances materials informatics and graph neural network modeling for large-scale property prediction as an AI Research Intern at Crystal Paradigm."], font_size=12)
    add_rounded_box(s17, Inches(0.5), Inches(6.0), Inches(12.33), Inches(1.0), "Strategic Scale Capability", 
                    ["The Extended Crystal Paradigm Engineering Team: The core architecture is rapidly scaled and supported by a dedicated extended team of 18 specialized AI Research Interns, ensuring massive parallel execution bandwidth for complex multi-physics simulations."], bg_color=ELECTRIC_BLUE)

    # --- SLIDE 18 ---
    s18 = create_base_slide(prs, "CRYSTAL PARADIGM", "Accelerating Deep-Tech Materials from 5 Years to 4 Weeks.")
    add_rounded_box(s18, Inches(2.0), Inches(2.0), Inches(9.33), Inches(2.5), None, 
                    ["We have completely solved the computational bottleneck.",
                     "We are ready to build the physical reality.",
                     "",
                     "Join us at the SCIDIP Advanced Materials Track."], font_size=18)
    add_rounded_box(s18, Inches(2.0), Inches(4.8), Inches(9.33), Inches(1.0), "crystalparadigm.in | khub.crystalparadigm@gmail.com", 
                    ["Scan QR Code to access the 50+ Page Technical Appendix"], bg_color=ELECTRIC_BLUE)
    add_placeholder_frame(s18, Inches(5.66), Inches(5.9), Inches(2.0), Inches(1.5), "QR CODE")

    prs.save("CrystalParadigm_Elite_Deck_FINAL.pptx")
    print("SUCCESS: 18-Slide Elite Deck generated as CrystalParadigm_Elite_Deck_FINAL.pptx")

if __name__ == '__main__':
    build_slides()
