from typing import Union, Iterable, Tuple

class TypeTreeNode(object):
    __slots__ = (
        "m_Version",
        "m_Level",
        "m_TypeFlags",
        "m_ByteSize",
        "m_Index",
        "m_MetaFlag",
        "m_Type",
        "m_Name",
        "m_TypeStrOffset",
        "m_NameStrOffset",
        "m_RefTypeHash",
        "m_VariableCount",
    )
    m_Type: str
    m_Name: str
    m_ByteSize: int
    m_Index: int
    m_Version: int
    m_MetaFlag: int
    m_Level: int
    m_TypeStrOffset: int
    m_NameStrOffset: int
    m_RefTypeHash: str
    m_TypeFlags: int
    m_VariableCount: int

    def __init__(self, data: Union[dict, Iterable[Tuple]] = None, **kwargs):
        if isinstance(data, dict):
            items = data.items()
        elif kwargs:
            items = kwargs.items()
        else:
            items = data

        for key, val in items:
            setattr(self, key, val)

    def __repr__(self):
        return f"<TypeTreeNode({self.m_Level} {self.m_Type} {self.m_Name})>"


try:
    from ..UnityPyBoost import TypeTreeNode
except:
    pass
