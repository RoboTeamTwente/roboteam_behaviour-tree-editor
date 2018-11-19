class Line:

    def __init__(self, id, a, b, coords):
        self.id = id
        self.a = a
        self.b = b
        self.x1, self.y1, self.x2, self.y2 = coords

    def changeCoords(self, coords):
        self.x1, self.y1, self.x2, self.y2 = coords