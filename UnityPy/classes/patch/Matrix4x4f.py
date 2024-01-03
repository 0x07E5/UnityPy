from typing import List, Tuple

from ..generated import Matrix4x4f
from .Vector3f import Vector3f

MATRIX4X4_INDEX_MAP = [f"e{i}{j}" for j in range(4) for i in range(4)]


def from_list(values: List[float]) -> Matrix4x4f:
    assert len(values) == 16
    return Matrix4x4f(**dict(zip(MATRIX4X4_INDEX_MAP, values)))


def to_list(self: Matrix4x4f):
    return [getattr(self, key) for key in MATRIX4X4_INDEX_MAP]


Matrix4x4f.from_list = from_list
Matrix4x4f.to_list = to_list


def scale(vector: Vector3f):
    return from_list(
        [vector.X, 0, 0, 0, 0, vector.Y, 0, 0, 0, 0, vector.Z, 0, 0, 0, 0, 1]
    )


Matrix4x4f.scale = scale


def getitem(self: Matrix4x4f, index: Tuple[int, int]) -> float:
    return getattr(self, f"e{index[0]}{index[1]}")


def setitem(self: Matrix4x4f, index: Tuple[int, int], value: float):
    setattr(self, f"e{index[0]}{index[1]}", value)


Matrix4x4f.__getitem__ = getitem
Matrix4x4f.__setitem__ = setitem


def mul(lhs: Matrix4x4f, rhs: Matrix4x4f) -> Matrix4x4f:
    res = Matrix4x4f.from_list([0.0] * 16)
    res.e00 = (
        lhs.e00 * rhs.e00 + lhs.e01 * rhs.e10 + lhs.e02 * rhs.e20 + lhs.e03 * rhs.e30
    )
    res.e01 = (
        lhs.e00 * rhs.e01 + lhs.e01 * rhs.e11 + lhs.e02 * rhs.e21 + lhs.e03 * rhs.e31
    )
    res.e02 = (
        lhs.e00 * rhs.e02 + lhs.e01 * rhs.e12 + lhs.e02 * rhs.e22 + lhs.e03 * rhs.e32
    )
    res.e03 = (
        lhs.e00 * rhs.e03 + lhs.e01 * rhs.e13 + lhs.e02 * rhs.e23 + lhs.e03 * rhs.e33
    )

    res.e10 = (
        lhs.e10 * rhs.e00 + lhs.e11 * rhs.e10 + lhs.e12 * rhs.e20 + lhs.e13 * rhs.e30
    )
    res.e11 = (
        lhs.e10 * rhs.e01 + lhs.e11 * rhs.e11 + lhs.e12 * rhs.e21 + lhs.e13 * rhs.e31
    )
    res.e12 = (
        lhs.e10 * rhs.e02 + lhs.e11 * rhs.e12 + lhs.e12 * rhs.e22 + lhs.e13 * rhs.e32
    )
    res.e13 = (
        lhs.e10 * rhs.e03 + lhs.e11 * rhs.e13 + lhs.e12 * rhs.e23 + lhs.e13 * rhs.e33
    )

    res.e20 = (
        lhs.e20 * rhs.e00 + lhs.e21 * rhs.e10 + lhs.e22 * rhs.e20 + lhs.e23 * rhs.e30
    )
    res.e21 = (
        lhs.e20 * rhs.e01 + lhs.e21 * rhs.e11 + lhs.e22 * rhs.e21 + lhs.e23 * rhs.e31
    )
    res.e22 = (
        lhs.e20 * rhs.e02 + lhs.e21 * rhs.e12 + lhs.e22 * rhs.e22 + lhs.e23 * rhs.e32
    )
    res.e23 = (
        lhs.e20 * rhs.e03 + lhs.e21 * rhs.e13 + lhs.e22 * rhs.e23 + lhs.e23 * rhs.e33
    )

    res.e30 = (
        lhs.e30 * rhs.e00 + lhs.e31 * rhs.e10 + lhs.e32 * rhs.e20 + lhs.e33 * rhs.e30
    )
    res.e31 = (
        lhs.e30 * rhs.e01 + lhs.e31 * rhs.e11 + lhs.e32 * rhs.e21 + lhs.e33 * rhs.e31
    )
    res.e32 = (
        lhs.e30 * rhs.e02 + lhs.e31 * rhs.e12 + lhs.e32 * rhs.e22 + lhs.e33 * rhs.e32
    )
    res.e33 = (
        lhs.e30 * rhs.e03 + lhs.e31 * rhs.e13 + lhs.e32 * rhs.e23 + lhs.e33 * rhs.e33
    )

    return res


Matrix4x4f.__mul__ = mul
