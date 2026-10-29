# Benchmarks: MemorySAT (ion shuttling)

Compares encodings of the MemorySAT model from
[mqt-ionshuttler](https://github.com/munich-quantum-toolkit/ionshuttler) (`single_shuttler/memory_sat.py`).

## Requirements

- A **local** ionshuttler checkout whose `memory_sat.py` has the PySAT/satencode modes
  (`SolverMode`, `PYSATSubMode`, `SATEncodingMode.HighLevel`). These modes are not part of upstream.
  The path defaults to `C:\Users\sirho\Documents\Masterarbeit\Quantum\ionshuttler`;
  set the `IONSHUTTLER` environment variable to use another location.
- `python-sat`, `z3-solver`, `networkx`, and for the CPMpy comparison `cpmpy` + `pindakaas`.
  CPMpy's `pysat` backend needs `pypblib`, which does not build on Windows / Python 3.13,
  so `pindakaas` is used as SAT backend instead.

Run the scripts from this folder, e.g. `python compare_full.py`.

## Scripts

| Script | What it does |
|---|---|
| `compare_modes.py` | manual vs. primitive vs. high-level PySAT encodings: minimal T, CNF size, cross-check of solutions |
| `compare_full.py` | adds Z3; full T search (2..T*) with encode/solve times |
| `cpm_model.py` | the same model in CPMpy (`bool`: 1:1 translation of the Z3 model, `int`: `pos[t, ion]` integer variables) |
| `compare_cpmpy.py` | satencode high-level vs. CPMpy variants, full T search |
| `compare_cpmpy_steps.py` | only T*-1 (UNSAT) and T* (SAT), each step in its own process with a hard timeout |

Every script checks equivalence, not just speed: all modes must find the same minimal T,
and solutions of one mode are passed as assumptions to the high-level CNF.

## Results (`results/`, single runs, 2026-10-28/29)

- `z3_vs_pysat.txt`: Z3 vs. manual / primitive / high-level PySAT, 6 instances
- `cpmpy_search_partial.txt`: CPMpy full search; stopped after ~2 h without progress
  during `full_register_access` (cause not identified)
- `cpmpy_steps.txt`: CPMpy vs. satencode at T*-1 / T* for `full_register_access` and `qft_05`;
  `cpm-bool/pindakaas` at T=26 on `qft_05` crashes reproducibly (segfault, exit code 139)

Summary for `qft_05` (T* = 26):

| | full search T=2..26 | at T* (encode + solve) |
|---|---|---|
| Z3 | 212.3 s | 18.1 + 6.4 s |
| PySAT manual | 65.2 s | 3.4 + 2.9 s |
| satencode primitive | 62.2 s | 3.5 + 4.9 s |
| **satencode high-level** | **47.3 s** | **2.3 + 2.4 s** |
| CPMpy bool / pindakaas | – | crash |
| CPMpy int / pindakaas | – | 31.4 + 14.5 s |
| CPMpy int / CP-SAT (1 thread) | – | 14.9 + 8.0 s |
