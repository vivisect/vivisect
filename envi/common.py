import logging

EMULOG = 9
LOG_LEVELS = (
        'CRITICAL',
        'ERROR',
        'WARNING',
        'INFO',
        'DEBUG',
        'EMULOG',
        )
LOG_FORMAT = '%(asctime)s:%(levelname)s:%(name)s: %(message)s' \
             '[%(filename)s:%(funcName)s:%(lineno)s:%(threadName)s]'

logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
logging.addLevelName(EMULOG, 'EMULOG')

def setLogging(logger, level=None):
    if level is not None:
        level = str(level).upper()
        if level not in LOG_LEVELS:
            raise ValueError('Invalid log level of %r' % level)
    else:
        level = 'ERROR'
    logger.setLevel(level)
