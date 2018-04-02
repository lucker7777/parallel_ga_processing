from scoop import logger
import socket


def log_method():
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur

    @param logger: The logging object
    """

    def decorator(func):

        def wrapper(*args, **kwargs):
            try:
                logger.info(func.__name__ + " [ENTER] on " + socket.gethostname())
                return func(*args, **kwargs)
            except:
                # log the exception
                err = "There was an exception in  "
                err += func.__name__
                logger.exception(err)

                # re-raise the exception
                raise

        return wrapper

    return decorator
