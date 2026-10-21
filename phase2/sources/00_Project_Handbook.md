# HE MCGA project handbook
Crystal Paradigm | Reading guide and current project explanation | 21 October 2026

We are developing a computational method to select refractory alloy compositions and metal to ceramic gradients for thermal applications. The deliverable today is a tested screening workflow and unmeasured coupon designs. The research question is whether this method can identify manufacturable systems that meet a real application's mechanical, thermal and environmental requirements with fewer unsuccessful experiments. That advantage has not yet been measured.

Start here, then use the nine focused documents. This pack is the current technical reference; conflicting claims in older submissions remain historical records.

## Read the pack in this order
| File | What you should learn |
| 00 Project Handbook | Explain the whole project and distinguish results from plans |
| 01 Materials Science Deep Dive | Connect composition, phases, microstructure and failure mechanisms |
| 02 Data and AI Models | Explain exactly what is learned, evaluated and uncertain |
| 03 Inverse Design and Closed Loop | Follow a proposal through selection, measurement and retraining |
| 04 Simulation and Evidence | Understand the executed physics, controls and limits |
| 05 Manufacturing and Recipe | Read the 11 layer design and understand what fabrication still needs |
| 06 Validation and IIT Delhi Collaboration | Turn unknowns into tests and realistic facility requests |
| 07 Business Budget and Milestones | Explain the customer hypothesis, INR 65 lakh plan and delivery gates |
| 08 Founder Preparation and Program Call | Rehearse technical and finance answers and use the manager's guidance |
| 09 Strict Audit and IP Handover | See residual rejection risks and prepare the next patent focused phase |

First read 00, the conclusions in 01, and 07 to 09. Then rehearse 02 to 06 alongside the generated data files.

## Problem and proposed solution
A hot surface and a cooler interior expand by different amounts. Joining a stiff ceramic to a metal adds differences in thermal expansion and stiffness. These mismatches can generate stresses, crack a coating or separate an interface. High temperature also introduces oxidation, time dependent deformation and chemical reactions. Solving only the elastic stress problem does not solve all of those mechanisms.

HE MCGA explores a refractory multicomponent metal and a graded transition toward lanthanum zirconate ceramic, abbreviated LZO. Alloy chemistry affects density and estimated properties. The ceramic fraction changes through thickness. The workflow searches chemistry, grading exponent and thickness together, then proposes specimens for experimental learning. This is inverse design: start with requirements and search for inputs that might satisfy them.

The nine element search alphabet is Mo, Nb, Ta, W, Cr, V, Ti, Zr and Hf. It does not currently include Al. The model's metal is a composition hypothesis, not an already manufactured or confirmed single phase alloy. LZO is a fixed ceramic choice in the checked profiles, not an independently optimized or proven best top coat.

{{figure:system_workflow.png|The connected computational path and the external experimental steps}}

## What exists now
| Evidence class | Current position |
| Executed software | Curated data, two property regressors, protected evaluation, joint inverse screening, reduced thermal mechanics, complete candidate vectors and feedback ingestion |
| Executed analysis | Two application screens, equal volume graded and sharp bilayer controls, mesh checks, boundary comparisons and assumption perturbations |
| Numerical verification | 37 checks passed; analytical limits, unit handling, benchmark separation and feedback failures are covered |
| Experimental material evidence | No new alloy, coating or physical feedback measurement was produced in these phases |
| Thermodynamic evidence | CALPHAD adapter checked on an Al Ni fixture; target alloy assessed database and phase validation absent |

## Current screening results
{{table:current_results}}

Estimated areal masses are 10.18 kg per square metre for aerospace and 6.04 for Sona. This is laminate mass per unit area, not blade or die mass. The two screens impose different conditions; compare each against its own baseline.

The protected compression yield benchmark remains MAE 229.5 MPa and R squared 0.457. More importantly, the calibrated yield bounds are wide enough that the top candidates' lower bounds are zero. Consequently the present ranking cannot establish a strength advantage. Chemistry, estimated stress, estimated mass and training proximity drive the current choices. A candidate is a testable question, not a discovered superior material.

## Application strategy and claim boundary
Aerospace supplies the original research motivation, but it requires substantial qualification beyond coupon screening. For Sona Comstar, precision forging provides a specific discussion about tooling durability. The connection is an application hypothesis inferred from the company's public product information, not an agreed pilot or evidence that our LZO gradient is suitable for a forging die. [S2]

We should present a narrow feasibility program: confirm requirements and the incumbent baseline, review manufacture, make controlled coupons, measure the missing properties, and complete one prospective feedback iteration. The proposed 24 month plan is organized around those gates. A failed candidate can still be useful if it identifies the limiting mechanism and changes the next selection.

## How to keep the versions straight
Phase 1 results are frozen at commit 2bd2885. Phase 2 code is version 0.2.0. Use phase2/results/aerospace_v2 and phase2/results/sona_v2; keep candidate chemistry, results and objective version together. Repairs are detailed in 09.

Patent drafting and the final deck follow this documentation phase. Read 09 before reusing historical patent, publication or performance claims.
