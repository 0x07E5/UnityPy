from dataclasses import dataclass
from typing import TypeVar, Generic, Union

from ..files import ObjectReader
from ..enums import ClassIDType

T = TypeVar("T")

@dataclass
class PPtr(Generic[T]):
    m_FileID: int
    m_PathID: int
    _reader: ObjectReader
    _obj: Union[ObjectReader, None] = None
    
    def __init__(self, m_FileID: int, m_PathID: int):
        self.m_FileID = m_FileID
        self.m_PathID = m_PathID

    def deref(self) -> ObjectReader:
        if self._obj is not None:
            return self._obj

        manager = None
        assetsfile = self._reader.assets_file

        if self.m_FileID == 0:
            manager = assetsfile

        elif self.m_FileID > 0 and self.m_FileID - 1 < len(assetsfile.externals):
            if self.index == -2:
                environment = assetsfile.environment
                external_name = self.external_name
                # try to find it in the already registered cabs
                manager = environment.get_cab(external_name)
                # not found, load all dependencies and try again
                if not manager:
                    assetsfile.load_dependencies([external_name])
                    manager = environment.get_cab(external_name)

        if manager is not None:
            self._obj = manager.objects.get(self.m_PathID)

        if self._obj is None:
            # TODO: add more details to error
            raise FileNotFoundError("Failed to resolve pointer!")

        return self._obj

    def deref_read(self) -> T:
        return self.deref().read()

    @property
    def type(self):
        obj = self.deref()
        if obj is None:
            return ClassIDType.UnknownType
        return obj.type

    @property
    def external_name(self):
        assetsfile = self._reader.assets_file
        if self.m_FileId > 0 and self.m_FileId - 1 < len(assetsfile.externals):
            return assetsfile.externals[self.m_FileId - 1].name

    def __repr__(self):
        try:
            return f"PPtr<{self.deref().__class__.__repr__(self.deref())}>"
        except Exception as e:
            return f"PPtr<{e}>"

    def __bool__(self):
        try:
            self.deref()
            return True
        except:
            return False
