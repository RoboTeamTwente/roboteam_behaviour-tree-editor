import tkinter
from Node import Node
import json

class Window:

    types = dict()
    nodes = dict()

    def __init__(self, root, types, nodes):
        self.root = root

        Window.types = types
        Window.nodes = nodes

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

        self.prop_window = tkinter.PanedWindow(self.window)
        self.window.add(self.prop_window)
        # self.properties.pack(fill=tkinter.BOTH, expand=1, side=tkinter.RIGHT)

        newNode = tkinter.Button(self.nodeList, text="Root", command=lambda name="Root": self.addNode(name))
        newNode.pack(fill=tkinter.BOTH)

        for type, nodes in types.items():
            newLabel = tkinter.Label(self.nodeList, text=type)
            newLabel.pack(fill=tkinter.BOTH)
            for node in nodes:
                newNode = tkinter.Button(self.nodeList, text=node, command= lambda name = node: self.addNode(name))
                newNode.pack(fill=tkinter.BOTH)

        self.menubar = tkinter.Menu(self.root)
        self.menubar.add_command(label="Save", command=lambda: self.saveTree())
        self.menubar.add_command(label="Load")
        self.menubar.add_command(label="Quit", command=self.root.quit)

        self.root.config(menu=self.menubar)

    def addNodes(self, added, nodes_list, curr):
        new_node = {}
        new_node["children"] = []
        added.append(curr)
        for node in nodes_list:
            if node.id == curr:
                new_node["name"] = node.name
                new_node["id"] = node.id
                for line in node.lines:
                    if line.a.id == curr:
                        if line.b.id not in added:
                            added.append(line.b.id)
                            nodes_list.extend(self.addNodes(added, nodes_list, line.b.id))
                            new_node["children"].append(line.b.id)
                    else:
                        if line.b.id not in added:
                            added.append(line.b.id)
                            nodes_list.extend(self.addNodes(added, nodes_list, line.a.id))
                            new_node["children"].append(line.a.id)

        nodes_list.append(new_node)
        return nodes_list

    def saveTree(self):
        name = "testJSON"
        data = {}
        data["name"] = name
        data["trees"] = []
        tree = {}
        tree["title"] = name
        tree["nodes"] = []

        for node in Node.nodes:
            if node.name == "Root":
                tree["root"] = node.id
                lines = node.lines
                tree["nodes"] = self.addNodes([],Node.nodes, node.id)

        print(tree["nodes"])


    def removeProperties(self):
        for item in self.prop_window.winfo_children():
            item.destroy()

    def spawnProperties(self, node):
        self.removeProperties()

        properties = node.properties
        for property, value in properties.items():
            window = tkinter.PanedWindow(self.prop_window)
            label = tkinter.Label(window, text=property)
            label.pack(side=tkinter.LEFT)
            entry = tkinter.Entry(window, textvariable=properties[property])
            entry.pack(side=tkinter.RIGHT)
            window.pack(fill=tkinter.X)

        self.window.add(self.prop_window)

    def addNode(self, name):
        print(Window.nodes)
        node = Node(name, Window.nodes[name])
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