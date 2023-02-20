# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_circuit.ipynb.

# %% auto 0
__all__ = ['GATES', 'unpack', 'Circuit']

# %% ../nbs/02_circuit.ipynb 3
from collections.abc import MutableSequence
from functools import cached_property
from hashlib import sha1
import latextools

# %% ../nbs/02_circuit.ipynb 4
GATES = {
    "init": {"init"},
    "q1": {"I", "X", "Y", "Z", "H", "T", "Q", "Qd", "S", "Sd", "R", "Rd", "Rx", "Ry", "Rz"},
    "q2": {"CNOT", "MSd"},
    "meas": {"measure"}
}

# %% ../nbs/02_circuit.ipynb 5
def unpack(seq):
    """Generator for all qubits defined in a circuit or tick"""
    
    if isinstance(seq, (tuple,set,list,Circuit)):
        yield from (x for y in seq for x in unpack(y))
    elif isinstance(seq, dict):
        yield from (x for v in seq.values() for y in v for x in unpack(y))
    else:
        yield seq

# %% ../nbs/02_circuit.ipynb 6
class Circuit(MutableSequence):
    """Representation of a quantum circuit"""
    
    def __init__(self, ticks=None, noisy=True, ff_det=False):
        self._ticks = ticks if ticks else []
        self._noisy = noisy
        self._ff_det = ff_det # fault-free deterministic
        
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
        return sha1((repr(self)).encode('UTF-8')).hexdigest()[:5]

    def draw(self, path=None, scale=2):

        n_qubits = max(unpack(self)) + 1
        cmat = [["",""] + [r"\qw" for _ in range(self.n_ticks - 1)] for _ in range(n_qubits)]

        for col, tick in enumerate(self,1):
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
        if path: 
            svg.saveSvg(path)
        try:
            from IPython.display import Image, display
            return display( svg )
        except:
            print('Image can only be drawn in Jupyter notebook.')
