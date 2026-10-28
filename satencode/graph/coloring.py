

from satencode.graph.variables import vertex_value_variables
from satencode.cardinality.encodings import exactly_one
from satencode.encoder import Encoder


def graph_coloring(enc, G, color):
    """
    Add graph coloring constraints.

    Args:
        enc: Encoder instance.
        G: NetworkX graph.
        color: Dictionary returned by vertex_value_variables().
    """

    # Every vertex gets exactly one color
    for v in G.nodes:
        exactly_one(enc, color[v])

    # Adjacent vertices may not share a color
    k = len(next(iter(color.values())))

    for u, v in G.edges:
        for c in range(k):
            enc.cnf.append([
                -color[u][c],
                -color[v][c]
            ])