# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09_examples.ipynb.

# %% auto 0
__all__ = ['ghz', 'ghz_stabs', 'eft', 'sz_123', 'meas7', 'fmx_1', 'fmx_2', 'fmx_3', 'nfs', 'ghz1', 'ghz3', 'ghz_stab', 'ftsteane',
           'steane0', 'flagstab', 'gen_ghz1', 'gen_ghz3', 'gen_ghz_stab', 'gen_ftsteane', 'gen_steane0', 'gen_flagstab']

# %% ../nbs/09_examples.ipynb 3
from .circuit import Circuit
from .protocol import Protocol

# %% ../nbs/09_examples.ipynb 5
ghz = Circuit([ {"init": {0,1,2,3,4}},
                {"H": {0}},
                {"CNOT": {(0,1)}},
                {"CNOT": {(1,2)}},
                {"CNOT": {(2,3)}},
                {"CNOT": {(3,4)}},
                {"CNOT": {(0,4)}},
                {"measure": {4}}   ])#, ff_deterministic=True)

# %% ../nbs/09_examples.ipynb 7
# stabilizers for 4-qubit ghz state are XXXX and three ZZ parity checks
ghz_stabs = Circuit([{"init": {4}},
                {"H": {4}},
                {"CNOT": {(4,0)}},
                {"CNOT": {(4,1)}},
                {"CNOT": {(4,2)}},
                {"CNOT": {(4,3)}},
                {"H": {4}},
                {"measure": {4}},
                
                {"init": {4}},
                {"CNOT": {(0,4)}},
                {"CNOT": {(1,4)}},
                {"measure": {4}},
                
                {"init": {4}},
                {"CNOT": {(1,4)}},
                {"CNOT": {(2,4)}},
                {"measure": {4}},
                
                {"init": {4}},
                {"CNOT": {(2,4)}},
                {"CNOT": {(3,4)}},
                {"measure": {4}}], noisy=False)

# %% ../nbs/09_examples.ipynb 9
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
                {"measure": {7}} ])#, ff_deterministic=True)

# %% ../nbs/09_examples.ipynb 11
sz_123 = Circuit([{"init": {8}},
                {"CNOT": {(0,8)}},
                {"CNOT": {(1,8)}},
                {"CNOT": {(3,8)}},
                {"CNOT": {(6,8)}},
                {"measure": {8}}])

# %% ../nbs/09_examples.ipynb 13
meas7 = Circuit([ {"measure": {0,1,2,3,4,5,6}} ])

# %% ../nbs/09_examples.ipynb 15
fmx_1 = Circuit([{"init": {8,9}},
                 {"H": {8}},
                # {"init": {9}},
                {"CNOT": {(8,3)}},
                {"CNOT": {(8,9)}},
                {"CNOT": {(8,4)}},
                {"CNOT": {(8,5)}},
                {"CNOT": {(8,9)}},
                {"CNOT": {(8,6)}},
                 {"H": {8}},
                {"measure": {8,9}}])
                # {"measure": {9}} ])

fmx_2 = Circuit([{"init": {8,9}},
                  {"H": {8}},
                # {"init": {9}},
                {"CNOT": {(8,0)}},
                {"CNOT": {(8,9)}},
                {"CNOT": {(8,2)}},
                {"CNOT": {(8,4)}},
                {"CNOT": {(8,9)}},
                {"CNOT": {(8,6)}},
                 {"H": {8}},
                {"measure": {8,9}}])
                # {"measure": {9}} ])

fmx_3 = Circuit([{"init": {8,9}},
                 {"H": {8}},
                # {"init": {9}},
                {"CNOT": {(8,1)}},
                {"CNOT": {(8,9)}},
                {"CNOT": {(8,2)}},
                {"CNOT": {(8,5)}},
                {"CNOT": {(8,9)}},
                {"CNOT": {(8,6)}},
                 {"H": {8}},
                {"measure": {8,9}}])
                # {"measure": {9}} ])

nfs = Circuit([{"init": {7,8,9}},
               {"H": {7,8,9}},
                {"CNOT": {(7,3)}},
                {"CNOT": {(7,4)}},
                {"CNOT": {(7,5)}},
                {"CNOT": {(7,6)}},
                {"CNOT": {(8,0)}},
                {"CNOT": {(8,2)}},
                {"CNOT": {(8,4)}},
                {"CNOT": {(8,6)}},
                {"CNOT": {(9,1)}},
                {"CNOT": {(9,2)}},
                {"CNOT": {(9,5)}},
                {"CNOT": {(9,6)}},
                {"H": {7,8,9}},
                {"measure": {7,8,9}},
                {"init": {7,8,9}},
                {"CNOT": {(3,7)}},
                {"CNOT": {(4,7)}},
                {"CNOT": {(5,7)}},
                {"CNOT": {(6,7)}},
                {"CNOT": {(0,8)}},
                {"CNOT": {(2,8)}},
                {"CNOT": {(4,8)}},
                {"CNOT": {(6,8)}},
                {"CNOT": {(1,9)}},
                {"CNOT": {(2,9)}},
                {"CNOT": {(5,9)}},
                {"CNOT": {(6,9)}},
                {"measure": {7,8,9}} ])

# %% ../nbs/09_examples.ipynb 21
def gen_ghz1():

    ghz1 = Protocol()
    ghz1.add_nodes_from(['ghz'], circuits=[ghz])
    ghz1.add_edge('START', 'ghz', check='True')
    ghz1.add_edge('ghz', 'FAIL', check='ghz[-1]==1')
    ghz1.ft_level = 1
    
    return ghz1
ghz1 = gen_ghz1()

# %% ../nbs/09_examples.ipynb 24
def gen_ghz3():
    
    def repeat(m):
        return len(m) < 3 and m[-1] == 1

    def logErr(m):
        return len(m) >= 3 and m == [1,1,1]

    functions = {'logErr': logErr, 'repeat': repeat}

    ghz3 = Protocol(check_functions=functions)
    ghz3.add_nodes_from(['ghz'], circuits=[ghz])
    ghz3.add_edge('START', 'ghz', check='True')
    ghz3.add_edge('ghz', 'ghz', check='repeat(ghz)')
    ghz3.add_edge('ghz', 'FAIL', check='logErr(ghz)')
    
    ghz3.ft_level = 1
    
    return ghz3
ghz3 = gen_ghz3()

# %% ../nbs/09_examples.ipynb 27
def gen_ghz_stab():
    def logErr(m):
        return m != 0b0000

    def lut(s):
        syn = format(s, '04b')
        sx = syn[0]
        sz = syn[1:]
        #print(sx, sz)

        c = Circuit(noisy=False)

        if sx == '1':
            c.insert(tick_index=0, tick={'Z': {0}})

        if sz in ['001', '100', '110', '011']: #, '101']: # '111' and '010' can only guess, '000' trivial
            corrs = {'001': {3}, '100': {0}, '110': {1}, '011': {2}} #, '101': {0,3}}
            c.insert(tick_index=0, tick={'X': corrs[sz]})

        return c

    functions = {'logErr': logErr, 'lut': lut}

    ghz_stab = Protocol(check_functions=functions)
    ghz_stab.add_nodes_from(['ghz', 'meas_1', 'meas_2'], circuits=[ghz, ghz_stabs, ghz_stabs])

    # ghz_stab.add_node('COR')
    ghz_stab.add_edge('START', 'ghz', check='True')
    ghz_stab.add_edge('ghz', 'ghz', check='ghz[-1]==1')
    ghz_stab.add_edge('ghz', 'meas_1', check='ghz[-1]==0')
    ghz_stab.add_edge('meas_1', 'COR', check='lut(meas_1[-1])')
    ghz_stab.add_edge('COR', 'meas_2', check='True')
    ghz_stab.add_edge('meas_2', 'FAIL', check='logErr(meas_2[-1])')
    
    ghz_stab.ft_level = 1
    
    return ghz_stab
ghz_stab = gen_ghz_stab()

# %% ../nbs/09_examples.ipynb 30
def gen_ftsteane():
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

    functions = {"logErr": logErr}

    # Define protocol

    ftsteane = Protocol(check_functions=functions)
    ftsteane.add_nodes_from(['ENC', 'meas'], circuits=[eft, meas7])

    ftsteane.add_edge('START', 'ENC', check='True')

    ftsteane.add_edge('ENC', 'ENC', check='ENC[-1]==1')
    ftsteane.add_edge('ENC', 'meas', check='ENC[-1]==0')

    ftsteane.add_edge('meas', 'FAIL', check='logErr(meas[-1])')
    
    ftsteane.ft_level = 1
    
    return ftsteane
ftsteane = gen_ftsteane()

# %% ../nbs/09_examples.ipynb 33
def gen_steane0():
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
        import numpy as np
        c = np.array([hamming2(out, i) for i in stabilizerSet])
        d = np.flatnonzero(c <= 1)
        e = np.array([hamming2(out ^ (0b1111111), i) for i in stabilizerSet])
        f = np.flatnonzero(e <= 1)
        if len(d) != 0:
            return False
        elif len(f) != 0:
            return True
        if len(d) != 0 and len(f) != 0: 
            raise('-!-!-CANNOT BE TRUE-!-!-')

    def flagged_z_look_up_table_1(z):
        s = [z]

        if s == [1]:
            return True
        else: 
            return False

    functions = {"logErr": logErr, "lut": flagged_z_look_up_table_1}

    init = Protocol(check_functions=functions)

    init.add_nodes_from(['ENC', 'Z2', 'meas'], circuits=[eft, sz_123, meas7])
    init.add_node('X_COR', circuit=Circuit([{'X': {6}}], noisy=False))

    init.add_edge('START', 'ENC', check='True')

    init.add_edge('ENC', 'meas', check='ENC[-1]==0')

    init.add_edge('ENC', 'Z2', check='ENC[-1]==1')
    init.add_edge('Z2', 'X_COR', check='lut(Z2[-1])')

    init.add_edge('X_COR', 'meas', check='True')

    init.add_edge('meas', 'FAIL', check='logErr(meas[-1])')
    
    init.ft_level = 1
    
    return init

steane0 = gen_steane0()

# %% ../nbs/09_examples.ipynb 36
def gen_flagstab():
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

    def flagged(m):
        v = 0b01 in m or 0b11 in m if m is not None else False
        #print('flag', [format(i, '02b') for i in m], ':', v)
        return v

    def flut(m, f1a, f1b, f2a, f2b, f3a, f3b):
        formatter = lambda i,m: str(format(m, '06b')[i])

        sx = ''.join([formatter(i,m) for i in range(3)])
        sz = ''.join([formatter(i,m) for i in range(3,6)])

        if (sz == '011' and flagged([f1a,f1b])) or (sz == '011' and flagged([f2a,f2b])) or (sz == '011' and flagged([f3a,f3b])):
            corrs = {'011': {4, 5}, '101': {2, 4}, '110': {2, 5}} #{'010': {5, 6}, '001': {4, 6}}
            return Circuit([{'X': corrs[sz]}], noisy=False)
        else: 
            return Circuit(noisy=False)

    def rep_check(m):
        # no flag triggered, run second round regardless of syndrome
        # v = m[-1] == 0b00 or m[-1] == 0b10 #and len(m) == 1
        #print('rep', [format(i, '02b') for i in m], ':', v)
        # return v
        return m[-1] == 0b00 or m[-1] == 0b10

    def nft_check1(m):
        # flag triggered in first or second round OR no flag triggered, syndromes disagree in second round
        # v = (len(m) == 1 and (m[-1] == 0b01 or m[-1] == 0b11)) or (len(m) == 2 and ((m[-1] == 0b00 and m[-2] == 0b10) or (m[-1] == 0b10 and m[-2] == 0b00) or (m[-1] == 0b01 or m[-1] == 0b11)))
        #print('nft', [format(i, '02b') for i in m], ':', v)
        return (m[-1] == 0b01 or m[-1] == 0b11 or (m[-1] == 0b01) or m[-1] == 0b11)
    
    def nft_check2(m1,m2):
        return (m2[-1] == 0b00 and m1[-1] == 0b10) or (m2[-1] == 0b10 and m1[-1] == 0b00) or (m2[-1] == 0b01 or m2[-1] == 0b11)

    def syn_check(m1,m2):
        # no flag triggered, syndromes agree in second round
        # v = len(m) == 2 and ((m[-1] == 0b00 and m[-2] == 0b00) or (m[-1] == 0b10 and m[-2] == 0b10))
        #print('syn', [format(i, '02b') for i in m], ':', v)
        return (m2[-1] == 0b00 and m1[-1] == 0b00) or (m2[-1] == 0b10 and m1[-1] == 0b10)


    functions = {"logErr": logErr, "flut": flut, "rep_check": rep_check, "nft_check1": nft_check1, 'nft_check2': nft_check2, "syn_check": syn_check}

    # Define protocol

    flagstab = Protocol(check_functions=functions)

    # flagstab.add_nodes_from(['X1', 'X2', 'X3', 'nonFT', 'meas'], circuits=[fmx_1, fmx_2, fmx_3, nfs, meas7])
    flagstab.add_nodes_from(['X1a', 'X1b', 'X2a', 'X2b', 'X3a', 'X3b', 'nonFT', 'meas'], circuits=[fmx_1, fmx_1, fmx_2,fmx_2, fmx_3,fmx_3, nfs, meas7])

    flagstab.add_node('COR')

    flagstab.add_edge('START', 'X1a', check='True')

    # no flag triggered, run second round regardless of syndrome
    flagstab.add_edge('X1a', 'X1b', check='rep_check(X1a)')
    flagstab.add_edge('X2a', 'X2b', check='rep_check(X2a)')
    flagstab.add_edge('X3a', 'X3b', check='rep_check(X3a)')

    # flag triggered in first or second round OR no flag triggered, syndromes disagree in second round
    flagstab.add_edge('X1b', 'nonFT', check='nft_check2(X1a,X1b)')
    flagstab.add_edge('X2b', 'nonFT', check='nft_check2(X2a,X2b)')
    flagstab.add_edge('X3b', 'nonFT', check='nft_check2(X3a,X3b)')
    
    # flag triggered in first or second round OR no flag triggered, syndromes disagree in second round
    flagstab.add_edge('X1a', 'nonFT', check='nft_check1(X1a)')
    flagstab.add_edge('X2a', 'nonFT', check='nft_check1(X2a)')
    flagstab.add_edge('X3a', 'nonFT', check='nft_check1(X3a)')

    # no flag triggered, syndromes agree in second round
    flagstab.add_edge('X1b', 'X2a', check='syn_check(X1a,X1b)')#False if rep_check(X1) or nft_check(X1) else True')
    flagstab.add_edge('X2b', 'X3a', check='syn_check(X2a,X2b)')#'False if rep_check(X2) or nft_check(X2) else True')
    flagstab.add_edge('X3b', 'meas', check='syn_check(X3a,X3b)')#'False if rep_check(X3) or nft_check(X3) else True')

    # apply flag correction after nonFT if a flag was triggered
    flagstab.add_edge('nonFT', 'COR', check='flut(nonFT[-1], X1a,X1b, X2a,X2b, X3a,X3b)')

    flagstab.add_edge('COR', 'meas', check='True')

    flagstab.add_edge('meas', 'FAIL', check='logErr(meas[-1])')
    
    flagstab.ft_level = 1
    
    return flagstab

flagstab = gen_flagstab()
