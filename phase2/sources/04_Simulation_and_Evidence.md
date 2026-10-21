# Thermal simulation and the evidence it supports
Crystal Paradigm | Equations assumptions controls and numerical verification

The executed physical model is steady one dimensional conduction plus small strain equibiaxial elastic laminate mechanics. It predicts heat flux, temperature distribution, curvature and in plane stress under explicit assumptions. It does not resolve interface shear, crack propagation, creep, fatigue life or a rotating aerospace component. The historical FEA filename is retained only as an adapter to this model.

## Geometry and properties
The metal rich cold face is at z equals zero and the ceramic rich hot face is at z equals L. Ceramic fraction follows a power of normalized thickness. Each layer uses the exact average of that function so the discretization conserves total ceramic volume. Conductivity and Young modulus use harmonic mixture estimates; CTE is volume weighted. These are declared screening approximations, not calibrated properties of an alloy ceramic microstructure.

| Quantity | Implemented assumption |
| Alloy E CTE and k | Inherited elemental reference values converted with declared volume mixture rules |
| LZO E CTE and k | 175 GPa; 9.1 microstrain per K; 1.6 W per metre K |
| Poisson ratio | Metal 0.30; ceramic 0.25; volume interpolation |
| Temperature behavior | Constants held fixed; no validated temperature dependence |
| Bonding | Perfect continuity and load transfer; no contact gap or interface resistance |
| Reference state | Configured stress free temperature; fabrication residual stress not inferred |

A harmonic mixture resembles a Reuss type estimate. It should not be relabeled a Hashin Shtrikman calculation or a validated bound for a reactive, porous real alloy. The predicted bulk modulus is not used to manufacture an elastic modulus through an arbitrary multiplier.

## Heat conduction
{{equation:conduction.png|Series resistance gives a conserved heat flux and a continuous layer temperature}}

Each layer has constant conductivity and a linear temperature profile. All layers carry the same steady heat flux. The input temperatures are material face temperatures. A gas temperature requires convection and radiation boundary information that is not currently supplied. Holding both faces at selected temperatures does not demonstrate a cooling induced substrate temperature reduction in a real engine.

At equal phase volumes and total thickness, the selected harmonic mixing and series model make total resistance independent of whether the distribution is graded or a sharp bilayer. The control study confirms equal heat flux. A claimed insulation benefit from grading alone would therefore be inconsistent with our current equations.

## Bonded laminate mechanics
{{equation:stress.png|In plane compatibility is solved with thermal eigenstrain and an elastic stiffness}}

Q is the equibiaxial plane stress stiffness E divided by one minus Poisson ratio. The midplane strain and curvature define a compatible in plane strain through thickness. Subtracting the local free thermal strain gives stress. Two point Gaussian integration evaluates the layerwise elastic force and moment terms.

For a freely curving laminate, a two by two extensional bending system solves strain and curvature so net force and moment match the applied resultants. For the flat case, curvature is fixed to zero; force equilibrium is solved and a reaction moment is reported. These are alternative constraints, not interchangeable material properties. No arbitrary creep relief or edge concentration multiplier is applied.

The code evaluates stress on both sides of each layer because stiffness changes can produce stress discontinuities. The result is in plane tensile or compressive stress, not interfacial shear. Dividing a compression yield prediction by a ceramic dominated in plane peak cannot establish a qualified safety factor.

## Equal volume architecture controls
{{table:control_results}}

Both architectures use the same chemistry, total thickness, average ceramic amount and constituent estimates. Only the distribution changes. In the aerospace free curvature comparison, grading lowers the calculated peak by about 42 percent; under flat constraint the reduction is about 6 percent. These percentages are model specific mechanical comparisons. No specimen survival, experimental improvement or general superiority over an incumbent coating follows from them.

{{figure:control_comparison.png|Boundary condition dependence of the graded and sharp architecture comparison}}

## Numerical verification and sensitivity
The tests cover an identical material with a linear gradient and free curvature, which should have essentially zero elastic stress; zero temperature change; prescribed force and moment balance; correct hot and cold orientation; conserved phase volumes; and layer geometry. A sharp control is also checked for equal thermal resistance at equal volumes. These checks detect mathematical or implementation errors.

The run includes 20, 40, 80, 160 and 320 layer comparisons. Peak stress need not converge monotonically because the location of a layerwise peak can move. Inspect the actual mesh table rather than asserting convergence from a single run. The 11 layer manufacturing proposal is recalculated separately; its stress is not silently copied from the 80 layer search.

A 100 draw assumption study perturbs the estimated alloy E, CTE and k by 10 percent, thickness by 5 percent and hot face temperature by 50 K. The uniform ranges are analyst chosen scenarios. Their stress range is not a calibrated material confidence interval or a reliability probability.

## What has not been simulated
No new target alloy DFT, molecular dynamics, 3D FEniCS component analysis, creep integration, transient burner rig or fatigue life analysis was performed. The Al Ni CALPHAD fixture verifies software operation only. The isolated centrifugal load helper assumes a constant area radial blade and is unit tested; without actual geometry and loads it is not a component assessment.

The next physical model should use measured temperature dependent properties, actual substrate and bond layers, realistic heating and cooling boundaries and an experimentally supported constitutive law. Cracks and delamination require appropriate fracture or cohesive descriptions and calibration. More mesh cells or cloud jobs cannot supply missing physics or material data.
