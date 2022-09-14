# AUTOGENERATED! DO NOT EDIT! File to edit: 01_circuit.ipynb (unless otherwise specified).

__all__ = ['Circuit', 'unpack', 'partition', 'freeze', 'make_hash']

# Cell
from collections.abc import MutableSequence
from functools import lru_cache

# Cell
class Circuit(MutableSequence):
    """Representation of a quantum circuit"""

    def __init__(self, ticks=None, noisy=True):
        self._ticks = ticks if ticks else []
        self._noisy = noisy

    def __getitem__(self, tick_index):
        return self._ticks[tick_index]

    def __setitem__(self, tick_index, tick):
        self._ticks[tick_index] = tick

    def __delitem__(self, tick_index):
        del self._ticks[tick_index]

    def __len__(self):
        return len(self._ticks)

    def insert(self, tick_index, tick):
        self._ticks.insert(tick_index, tick)

    def __str__(self):
        str_list = []
        for i, tick in enumerate(self._ticks):
            str_list.append(f"{i}: {str(tick)}")
        return "\n".join(str_list)

    def __repr__(self):
        return self.__str__()

    @property
    def _qubits(self):
        """Set of qubits used in circuit"""
        return set(unpack(self._ticks))

    @property
    @lru_cache(maxsize=1)
    def n_qubits(self):
        """Number of qubits used in circuit"""
        return len(self._qubits)

    @property
    def n_ticks(self):
        """Number of ticks"""
        return len(self._ticks)

# Cell
def unpack(seq):
    """Generator for all qubits defined in a (sub)circuit"""

    if isinstance(seq, (tuple,set,list,Circuit)):
        yield from (x for y in seq for x in unpack(y))
    elif isinstance(seq, dict):
        yield from (x for v in seq.values() for y in v for x in unpack(y))
    else:
        yield seq

# Cell
def partition(circuit,gates):
    """Find all (tick,qubit) circuit locations for list of `gates`"""

    return [(t_idx,q) for (t_idx,tick) in enumerate(circuit)
            for g,qs in tick.items() for q in qs if g.upper() in gates]

# Cell
#export
def freeze(obj):
    if isinstance(obj, dict): # dicts to frozensets
        return frozenset({k:freeze(v) for k,v in obj.items()}.items())
    if isinstance(obj, (set,tuple,list)):
        return tuple([freeze(v) for v in obj]) # lists sets and tuples to tuples
    return obj # hashable object

# Cell
def make_hash(circuit):
    return hash(freeze(circuit))