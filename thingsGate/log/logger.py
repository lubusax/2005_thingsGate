from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

from common.common import nowInSecondsAndMilliseconds

import logging, logging.config

logging.config.fileConfig(fname='./data/logging.conf', disable_existing_loggers=False)

def loggerTIMESTAMP(message):
  loggerDEBUGdim("TIMESTAMP - "+ message + f" : {nowInSecondsAndMilliseconds()}")

def loggerTIMESTAMPred(messageRED, messageDIMMED=""):
  loggerTIMESTAMP(Fore.RED+messageRED+Fore.RESET+messageDIMMED)

######################

def loggerDEBUG(message):
  logging.debug(message)

def loggerDEBUGdim(message):
  loggerDEBUG(Style.DIM + message + Style.RESET_ALL)

def loggerDEBUGredDIM(messageRED, messageDIMMED=""):
  loggerDEBUGdim(Fore.RED+messageRED+Fore.RESET+messageDIMMED)

#######################

def loggerINFO(message):
  logging.info(message)

def loggerINFOdim(message):
  loggerINFO(Style.DIM + message + Style.RESET_ALL)

def loggerINFOredDIM(messageRED, messageDIMMED=""):
  loggerINFOdim(Fore.RED+messageRED+Fore.RESET+messageDIMMED)

########################

def loggerWARNING(message):
  logging.warning(message)

########################

def loggerERROR(message):
  logging.error(message)

def loggerERRORdim(message):
  loggerERROR(Style.DIM + message + Style.RESET_ALL)

def loggerERRORredDIM(messageRED, messageDIMMED=""):
  loggerERRORdim(Fore.RED+messageRED+Fore.RESET+messageDIMMED)

########################

def loggerCRITICAL(message):
  logging.critical(message)

