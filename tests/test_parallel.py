from unittest import TestCase
from helpers import launcher

path = "/tmp/parallelGA/main"


class TestParallel(TestCase):
    def testFineGrained(self):
        executable = "runFineGrainedExample.py"
        launcher.parallel(["localhost"], 10, path, executable)

    def testCoarseGrained(self):
        executable = "runCoarseGrainedExample.py"
        launcher.parallel(["localhost"], 10, path, executable)

    def testMasterSlaveGrained(self):
        executable = "runMasterSlaveExample.py"
        launcher.parallel(["localhost"], 10, path, executable)
