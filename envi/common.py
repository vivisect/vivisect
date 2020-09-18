import logging

LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
LOG_FORMAT = '%(asctime)s:%(levelname)s:%(name)s: %(message)s' \
             '[%(filename)s:%(funcName)s:%(lineno)s:%(threadName)s]'


def setLogging(logger, level=None):
    if level:
        level = str(level).upper()
        if level not in LOG_LEVELS:
            raise ValueError('Invalid log level of %r' % level)
    else:
        level = 'ERROR'
    logging.basicConfig(level=level, format=LOG_FORMAT)
    logger.setLevel(level)
