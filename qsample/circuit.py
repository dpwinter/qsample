# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_circuit.ipynb.

# %% auto 0
__all__ = ['GATES', 'unpack', 'draw_circuit', 'Circuit']

# %% ../nbs/03_circuit.ipynb 3
from collections.abc import MutableSequence
from functools import cached_property
from hashlib import sha1
import latextools

# %% ../nbs/03_circuit.ipynb 4
GATES = {
    "init": {"init"},
    "q1": {"I", "X", "Y", "Z", "H", "T", "Q", "Qd", "S", "Sd", "R", "Rd", "Rx", "Ry", "Rz"},
    "q2": {"CNOT", "MSd"},
    "meas": {"measure"}
}

# %% ../nbs/03_circuit.ipynb 5
def unpack(seq):
    """Generator to unpack all values of dicts inside
    a list of dicts
    
    Parameters
    ----------
    seq : Iterable
        Iterable to recursively unpack
    """
    
    if isinstance(seq, (tuple,set,list,Circuit)):
        yield from (x for y in seq for x in unpack(y))
    elif isinstance(seq, dict):
        yield from (x for v in seq.values() for y in v for x in unpack(y))
    else:
        yield seq

# %% ../nbs/03_circuit.ipynb 6
def draw_circuit(circuit, path=None, scale=2):
    """Draw circuit using `latextools` library
    
    Parameters
    ----------
    circuit : Circuit
        The circuit to draw
    path : str or None
        The path to save the resulting image to (optional)
    scale : int
        The scale of the image
        
    Returns
    -------
    drawSvg.drawing.Drawing
        Image object
    """
    
    n_qubits = max(unpack(circuit)) + 1
    cmat = [["",""] + [r"\qw" for _ in range(circuit.n_ticks - 1)] for _ in range(n_qubits)]

    for col, tick in enumerate(circuit,1):
        for gate, qbs in tick.items():
            if gate in GATES['q2']:
                for qbtup in qbs:
                    ctrl, targ = qbtup[0], qbtup[1]
                    delta = targ - ctrl

                    cmat[ctrl][col] = r"\ctrl{%d}" % delta
                    sym = r"\targ" if gate == "CNOT" else r"\gate{%s}" % gate
                    cmat[targ][col] = sym
                continue
            elif gate == "measure": sym = r"\meter"
            elif gate == "init": sym = r"\push{\ket{0}}"

            elif gate in GATES['q1']: 
                sym = r"\gate{%s}" % gate
            else:
                raise Exception(f'Unknown gate {gate}')

            for row in qbs:
                cmat[row][col] = sym

    tex_str = r"\\".join([" & ".join([e for e in row]) for row in cmat])
    pdf = latextools.render_qcircuit(tex_str, const_row=False, const_col=True)
    svg = pdf.as_svg().as_drawing(scale=scale)
    if path: svg.saveSvg(path)
    return svg

# %% ../nbs/03_circuit.ipynb 7
class Circuit(MutableSequence):
    """Representation of a quantum circuit
    
    Attributes
    ----------
    _ticks : list of dict
        List of ticks in the circuit
    noisy : bool
        If true, circuit is subject to noise during sampling
    ff_deterministic : bool
        If true, the measurement result of the circuit in the
        fault-free case is always deterministic
    qubits : set
        Set of qubits "touched" by circuit
    n_qubits : int
        Numbers of qubits "touched" by circuit
    n_ticks : int
        Number of ticks in circuit
    id : str
        Unique circuit identifier
    """
    
    def __init__(self, ticks=None, noisy=True, ff_deterministic=False):
        """
        Parameters
        ----------
        ticks : list
            List of ticks defining a circuit
        noisy : bool
            If true, circuit is subject to noise during sampling
        ff_det : bool
            If true, the measurement result of the circuit in the
            fault-free case is always deterministic
        """
        self._ticks = ticks if ticks else [] # Must do this way, else keeps appending to same instance
        self.noisy = noisy
        self.ff_deterministic = ff_deterministic # fault-free deterministic
        
    def __getitem__(self, tick_index):
        return self._ticks[tick_index]
    
    def __setitem__(self, tick_index, tick):
        self._ticks[tick_index] = tick
        
    def __delitem__(self, tick_index):
        del self._ticks[tick_index]
        
    def __len__(self):
        return len(self._ticks)
    
    def insert(self, tick_index, tick):
        """Insert a tick into a circuit
        
        Parameters
        ----------
        tick_index : int
            Index at which tick is inserted (tick indices to right incremented by 1)
        tick : dict
            Tick dictionary to insert
        """
        self._ticks.insert(tick_index, tick)
    
    def __str__(self):
        str_list = []
        for i, tick in enumerate(self._ticks):
            str_list.append(f"{i}: {str(tick)}")
        return "\n".join(str_list)
    
    def __repr__(self):
        return self.__str__()
    
    @cached_property
    def qubits(self):  
        """Set of qubits used in circuit"""
        return set(unpack(self._ticks))
    
    @cached_property
    def n_qubits(self):
        """Number of qubits used in circuit"""
        return len(self.qubits)
    
    @cached_property
    def n_ticks(self):
        """Number of ticks"""
        return len(self._ticks)
    
    @property
    def id(self):
        """Unique circuit identifier"""
        return sha1((repr(self)).encode('UTF-8')).hexdigest()[:5]

    def draw(self, path=None, scale=2):
        """Draw the circuit"""
        return draw_circuit(self, path, scale)
