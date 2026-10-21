"""CLI: python -m he_mcga run|ingest|calphad ... (see phase1/README.md)."""
import argparse
import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from . import __version__
from .composition import ELEMENTS,descriptors,composition_id
from .data import curate,sha256
from .feedback import ingest,augment
from .models import PropertyModel
from .search import search,sensitivity
from .thermal import laminate
from .applications import readiness,tooling_economics

ROOT=Path(__file__).resolve().parents[2]


def write_json(path,value):
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def validate_config(c):
    required={'profile','seed','hot_face_K','cold_face_K','stress_free_K','yield_screen_temperature_K',
      'processing','mechanical_constraint','ceramic','thermal_cells','exponent_bounds',
      'thickness_bounds_m','population_multiplier','iterations','shortlist_size','constraints'}
    if not required<=set(c): raise ValueError(f'missing config fields: {sorted(required-set(c))}')
    for k in ('seed','thermal_cells','population_multiplier','iterations','shortlist_size'):
        if type(c[k]) is not int or c[k]<0: raise ValueError(f'{k} must be a nonnegative integer')
    if c['thermal_cells']<2 or min(c['population_multiplier'],c['shortlist_size'])<1: raise ValueError('invalid run size')
    for key in ('exponent_bounds','thickness_bounds_m'):
        lo,hi=c[key]
        if not np.isfinite([lo,hi]).all() or not 0<lo<hi: raise ValueError('positive ordered design bounds required')
    for key in ('hot_face_K','cold_face_K','stress_free_K','yield_screen_temperature_K'):
        if not np.isfinite(c[key]) or c[key]<=0: raise ValueError('temperatures must be positive kelvin')
    if c['hot_face_K']<=c['cold_face_K']: raise ValueError('hot face must exceed cold face')
    limits=c['constraints']
    for key in ('max_atomic_fraction','min_Cr_atomic_fraction','max_V_atomic_fraction','max_density_g_cm3','max_heat_flux_W_m2'):
        if key not in limits or not np.isfinite(limits[key]) or limits[key]<0: raise ValueError('invalid constraint bounds')
    if not .05<=limits['max_atomic_fraction']<=1 or limits['min_Cr_atomic_fraction']>limits['max_atomic_fraction'] or limits['max_V_atomic_fraction']>1:
        raise ValueError('inconsistent chemical constraints')


def run(args):
    cfg=json.loads(Path(args.config).read_text()); validate_config(cfg)
    out=Path(args.output)
    if out.exists(): raise ValueError('output already exists; choose a new immutable run directory')
    models={}; evaluations={}; sources={}; datasets={}; rejected={}; holdouts={}
    for target in ('bulk','yield'):
        data,reject,source=curate(ROOT,target)
        data=augment(data,args.feedback,target,cfg['seed'],ROOT)
        model=PropertyModel(data,target,cfg['seed']); report,rows=model.evaluate()
        models[target]=model; evaluations[target]=report; sources[target]=source
        datasets[target]=model.data; rejected[target]=reject; holdouts[target]=rows
    print('Models evaluated on protected composition groups; running joint screening...',flush=True)
    all_rows,feasible,top,batch,summary=search(models['bulk'],models['yield'],cfg)
    best=top.iloc[0].to_dict(); comp=json.loads(best['atomic_fractions']); material=descriptors(comp)
    def physical(cells,hot=None,constraint=None):
        return laminate(material['E_Pa'],material['alpha_1_K'],material['k_W_mK'],
           best['thickness_m'],best['exponent'],cfg['ceramic'],cells,cfg['cold_face_K'],
           cfg['hot_face_K'] if hot is None else hot,cfg['stress_free_K'],
           cfg['mechanical_constraint'] if constraint is None else constraint)
    mesh=[]
    for n in (20,40,80,160,320):
        r=physical(n); mesh.append({'cells':n,**{k:v for k,v in r.items() if k!='layers'}})
    # Same chemistry/geometry, two explicit face temperature profiles and two
    # mechanical constraints. These are comparisons, not optimized new winners.
    comparisons=[]
    for hot in (1400.,1673.15):
        for constraint in ('free_curvature','flat_force_free'):
            r=physical(cfg['thermal_cells'],hot,constraint)
            comparisons.append({'hot_face_K':hot,'hot_face_C':hot-273.15,
               **{k:v for k,v in r.items() if k!='layers'}})
    recipe_result=physical(11)
    recipe=recipe_result['layers']
    # Ceramic density is only a declared conversion assumption; vendor density
    # and measured shrinkage/porosity are needed before dispensing powders.
    for row in recipe:
        f=row['ceramic_volume_fraction']; rho_m=material['density_g_cm3']; rho_c=6.
        row.update({'metal_atomic_fractions':best['atomic_fractions'],'ceramic':cfg['ceramic'],
                    'metal_mass_fraction':(1-f)*rho_m/((1-f)*rho_m+f*rho_c),
                    'ceramic_mass_fraction':f*rho_c/((1-f)*rho_m+f*rho_c),
                    'ceramic_density_assumption_g_cm3':rho_c,
                    'status':'unqualified coupon design; no shrinkage/porosity/process calibration'})
    out.mkdir(parents=True)
    write_json(out/'config.json',cfg); write_json(out/'metrics.json',evaluations)
    write_json(out/'coupon_recipe_screening.json',{k:v for k,v in recipe_result.items() if k!='layers'});
    write_json(out/'search_summary.json',summary); write_json(out/'best_candidate.json',{
        'composition_id':composition_id(comp),'atomic_fractions':comp,
        'design':{'exponent':best['exponent'],'thickness_m':best['thickness_m'],'ceramic':cfg['ceramic']},
        'screening':best,'mixture_estimates':material,'qualification':'UNMEASURED, NOT QUALIFIED'})
    for target in models:
        datasets[target].to_csv(out/f'{target}_curated.csv',index=False)
        rejected[target].to_csv(out/f'{target}_rejected.csv',index=False)
        holdouts[target].to_csv(out/f'{target}_holdout_predictions.csv',index=False)
    all_rows.to_csv(out/'all_evaluations.csv',index=False)
    feasible.to_csv(out/'feasible_candidates.csv',index=False)
    top.to_csv(out/'shortlist.csv',index=False); batch.to_csv(out/'proposed_measurement_batch.csv',index=False)
    pd.DataFrame(recipe).to_csv(out/'coupon_recipe_11_layers.csv',index=False)
    pd.DataFrame(mesh).to_csv(out/'mesh_convergence.csv',index=False)
    pd.DataFrame(comparisons).to_csv(out/'temperature_and_constraint_comparison.csv',index=False)
    sensitivity(best,cfg,cfg['seed']).to_csv(out/'assumption_sensitivity.csv',index=False)
    pd.DataFrame(readiness()).to_csv(out/'readiness_gates.csv',index=False)
    write_json(out/'tooling_economics_assumptions.json',tooling_economics(1000000,50000,100000,65000,115000,500000))
    versions={p:importlib.metadata.version(p) for p in ('numpy','pandas','scipy','scikit-learn')}
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    status=subprocess.run(['git','status','--porcelain','--untracked-files=normal'],cwd=ROOT,capture_output=True,text=True)
    code_files=list((ROOT/'phase1/he_mcga').glob('*.py'))+[ROOT/'pyproject.toml']
    manifest={'package_version':__version__,'python':platform.python_version(),'dependencies':versions,
       'seed':cfg['seed'],'base_commit':git.stdout.strip(),'working_tree_dirty':bool(status.stdout.strip()),
       'code_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in sorted(code_files)},
       'input_sources':sources,'config_sha256':sha256(args.config),
       'feedback_sha256':sha256(args.feedback) if args.feedback else None,
       'feedback_records':len(json.loads(Path(args.feedback).read_text())) if args.feedback else 0,
       'closed_loop_status':'measurement ingestion/retraining implemented; no new physical measurement demonstrated in reference runs',
       'artifact_sha256':{p.name:sha256(p) for p in sorted(out.iterdir()) if p.is_file()}}
    write_json(out/'manifest.json',manifest)
    print(json.dumps({'output':str(out),'search':summary,'best':best},indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('run'); p.add_argument('--config',required=True); p.add_argument('--output',required=True)
    p.add_argument('--feedback'); p.set_defaults(handler=run)
    p=sub.add_parser('ingest'); p.add_argument('--measurements',required=True); p.add_argument('--ledger',required=True)
    p.add_argument('--seed',type=int,default=42)
    p.set_defaults(handler=lambda a:print(f'Accepted {ingest(a.measurements,a.ledger,ROOT,a.seed)} measurements'))
    p=sub.add_parser('calphad'); p.add_argument('--database',required=True); p.add_argument('--composition',required=True,
      help='JSON atomic-fraction mapping file'); p.add_argument('--temperatures-K',required=True,nargs='+',type=float)
    p.add_argument('--provenance',required=True); p.add_argument('--output',required=True)
    def calphad(a):
        from .calphad import equilibrate
        if Path(a.output).exists(): raise ValueError('output already exists')
        write_json(a.output,equilibrate(a.database,json.loads(Path(a.composition).read_text()),a.temperatures_K,a.provenance))
    p.set_defaults(handler=calphad)
    args=parser.parse_args()
    try: args.handler(args)
    except (ValueError,FileNotFoundError) as exc: parser.exit(2,f'ERROR: {exc}\n')

if __name__=='__main__': main()
