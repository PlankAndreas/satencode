import networkx as nx
from pysat.solvers import Solver

from satencode.encoder import Encoder

def test_triangle_two_coloring():

    G = nx.Graph()
    G.add_edges_from([
        (1, 2),
        (2, 3),
        (1, 3),
    ])

    enc = Encoder()

    color = enc.vertex_value_variables(G, 2)

    enc.graph_coloring(G, color)

    with Solver(bootstrap_with=enc.cnf) as solver:
        assert not solver.solve()


def test_triangle_three_coloring():

    G = nx.Graph()
    G.add_edges_from([
        (1, 2),
        (2, 3),
        (1, 3),
    ])

    enc = Encoder()

    color = enc.vertex_value_variables(G, 3)

    enc.graph_coloring(G, color)

    with Solver(bootstrap_with=enc.cnf) as solver:
        assert solver.solve()