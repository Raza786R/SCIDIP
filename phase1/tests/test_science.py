"""Analytical invariants and regression checks for scientific failure modes."""
import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
from he_mcga.composition import fractions,parse_stoichiometry,composition_id,descriptors
from he_mcga.data import curate,partition
from he_mcga.models import PropertyModel
from he_mcga.thermal import laminate,CERAMICS
from he_mcga.search import chemical_constraints,pareto_mask
from he_mcga.applications import centrifugal_root_stress_MPa,tooling_economics
from he_mcga.__main__ import validate_config,ROOT


class CompositionTests(unittest.TestCase):
    def test_unknown_element_never_dropped(self):
        for value in ['NbMoAl0.028','NbMo???','NbMo wt%','Nb1Nb1','Nb-1Mo2','']:
            with self.subTest(value=value),self.assertRaises(ValueError): parse_stoichiometry(value)

    def test_rounded_recipe_never_silently_repaired(self):
        for comp in [{'Nb':.5,'Mo':.492},{'Nb':1.01,'Mo':-.01},{'Nb':float('nan')},{'Al':1}]:
            with self.assertRaises(ValueError): fractions(comp)

    def test_stoichiometry_and_reordering(self):
        a=parse_stoichiometry('Nb2 Mo2'); b=parse_stoichiometry('Mo0.5Nb0.5')
        self.assertEqual(composition_id(a),composition_id(b))
        self.assertAlmostEqual(a['Nb'],.5)

    def test_atomic_density_uses_molar_volume(self):
        d=descriptors({'Mo':.5,'Nb':.5})
        expected=(95.95+92.91)/(95.95/10.2+92.91/8.6)
        self.assertAlmostEqual(d['density_g_cm3'],expected)
        self.assertAlmostEqual(sum(d['mass_fractions'].values()),1)
        self.assertAlmostEqual(sum(d['volume_fractions'].values()),1)

    def test_missing_binary_pair_is_unknown(self):
        self.assertIsNone(descriptors({'Ti':.5,'Nb':.5})['hmix_kJ_mol'])
        self.assertEqual(descriptors({'Nb':.5,'Ta':.5})['hmix_kJ_mol'],0)


class ThermalTests(unittest.TestCase):
    def test_identical_material_linear_gradient_free_plate_zero_stress(self):
        c=CERAMICS['LZO']
        r=laminate(c['E_Pa'],c['alpha_1_K'],c['k_W_mK'],metal_nu=c['nu'])
        self.assertLess(r['peak_inplane_stress_MPa'],1e-7)
        self.assertAlmostEqual(r['heat_flux_W_m2'],c['k_W_mK']*(1400-300)/.005)
        self.assertAlmostEqual(r['metal_face_K'],300)
        self.assertAlmostEqual(r['ceramic_face_K'],1400)

    def test_no_temperature_change_no_stress(self):
        r=laminate(100e9,5e-6,50,cold_face_K=300,hot_face_K=300)
        self.assertLess(r['peak_inplane_stress_MPa'],1e-8)

    def test_force_and_moment_equilibrium(self):
        r=laminate(100e9,5e-6,50,membrane_N_m=1200,moment_N=5)
        self.assertLess(abs(r['force_residual_N_m']),1e-5)
        self.assertLess(abs(r['moment_residual_N']),1e-7)

    def test_flat_constraint_has_reaction_not_free_curvature(self):
        a=laminate(100e9,5e-6,50,constraint='free_curvature')
        b=laminate(100e9,5e-6,50,constraint='flat_force_free')
        self.assertEqual(b['curvature_1_m'],0)
        self.assertIsNone(b['moment_residual_N'])
        self.assertIsNotNone(b['flat_reaction_moment_N'])
        self.assertGreater(b['peak_inplane_stress_MPa'],a['peak_inplane_stress_MPa'])

    def test_mesh_and_recipe_dimensions(self):
        a=laminate(100e9,5e-6,50,cells=160)
        b=laminate(100e9,5e-6,50,cells=320)
        self.assertLess(abs(a['peak_inplane_stress_MPa']/b['peak_inplane_stress_MPa']-1),.02)
        layers=laminate(100e9,5e-6,50,cells=11)['layers']
        self.assertAlmostEqual(sum(l['z_end_m']-l['z_start_m'] for l in layers),.005)
        self.assertAlmostEqual(sum(l['ceramic_volume_fraction'] for l in layers)/11,.5)
        for i,l in enumerate(layers):
            self.assertAlmostEqual(l['ceramic_volume_fraction']+l['metal_volume_fraction'],1)
            if i: self.assertEqual(l['z_start_m'],layers[i-1]['z_end_m'])

    def test_invalid_inputs(self):
        for kwargs in [{'E_Pa':-1},{'exponent':0},{'cells':1},{'constraint':'unspecified'},
                       {'constraint':'flat_force_free','moment_N':1}]:
            args={'E_Pa':100e9,'alpha_1_K':5e-6,'k_W_mK':50,**kwargs}
            with self.assertRaises((ValueError,KeyError)): laminate(**args)


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bulk,_,_=curate(ROOT,'bulk')
        cls.model=PropertyModel(cls.bulk,'bulk')

    def test_source_not_corrupted_processed_properties(self):
        self.assertTrue((self.bulk.target>0).all())
        self.assertFalse((self.bulk.formula_source=='TiVW').any())
        self.assertEqual(len(self.bulk),43)

    def test_train_calibration_test_have_zero_composition_overlap(self):
        d=self.model.data
        sets=[set(d[d.partition==p].composition_id) for p in ('train','calibration','test')]
        for i,a in enumerate(sets):
            for b in sets[i+1:]: self.assertFalse(a&b)

    def test_small_calibration_is_unbounded_not_fake_interval(self):
        self.assertIsNone(self.model.radius)
        p=self.model.predict(parse_stoichiometry('NbMo'))
        self.assertIsNone(p['lower']); self.assertFalse(p['interval_applicable'])

    def test_partition_stable_as_new_data_arrives(self):
        a=self.bulk.composition_id.to_numpy()
        np.testing.assert_array_equal(partition(a),partition(np.concatenate([a,['new']]))[:-1])


class OptimizationApplicationTests(unittest.TestCase):
    def test_hard_constraints_reject_single_element(self):
        cfg=json.loads((ROOT/'phase1/configs/aerospace_legacy_K.json').read_text())
        reasons,_=chemical_constraints({'Nb':1},cfg['constraints'])
        self.assertIn('fewer_than_5_elements_at_5atpct',reasons)
        self.assertIn('element_above_max_atomic_fraction',reasons)

    def test_pareto(self):
        np.testing.assert_equal(pareto_mask([[1,2],[2,1],[2,3],[1,2]]),[True,True,False,True])

    def test_rotating_load_has_correct_units(self):
        self.assertEqual(centrifugal_root_stress_MPa(8,0,.1,.2),0)
        a=centrifugal_root_stress_MPa(8,1000,.1,.2)
        self.assertAlmostEqual(centrifugal_root_stress_MPa(8,2000,.1,.2),4*a)

    def test_economics_no_savings_no_payback(self):
        r=tooling_economics(1000000,50000,100000,50000,120000,500000)
        self.assertLess(r['annual_tooling_difference_INR'],0)
        self.assertIsNone(r['simple_pilot_payback_years'])

if __name__=='__main__': unittest.main()
