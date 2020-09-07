from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

from common.common import nowInSecondsAndMilliseconds

import logging, logging.config

logging.config.fileConfig(fname='./data/logging.conf', disable_existing_loggers=False)

def loggerDEBUG(message):
  logging.debug(message)

def loggerDEBUGdim(message):
  loggerDEBUG(Style.DIM + message + Style.RESET_ALL)

def loggerTIMESTAMP(message):
  loggerDEBUGdim("TIMESTAMP - "+ message + f" : {nowInSecondsAndMilliseconds()}")

def loggerINFO(message):
  logging.info(message)

def loggerWARNING(message):
  logging.warning(message)

def loggerERROR(message):
  logging.error(message)

def loggerCRITICAL(message):
  logging.critical(message)

