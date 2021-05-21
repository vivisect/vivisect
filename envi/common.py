import logging

LOG_FORMAT = '%(asctime)s:%(levelname)s:%(name)s: %(message)s' \
             '[%(filename)s:%(funcName)s:%(lineno)s:%(threadName)s]'

EMULOG = 9
SHITE = 8

LOG_LEVELS = (
    logging.CRITICAL,
    logging.ERROR,
    logging.WARN,
    logging.INFO,
    logging.DEBUG,
    EMULOG,
    SHITE,
)

def initLogging(logger, level=None, fmt=LOG_FORMAT):
    '''
    Setup logging and log levels
    '''
    if level:
        if level not in LOG_LEVELS:
            raise ValueError('Invalid log level of %r' % level)
    else:
        level = 'ERROR'

    # Setup logging
    logging.addLevelName(EMULOG, 'EMULOG')
    logging.addLevelName(SHITE, 'SHITE')
    logging.basicConfig(level=level, format=fmt)

    # Set log level for current logger
    logger.setLevel(level)
