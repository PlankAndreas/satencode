# satencode
A Python Library that provides several methods to encode popular data structures and architectures.

## Usage

Every building block is a method of `Encoder`, which owns the CNF and the variable pool:

```python
from satencode import Encoder

enc = Encoder()
a, b = enc.pool.id("a"), enc.pool.id("b")
s, carry = enc.half_adder(a, b)
enc.exactly_one([a, b])

x = enc.finite_domain_variable("x", range(3))
y = enc.finite_domain_variable("y", range(3))
enc.transition(x, y, {0: [1], 1: [2], 2: [0]})
```

The functions in the submodules take the encoder as their first argument (`enc`) so they can be
bound as methods; inside the library they call each other through `enc.<method>(...)` as well.
