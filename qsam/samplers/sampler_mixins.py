# AUTOGENERATED! DO NOT EDIT! File to edit: 05c_samplers.sampler_mixins.ipynb (unless otherwise specified).

__all__ = ['SubsetAnalytics']

# Cell
import qsam.math as math

import numpy as np
import itertools as it

# Cell

class SubsetAnalytics:
    @staticmethod
    def subset_occurence(partitions, partition_w_vecs, p_phy_per_partition):
        """Return (weight)x(p_phys) (parition) subset occurance matrix transforming p_SS vector to p_L vector"""
        n_partition_elems = np.array([len(p) for p in partitions])
        Aws = np.array([math.binom(w_vec, n_partition_elems, p_phy_per_partition) for w_vec in partition_w_vecs])
        Aws = np.product(Aws, axis=-1) # mult Aws for multi-parameter, i.e. multi-partitions
        return Aws

    @staticmethod
    def weight_vectors(w_max, w_exclude={}):
        w_exclude = set((w,) if isinstance(w, int) else w for w in w_exclude)
        w_maxs = [w_max] if isinstance(w_max, int) else w_max

        w_upto_w_maxs = [tuple(range(w_max+1)) for w_max in w_maxs]
        w_vecs = list(it.product( *w_upto_w_maxs ))
        filtered_w_vecs = [w for w in w_vecs if w not in w_exclude]
        return filtered_w_vecs