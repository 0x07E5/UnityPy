from ..generated import StreamingInfo
from ...helpers.ResourceReader import get_resource_data


def resolve_resource(self: StreamingInfo):
    return get_resource_data(
        self.path,
        self._reader.assets_file,
        self.offset,
        self.size,
    )


StreamingInfo.resolve = resolve_resource
