# AUTOGENERATED! DO NOT EDIT! File to edit: 00_math.ipynb (unless otherwise specified).

__all__ = ['comb', 'binom', 'Wilson_var', 'Wald_var', 'std_sum']

# Cell
import numpy as np
from scipy.special import factorial

# Cell
def comb(n, k):
    """Vectorized combination"""
    return factorial(n) / (factorial(k) * factorial(n-k))

# Cell
def binom(k, n, p):
    """Vectorized binomial function"""
    return comb(n,k) * p**k * (1-p)**(n-k)

# Cell
def Wilson_var(p, N, z=1.96):
    """Wilson estimator of binomial variance"""
    # wilson_max = (p + z**2/(2*N) + z*np.sqrt(p*(1-p)/N+z**2/(4*N**2)))/(1+z**2/N)
    # wilson_min = (p + z**2/(2*N) - z*np.sqrt(p*(1-p)/N+z**2/(4*N**2)))/(1+z**2/N)
    # return (wilson_max - wilson_min) / 2 # assume symmetric C.I. => take std as half.
    return z**2 * (p*(1-p)/N + z**2/(4*N**2)) / (1+z**2/N)**2

# Cell
def Wald_var(p, N):
    """Wald estimator of binomial variance (known issues, better use Wilson)"""
    return p * (1-p) / N

# Cell
def std_sum(Aws, pws, n_samples, var=Wilson_var):
    """Standard deviation due to Gaussian error propagation of p_L."""
    return np.sqrt( np.sum( Aws**2 * var(pws,n_samples), axis=0 ) )