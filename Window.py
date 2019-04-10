try:
    from tkinter import *
    from tkinter import messagebox
except:
    from Tkinter import *
    import tkMessageBox as messagebox

from Node import Node
from Line import Line
import json
from time import sleep

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
import platform

OS = platform.system()

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
        self.nameEntry = Entry(self.topWindow, textvariable=self.treeName, width=100)
        self.topWindow.add(self.nameEntry)

        self.saveToFolder = StringVar()
        self.FolderOptions = []
        for directory in os.listdir(globals.ai_json_folder):
            if os.path.isdir(globals.ai_json_folder + directory):
                self.FolderOptions.append(directory)

        self.saveToFolder.set(self.FolderOptions[0])

        self.topWindow.add(Label(self.topWindow, text="Save to roboteam_ai"))
        self.saveToFolderEntry = OptionMenu(self.topWindow, self.saveToFolder, *self.FolderOptions)
        self.topWindow.add(self.saveToFolderEntry)

        self.e = Entry()
        self.e.pack()

        # Create bottom window that contains the rest of the application
        self.bottomWindow = PanedWindow(self.window)
        self.bottomWindow.pack(fill=BOTH, expand=1)

        self.nodeCanvas = Canvas(self.bottomWindow)
        self.nodeFrame = Frame(self.nodeCanvas)
        self.vsb = Scrollbar(self.nodeFrame, orient=VERTICAL, command=self.nodeCanvas.yview)
        self.nodeCanvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side=RIGHT, fill=Y)
        self.nodeCanvas.pack(side=LEFT, fill=Y, expand=False)
        self.nodeCanvas.create_window((4, 4), window=self.nodeFrame, anchor="nw", tags="self.nodeFrame")

        if OS == "Linux":
            self.nodeCanvas.bind_all("<4>", self.onMouseWheel)
            self.nodeCanvas.bind_all("<5>", self.onMouseWheel)
        else:
            self.nodeCanvas.bind_all("<MouseWheel>", self.onMouseWheel)

        self.nodeFrame.bind("<Configure>", self.onFrameConfigure)

        #self.bottomWindow.add(self.nodeList)

        self.canvasPane = PanedWindow(self.bottomWindow)
        self.canvasPane.pack(side=LEFT, expand=1, fill=BOTH)
        #self.bottomWindow.add(self.canvasPane)

        # Create canvas that the trees can be drawn on
        self.canvas = Canvas(self.canvasPane, width=750, height=550)
        self.canvasPane.add(self.canvas)
        self.canvas.dnd_accept = self.dnd_accept

        self.prop_window = PanedWindow(self.bottomWindow)
        self.prop_window.pack(side=RIGHT)
        #self.bottomWindow.add(self.prop_window)

        # Spawn root node
        newNode = Button(self.nodeFrame, text="Root", command=lambda title="Root": self.addNode(title))
        newNode.pack(side=TOP, fill=BOTH)

        # Spawn node types
        for type, nodes in types.items():
            nodeWindow = PanedWindow(self.nodeFrame)
            newLabel = Button(nodeWindow, text=type.capitalize(), font="bold", bd=0,
                              command=lambda type=type, nodeWindow=nodeWindow: self.toggleNodes(type, nodeWindow))
            newLabel.pack(side=TOP, fill=BOTH)
            nodeWindow.pack(side=TOP, fill=BOTH)

        # Spawn role nodes
        nodeWindow = PanedWindow(self.nodeFrame)
        newLabel = Button(nodeWindow, text="Roles", font="bold", bd=0,
                          command=lambda nodeWindow=nodeWindow: self.toggleNodes("roles", nodeWindow))
        newLabel.pack(side=TOP, fill=BOTH)
        nodeWindow.pack(side=TOP, fill=BOTH)

        # Create menu bar
        self.menubar = Menu(self.root)
        self.menubar.add_command(label="New", command=lambda: self.newTree())
        self.menubar.add_command(label="Save tree", command=lambda: self.save())

        # Create tree loading menu with all DO_NOT_TOUCH as buttons
        self.loadmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Load tree", menu=self.loadmenu)
        for directory in [location for location in os.listdir(globals.ai_json_folder) if os.path.isdir(globals.ai_json_folder + location)]:
            submenu = Menu(self.loadmenu, tearoff=0)
            for tree_file in [x for x in os.listdir(globals.ai_json_folder + directory) if x[-5:] == ".json"]:
                file = tree_file[:-5]
                submenu.add_command(label=file, command=lambda file=file, directory=directory: self.loadTree(directory, file))
            self.loadmenu.add_cascade(label=directory, menu=submenu)

        self.menubar.add_command(label="Reload all tactics", command=self.reloadAllTactics)
        self.menubar.add_command(label="Quit", command=self.root.quit)

        self.save_to_editor = BooleanVar()
        self.save_to_editor.set(False)
        self.save_json_ai = BooleanVar()
        self.save_json_ai.set(False)
        self.save_to_ai = BooleanVar()
        self.save_to_ai.set(True)

        self.saveConfirmation = True

        self.menubar.add_checkbutton(label="Save to editor", onvalue=True, offvalue=False, variable=self.save_to_editor)
        self.menubar.add_checkbutton(label="Save to roboteam_ai", onvalue=True, offvalue=False, variable=self.save_to_ai)
        self.menubar.add_separator()

        # Configure menu bar
        self.root.config(menu=self.menubar)

    def onMouseWheel(self, event):
        if OS == "Linux":
            if event.num == 4:
                self.nodeCanvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.nodeCanvas.yview_scroll(1, "units")
        else:
            self.nodeCanvas.yview_scroll(-1*event.delta/120, "units")

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.nodeCanvas.configure(scrollregion=self.nodeCanvas.bbox("all"))

    # Function to show/hide nodes belonging to a certain type
    def toggleNodes(self, type, nodeWindow):
        if type == "roles":
            nodes = [file[:-5] for file in os.listdir(globals.ai_json_folder + "roles/")]
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
            messagebox.showinfo('Error 576', 'Error 576: More or less than one root exists (' + str(len(roots)) + ')')
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

    def loadTree(self, directory, name, loadRole=False):
        self.newTree()
        self.treeName.set(name)
        self.saveToFolder.set(directory)
        self.e.focus()

        # Check if a role is loaded
        if loadRole:
            file = globals.ai_json_folder + 'roles/' + name + '.json'
        else:
            file = globals.ai_json_folder + directory + "/" + name + ".json"

        with open(file, 'r') as f:
            data = json.load(f)

        # Draw nodes
        nodes = data["data"]["trees"][0]["nodes"]
        root_child = data["data"]["trees"][0]["root"]

        nodes_to_draw = []
        nodes_to_draw.append([nodes[root_child]])
        levels = 1

        # Sort all nodes that need to be drawn into a list of lists, which represent layers
        while True:
            next_layer = []
            for node in nodes_to_draw[levels - 1]:
                if "children" in node and node["title"] != "Role":
                    next_layer.extend(node["children"])

            if len(next_layer) == 0:
                break

            next_layer = [nodes[node_id] for node_id in next_layer]
            nodes_to_draw.append(next_layer)
            levels += 1

        layer_height = self.canvas.winfo_height() / (levels + 2)

        # Loop over all layers
        for layer in range(len(nodes_to_draw)):
            y = (layer + 2) * layer_height
            layer_width = self.canvas.winfo_width() / (len(nodes_to_draw[layer]) + 1)

            # Loop over nodes in layer
            for i in range(len(nodes_to_draw[layer])):
                node = nodes_to_draw[layer][i]
                node_properties = {"location": {}, "id": node["id"]}
                node_properties["location"]["x"] = layer_width * (i + 1)
                node_properties["location"]["y"] = y
                if "properties" in node:
                    node_properties["properties"] = node["properties"]

                isRole = False
                if node["title"] == "Role":
                    node["title"] = node["role"]
                    if "properties" not in node_properties:
                        node_properties["properties"] = {}

                    node_properties["properties"]["ROLE"] = node["name"]

                    isRole = True
                elif node["title"] == "Tactic":
                    node_properties["properties"] = {"name": node["name"]}

                added_node = self.addNode(node["title"], node_properties, isRole)

                # Build root node if layer number = 0
                if layer == 0:
                    node_properties["id"] = globals.randomID()
                    node_properties["location"]["x"] = self.canvas.winfo_width() / 2
                    node_properties["location"]["y"] = layer_height

                    root = self.addNode("Root", node_properties)
                    root.drawLine(root, added_node)

        # Draw lines between all nodes just drawn
        for id, node in nodes.items():
            if id in [x.id for x in Node.nodes] and "children" in node:
                if "role" in node:
                    continue

                children = node["children"]
                for child in children:
                    first_node = [n for n in Node.nodes if n.id == id][0]
                    second_node = [n for n in Node.nodes if n.id == child][0]
                    first_node.drawLine(first_node, second_node)

    # Reload all tactics to make sure the roles are refreshed
    def reloadAllTactics(self):
        if messagebox.askyesno("Reload all tactics", "Are you sure you want to reload all tactics?"):
            self.saveConfirmation = False
            self.newTree()
            tactics = [file[:-5] for file in os.listdir(globals.ai_json_folder + "tactics/")]
            for tactic in tactics:
                try:
                    self.loadTree("tactics", tactic, False)
                    self.save()
                except:
                    print("Unable to save or load tactic", tactic)
                self.newTree()

        self.saveConfirmation = True

    # Load role in order to add to JSON
    def loadRole(self, role, roleRoot):
        self.e.focus()
        roleList = {}
        changedIDs = {}  # Dictionary to keep track of randomly changed IDs
        if not role.title + ".json" in os.listdir(globals.ai_json_folder + "roles/"):
            messagebox.showinfo('Error loading role!',
                                'Role "' + role.title + ' " not found in ' + globals.ai_json_folder + "roles/")
            return False

        with open(globals.ai_json_folder + "roles/" + role.title + ".json") as f:
            data = json.load(f)

        # Add Role node and add root as child of Role node
        roleList[roleRoot] = {"id": roleRoot}
        roleList[roleRoot]["title"] = "Role"
        roleList[roleRoot]["name"] = role.properties["ROLE"].get()
        roleList[roleRoot]["role"] = role.title
        roleList[roleRoot]["isRole"] = True
        childRoot = globals.randomID()
        changedIDs[data["data"]["trees"][0]["root"]] = childRoot
        roleList[roleRoot]["children"] = [childRoot]

        # Loop over all nodes in role
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

    @staticmethod
    def checkRoleNames():
        for node in Node.nodes:
            if node.isRole:
                if len(node.properties["ROLE"].get()) == 0:
                    return False

        return True

    def save(self):
        if not self.checkRoleNames():
            messagebox.showinfo('Warning', 'Role node without ROLE!')
            return

        if self.save_to_editor.get():
            self.saveJSON(globals.PROJECT_DIR)
        if self.save_to_ai.get():
            self.saveJSON(globals.ai_json_folder + self.saveToFolder.get())

        if not self.save_to_editor.get() and not self.save_to_ai.get():
            messagebox.showinfo('Warning', 'Nothing was saved!')

    # Save tree as interpretable JSON
    def saveJSON(self, directory):
        if not self.treeValidation():
            return

        name = self.treeName.get()
        que = queue.Queue()
        added = []
        changedIDs = {}

        json_file = {"name": name}
        data = {"trees": []}
        tree = {"title": name}

        # Loop over all existing nodes. Only do something when node title == "Root"
        for n in Node.nodes:

            # Start building tree if the root node is found
            if n.title == "Root":
                root_children = self.getChildren(n, added)
                if root_children[0].isRole:
                    changedIDs[root_children[0].id] = globals.randomID()
                    tree["root"] = changedIDs[root_children[0].id]
                else:
                    tree["root"] = root_children[0].id

                tree["nodes"] = {}
                que.put(n)

                # Children kept being added to the que, and nodes are added to the JSON until no children exist anymore
                while not que.empty():
                    node_dic = {}
                    curr_node = que.get()
                    # If curr_node is a role, it is replaced by the JSON of the role in the tree (most likely a tactic)
                    if curr_node.isRole:
                        roleChildren = self.loadRole(curr_node, changedIDs[curr_node.id])
                        if not roleChildren:
                            return

                        for id, roleChild in roleChildren.items():
                            # Inherit ROLE from the role node
                            if "properties" not in roleChild:
                                roleChild["properties"] = {}
                            if "ROLE" in curr_node.properties:
                                roleChild["properties"]["ROLE"] = curr_node.properties["ROLE"].get()

                            if "location" in roleChild:
                                del roleChild["location"]

                            if "isRole" in roleChild:
                                del roleChild["isRole"]

                            tree["nodes"][id] = roleChild

                    # If curr_node is not a role node, it is added and it's children are added to the queue
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
                                    if property[0] == "*":
                                        property = property.split(";")[0][1:]

                                    if value.get():
                                        node_dic["properties"][property] = value.get()

                        if curr_node.title != "Root":
                            tree["nodes"][curr_node.id] = node_dic

                        added.append(curr_node)

        data["trees"].append(tree)
        json_file["data"] = data

        file = directory + "/" + name + ".json"

        with open(file, 'w') as f:
            json.dump(json_file, f)
        os.chmod(file, 0o777)

        if self.saveConfirmation:
            messagebox.showinfo('JSON saved successfully!', 'JSON successfully exported to ' + directory + ' as ' + name + '.json')

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
            if property[0] == "*":
                propertyList = property.split(";")
                label = Label(window, text=propertyList[0][1:])
                label.pack(side=LEFT)
                choices = propertyList[1:]
                entry = OptionMenu(window, value, *choices)
                value.set(choices[0])
                entry.pack(side=RIGHT)
                window.pack(fill=X)
            else:
                label = Label(window, text=property)
                label.pack(side=LEFT)
                entry = Entry(window, textvariable=properties[property])
                entry.pack(side=RIGHT)
                window.pack(fill=X)

        #Spawn custom property
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