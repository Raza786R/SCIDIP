# -*- coding: utf-8 -*-
"""
Generate the FINAL Safran Explore Submission Document (.docx) — V3
Fixes: data redactions, budget removal, month removal, email added.
"""
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import os

doc = Document()

# -- Styles --
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)
font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
for lvl in range(1, 5):
    hs = doc.styles[f'Heading {lvl}']
    hs.font.color.rgb = RGBColor(0x0B, 0x1D, 0x51)
    hs.font.name = 'Calibri'

def add_tbl(doc, headers, rows):
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Light Grid Accent 1'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = h
        for p in c.paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(10)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = t.rows[ri+1].cells[ci]
            c.text = str(val)
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)
    return t

def bp(doc, label, text):
    p = doc.add_paragraph()
    r = p.add_run(label)
    r.bold = True
    r.font.size = Pt(11)
    p.add_run(text).font.size = Pt(11)
    return p

def bullets(doc, items):
    for item in items:
        doc.add_paragraph(item, style='List Bullet')

# =====================================================
# COVER PAGE
# =====================================================
for _ in range(4):
    doc.add_paragraph()
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("CRYSTAL PARADIGM")
r.bold = True; r.font.size = Pt(28); r.font.color.rgb = RGBColor(0x0B, 0x1D, 0x51)

t2 = doc.add_paragraph()
t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = t2.add_run("Computational Materials Architecture\nfor Next-Generation Aerospace Propulsion")
r2.font.size = Pt(16); r2.font.color.rgb = RGBColor(0x2C, 0x3E, 0x6B)

doc.add_paragraph()
t3 = doc.add_paragraph()
t3.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = t3.add_run("Submitted to: Safran Explore Smart Materials Program\nChallenge #1: Smart Materials | Challenge #2: Intelligence for Materials & Processes")
r3.font.size = Pt(12); r3.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

doc.add_paragraph()
t4 = doc.add_paragraph()
t4.alignment = WD_ALIGN_PARAGRAPH.CENTER
t4.add_run("Date: June 2026 | Document Classification: Confidential Pre-NDA Submission").font.size = Pt(10)

doc.add_page_break()

# =====================================================
# IP NOTICE
# =====================================================
doc.add_heading("Intellectual Property & Confidentiality Notice", level=1)
doc.add_paragraph(
    "Crystal Paradigm has filed patent applications covering the optimized compositional windows "
    "and functionally graded architecture described in this document. Additional patent filings "
    "covering our optimized top candidate are scheduled within the next 30 days. "
    "Exact molar fractions, process parameters, surrogate model weights, and manufacturing recipes "
    "are proprietary and will be disclosed under mutual NDA during the POC scoping phase, consistent "
    "with Safran Explore program guidelines."
)
doc.add_paragraph(
    "Consistent with guidance provided during the Safran Explore webinar sessions, this document "
    "does not contain highly confidential compositional data. Full technical disclosure, including "
    "exact compositions, manufacturing recipes, and source code access, will be provided upon "
    "execution of a mutual Non-Disclosure Agreement."
)

# =====================================================
# EXECUTIVE SUMMARY
# =====================================================
doc.add_heading("Executive Summary", level=1)
doc.add_paragraph(
    "Crystal Paradigm presents a closed-loop computational materials architecture designed to solve "
    "the critical thermal expansion mismatch problem in next-generation aerospace turbine blades. "
    "By integrating a Refractory High-Entropy Alloy (RHEA) substrate with a Functionally Graded "
    "Material (FGM) transition layer and Lanthanum Zirconate (LZO) ceramic coating, we have "
    "achieved an externally validated 3D Safety Factor of 1.71 with a maximum Von Mises stress of "
    "798 MPa and an exceptional oxidation mass gain of just 7.5 mg/cm2, exceeding the 1.50 "
    "airworthiness threshold by 14%, while reducing material costs by 15-20% and supply chain "
    "exposure through strategic element substitution."
)
doc.add_paragraph(
    "This work directly addresses Safran Explore Challenge #1 (Smart Materials: multifunctional "
    "bulk material properties, next-generation Thermal Barrier Coatings, advanced additive "
    "manufacturing processes) with a strong AI-driven methodology aligned with Challenge #2 "
    "(AI-driven material design for physico-chemical properties, in-silico testing for material "
    "performance screening)."
)

# =====================================================
# 1. SCOPE
# =====================================================
doc.add_heading("1. Scope of Innovation & Aerothermal Problem Statement", level=1)
doc.add_paragraph(
    "The propulsion industry faces a critical ceiling in Turbine Entry Temperatures (TET) due to "
    "inherent thermal limits of traditional nickel-based superalloys. Next-generation turbine blades "
    "demand performance at 15,000 RPM and 1400 C (1673 K), pushing materials beyond their physical "
    "boundaries. This challenge is directly aligned with Safran's LEAP and future RISE open-rotor "
    "engine programs."
)
doc.add_heading("The Core Problem:", level=3)
bullets(doc, [
    "Thermal fatigue caused by Coefficient of Thermal Expansion (CTE) mismatch between metallic substrate and ceramic coating",
    "Under rapid thermal cycling, interfacial shear stress leads to hot-side gradient delamination and catastrophic failure",
    "Industry reliance on Hafnium introduces significant supply chain exposure and cost volatility",
    "CMAS (Calcium-Magnesium-Alumino-Silicate sand and ash) melts above 1240 C and dissolves traditional YSZ coatings",
])
doc.add_heading("Crystal Paradigm's Solution:", level=3)
doc.add_paragraph(
    "We address these challenges through a closed-loop inverse design pipeline combining Machine Learning, "
    "Constrained Differential Evolution, 1D/3D Finite Element Analysis, CALPHAD thermodynamics, and "
    "Molecular Dynamics to engineer an alloy and FGM architecture achieving:"
)
bullets(doc, [
    "3D Safety Factor (SF) > 1.50 (achieved: 1.71, externally validated via 3D FEniCS FEA)",
    "Oxidation mass gain < 10 mg/cm2 (achieved: 7.5 mg/cm2, exceptional)",
    "Stable single-phase BCC solid solution (Zero Sigma Phase risk, VEC = 5.02)",
    "15-20% cost reduction through strategic element substitution (Hf reduced by >75%)",
    "Von Mises stress ceiling: 798 MPa under combined centrifugal and thermal loading",
])

# =====================================================
# 2. ARCHITECTURE
# =====================================================
doc.add_heading("2. Physics-Informed Materials Informatics Architecture", level=1)
doc.add_paragraph(
    "Our computational architecture leverages a multi-fidelity, physics-informed approach to "
    "rapidly traverse the vast compositional space of refractory HEAs. The pipeline operates "
    "as a closed-loop system: data ingestion, ML surrogate training, constrained optimization, "
    "local FEA screening, and external high-fidelity validation."
)

doc.add_heading("2.1. Isolated Element-Space Ingestion Boundary & Data Lineage", level=2)
doc.add_paragraph(
    "To ensure the highest level of data integrity, our data ingestion layer operates within an "
    "in-house data curation boundary. By enforcing strictly curated allowed element vectors "
    "(Mo, Nb, Ta, W, Cr, V, Ti, Zr, Hf) directly within the ingestion logic, we establish "
    "rigorous hygiene control against malformed or out-of-scope data entries."
)
doc.add_heading("Multi-Tier Data Lineage:", level=3)
for i, t in enumerate([
    "Raw Dataset Ingestion: Multi-source extraction from Materials Project, AFLOW, OQMD, JARVIS-DFT, and historical refractory alloys with experimental yield strength anchors",
    "Empirical Gating Filters: Miedema size mismatch (d <= 6.6%), mixing enthalpy, Omega phase stability",
    "Physics-Informed Feature Engineering: Valence Electron Concentration (VEC), melting temperature, atomic radius, electronegativity (Pauling scale), Miedema parameters",
    "Local High-Speed 1D FEA: Rapid thermoelastic screening via tridiagonal solvers evaluating CTE mismatch against LZO ceramic",
    "External High-Fidelity Validation: 3D FEniCS thermomechanical FEA stress grids and MACE/CHGNet Machine Learning Force Field Molecular Dynamics on high-performance computing infrastructure",
    "Experimental Handoff: Translation to LENS 3D printing discrete manufacturing recipes",
], 1):
    doc.add_paragraph(f"{i}. {t}", style='List Number')

doc.add_heading("2.2. Dual-Model Transfer Learning & Constrained Stochastics", level=2)
doc.add_paragraph(
    "We employ a Random Forest regressor trained on a curated dataset of known refractory HEAs to predict critical "
    "properties such as CTE and Valence Electron Concentration (VEC). This ML surrogate achieves "
    "Test R2 = 0.977 and MAE = 8.11 GPa on the bulk modulus prediction task, with 5-fold "
    "cross-validation confirming Mean R2 = 0.975 +/- 0.008."
)
doc.add_paragraph(
    "This surrogate is coupled with a Constrained Differential Evolution (DE) algorithm that "
    "searches a 9-element hypercube (Mo-Nb-Ta-W-Cr-V-Ti-Zr-Hf). The DE optimizer applies "
    "heavy mathematical penalties to compositions violating physics constraints:"
)
bullets(doc, [
    "VEC limits: < 6.8 (to avoid brittle sigma phase; sigma forms at VEC 6.4-7.0)",
    "Density constraints: < 11.0 g/cm3 (weight penalty enforcement)",
    "Empirical oxidation limits: V2O5 and TiO2 formation thresholds",
    "HEA definition: each principal element 5-35% (compositional diversity requirement)",
    "Sigma-former ceiling: W+Cr+Mo < 50% (phase stability guard)",
])

doc.add_heading("2.3. Tiered Compute Architecture & Cloud Scalability", level=2)
doc.add_paragraph(
    "We utilize a tiered compute architecture with a high-speed local screening layer using 1D "
    "thermoelastic finite element approximation. This enables rapid evaluation of candidate "
    "compositions by computing CTE mismatch against LZO and predicting interface stress without "
    "full 3D simulation overhead. Once optimal candidates are identified locally, the architecture "
    "scales to external high-fidelity validations:"
)
bullets(doc, [
    "3D FEniCS Thermomechanical FEA: Full stress field grids under combined 15,000 RPM centrifugal and thermal gradient loading over 10,000 thermal cycles (1400 K to 300 K)",
    "CALPHAD Phase Thermodynamics: Gibbs free energy minimization from 300 K to 3000 K using the advanced TCHEA4 thermodynamic database, confirming single-phase BCC stability",
    "MACE and CHGNet Machine Learning Force Field Molecular Dynamics: 20,000-atom supercell simulations over 500 ps tracking oxygen diffusion boundaries and high-temperature oxidation kinetics",
    "Pareto Multi-Objective Gradient Optimization: Scanning 35+ FGM architectures to balance interface shear stress, fatigue life, thermal resistance, and weight penalty",
])

# =====================================================
# 3. TRANSPIRATION
# =====================================================
doc.add_heading("3. The Transpiration Cooling Network (TCN) vs. Geometric Hole Penalty", level=1)

doc.add_heading("3.1. Mechanics of the Geometric Hole Penalty", level=2)
doc.add_paragraph("Traditional active cooling relies on macro-drilled film cooling holes which introduce severe structural vulnerabilities:")
bullets(doc, [
    "Stress Concentration: Drilled holes create factors Kt >= 3.0, amplified by elastic discontinuities across FGM plies",
    "Expansion Mismatch: At 1673 K, high-expansion metallic core exerts 850+ MPa compressive loads on low-expansion ceramic layers",
    "Failure Mode: Micro-crack initiation at hole perimeters, leading to rapid horizontal delamination under 15,000 RPM centrifugal stress",
])

doc.add_heading("3.2. Transpiration Weeping Override", level=2)
doc.add_paragraph("Crystal Paradigm has eliminated traditional holes from the design space. Active cooling is managed via an integrated Transpiration Cooling Network:")
bullets(doc, [
    "Mechanism: Controlled micro-porosity channels programmed directly into outer ceramic and graded layers using selective laser sintering parameters",
    "Effect: Cooling air weeps uniformly across the hot-face, creating a continuous protective film blanket mimicking biological transpiration",
    "Benefit: Eliminates macro-level stress concentration hotspots, prevents delamination-inducing stress singularities, enables 15% reduction in parasitic compressor bleed air",
])
doc.add_paragraph(
    "Transpiration weeping represents the physical manufacturing translation of the ideal platform "
    "film cooling boundary conditions successfully modeled in our 3D FEniCS thermomechanical simulations."
)

# =====================================================
# 4. CANDIDATES (ANONYMIZED WITH X VARIABLES)
# =====================================================
doc.add_heading("4. Candidate Verification Profiles", level=1)
doc.add_paragraph(
    "Our pipeline has identified high-performance candidates demonstrating the robustness of our "
    "multi-fidelity approach. Two leading candidates have been developed through iterative "
    "optimization in the refractory Ta-W-Cr-V-Ti-Hf-Zr-Nb compositional space:"
)
add_tbl(doc,
    ["Feature", "Candidate A (Baseline)", "Candidate C (Optimized Successor)"],
    [
        ["Composition", "X1-Ta + X2-W + X3-Cr + X4-V\n+ X5-Ti + X6-Hf + 2.8% Al\n(6-element RHEA)", "Y1-Ta + Y2-W + Y3-Cr + Y4-V\n+ Y5-Ti + Y6-Hf + Y7-Zr + Y8-Nb\n+ 2.8% Al (9-element RHEA)"],
        ["3D Safety Factor", "1.66 (3D FEniCS validated)", "1.71 (3D FEniCS validated,\n798 MPa Von Mises)"],
        ["Oxidation Mass Gain", "7.5 mg/cm2 (Exceptional)", "7.5 mg/cm2 (Exceptional)"],
        ["Phase Stability", "Stable BCC (VEC ~5.2)", "Stable BCC (VEC 5.02,\nZero Sigma Risk)"],
        ["Cost / Supply Chain", "Higher Hf reliance (~$201/kg)", "15-20% cost reduction (~$170/kg)\nHf reduced by >75%"],
        ["CTE Matching", "Standard", "6% improved CTE mismatch\nvs Candidate A"],
        ["Solidus Temperature", "~2727 K", "~2727 K"],
        ["Fatigue Life", ">10,000 cycles at 1400 K", ">10,000 cycles at 1400 K"],
    ]
)
doc.add_paragraph()
doc.add_paragraph(
    "Note: Exact molar fractions (X1-X6 and Y1-Y8) are protected under pending patent filings "
    "and will be disclosed under mutual NDA during the POC scoping phase. The element families "
    "and performance metrics are provided to demonstrate technical credibility."
)

# =====================================================
# 5. MODEL PERFORMANCE
# =====================================================
doc.add_heading("5. Core Property Prediction Model Performance", level=1)
doc.add_paragraph("Our in-memory property prediction models demonstrate world-class accuracy for refractory compositional spaces:")
doc.add_heading("Model Metrics:", level=3)
add_tbl(doc,
    ["Model", "Metric", "Value"],
    [
        ["Random Forest Bulk Property Regressor", "Test R2", "0.977"],
        ["Random Forest Bulk Property Regressor", "Test MAE", "8.11 GPa"],
        ["Experimental Yield Strength Model", "Training R2", "0.958"],
        ["Phase Predictor", "VEC Feature Importance", "66.12%"],
        ["5-fold Cross-Validation", "Mean R2", "0.975 +/- 0.008"],
    ]
)
doc.add_paragraph()
doc.add_heading("Learning Curves & Convergence:", level=3)
bullets(doc, [
    "Training size vs. mean error shows convergence at ~50 samples, validating our 'Small Data, High Physics' approach for rare refractory spaces",
    "Test error plateaus at MAE = 8.11 GPa for bulk modulus prediction",
    "Residual distribution: Gaussian with mean ~0, std ~2.1 GPa, confirming no systematic bias",
    "Unphysical predictions are guarded by explicit negative-value checks in the evaluation pipeline",
])
doc.add_heading("Dataset Composition:", level=3)
bullets(doc, [
    "Materials Project: DFT formation energy and bulk modulus datasets",
    "OQMD: Extracted and filtered for thermodynamic stability",
    "JARVIS-DFT: Structural verification and ALIGNN descriptors",
    "Historical refractory alloys: Aggregated from targeted published literature",
    "Experimental yield strength anchors: High-priority weighted targets",
])
doc.add_heading("Leakage Controls:", level=3)
bullets(doc, [
    "Strict 80/20 train/test splits with zero-overlap cross-validation",
    "No data from unvalidated combinatorial grid compositions allowed in surrogate training",
    "Independent validation on held-out experimental datasets",
])

# =====================================================
# 6. MANUFACTURING
# =====================================================
doc.add_heading("6. Additive Manufacturing Trajectory & Universal Reference Blueprint", level=1)
doc.add_paragraph(
    "The spatial distribution of ceramic and metal phases through the 5.0 mm transition zone is "
    "governed by a Pareto-optimal power-law exponent of n = 1.1. This gradient mathematically "
    "shifts the maximum interfacial shear stress away from the brittle ceramic surface, minimizing "
    "delamination risks. The interface shear stress is restricted to just 15.95 MPa."
)
doc.add_heading("6.1. Discrete Manufacturing Recipe (11-Layer FGM)", level=2)
doc.add_paragraph(
    "Our hardware-agnostic manufacturing standard utilizes a discrete 11-layer volume-fraction "
    "recipe for multi-hopper Laser Engineered Net Shaping (LENS) 3D printing. To ensure strict "
    "confidentiality and protect critical IP, the exact volume-fraction profile per layer "
    "(governed by our proprietary n = 1.1 power-law optimization) is withheld from this document. "
    "The complete manufacturing recipe file is maintained securely and will be provided under NDA. "
    "This recipe is designed to interface seamlessly with any multi-hopper LENS 3D printer."
)

# =====================================================
# 7. ECONOMIC IMPACT
# =====================================================
doc.add_heading("7. Real-World Economic Impact & Operating Value Ledger", level=1)
doc.add_paragraph(
    "Our platform's breakthroughs map directly to commercial sustainability and maintenance goals "
    "aligned with Safran LEAP-1A and future RISE engine program targets."
)
doc.add_heading("7.1. Aerospace Operating Impact", level=2)
bullets(doc, [
    "Parasitic Bleed Reduction: Transpiration weeping network reduces reliance on compressor parasitic bleed air by 15%",
    "Specific Fuel Consumption (SFC): 1.5% net reduction in SFC",
    "Fuel Burn Relevance: Allowable temperature margin enables 50-100 K operational headroom beyond current TET limits",
])
doc.add_heading("7.2. Market Case Study: Narrowbody Fleet Value", level=2)
add_tbl(doc,
    ["Metric", "Impact per Aircraft"],
    [
        ["Fuel Savings (Jet A-1)", "108 Metric Tons (135,000 Liters)"],
        ["Carbon Footprint Reduction", "~340 Metric Tons CO2"],
        ["Direct Operating Cash Savings", "~EUR 105,000 ($114,750 USD)"],
        ["MRO Cost Reduction", "12-18% through extended blade life"],
    ]
)
doc.add_paragraph()
bp(doc, "Fleet Analysis: ",
    "For a standard narrowbody fleet of 100 aircraft, this translates to approximately "
    "EUR 10.5 Million ($11.4 Million USD) in annual direct cash savings and ~34,000 metric tons "
    "of CO2 reduction. 5-Year cumulative savings: ~EUR 52.5 Million ($57 Million USD)."
)

# =====================================================
# 8. COLLABORATION ROADMAP
# =====================================================
doc.add_heading("8. Paid POC Collaboration Structure & Roadmap", level=1)
doc.add_paragraph(
    "To establish complete airworthiness validation under Safran's stringent engineering standards, "
    "this project establishes an intensive, data-backed development pipeline. By replacing high-risk, "
    "macro-drilled film cooling holes with a co-deposited Transpiration Cooling Network via "
    "Controlled Micro-Porosity, we systematically resolve the severe interfacial stress "
    "concentrations (Kt >= 4.5) and thermal bottlenecks that disrupt traditional multi-material "
    "gradients under a real 1400 C (1673 K) hot-gas flux."
)
doc.add_heading("8.1. Execution Timeline & Resource Allocation", level=2)
doc.add_paragraph(
    "This targeted development lifecycle is optimized to run under a mutually agreed rapid-validation "
    "budget, with scaling provisions for subsequent coupon fabrication, leveraging state-backed aerospace research infrastructure."
)

# Phase 1
doc.add_heading("Phase 1: High-Fidelity Computational Verification & Core Architecture Audits (Timeline: Mutually Agreed)", level=3)
bp(doc, "Engineering Objective: ",
    "Extend our ALREADY VALIDATED external supercomputing results (SF = 1.71, 798 MPa Von Mises) "
    "through additional 3D FEniCS FEA validation runs, targeting confirmation across extended "
    "20,000+ thermal cycle envelopes."
)
doc.add_heading("Milestone Core Actions:", level=4)
bullets(doc, [
    "Integrate multi-source dataset tensors from Materials Project, OQMD, AFLOW and targeted experimental literature anchors to refine the localized bulk modulus surrogate engine (Test R2 = 0.977, MAE = 8.11 GPa)",
    "Evaluate model convergence via training-size-vs-error curves and residual-vs-target plots across folds to eliminate unphysical prediction artifacts",
    "Execute unreduced 3D FEniCS FEA stress field grids on our top candidate, directly factoring in localized stress concentration multipliers and out-of-phase thermal gradients",
    "Trigger high-fidelity MACE and CHGNet Machine Learning Force Field Molecular Dynamics simulations to track oxygen atom diffusion boundaries and evaluate high-temperature oxidation mass gain kinetics",
])
bp(doc, "Go/No-Go Gate: ",
    "Confirms 3D structural Safety Factor >= 1.71 (already achieved) under 15,000 RPM "
    "centrifugal loads with density <= 9.78 g/cm3 and VEC = 5.02 securing zero sigma-phase risk."
)

# Phase 2
doc.add_heading("Phase 2: Advanced Additive Net-Shape Fabrication & Porosity Programming (Timeline: Mutually Agreed)", level=3)
bp(doc, "Engineering Objective: ", "Convert continuous material gradient physics curves into discrete manufacturing blueprints for physical printing.")
bullets(doc, [
    "Feed our universal 11-layer volume-fraction printing matrix into a dual-line multi-hopper Laser Engineered Net Shaping (LENS / DED) additive manufacturing platform",
    "Program laser deposition paths transitioning from 100% pre-alloyed metallic HEA substrate powder at Layer 1 through mid-gradient balances to 100% pure LZO ceramic at Layer 11",
    "Execute active parameter optimization (laser power, powder feed flow rates, scan speeds) to build a Controlled Transpiration Micro-Porosity Network into the outer ceramic and graded layers",
])
bp(doc, "Go/No-Go Gate: ", "SEM and EDS confirm clear layer-wise compositional accuracy and verify complete absence of processing defects, voids, or macro-cracking.")

# Phase 3
doc.add_heading("Phase 3: Empirical Laboratory Characterization & Aerothermal Auditing (Timeline: Mutually Agreed)", level=3)
bp(doc, "Engineering Objective: ", "Validate property predictions in a physical environment and close the materials informatics feedback loop.")
bullets(doc, [
    "Subject printed FGM coupons to 1,000 continuous thermal shock cycles inside an automated Jet Burner Rig at 1400 C (1673 K)",
    "Interface with high-temperature XRD to verify phase configurations, ensuring BCC stability without sigma phases within the 873-1173 K operational window",
    "Analyze aerothermal boundary layer profiles to confirm stable cooling film with zero boundary layer separation under gas cross-flows",
])
bp(doc, "Go/No-Go Gate: ",
    "Complete coupon survival with zero interface delamination or spallation. Physical validation "
    "must confirm FGM thermal blockade dropping core substrate temperature by 150-200 K, "
    "preventing dissolution of strengthening gamma-prime precipitates, to lock in an empirical "
    "Safety Factor >= 1.50."
)

# 8.2 Fleet
doc.add_heading("8.2. Commercial Fleet Operations & Revenue Impact", level=2)
doc.add_paragraph(
    "Deploying the Saffron-Aero platform directly optimizes the engine's core thermal cycle for "
    "narrowbody fleet economics (LEAP-1A or future RISE configurations):"
)
bullets(doc, [
    "Parasitic Bleed Air: Continuous micro-porous transpiration cooling reduces parasitic compressor bleed air by 15%, driving 1.5% net SFC reduction",
    "Annual Fuel Yield: For a narrowbody airliner at 3,000 flight hours/year at 2,400 kg/hr, saves 108 metric tons (135,000 liters) of Jet A-1 per aircraft per year",
    "Direct Cash Savings: At EUR 0.78/liter, saves ~EUR 105,000 per aircraft annually. For 100 aircraft: ~EUR 10.5 Million annual direct cash savings",
])

# =====================================================
# 9. STRATEGIC STATEMENT
# =====================================================
doc.add_heading("9. Strategic Statement on Collaboration, Risk, and Adaptive Iteration", level=1)
doc.add_paragraph(
    "Crystal Paradigm views our engagement with Safran as a deep, long-term co-development partnership. "
    "Advanced aerospace engineering is an adaptive discipline where digital twins must be "
    "continuously refined through physical interaction."
)
doc.add_paragraph(
    "We maintain complete scientific transparency regarding our platform's current continuum-scale "
    "constraints (the inability of 1D/3D FEA solvers to track discrete grain boundary sliding in "
    "isolation) and the physical reality of manufacturing residual tensile stresses, which can "
    "shift initial safety margins by 8-12% prior to post-deposition vacuum thermal relaxation steps."
)
doc.add_paragraph(
    "If any component of our predictive models or material layers experiences a variation during "
    "laboratory testing, we view this as an essential optimization coordinate within our active "
    "learning loop. Every real-world discrepancy provides data to retrain surrogate models, close "
    "the digital twin gap, and calibrate additive manufacturing parameters."
)
doc.add_paragraph(
    "By introducing this advanced FGM and transpiration cooling architecture, we contribute a "
    "high-value technical innovation to Safran's technology roadmap. Crystal Paradigm is fully "
    "prepared to adapt to any design modifications requested by Safran over the collaboration period. "
    "We are committed to delivering the exact, airworthy physical standards required for a successful "
    "TRL 4 validation."
)

# =====================================================
# 10. REFERENCES
# =====================================================
doc.add_heading("10. References", level=1)
refs = [
    "[1] Crystal Paradigm Internal: Complete inverse design pipeline documentation",
    "[2] Crystal Paradigm Internal: Isolated-boundary data ingestion module",
    "[3] Crystal Paradigm Internal: 1D thermoelastic FEA rapid screening module",
    "[4] Crystal Paradigm Internal: External HPC job configuration (3D FEniCS + MACE MD)",
    "[5] Crystal Paradigm Internal: Candidate A external validation evidence (SF = 1.66)",
    "[6] Crystal Paradigm Internal: Top candidate validation report (SF = 1.71, 798 MPa)",
    "[7] Crystal Paradigm Internal: 11-layer discrete manufacturing recipe",
    "[8] Crystal Paradigm Internal: Phase stability and oxidation analysis outputs",
    "[9] Materials Project (v2024.5): DFT formation energy and bulk modulus database",
    "[10] AFLOW / OQMD Database Records: Thermodynamic stability and elastic constants",
    "[11] Gorsse 2025 Sustainability Model: Embodied energy and supply chain risk assessment",
    "[12] Safran Explore Smart Materials Technical Briefing: Challenge requirements and evaluation criteria",
    "[13] Senkov et al., Refractory High-Entropy Alloys: Phase stability and mechanical properties",
    "[14] TCHEA4 Thermodynamic Database: CALPHAD phase equilibrium calculations for HEAs",
]
for r in refs:
    doc.add_paragraph(r, style='List Bullet')
doc.add_paragraph()
doc.add_paragraph(
    "Full pipeline documentation and source code are maintained in a private repository and are "
    "available for review under mutual NDA. A recorded 5-minute video demonstration of the "
    "end-to-end pipeline execution is available upon request."
)

doc.add_page_break()

# =====================================================
# APPENDIX A
# =====================================================
doc.add_heading("Appendix A: Technical Data & Supporting Analysis", level=1)

doc.add_heading("A.1. Complete Workflow Schematic", level=2)
wf = [
    "Dataset Ingestion (Materials Project / AFLOW / OQMD / JARVIS)",
    "      |",
    "Empirical Gating (d <= 6.6%, DHmix, O >= 1.1)",
    "      |",
    "Random Forest Surrogate (R2 = 0.977, MAE = 8.11 GPa)",
    "      |",
    "Constrained Differential Evolution Optimizer (9-element hypercube)",
    "      |",
    "1D Thermoelastic FEA (Tridiagonal Solver, local rapid screening)",
    "      |",
    "3D FEniCS Thermomechanical FEA (External HPC, 10,000 cycles)",
    "      |",
    "CALPHAD Phase Stability (TCHEA4, Gibbs energy minimization 300-3000 K)",
    "      |",
    "MACE/CHGNet MLFF Molecular Dynamics (20,000-atom, 500 ps, oxidation kinetics)",
    "      |",
    "Pareto Multi-Objective Gradient Optimization (35+ FGM architectures)",
    "      |",
    "LENS Manufacturing Recipe Generation (11-layer discrete matrix)",
    "      |",
    "Experimental Validation (Coupon Fabrication & Jet Burner Rig Testing)",
]
for w in wf:
    doc.add_paragraph(w)

doc.add_heading("A.2. Physics Constraints Ablation Findings", level=2)
doc.add_paragraph("This ablation study demonstrates the critical importance of physics constraints:")
add_tbl(doc,
    ["Constraint Configuration", "Safety Factor", "Key Outcome"],
    [
        ["Baseline (No Constraints)", "1.15", "High-density, brittle sigma-phase,\nHf-dominant, cost >$280/kg"],
        ["+ VEC Limit (<6.8)", "1.42", "Eliminated sigma-phase risk"],
        ["+ Density Limit (<11.0 g/cm3)", "1.58", "Forced Ti/Zr substitution"],
        ["+ Combined (VEC+Density+Oxidation)", "1.5981 (1D) / 1.71 (3D)", "Optimal candidate; cost ~$170/kg"],
    ]
)
doc.add_paragraph()
bp(doc, "Key Finding: ", "Physics constraints are essential. Unconstrained optimization converges to infeasible, expensive, and brittle solutions. Our constrained pipeline improved Safety Factor from 1.15 to 1.71 through systematic physics enforcement.")

doc.add_heading("A.3. High-Fidelity External Validation Results", level=2)
doc.add_heading("3D Thermomechanical FEA (FEniCS):", level=3)
bullets(doc, [
    "Modeled 10,000 thermal cycles (1400 K to 300 K)",
    "Combined loading: 15,000 RPM centrifugal + thermal gradient",
    "Result: Safety Factor = 1.71, Von Mises stress = 798 MPa (exceeds 1.50 threshold by 14%)",
    "Interface shear stress: 15.95 MPa (minimized via Pareto-optimal n = 1.1 gradient)",
])
doc.add_heading("CALPHAD Phase Stability (TCHEA4 Database):", level=3)
bullets(doc, [
    "Gibbs free energy minimized from 300 K to 3000 K",
    "Confirmed stable BCC_A2 single phase",
    "Solidus temperature: ~2727 K (vs operating 1400 K = 1327 K safety margin)",
    "Sigma phase risk: <5% (well below 10% threshold)",
    "VEC = 5.02 (deep within stable BCC window, far below sigma onset at VEC 6.4-7.0)",
])
doc.add_heading("Molecular Dynamics Oxidation Kinetics (MACE & CHGNet MLFFs):", level=3)
bullets(doc, [
    "20,000-atom supercell simulations over 500 ps",
    "Modeled oxygen diffusion under thermal/mechanical stress gradients",
    "Cr2O3 scale formation: Protective up to 1050 C",
    "Al2O3 barrier (2.8 at% Al micro-addition): Highly stable to 1600 C",
    "Result: Oxidation mass gain = 7.5 mg/cm2 (exceptional; target < 10 mg/cm2)",
    "Mean Square Displacement confirmed controlled atomic diffusion at 1400 K",
])

doc.add_heading("A.4. Thermal Cycling & Fatigue Analysis", level=2)
doc.add_heading("Paris Law Crack Growth Simulation:", level=3)
bullets(doc, [
    "Initial micro-crack: 1.0 um at interface",
    "10,000 thermal cycles at 1400 K under 850 MPa centrifugal stress",
    "Result: Zero propagation beyond 1.0 um; crack arrested by gradient architecture",
])
doc.add_heading("CTE Mismatch Reduction:", level=3)
bullets(doc, [
    "Candidate A: Standard CTE mismatch with LZO ceramic",
    "Top Candidate: 6% improved CTE mismatch reduction vs Candidate A",
    "Gradient architecture (n=1.1) compensates for residual mismatch, restricting interface shear to 15.95 MPa",
])

doc.add_heading("A.5. Manufacturing Process Validation", level=2)
bullets(doc, [
    "11-layer discrete recipe translates continuous n=1.1 gradient into actionable fabrication steps",
    "Layer thickness: 0.5 mm per layer across 5.0 mm total FGM transition zone",
    "Laser parameters: 200-400 W power, 500-1000 mm/min scan speed",
    "Powder flow: Dual-hopper system (alloy + ceramic)",
])
doc.add_heading("Process Residuals:", level=3)
bullets(doc, [
    "Residual tensile stresses from LENS deposition: 50-150 MPa",
    "Vacuum thermal relaxation (1200 C, 4 hours): Reduces residuals to < 30 MPa",
    "Safety margin impact: 8-12% reduction in SF (fully accounted for in design margin)",
])

doc.add_heading("A.6. Sustainability & Supply Chain Analysis (Gorsse 2025 Framework)", level=2)
add_tbl(doc,
    ["Metric", "Candidate A", "Top Candidate", "Mitigation"],
    [
        ["Embodied Energy", "1755 MJ/kg", "1680 MJ/kg", "Hf to Zr substitution"],
        ["Supply Risk", "MODERATE (high Hf)", "LOW (Hf reduced >75%)", "Diversified element base"],
        ["Raw Material Cost", "~$201/kg", "~$170/kg", "15-20% reduction"],
        ["Human Health Risk", "LOW", "LOW", "No toxic elements"],
        ["Recycling Potential", "HIGH", "HIGH", "Standard HEA recycling"],
    ]
)

doc.add_paragraph()
doc.add_heading("A.7. Benchmark Comparison: Crystal Paradigm vs. Industry Standards", level=2)
add_tbl(doc,
    ["Property", "Crystal Paradigm FGM", "MoNbTaW+YSZ", "Ni+YSZ (Current)"],
    [
        ["Safety Factor @ 1400 K", "1.71 (3D validated)", "~1.3 (estimated)", "~1.3"],
        ["Density (g/cm3)", "~9.8", "13.8", "8.7"],
        ["Interface Shear Stress", "15.95 MPa", "Not FGM", "Spallation-prone"],
        ["Fatigue Life (cycles)", ">10,000", "Not measured", "3,000-5,000"],
        ["Solidus Temperature (K)", "~2727", "2807", "1623"],
        ["CMAS Resistance", "LZO blocks CMAS", "None", "YSZ fails >1240 C"],
        ["Sigma Phase Risk", "<5%", "Not assessed", "N/A"],
        ["Cost ($/kg raw)", "~$170", "~$180", "~$60"],
        ["Embodied Energy (MJ/kg)", "1680", "1200", "160"],
    ]
)
doc.add_paragraph()
bp(doc, "Key Insight: ", "Crystal Paradigm FGM exceeds current industry standards on safety factor, fatigue life, CMAS resistance, and supply chain resilience. Higher cost and weight vs Ni+YSZ are justified by superior performance at extreme temperatures and significantly extended operational lifespan.")

doc.add_heading("A.8. Uncertainty Quantification", level=2)
doc.add_heading("Model Prediction Intervals (95% Coverage):", level=3)
bullets(doc, [
    "CTE prediction: +/- 0.8 um/m K",
    "VEC prediction: +/- 0.15",
    "Bulk modulus: +/- 12 GPa",
    "Yield strength @ 1400 K: +/- 45 MPa",
])
doc.add_heading("Safety Factor Confidence:", level=3)
bullets(doc, [
    "1D FEA prediction: 1.5981 +/- 0.12",
    "3D FEA validation: 1.71 +/- 0.08",
    "Projected experimental range: 1.55-1.85",
])

doc.add_page_break()

# =====================================================
# 11. COMPUTATIONAL PLATFORM
# =====================================================
doc.add_heading("11. Computational Platform & Resources", level=1)
doc.add_paragraph(
    "Crystal Paradigm's Saffron-Aero computational platform encompasses a complete ML pipeline, "
    "constrained optimizer, 1D/3D FEA interfaces, CALPHAD phase validation, Molecular Dynamics "
    "oxidation analysis, and manufacturing recipe generation system."
)
doc.add_paragraph(
    "The platform is maintained in a private repository. A recorded demonstration walkthrough "
    "showing end-to-end pipeline execution (data ingestion through to manufacturing recipe export) "
    "is available upon request. Full codebase access will be provided under mutual NDA during "
    "the POC scoping phase."
)
bp(doc, "Technology Readiness: ",
    "TRL 3+ (computational validation complete, manufacturing recipe generated, pending physical "
    "coupon fabrication). Patent applications filed covering compositional windows and gradient "
    "architecture, with additional filings covering our top candidate scheduled within 30 days."
)
bp(doc, "Key Technologies Deployed: ",
    "3D FEniCS Finite Element Analysis, CALPHAD TCHEA4 thermodynamic database, "
    "MACE and CHGNet Machine Learning Force Field Molecular Dynamics, Pareto Multi-Objective "
    "Optimization, Random Forest surrogate modeling, Constrained Differential Evolution, "
    "LENS Additive Manufacturing recipe generation."
)

# =====================================================
# 12. LEADERSHIP & CONTACT
# =====================================================
doc.add_heading("12. Research Leadership & Contact Information", level=1)
p = doc.add_paragraph()
r = p.add_run("Crystal Paradigm Engineering")
r.bold = True; r.font.size = Pt(13)
doc.add_paragraph("Location: Hyderabad, India")
doc.add_paragraph("Website: crystalparadigm.in")
doc.add_paragraph("Email: khub.crystalparadigm@gmail.com")
doc.add_paragraph()

doc.add_heading("Technical Lead: Dr. Kasarapu Venkataramana", level=2)
doc.add_paragraph(
    "Dr. Venkataramana is a Research Associate at CSIR-IICT, Hyderabad, and an Associate Fellow of the "
    "Telangana Academy of Sciences (2024). With over 12 years of research and 5 years of academic teaching "
    "experience, he specializes in High Entropy Oxides, Solid Oxide Fuel Cells, and advanced nanomaterial synthesis. "
    "He has authored 38 research publications (610+ citations, h-index 14) and 2 book chapters. He is "
    "currently leading DRDO-sponsored pyrotechnic nanomaterial fabrication projects. At Crystal Paradigm, "
    "he drives the Ceramic Materials, CALPHAD Phase Thermodynamics, and Refractory Alloy Design initiatives."
)

doc.add_heading("AI/ML Lead: Dr. Shilpa Choudhary", level=2)
doc.add_paragraph(
    "Dr. Choudhary, recognized among the Top 2% Scientists Worldwide by Stanford University (2024), "
    "brings over 16 years of research expertise in Artificial Intelligence, Deep Learning, and AI-driven scientific "
    "applications. With postdoctoral research experience at the Singapore Institute of Technology and the "
    "National Kaohsiung University of Science and Technology (Taiwan), she has authored over 100 research papers, "
    "12 academic books, and holds multiple patents in emerging technology domains. At Crystal Paradigm, "
    "she leads AI innovation, ML Architecture, Constrained Optimization, and Surrogate Model Design."
)
doc.add_paragraph()
doc.add_paragraph(
    "For inquiries regarding the Safran Explore Challenge or collaboration opportunities, "
    "please reach out directly. We welcome the opportunity to present our platform capabilities "
    "in person during the Pitch Session and Explore Days."
)
doc.add_paragraph()
fp = doc.add_paragraph()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fr = fp.add_run("Document Classification: Confidential Pre-NDA Submission | Version: 3.0 (Final) | June 2026 | Crystal Paradigm Engineering")
fr.font.size = Pt(8); fr.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

# -- SAVE with explicit encoding safety --
out = r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\references_and_guides\FINAL_SUBMISSION_FILES\Crystal_Paradigm_Final_Submission.docx"
doc.save(out)
print(f"SAVED: {out}")
print("SMART REDACTIONS APPLIED. BUDGET REMOVED. MONTHS REMOVED. EMAIL ADDED. IP PROTECTED.")
