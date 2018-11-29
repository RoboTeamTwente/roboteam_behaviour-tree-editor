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

        self.canvasPane = PanedWindow(self.bottomWindow)
        self.bottomWindow.add(self.canvasPane)

        self.canvas = Canvas(self.canvasPane, width=1100, height=900)
        self.canvasPane.add(self.canvas)
        self.canvas.dnd_accept = self.dnd_accept

        self.prop_window = PanedWindow(self.bottomWindow)
        self.bottomWindow.add(self.prop_window)

        # Spawn root node
        newNode = Button(self.nodeList, text="Root", command=lambda title="Root": self.addNode(title))
        newNode.pack(fill=BOTH)

        # Spawn node types
        for type, nodes in types.items():
            nodeWindow = PanedWindow(self.nodeList)
            newLabel = Button(nodeWindow, text=type.capitalize(), bd=0, command=lambda type=type, nodeWindow=nodeWindow: self.toggleNodes(type, nodeWindow))
            newLabel.pack(fill=BOTH)
            nodeWindow.pack(fill=BOTH)

        # Spawn role nodes
        nodeWindow = PanedWindow(self.nodeList)
        newLabel = Button(nodeWindow, text="Roles", bd=0, command=lambda nodeWindow=nodeWindow: self.toggleNodes("roles", nodeWindow))
        newLabel.pack(fill=BOTH)
        nodeWindow.pack(fill=BOTH)


        self.menubar = Menu(self.root)
        self.menubar.add_command(label="New", command=lambda: self.newTree())
        self.menubar.add_command(label="Save tree", command=lambda: self.saveTree())
        self.menubar.add_command(label="Load tree", command=lambda: self.loadTree())
        self.menubar.add_command(label="Save role", command=lambda: self.saveTree(True))
        self.menubar.add_command(label="Load role", command=lambda: self.loadTree(True))
        self.menubar.add_command(label="Export JSON", command=lambda: self.saveJSON())
        self.menubar.add_command(label="Quit", command=self.root.quit)

        self.root.config(menu=self.menubar)

    def toggleNodes(self, type, nodeWindow):
        if type == "roles":
            nodes = [file[:-5] for file in os.listdir("roles/")]
            isRole = True
        else:
            nodes = Window.types[type]
            isRole = False

        destroying = False
        for button in nodeWindow.winfo_children():
            if button["text"] in nodes:
                button.destroy()
                destroying = True

        if not destroying:
            for node in nodes:
                newNode = Button(nodeWindow, text=node, command=lambda title=node: self.addNode(title, isRole=isRole))
                newNode.pack(fill=BOTH)

    def newTree(self):
        for child in self.canvas.winfo_children():
            child.destroy()

        for node in Node.nodes:
            for line in Line.lines:
                node.canvas.after(10, node.canvas.delete, line.id)
                del line
            Line.lines = []
            del node
        Node.nodes = []

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

        if "x_orig" in children:
            return sorted(children, key=operator.attrgetter('x_orig'))
        else:
            return [child for _, child in sorted(zip([x for x, y in [a.canvas.coords(a.canvas_id) for a in children]], children))]

    def loadTree(self, loadRole=False):
        self.newTree()
        name = self.treeName.get()
        self.e.focus()
        if loadRole:
            file = 'roles/' + name + '.json'
        else:
            file = 'saved_trees/' + name + '.json'
        with open(file, 'r') as f:
            data = json.load(f)

        # Draw nodes
        nodes = data["data"]["trees"][0]["nodes"]
        root_child = data["data"]["trees"][0]["root"]
        for id, node in nodes.items():
            added_node = self.addNode(node["title"], node, node["isRole"])
            if id == root_child:
                root_properties = {"location": {}}
                root_properties["location"]["x"] = nodes[id]["location"]["x"]
                root_properties["location"]["y"] = nodes[id]["location"]["y"] - 100

                root = self.addNode("Root", root_properties)
                root_child = node["id"]
                root.drawLine(root, added_node)

        # Loop again to draw lines
        for id, node in nodes.items():
            if "children" in node:
                children = node["children"]
                for child in children:
                    first_node = [n for n in Node.nodes if n.id == id][0]
                    second_node = [n for n in Node.nodes if n.id == child][0]
                    first_node.drawLine(first_node, second_node)

    def addRole(self, role):
        roleList = {}
        changedIDs = {}
        with open("roles/" + role.title + ".json") as f:
            data = json.load(f)

        roleRoot = globals.randomID()
        roleList[roleRoot] = {"id": roleRoot}
        roleList[roleRoot]["title"] = "Role"
        roleList[roleRoot]["name"] = role.properties["ROLE"].get()
        childRoot = globals.randomID()
        changedIDs[data["data"]["trees"][0]["root"]] = childRoot
        roleList[roleRoot]["children"] = [childRoot]

        for id, node in data["data"]["trees"][0]["nodes"].items():
            if id in [key for key, _ in changedIDs.items()]:
                id = changedIDs[id]
            else:
                changedIDs[id] = globals.randomID()
                id = changedIDs[id]

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
        data = {"trees": []}
        tree = {"title": name}

        for n in Node.nodes:
            if n.title == "Root":
                root_children = self.getChildren(n, added)
                # Check if the root only has 1 child
                if len(root_children) == 1:
                    tree["root"] = root_children[0].id
                    tree["nodes"] = {}
                    que.put(root_children[0])
                    added.append(n)
                else:
                    exit("Root has more than 1 child")

                while not que.empty():
                    node_dic = {}
                    curr_node = que.get()
                    node_dic["id"] = curr_node.id
                    node_dic["title"] = curr_node.title
                    node_dic["isRole"] = curr_node.isRole
                    children = self.getChildren(curr_node, added)
                    if children:
                        node_dic["children"] = []
                        for child in children:
                            que.put(child)
                            node_dic["children"].append(child.id)

                    properties = curr_node.properties
                    if properties:
                        node_dic["properties"] = {}
                        for property, value in properties.items():
                            node_dic["properties"][property] = value.get()

                    node_dic["location"] = {}
                    node_dic["location"]["x"] = curr_node.x_orig
                    node_dic["location"]["y"] = curr_node.y_orig

                    tree["nodes"][curr_node.id] = node_dic
                    added.append(curr_node)

        data["trees"].append(tree)
        json_file["data"] = data

        if saveRole:
            file = "roles/" + name + ".json"

            with open(file, 'w') as f:
                json.dump(json_file, f)
            os.chmod(file, 0o777)

            newNode = Button(self.nodeList, text=name, command=lambda title=name: self.addNode(title, isRole=True))
            newNode.pack(fill=BOTH)
        else:
            file = "saved_trees/" + name + ".json"

            with open(file, 'w') as f:
                json.dump(json_file, f)
            os.chmod(file, 0o777)

    def saveJSON(self):
        name = self.treeName.get()
        que = queue.Queue()
        added = []

        json_file = {"name": name}
        data = {"trees": []}
        tree = {"title": name}

        for n in Node.nodes:
            if n.title == "Root":
                root_children = self.getChildren(n, added)
                # Check if the root only has 1 child
                if len(root_children) == 1:
                    tree["root"] = root_children[0].id
                    tree["nodes"] = {}
                    que.put(root_children[0])
                    added.append(n)
                else:
                    print("Error: root does not have only 1 child")

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
                                    if "ROLE" in child.properties and "properties" in roleChild:
                                        roleChild["properties"]["ROLE"] = child.properties["ROLE"].get()

                                    if "location" in roleChild:
                                        del roleChild["location"]

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
                                if value.get():
                                    node_dic["properties"][property] = value.get()

                    tree["nodes"][curr_node.id] = node_dic
                    added.append(curr_node)

        data["trees"].append(tree)
        json_file["data"] = data

        file = "jsons/" + name + ".json"

        with open(file, 'w') as f:
            json.dump(json_file, f)
        os.chmod(file, 0o777)

    def addProperty(self, node):
        node.properties[self.custom_prop_string.get()] = StringVar()
        self.spawnProperties(node)

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

        custom_prop_window = PanedWindow(self.prop_window)
        self.custom_prop_string = StringVar()
        cust_entry = Entry(custom_prop_window, textvariable=self.custom_prop_string)
        cust_entry.pack(side=LEFT)

        button = Button(custom_prop_window, text="Add", command=lambda node=node: self.addProperty(node))
        button.pack(side=RIGHT)
        custom_prop_window.pack(fill=X, pady=20)

    def addNode(self, title, loadProperties=None, isRole=False):
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
                    source.canvas.coords(line.id, x + source.x_off, y + source.y_off, line.x2, line.y2)
                    line.changeCoords([x + source.x_off, y + source.y_off, line.x2, line.y2])
                elif line.b == source:
                    source.canvas.coords(line.id, line.x1, line.y1, x + source.x_off, y + source.y_off)
                    line.changeCoords([line.x1, line.y1, x + source.x_off, y + source.y_off])

    def dnd_leave(self, source, event):
        self.root.focus_set()  # Hide highlight border
        self.canvas.delete(self.dndid)
        self.dndid = None

    def dnd_commit(self, source, event):
        self.dnd_leave(source, event)
        x, y = source.where(self.canvas, event)
        source.attach(self.canvas, x, y)

