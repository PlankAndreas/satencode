def transition(enc, x, y, allowed):
    """
    Restrict which values y may take, depending on the value of x.

    For every value v in allowed:
        x == v  ->  y in allowed[v]

    Each entry becomes a single clause, no auxiliary variables are needed.
    Values of x that are not in allowed are unconstrained.

    Args:
        enc: Encoder instance.
        x, y: FiniteDomainVariable (e.g. a position at time t and t+1).
        allowed: dict mapping a value of x to an iterable of values of y.
    """
    for v, targets in allowed.items():
        enc.cnf.append([-x[v]] + [y[w] for w in targets])


def guarded_transition(enc, x, y, allowed):
    """
    Like transition, but every target can carry a guard that has to hold too.

    For every value v in allowed:
        x == v  ->  OR over (w, guard) in allowed[v] of (y == w AND guard)

    The (y == w AND guard) terms only occur positively, so they are encoded
    half-reified (one direction of the Tseitin definition).

    Args:
        enc: Encoder instance.
        x, y: FiniteDomainVariable.
        allowed: dict mapping a value of x to an iterable of (w, guard) pairs,
            where guard is a list of literals (empty list for no guard).
    """
    for v, targets in allowed.items():
        options = []
        seen = set()

        for w, guard in targets:
            key = (w, frozenset(guard))
            if key in seen:
                continue
            seen.add(key)

            options.append(enc.and_([y[w]] + list(guard), polarity=1))

        enc.cnf.append([-x[v]] + options)
