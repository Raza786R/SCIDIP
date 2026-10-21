import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from he_mcga.composition import composition_id,parse_stoichiometry
from he_mcga.data import partition
from he_mcga.feedback import ingest,augment
from he_mcga.calphad import equilibrate
from he_mcga.__main__ import ROOT


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'phase1')
        self.folder=Path(self.temp.name)
        self.evidence=self.folder/'lab.txt'
        self.evidence.write_text('TEST FIXTURE ONLY: verifies ingestion, not a real experiment.\n')
        self.comp=None
        for i in range(1,100):
            c={'Nb':i/100,'Mo':1-i/100}
            if partition([composition_id(c)])[0]=='train': self.comp=c; break
        self.record={'measurement_id':'test_fixture_1','atomic_fractions':self.comp,
          'property':'compression_yield','value':500,'unit':'MPa','temperature_K':1000,
          'test_mode':'compression','processing':'CAST','source':'unit-test-fixture',
          'specimen_id':'fixture-specimen','evidence_path':str(self.evidence.relative_to(ROOT)),
          'evidence_sha256':hashlib.sha256(self.evidence.read_bytes()).hexdigest(),
          'measurement_uncertainty':10,'is_synthetic':False}
        # False is exercised only in a temporary test ledger; never committed as
        # an experimental run or used in any reported model/candidate result.
        self.path=self.folder/'input.json'; self.ledger=self.folder/'ledger.json'

    def tearDown(self): self.temp.cleanup()

    def call(self, records=None):
        self.path.write_text(json.dumps(records or [self.record]))
        return ingest(self.path,self.ledger,ROOT)

    def test_valid_fixture_then_duplicate_rejected(self):
        self.assertEqual(self.call(),1)
        before=self.ledger.read_bytes()
        with self.assertRaises(ValueError): self.call()
        self.assertEqual(self.ledger.read_bytes(),before)

    def test_synthetic_rejected(self):
        self.record['is_synthetic']=True
        with self.assertRaisesRegex(ValueError,'synthetic'): self.call()
        self.assertFalse(self.ledger.exists())

    def test_bad_unit_and_nonfinite_and_missing_evidence(self):
        for field,value in [('unit','Pa'),('value',float('nan')),('evidence_sha256','wrong')]:
            record={**self.record,field:value}
            with self.subTest(field=field),self.assertRaises(ValueError): self.call([record])

    def test_protected_composition_rejected(self):
        for i in range(1,100):
            c={'Nb':i/100,'Mo':1-i/100}
            if partition([composition_id(c)])[0]!='train': self.record['atomic_fractions']=c; break
        with self.assertRaisesRegex(ValueError,'protected'): self.call()

    def test_all_or_nothing_batch(self):
        with self.assertRaises(ValueError): self.call([self.record,{**self.record,'measurement_id':'two','unit':'bad'}])
        self.assertFalse(self.ledger.exists())

    def test_changed_evidence_rejected_on_retraining(self):
        import pandas as pd
        self.call(); self.evidence.write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed'): augment(pd.DataFrame(),self.ledger,'yield',42,ROOT)


class CalphadTests(unittest.TestCase):
    def test_missing_database_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'absent'): equilibrate('/nonexistent.tdb',{'NB':1},[1000],'citation')

    def test_real_binary_equilibrium_integration(self):
        try: import pycalphad
        except ImportError: self.skipTest('optional pycalphad is not installed')
        path=Path(pycalphad.__file__).parent/'tests/databases/alni_dupin_2001.tdb'
        if not path.is_file(): self.skipTest('pycalphad test database unavailable')
        r=equilibrate(path,{'AL':.1,'NI':.9},[1000.,1600.],
            'pycalphad distributed integration-test Al-Ni database; NOT target-alloy evidence')
        for item in r['results']: self.assertAlmostEqual(sum(item['phase_mole_fractions'].values()),1)
        self.assertEqual(r['dependent_component'],'NI')
        with self.assertRaisesRegex(ValueError,'lacks'): equilibrate(path,{'NB':.5,'NI':.5},[1000],'fixture')

if __name__=='__main__': unittest.main()
