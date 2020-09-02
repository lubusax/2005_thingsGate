from random import randint
import itertools
import time
import zmq

from log.logger import logger

from colorama import Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

#from log.logger import logger

def main():
	context = zmq.Context()
	server = context.socket(zmq.REP)
	server.bind("tcp://*:5555")

	for cycles in itertools.count():
		request = server.recv()

		# Simulate various problems, after a few cycles
		if cycles > 3 and randint(0, 3) == 0:
			logger(Fore.BLUE+Back.WHITE+"Simulating a crash"+Style.RESET_ALL)
			break
		elif cycles > 3 and randint(0, 3) == 0:
			logger(Fore.BLUE+Back.WHITE+"Simulating CPU overload"+Style.RESET_ALL)
			time.sleep(2)

		logger(Fore.BLUE+Back.WHITE+f"Normal request {request}" +Style.RESET_ALL)
		time.sleep(1)  # Do some heavy work
		server.send(request)


if __name__ == "__main__":
  main()