# AUTOGENERATED! DO NOT EDIT! File to edit: 01_circtools.ipynb (unless otherwise specified).

__all__ = ['unpack', 'partition']

# Cell
def unpack(seq):
    """Generator for all qubits defined in a (sub)circuit"""

    if isinstance(seq, (tuple,set,list)):
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