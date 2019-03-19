class Line:

    lines = []

    def __init__(self, id, a, b, coords):
        self.id = id
        self.a = a
        self.b = b
        self.x1, self.y1, self.x2, self.y2 = coords
        Line.lines.append(self)

    def delete(self):
        for node in list(self.a.nodes):
            for line in node.lines:
                if line == self:
                    node.lines.remove(self)

        for node in list(self.b.nodes):
            for line in node.lines:
                if line == self:
                    node.lines.remove(self)

        if self in Line.lines:
            Line.lines.remove(self)

        del self


    def changeCoords(self, coords):
        self.x1, self.y1, self.x2, self.y2 = coords