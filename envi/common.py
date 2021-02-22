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

def setLogging(logger, level=None, init=False, fmt=LOG_FORMAT):
    '''
    Setup logging and log levels
    '''
    if init:
        logging.basicConfig(level=logging.WARNING, format=fmt)
        logging.addLevelName(EMULOG, 'EMULOG')

    if level is not None:
        level = str(level).upper()
        if level not in LOG_LEVELS:
            raise ValueError('Invalid log level of %r' % level)
    else:
        level = 'ERROR'
    logger.setLevel(level)
