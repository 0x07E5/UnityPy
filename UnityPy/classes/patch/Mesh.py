import math
import struct
from typing import List, Optional, Union

from ..generated import Mesh, BoneWeights4, BoneInfluence, Vector2f, ColorRGBA, Vector4f
from ...enums import GfxPrimitiveType
from ...helpers import MeshHelper

from .Vector3f import Vector3f
from .Matrix4x4f import Matrix4x4f

try:
    from UnityPy import UnityPyBoost
except:
    UnityPyBoost = None


class MeshUnpacked(Mesh):
    m_Indices: List[int]
    m_Vertices: List[Vector3f]
    m_BindPose = List[Matrix4x4f]
    m_BoneNameHashes = List[str]
    m_Skin: Optional[Union[List[BoneWeights4], List[BoneInfluence]]]
    m_Normals: Optional[List[Vector3f]]
    m_Tangents: Optional[List[Vector4f]]
    m_Colors: Optional[List[ColorRGBA]]
    m_UV0: Optional[List[Vector2f]]
    m_UV1: Optional[List[Vector2f]]
    m_UV2: Optional[List[Vector2f]]
    m_UV3: Optional[List[Vector2f]]
    m_UV4: Optional[List[Vector2f]]
    m_UV5: Optional[List[Vector2f]]
    m_UV6: Optional[List[Vector2f]]
    m_UV7: Optional[List[Vector2f]]

    def __init__(self, src: Mesh):
        self.m_Indices = []
        self.m_Vertices = []
        self.m_Skin = None
        self.m_Normals = None
        self.m_Tangents = None
        self.m_Colors = None
        self.m_UV0 = None
        self.m_UV1 = None
        self.m_UV2 = None
        self.m_UV3 = None
        self.m_UV4 = None
        self.m_UV5 = None
        self.m_UV6 = None
        self.m_UV7 = None

        self.__dict__.update(src.__dict__)
        self.m_VertexData = self.m_VertexData.unpack()

        # convert IndexBuffer
        # Unity fixed it in 2017.3.1p1 and later versions
        if (
            self.version >= (2017, 4)  # 2017.4
            # fixed after 2017.3.1px
            or self.version[:3] == (2017, 3, 1)
            and self.build_type.IsPatch
            # 2017.3.xfx with no compression
            or self.version[:2] == (2017, 3)
            and self.m_MeshCompression == 0
        ):
            self.m_Use16BitIndices = self.m_IndexFormat == 0

        if self.m_Use16BitIndices:
            self.m_IndexBuffer = struct.unpack(
                f"{self._reader.endian}{len(self.m_IndexBuffer)//2}H",
                bytes(self.m_IndexBuffer),
            )
        else:
            self.m_IndexBuffer = struct.unpack(
                f"{self._reader.endian}{len(self.m_IndexBuffer)//4}I",
                bytes(self.m_IndexBuffer),
            )

        if self.version >= (3, 5):  # 3.5 and up
            self.read_vertex_data()

        if self.version >= (2, 6):  # 2.6.0 and later
            self.decompress_compressed_mesh()

        self.get_triangles()

    def read_vertex_data(self):
        version = self.version
        m_VertexData = self.m_VertexData
        m_VertexCount = self.m_VertexCount = m_VertexData.m_VertexCount

        for chn, m_Channel in enumerate(m_VertexData.m_Channels):
            if m_Channel.dimension > 0:
                m_Stream = m_VertexData.m_Streams[m_Channel.stream]
                channelMask = bin(m_Stream.channelMask)[::-1]
                if channelMask[chn] == "1":
                    if version[0] < 2018 and chn == 2 and m_Channel.format == 2:
                        m_Channel.dimension = 4

                    componentByteSize = MeshHelper.get_format_size(
                        MeshHelper.convert_vertex_format(
                            m_Channel.format, self._reader.version
                        )
                    )
                    swap = self._reader.endian == "<" and componentByteSize > 1

                    if UnityPyBoost:
                        componentBytes = UnityPyBoost.unpack_vertexdata(
                            bytes(m_VertexData.m_DataSize),
                            componentByteSize,
                            m_VertexCount,
                            m_Stream.offset,
                            m_Stream.stride,
                            m_Channel.offset,
                            m_Channel.dimension,
                            swap,
                        )
                    else:
                        componentBytes = bytearray(
                            m_VertexCount * m_Channel.dimension * componentByteSize
                        )

                        vertexBaseOffset = m_Stream.offset + m_Channel.offset
                        for v in range(m_VertexCount):
                            vertexOffset = vertexBaseOffset + m_Stream.stride * v
                            for d in range(m_Channel.dimension):
                                componentOffset = vertexOffset + componentByteSize * d
                                vertexDataSrc = componentOffset
                                componentDataSrc = componentByteSize * (
                                    v * m_Channel.dimension + d
                                )
                                buff = m_VertexData.m_DataSize[
                                    vertexDataSrc : vertexDataSrc + componentByteSize
                                ]
                                if swap:  # swap bytes
                                    buff = buff[::-1]
                                componentBytes[
                                    componentDataSrc : componentDataSrc
                                    + componentByteSize
                                ] = buff

                    if MeshHelper.is_int_format(version, m_Channel.format):
                        componentsIntArray = MeshHelper.parse_int_array(
                            componentBytes, componentByteSize
                        )
                    else:
                        componentsFloatArray = MeshHelper.parse_float_array(
                            componentBytes,
                            componentByteSize,
                            MeshHelper.convert_vertex_format(m_Channel.format, version),
                        )

                    if version[0] >= 2018:
                        if chn == 0:  # kShaderChannelVertex
                            self.m_Vertices = componentsFloatArray
                        elif chn == 1:  # kShaderChannelNormal
                            self.m_Normals = componentsFloatArray
                        elif chn == 2:  # kShaderChannelTangent
                            self.m_Tangents = componentsFloatArray
                        elif chn == 3:  # kShaderChannelColor
                            self.m_Colors = componentsFloatArray
                        elif chn == 4:  # kShaderChannelTexCoord0
                            self.m_UV0 = componentsFloatArray
                        elif chn == 5:  # kShaderChannelTexCoord1
                            self.m_UV1 = componentsFloatArray
                        elif chn == 6:  # kShaderChannelTexCoord2
                            self.m_UV2 = componentsFloatArray
                        elif chn == 7:  # kShaderChannelTexCoord3
                            self.m_UV3 = componentsFloatArray
                        elif chn == 8:  # kShaderChannelTexCoord4
                            self.m_UV4 = componentsFloatArray
                        elif chn == 9:  # kShaderChannelTexCoord5
                            self.m_UV5 = componentsFloatArray
                        elif chn == 10:  # kShaderChannelTexCoord6
                            self.m_UV6 = componentsFloatArray
                        elif chn == 11:  # kShaderChannelTexCoord7
                            self.m_UV7 = componentsFloatArray
                        # 2018.2 and up
                        elif chn == 12:  # kShaderChannelBlendWeight
                            if not self.m_Skin:
                                self.InitMSkin()
                            for i in range(m_VertexCount):
                                for j in range(m_Channel.dimension):
                                    self.m_Skin[i].weight[j] = componentsFloatArray[
                                        i * m_Channel.dimension + j
                                    ]
                        elif chn == 13:  # kShaderChannelBlendIndices
                            if not self.m_Skin:
                                self.InitMSkin()
                            for i in range(m_VertexCount):
                                for j in range(m_Channel.dimension):
                                    self.m_Skin[i].boneIndex[j] = componentsIntArray[
                                        i * m_Channel.dimension + j
                                    ]
                    else:
                        if chn == 0:  # kShaderChannelVertex
                            self.m_Vertices = componentsFloatArray
                        elif chn == 1:  # kShaderChannelNormal
                            self.m_Normals = componentsFloatArray
                        elif chn == 2:  # kShaderChannelColor
                            self.m_Colors = componentsFloatArray
                        elif chn == 3:  # kShaderChannelTexCoord0
                            self.m_UV0 = componentsFloatArray
                        elif chn == 4:  # kShaderChannelTexCoord1
                            self.m_UV1 = componentsFloatArray
                        elif chn == 5:
                            if version[0] >= 5:  # kShaderChannelTexCoord2
                                self.m_UV2 = componentsFloatArray
                            else:  # kShaderChannelTangent
                                self.m_Tangents = componentsFloatArray
                        elif chn == 6:  # kShaderChannelTexCoord3
                            self.m_UV3 = componentsFloatArray
                        elif chn == 7:  # kShaderChannelTangent
                            self.m_Tangents = componentsFloatArray

    def decompress_compressed_mesh(self):
        # Vertex
        version = self.version
        m_CompressedMesh = self.m_CompressedMesh
        if m_CompressedMesh.m_Vertices.m_NumItems > 0:
            self.m_VertexCount = int(m_CompressedMesh.m_Vertices.m_NumItems / 3)
            self.m_Vertices = m_CompressedMesh.m_Vertices.unpack_floats(3, 3 * 4)
        m_VertexCount = self.m_VertexCount
        # UV
        if m_CompressedMesh.m_UV.m_NumItems > 0:  #
            m_UVInfo = m_CompressedMesh.m_UVInfo
            if m_UVInfo != 0:
                kInfoBitsPerUV = 4
                kUVDimensionMask = 3
                kUVChannelExists = 4
                kMaxTexCoordShaderChannels = 8

                uvSrcOffset = 0

                for uv in range(kMaxTexCoordShaderChannels):
                    texCoordBits = m_UVInfo >> (uv * kInfoBitsPerUV)
                    texCoordBits &= (1 << kInfoBitsPerUV) - 1
                    if (texCoordBits & kUVChannelExists) != 0:
                        uvDim = 1 + int(texCoordBits & kUVDimensionMask)
                        m_UV = m_CompressedMesh.m_UV.unpack_floats(
                            uvDim, uvDim * 4, uvSrcOffset, self.m_VertexCount
                        )
                        self.SetUV(uv, m_UV)
            else:
                self.m_UV0 = m_CompressedMesh.m_UV.unpack_floats(
                    2, 2 * 4, 0, m_VertexCount
                )
                if m_CompressedMesh.m_UV.m_NumItems >= m_VertexCount * 4:  #
                    self.m_UV1 = m_CompressedMesh.m_UV.unpack_floats(
                        2, 2 * 4, m_VertexCount * 2, m_VertexCount
                    )

        # BindPose
        if version < (5,):  # 5.0 down
            if m_CompressedMesh.m_BindPoses.m_NumItems > 0:  #
                m_BindPoses_Unpacked = m_CompressedMesh.m_BindPoses.unpack_floats(
                    16, 4 * 16
                )
                self.m_BindPose = [
                    Matrix4x4f(m_BindPoses_Unpacked[i : i + 16])
                    for i in range(0, m_CompressedMesh.m_BindPoses.m_NumItems, 16)
                ]
        # Normal
        if m_CompressedMesh.m_Normals.m_NumItems > 0:
            normalData = m_CompressedMesh.m_Normals.unpack_floats(2, 4 * 2)
            signs = m_CompressedMesh.m_NormalSigns.unpack_ints()
            self.m_Normals = []  # float[m_CompressedMesh.m_Normals.m_NumItems / 2 * 3]
            for i in range(0, math.ceil(m_CompressedMesh.m_Normals.m_NumItems / 2)):
                x = normalData[i * 2 + 0]
                y = normalData[i * 2 + 1]
                zsqr = 1 - x * x - y * y
                if zsqr >= 0:
                    z = math.sqrt(zsqr)
                else:
                    z = 0
                    normal = Vector3f(x, y, z)
                    normal.normalize()
                    x = normal.X
                    y = normal.Y
                    z = normal.Z
                if signs[i] == 0:
                    z = -z
                self.m_Normals.extend([x, y, z])
        # Tangent
        if m_CompressedMesh.m_Tangents.m_NumItems > 0:
            tangentData = m_CompressedMesh.m_Tangents.unpack_floats(2, 4 * 2)
            signs = m_CompressedMesh.m_TangentSigns.unpack_ints()
            self.m_Tangents = (
                []
            )  # float[m_CompressedMesh.m_Tangents.m_NumItems / 2 * 4]
            for i in range(0, math.ceil(m_CompressedMesh.m_Tangents.m_NumItems / 2)):
                x = tangentData[i * 2 + 0]
                y = tangentData[i * 2 + 1]
                zsqr = 1 - x * x - y * y
                if zsqr >= 0:
                    z = math.sqrt(zsqr)
                else:
                    z = 0
                    vector3f = Vector3f(x, y, z)
                    vector3f.normalize()
                    x = vector3f.X
                    y = vector3f.Y
                    z = vector3f.Z
                if signs[i * 2 + 0] == 0:  #
                    z = -z
                w = 1.0 if signs[i * 2 + 1] > 0 else -1.0
                self.m_Tangents.extend([x, y, z, w])

        # FloatColor
        if version >= (5,):  # 5.0 and up
            if m_CompressedMesh.m_FloatColors.m_NumItems > 0:  #
                self.m_Colors = m_CompressedMesh.m_FloatColors.unpack_floats(1, 4)

        # Skin
        if m_CompressedMesh.m_Weights.m_NumItems > 0:
            weights = m_CompressedMesh.m_Weights.unpack_ints()
            boneIndices = m_CompressedMesh.m_BoneIndices.unpack_ints()
            self.InitMSkin()
            bonePos = 0
            boneIndexPos = 0
            j = 0
            sum = 0

            for i in range(m_CompressedMesh.m_Weights.m_NumItems):
                # read bone index and weight.
                self.m_Skin[bonePos].weight[j] = weights[i] / 31.0
                self.m_Skin[bonePos].boneIndex[j] = boneIndices[boneIndexPos]
                boneIndexPos += 1
                j += 1
                sum += weights[i]

                # the weights add up to one. fill the rest for this vertex with zero, and continue with next one.
                if sum >= 31:  #
                    while j < 4:
                        self.m_Skin[bonePos].weight[j] = 0
                        self.m_Skin[bonePos].boneIndex[j] = 0
                        j += 1

                    bonePos += 1
                    j = 0
                    sum = 0
                # we read three weights, but they don't add up to one. calculate the fourth one, and read
                # missing bone index. continue with next vertex.
                elif j == 3:  #
                    self.m_Skin[bonePos].weight[j] = (31 - sum) / 31.0
                    self.m_Skin[bonePos].boneIndex[j] = boneIndices[boneIndexPos]
                    boneIndexPos += 1
                    bonePos += 1
                    j = 0
                    sum = 0
        # IndexBuffer
        if m_CompressedMesh.m_Triangles.m_NumItems > 0:  #
            self.m_IndexBuffer = m_CompressedMesh.m_Triangles.unpack_ints()
        # Color
        if (
            m_CompressedMesh.m_Colors is not None
            and self.m_CompressedMesh.m_Colors.m_NumItems > 0
        ):
            m_CompressedMesh.m_Colors.m_NumItems *= 4
            m_CompressedMesh.m_Colors.m_BitSize /= 4
            tempColors = m_CompressedMesh.m_Colors.unpack_ints()
            self.m_Colors = [color / 255 for color in tempColors]

    def get_triangles(self):
        m_IndexBuffer = self.m_IndexBuffer
        m_Indices = self.m_Indices

        for m_SubMesh in self.m_SubMeshes:
            firstIndex = m_SubMesh.firstByte // 2
            if not self.m_Use16BitIndices:
                firstIndex //= 2

            indexCount = m_SubMesh.indexCount
            topology = m_SubMesh.topology
            if topology == GfxPrimitiveType.kPrimitiveTriangles:
                m_Indices.extend(
                    m_IndexBuffer[firstIndex : firstIndex + indexCount - indexCount % 3]
                )

            elif (
                self.version[0] < 4
                or topology == GfxPrimitiveType.kPrimitiveTriangleStrip
            ):
                # de-stripify :
                triIndex = 0
                for i in range(indexCount - 2):
                    a, b, c = m_IndexBuffer[firstIndex + i : firstIndex + i + 3]

                    # skip degenerates
                    if a == b or a == c or b == c:
                        continue

                    # do the winding flip-flop of strips :
                    m_Indices.extend([b, a, c] if ((i & 1) == 1) else [a, b, c])
                    triIndex += 3
                # fix indexCount
                m_SubMesh.indexCount = triIndex

            elif topology == GfxPrimitiveType.kPrimitiveQuads:
                for q in range(0, indexCount, 4):
                    m_Indices.extend(
                        [
                            m_IndexBuffer[firstIndex + q],
                            m_IndexBuffer[firstIndex + q + 1],
                            m_IndexBuffer[firstIndex + q + 2],
                            m_IndexBuffer[firstIndex + q],
                            m_IndexBuffer[firstIndex + q + 2],
                            m_IndexBuffer[firstIndex + q + 3],
                        ]
                    )
                # fix indexCount
                m_SubMesh.indexCount = indexCount // 2 * 3

            else:
                raise NotImplementedError(
                    "Failed getting triangles. Submesh topology is lines or points."
                )

    def InitMSkin(self):
        self.m_Skin = [BoneWeights4() for _ in range(self.m_VertexCount)]

    def SetUV(self, uv: int, m_UV: List[float]):
        if uv == 0:
            self.m_UV0 = m_UV
        elif uv == 1:
            self.m_UV1 = m_UV
        elif uv == 2:
            self.m_UV2 = m_UV
        elif uv == 3:
            self.m_UV3 == m_UV
        elif uv == 4:
            self.m_UV4 == m_UV
        elif uv == 5:
            self.m_UV5 == m_UV
        elif uv == 6:
            self.m_UV6 == m_UV
        elif uv == 7:
            self.m_UV7 == m_UV
        else:
            raise IndexError("Out of Range")

    def GetUV(self, uv: int) -> Optional[List[float]]:
        if uv == 0:
            return self.m_UV0
        elif uv == 1:
            return self.m_UV1
        elif uv == 2:
            return self.m_UV2
        elif uv == 3:
            return self.m_UV3
        elif uv == 4:
            return self.m_UV4
        elif uv == 5:
            return self.m_UV5
        elif uv == 6:
            return self.m_UV6
        elif uv == 7:
            return self.m_UV7
        else:
            raise IndexError("Out of Range")


def unpack(self: Mesh) -> MeshUnpacked:
    return MeshUnpacked(self)


Mesh.unpack = unpack
