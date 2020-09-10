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
  logging.debug("TIMESTAMP-"+Fore.RED+messageRED+Fore.RESET+Style.DIM+messageDIMMED+ f" : {nowInSecondsAndMilliseconds()}"+Style.RESET_ALL)

######################

def loggerDEBUG(message):
  logging.debug(message)

def loggerDEBUGdim(message):
  loggerDEBUG(Style.DIM + message + Style.RESET_ALL)

def loggerDEBUGredDIM(messageRED, messageDIMMED=""):
  logging.debug(Fore.RED+messageRED+Fore.RESET+Style.DIM+messageDIMMED+Style.RESET_ALL)

#######################

def loggerINFO(message):
  logging.info(message)

def loggerINFOdim(message):
  loggerINFO(Style.DIM + message + Style.RESET_ALL)

def loggerINFOredDIM(messageRED, messageDIMMED=""):
  logging.info(Fore.RED+messageRED+Fore.RESET+Style.DIM+messageDIMMED+Style.RESET_ALL)

########################

def loggerWARNING(message):
  logging.warning(message)

########################

def loggerERROR(message):
  logging.error(message)

def loggerERRORdim(message):
  loggerERROR(Style.DIM + message + Style.RESET_ALL)

def loggerERRORredDIM(messageRED, messageDIMMED=""):
  logging.error(Fore.RED+messageRED+Fore.RESET+Style.DIM+messageDIMMED+Style.RESET_ALL)

########################

def loggerCRITICAL(message):
  logging.critical(message)

