"""Exact workflow diagrams and plots derived from current checked results."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
root=Path(__file__).resolve().parents[2];out=root/'phase2/assets';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
BLUE='#28516B';PALE='#EAF0F4';GRAY='#4B5560'

def flow(name,nodes,edges,size):
 fig,ax=plt.subplots(figsize=size);ax.set_xlim(0,10);ax.set_ylim(0,7);ax.axis('off')
 for key,(x,y,label,external) in nodes.items():
  p=FancyBboxPatch((x-1.4,y-.48),2.8,.96,boxstyle='round,pad=0.06',facecolor='white' if external else PALE,
                   edgecolor=GRAY,linestyle='--' if external else '-',linewidth=1.2);ax.add_patch(p)
  ax.text(x,y,label,ha='center',va='center',fontsize=12,color='black')
 for a,b,dashed in edges:
  x,y,*_=nodes[a];xx,yy,*_=nodes[b];dx=xx-x;dy=yy-y
  if abs(dx)>abs(dy):start=(x+np.sign(dx)*1.47,y);end=(xx-np.sign(dx)*1.47,yy)
  else:start=(x,y+np.sign(dy)*.55);end=(xx,yy-np.sign(dy)*.55)
  ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=13,lw=1.2,color=GRAY,linestyle='--' if dashed else '-'))
 fig.savefig(out/name,dpi=220,bbox_inches='tight',facecolor='white');plt.close(fig)
flow('system_workflow.png',{
 'a':(1.7,6,'Sources and\nstrict curation',False),'b':(5,6,'Train and calibrate\nproperty models',False),'c':(8.3,6,'Protected test\nevaluation',False),
 'd':(1.7,3.9,'Thermal laminate\nand constraints',False),'e':(5,3.9,'Joint chemistry and\ngradient search',False),'f':(8.3,3.9,'Candidates and\ncoupon designs',False),
 'g':(8.3,1.7,'Manufacture and\ncharacterize externally',True),'h':(5,1.7,'Validate feedback\nand retrain models',False)},
 [('a','b',False),('b','c',False),('b','e',False),('d','e',False),('e','f',False),('f','g',True),('g','h',True),('h','e',False)],(9.5,5.1))
# Explicit return to training is shown separately without crossing the model diagram.
flow('feedback_workflow.png',{
 'a':(1.7,5.9,'Propose candidates\nwith partition roles',False),'b':(5,5.9,'Make specimens\nand measure externally',True),'c':(8.3,5.9,'Record actual chemistry\nunits and report evidence',False),
 'd':(8.3,3.4,'Validation gate\nreject invalid records',False),'e':(5,3.4,'Training eligible\nappend and retrain',False),'f':(1.7,3.4,'New model generation\nand next proposals',False),
 'g':(8.3,1.2,'Protected groups\nexternal validation only',False)},
 [('a','b',True),('b','c',True),('c','d',False),('d','e',False),('e','f',False),('d','g',False)],(9.5,4.7))
p=root/'phase2/results/aerospace_v2';recipe=pd.read_csv(p/'coupon_recipe_11_layers.csv')
fig,axes=plt.subplots(1,2,figsize=(8,4.8),gridspec_kw={'width_ratios':[1.2,1]})
z=(recipe.z_start_m+recipe.z_end_m)*500;h=(recipe.z_end_m-recipe.z_start_m)*1000
axes[0].barh(z,recipe.metal_volume_fraction,height=h,color='#ACB8C1',edgecolor='white',label='Metal')
axes[0].barh(z,recipe.ceramic_volume_fraction,left=recipe.metal_volume_fraction,height=h,color=BLUE,edgecolor='white',label='LZO')
axes[0].set(xlabel='Phase volume fraction',ylabel='Depth from cold metal face in mm',xlim=(0,1));axes[0].legend(loc='upper center',bbox_to_anchor=(.5,1.18),ncol=2,frameon=False)
axes[1].plot(recipe.temperature_center_K,z,'o-',color=BLUE,lw=1.7);axes[1].set(xlabel='Modeled layer center temperature in K',ylabel='Depth in mm')
fig.tight_layout();fig.savefig(out/'architecture.png',dpi=230,bbox_inches='tight',facecolor='white');plt.close(fig)
controls=pd.read_csv(root/'phase2/results/graded_bilayer_controls.csv')
fig,axes=plt.subplots(1,2,figsize=(8,3.8))
for ax,profile,title in zip(axes,['aerospace_v2','sona_v2'],['Aerospace face profile','Sona coupon hypothesis']):
 for j,(arch,color) in enumerate([('graded',BLUE),('sharp_bilayer','#AFB8BF')]):
  rows=controls[(controls.profile==profile)&(controls.architecture==arch)]
  vals=[rows[rows.constraint==c].peak_inplane_stress_MPa.iloc[0] for c in ['free_curvature','flat_force_free']]
  ax.bar(np.arange(2)+(j-.5)*.32,vals,.32,label='Graded' if arch=='graded' else 'Sharp',color=color)
 ax.set_xticks([0,1],['Free curvature','Held flat']);ax.set_title(title,fontsize=11);ax.set_ylabel('Peak in plane stress in MPa');ax.legend(frameon=False,fontsize=9)
fig.tight_layout();fig.savefig(out/'control_comparison.png',dpi=230,bbox_inches='tight',facecolor='white');plt.close(fig)
