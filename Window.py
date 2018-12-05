try:
    from tkinter import *
    from tkinter import messagebox
except:
    from Tkinter import *
    import tkMessageBox as messagebox

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

        # Create main window
        self.window = PanedWindow(orient=VERTICAL)
        self.window.pack(fill=BOTH, expand=1)

        # Create top window that contains the tree name entrance
        self.topWindow = PanedWindow(self.window)
        self.topWindow.pack(fill=X)

        self.treeName = StringVar()
        self.topWindow.add(Label(self.topWindow, text="Name"))
        self.nameEntry = Entry(self.topWindow, textvariable=self.treeName)
        self.topWindow.add(self.nameEntry)
        self.e = Entry()
        self.e.pack()

        # Create bottom window that contains the rest of the application
        self.bottomWindow = PanedWindow(self.window)
        self.bottomWindow.pack(fill=BOTH, expand=1)

        self.nodeList = PanedWindow(self.bottomWindow, orient=VERTICAL)
        self.bottomWindow.add(self.nodeList)

        self.canvasPane = PanedWindow(self.bottomWindow)
        self.bottomWindow.add(self.canvasPane)

        # Create canvas that the trees can be drawn on
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
            newLabel = Button(nodeWindow, text=type.capitalize(), bd=0,
                              command=lambda type=type, nodeWindow=nodeWindow: self.toggleNodes(type, nodeWindow))
            newLabel.pack(fill=BOTH)
            nodeWindow.pack(fill=BOTH)

        # Spawn role nodes
        nodeWindow = PanedWindow(self.nodeList)
        newLabel = Button(nodeWindow, text="Roles", bd=0,
                          command=lambda nodeWindow=nodeWindow: self.toggleNodes("roles", nodeWindow))
        newLabel.pack(fill=BOTH)
        nodeWindow.pack(fill=BOTH)

        # Create menu bar
        self.menubar = Menu(self.root)
        self.menubar.add_command(label="New", command=lambda: self.newTree())
        self.menubar.add_command(label="Save tree", command=lambda: self.saveTree())

        # Create tree loading menu with all saved_trees as buttons
        self.loadmenu = Menu(self.menubar, tearoff=0)
        for file in sorted([f for f in os.listdir(globals.PROJECT_DIR + "saved_trees") if f != ".keep"]):
            file = file[:-5]
            self.loadmenu.add_command(label=file, command=lambda file=file: self.loadTree(file))
        self.menubar.add_cascade(label="Load tree", menu=self.loadmenu)

        self.menubar.add_command(label="Save role", command=lambda: self.saveTree(True))

        # Create role loading menu with all roles as buttons
        self.loadRoleMenu = Menu(self.menubar, tearoff=0)
        for file in sorted([f for f in os.listdir(globals.PROJECT_DIR + "roles") if f != ".keep"]):
            file = file[:-5]
            self.loadRoleMenu.add_command(label=file, command=lambda file=file: self.loadTree(file, loadRole=True))
        self.menubar.add_cascade(label="Load role", menu=self.loadRoleMenu)

        self.menubar.add_command(label="Export JSON", command=lambda: self.saveJSON())
        self.menubar.add_command(label="Quit", command=self.root.quit)

        # Configure menu bar
        self.root.config(menu=self.menubar)

    # Function to show/hide nodes belonging to a certain type
    def toggleNodes(self, type, nodeWindow):
        if type == "roles":
            nodes = [file[:-5] for file in os.listdir(globals.PROJECT_DIR + "roles/")]
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

    def validRootCheck(self):
        roots = [node for node in Node.nodes if node.title == "Root"]
        if len(roots) != 1:
            messagebox.showinfo('Error 576', 'Error 576: More or less than one root exists')
            return False

        root_children = self.getChildren(roots[0], [])
        if len(root_children) != 1:
            messagebox.showinfo('Error 594', 'Error 594: Root has more or less than 1 child')
            return False

        return True

    def circularCheck(self):
        que = queue.Queue()
        added = []
        root = [node for node in Node.nodes if node.title == "Root"][0]
        que.put([root, None])
        while not que.empty():
            node, parent = que.get()
            children = self.getChildren(node, [parent])
            for child in children:
                if child in added:
                    return False
                que.put([child, node])

            added.append(node)

        return True

    def treeValidation(self):
        if not self.validRootCheck():
            return False
        if not self.circularCheck():
            messagebox.showinfo('Error 839', 'Error 839: Tree is circular!')
            return False

        return True

    # Removes all nodes and starts with fresh canvas
    def newTree(self):
        for line in list(Line.lines):
            self.canvas.after(10, self.canvas.delete, line.id)
            line.delete()

        for node in list(Node.nodes):
            for line in list(node.lines):
                self.canvas.after(10, self.canvas.delete, line.id)
                line.delete()
            node.delete()

        for child in list(self.canvas.winfo_children()):
            child.destroy()

    # Get all children of specific node, and keep track of which are added
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
                messagebox.showinfo('Error 102', 'Error 102: Cry for help!')
                return

        if "x_orig" in children:
            return sorted(children, key=operator.attrgetter('x_orig'))
        else:
            return [child for _, child in
                    sorted(zip([x for x, y in [a.canvas.coords(a.canvas_id) for a in children]], children))]

    def loadTree(self, name, loadRole=False):
        self.newTree()
        self.treeName.set(name)
        self.e.focus()
        if loadRole:
            file = globals.PROJECT_DIR + 'roles/' + name + '.json'
        else:
            file = globals.PROJECT_DIR + 'saved_trees/' + name + '.json'
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

    # Load role in order to add to JSON
    def loadRole(self, role, roleRoot):
        self.treeName.set(role.title)
        self.e.focus()
        roleList = {}
        changedIDs = {}  # Dictionary to keep track of randomly changed IDs
        with open(globals.PROJECT_DIR + "roles/" + role.title + ".json") as f:
            data = json.load(f)

        # Add Role node and add root as child of Role node
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

        return roleList

    # Save tree so it can be loaded in again
    def saveTree(self, saveRole=False):
        if not self.treeValidation():
            return

        name = self.treeName.get()
        que = queue.Queue()
        added = []

        json_file = {"name": name}
        data = {"trees": []}
        tree = {"title": name}

        for n in Node.nodes:
            if n.title == "Root":
                root_children = self.getChildren(n, added)
                print(root_children)
                # Check if the root only has 1 child
                if len(root_children) == 1:
                    tree["root"] = root_children[0].id
                    tree["nodes"] = {}
                    que.put(root_children[0])
                    added.append(n)
                else:
                    messagebox.showinfo('Error 594', 'Error 594: Root has more or less than 1 child')
                    return

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
            file = globals.PROJECT_DIR + "roles/" + name + ".json"

            with open(file, 'w') as f:
                json.dump(json_file, f)
            os.chmod(file, 0o777)

            newNode = Button(self.nodeList, text=name, command=lambda title=name: self.addNode(title, isRole=True))
            newNode.pack(fill=BOTH)

            self.loadmenu.add_command(label=name, command=lambda file=name: self.loadTree(file, loadRole=True))
            messagebox.showinfo('Role saved successfully!', 'Role successfully saved in "roles" as ' + name + '.json')

        else:
            file = globals.PROJECT_DIR + "saved_trees/" + name + ".json"

            with open(file, 'w') as f:
                json.dump(json_file, f)
            os.chmod(file, 0o777)

            self.loadmenu.add_command(label=name, command=lambda file=name: self.loadTree(file))
            messagebox.showinfo('Tree saved successfully!',
                                'Tree successfully saved in "saved_trees" as ' + name + '.json')

    # Save tree as interpretable JSON
    def saveJSON(self):
        if not self.treeValidation():
            return

        name = self.treeName.get()
        que = queue.Queue()
        added = []
        changedIDs = {}

        json_file = {"name": name}
        data = {"trees": []}
        tree = {"title": name}

        for n in Node.nodes:
            if n.title == "Root":
                root_children = self.getChildren(n, added)
                # Check if the root only has 1 child
                if len(root_children) == 1:

                    if root_children[0].isRole:
                        changedIDs[root_children[0].id] = globals.randomID()
                        tree["root"] = changedIDs[root_children[0].id]
                    else:
                        tree["root"] = root_children[0].id

                    tree["nodes"] = {}
                    que.put(n)
                else:
                    messagebox.showinfo('Error 592', 'Error 592: Root has more or less than 1 child')
                    return

                while not que.empty():
                    node_dic = {}
                    curr_node = que.get()
                    if curr_node.isRole:
                        roleChildren = self.loadRole(curr_node, changedIDs[curr_node.id])
                        for id, roleChild in roleChildren.items():
                            # Inherit ROLE from the role node
                            if "ROLE" in curr_node.properties and "properties" in roleChild:
                                roleChild["properties"]["ROLE"] = curr_node.properties["ROLE"].get()

                            if "location" in roleChild:
                                del roleChild["location"]

                            tree["nodes"][id] = roleChild
                    else:
                        node_dic["id"] = curr_node.id
                        node_dic["title"] = curr_node.title
                        children = self.getChildren(curr_node, added)
                        if children:
                            node_dic["children"] = []
                            for child in children:
                                que.put(child)
                                if child.isRole:
                                    if child.id not in changedIDs:
                                        changedIDs[child.id] = globals.randomID()
                                    node_dic["children"].append(changedIDs[child.id])
                                else:
                                    node_dic["children"].append(child.id)

                        properties = curr_node.properties
                        if properties:
                            # In case of Role and Tactic nodes, make the child name/role the name of the node
                            if curr_node.title == "Tactic":
                                node_dic["name"] = properties["name"].get()
                            elif curr_node.title == "Role":
                                node_dic["name"] = properties["ROLE"].get()
                            else:
                                node_dic["properties"] = {}
                                for property, value in properties.items():
                                    if value.get():
                                        node_dic["properties"][property] = value.get()

                        if curr_node.title != "Root":
                            tree["nodes"][curr_node.id] = node_dic

                        added.append(curr_node)

        data["trees"].append(tree)
        json_file["data"] = data

        file = globals.PROJECT_DIR + "jsons/" + name + ".json"

        with open(file, 'w') as f:
            json.dump(json_file, f)
        os.chmod(file, 0o777)

        messagebox.showinfo('JSON saved successfully!', 'JSON successfully exported to "jsons" as ' + name + '.json')

    # Add custom property
    def addProperty(self, node):
        node.properties[self.custom_prop_string.get()] = StringVar()
        self.spawnProperties(node)

    # Remove previous spawned properties
    def removeProperties(self):
        for item in self.prop_window.winfo_children():
            item.destroy()

    # Spawn property window
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

    # Add node to window
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
