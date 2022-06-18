# AUTOGENERATED! DO NOT EDIT! File to edit: 06_samplers.ipynb (unless otherwise specified).

__all__ = ['ONE_QUBIT_GATES', 'TWO_QUBIT_GATES', 'GATE_GROUPS', 'Sampler', 'DirectSampler', 'uniform_select',
           'ERV_select', 'calc_w_max', 'calc_subset_occurances', 'SubsetSampler']

# Cell
import qsam.math as math
from .circuit import partition
from .simulators.chp import CHP
from .fault_generators import Depolar

import numpy as np
import itertools as it

# Cell
ONE_QUBIT_GATES = {'H', 'X', 'Z'}
TWO_QUBIT_GATES = {'CNOT'}

GATE_GROUPS = {'p': ONE_QUBIT_GATES | TWO_QUBIT_GATES,
               'p1': ONE_QUBIT_GATES,
               'p2': TWO_QUBIT_GATES }

# Cell
class Sampler:
    """Sampler base class"""

    def __init__(self, circuit, err_params):
        self.circuit = circuit
        self.n_qubits = circuit.n_qubits
        self.partitions = [partition(circuit, GATE_GROUPS[g]) for g in err_params.keys()]
        self.p_phys_mat = np.vstack(list(err_params.values())).T # p_phy_range x partitions
        self.fault_gen = Depolar(n_ticks=len(circuit))

    def _sample(self, params):
        sim = CHP(self.n_qubits)
        fault_circuit = self.fault_gen.generate(self.partitions, params, type(self).__name__)
        return sim.run(self.circuit, fault_circuit)

    def _check_logical_failure(self, msmt):
        return 1 if msmt.items() <= self.circuit.failures.items() else 0

# Cell
class DirectSampler(Sampler):
    """Direct Monte Carlo sampler"""

    def run(self, n_samples=100, var=math.Wilson_var):
        fail_cnts = np.zeros((self.p_phys_mat.shape[0])) # one fail counter per p_phys

        for i, p_phys in enumerate(self.p_phys_mat):
            for _ in range(n_samples):
                msmt = self._sample(p_phys)
                fail_cnts[i] += self._check_logical_failure(msmt)

        p_L = fail_cnts / n_samples
        std = np.sqrt( var(p_L, n_samples) )
        return p_L, std

# Cell
#export
def uniform_select(counts, *args, **kwargs):
    """Return index of least sampled SS"""
    # return np.argmin(counts)
    return counts.argmin()

def ERV_select(counts, fail_counts, Aw=1, var=math.Wilson_var, *args, **kwargs):
    """Return index of SS which yields maximum ERV"""

    p = fail_counts / counts # list of SS failure rates
    v = var(p, counts) # list of variances

    # prospective failure rates
    p_p = (fail_counts+1) / (counts+1) # next msmt yields +1 (i.e. 1)
    p_m = fail_counts / (counts+1) # next msmt yields -1 (i.e. 0)

    # prospective variances
    v_p = var(p_p, counts+1)
    v_m = var(p_m, counts+1)

    # expectation value of prospective variances
    v_prop = p*v_p + (1-p)*v_m

    # maximize difference (scaled by occurance prob)
    delta = Aw**2 * (v - v_prop)
    # return np.argmax(delta)
    return delta.argmax()

# Cell
#export
def calc_w_max(p_max, delta_max, n_partition_elems):
    """Calculate weight cutoff at p_max for delta_max"""

    delta = 1
    for w_max in range(n_partition_elems+1):
        delta -= math.binom(w_max, n_partition_elems, p_max)
        if delta < delta_max:
            break
    return w_max

def calc_subset_occurances(partitions, partition_weight_vecs, p_phys_mat):
    """Calculate 3D tensor of binom. coefficients for each partition"""

    n_partition_elems = np.array([len(p) for p in partitions])
    Aws = np.array([math.binom(w_vec, n_partition_elems, p_phys_mat) for w_vec in partition_weight_vecs])
    Aws = np.product(Aws, axis=-1) # get list of Aw for each partition SS combination
    return Aws

# Cell
class SubsetSampler(Sampler):
    """Monte Carlo subset sampler"""

    def __init__(self, circuit, err_params, w_params, subset_select_fn=uniform_select):
        super().__init__(circuit, err_params)
        self.subset_select_fn = subset_select_fn

        if 'w_max' in w_params:
            w_max_vec = w_params['w_max']
        elif 'p_max' in w_params and 'delta_max' in w_params:
            w_max_vec = [calc_w_max(p,d,len(par)) for p,d,par in zip(w_params['p_max'],w_params['delta_max'],self.partitions)]
        else:
            raise Exception(f"Cannot process setup parameters {w_params}.")

        # Not ideal: Calculate Aws for all w_vecs and later for w_vecs with exclusion.
        w_upto_w_maxs = [tuple(range(w_max+1)) for w_max in w_max_vec] # tuples of ranges upto w_max
        w_vecs = list(it.product( *w_upto_w_maxs )) # all weight vector combinations
        self.Aws_upper = 1 - np.sum(calc_subset_occurances(self.partitions, w_vecs, self.p_phys_mat), axis=0) # calc. upper bound for binomal weights

        w_exclude = w_params.get('w_exclude', set())
        w_exclude = set((w,) if type(w)==int else w for w in w_exclude) # convert ints to tuple for single-parameter case
        self.w_vecs = [w_vec for w_vec in it.product( *w_upto_w_maxs ) if w_vec not in w_exclude]
        self.Aws = calc_subset_occurances(self.partitions, self.w_vecs, self.p_phys_mat) # Aws with exclusion

        print(f"Setup sampling of partitions {list(err_params.keys())} with maximum fault weights {w_max_vec} and excluded weights {w_exclude}.")


    def run(self, n_samples=100, var=math.Wilson_var):

        print(f"Start sampling of {n_samples} samples using {self.subset_select_fn.__name__} as subset selector.")

        cnts      = np.zeros((len(self.w_vecs))) + 1 # one virtual sample to avoid div0
        fail_cnts = np.zeros((len(self.w_vecs)))

        for i in range(n_samples):
            idx = self.subset_select_fn(cnts, fail_cnts, Aw=np.sum(self.Aws,axis=1)) # TODO: Aw for ERV should be first selected Aw, not sum
            w_vec = self.w_vecs[idx]
            msmt = self._sample(w_vec)
            fail_cnts[idx] += self._check_logical_failure(msmt)
            cnts[idx] += 1
        pws = (fail_cnts / (cnts-1))[:,None]

        p_L_low = np.sum(self.Aws * pws, axis=0)
        p_L_up = p_L_low + self.Aws_upper
        std = math.std_sum(self.Aws, pws, n_samples, var)

        print(f"Finished sampling. Subset error rates: {pws.T}")

        return p_L_up, p_L_low, std