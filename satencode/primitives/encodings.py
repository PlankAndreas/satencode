def add_clause(enc, *lits):
    if len(lits) == 1 and isinstance(lits[0], (list, tuple)):
        clause = list(lits[0])
    else:
        clause = list(lits)

    enc.cnf.append(clause)

def add_unit(enc, lit):
    enc.cnf.append([lit])

def add_binary(enc, a, b):
    enc.cnf.append([a, b])
    

def _cached_gate(enc, kind, lits, polarity):
    # Returns (cache, key, existing_var); cache is None when caching is off
    cache = getattr(enc, "gate_cache", None)
    if cache is None:
        return None, None, None
    key = (kind, frozenset(lits), polarity)
    return cache, key, cache.get(key)

def and_(enc, *args, polarity=0):
    """
    Tseitin AND gate.

    polarity (Plaisted-Greenbaum):
         0: aux <-> AND(lits)
        +1: aux  -> AND(lits)   (aux only used positively)
        -1: aux <-  AND(lits)   (aux only used negatively)
    """

    # Support and_([a,b,c])
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        lits = list(args[0])
    else:
        lits = list(args)

    # If there are no literals, return True
    if len(lits) == 0:
        return enc.true()

    # If there is only one literal, return it
    if len(lits) == 1:
        return lits[0]

    cache, key, cached = _cached_gate(enc, "and", lits, polarity)
    if cached is not None:
        return cached

    # Create a new variable to represent the AND of the literals
    and_var = enc.pool.id()

    # Add clauses to enforce the AND relationship
    if polarity >= 0:
        for lit in lits:
            enc.cnf.append([-and_var, lit])  # If and_var is True, all lits must be True
    if polarity <= 0:
        enc.cnf.append([and_var] + [-lit for lit in lits])  # If all lits are True, and_var must be True

    if cache is not None:
        cache[key] = and_var
    return and_var

def or_(enc, *args, polarity=0):
    """
    Tseitin OR gate. polarity works as in and_.
    """

    # Support or_([a,b,c])
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        lits = list(args[0])
    else:
        lits = list(args)

    # If there are no literals, return False
    if len(lits) == 0:
        return enc.false()

    # If there is only one literal, return it
    if len(lits) == 1:
        return lits[0]

    cache, key, cached = _cached_gate(enc, "or", lits, polarity)
    if cached is not None:
        return cached

    # Create a new variable to represent the OR of the literals
    or_var = enc.pool.id()

    # Add clauses to enforce the OR relationship
    if polarity <= 0:
        for lit in lits:
            enc.cnf.append([-lit, or_var])  # If any lit is True, or_var must be True
    if polarity >= 0:
        enc.cnf.append([-or_var] + lits)  # If or_var is True, some lit must be True

    if cache is not None:
        cache[key] = or_var
    return or_var

def not_(enc, lit):
    return -lit

def implies(enc, a, b):
    # a implies b is equivalent to (not a) or b
    return enc.or_(enc.not_(a), b)

def iff(enc, a, b):
    # a iff b is equivalent to not (a xor b)
    return enc.not_(enc.xor(a, b))

def xor(enc, a, b):
    # a xor b is equivalent to (a and not b) or (not a and b)
    return enc.or_(enc.and_(a, enc.not_(b)), enc.and_(enc.not_(a), b))

def nand(enc, a, b):
    # a nand b is equivalent to not (a and b)
    return enc.not_(enc.and_(a, b))

def nor(enc, a, b):
    # a nor b is equivalent to not (a or b)
    return enc.not_(enc.or_(a, b))    

def mux(enc, sel, a, b):
    # Multiplexer: if sel is True, return a; else return b
    return enc.or_(enc.and_(sel, a), enc.and_(enc.not_(sel), b))

def majority(enc, a, b, c):
    # Majority function: returns True if at least two of the inputs are True
    return enc.or_(enc.and_(a, b), enc.and_(a, c), enc.and_(b, c))



