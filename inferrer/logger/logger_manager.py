import os
import logging
from logging.handlers import RotatingFileHandler

from inferrer import ROOT_DIR
from inferrer.logger.singleton import Singleton


class LoggerManager(Singleton):

    def init(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        full_path = '{}/{}.log'.format(ROOT_DIR, logger_name)

        if not os.path.isdir(ROOT_DIR):
            os.makedirs(ROOT_DIR)

        try:
            rotating_handler = RotatingFileHandler(
                full_path,
                mode='a',
                maxBytes=10 * 1024 * 1024,
                backupCount=5
            )
        except:
            raise IOError('Could not create/open file\'{}\''
                          .format(full_path))

        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)-4s] %(message)s',
            datefmt='%F %H:%M:%S'
        )

        rotating_handler.setFormatter(formatter)
        self.logger.addHandler(rotating_handler)

    def get_logger(self, logger_name):
        return logging.getLogger(logger_name)
