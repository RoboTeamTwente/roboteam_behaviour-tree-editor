try:
    from tkinter import *
except:
    from Tkinter import *

from Window import Window
import os
from collections import defaultdict
import csv
import globals


def getNodes():
    DIR = globals.PROJECT_DIR + "/config_files/"

    types = defaultdict(list)
    nodes = defaultdict(list)

    for file in os.listdir(DIR):
        with open(DIR + file) as f:
            node_type = file[:-4]
            csv_reader = csv.reader(f)
            for row in csv_reader:
                node = row[0]
                types[node_type].append(row[0])
                nodes[node].extend(row[1:])

    return types, nodes


def main():
    root = Tk()
    root.minsize(width=750, height=500)
    root.winfo_toplevel().title("RTT Behavior Tree Editor")
    types, nodes = getNodes()

    globals.main_window = Window(root, types, nodes)
    root.mainloop()


if __name__ == '__main__':
    main()
