from __future__ import annotations
import io
from struct import pack

from .. import classes


class EndianBinaryWriter:
    endian: str
    Length: int
    Position: int
    stream: io.BufferedReader

    def __init__(self, input_=b"", endian=">"):
        if isinstance(input_, (bytes, bytearray)):
            self.stream = io.BytesIO(input_)
            self.stream.seek(0, 2)
        elif isinstance(input_, io.IOBase):
            self.stream = input_
        else:
            raise ValueError("Invalid input type - %s." % type(input_))
        self.endian = endian
        self.Position = self.stream.tell()

    @property
    def bytes(self):
        self.stream.seek(0)
        return self.stream.read()

    @property
    def Length(self) -> int:
        pos = self.stream.tell()
        self.stream.seek(0, 2)
        l = self.stream.tell()
        self.stream.seek(pos)
        return l

    def dispose(self):
        self.stream.close()
        pass

    def write(self, *args):
        if self.Position != self.stream.tell():
            self.stream.seek(self.Position)
        ret = self.stream.write(*args)
        self.Position = self.stream.tell()
        return ret

    def write_byte(self, value: int):
        self.write(pack(self.endian + "b", value))

    def write_u_byte(self, value: int):
        self.write(pack(self.endian + "B", value))

    def write_bytes(self, value: bytes):
        return self.write(value)

    def write_short(self, value: int):
        self.write(pack(self.endian + "h", value))

    def write_int(self, value: int):
        self.write(pack(self.endian + "i", value))

    def write_long(self, value: int):
        self.write(pack(self.endian + "q", value))

    def write_u_short(self, value: int):
        self.write(pack(self.endian + "H", value))

    def write_u_int(self, value: int):
        self.write(pack(self.endian + "I", value))

    def write_u_long(self, value: int):
        self.write(pack(self.endian + "Q", value))

    def write_float(self, value: float):
        self.write(pack(self.endian + "f", value))

    def write_double(self, value: float):
        self.write(pack(self.endian + "d", value))

    def write_boolean(self, value: bool):
        self.write(pack(self.endian + "?", value))

    def write_string_to_null(self, value: str):
        self.write(value.encode("utf8", "surrogateescape"))
        self.write(b"\0")

    def write_aligned_string(self, value: str):
        bstring = value.encode("utf8", "surrogateescape")
        self.write_int(len(bstring))
        self.write(bstring)
        self.align_stream(4)

    def align_stream(self, alignment=4):
        pos = self.stream.tell()
        align = (alignment - pos % alignment) % alignment
        self.write(b"\0" * align)

    def write_quaternion(self, value: classes.Quaternionf):
        self.write_float(value.x)
        self.write_float(value.y)
        self.write_float(value.z)
        self.write_float(value.w)

    def write_vector2(self, value: classes.Vector2f):
        self.write_float(value.x)
        self.write_float(value.y)

    def write_vector3(self, value: classes.Vector3f):
        self.write_float(value.x)
        self.write_float(value.y)
        self.write_float(value.z)

    def write_vector4(self, value: classes.Vector4f):
        self.write_float(value.x)
        self.write_float(value.y)
        self.write_float(value.z)
        self.write_float(value.w)

    def write_rectangle_f(self, value: classes.Rectf):
        self.write_float(value.x)
        self.write_float(value.y)
        self.write_float(value.width)
        self.write_float(value.height)

    def write_color_uint(self, value: classes.ColorRGBA):
        self.write_u_byte(value.r * 255)
        self.write_u_byte(value.g * 255)
        self.write_u_byte(value.b * 255)
        self.write_u_byte(value.a * 255)

    def write_color4(self, value: classes.ColorRGBA):
        self.write_float(value.r)
        self.write_float(value.g)
        self.write_float(value.b)
        self.write_float(value.a)

    def write_matrix(self, value: classes.Matrix4x4f):
        for val in value.to_list():
            self.write_float(val)

    def write_array(self, command, value: list, write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for val in value:
            command(val)

    def write_byte_array(self, value: bytes):
        self.write_int(len(value))
        self.write(value)

    def write_boolean_array(self, value: list):
        self.write_array(self.write_boolean, value)

    def write_u_short_array(self, value: list):
        self.write_array(self.write_u_short, value)

    def write_int_array(self, value: list, write_length: bool = False):
        return self.write_array(self.write_int, value, write_length)

    def write_u_int_array(self, value: list, write_length: bool = False):
        return self.write_array(self.write_u_int, value, write_length)

    def write_float_array(self, value: list, write_length: bool = False):
        return self.write_array(self.write_float, value, write_length)

    def write_string_array(self, value: list):
        self.write_array(self.write_aligned_string, value)

    def write_vector2_array(self, value: list):
        self.write_array(self.write_vector2, value)

    def write_vector4_array(self, value: list):
        self.write_array(self.write_vector4, value)

    def write_matrix_array(self, value: list):
        self.write_array(self.write_matrix, value)
