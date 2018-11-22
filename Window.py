import tkinter
from Node import Node
import json
import queue
import os
import pickle
import operator

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
        self.menubar.add_command(label="Load", command=lambda: self.loadTree())
        self.menubar.add_command(label="Quit", command=self.root.quit)

        self.root.config(menu=self.menubar)

    def getChildren(self, node, added):
        children = []
        for line in node.lines:
            if line.a == node:
                if line.b not in added:
                    children.append(line.b)
            elif line.b == node:
                if line.a not in added:
                    children.append(line.a)
            else:
                exit("Line error")

        return sorted(children, key=operator.attrgetter('x_orig'))


    def loadTree(self):
        file = 'trees/hanlo.p'
        with open(file, 'rb') as f:
            data = pickle.load(f)
            pass

    def saveTree(self):
        name = input("Tree name")
        que = queue.Queue()
        added = []

        json_file = {}
        json_file["name"] = name

        data = {}
        data["trees"] = []
        tree = {}
        tree["title"] = name

        for n in Node.nodes:
            if n.name == "Root":
                root_children = self.getChildren(n, added)
                if len(root_children) == 1:
                    tree["root"] = root_children[0].id
                    tree["nodes"] = {}
                    que.put(root_children[0])
                    added.append(n)
                else:
                    exit("Root has more than 1 child")
                while not que.empty():
                    node_dir = {}
                    curr_node = que.get()
                    node_dir["id"] = curr_node.id
                    node_dir["name"] = curr_node.name
                    children = self.getChildren(curr_node, added)
                    if children:
                        node_dir["children"] = []
                        for child in children:
                            que.put(child)
                            node_dir["children"].append(child.id)

                    properties = curr_node.properties
                    if properties:
                        node_dir["properties"] = {}
                        for property, value in properties.items():
                            node_dir["properties"][property] = value.get()

                    tree["nodes"][curr_node.id] = node_dir
                    added.append(curr_node)

        data["trees"].append(tree)
        json_file["data"] = data

        file = "jsons/" + name + ".json"
        with open(file, 'w') as f:
            json.dump(json_file, f)
        os.chmod(file, 0o777)

        file = "trees/" + name + ".p"
        pickle_nodes = []
        for node in Node.nodes:
            node_dic = {}
            node_dic["name"] = node.name
            node_dic["lines"] = []
            for line in node.lines:
                node_dic["lines"].append([line.id, line.a.id, line.b.id])

            node_dic["x_orig"] = node.x_orig
            node_dic["y_orig"] = node.y_orig
            node_dic["x_off"] = node.x_off
            node_dic["y_off"] = node.y_off
            node_dic["id"] = node.id
            pickle_nodes.append(node_dic)

        with open(file, 'wb') as f:
            pickle.dump(pickle_nodes, f)

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