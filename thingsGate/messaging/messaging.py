import time
import zmq
import itertools

from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

from log.logger import logger
from random import randrange

class zmqLazyPirateClient():

  def __init__(self, port, timeout=2500, retries=3):
    self.requestTimeout = timeout # in ms
    self.requestRetries = retries
    self.serverEndpoint = "tcp://localhost:"+port
    self.context = zmq.Context()
    self.connectToServer()

  def connectToServer(self):
    logger("Connecting to server…")
    self.client = self.context.socket(zmq.REQ)
    self.client.connect(self.serverEndpoint)

  def closeAndRemoveSocket(self):
    self.client.setsockopt(zmq.LINGER, 0)
    self.client.close()

  def send(self, message):
    request = str(message).encode()
    logger(f"Sending {request}")
    self.client.send(request)

    retries_left = self.requestRetries
    while True:
      if (self.client.poll(self.requestTimeout) & zmq.POLLIN) != 0:
        reply = self.client.recv()
        if int(reply) == 1:
          logger(f"Server replied OK  {reply}")
          return "Server replied OK"
        else:
          logger(f"Malformed reply from server:  {reply}")
          continue

      retries_left -= 1
      logger("No response from server")
      # Socket is confused. Close and remove it.
      self.closeAndRemoveSocket()
      if retries_left == 0:
        logger("Server seems to be offline, abandoning")
        return "Server seems to be offline"
      else:
        logger("Reconnecting to server…")
        # Create new connection
        self.connectToServer()
        logger(f"Resending  {request}")
        self.client.send(request)

class zmqLazyPirateServer():
    def __init__(self, port):
      self.serverEndpoint = "tcp://*:"+port
      self.context = zmq.Context()
      self.server = self.context.socket(zmq.REP)
      self.server.bind(self.serverEndpoint)

    def receive(self):
      self.requestMessage = self.server.recv()
      return str(self.requestMessage, 'utf-8')

    def reply(self,replyMessage):
    	self.server.send(bytes(replyMessage, 'utf-8'))

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

class zmqRequester():

  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.REQ)
    self.socket.connect("tcp://localhost:"+port)
    self.port=port

  def request(self, topic, message):
    logger(Fore.CYAN + f"timestamp: {time.ctime()}, topic: {topic}, message: {message}" + Style.RESET_ALL)
    string= topic+" "+ message
    self.socket.send(bytes(string, 'utf-8'))
    message = self.socket.recv()
    answerString = str(message, 'utf-8')
    topic, message = answerString.split()
    return topic, message

class zmqReplier():
  def __init__(self,port):
    self.context = zmq.Context()  
    self.socket = self.context.socket(zmq.REP)
    self.socket.connect("tcp://localhost:"+port)
    self.port=port

  def receive(self):
    message = self.socket.recv()
    answerString = str(message, 'utf-8')
    topic, message = answerString.split()
    logger(Fore.RED + f"timestamp: {time.ctime()}, topic: {topic}, message: {message}" + Style.RESET_ALL)
    return topic, message
  
  def reply(self, topic, message):
    string= topic+" "+ message
    self.socket.send(bytes(string, 'utf-8'))
