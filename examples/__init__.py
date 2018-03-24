from algorithmRunners import launch
import os

if __name__ == '__main__':
    path = str(os.getcwd()) + "/"
    executable = "runFineGrainedExample.py"
    launch(["localhost"], 10, path, executable)
