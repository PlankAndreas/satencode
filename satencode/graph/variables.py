def vertex_variables(enc, G):
    """
    Create a dictionary of SAT variables for each vertex in the graph G.

    Args:
        enc (Encoder): The Encoder instance to use for creating SAT variables.
        G (networkx.Graph): The input graph.

    Returns:
        dict: A dictionary mapping each vertex in G to its corresponding SAT variable.
    """
    return {v: enc.pool.id(f"v_{v}") for v in G.nodes()}

def vertex_literal(vertex_vars, v, value):
    """
    Get the SAT variable corresponding to a specific vertex and its value.

    Args:
        vertex_vars (dict): A dictionary mapping vertices to their SAT variables.
        v: The vertex for which to get the SAT variable.
        value (bool): The value (True or False) for the vertex.

    Returns:
        int: The SAT variable corresponding to the vertex and its value.
    """
    var = vertex_vars[v]
    return var if value else -var


def vertex_value_variables(enc, G, values):
    """
    Create a list of SAT variables for a vertex v, where each variable corresponds to a possible value of the vertex.
    """
    return {
            v: [
                enc.pool.id(("vertex", v, i))
                for i in range(values)
            ]
            for v in G.nodes
        }

def edge_variables(enc, G):
    """
    Create a dictionary of SAT variables for each edge in the graph G.

    Args:
        enc (Encoder): The Encoder instance to use for creating SAT variables.
        G (networkx.Graph): The input graph.

    Returns:
        dict: A dictionary mapping each edge in G to its corresponding SAT variable.
    """
    return {e: enc.pool.id(f"e_{e[0]}_{e[1]}") for e in G.edges()}  

def edge_variable_value(enc, G,values):
    """
    Create a list of SAT variables for an edge e, where each variable corresponds to a possible value of the edge.
    """
    return {
            e: [
                enc.pool.id(("edge", e, i))
                for i in range(values)
            ]
            for e in G.edges
        }

