import networkx as nx
from pysat.solvers import Solver

from satencode.encoder import Encoder
from satencode.graph.variables import vertex_value_variables
from satencode.graph.coloring import graph_coloring

def test_triangle_two_coloring():

    G = nx.Graph()
    G.add_edges_from([
        (1, 2),
        (2, 3),
        (1, 3),
    ])

    enc = Encoder()

    color = vertex_value_variables(enc, G, 2)

    graph_coloring(enc, G, color)

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

    color = vertex_value_variables(enc, G, 3)

    graph_coloring(enc, G, color)

    with Solver(bootstrap_with=enc.cnf) as solver:
        assert solver.solve()