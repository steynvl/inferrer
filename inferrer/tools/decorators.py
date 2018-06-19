import logging


def inferrer_logger(target_class):
    """
    Class decorator, that adds an instance of
    the logger (self._logger) to the attached
    class.

    :param target_class: Class to decorate with a logger
    """
    if any(isinstance(v, logging.Logger) for v in target_class.__dict__.values()):
        return

    target_class._logger = logging.getLogger(target_class.__name__)
    # handler = logging.FileHandler('/path/to/log_file')
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    fmt = '%(relativeCreated)d: [%(levelname)s] %(module)s:%(funcName)s: %(message)s'
    handler.setFormatter(logging.Formatter(fmt))
    target_class._logger.addHandler(handler)
    target_class._logger.propagate = False

    return target_class
