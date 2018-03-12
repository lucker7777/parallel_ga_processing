from geneticAlgorithms.masterSlave import MasterSlave
from scoop import futures, logger


if __name__ == '__main__':
    population_size = 10
    ins = MasterSlave(population_size=population_size, chromosome_size=4,
                      number_of_generations=100)
    solution, sol_vec = ins(None, None)
    logger.info("FINAL RESULT: weight: " + str(solution) + " vector: " + str(sol_vec))