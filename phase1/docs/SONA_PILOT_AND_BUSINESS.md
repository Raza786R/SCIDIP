# Sona Comstar fit and startup experiment

## Specific, evidence-aligned application hypothesis

Sona Comstar publicly lists precision warm- and hot-forged driveline gears. A plausible conversation is therefore **thermal-management and durability screening for forging-tool surface/coupon architectures**. This is an inference from its manufacturing activities, not evidence of a known Sona die-life problem, an approved pilot, or internal operating conditions. See the company source in [SOURCES.md](SOURCES.md).

The current HE-MCGA model can help choose chemistry/gradient hypotheses and quantify sensitivity to thermal assumptions. It cannot yet choose an industrial die coating: tool steel/substrate compatibility, coating thickness, contact pressure, wear, friction, lubrication and failure modes are not represented. A 0.5–5 mm LZO-containing laminate is a research design space, not a recommendation to coat production tooling. The right pilot could reject the refractory alloy or ceramic altogether; that is a valid outcome.

Do not position this as an EV motor core or permanent-magnet replacement. The current data do not establish magnetic losses, permeability, saturation, electrical performance or motor efficiency. Do not imply an aerospace coupon is already suitable for automotive gear contact.

## Implemented application screen

`configs/sona_tooling_hypothesis.json` declares a cold face of 473.15 K, hot face of 873.15 K, stress-free reference of 300 K and flat mechanical constraint. These are **illustrative assumptions**, not customer specifications. The model searches composition, gradient exponent and thickness under the same explicit screening rules used by the aerospace profile. It provides a separate shortlist, proposed measurement batch and coupon recipe.

The leading Sona-screening hypothesis has density estimate 7.827 g/cm3, gradient exponent 0.5684, thickness 3.8389 mm and estimated peak in-plane stress 544.5 MPa under those assumptions. Compression-yield prediction is 890.5 MPa at 873.15 K, with a nominal calibrated interval approximately 0–2,539.2 MPa. Those wide bounds do not demonstrate a positive strength margin. No wear, life or cost reduction has been measured.

## Discovery and pilot scope

| Item to confirm with sponsor | Why it changes the design | Required output |
|---|---|---|
| Tool/process family and dominant failure mode | Thermal checking, abrasive wear and plastic collapse require different solutions | One agreed use case and baseline |
| Measured contact cycle, heating/cooling and atmosphere | Boundary conditions determine thermal stresses and oxidation needs | Instrumented cycle or accepted operating envelope |
| Existing substrate, surface treatment and allowable dimensions | Compatibility and geometry may exclude the current gradient | Manufacturing constraint sheet |
| Contact pressure, speed, lubricant and surface-quality requirement | Thermal insulation alone may harm forming performance | Wear/friction and part-quality acceptance tests |
| Current life distribution and replacement/refurbishment cost | Establishes the commercial break-even threshold | Anonymized baseline records and quotations |
| Access, ownership and review milestones | Makes the proposed work executable and governs resulting evidence | Written pilot scope, owners and data/IP terms |

A sensible first offer is a fixed-scope, paid-or-sponsored feasibility study with a requirement sheet, competing baseline, coupon design, evidence-backed report and go/no-go decision. Revenue, pricing and sponsor willingness are currently unvalidated. A subscription discovery platform or alloy license is a later business hypothesis, conditional on repeatable validated delivery and protectable/customer-owned data rights.

## Transparent tooling economics

`he_mcga/applications.py` implements continuous expected tool-consumption arithmetic and handles nonpositive savings without inventing a payback. The checked scenario assumes:

- 1,000,000 parts/year; baseline life 50,000 parts/tool and cost INR 100,000/tool.
- Proposed life 65,000 parts/tool and cost INR 115,000/tool.
- Feasibility/pilot cost INR 500,000.

These are invented **scenario inputs**, not material predictions, quotations or customer metrics. Baseline annual tooling is INR 2,000,000; proposed annual tooling is INR 1,769,231; difference is INR 230,769/year. Simple pilot payback is about 2.17 years. With a 15% tool-cost premium, life must improve by more than 15% just to reduce this modeled tooling expense. Downtime, scrap, process changes, maintenance, qualification, financing and tax are excluded. If life does not increase, the proposed tool is more expensive and no positive payback is reported.

## Startup and SCIDIP review

The defensible business claim is a method for reducing uncertainty in a defined materials development decision. Demonstrating faster iteration requires comparing against conventional expert selection at equal test budget, reporting unsuccessful experiments, time, cost and achieved properties. No quantified acceleration percentage is established by this repair.

Current rejection risks are broad application scope, missing customer evidence, uncertain manufacture, weak transfer from public data, no prospective feedback, unconfirmed execution partners and unassessed IP. Phase 1 supplies an auditable technical base and measurable gates. Phase 2 must address prior art, public-disclosure history and claim scope with appropriate expertise; a public repository or use of DE/ML alone does not establish an IP moat. Phase 3 should present the de-risking plan and evidence at its actual maturity.
