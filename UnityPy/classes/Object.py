from ..files import ObjectReader


class Object:
    _reader: ObjectReader
    
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(**kwargs)

    @property
    def path_id(self):
        return self._reader.path_id

    @property
    def version(self):
        return self._reader.version
    
    @property
    def platform(self):
        return self._reader.platform
    
    @property
    def assets_file(self):
        return self._reader.assets_file

    @property
    def container(self):
        return self._reader.assets_file.container.path_dict.get(self.reader._path_id)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"