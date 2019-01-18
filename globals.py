import string
import random
import os
import sys
from time import sleep

main_window = None
PROJECT_DIR = os.path.dirname(sys.argv[0])
if PROJECT_DIR:
    PROJECT_DIR += "/"


def randomID():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(random.randint(13, 17)))

def findJSONDirectory(folder):
    directory = os.getcwd()
    while True:
        directory = os.path.abspath(os.path.join(directory, ".."))
        if directory.split("/")[-1] == "roboteamtwente":
            directory += "/workspace/src/roboteam_ai/roboteam_ai/src/jsons/" + folder + "/"
            if os.path.exists(directory):
                return directory
            else:
                return False
