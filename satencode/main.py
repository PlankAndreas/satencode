from pysat.solvers import Solver
from ortools.sat.python import cp_model

from satencode.csp.constraints import NotEqual
from satencode.csp.csp_model import CSPModel
from satencode.encoder import Encoder


enc = Encoder()

if False:
    x = [
        enc.pool.id(("x", i))
        for i in range(5)
    ]

    enc.exactly_one(x)

    with Solver(name="cadical195", bootstrap_with=enc.cnf) as solver:

        result = solver.solve()
        if result:
            model = solver.get_model()
            print("Model:", model)
        print("SAT result:", result)



        model = solver.get_model()


 # Create CSP model
cspmodel = CSPModel()

# Create finite domain variables
x = cspmodel.NewIntVar(range(3), "x")
y = cspmodel.NewIntVar(range(3), "y")

# Add CSP constraint
cspmodel.Add(NotEqual(x, y))

enc = Encoder()

# Compile CSP -> CNF
sat_vars = enc.csp_direct_encode(cspmodel)


print("CSP variables:")
for var in cspmodel.variables:
    print(f"  {var.name}: {var.domain}")

print("\nGenerated SAT variables:")
for var, values in sat_vars.items():
    print(var.name, values)


print("\nCNF clauses:")
for clause in enc.cnf.clauses:
    print(clause)

with Solver(bootstrap_with=enc.cnf) as solver:
    print(solver.solve())
    print(solver.get_model())

enc = Encoder()

x = enc.pool.id("x")
y = enc.pool.id("y")

print("x:", x)
print("y:", y)

t = enc.and_(x, y)
print("t:", t)

print("\nCNF:")
for clause in enc.cnf.clauses:
    print(clause)

with Solver(bootstrap_with=enc.cnf) as solver:
    print("SAT:", solver.solve())
    print("Model:", solver.get_model())


