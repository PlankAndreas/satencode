"""Z3 vs. PySAT (manual / primitive / high-level) on the MemorySAT model.

Per instance and mode: search the minimal T (like main.py), and report
  * T*                      minimal number of timesteps
  * encode / solve          time at T* (solve without the extra solve in evaluate())
  * search                  total encode+solve time over T = 2..T*
  * size                    clauses (PySAT) / assertions (Z3) at T*
Z3's solution at T* is additionally checked against the high-level CNF.
"""
import contextlib
import io
import json
import sys
import time

import _paths  # noqa: E402,F401

import z3  # noqa: E402
from pysat.solvers import Cadical153  # noqa: E402

import mqt.ionshuttler.single_shuttler.memory_sat as ms  # noqa: E402

_paths.check_local(ms)

INPUTS = _paths.INPUTS

MODES = {
    "z3": (ms.SolverMode.Z3, ms.PYSATSubMode.MANUAL, ms.SATEncodingMode.Primitive),
    "manual": (ms.SolverMode.PYSAT, ms.PYSATSubMode.MANUAL, ms.SATEncodingMode.Primitive),
    "primitive": (ms.SolverMode.PYSAT, ms.PYSATSubMode.SATENCODE, ms.SATEncodingMode.Primitive),
    "highlevel": (ms.SolverMode.PYSAT, ms.PYSATSubMode.SATENCODE, ms.SATEncodingMode.HighLevel),
}

Z3_TIMEOUT_S = 300      # per single check
MODE_BUDGET_S = 1200    # per instance and mode (whole T search)


def load(name):
    with open(f"{INPUTS}/{name}.json") as f:
        cfg = json.load(f)
    seq = [q[0] if len(q) == 1 else tuple(q) for q in cfg["qu_alg"]]
    return tuple(cfg["arch"]), cfg["num_ion_chains"], seq


INSTANCES = [
    ("2x2 ions3 seq3", (2, 2, 1, 1), 3, [0, 1, 2]),
    ("2x2 ions3 tuples", (2, 2, 1, 1), 3, [2, (0, 2), 1, (0, 1)]),
    ("2x2 chain2 ions3", (2, 2, 2, 2), 3, [0, 2, (0, 1)]),
    ("3x3 ions4 qft-ish", (3, 3, 1, 1), 4, [3, (0, 3), (1, 3), 2, (0, 2)]),
    ("full_register_access", *load("full_register_access")),
    ("qft_05", *load("qft_05")),
]


class _NoCheck:
    """Stands in for z3.Solver.check during evaluate() so we can time it ourselves."""


def build(mode, arch, num_ions, seq, T):
    ms.SOLVER_MODE, ms.PYSATSUBMODE, ms.SAT_ENCODING_MODE = MODES[mode]
    m, n, v, h = arch
    graph = ms.create_graph(m, n, v, h)
    traps = [e for e in graph.edges() if graph.get_edge_data(*e)["edge_type"] == "trap"][:num_ions]
    sat = ms.MemorySAT(graph, h, v, list(range(num_ions)), T)

    # evaluate() both encodes and solves (twice); disable solving while encoding
    if mode == "z3":
        sat.s.check = lambda *a: z3.unknown
    else:
        sat.solve_with_pysat = lambda: None

    t0 = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        sat.create_constraints(traps)
        sat.evaluate(seq, num_ions)
    return sat, time.perf_counter() - t0


def solve(mode, sat):
    t0 = time.perf_counter()
    if mode == "z3":
        sat.s.set("timeout", Z3_TIMEOUT_S * 1000)
        res = z3.Solver.check(sat.s)
        if res == z3.sat:
            sat.model = sat.s.model()
        res = True if res == z3.sat else False if res == z3.unsat else None  # None = timeout
    else:
        with Cadical153(bootstrap_with=sat.cnf.clauses) as s:
            res = s.solve()
            sat.solver_model = s.get_model() if res else None
    return res, time.perf_counter() - t0


def size(mode, sat):
    if mode == "z3":
        return f"{len(sat.s.assertions()):8d} assertions"
    return f"{len(sat.cnf.clauses):8d} clauses   "


def z3_accepted_by_cnf(sat_z3, arch, num_ions, seq, T):
    sat_hl, _ = build("highlevel", arch, num_ions, seq, T)
    model = sat_z3.model
    lits = []
    for t in range(T):
        for e in range(len(sat_z3.graph.edges())):
            for ion in range(num_ions):
                val = z3.is_true(model.eval(sat_z3.states[t][e][ion], model_completion=True))
                vid = sat_hl.pool.id(("state", t, e, ion))
                lits.append(vid if val else -vid)
        for i in range(len(seq)):
            val = z3.is_true(model.eval(sat_z3.seq_index[t][i], model_completion=True))
            vid = sat_hl.pool.id(("seq", t, i))
            lits.append(vid if val else -vid)
    with Cadical153(bootstrap_with=sat_hl.cnf.clauses) as s:
        return s.solve(assumptions=lits)


def run_mode(mode, arch, num_ions, seq):
    search = 0.0
    for T in range(2, 51):
        sat, t_enc = build(mode, arch, num_ions, seq, T)
        res, t_sol = solve(mode, sat)
        search += t_enc + t_sol
        if res is None:
            return dict(T=None, note=f"Z3 timeout at T={T}", search=search)
        if res:
            return dict(T=T, enc=t_enc, sol=t_sol, search=search, size=size(mode, sat), sat=sat)
        if search > MODE_BUDGET_S:
            return dict(T=None, note=f"budget exceeded at T={T}", search=search)
    return dict(T=None, note="no solution up to T=50", search=search)


def main():
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    for name, arch, num_ions, seq in INSTANCES:
        if only and name not in only:
            continue
        print(f"\n### {name}  arch={arch} ions={num_ions} gates={len(seq)}", flush=True)
        results = {}
        for mode in MODES:
            r = run_mode(mode, arch, num_ions, seq)
            results[mode] = r
            if r["T"] is None:
                print(f"  {mode:10s} T*=--  {r['note']}  (search {r['search']:.1f}s)", flush=True)
            else:
                print(
                    f"  {mode:10s} T*={r['T']:<3d} {r['size']}  encode {r['enc']:7.2f}s"
                    f"  solve {r['sol']:7.2f}s  | search total {r['search']:8.1f}s",
                    flush=True,
                )

        ts = {m: r["T"] for m, r in results.items() if r["T"] is not None}
        if len(set(ts.values())) > 1:
            print("  !! minimal T differs:", ts)
        elif results["z3"]["T"] is not None:
            ok = z3_accepted_by_cnf(results["z3"]["sat"], arch, num_ions, seq, results["z3"]["T"])
            print(f"  Z3 solution accepted by high-level CNF: {ok}", flush=True)


if __name__ == "__main__":
    main()
