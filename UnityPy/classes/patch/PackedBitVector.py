import math
from typing import List

from ..generated import PackedBitVector, Quaternionf

try:
    from UnityPy import UnityPyBoost
except:
    UnityPyBoost = None


def uint(num):
    if num < 0 or num > 4294967295:
        return num % 4294967296
    return num


def unpack_floats(
    self: PackedBitVector,
    itemCountInChunk: int,
    chunkStride: int,
    start: int = 0,
    numChunks: int = -1,
) -> List[float]:
    if UnityPyBoost:
        return UnityPyBoost.unpack_floats(
            self.m_NumItems,
            self.m_Range,
            self.m_Start,
            bytes(self.m_Data),
            self.m_BitSize,
            itemCountInChunk,
            chunkStride,
            start,
            numChunks,
        )

    bitPos: int = self.m_BitSize * start
    indexPos: int = bitPos // 8
    bitPos %= 8

    scale: float = (1.0 / self.m_Range) if self.m_Range else float("inf")
    if numChunks == -1:
        numChunks = self.m_NumItems // itemCountInChunk
    end = int(chunkStride * numChunks / 4)
    data = []
    for index in range(0, end, chunkStride // 4):
        for i in range(itemCountInChunk):
            x = 0  # uint
            bits = 0
            while bits < self.m_BitSize:
                x |= uint(
                    (self.m_Data[indexPos] >> bitPos) << bits
                )  # (uint)((m_Data[indexPos] >> bitPos) << bits)
                num = min(self.m_BitSize - bits, 8 - bitPos)
                bitPos += num
                bits += num
                if bitPos == 8:  #
                    indexPos += 1
                    bitPos = 0

            x &= uint((1 << self.m_BitSize) - 1)  # (uint)(1 << m_BitSize) - 1u
            denomi = scale * ((1 << self.m_BitSize) - 1)
            data.append((x / denomi if denomi else float("inf")) + self.m_Start)
    return data


def unpack_ints(self: PackedBitVector) -> List[int]:
    if UnityPyBoost:
        return UnityPyBoost.unpack_ints(
            self.m_NumItems, bytes(self.m_Data), self.m_BitSize
        )

    data = [0] * self.m_NumItems
    indexPos = 0
    bitPos = 0
    for i in range(self.m_NumItems):
        bits = 0
        data[i] = 0
        while bits < self.m_BitSize:
            data[i] |= (self.m_Data[indexPos] >> bitPos) << bits
            num = min(self.m_BitSize - bits, 8 - bitPos)
            bitPos += num
            bits += num
            if bitPos == 8:
                indexPos += 1
                bitPos = 0
        data[i] &= (1 << self.m_BitSize) - 1
    return data


def unpack_quats(self: PackedBitVector):
    m_Data = self.m_Data
    data = [None] * self.m_NumItems
    indexPos = 0
    bitPos = 0

    for i in range(self.m_NumItems):
        flags = 0
        bits = 0
        while bits < 3:
            flags |= (m_Data[indexPos] >> bitPos) << bits  # unit
            num = min(3 - bits, 8 - bitPos)
            bitPos += num
            bits += num
            if bitPos == 8:  #
                indexPos += 1
                bitPos = 0
        flags &= 7

        q = [0.0] * 4
        sum = 0
        for j in range(4):
            if (flags & 3) != j:  #
                bitSize = 9 if ((flags & 3) + 1) % 4 == j else 10
                x = 0

                bits = 0
                while bits < bitSize:
                    x |= (m_Data[indexPos] >> bitPos) << bits  # uint
                    num = min(bitSize - bits, 8 - bitPos)
                    bitPos += num
                    bits += num
                    if bitPos == 8:  #
                        indexPos += 1
                        bitPos = 0
                x &= (1 << bitSize) - 1  # unit
                q[j] = x / (0.5 * ((1 << bitSize) - 1)) - 1
                sum += q[j] * q[j]

        lastComponent = flags & 3  # int
        q[lastComponent] = math.sqrt(1 - sum)  # float
        if (flags & 4) != 0:  # 0u
            q[lastComponent] = -q[lastComponent]
        data.append(q)

    return [Quaternionf(**dict(zip("xyzw", v))) for v in data]
