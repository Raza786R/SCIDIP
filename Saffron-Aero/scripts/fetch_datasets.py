import os
import requests
import pandas as pd
import time
from traceback import print_exc

# Elements for our High-Entropy Alloy
ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']
COMMA_ELEMENTS = ','.join(ELEMENTS)
HYPHEN_ELEMENTS = '-'.join(ELEMENTS)

def get_mp_key():
    return "nREzcJl7KZF5PZl1FIXCMbCSTbxQ55Ii"

def fetch_materials_project():
    print("Fetching from Materials Project...")
    key = get_mp_key()
    if not key:
        print("Skipping MP: No valid API key found in api.txt or apikeys.txt")
        return pd.DataFrame()
    
    try:
        from mp_api.client import MPRester
        import itertools
        
        # Build all valid combinations of strictly these 5 elements for the 'chemsys' query
        chemsys_list = []
        for i in range(1, 6):
            for c in itertools.combinations(ELEMENTS, i):
                chemsys_list.append("-".join(sorted(c)))
                
        with MPRester(key) as mpr:
            results = mpr.materials.summary.search(
                chemsys=chemsys_list,
                fields=[
                    'material_id', 'formula_pretty', 'formation_energy_per_atom',
                    'energy_above_hull', 'bulk_modulus', 'shear_modulus',
                    'density', 'volume'
                ]
            )
        
        data = []
        for r in results:
            data.append({
                'formula': r.formula_pretty,
                'formation_energy': getattr(r, 'formation_energy_per_atom', None),
                'energy_hull': getattr(r, 'energy_above_hull', None),
                    'bulk_modulus': r.bulk_modulus.get('vrh', None) if isinstance(r.bulk_modulus, dict) else (getattr(r.bulk_modulus, 'vrh', None) if r.bulk_modulus else None),
                    'shear_modulus': r.shear_modulus.get('vrh', None) if isinstance(r.shear_modulus, dict) else (getattr(r.shear_modulus, 'vrh', None) if r.shear_modulus else None),
                'density': getattr(r, 'density', None),
                'source': 'materials_project'
            })
        df = pd.DataFrame(data)
        
        # STRICT FILTER: Make sure the formula is composed ONLY of our 5 required elements
        if not df.empty:
            df = df[df['formula'].apply(is_allowed)]
            print(f"Materials Project final count (after strict filtering): {len(df)}")
            df.to_csv('raw_materials_project.csv', index=False)
        return df
    except ImportError:
        print("Skipping MP: mp-api not installed. Run: pip install mp-api")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching from MP: {e}")
        return pd.DataFrame()

def fetch_aflow():
    print("Fetching from AFLOW...")
    url = 'http://aflow.org/API/aflowlib.php'
    params = {
        'species': COMMA_ELEMENTS,
        'format': 'json',
        'properties': 'compound,energy_atom,density,elastic_moduli_values'
    }
    try:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    # Sometimes AFLOW returns dict if error, just fallback
                    df = pd.DataFrame([data])
                else:
                    df = pd.DataFrame()
            except BaseException:
                df = pd.DataFrame()
            
            if not df.empty:
                df.rename(columns={'compound': 'formula', 'energy_atom': 'formation_energy'}, inplace=True)
                df['source'] = 'aflow'
                print(f"AFLOW raw count: {len(df)}")
                df.to_csv('raw_aflow.csv', index=False)
                return df
        print(f"AFLOW failed with status {response.status_code}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching from AFLOW: {e}")
        return pd.DataFrame()

def is_allowed(formula):
    import re
    ALLOWED_ELEMENTS = {'Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf'}
    matches = set(re.findall(r'([A-Z][a-z]*)', str(formula)))
    # Ensure it's not empty and only contains allowed elements
    return bool(matches) and matches.issubset(ALLOWED_ELEMENTS)

def fetch_oqmd():
    print("Fetching from OQMD...")
    # NOTE: The word document stated `oqmdapi/formationenthalpy` which is deprecated/404.
    # The api.txt correctly points to `oqmdapi/formationenergy`.
    url = 'http://oqmd.org/oqmdapi/formationenergy'
    params = {
        'fields': 'name,entry_id,delta_e,stability,band_gap,ntypes,volume',
        'filter': 'element_set=(Mo-Nb-Ta-W-Cr)',
        'limit': 1000,
        'offset': 0
    }
    all_oqmd = []
    
    while True:
        try:
            response = requests.get(url, params=params, timeout=60)
            if response.status_code != 200:
                print(f"OQMD Endpoint failed with status {response.status_code}")
                break
                
            data = response.json()
            batch = data.get('data', [])
            if not batch: 
                break
                
            all_oqmd.extend(batch)
            if not data.get('meta', {}).get('more_data_available', False):
                break
                
            params['offset'] += params['limit']
            print(f"OQMD fetched so far: {len(all_oqmd)}")
            time.sleep(1) # Courtesy sleep
        except Exception as e:
            print(f"Error fetching from OQMD: {e}")
            break
            
    df = pd.DataFrame(all_oqmd)
    if not df.empty:
        # Standardize
        df.rename(columns={'name': 'formula', 'delta_e': 'formation_energy', 'stability': 'energy_hull'}, inplace=True)
        df['source'] = 'oqmd'
        
        # STRICT FILTER: Ensure only combinations of the 5 requested HEA elements are kept 
        df = df[df['formula'].apply(is_allowed)]
        
        print(f"OQMD final count (after strict filtering): {len(df)}")
        df.to_csv('raw_oqmd.csv', index=False)
    return df

def fetch_jarvis():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("Fetching from JARVIS-DFT (OPTIMADE)...")
    url = "https://jarvis.nist.gov/optimade/jarvisdft/v1/structures"
    all_jarvis = []
    # We query elements containing HEA targets, then strictly filter in python
    params = {"page_limit": 100}
    
    # Simple query fetching bulk chunk instead of complex filters since OPTIMADE parsing is strict
    try:
        resp = requests.get(url, params={"filter": 'elements HAS ANY "Mo", "Nb", "Ta", "W", "Cr"', "page_limit": 100}, verify=False, timeout=30)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            for item in data:
                attr = item.get('attributes', {})
                all_jarvis.append({
                    'formula': attr.get('chemical_formula_reduced'),
                    'formation_energy': attr.get('_jarvis_dft_formation_energy_per_atom'),
                    'density': attr.get('density'),
                    'volume': attr.get('cartesian_site_positions', []), # can derive volume/len
                    'bulk_modulus': attr.get('_jarvis_dft_bulk_modulus_kv'),
                    'shear_modulus': attr.get('_jarvis_dft_shear_modulus_gv')
                })
    except Exception as e:
        print(f"Error fetching from JARVIS: {e}")
        
    df = pd.DataFrame(all_jarvis)
    if not df.empty:
        df['source'] = 'jarvis'
        df = df[df['formula'].apply(is_allowed)]
        print(f"JARVIS final count (after strict filtering): {len(df)}")
        df.to_csv('raw_jarvis.csv', index=False)
    return df

def main():
    print("Starting combined dataset extraction...")
    
    df_mp = fetch_materials_project()
    df_aflow = fetch_aflow()
    df_oqmd = fetch_oqmd()
    df_jarvis = fetch_jarvis()
    
    dfs = [df for df in [df_mp, df_aflow, df_oqmd, df_jarvis] if not df.empty]
    
    if dfs:
        df_combined = pd.concat(dfs, ignore_index=True)
        df_combined.to_csv('combined_raw_data.csv', index=False)
        print(f"\\nSUCCESS: Created combined_raw_data.csv with {len(df_combined)} total materials.")
    else:
        print("\\nWARNING: No data was retrieved from any source.")

if __name__ == "__main__":
    main()