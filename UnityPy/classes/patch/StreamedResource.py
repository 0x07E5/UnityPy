from ..generated import StreamedResource
from ...helpers.ResourceReader import get_resource_data


def resolve_resource(self: StreamedResource):
    return get_resource_data(
        self.m_Source, self._reader.assets_file, self.m_Offset, self.m_Size
    )


StreamedResource.resolve = resolve_resource
