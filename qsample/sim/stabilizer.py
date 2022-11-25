# AUTOGENERATED! DO NOT EDIT! File to edit: 04b_sim.stabilizer.ipynb (unless otherwise specified).

__all__ = ['StabilizerSimulator']

# Cell
from chp_sim import ChpSimulator
from .mixin import CircuitRunnerMixin

# Cell
class StabilizerSimulator(ChpSimulator, CircuitRunnerMixin):
    """The bare minimum needed for the CHP simulation.

    Reference:
        "Improved Simulation of Stabilizer Circuits"
        Scott Aaronson and Daniel Gottesman
        https://arxiv.org/abs/quant-ph/0406196

    Original author:
        Craig Gidney
        https://github.com/Strilanc/python-chp-stabilizer-simulator
    """

    def init(self, qubit: int) -> None:
        """Initialize to |0>"""
        m = self.measure(qubit)
        if m == 1:
            self.X(qubit)

    def S(self, qubit: int) -> None:
        """Phase gate"""
        self.phase(qubit)

    def H(self, qubit:int) -> None:
        """H gate"""
        self.hadamard(qubit)

    def CNOT(self, control: int, target: int) -> None:
        """CNOT gate"""
        self.cnot(control, target)

    def I(self, qubit: int) -> None:
        """Identity gate"""
        pass

    def Z(self, qubit: int) -> None:
        """Z gate"""
        self.S(qubit)
        self.S(qubit)

    def X(self, qubit: int) -> None:
        """X gate"""
        self.H(qubit)
        self.Z(qubit)
        self.H(qubit)

    def Y(self, qubit: int) -> None:
        """Y gate"""
        self.S(qubit)
        self.S(qubit)
        self.S(qubit)
        self.X(qubit)
        self.S(qubit)