import logging, logging.config

logging.config.fileConfig(fname='./data/logging.conf', disable_existing_loggers=False)

def logger(message):
  #logging.config.fileConfig(fname='./data/logging.conf', disable_existing_loggers=False)
  logging.debug(message)