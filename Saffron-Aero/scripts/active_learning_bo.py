"""
Multi-Fidelity Bayesian Optimization (MFBO) configuration.
Targets the minimal interface stress and maximum cycles across thermal gradients.
"""

import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
from scipy.optimize import minimize
import warnings

# Suppress sklearn convergence warnings for surrogate loops
warnings.filterwarnings('ignore')

from scipy.stats import norm

class CostAwareMFBOSurrogate:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        self.kernel = ConstantKernel(1.0) * Matern(length_scale=1.0, nu=2.5) + WhiteKernel(noise_level=1e-5)
        self.surrogate = GaussianProcessRegressor(
            kernel=self.kernel, 
            n_restarts_optimizer=5,
            normalize_y=True  # important for numerical stability
        )
        self.X_train = []
        self.y_train = []
        self.y_best = np.inf  # tracking minimum stress (minimization problem)

    def update_model(self, X_new, y_new):
        self.X_train.append(X_new)
        self.y_train.append(y_new)
        self.y_best = min(self.y_train)
        X_arr = np.array(self.X_train)
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(-1, 1)
        self.surrogate.fit(X_arr, np.array(self.y_train))

    def expected_improvement(self, X_candidate, xi=0.01):
        """
        Standard EI for minimization.
        xi: exploration-exploitation tradeoff. 0.01 = exploit, 0.1 = explore.
        """
        mu, sigma = self.surrogate.predict(
            X_candidate.reshape(1, -1), return_std=True
        )
        sigma = sigma.reshape(-1, 1)
        mu = mu.reshape(-1, 1)

        if sigma == 0.0:
            return 0.0

        # For minimization: improvement = y_best - mu
        improvement = self.y_best - mu - xi
        Z = improvement / sigma
        ei = improvement * norm.cdf(Z) + sigma * norm.pdf(Z)
        return ei.squeeze()

    def expected_improvement_per_cost(self, X_candidate, fea_cost=1.0):
        """
        CAGES-style: EI divided by expected evaluation cost.
        fea_cost: relative cost of this fidelity level.
        Low fidelity (surrogate) = cost 1, High fidelity (FEniCS) = cost ~100.
        """
        ei = self.expected_improvement(X_candidate)
        return ei / fea_cost

    def suggest_next(self, X_candidates, fea_cost=1.0):
        """
        Given a grid of candidates, return the one with highest EI/cost.
        X_candidates: (N, D) array of candidate points
        """
        eic = np.array([
            self.expected_improvement_per_cost(x, fea_cost) 
            for x in X_candidates
        ])
        best_idx = np.argmax(eic)
        return X_candidates[best_idx], eic[best_idx]

if __name__ == "__main__":
    print("MFBO loop scaffolding standing by.")
    print("Ready to wrap around 1D FEA solver...")