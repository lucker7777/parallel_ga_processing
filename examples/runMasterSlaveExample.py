from algorithmRunners import run_master_slave_ga
from .masterSlave import MasterSlave
if __name__ == '__main__':
    ins = MasterSlave(population_size=10, chromosome_size=4,
                      number_of_generations=100)
    run_master_slave_ga(ins)
