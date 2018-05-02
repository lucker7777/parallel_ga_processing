from scoop import logger
from parallel_ga_processing.geneticAlgorithms import MasterSlaveBase


def run_master_slave_ga(population_size, chromosome_size,
                        number_of_generations, fitness):
    ins = MasterSlaveBase(population_size=population_size,
                          chromosome_size=chromosome_size,
                          number_of_generations=number_of_generations,
                          fitness=fitness)
    solution, sol_vec = ins()
    logger.info("FINAL RESULT: fitness: " + str(solution) + " vector: " + str(sol_vec))
    return solution, sol_vec
