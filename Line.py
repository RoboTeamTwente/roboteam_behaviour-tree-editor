class Line:

    lines = []

    def __init__(self, id, a, b, coords):
        self.id = id
        self.a = a
        self.b = b
        self.x1, self.y1, self.x2, self.y2 = coords
        Line.lines.append(self)

    def __del__(self):
        print("Line successfully deleted!")

    def delete(self):
        if self in Line.lines:
            Line.lines.remove(self)

        del self

    def changeCoords(self, coords):
        self.x1, self.y1, self.x2, self.y2 = coords