from itertools import product

from pysat.solvers import Solver

from satencode.encoder import Encoder


def solve(enc, assumptions):
    with Solver(bootstrap_with=enc.cnf) as solver:
        return solver.solve(assumptions=assumptions)


def assign(var, value):
    return [var[v] if v == value else -var[v] for v in var.domain]


def test_in():
    domain = range(4)
    for values in ([1], [0, 2], [1, 2, 3]):
        for value in domain:
            enc = Encoder()
            x = enc.finite_domain_variable("x", domain)
            lit = x.in_(values)

            assert solve(enc, assign(x, value) + [lit]) == (value in values)
            assert solve(enc, assign(x, value) + [-lit]) == (value not in values)


def test_transition():
    domain = range(4)
    allowed = {0: [1, 2], 3: [3]}

    for a, b in product(domain, domain):
        enc = Encoder()
        x = enc.finite_domain_variable("x", domain)
        y = enc.finite_domain_variable("y", domain)
        enc.transition(x, y, allowed)

        expected = a not in allowed or b in allowed[a]
        assert solve(enc, assign(x, a) + assign(y, b)) == expected


def test_guarded_transition():
    domain = range(3)

    for a, b, g in product(domain, domain, [False, True]):
        enc = Encoder()
        x = enc.finite_domain_variable("x", domain)
        y = enc.finite_domain_variable("y", domain)
        guard = enc.pool.id("guard")

        # from 0: to 1 only if guard holds, to 2 always
        enc.guarded_transition(x, y, {0: [(1, [guard]), (2, [])]})

        if a != 0:
            expected = True
        else:
            expected = b == 2 or (b == 1 and g)

        lits = assign(x, a) + assign(y, b) + [guard if g else -guard]
        assert solve(enc, lits) == expected


def test_polarity_gates():
    # polarity +1: aux -> AND(a, b);  polarity -1: aux <- OR(a, b)
    for va, vb, vaux in product([False, True], repeat=3):
        enc = Encoder()
        a, b = enc.pool.id("a"), enc.pool.id("b")
        aux = enc.and_(a, b, polarity=1)
        lits = [a if va else -a, b if vb else -b, aux if vaux else -aux]
        assert solve(enc, lits) == (not vaux or (va and vb))

        enc = Encoder()
        a, b = enc.pool.id("a"), enc.pool.id("b")
        aux = enc.or_(a, b, polarity=-1)
        lits = [a if va else -a, b if vb else -b, aux if vaux else -aux]
        assert solve(enc, lits) == (vaux or not (va or vb))


def test_gate_cache():
    enc = Encoder(cache_gates=True)
    a, b = enc.pool.id("a"), enc.pool.id("b")

    assert enc.and_(a, b) == enc.and_(b, a)
    assert enc.or_(a, b) == enc.or_([b, a])
    assert enc.and_(a, b) != enc.or_(a, b)

    enc = Encoder()
    assert enc.and_(a, b) != enc.and_(a, b)
