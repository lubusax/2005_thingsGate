import os, sys, logging

def setHostname(index):
  file = 'hostname' # changing this File Name does not have consequences
  dir = '/etc/'
  hostname = 'thingsGate'+index
  file = open(dir+file, 'w')
  line = hostname + '\n'
  logging.debug(('setting hostname to: {h}').format(h=hostname))
  file.write(line)
  file.close()
  os.system('sudo service hostname restart')

if __name__ == '__main__':
  index = "00"
  setHostname(index)
  