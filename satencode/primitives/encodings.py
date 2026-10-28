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
    

def and_(enc, *args):

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

    # Create a new variable to represent the AND of the literals
    and_var = enc.pool.id()

    # Add clauses to enforce the AND relationship
    for lit in lits:
        enc.cnf.append([-and_var, lit])  # If and_var is True, all lits must be True
    enc.cnf.append([and_var] + [-lit for lit in lits])  # If any lit is False, and_var must be False   

    return and_var  

def or_(enc, *args):

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

    # Create a new variable to represent the OR of the literals
    or_var = enc.pool.id()

    # Add clauses to enforce the OR relationship
    for lit in lits:
        enc.cnf.append([-lit, or_var])  # If any lit is True, or_var must be True
    enc.cnf.append([-or_var] + lits)  # If or_var is False, all lits must be False

    return or_var

def not_(enc, lit):
    return -lit

def implies(enc, a, b):
    # a implies b is equivalent to (not a) or b
    return or_(enc, not_(enc, a), b)

def iff(enc, a, b):
    # a iff b is equivalent to not (a xor b)
    return not_(enc, xor(enc, a, b))

def xor(enc, a, b):
    # a xor b is equivalent to (a and not b) or (not a and b)
    return or_(enc, and_(enc, a, not_(enc, b)), and_(enc, not_(enc, a), b))

def nand(enc, a, b):
    # a nand b is equivalent to not (a and b)
    return not_(enc, and_(enc, a, b))

def nor(enc, a, b):
    # a nor b is equivalent to not (a or b)
    return not_(enc, or_(enc, a, b))    

def mux(enc, sel, a, b):
    # Multiplexer: if sel is True, return a; else return b
    return or_(enc, and_(enc, sel, a), and_(enc, not_(enc, sel), b))

def majority(enc, a, b, c):
    # Majority function: returns True if at least two of the inputs are True
    return or_(enc, and_(enc, a, b), and_(enc, a, c), and_(enc, b, c))



