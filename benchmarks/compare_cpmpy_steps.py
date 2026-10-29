"""Measure only T*-1 (UNSAT) and T* (SAT) per mode, each in its own process with a hard timeout.

Usage:
  python compare_cpmpy_steps.py                 run all (instance, mode, T) jobs
  python compare_cpmpy_steps.py --one I M T     worker: one instance/mode/T, prints one result line
"""
import subprocess
import sys
import time

STEP_TIMEOUT_S = 900
JOBS = [  # (instance, T*)
    ("full_register_access", 16),
    ("qft_05", 26),
]
MODES = ["highlevel", "cpm-bool/pindakaas", "cpm-int/pindakaas", "cpm-int/cp-sat"]


def worker(name, mode, T):
    import compare_cpmpy as cc
    import compare_full as cf

    _, arch, num_ions, seq = next(i for i in cf.INSTANCES if i[0] == name)
    if mode == "highlevel":
        sat, t_enc = cf.build(mode, arch, num_ions, seq, T)
        res, t_sol = cf.solve(mode, sat)
    else:
        variant, solver = cc.MODES[mode]
        res, t_enc, t_sol, _, _ = cc.run_cpm(variant, solver, arch, num_ions, seq, T)
    print(f"RESULT {'SAT' if res else 'UNSAT'} encode={t_enc:.2f} solve={t_sol:.2f}", flush=True)


def main():
    for name, t_star in JOBS:
        print(f"\n### {name}  (T* = {t_star})", flush=True)
        for mode in MODES:
            cells = []
            for T in (t_star - 1, t_star):
                t0 = time.perf_counter()
                try:
                    out = subprocess.run(
                        [sys.executable, "-u", __file__, "--one", name, mode, str(T)],
                        capture_output=True, text=True, timeout=STEP_TIMEOUT_S,
                    ).stdout
                    line = next((l for l in out.splitlines() if l.startswith("RESULT")), "ERROR (no result)")
                    cells.append(f"T={T}: {line.removeprefix('RESULT ')}")
                except subprocess.TimeoutExpired:
                    cells.append(f"T={T}: TIMEOUT (>{STEP_TIMEOUT_S}s)")
                cells[-1] += f" [{time.perf_counter() - t0:.0f}s wall]"
            print(f"  {mode:18s} " + "  |  ".join(cells), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--one":
        worker(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        main()
