import unittest
import main
from Window import *


def makeWindow():
    root = main.Tk()
    types, nodes = main.getNodes()
    return Window(root, types, nodes)


class mainTest(unittest.TestCase):
    def test_Tkinter(self):
        root = main.Tk()


class windowTest(unittest.TestCase):
    def test_init(self):
        root = main.Tk()
        types, nodes = main.getNodes()
        main_window = Window(root, types, nodes)
        self.assertEqual(root, main_window.root)

    def test_AddNode(self):
        main_window = makeWindow()
        node = main_window.addNode("testNode0")
        self.assertIsInstance(node, Node)

        properties = {"location": {}}
        properties["location"]["x"] = 50
        properties["location"]["y"] = 50
        node2 = main_window.addNode("testNode0_1", properties)
        self.assertEqual(node2.canvas.coords(node2.canvas_id), [50, 50])


class lineTest(unittest.TestCase):
    def test_LineCounter(self):
        self.assertEqual(len(Line.lines), 0)
        node1 = Node("testNode1", [])
        node2 = Node("testNode2", [])
        coords = 1, 1, 3, 3
        line = Line(1, node1, node2, coords)
        self.assertEqual(len(Line.lines), 1)
        newCoords = 2, 2, 4, 4
        line.changeCoords(newCoords)
        self.assertEqual(line.x2, 4)


class nodeTest(unittest.TestCase):
    def test_NodeCounter(self):
        self.assertEqual(len(Node.nodes), 4)
        Node("testNode3", [])
        self.assertEqual(len(Node.nodes), 5)

    def test_DrawLine(self):
        main_window = makeWindow()

        node1 = main_window.addNode("testNode4")
        node2 = main_window.addNode("testNode5")
        self.assertEqual(len(node1.lines), 0)
        node1.drawLine(node1, node2)
        self.assertEqual(len(node1.lines), 1)
        self.assertEqual(len(node1.lines), len(node2.lines))


unittest.main()
