# roboteam_behaviour-tree-editor
New behaviour tree editor written in Python for Roboteam Twente

Make sure to run main.py with sudo rights!

# depedencies
keyboard

tkinter

numpy

# Setup
Run setup.sh and the shell script "b3e.sh" will be generated in the main RTT folder. This script can be ran to launch the behavior tree editor.

# How-to draw trees
Click a node at the left to spawn it, it can be moved by simply dragging.

To draw lines between nodes, hold "d" and drag a line between nodes.

To remove nodes, hold "r" while pressing it.

Currently, lines cannot be deleted. Delete one of the nodes connected to it to also remove the line.

# How-to save trees and compile them to JSON
When saving a tree, make sure it has a root node! Trees are generated from the root downwards. The root node can only have 1 child.

Currently the system is not completely fool-proof, so adding circles to the tree might give errors.

# roboteam_ai integration
The behavior tree editor is integrated with roboteam_ai. This means that all trees are directly loaded from and saved to the jsons folder in roboteam_ai. The only folder that must exists here is "roles", because it is needed for the role integration. The rest can be named whatever, but will most likely be "strategies" and "tactics".

The config files are found in "src/tree_interep/config_files" in roboteam_ai.

Trees with Role nodes that were made before the roboteam_ai integration will not be able to be loaded back in.

# How-to create and use roles
Roles do not need the node "Role", but they do need a root.

When adding a role to a tactic, first create a "Role" node with as property the name of the roll. Add the actual role node to this, and it works! All skills or other nodes that have a "ROLE" property will inherit this property from the "Role" node.

# Main.py
Main function that creates the window using Window(). Also contains getNodes to collect all the usable nodes from the config files.

# Window.py
Contains most functions, main window creation, load and save function and the JSON compiler. Contains a few functions to handle DnD (Drag and Drop) events.

# Node.py
Node class to create Node objects. Includes function to add nodes, draw lines between them and handle DnD events.

# DndHandler.py
Main function to handle DnD events. Also manages clicked using hotkeys "d" and "r".

# globals.py
Makes the main window a global variable, as well as the random ID generation.
