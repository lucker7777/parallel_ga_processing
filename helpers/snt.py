class Snt(object):
    def __init__(self, fit, chromosome):
        self._fit = fit
        self._chromosome = chromosome

    @property
    def fit(self):
        return self._fit

    @property
    def chromosome(self):
        return self._chromosome

    def __str__(self):
        return "Fitness is " + str(self._fit) + " chromosome is " + str(self.chromosome)

    def __repr__(self):
        return self.__str__()