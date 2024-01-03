__version__ = "2.0.0.dev"

from .environment import Environment
from .helpers.ArchiveStorageManager import set_assetbundle_decrypt_key


def load(*args, fs=None, **kwargs):
    return Environment(*args, fs=fs, **kwargs)


# backward compatibility
AssetsManager = Environment
