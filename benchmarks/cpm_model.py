"""MemorySAT model in CPMpy, following the Z3 encoding in memory_sat.py constraint by constraint.

Two variants:
  bool: state[t, e, ion] Boolean matrix (1:1 translation of the Z3 model)
  int:  pos[t, ion] integer variable (edge index), state(t, e, ion) := pos[t, ion] == e
"""
import sys
from itertools import pairwise

import cpmpy as cp
import networkx as nx

import _paths  # noqa: E402,F401

import mqt.ionshuttler.single_shuttler.memory_sat as ms  # noqa: E402


class Instance:
    """Graph data shared by both variants (same helpers as MemorySAT)."""

    def __init__(self, arch, num_ions, seq, T):
        m, n, v, h = arch
        self.graph = g = ms.create_graph(m, n, v, h)
        self.h, self.v = h, v
        self.T = T
        self.ions = list(range(num_ions))
        self.seq = seq
        self.idc = ms.create_idc_dictionary(g)
        self.E = len(g.edges())
        self.starting_traps = [e for e in g.edges() if g.get_edge_data(*e)["edge_type"] == "trap"][:num_ions]

        for e in g.edges():
            if g.edges[e]["edge_type"] == "entry":
                self.entry = e
            elif g.edges[e]["edge_type"] == "exit":
                self.exit = e
        self.entry_node = min(self.entry)
        self.exit_node = min(self.exit)

        node_type = nx.get_node_attributes(g, "node_type")
        self.junction_nodes = [nd for nd in g.nodes() if node_type[nd] == "junction_node"]
        junction_edges = [
            tuple(sorted(e)) for nd in self.junction_nodes for e in g.edges(nd)
        ]
        self.junction_move_dict = ms.create_graph_dict(g, ms.get_possible_moves_over_junction, h, v)
        self.previous_junction_move_dict = ms.create_graph_dict(
            g, ms.get_possible_previous_edges_from_junction_move, h, v, edges=junction_edges
        )

    def idx(self, e):
        return ms.get_idx_from_idc(self.idc, e)


def build(inst, variant):
    """Returns (model, state_fn, seq) where state_fn(t, e_idx, ion) is a Boolean expression."""
    T, ions, g = inst.T, inst.ions, inst.graph
    cons = []

    if variant == "bool":
        state_vars = cp.boolvar(shape=(T, inst.E, len(ions)), name="state")

        def state(t, e, ion):
            return state_vars[t, e, ion]
    else:
        pos = cp.intvar(0, inst.E - 1, shape=(T, len(ions)), name="pos")

        def state(t, e, ion):
            return pos[t, ion] == e

    seq = cp.boolvar(shape=(T, len(inst.seq)), name="seq")

    # starting configuration
    for k, trap in enumerate(inst.starting_traps):
        for ion in ions:
            cons.append(state(0, inst.idx(trap), ion) if ion == k else ~state(0, inst.idx(trap), ion))
    for e in g.edges():
        if e not in inst.starting_traps:
            cons += [~state(0, inst.idx(e), ion) for ion in ions]

    # MV_CONSTR_1: every ion on exactly one edge (implicit for the int variant)
    if variant == "bool":
        for t in range(1, T):
            for ion in ions:
                cons.append(cp.sum(state(t, e, ion) for e in range(inst.E)) == 1)

    # MV_CONSTR_2: reachable next edge, path free
    for t in range(T - 1):
        for ion in ions:
            for e in g.edges():
                options = []
                for p in inst.junction_move_dict[e] + list(g.edges(e)):
                    path = ms.get_path_between_edges(g, e, p)
                    options.append(cp.all(
                        [state(t + 1, inst.idx(p), ion)]
                        + [~state(t, inst.idx(pe), o) for pe in path for o in ions]
                    ))
                cons.append(state(t, inst.idx(e), ion).implies(cp.any(options)))

    # MV_CONSTR_2 EXTRA: at most one ion crosses each junction per step
    for t in range(1, T):
        for nd in inst.junction_nodes:
            cons.append(cp.sum(
                state(t, inst.idx(je), ion)
                & cp.any(state(t - 1, inst.idx(pp), ion) for pp in inst.previous_junction_move_dict[je])
                for je in g.edges(nd)
                for ion in ions
            ) <= 1)

    # MV_CONSTR_2_EXTRA_EXTRA: at most one ion moves through each node per step
    for t in range(1, T):
        for nd in g.nodes():
            moves = ms.get_possible_moves_through_node(g, inst.idc, nd)
            if moves:
                cons.append(cp.sum(
                    state(t, a, ion) & state(t - 1, b, ion) for ion in ions for a, b in moves
                ) <= 1)

    # MV_CONSTR_3: capacity (entry edge holds 2)
    for t in range(1, T):
        for e in g.edges():
            cap = 2 if g.edges[e]["edge_type"] == "entry" else 1
            cons.append(cp.sum(state(t, inst.idx(e), ion) for ion in ions) <= cap)

    ex, en = inst.idx(inst.exit), inst.idx(inst.entry)
    for t in range(1, T - 1):
        for ion in ions:
            cons.append(state(t, ex, ion).implies(
                state(t + 1, en, ion)
                & cp.any(state(t - 1, inst.idx(c), ion) for c in g.edges(inst.exit_node))
            ))
    for t in range(1, T):
        for ion in ions:
            cons.append(state(t, en, ion).implies(state(t - 1, ex, ion) | state(t - 1, en, ion)))
    for t in range(T - 1):
        for ion in ions:
            cons.append(state(t, en, ion).implies(
                cp.any([state(t + 1, en, ion)] + [state(t + 1, inst.idx(c), ion) for c in g.edges(inst.entry_node)])
            ))
    for ion in ions:
        cons += [~state(T - 1, ex, ion), ~state(T - 1, en, ion)]

    # sequence: gate i at time t means its ion(s) are in the entry edge
    for t in range(T):
        for i, gate in enumerate(inst.seq):
            if isinstance(gate, tuple):
                cons.append(seq[t, i].implies(cp.all(state(t, en, q) for q in gate)))
            else:
                cons.append(seq[t, i].implies(cp.all(
                    [state(t, en, gate)] + [~state(t, en, o) for o in ions if o != gate]
                )))

    # consecutive gates: i at t, j at some later t', no other ion in entry in between
    for i, j in pairwise(range(len(inst.seq))):
        used = set()
        for gate in (inst.seq[i], inst.seq[j]):
            used.update(gate if isinstance(gate, tuple) else (gate,))
        others = [o for o in ions if o not in used]
        cons.append(cp.any(
            cp.all(
                [seq[t, i], seq[t2, j]]
                + [~state(ti, en, o) for o in others for ti in range(t, t2)]
            )
            for t in range(T)
            for t2 in range(t + 1, T)
        ))

    for i in range(len(inst.seq)):
        cons.append(cp.sum(seq[t, i] for t in range(1, T)) <= 1)
    for t in range(1, T):
        cons.append(cp.sum(seq[t, i] for i in range(len(inst.seq))) <= 1)

    return cp.Model(cons), state, seq
