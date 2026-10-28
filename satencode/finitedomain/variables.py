class FiniteDomainVariable:
    def __init__(self, encoder, name, domain, literals=None):
        self.encoder = encoder
        self.name = name
        self.domain = list(domain)

        if literals is None:
            self._literals = {
                value: encoder.pool.id(f"{name}={value}")
                for value in self.domain
            }
        else:
            self._literals = dict(zip(self.domain, literals))

    def __getitem__(self, value):
        return self._literals[value]

    def literals(self):
        return list(self._literals.values())

    def exactly_one(self):
        self.encoder.exactly_one(self.literals())

    def in_(self, values, polarity=0):
        # Literal that is true iff the variable takes one of the given values
        return self.encoder.or_([self[value] for value in values], polarity=polarity)

class FiniteDomainVariableFamily:
    def __init__(self, encoder, name, indices, domain, literals=None):
        self.encoder = encoder
        self.name = name
        self.domain = list(domain)

        self.variables = {}

        for index in indices:
            variable_literals = None

            if literals is not None:
                variable_literals = literals[index]

            self.variables[index] = FiniteDomainVariable(
                encoder,
                f"{name}[{index}]",
                self.domain,
                variable_literals,
            )

    def __getitem__(self, index):
        return self.variables[index]