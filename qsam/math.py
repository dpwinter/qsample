# AUTOGENERATED! DO NOT EDIT! File to edit: 05_math.ipynb (unless otherwise specified).

__all__ = ['comb', 'binom', 'Wilson_std', 'Wilson_var', 'Wald_var', 'Wald_std', 'std_sum']

# Cell
import numpy as np
from scipy.special import factorial

# Cell
def comb(n, k):
    """Vectorized function to calculate a combination"""
    return factorial(n) / (factorial(k) * factorial(n-k))

# Cell
def binom(k, n, p):
    """Vectorized function to calculate binomial function"""
    return comb(n,k) * p**k * (1-p)**(n-k)

# Cell
def Wilson_std(p, N, z=1.96):
    """Wilson estimator of std of binomial distribution"""
    wilson_max = (p + z**2/(2*N) + z*np.sqrt(p*(1-p)/N+z**2/(4*N**2)))/(1+z**2/N)
    wilson_min = (p + z**2/(2*N) - z*np.sqrt(p*(1-p)/N+z**2/(4*N**2)))/(1+z**2/N)
    return wilson_max - wilson_min

def Wilson_var(p, N):
    return Wilson_std(p, N)**2

# Cell
def Wald_var(p, N):
    """Wald variance estimator (known issues, better use Wilson)"""
    return p * (1-p) / N

def Wald_std(p, N):
    return np.sqrt(Wald_var(p, N))

# Cell
def std_sum(Aws, pws, n_samples, var=Wilson_var):
    """Calculate standard deviation according to Gaussian error propagation
    applied to p_L: V_L = sum_i (dp_L/dp_i)^2 * V_i"""
    return np.sqrt( np.sum( Aws[1:]**2 * var(pws[1:],n_samples), axis=0 ) )