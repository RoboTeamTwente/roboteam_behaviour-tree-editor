import string
import random
import os
import sys

main_window = None
PROJECT_DIR = os.path.dirname(sys.argv[0])
print(PROJECT_DIR)

def randomID():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(random.randint(13, 17)))

