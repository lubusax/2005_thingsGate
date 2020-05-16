import os, sys

def minuteTrigger(dirPath):
  fileCrontab = 'crontabTask' # changing this File Name does not have consequences
  taskDir = '/display/'
  taskFileName = 'test3Display'
  file = open(fileCrontab, 'w')
  line = '* * * * * ' + dirPath + taskDir + taskFileName + '\n'
  print("line ", line)
  file.write(line)
  file.close()
  os.system(
    'crontab -u pi ' + fileCrontab)


if __name__ == '__main__':
 
  setupCrontab()
  
