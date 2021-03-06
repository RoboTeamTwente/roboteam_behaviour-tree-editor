try:
    from tkinter import *
except:
    from Tkinter import *

from Window import Window
import os
from collections import defaultdict
import csv
import globals
import collections
import pprint

pp = pprint.PrettyPrinter()

def getNodes():
    DIR = os.path.abspath(os.path.join(globals.ai_json_folder, "..", "treeinterp/config_files/"))
    types = defaultdict(list)
    nodes = defaultdict(list)

    for file in os.listdir(DIR):
        with open(DIR + "/" + file) as f:
            node_type = file[:-4]
            csv_reader = csv.reader(f)
            for row in csv_reader:
                if len(row) > 0:
                    node = row[0]
                    types[node_type].append(row[0])
                    nodes[node].extend(row[1:])

    for key, value in types.items():
        types[key] = sorted(value, key=lambda s: s.lower())

    return types, nodes


def main():
    root = Tk()
    root.minsize(width=800, height=600)
    root.winfo_toplevel().title("RTT Behavior Tree Editor")
    globals.ai_json_folder = globals.findJSONDirectory()
    types, nodes = getNodes()

    if not globals.ai_json_folder:
        exit("jsons folder in roboteam_ai not found!")

    globals.main_window = Window(root, types, nodes)
    root.mainloop()


if __name__ == '__main__':
    main()
