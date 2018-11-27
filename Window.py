try:
    from tkinter import *
except:
    from Tkinter import *

from Node import Node
from Line import Line
import json

try:
    import queue as queue
except ImportError:
    import Queue as queue

import os
import pickle
import operator
import random
import string
import globals

class Window:
    types = dict()
    nodes = dict()

    def __init__(self, root, types, nodes):
        self.root = root

        Window.types = types
        Window.nodes = nodes

        self.window = PanedWindow(orient=VERTICAL)
        self.window.pack(fill=BOTH, expand=1)

        self.topWindow = PanedWindow(self.window)
        self.topWindow.pack(fill=X)
        self.treeName = StringVar()
        self.topWindow.add(Label(self.topWindow, text="Name"))
        self.nameEntry = Entry(self.topWindow, textvariable=self.treeName)
        self.topWindow.add(self.nameEntry)
        self.e = Entry()
        self.e.pack()

        self.bottomWindow = PanedWindow(self.window)
        self.bottomWindow.pack(fill=BOTH, expand=1)

        self.nodeList = PanedWindow(self.bottomWindow, orient=VERTICAL)
        self.bottomWindow.add(self.nodeList)
        # self.nodeList.pack(fill=BOTH, expand=1, side=LEFT)

        self.canvasPane = PanedWindow(self.bottomWindow)
        self.bottomWindow.add(self.canvasPane)
        # self.canvasPane.pack(fill=BOTH, expand=1)

        self.canvas = Canvas(self.canvasPane, width=1100, height=900)
        self.canvasPane.add(self.canvas)
        # self.canvas.pack(fill="both", expand=1)
        self.canvas.dnd_accept = self.dnd_accept

        self.prop_window = PanedWindow(self.bottomWindow)
        self.bottomWindow.add(self.prop_window)
        # self.properties.pack(fill=BOTH, expand=1, side=RIGHT)

        newNode = Button(self.nodeList, text="Root", command=lambda title="Root": self.addNode(title))
        newNode.pack(fill=BOTH)

        for type, nodes in types.items():
            newLabel = Label(self.nodeList, text=type)
            newLabel.pack(fill=BOTH)
            for node in nodes:
                newNode = Button(self.nodeList, text=node, command=lambda title=node: self.addNode(title))
                newNode.pack(fill=BOTH)

        newLabel = Label(self.nodeList, text="Roles")
        newLabel.pack(fill=BOTH)
        for file in os.listdir("roles/"):
            roleTitle = file[:-5]
            newNode = Button(self.nodeList, text=roleTitle, command=lambda title=roleTitle: self.addNode(title, isRole=True))
            newNode.pack(fill=BOTH)


        self.menubar = Menu(self.root)
        self.menubar.add_command(label="New", command=lambda: self.newTree())
        self.menubar.add_command(label="Save", command=lambda: self.saveTree())
        self.menubar.add_command(label="Load", command=lambda: self.loadTree())
        self.menubar.add_command(label="Save role", command=lambda: self.saveTree(True))
        self.menubar.add_command(label="Load role", command=lambda: self.loadTree(True))
        self.menubar.add_command(label="Quit", command=self.root.quit)

        self.root.config(menu=self.menubar)

    def newTree(self):
        for child in self.canvas.winfo_children():
            child.destroy()

        for node in Node.nodes:
            for line in node.lines:
                node.canvas.after(10, node.canvas.delete, line.id)
                del line
            del node

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

    def loadTree(self, loadRole=False):
        self.newTree()
        name = self.treeName.get()
        self.e.focus()
        if loadRole:
            file = 'roles/' + name + '.json'
        else:
            file = 'big_jsons/' + name + '.json'
        with open(file, 'r') as f:
            data = json.load(f)

        # Draw nodes
        nodes = data["data"]["trees"][0]["nodes"]
        root_child = None
        for id, node in nodes.items():
            added_node = self.addNode(node["title"], node)
            if not root_child:
                root = self.addNode("Root")
                root_child = node["id"]
                root.drawLine(root, added_node)

        # Loop again to draw lines
        for id, node in nodes.items():
            if "children" in node:
                children = node["children"]
                for child in children:
                    first_node = [n for n in Node.nodes if n.id == int(id)][0]
                    second_node = [n for n in Node.nodes if n.id == int(child)][0]
                    first_node.drawLine(first_node, second_node)

    def addRole(self, role):
        roleList = {}
        changedIDs = {}
        with open("roles/" + role.title + ".json") as f:
            data = json.load(f)

        roleRoot = None
        for id, node in data["data"]["trees"][0]["nodes"].items():
            if not roleRoot:
                roleRoot = globals.randomID()
                changedIDs[id] = roleRoot

            if id in [key for key, _ in changedIDs.items()]:
                id = changedIDs[id]
            else:
                id = globals.randomID()

            if "children" in node:
                for i, child in enumerate(node["children"]):
                    if not child in [key for key, _ in changedIDs.items()]:
                        changedIDs[child] = globals.randomID()

                    node["children"][i] = changedIDs[child]

            node["id"] = id
            roleList[id] = node

        return roleRoot, roleList

    def saveTree(self, saveRole=False):
        name = self.treeName.get()
        que = queue.Queue()
        added = []

        json_file = {"name": name}
        big_json_file = {"name": name}

        data = {"trees": []}
        big_data = {"trees": []}

        tree = {"title": name}
        big_tree = {"title": name}

        for n in Node.nodes:
            if n.title == "Root":
                root_children = self.getChildren(n, added)
                # Check if the root only has 1 child
                if len(root_children) == 1:
                    tree["root"] = root_children[0].id
                    tree["nodes"] = {}
                    big_tree["root"] = root_children[0].id
                    big_tree["nodes"] = {}
                    que.put(root_children[0])
                    added.append(n)
                else:
                    exit("Root has more than 1 child")

                while not que.empty():
                    node_dic = {}
                    curr_node = que.get()
                    node_dic["id"] = curr_node.id
                    node_dic["title"] = curr_node.title
                    children = self.getChildren(curr_node, added)
                    if children:
                        node_dic["children"] = []
                        for child in children:
                            if child.isRole:
                                id, roleChildren = self.addRole(child)
                                node_dic["children"].append(id)
                                for id, roleChild in roleChildren.items():
                                    if "ROLE" in curr_node.properties and "robotID" in curr_node.properties:
                                        roleChild["properties"]["ROLE"] = curr_node.properties["ROLE"].get()
                                        roleChild["properties"]["robotID"] = curr_node.properties["robotID"].get()

                                    tree["nodes"][id] = roleChild
                            else:
                                que.put(child)
                                node_dic["children"].append(child.id)

                    properties = curr_node.properties
                    if properties:
                        if curr_node.title == "Tactic":
                            node_dic["name"] = properties["name"].get()
                        elif curr_node.title == "Role":
                            node_dic["name"] = properties["ROLE"].get()
                        else:
                            node_dic["properties"] = {}
                            for property, value in properties.items():
                                node_dic["properties"][property] = value.get()

                    tree["nodes"][curr_node.id] = node_dic
                    # Save the locations only in the big json

                    node_dic["location"] = {}
                    node_dic["location"]["x"] = curr_node.x_orig
                    node_dic["location"]["y"] = curr_node.y_orig

                    big_tree["nodes"][curr_node.id] = node_dic

                    added.append(curr_node)

        data["trees"].append(tree)
        big_data["trees"].append(big_tree)
        json_file["data"] = data
        big_json_file["data"] = big_data

        if saveRole:
            file = "roles/" + name + ".json"

            with open(file, 'w') as f:
                json.dump(json_file, f)
            os.chmod(file, 0o777)
        else:
            file = "jsons/" + name + ".json"

            with open(file, 'w') as f:
                json.dump(json_file, f)
            os.chmod(file, 0o777)

            file = "big_jsons/" + name + ".json"
            with open(file, 'w') as f:
                json.dump(big_json_file, f)
            os.chmod(file, 0o777)

    def removeProperties(self):
        for item in self.prop_window.winfo_children():
            item.destroy()

    def spawnProperties(self, node):
        self.removeProperties()

        properties = node.properties
        for property, value in properties.items():
            window = PanedWindow(self.prop_window)
            label = Label(window, text=property)
            label.pack(side=LEFT)
            entry = Entry(window, textvariable=properties[property])
            entry.pack(side=RIGHT)
            window.pack(fill=X)

        self.bottomWindow.add(self.prop_window)

    def addNode(self, title, loadProperties=None, isRole = False):
        node = Node(title, Window.nodes[title], loadProperties, isRole)
        if loadProperties:
            node.attach(self.canvas, loadProperties["location"]["x"], loadProperties["location"]["y"])
        else:
            node.attach(self.canvas)

        return node

    def dnd_accept(self, source, event):
        return self

    def dnd_enter(self, source, event):
        self.canvas.focus_set()  # Show highlight border
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = source.canvas.bbox(source.canvas_id)

        dx, dy = x2 - x1, y2 - y1
        self.dndid = self.canvas.create_rectangle(x, y, x + dx, y + dy)
        self.dnd_motion(source, event)

    def dnd_motion(self, source, event):
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = self.canvas.bbox(self.dndid)
        self.canvas.move(self.dndid, x - x1, y - y1)

        if len(source.lines) > 0:
            for line in source.lines:
                if line.a == source:
                    source.canvas.coords(line.id, x, y, line.x2, line.y2)
                    line.changeCoords([x, y, line.x2, line.y2])
                elif line.b == source:
                    source.canvas.coords(line.id, line.x1, line.y1, x, y)
                    line.changeCoords([line.x1, line.y1, x, y])

    def dnd_leave(self, source, event):
        self.root.focus_set()  # Hide highlight border
        self.canvas.delete(self.dndid)
        self.dndid = None

    def dnd_commit(self, source, event):
        self.dnd_leave(source, event)
        x, y = source.where(self.canvas, event)
        source.attach(self.canvas, x, y)

