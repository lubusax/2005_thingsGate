import time
import zmq

from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

from log.logger import logger
from random import randrange

class zmqSubscriber():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.SUB)
    self.socket.connect("tcp://localhost:"+port)
    self.port=port

  def subscribe(self, topic):
    self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

  def receiveSubscription(self):
    logger(Fore.RED + f"time STAMP before recv_string: {time.ctime()} " + Style.RESET_ALL)
    string = self.socket.recv_string() # this call is blocking
    zipcode, temperature, relhumidity = string.split()
    logger(Fore.GREEN + f"time STAMP: {time.ctime()}; zipcode:{zipcode}; temperature:{temperature}; relhumidity:{relhumidity} " + Style.RESET_ALL)

class zmqPublisher():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.PUB)
    self.socket.bind("tcp://*:"+port)
    self.port=port

  def publish(self):
    zipcode     = randrange(60435, 60438)
    temperature = randrange(14, 24)
    relhumidity = randrange(15, 55)
    logger(Fore.CYAN + f"timestamp: {time.ctime()}, zipcode: {zipcode}, temperature: {temperature}, rel. humidity: {relhumidity}" + Style.RESET_ALL)
    self.socket.send_string("%i %i %i" % (zipcode, temperature, relhumidity))