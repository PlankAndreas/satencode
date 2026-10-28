from pysat.formula import CNF, IDPool
from . import primitives
from . import cardinality
from . import arithmetic
from . import bitvector



class Encoder:

    def __init__(self):
        self.cnf = CNF()
        self.pool = IDPool()
        self._true = self.pool.id("__TRUE__")
        self.cnf.append([self._true])

    add_clause = primitives.add_clause
    add_unit = primitives.add_unit
    add_binary = primitives.add_binary
    and_ = primitives.and_
    or_ = primitives.or_
    not_ = primitives.not_
    xor = primitives.xor
    implies = primitives.implies
    iff = primitives.iff
    nand = primitives.nand
    nor = primitives.nor
    mux = primitives.mux
    majority = primitives.majority

    # cardinality
    exactly_one = cardinality.exactly_one
    exactly_k = cardinality.exactly_k
    at_most_one = cardinality.at_most_one
    at_most_k = cardinality.at_most_k
    at_least_k = cardinality.at_least_k

    # arithmetic
    half_adder = arithmetic.half_adder
    full_adder = arithmetic.full_adder
    ripple_carry_adder = arithmetic.ripple_carry_adder
    binary_incrementer = arithmetic.binary_incrementer
    binary_decrementer = arithmetic.binary_decrementer
    binary_multiplier = arithmetic.binary_multiplier

    # bit vectors
    equal_bits = bitvector.equal_bits
    not_equal_bits = bitvector.not_equal_bits
    less_than_bits = bitvector.less_than_bits
    greater_than_bits = bitvector.greater_than_bits
    less_equal_bits = bitvector.less_equal_bits
    greater_equal_bits = bitvector.greater_equal_bits

    def true(self):
        return self._true

    def false(self):
        return -self._true