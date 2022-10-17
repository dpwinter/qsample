# qsam - quantum protocol sampling
> Efficient and user-friendly sampling of quantum protocols.


## Install

`pip install qsam`... not yet, soon to come

## Prerequisites 

## When to use

qsam offers efficient and fast estimation of logical failure rates of quantum error correction protocols when the fidelity of physical operations in the quantum circuits is high, such as in expertimental implementations today. 

This package is for you if you want to
* model circuit-level incoherent Pauli noise (we don't do coherent noise here, neither are our auxiliary qubits modelled as ideal) 
* with high fidelity physical operations aka low physical error rates
* for a QEC protocol that consists of execution of one or more quantum circuits with in-sequence measurements and feed-forward of measurement information
* over a specific range of varying physical error rates

It currently offers to
* build quantum circuits from the standard quantum gates: H, X, Z, CNOT
* run stabilizer simulations with a standard CHP backend
* model multiparameter noise with distinct error rates for single- and two-qubit gates: p1, p2
* estimate logical failure rates until uncertainty is lower than a given target confidence interval
* choose direct Monte Carlo or Subset Sampling as sampling method

Background information:

The predominant method to model incoherent Pauli noise in quantum circuits is direct Monte Carlo (MC) sampling. MC is very inefficient for low physical error rates since most of the time no actual fault event is realized in simulation. Subset sampling circumvents this issue. With this method, presented in [<a class="latex_cit" id="call-DSS" href="#cit-DSS">DSS</a>], fault events are categorized into distinct subsets which contribute to a polynomial sum expansion of the logical failure rate. In subset sampling, only the subsets that contribute most to the logical failure rate are actually estimated via sampling -- rendering it an importance sampling technique. Both the sampling variance and the uncertainty from ignored, i.e. non-sampled, subsets stay well-defined and can be held small throughout the sampling procedure.

## Getting started

### Circuits 

To get started, we first need to define one or more circuits, which is easily done in qsam. Below we create a circuit that prepares the 4-qubit GHZ state $|\text{GHZ}\rangle=\frac{1}{\sqrt{2}}(|0000\rangle+|1111\rangle)$. 

```python
from qsam.circuit import Circuit

ghz = Circuit([ {"init": {0,1,2,3,4}},
                {"H": {0}},
                {"CNOT": {(0,1)}},
                {"CNOT": {(1,2)}},
                {"CNOT": {(2,3)}},
                {"CNOT": {(3,4)}},
                {"CNOT": {(0,4)}},
                {"measure": {4}}], ff_det=True)
```

The keyword `ff_det`is set to `True` to indicate that the circuit will yield a deterministic outcome when ran fault-free. It is important for the calculation of uncertainties. This need not be the case, e.g. for circuits that measure stabilizers on unencoded states and thus yield random measurement results. An example of a fault-tolerant measurement circuit for the Steane code stabilizer $Z_0Z_1Z_3Z_6$ is given below. The default value of `ff_det`is `False`.

```python
sz_123 = Circuit([{"init": {8}},
                {"CNOT": {(0,8)}},
                {"CNOT": {(1,8)}},
                {"CNOT": {(3,8)}},
                {"CNOT": {(6,8)}},
                {"measure": {8}}])
```

```python
# add ghz run, explain all arguments and comparison of mc and ss
```

```python
# also output errors, esp. show that delta only becomes smaller
```

### Protocols

From the single ghz-circuit given above, we may construct a simple toy-protocol to demonstrate essential features of qsam. The protocol is that, whenever the circuit measurement is $-1$, we shall repeat the preparation circuit since the fifth qubit indicates preparation of an erroneous state. When the measurement is $+1$ the state is prepared correctly. If there is still no $+1$ after two preparation attempts, we count the protocol run as a logical failure. These conditions are defined in the following functions:

```python
from qsam.protocol import Protocol, draw_protocol

def repeat(m):
    return len(m) < 2 and m[-1] == 1
    
def logErr(m):
    return len(m) >= 2 and m[-1] == 1 and m[-2] == 1

functions = {'logErr': logErr, 'repeat': repeat}
```

The protocol is now defined as a graph, where nodes are circuits and edges between the nodes are labelled with transition conditions between the circuits. Terminating a protocol with success (instead of fail) will not be shown explicitly by the protocol graph. The `check` argument takes a function, which returns a boolean, to evaluate a transition based on the sequence of measurement results stored in the node as a list (`ghz` in this example).

```python
g = Protocol()
g._check_fns.update(functions)
g.add_nodes_from(['ghz'], circuits=[ghz])

g.add_edge('START', 'ghz', check='True')

g.add_edge('ghz', 'ghz', check='repeat(ghz)')
g.add_edge('ghz', 'FAIL', check='logErr(ghz)')

draw_protocol(g, figsize=(6,5))
```


    
![png](docs/images/output_17_0.png)
    


We may now specify our error parameters, i.e. the range over which we wish to scale the physical error rates. Let's start with a single parameter $p$ for both single- and two-qubit-gates. Here, we are exploring logical failure rates for physical error rates $p \in [0.00001, 0.1]$.

```python
from qsam.fault_generators import Depolarizing

scale = np.logspace(-5,-1,5)
err_params = {'p': scale}
fault_gen = Depolarizing(err_params)
```

We initialize a new direct Monte Carlo sampler and set up a depolarizing noise model.

```python
#slow

from qsam.simulators.chp import ChpSimulator
# from qsam.simulators.projectq import StateVector
from qsam.samplers.protocol_samplers import Sampler


mc_sam = Sampler(g, ChpSimulator, fault_gen)
# mc_sam = Sampler(g, StateVector)
```

Its `run` function takes the maximum number of samples and/or user specified callback functions. Here we use for example the `RelStdTarget` callback to specify a maximum error of 10% (which is actually the default value) or 50000 samples at max. The logical failure rate estimator and its uncertainty are then plotted in the range defined by `scale` by the `PlotStats` callback from the relevant information (counts and fail_counts) which are stored directly in the `Sampler` object.

```python
#slow

import qsam.samplers.callbacks as cb

callbacks = [
    cb.RelStdTarget(target=0.1),
    cb.PlotStats(scale)
]

mc_sam.run(n_samples=10000, callbacks=callbacks)
```

    Rel. std target of 0.1 reached. Sampling stopped.



    
![png](docs/images/output_23_1.png)
    


The sampler instance allows to print the logical failure rate estimator and its sampling and cutoff error over the sampled range.

```python
#slow
p_L, std, delta, _ = mc_sam.stats()
print(p_L)
print(std)
```

    [0.         0.         0.         0.00049505 0.04876428]
    [0.00019011 0.00019011 0.00019011 0.0004735  0.00487017]


We can observe in the statistics of the direct MC Sampler that it does not even record logical failures with moderately low $p$ with the given number of samples. The Subset Sampler fixes this problem. 

Additionally to just sampling the logical failure rate we can specify a variety of callbacks to track desired quantities of the sampling process. A comprehensive list is given in `directory`. Below we plot, for example, the logical failure rate at `p = p_max = 0.01` and its uncertainty as a function of the number of samples run.

```python
#slow
from qsam.samplers.protocol_samplers import SubsetSampler

sb_sam = SubsetSampler(g, ChpSimulator, fault_gen, p_max=0.1)
# sb_sam = SubsetSampler(g, StateVector)


callbacks = [
    cb.StatsPerSample()
]
sb_sam.run(1000, callbacks=callbacks)
```


    
![png](docs/images/output_27_0.png)
    


The Sampler instance contains a `Tree` structure that we can investigate manually with `sb_sam.tree`, or plot as image.

```python
#slow
sb_sam.tree.display()
```


    
![png](docs/images/output_29_0.png)
    





    'temp.png'



From plotting the MC and SS results together we can see that they produce the same results in some intermediate regime of $p$. Subset Sampling achieves tight bounds on the logical failure rate for low $p$ where the uncertainty for MC is large. Vice versa, Subset Sampling becomes inefficient if the cutoff error from only sampling a few subsets becomes large for larger $p$. Here though, MC is efficient.

```python
#slow
import matplotlib.pyplot as plt

p_L_low, ss_std, delta, _ = sb_sam.stats()
p_L, std, _, _ = mc_sam.stats()

plt.errorbar(scale, p_L, fmt='--', c="black", yerr=std, label="Direct MC")

plt.plot(scale, p_L_low, label="SS low")
plt.fill_between(scale, p_L_low-ss_std, p_L_low+delta+ss_std, alpha=0.2)

plt.plot(scale, p_L_low+delta, label="SS up")
plt.fill_between(scale, p_L_low-ss_std, p_L_low+delta+ss_std, alpha=0.2)

plt.plot(scale, scale, 'k:', alpha=0.5)
plt.xscale('log')
plt.yscale('log')
plt.ylabel(r'$p_L$')
plt.xlabel(r'$\lambda$ - uniform')
plt.legend();
```


    
![png](docs/images/output_31_0.png)
    


With the already sampled subsets we can also vary the plotted range in retrospect. 

```python
#slow
adjusted_scale = np.logspace(-3,-1,5)
sb_sam.set_range({'p': adjusted_scale})
p_L_low, ss_std, delta, _ = sb_sam.stats()
```

(Below we also show the MC output in the adjusted range but for the direct Sampler we cannot modify the range in that way)

```python
#slow
plt.errorbar(scale[-2:], p_L[-2:], fmt='--', c="black", yerr=std[-2:], label="Direct MC")

plt.plot(adjusted_scale, p_L_low, label="SS low")
plt.fill_between(adjusted_scale, p_L_low-ss_std, p_L_low+delta+ss_std, alpha=0.2)

plt.plot(adjusted_scale, p_L_low+delta, label="SS up")
plt.fill_between(adjusted_scale, p_L_low-ss_std, p_L_low+delta+ss_std, alpha=0.2)

plt.xscale('log')
plt.yscale('log')
plt.ylabel(r'$p_L$')
plt.xlabel(r'$\lambda$ - uniform')
plt.legend();
```


    
![png](docs/images/output_35_0.png)
    


We may add 100 more samples to the already existing 500 samples...

```python
#slow
sb_sam.run(100, callbacks=callbacks)
```


    
![png](docs/images/output_37_0.png)
    


... or pickle it for later use.

```python
#slow
print(sb_sam.tree)
```

    ghz (1100)
    ├── (0,) (1)
    │   └── None (1/1, 1.57e-01)
    ├── (1,) (1076)
    │   ├── None (595/1076, 8.79e-04)
    │   └── ghz (481/1076, 8.79e-04)
    │       ├── (0,) (1)
    │       │   └── None (1/1, 1.57e-01)
    │       ├── (1,) (471)
    │       │   ├── FAIL (205/471, 1.99e-03)
    │       │   └── None (266/471, 1.99e-03)
    │       └── (2,) (9)
    │           ├── None (4/9, 7.41e-02)
    │           └── FAIL (5/9, 7.41e-02)
    └── (2,) (23)
        ├── ghz (11/23, 3.57e-02)
        │   ├── (0,) (1)
        │   │   └── None (1/1, 1.57e-01)
        │   └── (1,) (10)
        │       ├── None (5/10, 6.94e-02)
        │       └── FAIL (5/10, 6.94e-02)
        └── None (12/23, 3.57e-02)


```python
#slow
sb_sam.tree.save('ghz_rep.json')
```

```python
#slow
sb_sam = SubsetSampler(g, ChpSimulator)
sb_sam.setup(scale, err_params, p_max=err_params['p'])
sb_sam.tree.load('ghz_rep.json')
print(sb_sam.tree)
```

    ghz (1100)
    ├── [0] (2)
    │   └── None (2/2, 1.08e-01)
    ├── [1] (1071)
    │   ├── ghz (463/1071, 8.77e-04)
    │   │   ├── [0] (2)
    │   │   │   └── None (2/2, 1.08e-01)
    │   │   ├── [1] (451)
    │   │   │   ├── FAIL (195/451, 2.07e-03)
    │   │   │   └── None (256/451, 2.07e-03)
    │   │   ├── [2] (8)
    │   │   │   ├── FAIL (6/8, 6.74e-02)
    │   │   │   └── None (2/8, 6.74e-02)
    │   │   ├── [3] (1)
    │   │   │   └── FAIL (1/1, 1.00e+00)
    │   │   └── [4] (1)
    │   │       └── FAIL (1/1, 1.00e+00)
    │   └── None (608/1071, 8.77e-04)
    ├── [2] (23)
    │   ├── ghz (13/23, 3.53e-02)
    │   │   ├── [0] (2)
    │   │   │   └── None (2/2, 1.08e-01)
    │   │   ├── [1] (7)
    │   │   │   ├── FAIL (3/7, 8.74e-02)
    │   │   │   └── None (4/7, 8.74e-02)
    │   │   ├── [2] (1)
    │   │   │   └── FAIL (1/1, 1.00e+00)
    │   │   ├── [3] (1)
    │   │   │   └── FAIL (1/1, 1.00e+00)
    │   │   └── [4] (2)
    │   │       ├── None (1/2, 1.64e-01)
    │   │       └── FAIL (1/2, 1.64e-01)
    │   └── None (10/23, 3.53e-02)
    ├── [3] (2)
    │   └── ghz (2/2, 1.08e-01)
    │       └── [0] (2)
    │           └── None (2/2, 1.08e-01)
    └── [4] (2)
        └── ghz (2/2, 1.08e-01)
            └── [0] (2)
                └── None (2/2, 1.08e-01)


## Real examples

For more complicated protocols, we might want to receive more feedback from what the sampler is actually doing. Using the `verbose` keyword, we can print the actual circuit sequences realized through out the sampling procedure and watch which intermediate measurement results lead to different circuit branchings. 

To illustrate this, we give the example of first preparing the logical zero state of the Steane code. A flag qubit verifies correct preparation in the first circuit. The second circuit is only run, if the flag is triggered. It restores the correct state in a fault-tolerant way from the state after the first circuit marked as faulty by the flag.

```python
eft = Circuit([ {"init": {0,1,2,4,3,5,6,7}},
                {"H": {0,1,3}},
                {"CNOT": {(0,4)}},
                {"CNOT": {(1,2)}},
                {"CNOT": {(3,5)}},
                {"CNOT": {(0,6)}},
                {"CNOT": {(3,4)}},
                {"CNOT": {(1,5)}},
                {"CNOT": {(0,2)}},
                {"CNOT": {(5,6)}},
                {"CNOT": {(4,7)}},
                {"CNOT": {(2,7)}},
                {"CNOT": {(5,7)}},
                {"measure": {7}} ], ff_det=True)

sz_123 = Circuit([{"init": {8}},
                {"CNOT": {(0,8)}},
                {"CNOT": {(1,8)}},
                {"CNOT": {(3,8)}},
                {"CNOT": {(6,8)}},
                {"measure": {8}}])

meas = Circuit([ {"measure": {0,1,2,3,4,5,6}} ])

k1 = 0b0001111
k2 = 0b1010101
k3 = 0b0110011
k12 = k1 ^ k2
k23 = k2 ^ k3
k13 = k1 ^ k3
k123 = k12 ^ k3
stabilizerGenerators = [k1, k2, k3]
stabilizerSet = [0, k1, k2, k3, k12, k23, k13, k123]

def hamming2(x, y):
    count, z = 0, x ^ y
    while z:
        count += 1
        z &= z - 1
    return count


def logErr(out):
    if min([hamming2(out, i) for i in stabilizerSet]) > 1:
        return True
    else:
        return False
        
def flagged_z_look_up_table_1(z):
    if z:
        return Circuit([{'X': {6}}], noisy=False)
    else:
        return Circuit(noisy=False)

functions = {"logErr": logErr, "lut": flagged_z_look_up_table_1}

init = Protocol()
init._check_fns.update(functions)

init.add_nodes_from(['ENC', 'SZ', 'meas'], circuits=[eft, sz_123, meas])
init.add_node('X_COR', circuit=Circuit(noisy=False))

init.add_edge('START', 'ENC', check='True')

init.add_edge('ENC', 'meas', check='ENC[-1]==0')

init.add_edge('ENC', 'SZ', check='ENC[-1]==1')
init.add_edge('SZ', 'X_COR', check='lut(SZ[-1])')

init.add_edge('X_COR', 'meas', check='True')

init.add_edge('meas', 'FAIL', check='logErr(meas[-1])')

draw_protocol(init, figsize=(6,6), edge_legend=True)
```


    
![png](docs/images/output_44_0.png)
    


The protocol contains a recovery operation which is applied conditioned on the stabilizer measurement result being $-1$. The `check` function, which we previously introduced to only take boolean values, in this case actually accepts a circuit which corresponds to the recovery operation. To avoid also placing fault operators on this circuit, we use the keyword `noisy` and set it to `False` (this can be used for any circuit). The recovery operation is the return value of the look up table function we define above. 

We may choose more realistic error rates for single and two qubit gates.

```python
err_params = {'p1': 0.01 * scale, 'p2': 0.1 * scale}
```

Let's first run 10 samples to see what the protocol does. For this means we can use the `VerboseCircuitExec` callback:

```python
#slow
fault_gen.__init__(err_params)
sb_sam = SubsetSampler(init, ChpSimulator, fault_gen, p_max=(0.01, 0.1))

callbacks = [
    cb.VerboseCircuitExec()
]
sb_sam.run(10, callbacks=callbacks)
```

    --- Protocol Run: 1 ---
    Node ENC, Faults ["Tick 4 :: {'Z': {3, 5}}"], Measured 0-> meas
    Node meas, Faults [], Measured 1011010-> None
    --- Protocol Run: 2 ---
    Node ENC, Faults [], Measured 0-> meas
    Node meas, Faults [], Measured 0111100-> None
    --- Protocol Run: 3 ---
    Node ENC, Faults [], Measured 0-> meas
    Node meas, Faults [], Measured 0000000-> None
    --- Protocol Run: 4 ---
    Node ENC, Faults ["Tick 10 :: {'Z': {4}, 'Y': {7}}", "Tick 3 :: {'Z': {1}}"], Measured 1-> SZ
    Node SZ, Faults [], Measured 0-> None
    --- Protocol Run: 5 ---
    Node ENC, Faults [], Measured 0-> meas
    Node meas, Faults [], Measured 1100110-> None
    --- Protocol Run: 6 ---
    Node ENC, Faults [], Measured 0-> meas
    Node meas, Faults [], Measured 1011010-> None
    --- Protocol Run: 7 ---
    Node ENC, Faults ["Tick 8 :: {'X': {2}}", "Tick 6 :: {'X': {3, 4}}"], Measured 0-> meas
    Node meas, Faults [], Measured 1001001-> None
    --- Protocol Run: 8 ---
    Node ENC, Faults ["Tick 7 :: {'X': {1, 5}}", "Tick 11 :: {'Y': {7}}"], Measured 0-> meas
    Node meas, Faults [], Measured 0010000-> None
    --- Protocol Run: 9 ---
    Node ENC, Faults [], Measured 0-> meas
    Node meas, Faults [], Measured 0110011-> None
    --- Protocol Run: 10 ---
    Node ENC, Faults ["Tick 10 :: {'X': {4}, 'Z': {7}}", "Tick 4 :: {'Y': {5}}"], Measured 1-> SZ
    Node SZ, Faults [], Measured 1-> X_COR
    Node X_COR, Circuit 0: {'X': {6}} -> meas
    Node meas, Faults [], Measured 1100000-> FAIL


When the flag is triggered, measurement of $Z_0Z_1Z_3Z_6$ follows. 

We can now go on and sample in a regime virtually inaccessible to direct MC until our target uncertainty of -- let say 5% -- is reached.

```python
err_params = {'p1': 0.0001 * scale, 'p2': 0.001 * scale}
fault_gen.__init__(err_params)
```

```python
#slow
fault_gen.__init__(err_params)
sb_sam = SubsetSampler(init, ChpSimulator, fault_gen, p_max=(0.01, 0.1))

callbacks = [
    cb.RelStdTarget(target=0.05),
    cb.SubsetRates(),
    cb.StatsPerSample(),
    cb.PlotStats(scale)
]

sb_sam.run(1_000, callbacks=callbacks)
```


    
![png](docs/images/output_51_0.png)
    



    
![png](docs/images/output_51_1.png)
    



    
![png](docs/images/output_51_2.png)
    


```python
#slow
print(sb_sam.tree)
```

    ENC (1000)
    ├── (0, 1) (625)
    │   ├── meas (284/625, 1.51e-03)
    │   │   └── (0, 0) (284)
    │   │       └── None (284/284, 4.45e-05)
    │   └── SZ (341/625, 1.51e-03)
    │       ├── (0, 0) (250)
    │       │   ├── None (176/250, 3.16e-03)
    │       │   └── X_COR (74/250, 3.16e-03)
    │       │       └── meas (74/74, 6.09e-04)
    │       │           └── (0, 0) (74)
    │       │               └── None (74/74, 6.09e-04)
    │       ├── (0, 1) (84)
    │       │   ├── X_COR (49/84, 1.06e-02)
    │       │   │   └── meas (49/49, 1.32e-03)
    │       │   │       └── (0, 0) (49)
    │       │   │           ├── None (17/49, 1.66e-02)
    │       │   │           └── FAIL (32/49, 1.66e-02)
    │       │   └── None (35/84, 1.06e-02)
    │       └── (0, 2) (7)
    │           ├── None (1/7, 5.94e-02)
    │           └── X_COR (6/7, 5.94e-02)
    │               └── meas (6/6, 3.81e-02)
    │                   └── (0, 0) (6)
    │                       ├── None (3/6, 9.76e-02)
    │                       └── FAIL (3/6, 9.76e-02)
    ├── (0, 0) (82)
    │   └── meas (82/82, 5.01e-04)
    │       └── (0, 0) (82)
    │           └── None (82/82, 5.01e-04)
    ├── (0, 2) (180)
    │   ├── meas (91/180, 5.22e-03)
    │   │   └── (0, 0) (91)
    │   │       ├── None (71/91, 7.07e-03)
    │   │       └── FAIL (20/91, 7.07e-03)
    │   └── SZ (89/180, 5.22e-03)
    │       ├── (0, 0) (86)
    │       │   ├── X_COR (38/86, 1.06e-02)
    │       │   │   └── meas (38/38, 2.11e-03)
    │       │   │       └── (0, 0) (38)
    │       │   │           ├── None (33/38, 1.16e-02)
    │       │   │           └── FAIL (5/38, 1.16e-02)
    │       │   └── None (48/86, 1.06e-02)
    │       ├── (0, 1) (2)
    │       │   ├── None (1/2, 1.64e-01)
    │       │   └── X_COR (1/2, 1.64e-01)
    │       │       └── meas (1/1, 1.57e-01)
    │       │           └── (0, 0) (1)
    │       │               └── FAIL (1/1, 1.57e-01)
    │       └── (0, 2) (1)
    │           └── None (1/1, 1.57e-01)
    ├── (0, 3) (90)
    │   ├── SZ (43/90, 1.02e-02)
    │   │   ├── (0, 0) (33)
    │   │   │   ├── X_COR (19/33, 2.55e-02)
    │   │   │   │   └── meas (19/19, 7.07e-03)
    │   │   │   │       └── (0, 0) (19)
    │   │   │   │           ├── FAIL (8/19, 4.12e-02)
    │   │   │   │           └── None (11/19, 4.12e-02)
    │   │   │   └── None (14/33, 2.55e-02)
    │   │   └── (0, 1) (10)
    │   │       ├── None (6/10, 6.74e-02)
    │   │       └── X_COR (4/10, 6.74e-02)
    │   │           └── meas (4/4, 6.00e-02)
    │   │               └── (0, 0) (4)
    │   │                   ├── None (1/4, 1.07e-01)
    │   │                   └── FAIL (3/4, 1.07e-01)
    │   └── meas (47/90, 1.02e-02)
    │       └── (0, 0) (47)
    │           ├── None (34/47, 1.54e-02)
    │           └── FAIL (13/47, 1.54e-02)
    ├── (0, 4) (7)
    │   ├── SZ (6/7, 5.94e-02)
    │   │   ├── (0, 0) (3)
    │   │   │   ├── None (1/3, 1.34e-01)
    │   │   │   └── X_COR (2/3, 1.34e-01)
    │   │   │       └── meas (2/2, 1.08e-01)
    │   │   │           └── (0, 0) (2)
    │   │   │               └── FAIL (2/2, 1.08e-01)
    │   │   └── (0, 1) (3)
    │   │       ├── None (2/3, 1.34e-01)
    │   │       └── X_COR (1/3, 1.34e-01)
    │   │           └── meas (1/1, 1.57e-01)
    │   │               └── (0, 0) (1)
    │   │                   └── FAIL (1/1, 1.57e-01)
    │   └── meas (1/7, 5.94e-02)
    │       └── (0, 0) (1)
    │           └── FAIL (1/1, 1.57e-01)
    ├── (1, 1) (14)
    │   ├── meas (7/14, 5.38e-02)
    │   │   └── (0, 0) (7)
    │   │       └── None (7/7, 3.14e-02)
    │   └── SZ (7/14, 5.38e-02)
    │       ├── (0, 0) (6)
    │       │   ├── None (5/6, 7.11e-02)
    │       │   └── X_COR (1/6, 7.11e-02)
    │       │       └── meas (1/1, 1.57e-01)
    │       │           └── (0, 0) (1)
    │       │               └── None (1/1, 1.57e-01)
    │       └── (0, 1) (1)
    │           └── None (1/1, 1.57e-01)
    ├── (1, 0) (1)
    │   └── meas (1/1, 1.57e-01)
    │       └── (0, 0) (1)
    │           └── None (1/1, 1.57e-01)
    └── (1, 2) (1)
        └── meas (1/1, 1.57e-01)
            └── (0, 0) (1)
                └── None (1/1, 1.57e-01)


More elaborate examples are given in `directory`.

## Contribute 

# planned future features
* statevector backend
* MS gates
* crosstalk and idling noise

# submit your feature request via github issue

## Team 

qsam was developed by Don Winter based on [<a class="latex_cit" id="call-DSS" href="#cit-DSS">DSS</a>] and in collaboration with Sascha Heußen under supervision of Prof. Dr. Markus Müller.

## License
