import logging

def log(*args):
    logger1 = logging.getLogger('Log.Parser')
    logger1.info(' '.join([str(arg) for arg in args]))



