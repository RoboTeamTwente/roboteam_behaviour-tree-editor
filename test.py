import unittest
import main
from Window import *


def makeWindow():
    root = main.Tk()
    types, nodes = main.getNodes()
    return Window(root, types, nodes)


class mainTest(unittest.TestCase):
    def testRoleLoading(self):
        self.assertEqual(len(main.getNodes()), len(os.listdir("roles")))

    def testTkinter(self):
        root = main.Tk()


class windowTest(unittest.TestCase):
    def testInit(self):
        root = main.Tk()
        types, nodes = main.getNodes()
        main_window = Window(root, types, nodes)
        self.assertEqual(root, main_window.root)


class lineTest(unittest.TestCase):
    def testLineCounter(self):
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
    def testNodeCounter(self):
        self.assertEqual(len(Node.nodes), 2)
        node = Node("testNode3", [])
        self.assertEqual(len(Node.nodes), 3)

    def drawLineTest(self):
        node1 = Node("testNode4", [])
        node2 = Node("testNode5", [])
        node1.drawLine(node1, node2)
        self.assertEqual(len(node1.lines), 1)
        self.assertEqual(len(node1.lines), len(node2.lines))


unittest.main()
