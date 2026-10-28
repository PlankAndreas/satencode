def equal_bits(enc, x_bits, y_bits):

    assert len(x_bits) == len(y_bits)

    equalities = []

    for xb, yb in zip(x_bits, y_bits):
        equalities.append(enc.iff(xb, yb))

    return enc.and_(equalities)

def not_equal_bits(enc, x_bits, y_bits):

    assert len(x_bits) == len(y_bits)

    inequalities = []

    for xb, yb in zip(x_bits, y_bits):
        inequalities.append(enc.not_(enc.iff(xb, yb)))

    return enc.or_(inequalities)

def less_than_bits(enc, x_bits, y_bits):

    assert len(x_bits) == len(y_bits)

    n = len(x_bits)

    if n == 0:
        return enc.false()

    # Base case for single bit comparison
    if n == 1:
        return enc.and_(enc.not_(x_bits[0]), y_bits[0])

    # Recursive case for multi-bit comparison
    msb_x = x_bits[-1]
    msb_y = y_bits[-1]

    # If the most significant bits are equal, compare the remaining bits
    equal_msb = enc.iff(msb_x, msb_y)
    less_than_remaining = less_than_bits(enc, x_bits[:-1], y_bits[:-1])

    # If the most significant bits are not equal, check if x < y based on the MSB
    less_than_msb = enc.and_(enc.not_(msb_x), msb_y)

    return enc.or_(less_than_msb, enc.and_(equal_msb, less_than_remaining))

def greater_than_bits(enc, x_bits, y_bits):

    return less_than_bits(enc, y_bits, x_bits)

def less_equal_bits(enc, x, y):
    return enc.or_(
        less_than_bits(enc, x, y),
        equal_bits(enc, x, y)
    )

def greater_equal_bits(enc, x, y):
    return enc.or_(
        greater_than_bits(enc, x, y),
        equal_bits(enc, x, y)
    )