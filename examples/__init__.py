from parallel_ga_processing.algorithmRunners import launch
import os

if __name__ == '__main__':
    path = str(os.getcwd()) + "/"
    executable = "runCoarseGrainedExample.py"
    launch(["localhost"], 20, path, executable)
