"""Location of the local ionshuttler checkout (override with the IONSHUTTLER environment variable)."""
import os
import sys

IONSHUTTLER = os.environ.get("IONSHUTTLER", r"C:\Users\sirho\Documents\Masterarbeit\Quantum\ionshuttler")
SRC = os.path.join(IONSHUTTLER, "src")
INPUTS = os.path.join(IONSHUTTLER, "inputs", "algorithms_exact")

# the installed mqt.ionshuttler package would shadow the local memory_sat.py otherwise
if SRC not in sys.path:
    sys.path.insert(0, SRC)


def check_local(module):
    assert os.path.abspath(module.__file__).startswith(os.path.abspath(SRC)), (
        f"{module.__name__} loaded from {module.__file__}, expected the local checkout in {SRC}"
    )
