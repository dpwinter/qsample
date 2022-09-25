# AUTOGENERATED! DO NOT EDIT! File to edit: 05b_samplers.protocol_samplers.ipynb (unless otherwise specified).

__all__ = ['ONE_QUBIT_GATES', 'TWO_QUBIT_GATES', 'GATE_GROUPS', 'Sampler', 'SubsetSampler']

# Cell
import qsam.math as math
from ..circuit import partition, make_hash, unpack
from ..fault_generators import Depolar
from ..protocol import iterate
from .sampler_mixins import SubsetAnalytics
from .datatypes import CountNode, Variable, Constant, Fail, NoFail, Tree

import numpy as np
from functools import lru_cache
from tqdm import tqdm

# Cell
ONE_QUBIT_GATES = {'H', 'X', 'Z'}
TWO_QUBIT_GATES = {'CNOT'}

GATE_GROUPS = {'p': ONE_QUBIT_GATES | TWO_QUBIT_GATES,
               'p1': ONE_QUBIT_GATES,
               'p2': TWO_QUBIT_GATES,
               }

# Cell

class Sampler:
    def __init__(self, protocol, simulator):
        self.protocol = protocol
        self.simulator = simulator
        self.n_qubits = len(set(q for c in protocol._circuits.values() for q in unpack(c)))

    def run(self, n_samples, sample_range, err_params, RSE_target=1e-1, var=math.Wilson_var, eval_fns=None, verbose=False):

        # RSE: rel. standard error target
        fail_cnts = np.zeros(len(sample_range)) # one fail counter per sample point
        partitions = {circuit_hash: [partition(circuit, GATE_GROUPS[k]) for k in err_params.keys()]
                     for circuit_hash, circuit in self.protocol._circuits.items()}

        for i,sample_pt in enumerate(sample_range): # n_samples at sample_pt

            p_phy = np.array(list(err_params.values())) * sample_pt

            for j in tqdm(range(n_samples)):

                sim = self.simulator(self.n_qubits)
                p_it = iterate(self.protocol, eval_fns)
                node = next(p_it)

                if verbose: print(f'--- Protocol run {j} ---')

                while node:

                    if not self.protocol.out_edges(node):
                        fail_cnts[i] += 1
                        break

                    circuit_hash, circuit = self.protocol.circuit_from_node(node)
                    if not circuit._noisy or circuit_hash not in partitions.keys():
                        msmt = sim.run(circuit)
                    else:
                        circuit_partitions = partitions[circuit_hash]
                        faults = Depolar.faults_from_probs(circuit_partitions, p_phy)
                        fault_circuit = Depolar.gen_circuit(len(circuit), faults)
                        msmt = sim.run(circuit, fault_circuit)
                    _node = node
                    node = p_it.send(msmt if msmt==None else int(msmt,2))

                    if verbose:
                        pauli_faults = [] if not circuit._noisy else [f'Tick {tick} :: {fault_circuit[tick]}' for tick,_ in faults]
                        if _node == 'COR': print(f"Node {_node}, Circuit {circuit} -> {node}")
                        else: print(f"Node {_node}, Faults {pauli_faults}, Measured {msmt}-> {node}")

                if j > 1:
                    p_L_j = fail_cnts[i] / j
                    if p_L_j != 0 and np.sqrt( var(p_L_j, j) )/ p_L_j < RSE_target:
                        print(f'RSE target of {RSE_target} reached.')
                        break

        p_L = fail_cnts / n_samples
        std = np.sqrt( var(p_L, n_samples) )
        return p_L, std

# Cell

class SubsetSampler(SubsetAnalytics):
    """Subset Sampler of quantum protocols"""

    def __init__(self, protocol, simulator):
        self.protocol = protocol
        self.simulator = simulator
        self.n_qubits = len(set(q for c in protocol._circuits.values() for q in unpack(c)))
        self.tree = Tree()

    def run(self, n_samples, sample_range, err_params, chi_min=1e-2, p_max=0.1, RSE_target=1e-1, ERV_sel=True, var=math.Wilson_var, eval_fns={}):

        p_phy_per_partition = np.array([[p_phy * mul for p_phy in sample_range] for mul in err_params.values()]).T
        partitions = {circuit_hash: [partition(circuit, GATE_GROUPS[k]) for k in err_params.keys()]
                      for circuit_hash, circuit in self.protocol._circuits.items() if circuit._noisy}
        w_vecs = {circuit_hash: SubsetSampler.weight_vectors([len(p) for p in pars])
                  for circuit_hash, pars in partitions.items()}
        Aws = {circuit_hash: SubsetSampler.subset_occurence(partitions[circuit_hash], w_vecs, p_phy_per_partition)
               for circuit_hash, w_vecs in w_vecs.items()}

        Aws_at_p_max = {circuit_hash: SubsetSampler.subset_occurence(partitions[circuit_hash], w_vecs, np.array(p_max))
                        for circuit_hash, w_vecs in w_vecs.items()}

        for _ in tqdm(range(n_samples)):

            chi = 1
            sim = self.simulator(self.n_qubits)
            p_it = iterate(self.protocol, eval_fns)
            node = next(p_it)
            tree_node = self.tree.add(name=node, node_cls=CountNode)
            tree_node.counts += 1

            while node:

                if not self.protocol.out_edges(node):
                    break # terminal node reached

                circuit_hash, circuit = self.protocol.circuit_from_node(node)

                if circuit_hash not in partitions.keys(): # handle circuits created at runtime
                    msmt = sim.run(circuit)
                    tree_node = self.tree.add(name=(0,),
                                              node_cls=Constant,
                                              parent=tree_node,
                                              data={'Aw': np.ones(shape=p_phy_per_partition.shape[0]),
                                                    'Aw_p_max': np.array([1])})
                else:
                    ids = np.where(chi * Aws_at_p_max[circuit_hash] > chi_min)[0]
                    if len(ids) == 0 or not circuit._noisy:
                        idx = 0
                    else:
                        delta = self.tree.delta(ckey='Aw_p_max')
                        v_L = self.tree.var(ckey='Aw_p_max')
                        p_L = self.tree.rate(ckey='Aw_p_max')

                        if not ERV_sel:
                            idx = np.random.choice(ids)
                        else:
                            erv_deltas = []
                            for idx in ids:
                                Aw = Aws[circuit_hash][idx]
                                Aw_p_max = Aws_at_p_max[circuit_hash][idx]
                                w_vec = w_vecs[circuit_hash][idx]

                                _tree_node = self.tree.add(w_vec, node_cls=Constant, parent=tree_node, data={'Aw': Aw, 'Aw_p_max': Aw_p_max})
                                __tree_node = self.tree.add('FAIL', node_cls=Fail, parent=_tree_node)
                                _delta = self.tree.delta(ckey='Aw_p_max')
                                _rate = __tree_node.rate

                                _tree_node.counts += 1
                                v_L_minus = self.tree.var(ckey='Aw_p_max')

                                __tree_node.counts += 1
                                v_L_plus = self.tree.var(ckey='Aw_p_max')

                                _v_L = _rate * v_L_plus + (1 - _rate) * v_L_minus
                                erv_delta = np.abs(v_L - _v_L) + (delta - _delta)
                                erv_deltas.append( erv_delta )

                                # revert the change
                                _tree_node.counts -= 1
                                __tree_node.counts -= 1
                                if _tree_node.counts == 0: self.tree.detach(_tree_node)
                                if __tree_node.counts == 0: self.tree.detach(__tree_node)

                            idx = np.argmax(erv_deltas)
                            idx = ids[idx]

                    Aw = Aws[circuit_hash][idx]
                    Aw_p_max = Aws_at_p_max[circuit_hash][idx]
                    w_vec = w_vecs[circuit_hash][idx]
                    chi *= Aw_p_max

                    faults = Depolar.faults_from_weights(partitions[circuit_hash], w_vec)
                    fault_circuit = Depolar.gen_circuit(len(circuit), faults)
                    msmt = sim.run(circuit, fault_circuit)

                    tree_node = self.tree.add(name=w_vec, node_cls=Constant, parent=tree_node, data={'Aw': Aw, 'Aw_p_max': Aw_p_max},
                                              deterministic=True if circuit._ff_deterministic and not any(w_vec) else False)

                tree_node.counts += 1
                node = p_it.send(msmt if msmt==None else int(msmt,2)) # exchange with iterator

                if node == None: name, node_cls = "NO FAIL", NoFail
                elif node == 'FAIL': name, node_cls = node, Fail
                else: name, node_cls = node, Variable
                tree_node = self.tree.add(name=name, node_cls=node_cls, parent=tree_node)
                tree_node.counts += 1


            if p_L > 0 and (np.sqrt(v_L) + delta) / p_L < RSE_target:
                print(f'RSE target of {RSE_target} reached.')
                break

        v_L = self.tree.var(ckey='Aw')
        p_L_low = self.tree.rate(ckey='Aw')
        p_L_low = np.zeros_like(v_L) if type(p_L_low) == int else p_L_low # if all paths fault free: return array of 0s
        p_L_up = p_L_low + self.tree.delta(ckey='Aw')

        return p_L_low, p_L_up, np.sqrt(v_L)

    def __str__(self):
        return self.tree.__str__()