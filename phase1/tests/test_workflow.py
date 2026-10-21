"""Integration: deterministic run, evidence artifacts, protected feedback retrain."""
import argparse
import contextlib
import io
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from he_mcga.__main__ import run,ROOT
from he_mcga.data import curate
from he_mcga.models import PropertyModel
from he_mcga.feedback import augment


class WorkflowTests(unittest.TestCase):
    def test_small_run_is_reproducible_and_outputs_are_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            cfg=json.loads((ROOT/'phase1/configs/aerospace_legacy_K.json').read_text())
            cfg.update(iterations=0,population_multiplier=3)
            conf=folder/'input.json';conf.write_text(json.dumps(cfg))
            for name in ('a','b'):
                with contextlib.redirect_stdout(io.StringIO()):
                    run(argparse.Namespace(config=conf,output=folder/name,feedback=None))
            for name in ('all_evaluations.csv','shortlist.csv','metrics.json','coupon_recipe_11_layers.csv'):
                self.assertEqual((folder/'a'/name).read_bytes(),(folder/'b'/name).read_bytes())
            manifest=json.loads((folder/'a/manifest.json').read_text())
            for name,digest in manifest['artifact_sha256'].items():
                self.assertEqual(hashlib.sha256((folder/'a'/name).read_bytes()).hexdigest(),digest)
            feasible=pd.read_csv(folder/'a/feasible_candidates.csv')
            self.assertTrue((feasible.heat_flux_W_m2<=cfg['constraints']['max_heat_flux_W_m2']).all())
            for raw in feasible.atomic_fractions:
                comp=json.loads(raw)
                self.assertAlmostEqual(sum(comp.values()),1,places=12)
                self.assertGreaterEqual(sum(v>=.05-1e-12 for v in comp.values()),5)
                self.assertLessEqual(max(comp.values()),.35)
            with self.assertRaisesRegex(ValueError,'already exists'):
                run(argparse.Namespace(config=conf,output=folder/'a',feedback=None))

    def test_augmentation_retrains_without_changing_protected_rows(self):
        # Temporary controlled perturbation tests code response, not real science.
        data,_,_=curate(ROOT,'yield'); before=PropertyModel(data,'yield')
        selected=before.data[before.data.partition=='train'].iloc[0]
        row={'measurement_id':'temporary-unit-fixture','atomic_fractions':json.loads(selected.atomic_fractions),
             'target_name':'yield','value':selected.target+500,'temperature_K':selected.temperature_K,
             'processing':selected.processing,'source':'TEMPORARY TEST FIXTURE','is_synthetic':False}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'fixture.json';path.write_text(json.dumps([row]))
            after=PropertyModel(augment(data,path,'yield'),'yield')
        for partition in ('test','calibration'):
            pd.testing.assert_frame_equal(before.data[before.data.partition==partition].reset_index(drop=True),
                                           after.data[after.data.partition==partition].reset_index(drop=True),check_dtype=False)
        self.assertEqual(len(after.train),len(before.train)+1)
        self.assertFalse(np.array_equal(before.model.predict(before.X[before.test]),after.model.predict(after.X[before.test])))

    def test_old_optimizer_cannot_emit_legacy_safety_claims(self):
        result=subprocess.run([sys.executable,str(ROOT/'Saffron-Aero/scripts/differential_evolution_search.py')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('superseded',result.stderr)
        self.assertNotIn('Max achieved Safety Factor',result.stdout)

if __name__=='__main__': unittest.main()
