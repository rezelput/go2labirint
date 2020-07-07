import math


def deg_to_rad(degrees):
    return degrees / 180.0 * math.pi


def read_point(str):
    coords = str.split(' ')
    assert len(coords) == 2
    return Point(float(coords[0]), float(coords[1]))


def read_line(str):
    coords = str.split(' ')
    assert len(coords) == 4
    a = Point(float(coords[0]), float(coords[1]))
    b = Point(float(coords[2]), float(coords[3]))
    return Line(a, b)


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def angle(self):
        ang = math.atan2(self.y, self.x) / math.pi * 180.0
        if (ang < 0.0):
            return ang + 360
        return ang

    def rotate(self, angle, point):
        rad = deg_to_rad(angle)
        self.x -= point.x
        self.y -= point.y
        ox, oy = self.x, self.y
        self.x = math.cos(rad) * ox - math.sin(rad) * oy
        self.y = math.sin(rad) * ox - math.cos(rad) * oy
        self.x += point.x
        self.y += point.y

    def distance(self, point):
        dx = self.x - point.x
        dy = self.y - point.y

        return math.sqrt(dx * dx + dy * dy)

    def __str__(self):
        return "Point (%.1f, %.1f)" % (self.x, self.y)


class Line:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def midpoint(self):
        x = (self.a.x + self.b.x) / 2.0
        y = (self.a.y + self.b.y) / 2.0

        return Point(x, y)

    def intersection(self, line):

        A, B, C, D = self.a, self.b, line.a, line.b

        rTop = (A.y - C.y) * (D.x - C.x) - (A.x - C.x) * (D.y - C.y)
        rBot = (B.x - A.x) * (D.y - C.y) - (B.y - A.y) * (D.x - C.x)

        sTop = (A.y - C.y) * (B.x - A.x) - (A.x - C.x) * (B.y - A.y)
        sBot = (B.x - A.x) * (D.y - C.y) - (B.y - A.y) * (D.x - C.x)

        if rBot == 0 or sBot == 0:
            return False, None

        r = rTop / rBot
        s = sTop / sBot
        if r > 0 and r < 1 and s > 0 and s < 1:
            x = A.x + r * (B.x - A.x)
            y = A.y + r * (B.y - A.y)
            return True, Point(x, y)

        return False, None

    def distance(self, p):
        utop = (p.x - self.a.x) * (self.b.x - self.a.x) + (p.y - self.a.y) * (self.b.y - self.a.y)
        ubot = self.a.distance(self.b)
        ubot *= ubot
        if ubot == 0.0:
            return 0.0

        u = utop / ubot
        if u < 0 or u > 1:
            d1 = self.a.distance(p)
            d2 = self.b.distance(p)
            if d1 < d2:
                return d1
            return d2

        x = self.a.x + u * (self.b.x - self.a.x)
        y = self.a.y + u * (self.b.y - self.a.y)
        point = Point(x, y)
        return point.distance(p)

    def length(self):
        return self.a.distance(self.b)

    def __str__(self):
        return "Line (%.1f, %.1f) -> (%.1f, %.1f)" % (self.a.x, self.a.y, self.b.x, self.b.y)