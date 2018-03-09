import numpy as np
import random, time
from scoop import futures, logger

NUMBER_OF_GENERATIONS = 100
POPULATION_SIZE = 10
CHROMOSOME_SIZE = 4
KNAPSACK_SIZE = 30

class Item(object):
    def __init__(self, volume, weight, name):
        self._weight = weight
        self._volume = volume
        self._name = name

    @property
    def volume(self):
        return self._volume

    @property
    def weight(self):
        return self._weight

    @property
    def name(self):
        return self._name

items = {0: Item(10, 30, 'knife'),
        1: Item(20, 40, 'food'),
        2: Item(5, 5, 'rope'),
        3: Item(10, 15, 'matches')}

def initialize_population():
    """
    Generate the population
    :return: population
    """
    population = []
    for i in range(0, POPULATION_SIZE):
        population.append(gen_individual())
    return population

def gen_individual():
    """
    Generate binary array
    :return: individual's chromosome
    """
    return np.random.randint(2, size=(CHROMOSOME_SIZE))

def crossover(father, mother):
    """
    Exchange the random number of bits
    between father and mother
    :param father
    :param mother
    """
    cross = random.randint(0, CHROMOSOME_SIZE - 1)
    for i in range(0,cross):
        mother[i] = father[i]
    for i in range(cross, CHROMOSOME_SIZE):
        father[i] = mother[i]

def mutation(chromosome):
    """
    Invert one random bit based on probability
    :param chromosome
    """
    if np.random.choice([True, False], p=[0.1, 0.9]):
        rnd = random.randint(0, CHROMOSOME_SIZE - 1)
        chromosome[rnd] = abs(chromosome[rnd] - 1)

def fitness(chromosome):
    """
    Fitness is processed as sum of weights.
    If volume is bigger than limit, fitness is zero
    :param chromosome
    :return: fitness value
    """
    #time.sleep(3)
    logger.info("Processing fitness function DONE: " + str(chromosome))
    fitness_value = 0
    volume_value = 0
    for i in range(0, CHROMOSOME_SIZE):
        fitness_value = fitness_value + chromosome[i] * items.get(i).weight
        volume_value = volume_value + chromosome[i] * items.get(i).volume
    return fitness_value if volume_value <= KNAPSACK_SIZE else 0

def send_individuals_reproduce(population):
    """
    Select individuals for reproduction with probability
    based on fitness value. Weak individuals are removed
    and replaced with newly generated ones.
    :param population
    """

    # retrieve best fitness of population
    best_individual = None
    chromosomes_reproducing = {}
    logger.error(str(population))
    logger.error(str(len(population)))
    fit_values = list(futures.map(fitness, population))
    fitnessmax = max(fit_values)
    logger.info("fit values " + str(fit_values) + " max " + str(fitnessmax))
    # choose individuals for reproduction based on probability
    for i in range(0, POPULATION_SIZE):
        # best individual has 100% probability to reproduce
        # others probability is relative to his
        # weak individuals are replaced with new ones
        prob = fit_values[i] / fitnessmax
        # retrieve best individual, others are randomly selected
        if int(prob) == 1 and best_individual is None:
            logger.info("BEST")
            best_individual = population[i]
        elif np.random.choice([True, False], p=[prob, 1 - prob]):
            chromosomes_reproducing[i] = population[i]

    # if none of individuals were selected
    # try it once again
    if len(chromosomes_reproducing) is 0:
        return
    # remove old population
    del population[:]

    # Reproducing requires two individuals.
    # If number of selected individuals is even
    # put the best individual to the new population.
    # Otherwise, put him to individuals dedicated
    # for reproduction
    logger.info("Actual popul is " + str(chromosomes_reproducing) + " with length " + str(len(chromosomes_reproducing)))
    logger.info("best indiv " + str(best_individual))
    if len(chromosomes_reproducing) % 2 is 0:
        population.append(best_individual)
    else:
        # put the best individual to max index in order to not rewrite existing
        chromosomes_reproducing[POPULATION_SIZE] = best_individual
    # randomly choose pairs for crossover
    # then mutate new individuals and put them to new population
    while bool(chromosomes_reproducing):
        father_index = random.choice(list(chromosomes_reproducing.keys()))
        father = chromosomes_reproducing.pop(father_index)
        mother_index = random.choice(list(chromosomes_reproducing.keys()))
        mother = chromosomes_reproducing.pop(mother_index)
        logger.info("father " + str(father) + " mother " + str(mother))
        crossover(father, mother)
        # mutate
        mutation(father)
        mutation(mother)
        population.append(father)
        population.append(mother)

    # Generate new individuals in order to make new population the same size
    while len(population) is not POPULATION_SIZE:
        population.append(gen_individual())


def find_solution(population):
    """
    Find the best solution
    :param population
    :return: best_weight, chromosome
    """
    max_val = 0
    max_index = None
    fit_values = list(futures.map(fitness, population))
    for i in range(0, POPULATION_SIZE):
        curr_fit = fit_values[i]
        if(curr_fit > max_val):
            max_val = curr_fit
            max_index = i
    return max_val, population[max_index]

if __name__ == '__main__':
    popula = initialize_population()
    for i in range(0, NUMBER_OF_GENERATIONS):
        send_individuals_reproduce(popula)
        logger.info("EJHAAA " + str(popula))
        solution, sol_vec = find_solution(popula)
        logger.info("actual: weight: " + str(solution) + " vector: " + str(sol_vec))
    solution, sol_vec = find_solution(popula)
    logger.info("FINAL RESULT: weight: " + str(solution) + " vector: " + str(sol_vec))