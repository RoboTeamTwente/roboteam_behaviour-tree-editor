import string
import random

def initialize():
    main_window = None

def main_window():
    return None

def randomID():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(random.randint(13, 17)))

