# Manufacturing interpretation of the eleven layer recipe
Crystal Paradigm | From a computational composition to a coupon process plan

The exported recipe defines geometry and ideal phase proportions. It is a coupon design proposal, not validated machine code or a qualified LENS process. No beam power, feed rate, scan strategy, sintering schedule or heat treatment has been experimentally calibrated for the selected alloy and ceramic.

## What the architecture actually specifies
The metal composition is constant across the current gradient. The metal to ceramic volume ratio changes with depth. The first layer is metal rich and the last is ceramic rich; their layer averages are not exactly pure endpoint compositions. A separate pure substrate or top coat is not automatically included. If a real component requires them, its geometry and compatibility must be added explicitly.

{{equation:gradient.png|Exact layer average fractions conserve the continuous gradient volume}}

The layer thicknesses sum to the specified total. The average ceramic fraction over the full laminate is one divided by n plus one. A smaller exponent places more ceramic toward the metal side under this convention. The term graded architecture describes this function; it does not demonstrate that deposition can reproduce it.

## Current aerospace metal chemistry
{{table:composition_recipe}}

Atomic percent is appropriate for defining the alloy. The corresponding mass fractions are needed if elemental powders are weighed separately. If a prealloyed metal powder is used, the feedstock already carries the specified metal chemistry and the phase blending problem is different. We must verify the actual composition of the manufactured coupon rather than treating a digital ratio as the measured result.

## The eleven layer design
{{table:layer_recipe}}

The table gives the nominal dense architecture. The metal mass fraction per layer follows the alloy density estimate and an assumed LZO density of 6 g per cubic centimetre. It does not include binder, powder loss, packing voids, oxidation, evaporation or sintering shrinkage. The authority is the full precision CSV, not the rounded table above.

For a proposed one square centimetre coupon, the current modeled areal mass corresponds to about 1.018 g of ideal dense laminate before those process effects. This is a geometry example, not a procurement quantity or an experimentally achieved mass. For an elemental feed in a layer, multiply total layer mass by metal mass fraction and then by the metal element's mass fraction. Ceramic powder is a compound; La and O in LZO are not additions to the metallic alloy model alphabet.

## Candidate process routes and why none is yet selected
Directed energy deposition, DED, delivers feedstock into a locally heated region. LENS is a particular laser based approach in this family. A graded feed can potentially vary composition, but powder transport, capture efficiency, melting, wetting and reaction behavior must be established. A generic multi feeder system does not prove that this refractory alloy and LZO can be co deposited without cracking or reaction.

Powder consolidation and sintering offer another research route. Densification mismatch, interface diffusion, temperature windows and residual stress still need qualification. A sprayed or layered ceramic over a separately made alloy coupon is another architecture, with its own bond and porosity questions. These are alternatives for process review, not promises that all are available or suitable.

| Process question | Evidence needed before a fabrication claim |
| Feedstock | Supplier composition certificate, particle size and morphology, contamination and safety information |
| Thermal compatibility | Melting or consolidation window, differential shrinkage and reaction assessment |
| Gradient delivery | Calibrated relationship between commanded and deposited phase fractions |
| Bond and defects | Cross sections, porosity, crack maps and relevant adhesion or fracture test |
| Reproducibility | Independently made specimens with recorded process history and actual chemistry |
| Application finish | Surface finish, dimensions and post treatment compatible with the use case |

Do not copy a laser parameter from an unrelated material and call it a recipe validation. High nominal feedstock purity does not by itself guarantee single phase BCC or prevent every brittle phase. Powder hazards and atmosphere controls must be assessed for the actual supplier and process; blanket statements about every refractory powder are not adequate.

## Batch record and acceptance
Assign specimen IDs before manufacture. Record feedstock lot, nominal and actual chemistry, process settings, layer sequence, atmosphere, temperature history, post treatment, dimensions and mass. Characterize phase structure and elemental distribution through the gradient. Record rejected and cracked specimens, not only successful sections.

Acceptance starts with measurable geometry and chemistry tolerances agreed with the lab, followed by defect and bonding limits appropriate to the intended application. Tolerances are not yet assigned numerical values because process capability has not been measured. The 11 layer design can be revised after the first manufacture study; eleven is a chosen discretization, not a physically proven optimal number.

## What to ask IIT Delhi
Ask which route can safely process these exact metal and ceramic feedstocks, what specimen dimensions are accepted, how atmosphere and gradient composition are controlled, and what preparation and characterization services are available. Request a feasibility review and a written quote. The official facility listings support an initial discussion; they do not establish a booked target compatible multi hopper LENS system or an exclusive capability in India. [S8 S12]
