"""Compare the MemorySAT encoding modes on small instances.

For every instance and every mode:
  * minimal number of timesteps (must be identical across modes)
  * CNF size at that horizon
  * cross-check: the state/seq assignment found by one mode must be
    accepted (as assumptions) by every other mode at the same horizon.
"""
import contextlib
import io
import sys
import time

import _paths  # noqa: E402,F401

from pysat.solvers import Cadical153  # noqa: E402

import mqt.ionshuttler.single_shuttler.memory_sat as ms  # noqa: E402

_paths.check_local(ms)

MODES = {
    "manual": (ms.PYSATSubMode.MANUAL, ms.SATEncodingMode.Primitive),
    "primitive": (ms.PYSATSubMode.SATENCODE, ms.SATEncodingMode.Primitive),
    "highlevel": (ms.PYSATSubMode.SATENCODE, ms.SATEncodingMode.HighLevel),
}

if len(sys.argv) > 1:
    MODES = {k: v for k, v in MODES.items() if k in sys.argv[1].split(",")}

# (name, arch, num_ions, sequence)
INSTANCES = [
    ("2x2 ions3 seq3", (2, 2, 1, 1), 3, [0, 1, 2]),
    ("2x2 ions3 tuples", (2, 2, 1, 1), 3, [2, (0, 2), 1, (0, 1)]),
    ("3x3 ions4 seq4", (3, 3, 1, 1), 4, [0, 1, 2, 3]),
    ("3x3 ions4 qft-ish", (3, 3, 1, 1), 4, [3, (0, 3), (1, 3), 2, (0, 2)]),
    ("2x2 chain2 ions3", (2, 2, 2, 2), 3, [0, 2, (0, 1)]),
    ("3x3 ions6 full", (3, 3, 1, 1), 6, [0, 1, 2, 3, 4, 5]),
]

MAX_T = 30


def setup(arch):
    m, n, v, h = arch
    graph = ms.create_graph(m, n, v, h)
    return graph, v, h


def build_and_solve(mode, arch, num_ions, seq, T):
    ms.SOLVER_MODE = ms.SolverMode.PYSAT
    ms.PYSATSUBMODE, ms.SAT_ENCODING_MODE = MODES[mode]
    graph, v, h = setup(arch)
    traps = [e for e in graph.edges() if graph.get_edge_data(*e)["edge_type"] == "trap"][:num_ions]
    ions = list(range(num_ions))
    sat = ms.MemorySAT(graph, h, v, ions, T)
    with contextlib.redirect_stdout(io.StringIO()):
        sat.create_constraints(traps)
        res = sat.evaluate(seq, num_ions)
    return sat, res


def projection(sat):
    """Assignment of the named state/seq variables in the found model."""
    model = set(sat.solver_model)
    proj = {}
    for obj, vid in sat.pool.obj2id.items():
        if isinstance(obj, tuple) and obj and obj[0] in ("state", "seq"):
            proj[obj] = vid in model
    return proj


def accepts(sat, proj):
    lits = []
    for obj, val in proj.items():
        if obj in sat.pool.obj2id:
            vid = sat.pool.obj2id[obj]
            lits.append(vid if val else -vid)
    with Cadical153(bootstrap_with=sat.cnf.clauses) as s:
        return s.solve(assumptions=lits)


def main():
    ok = True
    for name, arch, num_ions, seq in INSTANCES:
        print(f"\n### {name}  arch={arch} ions={num_ions} seq={seq}")
        found = {}
        for mode in MODES:
            t0 = time.perf_counter()
            for T in range(2, MAX_T + 1):
                sat, res = build_and_solve(mode, arch, num_ions, seq, T)
                if res:
                    break
            else:
                T, sat = None, None
            dt = time.perf_counter() - t0
            found[mode] = (T, sat)
            size = f"vars={sat.pool.top:7d} clauses={len(sat.cnf.clauses):8d}" if sat else ""
            print(f"  {mode:10s} T*={T}  {size}  ({dt:.1f}s)")

        ts = {m: t for m, (t, _) in found.items()}
        if len(set(ts.values())) != 1:
            ok = False
            print("  !! minimal T differs:", ts)
            continue

        T = next(iter(ts.values()))
        # UNSAT at T-1 is already covered by the minimal-T search.
        for a, (_, sat_a) in found.items():
            proj = projection(sat_a)
            for b in found:
                if a == b:
                    continue
                sat_b, _ = build_and_solve(b, arch, num_ions, seq, T)
                if not accepts(sat_b, proj):
                    ok = False
                    print(f"  !! solution of {a} rejected by {b}")
        print("  cross-check done")
    print("\nALL CONSISTENT" if ok else "\nDIFFERENCES FOUND")


if __name__ == "__main__":
    main()
