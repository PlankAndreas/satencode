from satencode.primitives.encodings import and_, or_, xor

def half_adder(enc, a, b):
    s = xor(enc, a, b)
    c = and_(enc, a, b)
    return s, c


def full_adder(enc, a, b, carry_in):
    ab_xor = xor(enc, a, b)

    s = xor(enc, ab_xor, carry_in)

    carry = or_(
        enc,
        and_(enc, a, b),
        and_(enc, ab_xor, carry_in)
    )

    return s, carry

def ripple_carry_adder(enc, a_bits, b_bits):
    n = len(a_bits)
    assert n == len(b_bits), "Both inputs must have the same number of bits"

    sum_bits = []
    carry = enc.false()  # Initial carry is 0

    for i in range(n):
        s, carry = full_adder(enc, a_bits[i], b_bits[i], carry)
        sum_bits.append(s)

    return sum_bits, carry

def binary_incrementer(enc, bits):
    result = []
    carry = enc.true()

    for bit in bits:
        s = xor(enc, bit, carry)
        carry = and_(enc, bit, carry)
        result.append(s)

    return result, carry

def binary_decrementer(enc, bits):
    result = []
    borrow = enc.true()

    for bit in bits:
        diff = xor(enc, bit, borrow)
        borrow = and_(enc, -bit, borrow)
        result.append(diff)

    return result, borrow

def binary_multiplier(enc, a_bits, b_bits): 
    n = len(a_bits)
    m = len(b_bits)
    product_bits = [enc.false()] * (n + m)  # Initialize product bits to 0

    for i in range(m):
        # Create partial product for b_bits[i]
        partial_product = [and_(enc, a_bit, b_bits[i]) for a_bit in a_bits]
        # Shift the partial product by i positions
        shifted_partial_product = (
            [enc.false()] * i
            + partial_product
            + [enc.false()] * (n + m - i - len(partial_product))
        )
        # Add the shifted partial product to the current product
        product_bits, _ = ripple_carry_adder(enc, product_bits, shifted_partial_product)

    return product_bits