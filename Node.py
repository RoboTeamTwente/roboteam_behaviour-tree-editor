try:
    from tkinter import *
except:
    from Tkinter import *
    
import datetime
from Line import Line
from collections import defaultdict

from DndHandler import DndHandler

def dnd_start(source, event):
    h = DndHandler(source, event)
    if h.root:
        return h
    else:
        return None

class Node:

    nodeCounter = 0
    nodes = []

    def __init__(self, name, properties, loadProperties=None):
        self.lines = []
        self.properties = defaultdict()
        self.canvas = self.label = None
        self.name = name
        self.makeNode(properties, loadProperties)

    def makeNode(self, properties, loadProperties):
        try:
            self.id = loadProperties["id"]
        except:
            self.id = Node.nodeCounter
            Node.nodeCounter += 1

        try:
            for prop, value in loadProperties["properties"].items():
                self.properties[prop] = StringVar()
                self.properties[prop].set(value)
        except:
            for prop in properties:
                self.properties[prop] = StringVar()
            print(sys.exc_info()[0])

        Node.nodes.append(self)


    def attach(self, canvas, x=30, y=20):
        if canvas is self.canvas:
            self.canvas.coords(self.canvas_id, x, y)
            return
        if self.canvas:
            self.detach()
        if not canvas:
            return
        label = Button(canvas, text=self.name,
                              relief="raised")
        canvas_id = canvas.create_window(x, y, window=label, anchor="nw")
        self.canvas = canvas
        self.label = label
        self.canvas_id = canvas_id
        label.bind("<ButtonPress>", self.press)

    def drawLine(self, a, b):
        if not a == b:
            try:
                x1 = a.x_orig + a.x_off
                y1 = a.y_orig + a.y_off
                x2 = b.x_orig + b.x_off
                y2 = b.y_orig + b.y_off
            except:
                x1, y1 = a.canvas.coords(a.canvas_id)
                x2, y2 = b.canvas.coords(b.canvas_id)

            lineid = self.canvas.create_line(x1, y1, x2, y2)
            line = Line(lineid, a, b, [x1, y1, x2, y2])
            a.lines.append(line)
            b.lines.append(line)
            self.canvas.coords(lineid, x1, y1, x2, y2)

            self.canvas.pack(fill=BOTH, expand=1)

    def detach(self):
        canvas = self.canvas
        if not canvas:
            return
        canvas_id = self.canvas_id
        label = self.label
        self.canvas = self.label = self.id = None
        canvas.delete(canvas_id)
        label.destroy()

    def press(self, event):
        if dnd_start(self, event):
            # where the pointer is relative to the label widget:
            self.x_off = event.x
            self.y_off = event.y
            # where the widget is relative to the canvas:
            self.x_orig, self.y_orig = self.canvas.coords(self.canvas_id)

    def move(self, event):
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.canvas_id, x, y)


    def putback(self):
        self.canvas.coords(self.canvas_id, self.x_orig, self.y_orig)

    def where(self, canvas, event):
        # where the corner of the canvas is relative to the screen:
        x_org = canvas.winfo_rootx()
        y_org = canvas.winfo_rooty()
        # where the pointer is relative to the canvas widget:
        x = event.x_root - x_org
        y = event.y_root - y_org
        # compensate for initial pointer offset
        return x - self.x_off, y - self.y_off

    def spawnOptions(self):
        pass

    def dnd_end(self, target, event):
        pass