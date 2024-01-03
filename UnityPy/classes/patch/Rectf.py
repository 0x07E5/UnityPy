from ..generated import Rectf


def round(self: Rectf):
    return Rectf(round(self.x), round(self.y), round(self.width), round(self.height))


def left(self: Rectf):
    return self.x


def top(self: Rectf):
    return self.y


def right(self: Rectf):
    return self.x + self.width


def bottom(self: Rectf):
    return self.y + self.height


def size(self: Rectf):
    return self.width, self.height


def location(self: Rectf):
    return self.x, self.y


Rectf.round = round
Rectf.left = property(left)
Rectf.top = property(top)
Rectf.right = property(right)
Rectf.bottom = property(bottom)
Rectf.size = property(size)
Rectf.location = property(location)
