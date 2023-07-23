# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/06a_sampler.tree.ipynb.

# %% auto 0
__all__ = ['draw_tree', 'Constant', 'Delta', 'Variable', 'Tree']

# %% ../../nbs/06a_sampler.tree.ipynb 3
from anytree import RenderTree, PreOrderIter, Node, NodeMixin
import qsample.math as math
import numpy as np
import itertools as it
import pydot

from fastcore.test import *

# %% ../../nbs/06a_sampler.tree.ipynb 4
def draw_tree(tree, verbose=False, path=None):
    """Generate and return PNG image of `tree`

    To display the image in command line call .show() on the returned
    PIL image object.

    Parameters
    ----------
    path : str or None
        File path to save png image to, if None only display image

    Returns
    -------
    PNG image
        Image of `CountTree`
    """

    def gen_node(node):
        """Generate pydot.Node object from `Constant` of `Variable`
        
        Parameters
        ----------
        node : Constant or Variable
            `CountNode` to generate pydot.Node object from

        Returns
        -------
        pydot.Node
            Graphical representation of node
        """
        if isinstance(node, Variable):
            color = "#ff0000" if node in tree.marked else "black"
            return pydot.Node(hex(id(node)), label=f"{node.name} : {node.count}", style="filled", color=color, fillcolor="white", shape="ellipse")
        if isinstance(node, Delta):
            return pydot.Node(hex(id(node)), label=f"δ", style="filled", fillcolor="#efefef", shape="box")
        if isinstance(node, Constant):
            return pydot.Node(hex(id(node)), label=f"{node.name} : {node.count}", style="filled", fillcolor="white", shape="box")

    def edgeattrfunc(node, child):
        """
        Parameters
        ----------
        node : Constant or Variable
            Parent node of a (node, child) pair
        child : 
            Child node of a (node, child) pair

        Returns
        -------
        dict
            Specification of the thickness of the edge between `node` and `child`
        """
        weight = 0 if tree.root.count == 0 or isinstance(child, Delta) else 10.0 * child.count / tree.root.count 
        weight = min(weight, 5.0) if weight > 5.0 else max(weight, 0.2)
        return {"penwidth": str(weight)}

    G = pydot.Dot(graph_type="digraph")

    for node in PreOrderIter(tree.root):
        if not verbose and (isinstance(node, Delta) or node.count == 0): 
            continue
        nodeA = gen_node(node)
        G.add_node(nodeA)
        for child in node.children:
            if not verbose and (isinstance(child, Delta) or child.count == 0): 
                continue
            nodeB = gen_node(child)
            edge = pydot.Edge(nodeA,nodeB,**edgeattrfunc(node,child))
            G.add_edge(edge)

    if path is not None:
        G.write_png(path)

    from PIL import Image
    from io import BytesIO
    return Image.open(BytesIO(G.create_png()))

# %% ../../nbs/06a_sampler.tree.ipynb 5
class Constant(Node):
    """Representation of a constant value inside `Tree`.
    
    A node in a tree is a uniquely identifiable object containing references
    to at most one parent and possibly many children. The root node has no 
    parent and leaf nodes have not children.
    
    The `Constant` class complements the common tree node by a `count` attribute
    which represents the number of times a node has been visited during sampling.
    
    Attributes
    ----------
    name : str
        The (not necessarily unique) name of the node
    count : int
        Node visit counter variable
    """
    
    def __init__(self, name, count=0, parent=None, const_val=None, **kwargs):
        """
        Parameters
        ----------
        name : str
            The (not necessarily unique) name of the node
        count : int
            Initial value of visit counter variable
        parent : Node
            Reference to parent node object
        """
        self.const_val = const_val
        super().__init__(name=name, count=count, parent=parent, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.count})"
    
class Delta(Node):
    """Representation of subset cutoff error inside `Tree`
    
    Attributes
    ----------
    name : str
        The (not necessarily unique) name of the node
    value : float
        Constant value, if not None is used for virtual Delta nodes (case III in paper)
    """
    
    value = None
    
    def __str__(self):
        return f"{self.name}"
        
class Variable(Node):
    """Representation of a random variable inside `Tree`
    
    Attributes
    ----------
    name : str
        The (not necessarily unique) name of the node
    count : int
        Node visit counter variable
    invariant : bool
        If true variance of this random variable is 0
    ff_deterministic : bool
        If true ...
    circuit_id : str
        Unique identifier of circuit associated to random variable
    """
    
    def __init__(self, name, count=0, invariant=False, ff_deterministic=False, circuit_id=None, **kwargs):
        super().__init__(name=name, count=count, invariant=invariant, 
                         ff_deterministic=ff_deterministic, circuit_id=circuit_id, **kwargs)
        
    @property
    def rate(self):
        """Calculate transition rate from parent node to this node.
        
        We consider `parent.count` coin flips of a Bernoulli random variable X
        for which we would like to determine the rate p that a transition from
        parent node to this node (X=1) took place, i.e.:
        
        .. math:: p(X=1) = self.count / self.parent.count
        
        Returns
        -------
        float
            Value of transition rate in range [0,1]
        """
        if self.is_root:
            return 1.0
        elif self.parent.count == 0:
            return 0.5 # Default value for virtual nodes
        return self.count / self.parent.count
    
    @property
    def var(self):
        """Calculate the variance of the transition rate between
        the parent node and this node. 
        
        As the variance of the Wald interval results in unrealistic variances
        at small sample sizes, we use the variance of the Wilson interval instead.
        
        Returns
        -------
        float
            Value of variance of transition rate
        """
        if self.is_root or self.invariant or self.parent.count == 0:
            return 0.0
        return math.Wilson_var(self.rate, self.parent.count)
    
    def __str__(self):
        return f"{self.name} ({self.count}, {self.var:.2e})"
    
class Tree:
    """Data structure to track sampled `Circuit`s in `Protocol`
    
    Attributes
    ----------
    constants : list
        List of constant values corresponding to circuits' weight subsets
    root : Variable, default: None
        Root node of the tree
    marked : set
        Marked leaf nodes, i.e. due to logical failure
    """
    
    def __init__(self, constants, L=None):
        """
        Parameters
        ----------
        constants : list
            List of constant values corresponding to weight subsets of circuits
        L : int
            Length of longest non-fail path (only relevant for F.T. protocols)
        """
        self.root = None
        self.constants = constants
        self.marked = set()
        
        self.L = L # longest circuit sequence for non-fail paths
        index_tuples = [(cid, sskey) for cid, ss in self.constants.items() for sskey in ss.keys() if sum(sskey) == 0]
        self.M0_index = index_tuples[ np.argmin([self.constants[k][v] for k, v in index_tuples]) ]
    
    def add(self, name, node_type, parent=None, **kwargs):
        """Add node of `node_type` and `name` as child of `parent`.
        
        Parameters
        ----------
        name : str
            Name of node to add
        node_type : Variable, Constant or Delta
            Type of node to add
        parent : Variable or Constant, default: None
            Parent of node to add, only root node has no parent
            
        Returns
        -------
        Variable, Constant or Delta
            Reference to added node
        """
        if parent is None:
            if self.root is None:
                self.root = Variable(name, **kwargs)
            return self.root
        else:
            child_match = [n for n in parent.children if n.name == name]
            if child_match:
                return child_match[0]
            else:  
                return node_type(name=name, parent=parent, **kwargs)
            
    def remove(self, node) -> None:
        """Remove `node` from tree"""
        children = set(node.parent.children)
        children.remove(node)
        node.parent.children = tuple(children)
        node.parent = None
        if node.is_leaf and node in self.marked:
            self.marked.remove(node)
    
    @property
    def root_leaf_rate(self):
        """Sum of rates marked leaf Variable node.count / root.count.
        
        Returns
        -------
        float
            Direct MC estimate of logical failure rate
        """
        return sum([node.count / self.root.count for node in self.marked])
    
    @property
    def root_leaf_var(self):
        """Variance of root leaf rate
        
        Returns
        -------
        float
            Variance of direct MC estimate of logical failure rate
        """
        return math.Wilson_var(self.root_leaf_rate, self.root.count)
    
    def value(self, node):
        """Lookup the value of a node.
        
        For `Variable` return its `rate`, for `Constant` return a corresponding
        value from the `constants` dict, for `Delta` return the cutoff error, i.e.
        1 - sum(constants) in a level
        
        Parameters
        ----------
        node : Constant, Variable or Delta
            Node for which value is returned
            
        Returns
        -------
        float
            Value of node
            
        Raises
        ------
        TypeError
            If `node` has different type than `Variable` or `Constant`
        """
        if type(node) == Variable:
            return node.rate
        elif type(node) == Constant:
            if node.const_val:
                return node.const_val
            else:
                return self.constants[node.parent.circuit_id][node.name]
        elif type(node) == Delta:
            
            if node.parent.count == 0:
                if node.value:
                    return node.value
                else:
                    return self.L * (1 - self.constants[self.M0_index[0]][self.M0_index[1]])
            else: 
                acc = 1.0
                for n in node.siblings:
                    acc -= self.constants[node.parent.circuit_id][n.name]
                return acc
        else:
            raise TypeError(f"Unknown node type: {type(node)}")
    
    def path_weight(self, node):
        """Calculate total path weight from `root` to `node`.
        
        We sum over all subsets in a path. In multi-parameter case we sum over all weights first.
        Note: When there is a circuit in the path which was set `ff_deterministic` by the user, all qubits
        have been reset before execution and the path weight must only be calculated until this node
        
        Parameters
        ----------
        node : Constant
            End node of a path starting from `root`
        
        Returns
        -------
        int
            Weight of path
        """
        weight = 0
        for n in node.iter_path_reverse():
            if type(n) == Constant:
                weight += sum(n.name)
        return weight
    
    def path_prod(self, nodeA, nodeB):
        """Product of node values from `nodeA` to `nodeB`
        
        Parameters
        ----------
        nodeA : Constant, Variable or Delta
            Start node of the path
        nodeB : Constant, Variable or Delta
            End node of the path
        """
        prod = 1
        for node in nodeB.iter_path_reverse():
            prod *= self.value(node)
            if node == nodeA: break
        return prod

    def path_var(self, node, zero_leaf=False):
        """Variance of path from `root` to `node`
        
        Parameters
        ----------
        node : Constant, Variable or Delta
            End node of path for which to calculate variance
        
        Returns
        -------
        float
            Variance of path
        """
        E2 = 1
        VpE2 = 1
        
        for n in node.path:
            v = self.value(n)**2
            if zero_leaf and n == node: v = 0
            E2 *= v
            VpE2 *= (n.var + v) if type(n) == Variable else v
                
        return VpE2 - E2
    
    def subtree_sum(self, node, leaves):
        """Sum of paths from `node` to `leaves`
        
        Parameters
        ----------
        node : Variable, Constant or Delta
            Start node for which to calculate the sum of paths, i.e. subtree
        leaves : Set of Variable, Constant and/or Delta
            Consider only nodes in `leaves` as possible end nodes of paths from `node`
            in the calculation of the path products
            
        Returns
        -------
        float
            Sum of `node`'s subtree
        """
        acc = 0
        for leaf in set(node.leaves).intersection(leaves):
            acc += self.path_prod(node, leaf)
        return acc
    
    def var(self, mode=1):
        """Variance of tree
        
        Parameters
        ----------
        mode : int
            0: upper bound variance, 1: variance of pL (lower bound)
            
        Returns 
        -------
        float
            Variance
        """        
        if mode == 0:
            deltas = [n for n in self.root.leaves if type(n) == Delta]
            leaves = set(self.root.leaves).intersection(self.marked.union(deltas))
        elif mode == 1:
            leaves = set(self.root.leaves).intersection(self.marked)
        else:
            raise Exception(f"Unknown mode {mode}")
        
        ix_nodes = set() # Intersection nodes
        for (nodeA, nodeB) in it.combinations(leaves, 2):
            common_nodes = list(n1 for n1,n2 in zip(nodeA.path, nodeB.path) if n1 == n2)
            if len(common_nodes) > 0 and not common_nodes[-1].is_root:
                ix_nodes.add(common_nodes[-1])
                    
        acc = 0
        for leaf in leaves: # path variances
            if self.path_weight(leaf) >= 1: # exclude weight-0 paths
                acc += self.path_var(leaf)
        
        
        # Add contributions to variance from no-fail paths
        nf_leaves = set(n for n in set(self.root.leaves).difference(self.marked) if type(n)==Variable and not n.invariant and len(n.siblings)==0)
        for leaf in nf_leaves:
            acc += self.path_var(leaf, zero_leaf=True)
            
        for ix_node in ix_nodes:
            cov = 0
            for (nodeA, nodeB) in it.combinations(ix_node.children, 2):

                if type(ix_node) == Constant: # ignore branching ratio (is here random var)
                    accA, accB = 0, 0
                    for child in nodeA.children:
                        accA += self.subtree_sum(child, leaves)
                    for child in nodeB.children:
                        accB += self.subtree_sum(child, leaves)
                    cov += accA * accB
                elif type(ix_node) == Variable:
                    cov += self.subtree_sum(nodeA, leaves) * self.subtree_sum(nodeB, leaves)
                    

            if type(ix_node) == Constant:
                q = ix_node.children[0]
                cov *= 2 * (q.rate * self.path_var(ix_node) - self.path_var(q))
            elif type(ix_node) == Variable:
                cov *= 2 * self.path_var(ix_node)
            else:
                raise Exception(f"Node {ix_node.name} of type {type(ix_node)} shouldn't be common.")
            

            acc += cov
            
        return acc

    @property
    def delta(self):
        """Cutoff error of tree
        
        Returns
        -------
        float
            Sum of delta paths
        """
        acc = 0
        deltas = [n for n in self.root.leaves if type(n) == Delta]
        for dnode in deltas:
            acc += self.path_prod(self.root, dnode)
        return acc
            
    def __str__(self):
        return '\n'.join([f'{pre}{node}' for pre, _, node in RenderTree(self.root)])
    
    def draw(self, verbose=False, path=None):
        return draw_tree(self, path=path, verbose=verbose)
