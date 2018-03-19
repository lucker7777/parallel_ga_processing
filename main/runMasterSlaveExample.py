from algorithmRunners import masterSlaveRunner
from geneticAlgorithms import MasterSlave
if __name__ == '__main__':
    ins = MasterSlave(population_size=10, chromosome_size=4,
                      number_of_generations=100)
    masterSlaveRunner.master_slave_runner(ins)
