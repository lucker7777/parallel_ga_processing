import sys
import threading
from scoop import logger, utils
from scoop.launcher import ScoopApp


def launch(hosts_list, num_of_workers, path, executable):
    # Get a list of resources to launch worker(s) on
    hosts = utils.getHosts(None, hosts_list)
    external_hostname = [utils.externalHostname(hosts)]
    # Launch SCOOP
    app = ScoopApp(hosts=hosts, n=num_of_workers, b=1,
                   verbose=4,
                   python_executable=[sys.executable],
                   externalHostname=external_hostname[0],
                   executable=executable,
                   arguments=None,
                   tunnel=False,
                   path=path,
                   debug=False,
                   nice=None,
                   env=utils.getEnv(),
                   profile=None,
                   pythonPath=None,
                   prolog=None, backend='ZMQ')

    interrupt_prevent = threading.Thread(target=app.close)
    try:
        root_task_exit_code = app.run()
    except Exception as e:
        logger.error('Error while launching SCOOP subprocesses:' + str(e))
        root_task_exit_code = -1
    finally:
        # This should not be interrupted (ie. by a KeyboadInterrupt)
        # The only cross-platform way to do it I found was by using a thread.
        interrupt_prevent.start()
        interrupt_prevent.join()

    # Exit with the proper exit code
    print("exit code " + str(root_task_exit_code))
    if root_task_exit_code:
        sys.exit(root_task_exit_code)
