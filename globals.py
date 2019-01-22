import string
import random
import os
import sys
from time import sleep

main_window = None
ai_json_folder = ""

PROJECT_DIR = os.path.dirname(sys.argv[0])
if PROJECT_DIR:
    PROJECT_DIR += "/"

def randomID():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(random.randint(13, 17)))

def findJSONDirectory():
    directory = os.getcwd()
    while True:
        if directory.split("/")[-1] == "roboteamtwente":
            directory += "/workspace/src/roboteam_ai/roboteam_ai/src/jsons/"
            if os.path.exists(directory):
                return directory
            else:
                return False
        elif directory == "home":
            exit("roboteam_ai not found!")

        directory = os.path.abspath(os.path.join(directory, ".."))
