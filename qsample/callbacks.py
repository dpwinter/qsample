# AUTOGENERATED! DO NOT EDIT! File to edit: ../05_callbacks.ipynb.

# %% auto 0
__all__ = ['Callback', 'CallbackList', 'PlotStats', 'RelStdTarget', 'StatsPerSample', 'VerboseCircuitExec', 'ErvPerSample']

# %% ../05_callbacks.ipynb 3
import qsample.math as math
import matplotlib.pyplot as plt
import numpy as np

# %% ../05_callbacks.ipynb 4
class Callback:
    
    def on_sampler_begin(self, *args, **kwargs):
        pass
    
    def on_sampler_end(self, *args, **kwargs):
        pass

    def on_circuit_begin(self, *args, **kwargs):
        pass
    
    def on_circuit_end(self, *args ,**kwargs):
        pass
    
    def on_protocol_begin(self, *args, **kwargs):
        pass
    
    def on_protocol_end(self, *args ,**kwargs):
        pass
    
    def store(self, log_dir, data, ext=""):
        with open(log_dir + f'/{self.__class__.__name__}_{str(ext)}.json', 'w') as f:
            json.dump(data, f)
    
class CallbackList:
    def __init__(self, sampler, callbacks=[]):
        self.sampler = sampler
        self.callbacks = callbacks
        self._add_default_callbacks()
        
    def _add_default_callbacks(self):
        pass
    
    def on_sampler_begin(self):
        for callback in self.callbacks:
            callback.on_sampler_begin(sampler=self.sampler)
            
    def on_sampler_end(self):
        for callback in self.callbacks:
            callback.on_sampler_end(sampler=self.sampler)
            
    def on_protocol_begin(self):
        for callback in self.callbacks:
            callback.on_protocol_begin(sampler=self.sampler)
            
    def on_protocol_end(self):
        for callback in self.callbacks:
            callback.on_protocol_end(sampler=self.sampler)
            
    def on_circuit_begin(self):
        for callback in self.callbacks:
            callback.on_circuit_begin(sampler=self.sampler)
            
    def on_circuit_end(self, local_vars):
        for callback in self.callbacks:
            callback.on_circuit_end(sampler=self.sampler, local_vars=local_vars)
            
    def __iter__(self):
        return iter(self.callbacks)

# %% ../05_callbacks.ipynb 5
class PlotStats(Callback):
        
    def on_sampler_end(self, sampler):
        
        stats = sampler.stats()
        xs = sampler.err_probs.T     
        x_label = sampler.grp_order
        
        def pop(stats_len, ax):
            n_lines = int(stats_len/2)
            for _ in range(n_lines):
                ax.collections.pop()
                ax.lines.pop()

        def plot(ax, x, stats, i, drawn):
            stats_len = len(stats)
            if stats_len == 4:
                p_L_low, std_low, p_L_up, std_up = stats
                ax.plot(x, p_L_low, label="SS low")
                ax.plot(x, p_L_up, label="SS up")
                ax.fill_between(x, p_L_low-std_low, p_L_low+std_low, alpha=0.2)
                ax.fill_between(x, p_L_up-std_up, p_L_up+std_up, alpha=0.2)
            else:
                p_L, std = stats
                ax.errorbar(x, p_L, fmt='--', c="black", yerr=std, label="Direct MC")

            if len(set(x)) <= 1:
                xticks = ax.get_xticks()
                ax.set_xticks(xticks, [x[0]] * len(xticks))
                pop(stats_len, ax)
            else:
                ax.set_xscale('log')
                ax.set_yscale('log') 
                if drawn:
                    pop(stats_len, ax)
                else:
                    ax.plot(x,x ,'k:', alpha=0.5)
                    ax.legend()
                drawn = True

            ax.xaxis.set_ticks_position('bottom')
            ax.xaxis.set_label_position('bottom')
            ax.spines['bottom'].set_position(('axes', -0.25 * i))
            ax.set_xlabel(x_label[i])

            return drawn
        
        fig,ax = plt.subplots(figsize=(6,4))
        ax.set_ylabel('$p_L$')

        drawn = plot(ax,xs[0],stats,0,False)
        for i,x in enumerate(xs[1:],1):
            ax = ax.twiny()
            drawn = plot(ax,x,stats,i,drawn)
        

# %% ../05_callbacks.ipynb 6
class RelStdTarget(Callback):
    def __init__(self, target=0.1, include_delta=True):
        self.target = target
        self.include_delta = include_delta
        
    def on_protocol_end(self, sampler):
        if sampler.__class__.__name__ == "DirectSampler":
            p_L, err = sampler.stats(tree_idx=sampler.tree_idx)
        else:
            
            p_L = sampler.tree.rate
            std = np.sqrt(sampler.tree.variance)
            delta = sampler.tree.delta
            
            err = std + delta if self.include_delta else std
        
        if p_L > 0 and err / p_L < self.target: 
            print(f'Rel. std target of {self.target} reached. Sampling stopped.') 
            sampler.stop_sampling = True

# %% ../05_callbacks.ipynb 7
class StatsPerSample(Callback):
    def __init__(self, log_dir=None):
        self.log_dir = log_dir
        self.data = []
        self.n_calls = 0
        
    def on_protocol_end(self, sampler):
        
        if sampler.__class__.__name__ == "DirectSampler":
            stats = sampler.stats(tree_idx=sampler.tree_idx)
        else:
            p_L = sampler.tree.rate
            std = np.sqrt(sampler.tree.variance)
            delta = sampler.tree.delta
            std_up = np.sqrt(sampler.tree.variance_ub)
            stats = [p_L, std, delta, std_up]
            stats = [e if not isinstance(e,np.ndarray) else e[0] for e in stats]
            
        self.data.append(stats)
        self.n_calls += 1
    
    def on_sampler_end(self, **kwargs):
        
        data = np.array(self.data).T
        x = range(self.n_calls)        
        n_cols = data.shape[0]
            
        fig, ax = plt.subplots(1, n_cols, figsize=(8*n_cols, 5))
        labels = ['$p_L$', 'std[$p_L$]', '$\delta$', 'std[$p_L^{up}$]']
        
        for i in range(n_cols):
            ax[i].plot(x, data[i])
            ax[i].set_xlabel('# of samples')
            ax[i].set_ylabel(labels[i])
            if i != 0:
                ax[i].set_yscale('log')

# %% ../05_callbacks.ipynb 8
class VerboseCircuitExec(Callback):
    
    def on_circuit_end(self, sampler, local_vars):
        circuit = local_vars.get('circuit', None)
        fault_circuit = local_vars.get('fault_circuit', None)
        name = local_vars.get('name', None)
        msmt = local_vars.get('msmt', None)
        if circuit == None:
            print(name)
        elif circuit._noisy:
            faults = [(i,tick) for i, tick in enumerate(fault_circuit._ticks) if tick]
            print(f"{name} -> Faults: {faults} -> Msmt: {msmt}")
        elif "COR" in name:
            cor = [(i,tick) for i, tick in enumerate(circuit._ticks) if tick]
            print(f"{name}: {cor}")
        else:
            print(f"{name} -> Msmt: {msmt}")

# %% ../05_callbacks.ipynb 9
class ErvPerSample(Callback):
    def __init__(self, log_dir=None):
        self.log_dir = log_dir
        self.data = []
        self.n_calls = 0
        
    def on_protocol_begin(self, **kwargs):
        self.erv_vals = []
        
    def on_circuit_end(self, local_vars, **kwargs):
        subset = local_vars.get("subset", None)
        name = local_vars.get("name", None)
        if subset:
            erv_val = local_vars["erv"]
            self.erv_vals.append((name,subset,erv_val))
        
    def on_protocol_end(self, **kwargs):
        self.data.append(self.erv_vals)
        self.n_calls += 1
        
    def on_sampler_end(self, **kwargs):
        data = dict()
        for i, erv_sel in enumerate(self.data):
            for j, (name, subset, erv) in enumerate(erv_sel):
                key = (j, name, subset)
                data[key] = data.get(key, []) + [(i,erv)]
        
        max_levels = max([k[0] for k in data.keys()])
        max_subset_weight = max([sum(k[-1]) for k in data.keys()])
        cmap = lambda p1, p2: (p1, 0, p2)

        plt.figure(figsize=(6,4))
        for k,vlist in sorted(data.items()):
            p1 = k[0] / (max_levels + 1)
            p2 = sum(k[-1]) / max_subset_weight

            xs = [x for x,_ in vlist]
            ys = [np.nan if np.ma.is_masked(y) else y for _,y in vlist]
            plt.plot(xs, ys, '.',label=k)#, color=cmap(p1,p2))
            
        plt.yscale('log')
        plt.legend(ncol=3, loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xlabel('# of samples')
        plt.ylabel('ERV value of selection')
            
        if self.log_dir: 
            self.store(self.log_dir, self.data, ext=self.n_calls)
