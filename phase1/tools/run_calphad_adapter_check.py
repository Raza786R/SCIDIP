"""Reproduce a real binary equilibrium integration check, not HE-MCGA evidence."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from he_mcga.calphad import equilibrate


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);a=p.parse_args()
    import pycalphad
    database=Path(pycalphad.__file__).parent/'tests/databases/alni_dupin_2001.tdb'
    output=Path(a.output)
    if output.exists(): p.error('output already exists')
    r=equilibrate(database,{'AL':.1,'NI':.9},[1000.,1600.],
       'pycalphad distributed alni_dupin_2001.tdb (Dupin et al. assessment); used only as a software integration fixture')
    r['purpose']='Adapter integration check ONLY. Al-Ni is outside HE-MCGA search; no target-alloy phase claim.'
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(r,indent=2)+'\n')
    print(output)

if __name__=='__main__': main()
