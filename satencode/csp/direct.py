from satencode.csp.constraints import NotEqual

def encode_not_equal(enc, sat_vars, constraint):
    """
    Encode X != Y using direct encoding.

    For every forbidden assignment X=i and Y=i:
        ¬x_i ∨ ¬y_i
    """

    x = constraint.x
    y = constraint.y

    for value in x.domain:
        if value not in sat_vars[y]:
            continue
        enc.cnf.append([
            -sat_vars[x][value],
            -sat_vars[y][value]
        ])

def csp_direct_encode(enc, model):

    sat_vars = {}

    # Create Boolean variables
    for var in model.variables:

        sat_vars[var] = {}

        for value in var.domain:
            sat_vars[var][value] = enc.pool.id(
                f"{var.name}_{value}"
            )

    # Every CSP variable takes exactly one value
    for var in model.variables:
        enc.exactly_one(sat_vars[var].values())


    # Binary constraints
    for c in model.constraints:

        if isinstance(c, NotEqual):
            enc.encode_not_equal(sat_vars, c)
    return sat_vars

