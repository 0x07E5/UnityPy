from __future__ import annotations
import struct
from enum import IntEnum
from typing import List, Tuple, ByteString


def get_format_size(format: int) -> int:
    if format in [
        VertexFormat.kVertexFormatFloat,
        VertexFormat.kVertexFormatUInt32,
        VertexFormat.kVertexFormatSInt32,
    ]:
        return 4
    elif format in [
        VertexFormat.kVertexFormatFloat16,
        VertexFormat.kVertexFormatUNorm16,
        VertexFormat.kVertexFormatSNorm16,
        VertexFormat.kVertexFormatUInt16,
        VertexFormat.kVertexFormatSInt16,
    ]:
        return 2
    elif format in [
        VertexFormat.kVertexFormatUNorm8,
        VertexFormat.kVertexFormatSNorm8,
        VertexFormat.kVertexFormatUInt8,
        VertexFormat.kVertexFormatSInt8,
    ]:
        return 1
    raise ValueError(format)


def is_int_format(version: Tuple[int, int, int, int], format: int) -> bool:
    if version[0] < 2017:
        return format == 4
    elif version[0] < 2019:
        return format >= 7
    else:
        return format >= 6


def parse_float_array(
    data: ByteString, component_size: int, format: VertexFormat
) -> List[float]:
    if format == VertexFormat.kVertexFormatFloat:
        return struct.unpack(f">{'f'*(len(data)//4)}", data)
    elif format == VertexFormat.kVertexFormatFloat16:
        return struct.unpack(f">{'e'*(len(data)//2)}", data)
    elif format == VertexFormat.kVertexFormatUNorm8:
        return [byte / 255.0 for byte in data]
    elif format == VertexFormat.kVertexFormatSNorm8:
        return [max(((byte - 128) / 127.0), -1.0) for byte in data]
    elif format == VertexFormat.kVertexFormatUNorm16:
        return [x / 65535.0 for x in struct.unpack(f">{'H'*(len(data)//2)}", data)]
    elif format == VertexFormat.kVertexFormatSNorm16:
        return [
            max(((x - 32768) / 32767.0), -1.0)
            for x in struct.unpack(f">{'h'*(len(data)//2)}", data)
        ]


def parse_int_array(data: ByteString, component_size: int):
    if component_size == 1:
        return [x for x in data]
    elif component_size == 2:
        return [x for x in struct.unpack(f">{'h'*(len(data)//2)}", data)]
    elif component_size == 4:
        return [x for x in struct.unpack(f">{'i'*(len(data)//4)}", data)]


def convert_vertex_format(format: int, version: List[int]) -> VertexFormat:
    if version[0] < 2017:
        if format == VertexChannelFormat.kChannelFormatFloat:
            return VertexFormat.kVertexFormatFloat
        elif format == VertexChannelFormat.kChannelFormatFloat16:
            return VertexFormat.kVertexFormatFloat16
        elif format == VertexChannelFormat.kChannelFormatColor:  # in 4.x is size 4
            return VertexFormat.kVertexFormatUNorm8
        elif format == VertexChannelFormat.kChannelFormatByte:
            return VertexFormat.kVertexFormatUInt8
        elif format == VertexChannelFormat.kChannelFormatUInt32:  # in 5.x
            return VertexFormat.kVertexFormatUInt32
        else:
            raise ValueError(f"Failed to convert {format} to VertexFormat")
    elif version[0] < 2019:
        if format == VertexFormat2017.kVertexFormatFloat:
            return VertexFormat.kVertexFormatFloat
        elif format == VertexFormat2017.kVertexFormatFloat16:
            return VertexFormat.kVertexFormatFloat16
        elif (
            format == VertexFormat2017.kVertexFormatColor
            or format == VertexFormat2017.kVertexFormatUNorm8
        ):
            return VertexFormat.kVertexFormatUNorm8
        elif format == VertexFormat2017.kVertexFormatSNorm8:
            return VertexFormat.kVertexFormatSNorm8
        elif format == VertexFormat2017.kVertexFormatUNorm16:
            return VertexFormat.kVertexFormatUNorm16
        elif format == VertexFormat2017.kVertexFormatSNorm16:
            return VertexFormat.kVertexFormatSNorm16
        elif format == VertexFormat2017.kVertexFormatUInt8:
            return VertexFormat.kVertexFormatUInt8
        elif format == VertexFormat2017.kVertexFormatSInt8:
            return VertexFormat.kVertexFormatSInt8
        elif format == VertexFormat2017.kVertexFormatUInt16:
            return VertexFormat.kVertexFormatUInt16
        elif format == VertexFormat2017.kVertexFormatSInt16:
            return VertexFormat.kVertexFormatSInt16
        elif format == VertexFormat2017.kVertexFormatUInt32:
            return VertexFormat.kVertexFormatUInt32
        elif format == VertexFormat2017.kVertexFormatSInt32:
            return VertexFormat.kVertexFormatSInt32
        else:
            raise ValueError(f"Failed to convert {format} to VertexFormat")
    else:
        return VertexFormat(format)


class VertexChannelFormat(IntEnum):
    kChannelFormatFloat = 0
    kChannelFormatFloat16 = 1
    kChannelFormatColor = 2
    kChannelFormatByte = 3
    kChannelFormatUInt32 = 4


class VertexFormat2017(IntEnum):
    kVertexFormatFloat = 0
    kVertexFormatFloat16 = 1
    kVertexFormatColor = 2
    kVertexFormatUNorm8 = 3
    kVertexFormatSNorm8 = 4
    kVertexFormatUNorm16 = 5
    kVertexFormatSNorm16 = 6
    kVertexFormatUInt8 = 7
    kVertexFormatSInt8 = 8
    kVertexFormatUInt16 = 9
    kVertexFormatSInt16 = 10
    kVertexFormatUInt32 = 11
    kVertexFormatSInt32 = 12


class VertexFormat(IntEnum):
    kVertexFormatFloat = 0
    kVertexFormatFloat16 = 1
    kVertexFormatUNorm8 = 2
    kVertexFormatSNorm8 = 3
    kVertexFormatUNorm16 = 4
    kVertexFormatSNorm16 = 5
    kVertexFormatUInt8 = 6
    kVertexFormatSInt8 = 7
    kVertexFormatUInt16 = 8
    kVertexFormatSInt16 = 9
    kVertexFormatUInt32 = 10
    kVertexFormatSInt32 = 11
