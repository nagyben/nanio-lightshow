#!/usr/bin/python3

# logger

import logging

logger = logging.getLogger("nanio-lightshow")
logger.setLevel(logging.DEBUG)

# log file handler - reports server logs
fh = logging.FileHandler('nanio-lightshow.log')
fh.setLevel(logging.DEBUG)

# log everything else to console output
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to both handlers
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
# logger.addHandler(fh)
logger.addHandler(ch)
