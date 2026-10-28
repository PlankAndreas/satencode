from pysat.card import CardEnc, EncType


def exactly_one(enc, lits):

    card = CardEnc.equals(
        lits=list(lits),
        bound=1,
        vpool=enc.pool,
        encoding=EncType.totalizer
    )

    enc.cnf.extend(card.clauses)

def at_most_one(enc, lits):
    card = CardEnc.atmost(
        lits=list(lits),
        bound=1,
        vpool=enc.pool,
        encoding=EncType.totalizer
    )

    enc.cnf.extend(card.clauses)

def at_least_k(enc, lits, k):
    # Use the CardEnc class to encode the at least k constraint
    card = CardEnc.atleast(
        lits=list(lits),
        bound=k,
        vpool=enc.pool,
        encoding=EncType.totalizer
    )

    enc.cnf.extend(card.clauses)

def at_most_k(enc, lits, k):
    # Use the CardEnc class to encode the at most k constraint
    card = CardEnc.atmost(
        lits=list(lits),
        bound=k,
        vpool=enc.pool,
        encoding=EncType.totalizer
    )

    enc.cnf.extend(card.clauses)

def exactly_k(enc, lits, k):
    # Use the CardEnc class to encode the exactly k constraint
    card = CardEnc.equals(
        lits=list(lits),
        bound=k,
        vpool=enc.pool,
        encoding=EncType.totalizer
    )

    enc.cnf.extend(card.clauses)   




    