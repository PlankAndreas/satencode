from .variables import IntVar
from .constraints import Constraint


class CSPModel:

    def __init__(self):
        self.variables = []
        self.constraints = []

    def NewIntVar(self, domain, name):

        var = IntVar(name, domain)

        self.variables.append(var)

        return var

    def Add(self, constraint):

        self.constraints.append(constraint)