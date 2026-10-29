"""CPMpy vs. satencode high-level on the MemorySAT model (same instances as compare_full.py)."""
import sys
import time

import cpmpy as cp
from pysat.solvers import Cadical153

import compare_full as cf
from cpm_model import Instance, build

MODES = {
    "highlevel": None,
    # pysat backend needs pypblib, which does not build on Windows/Python 3.13
    "cpm-bool/pindakaas": ("bool", "pindakaas"),
    "cpm-int/pindakaas": ("int", "pindakaas"),
    "cpm-int/cp-sat": ("int", "ortools"),
}
MODE_BUDGET_S = 1200


def run_cpm(variant, solver, arch, num_ions, seq, T):
    t0 = time.perf_counter()
    inst = Instance(arch, num_ions, seq, T)
    model, state, seqv = build(inst, variant)
    s = cp.SolverLookup.get(solver, model)  # runs CPMpy's transformations + encoding
    t_enc = time.perf_counter() - t0

    t0 = time.perf_counter()
    if solver == "ortools":
        res = s.solve(num_workers=1)
    else:
        res = s.solve()
    t_sol = time.perf_counter() - t0

    size = f"{len(model.constraints):8d} cpm-cons  "
    return res, t_enc, t_sol, size, (inst, state, seqv)


def accepted_by_highlevel(inst, state, seqv, arch, num_ions, seq):
    sat_hl, _ = cf.build("highlevel", arch, num_ions, seq, inst.T)
    lits = []
    for t in range(inst.T):
        for e in range(inst.E):
            for ion in inst.ions:
                vid = sat_hl.pool.id(("state", t, e, ion))
                lits.append(vid if state(t, e, ion).value() else -vid)
        for i in range(len(seq)):
            vid = sat_hl.pool.id(("seq", t, i))
            lits.append(vid if seqv[t, i].value() else -vid)
    with Cadical153(bootstrap_with=sat_hl.cnf.clauses) as s:
        return s.solve(assumptions=lits)


def run_mode(mode, arch, num_ions, seq):
    if MODES[mode] is None:
        return {**cf.run_mode(mode, arch, num_ions, seq), "sol_data": None}
    variant, solver = MODES[mode]
    search = 0.0
    for T in range(2, 51):
        res, t_enc, t_sol, size, data = run_cpm(variant, solver, arch, num_ions, seq, T)
        search += t_enc + t_sol
        if res:
            return dict(T=T, enc=t_enc, sol=t_sol, search=search, size=size, sol_data=data)
        if search > MODE_BUDGET_S:
            return dict(T=None, note=f"budget exceeded at T={T}", search=search)
    return dict(T=None, note="no solution up to T=50", search=search)


def main():
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    for name, arch, num_ions, seq in cf.INSTANCES:
        if only and name not in only:
            continue
        print(f"\n### {name}  arch={arch} ions={num_ions} gates={len(seq)}", flush=True)
        results = {}
        for mode in MODES:
            r = run_mode(mode, arch, num_ions, seq)
            results[mode] = r
            if r["T"] is None:
                print(f"  {mode:18s} T*=--  {r['note']}  (search {r['search']:.1f}s)", flush=True)
            else:
                print(
                    f"  {mode:18s} T*={r['T']:<3d} {r['size']}  encode {r['enc']:7.2f}s"
                    f"  solve {r['sol']:7.2f}s  | search total {r['search']:8.1f}s",
                    flush=True,
                )

        ts = {m: r["T"] for m, r in results.items() if r["T"] is not None}
        if len(set(ts.values())) > 1:
            print("  !! minimal T differs:", ts, flush=True)
        for mode, r in results.items():
            if r.get("sol_data"):
                ok = accepted_by_highlevel(*r["sol_data"], arch, num_ions, seq)
                print(f"  {mode} solution accepted by high-level CNF: {ok}", flush=True)


if __name__ == "__main__":
    main()
