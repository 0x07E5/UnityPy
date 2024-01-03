from PIL import Image, ImageDraw

from .Texture2DConverter import get_image_from_texture2d
from ..classes import Sprite, Texture2D, PPtr
from ..enums import (
    ClassIDType,
    SpritePackingMode,
    SpritePackingRotation,
    SpriteMeshType,
)
from ..streams import EndianBinaryReader


class SpriteSettings:
    def __init__(self, settingsRaw: int):
        self.settingsRaw = settingsRaw

    @property
    def packed(self):
        return self.settingsRaw & 1

    @property
    def packingMode(self):
        return SpritePackingMode((self.settingsRaw >> 1) & 1)

    @property
    def packingRotation(self):
        return SpritePackingRotation((self.settingsRaw >> 2) & 0xF)

    @property
    def meshType(self):
        return SpriteMeshType((self.settingsRaw >> 6) & 1)


def get_image(
    sprite: Sprite, texture: PPtr[Texture2D], alpha_texture: PPtr[Texture2D]
) -> Image.Image:
    if (
        alpha_texture
        and getattr(alpha_texture, "type", ClassIDType.UnknownType)
        == ClassIDType.Texture2D
    ):
        cache_id = (texture.m_PathID, alpha_texture.m_PathID)
        if cache_id not in sprite.assets_file._cache:
            original_image = get_image_from_texture2d(texture.deref_read(), False)
            alpha_image = get_image_from_texture2d(alpha_texture.deref_read(), False)
            original_image = Image.merge(
                "RGBA", (*original_image.split()[:3], alpha_image.split()[0])
            )
            sprite.assets_file._cache[cache_id] = original_image
    else:
        cache_id = texture.m_PathID
        if cache_id not in sprite.assets_file._cache:
            original_image = get_image_from_texture2d(texture.deref_read(), False)
            sprite.assets_file._cache[cache_id] = original_image
    return sprite.assets_file._cache[cache_id]


def get_image_from_sprite(m_Sprite: Sprite) -> Image.Image:
    atlas = None
    if getattr(m_Sprite, "m_SpriteAtlas", None):
        if m_Sprite.m_SpriteAtlas:
            atlas = m_Sprite.m_SpriteAtlas.deref_read()
    elif getattr(m_Sprite, "m_AtlasTags", None):
        # looks like the direct pointer is empty, let's try to find the Atlas via its name
        for obj in m_Sprite.assets_file.objects.values():
            if obj.type == ClassIDType.SpriteAtlas:
                atlas = obj.read()
                if atlas.m_Name == m_Sprite.m_AtlasTags[0]:
                    break
                atlas = None

    if atlas:
        for key, sprite_atlas_data in atlas.m_RenderDataMap:
            if key == m_Sprite.m_RenderDataKey:
                break
        else:
            raise FileNotFoundError("Failed to find sprite atlas!")
    else:
        sprite_atlas_data = m_Sprite.m_RD

    m_Texture2D = sprite_atlas_data.texture
    alpha_texture = sprite_atlas_data.alphaTexture
    texture_rect = sprite_atlas_data.textureRect
    settings_raw = SpriteSettings(sprite_atlas_data.settingsRaw)

    original_image = get_image(m_Sprite, m_Texture2D, alpha_texture)

    sprite_image = original_image.crop(
        (
            texture_rect.x,
            texture_rect.y,
            texture_rect.x + texture_rect.width,
            texture_rect.y + texture_rect.height,
        )
    )

    if settings_raw.packed == 1:
        rotation = settings_raw.packingRotation
        if rotation == SpritePackingRotation.kSPRFlipHorizontal:
            sprite_image = sprite_image.transpose(Image.FLIP_LEFT_RIGHT)
        # spriteImage = RotateFlip(RotateFlipType.RotateNoneFlipX)
        elif rotation == SpritePackingRotation.kSPRFlipVertical:
            sprite_image = sprite_image.transpose(Image.FLIP_TOP_BOTTOM)
        # spriteImage.RotateFlip(RotateFlipType.RotateNoneFlipY)
        elif rotation == SpritePackingRotation.kSPRRotate180:
            sprite_image = sprite_image.transpose(Image.ROTATE_180)
        # spriteImage.RotateFlip(RotateFlipType.Rotate180FlipNone)
        elif rotation == SpritePackingRotation.kSPRRotate90:
            sprite_image = sprite_image.transpose(Image.ROTATE_270)
    # spriteImage.RotateFlip(RotateFlipType.Rotate270FlipNone)

    if settings_raw.packingMode == SpritePackingMode.kSPMTight:
        # Tight

        # create mask to keep only the polygon
        mask = Image.new("1", sprite_image.size, color=0)
        draw = ImageDraw.ImageDraw(mask)
        for triangle in get_triangles(m_Sprite):
            draw.polygon(triangle, fill=1)

        # apply the mask
        if sprite_image.mode == "RGBA":
            # the image already has an alpha channel,
            # so we have to use composite to keep it
            empty_img = Image.new(sprite_image.mode, sprite_image.size, color=0)
            sprite_image = Image.composite(sprite_image, empty_img, mask)
        else:
            # add mask as alpha-channel to keep the polygon clean
            sprite_image.putalpha(mask)

    return sprite_image.transpose(Image.FLIP_TOP_BOTTOM)


def get_triangles(m_Sprite: Sprite):
    """
    returns the triangles of the sprite polygon
    """
    m_RD = m_Sprite.m_RD

    # read the raw points
    points = []
    if m_RD.vertices is not None:  # 5.6 down
        vertices = [v.pos for v in m_RD.vertices]
        points = [vertices[index] for index in m_RD.indices]
    else:  # 5.6 and up
        vertexdata = m_RD.m_VertexData.unpack()
        m_Channel = vertexdata.m_Channels[0]  # kShaderChannelVertex
        m_Stream = vertexdata.m_Streams[m_Channel.stream]

        vertexReader = EndianBinaryReader(vertexdata.m_DataSize, endian="<")
        indexReader = EndianBinaryReader(bytearray(m_RD.m_IndexBuffer), endian="<")

        for subMesh in m_RD.m_SubMeshes:
            vertexReader.Position = (
                m_Stream.offset
                + subMesh.firstVertex * m_Stream.stride
                + m_Channel.offset
            )

            vertices = []
            for _ in range(subMesh.vertexCount):
                vertices.append(vertexReader.read_vector3())
                vertexReader.Position = vertexReader.Position + m_Stream.stride - 12

            indexReader.Position = subMesh.firstByte

            for _ in range(subMesh.indexCount):
                points.append(
                    vertices[indexReader.read_u_short() - subMesh.firstVertex]
                )

    # normalize the points
    #  shift the whole point matrix into the positive space
    #  multiply them with a factor to scale them to the image
    min_x = min(p.x for p in points)
    min_y = min(p.y for p in points)
    factor = m_Sprite.m_PixelsToUnits
    points = [((p.x - min_x) * factor, (p.y - min_y) * factor) for p in points]

    # generate triangles from the given points
    return [points[i : i + 3] for i in range(0, len(points), 3)]
