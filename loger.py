import logging
import sys

def get_logger(name = __file__, file = 'log.txt', encoding = 'utf-8'):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s]: %(message)s')

    fh = logging.FileHandler(file, encoding = encoding)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    sh = logging.StreamHandler(stream = sys.stdout)
    sh.setFormatter(formatter)
    log.addHandler(sh)

    return log