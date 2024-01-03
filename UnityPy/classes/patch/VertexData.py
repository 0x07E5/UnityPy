from typing import List, Optional

from ..generated import VertexData, StreamInfo, ChannelInfo
from ...helpers import MeshHelper


class VertexDataUnpacked(VertexData):
    m_DataSize: bytes
    m_VertexCount: int
    m_Channels: List[ChannelInfo]
    m_Streams: List[StreamInfo]
    m_CurrentChannels: Optional[int]

    def __init__(self, src: VertexData):
        self._reader = src._reader
        self.m_DataSize = src.m_DataSize
        self.m_VertexCount = src.m_VertexCount
        self.m_Channels = src.m_Channels
        self.m_CurrentChannels = src.m_CurrentChannels
        if isinstance(src.m_Streams, list):
            self.m_Streams = src.m_Streams
        else:
            self.m_Streams = [
                src.m_Streams_0_,
                src.m_Streams_1_,
                src.m_Streams_2_,
                src.m_Streams_3_,
            ]

        version = src._reader.version
        if version < (4,):  # 4.0 down
            self.get_channels()
        elif version >= (5,):  # 5.0 and up
            self.get_streams()

    def get_streams(self):
        assert self.m_Channels is not None

        streamCount = 1
        if self.m_Channels:
            streamCount += max(x.stream for x in self.m_Channels)

        self.m_Streams = [None] * streamCount
        offset = 0
        for s in range(streamCount):
            chnMask = 0
            stride = 0
            for chn, m_Channel in enumerate(self.m_Channels):
                if m_Channel.stream == s:
                    if m_Channel.dimension > 0:
                        chnMask |= 1 << chn  # Shift 1UInt << chn
                        stride += m_Channel.dimension * MeshHelper.get_format_size(
                            MeshHelper.convert_vertex_format(
                                m_Channel.format, self._reader.version
                            )
                        )
            self.m_Streams[s] = StreamInfo(
                channelMask=chnMask,
                offset=offset,
                stride=stride,
                dividerOp=0,
                frequency=0,
            )
            offset += self.m_VertexCount * stride
            # static size_t align_streamSize (size_t size) { return (size + (kVertexStreamAlign-1)) & ~(kVertexStreamAlign-1)
            offset = (offset + (16 - 1)) & ~(
                16 - 1
            )  # (offset + (16u - 1u)) & ~(16u - 1u);

    def get_channels(self):
        assert self.m_Streams is not None

        self.m_Channels = []  # ChannelInfo[6]
        for i in range(6):
            self.m_Channels.append(ChannelInfo(self._reader))
        for s, m_Stream in enumerate(self.m_Streams):
            channelMask = bytearray(m_Stream.channelMask)  # BitArray
            offset = 0
            for i in range(6):
                if channelMask[i]:
                    m_Channel = self.m_Channels[i]
                    m_Channel.stream = s
                    m_Channel.offset = offset
                    if i in [0, 1]:
                        # 0 - kShaderChannelVertex
                        # 1 - kShaderChannelNormal
                        m_Channel.format = 0  # kChannelFormatFloat
                        m_Channel.dimension = 3
                    elif i == 2:  # kShaderChannelColor
                        m_Channel.format = 2  # kChannelFormatColor
                        m_Channel.dimension = 4
                    elif i in [3, 4]:
                        # 3 - kShaderChannelTexCoord0
                        # 4 - kShaderChannelTexCoord1
                        m_Channel.format = 0  # kChannelFormatFloat
                        m_Channel.dimension = 2
                    elif i == 5:  # kShaderChannelTangent
                        m_Channel.format = 0  # kChannelFormatFloat
                        m_Channel.dimension = 4
                    offset += m_Channel.dimension * MeshHelper.get_format_size(
                        MeshHelper.convert_vertex_format(
                            m_Channel.format, self._reader.version
                        )
                    )


def unpack(self) -> VertexDataUnpacked:
    return VertexDataUnpacked(self)


VertexData.unpack = unpack
