import math
from parallel_ga_processing.geneticAlgorithms import coarseGrainedBase


class CoarseGrained(coarseGrainedBase.CoarseGrainedBase):

    def fitness(self, chromosome):
        first_sum = 0.0
        second_sum = 0.0
        for c in chromosome:
            first_sum += c ** 2.0
            second_sum += math.cos(2.0 * math.pi * c)
        n = float(len(chromosome))
        return 10 - (-20.0 * math.exp(-0.2 * math.sqrt(first_sum / n)) - math.exp(second_sum / n) + 20 + math.e)




