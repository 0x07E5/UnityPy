from math import sqrt
from typing import Union

from ..generated import Vector3f

kEpsilon = 0.00001


def getitem(self: Vector3f, index: int):
    if index == 0:
        return self.x
    elif index == 1:
        return self.y
    elif index == 2:
        return self.z
    else:
        raise IndexError()


def setitem(self: Vector3f, index: int, value: float):
    if index == 0:
        self.x = value
    elif index == 1:
        self.y = value
    elif index == 2:
        self.z = value
    else:
        raise IndexError("Index out of range")


def normalize(self: Vector3f):
    length = self.length()
    if length > kEpsilon:
        invNorm = 1.0 / length
        self.x *= invNorm
        self.y *= invNorm
        self.z *= invNorm
    else:
        self.x = 0
        self.y = 0
        self.z = 0


def length(self: Vector3f):
    return sqrt(self.length_squared())


def length_squared(self: Vector3f):
    return self.x**2 + self.y**2 + self.z**2


def zero() -> Vector3f:
    return Vector3f(x=0, y=0, z=0)


def one() -> Vector3f:
    return Vector3f(x=1, y=1, z=1)


def add(a: Vector3f, b: Union[Vector3f, float]) -> Vector3f:
    if isinstance(b, Vector3f):
        return Vector3f(a.x + b.x, a.y + b.y, a.z + b.z)
    else:
        return Vector3f(a.x + b, a.y + b, a.z + b)


def sub(a: Vector3f, b: Vector3f) -> Vector3f:
    if isinstance(b, Vector3f):
        return Vector3f(a.x - b.x, a.y - b.y, a.z - b.z)
    else:
        return Vector3f(a.x + b, a.y + b, a.z + b)


def mul(a: Vector3f, b: Vector3f) -> Vector3f:
    if isinstance(b, Vector3f):
        return Vector3f(a.x * b.x, a.y * b.y, a.z * b.z)
    else:
        return Vector3f(a.x * b, a.y * b, a.z * b)


def div(a: Vector3f, b: Vector3f) -> Vector3f:
    if isinstance(b, Vector3f):
        return Vector3f(a.x / b.x, a.y / b.y, a.z / b.z)
    else:
        return Vector3f(a.x / b, a.y / b, a.z / b)


def eq(a: Vector3f, b: Vector3f) -> bool:
    return (a - b).length_squared() < kEpsilon


def ne(a: Vector3f, b: Vector3f) -> bool:
    return not (a == b)


Vector3f.__getitem__ = getitem
Vector3f.__setitem__ = setitem
Vector3f.normalize = normalize
Vector3f.length = length
Vector3f.length_squared = length_squared
Vector3f.one = one
Vector3f.zero = zero
Vector3f.__add__ = add
Vector3f.__sub__ = sub
Vector3f.__mul__ = mul
Vector3f.__div__ = div
Vector3f.__eq__ = eq
Vector3f.__ne__ = ne
