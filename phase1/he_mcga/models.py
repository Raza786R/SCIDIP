"""Fixed grouped benchmark, training-only CV and split-calibration diagnostics."""
import json
import math
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from .composition import features, vector
from .data import matrix, partition


def estimator(seed):
    return ExtraTreesRegressor(n_estimators=96,min_samples_leaf=2,max_features=1.,
                               random_state=seed,n_jobs=1)


def metrics(y,p):
    return {'n':len(y),'MAE':float(mean_absolute_error(y,p)),
            'R2':float(r2_score(y,p)) if len(y)>1 else None}


class PropertyModel:
    def __init__(self, data, target, seed=42):
        self.data = data.copy(); self.target = target; self.seed = seed
        self.data['partition'] = partition(data.composition_id,seed)
        self.X = matrix(data,target); self.y = data.target.to_numpy(float)
        self.train = np.flatnonzero(self.data.partition=='train')
        self.cal = np.flatnonzero(self.data.partition=='calibration')
        self.test = np.flatnonzero(self.data.partition=='test')
        if min(len(self.train),len(self.cal),len(self.test))<2:
            raise ValueError('insufficient non-overlapping train/calibration/test groups')
        self.model = estimator(seed).fit(self.X[self.train],self.y[self.train])
        residual = np.abs(self.y[self.cal]-self.model.predict(self.X[self.cal]))
        # One score per composition group: max residual across temperature/processing.
        scores = pd.DataFrame({'g':self.data.iloc[self.cal].composition_id.to_numpy(),'r':residual}).groupby('g').r.max().to_numpy()
        rank = math.ceil((len(scores)+1)*.9)
        # Insufficient groups for requested level => unbounded, never fake a 90% bound.
        self.radius = float(np.sort(scores)[rank-1]) if rank<=len(scores) else None
        self.cal_groups = len(scores)
        self.train_comps = np.array([vector(json.loads(c)) for c in self.data.iloc[self.train].atomic_fractions])
        unique = np.unique(self.train_comps,axis=0)
        d = cdist(unique,unique,metric='cityblock'); np.fill_diagonal(d,np.inf)
        self.domain_cutoff = float(np.quantile(d.min(axis=1),.95))
        self.temp_min = float(data.iloc[self.train].temperature_K.min()) if target=='yield' else None
        self.temp_max = float(data.iloc[self.train].temperature_K.max()) if target=='yield' else None

    def predict(self, comp, temperature_K=298.15, processing='CAST'):
        x = features(comp,temperature_K,processing,self.target=='yield').reshape(1,-1)
        pred = float(self.model.predict(x)[0])
        # Tree disagreement is a heuristic, not a posterior/coverage guarantee.
        spread = float(np.std([tree.predict(x)[0] for tree in self.model.estimators_]))
        dist = float(cdist(vector(comp)[None,:],self.train_comps,metric='cityblock').min())
        seen = (self.train_comps>0).any(axis=0)
        flags = []
        if ((vector(comp)>0)&~seen).any(): flags.append('unseen_training_element')
        if dist>self.domain_cutoff: flags.append('composition_distance_exceeds_training_95pct')
        if self.target=='yield' and not self.temp_min<=temperature_K<=self.temp_max:
            flags.append('temperature_outside_training_range')
        if self.target=='yield' and processing not in set(self.data.iloc[self.train].processing):
            flags.append('processing_not_seen_in_training')
        radius = self.radius
        return {'prediction':pred,'tree_spread':spread,'calibration_radius':radius,
                'lower':max(0.,pred-radius) if radius is not None else None,
                'upper':pred+radius if radius is not None else None,
                'nearest_training_L1':dist,'domain_cutoff_L1':self.domain_cutoff,
                'domain_flags':flags,'interval_applicable':radius is not None and not flags}

    def evaluate(self):
        p = self.model.predict(self.X[self.test]); y = self.y[self.test]
        base = DummyRegressor(strategy='median').fit(self.X[self.train],self.y[self.train])
        cv = []; train = self.train
        groups = self.data.iloc[train].composition_id.to_numpy()
        splitter = GroupKFold(n_splits=min(5,len(set(groups))))
        for fold,(a,b) in enumerate(splitter.split(self.X[train],groups=groups)):
            m = estimator(self.seed).fit(self.X[train[a]],self.y[train[a]])
            cv.append({'fold':fold,**metrics(self.y[train[b]],m.predict(self.X[train[b]])),
                       'composition_overlap':len(set(groups[a])&set(groups[b]))})
        partitions = {p:set(self.data[self.data.partition==p].composition_id) for p in ('train','calibration','test')}
        out = {'target':self.target,'units':'GPa' if self.target=='bulk' else 'MPa',
               'model':'ExtraTreesRegressor(96 trees, min_samples_leaf=2)',
               'split_policy':'SHA256(seed:composition_id) mod 10: test 0-1, calibration 2-3, train 4-9',
               'rows_by_partition':self.data.partition.value_counts().to_dict(),
               'groups_by_partition':{k:len(v) for k,v in partitions.items()},
               'composition_overlap':sum(len(partitions[a]&partitions[b]) for a,b in [('train','test'),('train','calibration'),('test','calibration')]),
               'locked_test':metrics(y,p),'median_baseline_test':metrics(y,base.predict(self.X[self.test])),
               'training_only_group_cv':cv,'calibration_groups':self.cal_groups,
               'group_max_residual_nominal_90pct_radius':self.radius,
               'test_row_interval_coverage':float(np.mean(np.abs(y-p)<=self.radius)) if self.radius is not None else None,
               'interval_limit':'Exchangeability assumed; composition distance and processing/temperature shifts invalidate coverage claims.',
               'domain_cutoff_L1':self.domain_cutoff,'training_temperature_K':[self.temp_min,self.temp_max]}
        if self.target=='yield':
            # Stronger stress test: connected components of shared composition OR
            # publication, so neither can leak across this training-only CV.
            parent = list(range(len(train)))
            def find(i):
                while parent[i]!=i:
                    parent[i]=parent[parent[i]]; i=parent[i]
                return i
            for col in ('composition_id','source'):
                seen = {}
                for i,val in enumerate(self.data.iloc[train][col]):
                    if val in seen: parent[find(i)]=find(seen[val])
                    else: seen[val]=i
            blocks = np.array([find(i) for i in range(len(train))]); n = len(set(blocks))
            pubcv = []
            if n>=2:
                for fold,(a,b) in enumerate(GroupKFold(min(5,n)).split(self.X[train],groups=blocks)):
                    m = estimator(self.seed).fit(self.X[train[a]],self.y[train[a]])
                    pubcv.append({'fold':fold,**metrics(self.y[train[b]],m.predict(self.X[train[b]]))})
            out['composition_publication_connected_blocks'] = n
            out['training_only_composition_and_publication_cv'] = pubcv
            out['qualification_limit'] = 'Compression yield only; no tensile, creep, fatigue or coating bond allowables.'
        rows = self.data.iloc[self.test][['row_id','composition_id','target','temperature_K','processing','source']].copy()
        rows['prediction']=p; rows['absolute_error']=np.abs(y-p)
        return out,rows
