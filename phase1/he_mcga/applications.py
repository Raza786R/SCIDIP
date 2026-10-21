"""Transparent application checks and scenario economics; no customer claims."""
import numpy as np


def centrifugal_root_stress_MPa(density_g_cm3,rpm,root_radius_m,tip_radius_m):
    """Constant-area radial blade, no taper, bending, gas or thermal stress.

    sigma_root = rho * omega^2 * (r_tip^2-r_root^2)/2.
    This isolated load term is not a component assessment or an allowable.
    """
    if not np.isfinite([density_g_cm3,rpm,root_radius_m,tip_radius_m]).all() or density_g_cm3<=0 or rpm<0 or not 0<=root_radius_m<tip_radius_m:
        raise ValueError('positive density, valid rpm and ordered radii required')
    return float(density_g_cm3*1000*(rpm*2*np.pi/60)**2*(tip_radius_m**2-root_radius_m**2)/2/1e6)


def tooling_economics(annual_parts,baseline_parts_per_tool,baseline_tool_cost_INR,
                      proposed_parts_per_tool,proposed_tool_cost_INR,pilot_cost_INR):
    """Continuous expected tool consumption; all arguments are scenario assumptions.

    Excludes downtime, scrap, tax, financing and maintenance. Does not assert
    tool life improvement or Sona Comstar's costs, throughput or requirements.
    """
    vals=[annual_parts,baseline_parts_per_tool,baseline_tool_cost_INR,
          proposed_parts_per_tool,proposed_tool_cost_INR,pilot_cost_INR]
    if not np.isfinite(vals).all() or min(vals[:5])<=0 or pilot_cost_INR<0:
        raise ValueError('invalid tooling scenario')
    baseline=annual_parts/baseline_parts_per_tool*baseline_tool_cost_INR
    proposed=annual_parts/proposed_parts_per_tool*proposed_tool_cost_INR
    savings=baseline-proposed
    return {'assumptions_only':True,'baseline_annual_tooling_INR':baseline,
       'proposed_annual_tooling_INR':proposed,'annual_tooling_difference_INR':savings,
       'break_even_life_ratio':proposed_tool_cost_INR/baseline_tool_cost_INR,
       'simple_pilot_payback_years':pilot_cost_INR/savings if savings>0 else None,
       'customer_evidence':'none; require measured life and supplier quotations'}


def readiness():
    return [
      {'area':'materials','gate':'phase stability','status':'unverified','evidence_needed':'composition-specific assessed CALPHAD + XRD/SEM/EDS after exposure'},
      {'area':'materials','gate':'oxidation and ceramic compatibility','status':'unverified','evidence_needed':'cyclic oxidation mass change, scale chemistry, diffusion couple and bond tests'},
      {'area':'AI_ML','gate':'unseen composition benchmark','status':'computed','evidence_needed':'metrics.json; independent prospective external test still required'},
      {'area':'closed_loop','gate':'measured feedback iteration','status':'not_yet_demonstrated','evidence_needed':'real lab report + validated ingest + next-generation run comparison'},
      {'area':'aerospace','gate':'component qualification','status':'not_qualified','evidence_needed':'temperature-dependent tensile/creep/fatigue/bond allowables + transient 3-D thermo-mechanics + component validation'},
      {'area':'Sona_Comstar','gate':'forging-tool coupon pilot','status':'hypothesis','evidence_needed':'confirm thermal cycle, substrate, pressure, friction/wear and failure mode with sponsor; benchmark current tool'},
      {'area':'business','gate':'paying customer and advantage','status':'unverified','evidence_needed':'signed pilot scope, competing baseline, measured cost/part and repeatable delivery'},
      {'area':'IP','gate':'protectable scope','status':'not_assessed_in_phase1','evidence_needed':'Phase 2 prior art, disclosure timeline, inventorship and professional claim assessment'},
      {'area':'team','gate':'execution capability','status':'requires_confirmation','evidence_needed':'named metallurgy, coatings/manufacturing, ML and customer pilot owners with facility access'}]
