"""Equal-volume graded/bilayer controls; no empirical material validation."""
import json,sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'phase1'))
from he_mcga.composition import descriptors
from he_mcga.thermal import laminate
root=Path(__file__).resolve().parents[2]
rows=[]
for profile in ('aerospace_v2','sona_v2'):
 p=root/'phase2/results'/profile
 b=json.loads((p/'best_candidate.json').read_text());cfg=json.loads((p/'config.json').read_text())
 d=descriptors(b['atomic_fractions']);design=b['design'];L=design['thickness_m'];n=design['exponent'];fbar=1/(n+1)
 interface=L*(1-fbar);edges=np.r_[np.linspace(0,interface,41),np.linspace(interface,L,41)[1:]]
 for constraint in ('free_curvature','flat_force_free'):
  for architecture in ('graded','sharp_bilayer'):
   extra={} if architecture=='graded' else {'layer_edges_m':edges,'ceramic_fractions':[0.]*40+[1.]*40}
   r=laminate(d['E_Pa'],d['alpha_1_K'],d['k_W_mK'],L,n,cfg['ceramic'],80,
       cfg['cold_face_K'],cfg['hot_face_K'],cfg['stress_free_K'],constraint,**extra)
   rows.append({'profile':profile,'architecture':architecture,'constraint':constraint,
    'ceramic_average_volume_fraction':fbar,'thickness_m':L,
    **{k:v for k,v in r.items() if k!='layers'}})
frame=pd.DataFrame(rows);frame.to_csv(root/'phase2/results/graded_bilayer_controls.csv',index=False)
print(frame[['profile','architecture','constraint','peak_inplane_stress_MPa','heat_flux_W_m2']].to_string(index=False))
