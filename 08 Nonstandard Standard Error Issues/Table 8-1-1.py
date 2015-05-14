#!/usr/bin/env python
"""
Tested on Python 3.4
numpy: generate random data, manipulate arrays
statsmodels.api: estimate OLS and robust errors
tabulate: pretty print to markdown
scipy.stats: calculate distributions
"""

import numpy as np
import statsmodels.api as sm
from tabulate import tabulate
import scipy.stats

# Set seed
np.random.seed(1025)

# Set number of simulations
nsims = 2500

# Create function to create data for each run
def generateHC(sigma):
    # Set parameters of the simulation
    N   = 30
    r   = 0.9
    N_1 = int(r * 30)

    # Generate simulation data
    d = np.ones(N); d[0:N_1] = 0;

    epsilon         = np.empty(N)
    epsilon[d == 1] = np.random.normal(0, 1, N - N_1)
    epsilon[d == 0] = np.random.normal(0, sigma, N_1)

    # Run regression
    y       = 0 * d + epsilon
    X       = sm.add_constant(d)
    model   = sm.OLS(y, X)
    results = model.fit()
    b1      = results.params[1]

    # Calculate standard errors
    conventional = results.bse[1]
    hc0          = results.get_robustcov_results(cov_type = 'HC0').bse[1]
    hc1          = results.get_robustcov_results(cov_type = 'HC1').bse[1]
    hc2          = results.get_robustcov_results(cov_type = 'HC2').bse[1]
    hc3          = results.get_robustcov_results(cov_type = 'HC3').bse[1]
    return([b1, conventional, hc0, hc1, hc2, hc3])

# Create function to report simulations
def simulateHC(nsims, sigma):
    # Initialize array to save results
    simulation_results = np.empty(shape = [nsims, 6])

    # Run simulation
    for i in range(0, nsims):
        simulation_results[i, :] = generateHC(0.5)

    compare_errors     = np.maximum(simulation_results[:, 1].transpose(), simulation_results[:, 2:6].transpose()).transpose()
    simulation_results = np.concatenate((simulation_results, compare_errors), axis=1)
    test_stats         = np.tile(simulation_results[:, 0], (9, 1)).transpose() / simulation_results[:, 1:10]
    summary_reject_z   = np.mean(2 * scipy.stats.norm.cdf(-abs(test_stats)) <= 0.05, axis = 0).transpose()
    summary_reject_t   = np.mean(2 * scipy.stats.t.cdf(-abs(test_stats), df = 30 - 2) <= 0.05, axis = 0).transpose()
    summary_reject_z   = np.concatenate([[np.nan], summary_reject_z]).transpose()
    summary_reject_t   = np.concatenate([[np.nan], summary_reject_t]).transpose()

    summary_mean  = np.mean(simulation_results, axis = 0).transpose()
    summary_std   = np.std(simulation_results, axis = 0).transpose()
    summary_stats = np.column_stack((summary_mean, summary_std, summary_reject_z, summary_reject_t))
    return(tabulate(summary_stats))

print(simulateHC(nsims, 0.5))
print(simulateHC(nsims, 0.85))
print(simulateHC(nsims, 0.1))
# End of script