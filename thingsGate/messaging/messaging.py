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

  def receive(self):
    string = self.socket.recv_string() # this call is blocking
    topic, message = string.split()
    logger(Fore.GREEN + f"time STAMP: {time.ctime()}; topic:{topic}; message: {message} " + Style.RESET_ALL)
    return topic, message

class zmqPublisher():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.PUB)
    self.socket.bind("tcp://*:"+port)
    self.port=port

  def publish(self, topic, message):
    logger(Fore.CYAN + f"timestamp: {time.ctime()}, topic: {topic}, message: {message}" + Style.RESET_ALL)
    string= topic+" "+ message
    self.socket.send_string(string)