# AUTOGENERATED! DO NOT EDIT! File to edit: 03a_simulators.simulator_mixins.ipynb (unless otherwise specified).

__all__ = ['CircuitRunnerMixin']

# Cell
class CircuitRunnerMixin:
    """Simulator mixin for running quantum circuits"""

    def _apply_gate(self, gate_symbol, qubits):
        """Apply a gate to the `qubits` of the current state."""

        gate = getattr(self, gate_symbol)
        args = (qubits,) if type(qubits)==int else qubits
        return gate(*args)

    def run(self, circuit, fault_circuit=None):
        """Apply gates in `circuit` sequentially to current state.
        If `fault_circuit` is specified apply fault gates at end of each tick.

        Measurement results are saved in the order in which they appear in the
        circuit into an output string."""

        msmt_res = []
        for tick_index in range(circuit.n_ticks):

            for gate, qubits in circuit[tick_index].items():
                for qubit in qubits:
                    res = self._apply_gate(gate, qubit)

                    if res is not None:
                        msmt_res.append( int(res.value) )
            if fault_circuit:
                for f_gate, f_qubits in fault_circuit[tick_index].items():
                    for f_qubit in f_qubits:
                        self._apply_gate(f_gate, f_qubit)

        if msmt_res:
            msmt_bit_str = ''.join(map(str, msmt_res))
            return int(msmt_bit_str, 2)
        else:
            return None # no measurement