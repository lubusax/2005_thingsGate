import logging, logging.config

logging.config.fileConfig(fname='./data/logging.conf', disable_existing_loggers=False)

def loggerDEBUG(message):
  logging.debug(message)

def loggerINFO(message):
  logging.info(message)

def loggerWARNING(message):
  logging.warning(message)

def loggerERROR(message):
  logging.error(message)

def loggerCRITICAL(message):
  logging.critical(message)

