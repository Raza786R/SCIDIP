"""Seeded joint composition/gradient screening with hard feasibility checks."""
import json
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution
from .composition import ELEMENTS, fractions, composition_id, encode, descriptors
from .thermal import laminate
from .data import partition


def chemical_constraints(comp, cfg):
    c = fractions(comp); d = descriptors(c); problems = []
    if sum(v>=.05-1e-12 for v in c.values())<5: problems.append('fewer_than_5_elements_at_5atpct')
    if max(c.values())>cfg['max_atomic_fraction']+1e-12: problems.append('element_above_max_atomic_fraction')
    if c['Cr']<cfg['min_Cr_atomic_fraction']-1e-12: problems.append('Cr_below_design_minimum')
    if c['V']>cfg['max_V_atomic_fraction']+1e-12: problems.append('V_above_design_maximum')
    if d['density_g_cm3']>cfg['max_density_g_cm3']+1e-12: problems.append('density_above_design_limit')
    return problems,d


def pareto_mask(values):
    """All objectives minimized. Equal points remain nondominated."""
    a = np.asarray(values); keep = np.ones(len(a),dtype=bool)
    for i in range(len(a)):
        keep[i] = not np.any(np.all(a<=a[i],axis=1)&np.any(a<a[i],axis=1))
    return keep


def eligible_strength_lower(prediction):
    """No optimization reward from an interval flagged outside applicability."""
    lower=prediction.get('lower')
    if not prediction.get('interval_applicable') or lower is None or not np.isfinite(lower):
        return 0.0
    return max(0.0,float(lower))


def areal_mass_kg_m2(density_g_cm3,ceramic_density_g_cm3,thickness_m,exponent):
    """Integrate rho(z) for additive-volume grading with f_c=(z/L)^n."""
    values=[density_g_cm3,ceramic_density_g_cm3,thickness_m,exponent]
    if not np.isfinite(values).all() or min(values)<=0:
        raise ValueError('positive finite density and gradient geometry required')
    return thickness_m*1000*(density_g_cm3+(ceramic_density_g_cm3-density_g_cm3)/(exponent+1))


def search(bulk, strength, cfg):
    seed = cfg['seed']; rng = np.random.default_rng(seed); records = []
    def evaluate(x, method):
        raw = np.exp(x[:9]-np.max(x[:9])); comp = dict(zip(ELEMENTS,raw/raw.sum()))
        exponent,thickness = float(x[9]),float(x[10])
        errors,d = chemical_constraints(comp,cfg['constraints'])
        row = {'evaluation':len(records)+1,'method':method,'composition_id':composition_id(comp),
               'atomic_fractions':encode(comp),'exponent':exponent,'thickness_m':thickness,
               'density_g_cm3':d['density_g_cm3'],'feasible':False}
        if errors:
            row['rejections']=';'.join(errors); row['score']=1e6+len(errors)
            records.append(row); return row['score']
        b = bulk.predict(comp)
        y = strength.predict(comp,cfg['yield_screen_temperature_K'],cfg['processing'])
        physical = laminate(d['E_Pa'],d['alpha_1_K'],d['k_W_mK'],thickness,exponent,
                             cfg['ceramic'],cfg['thermal_cells'],cfg['cold_face_K'],
                             cfg['hot_face_K'],cfg['stress_free_K'],cfg['mechanical_constraint'])
        if abs(physical['heat_flux_W_m2'])>cfg['constraints']['max_heat_flux_W_m2']:
            errors.append('heat_flux_above_design_limit')
        # Scalarized heuristic for search only. No safety-factor or life claim.
        # Penalize surrogate extrapolation rather than rewarding high predictions alone.
        lower = eligible_strength_lower(y)
        areal_mass=areal_mass_kg_m2(d['density_g_cm3'],cfg.get('ceramic_density_g_cm3',6.),thickness,exponent)
        score = (physical['peak_inplane_stress_MPa']/1000
                 +.2*d['density_g_cm3']/10-.2*lower/1000
                 +.25*y['nearest_training_L1']+.5*len(y['domain_flags'])
                 +cfg.get('areal_mass_weight',.1)*areal_mass/20)
        row.update({'feasible':not errors,'rejections':';'.join(errors),
                    'score':score if not errors else 1e6+len(errors),
                    'peak_inplane_stress_MPa':physical['peak_inplane_stress_MPa'],
                    'heat_flux_W_m2':physical['heat_flux_W_m2'],
                    'bulk_GPa_prediction':b['prediction'], 'bulk_domain_flags':';'.join(b['domain_flags']),
                    'compression_YS_MPa_prediction':y['prediction'],
                    'compression_YS_MPa_lower':y['lower'],'compression_YS_MPa_upper':y['upper'],
                    'ranking_YS_lower_MPa':lower,'areal_mass_kg_m2':areal_mass,
                    'yield_tree_spread_MPa':y['tree_spread'],
                    'yield_nearest_training_L1':y['nearest_training_L1'],
                    'yield_domain_flags':';'.join(y['domain_flags']),
                    'yield_interval_applicable':y['interval_applicable'],
                    'phase_status':'unverified','oxidation_status':'unverified',
                    'qualification_status':'screening_only'})
        records.append(row)
        return row['score']
    bounds = [(-2,2)]*9+[tuple(cfg['exponent_bounds']),tuple(cfg['thickness_bounds_m'])]
    start = len(records)
    result = differential_evolution(lambda x:evaluate(x,'differential_evolution'),bounds,
             seed=seed,popsize=cfg['population_multiplier'],maxiter=cfg['iterations'],
             polish=False,tol=0,atol=0,updating='immediate',workers=1)
    budget = len(records)-start
    # Fair equal evaluation budget random baseline, same bounds/parameterization.
    for _ in range(budget):
        evaluate(np.array([rng.uniform(*b) for b in bounds]),'random_baseline')
    frame = pd.DataFrame(records)
    feasible = frame[frame.feasible].copy()
    if feasible.empty:
        raise ValueError('no feasible screening candidates; no recipe may be exported')
    feasible['pareto'] = pareto_mask(np.column_stack([
       feasible.peak_inplane_stress_MPa,feasible.density_g_cm3,
       -feasible.ranking_YS_lower_MPa,feasible.areal_mass_kg_m2]))
    feasible = feasible.sort_values(['score','evaluation'])
    shortlist = feasible.head(cfg['shortlist_size']).copy()
    # Separate batches: near-term exploitation, then high disagreement exploration,
    # with a composition L1 diversity threshold and no fake experimental results.
    selected = []; used = []
    pool = feasible.drop_duplicates('composition_id')
    for intent,rows in [('performance_screen',pool.sort_values('score')),
                        ('uncertainty_probe',pool.sort_values('yield_tree_spread_MPa',ascending=False))]:
        n = 0
        for _,r in rows.iterrows():
            c = np.array(list(json.loads(r.atomic_fractions).values()))
            if any(np.abs(c-v).sum()<.15 for v in used): continue
            used.append(c); row=r.to_dict(); row['intent']=intent
            row['requested_measurement']='compression YS; separate oxidation/XRD/bond tests required'
            row['requested_temperature_K']=cfg['yield_screen_temperature_K']
            row['requested_unit']='MPa'; row['processing']=cfg['processing']
            row['specimen_status']='not_manufactured'; row['test_mode']='compression'
            group_role=partition([r.composition_id],seed)[0]
            row['benchmark_partition']=group_role
            row['ledger_ingest_allowed']=bool(group_role=='train')
            row['feedback_role']='training_feedback' if group_role=='train' else 'protected_validation_only'
            selected.append(row); n+=1
            if n==3: break
    summary = {'evaluations_per_method':budget,'seed':seed,
       'objective_version':'phase2_v2_applicability_gated_strength_and_areal_mass',
       'areal_mass_weight':cfg.get('areal_mass_weight',.1),
       'ceramic_density_assumption_g_cm3':cfg.get('ceramic_density_g_cm3',6.),
       'optimizer_success':bool(result.success),'optimizer_message':str(result.message),
       'termination_note':'Fixed-budget screen; no global optimality claim.',
       'feasible_per_method':feasible.groupby('method').size().to_dict(),
       'best_score_by_method':feasible.groupby('method').score.min().to_dict(),
       'pareto_candidates':int(feasible.pareto.sum()),
       'candidate_status':'Unmeasured computational hypotheses; no validated winner or safety factor.'}
    return frame,feasible,shortlist,pd.DataFrame(selected),summary


def sensitivity(candidate,cfg,seed=42,draws=100):
    comp = json.loads(candidate['atomic_fractions']); d = descriptors(comp)
    rng = np.random.default_rng(seed); rows=[]
    for i in range(draws):
        # Analyst-selected perturbation ranges, not measured probability laws.
        scales = rng.uniform(.9,1.1,3); hot = cfg['hot_face_K']+rng.uniform(-50,50)
        result = laminate(d['E_Pa']*scales[0],d['alpha_1_K']*scales[1],d['k_W_mK']*scales[2],
             candidate['thickness_m']*rng.uniform(.95,1.05),candidate['exponent'],cfg['ceramic'],
             cfg['thermal_cells'],cfg['cold_face_K'],hot,cfg['stress_free_K'],cfg['mechanical_constraint'])
        rows.append({'draw':i,'E_scale':scales[0],'alpha_scale':scales[1],'k_scale':scales[2],
                     'hot_face_K':hot,'peak_inplane_stress_MPa':result['peak_inplane_stress_MPa'],
                     'heat_flux_W_m2':result['heat_flux_W_m2']})
    return pd.DataFrame(rows)
