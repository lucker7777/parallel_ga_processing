from helpers import launcher
import os

if __name__ == '__main__':
    path = str(os.getcwd()) + "/"
    executable = "runFineGrainedExample.py"
    launcher.parallel(["localhost"], 10, path, executable)
