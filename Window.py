import tkinter
from Node import Node

class Window:

    def __init__(self, root):
        self.root = root

        self.window = tkinter.PanedWindow()
        self.window.pack(fill=tkinter.BOTH, expand=1)

        self.nodeList = tkinter.PanedWindow(self.window, orient=tkinter.VERTICAL)
        self.window.add(self.nodeList)
        # self.nodeList.pack(fill=tkinter.BOTH, expand=1, side=tkinter.LEFT)

        self.canvasPane = tkinter.PanedWindow(self.window)
        self.window.add(self.canvasPane)
        # self.canvasPane.pack(fill=tkinter.BOTH, expand=1)

        self.canvas = tkinter.Canvas(self.canvasPane, width=500, height=500)
        self.canvasPane.add(self.canvas)
        # self.canvas.pack(fill="both", expand=1)
        self.canvas.dnd_accept = self.dnd_accept

        self.properties = tkinter.PanedWindow(self.window)
        self.window.add(self.properties)
        # self.properties.pack(fill=tkinter.BOTH, expand=1, side=tkinter.RIGHT)

        self.dropdown = tkinter.OptionMenu(self.properties, tkinter.StringVar(self.root), "One", "Two", "Three")
        self.properties.add(self.dropdown)
        # self.dropdown.pack()


        nodes = "Root", "Repeater", "Sequence", "ParallelSequence"
        for node in nodes:
            newNode = tkinter.Button(self.nodeList, text=node, command= lambda name = node: self.addNode(name))
            newNode.pack(fill=tkinter.BOTH)

    def addNode(self, name):
        node = Node(name)
        node.attach(self.canvas)

    def dnd_accept(self, source, event):
        return self

    def dnd_enter(self, source, event):
        self.canvas.focus_set() # Show highlight border
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = source.canvas.bbox(source.id)
        dx, dy = x2-x1, y2-y1
        self.dndid = self.canvas.create_rectangle(x, y, x+dx, y+dy)
        self.dnd_motion(source, event)

    def dnd_motion(self, source, event):
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = self.canvas.bbox(self.dndid)
        self.canvas.move(self.dndid, x-x1, y-y1)

        if len(source.lines) > 0:
            for line in source.lines:
                if line.a == source:
                    source.canvas.coords(line.id, x, y, line.x2, line.y2)
                    line.changeCoords([x, y, line.x2, line.y2])
                elif line.b == source:
                    source.canvas.coords(line.id, line.x1, line.y1, x, y)
                    line.changeCoords([line.x1, line.y1, x, y])

    def dnd_leave(self, source, event):
        self.root.focus_set() # Hide highlight border
        self.canvas.delete(self.dndid)
        self.dndid = None

    def dnd_commit(self, source, event):
        self.dnd_leave(source, event)
        x, y = source.where(self.canvas, event)
        source.attach(self.canvas, x, y)