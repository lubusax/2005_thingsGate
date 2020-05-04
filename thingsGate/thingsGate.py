import os
from crontab.crontabSetup import setupCrontab

dirPath = os.path.dirname(os.path.realpath(__file__))
setupCrontab(dirPath)