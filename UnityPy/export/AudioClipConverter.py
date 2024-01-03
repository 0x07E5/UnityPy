import ctypes
import os
import platform

from ..classes.generated import AudioClip
from UnityPy.streams import EndianBinaryWriter

# pyfmodex loads the dll/so/dylib on import
# so we have to adjust the environment vars
# before importing it
# This is done in import_pyfmodex()
# which will replace the global pyfmodex var
pyfmodex = None


def import_pyfmodex():
    global pyfmodex
    if pyfmodex is not None:
        return

    ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    # determine system - Windows, Darwin, Linux, Android
    system = platform.system()
    if system == "Linux" and "ANDROID_BOOTLOGO" in os.environ:
        system = "Android"
    # determine architecture
    machine = platform.machine()
    arch = platform.architecture()[0]

    if system in ["Windows", "Darwin"]:
        if arch == "32bit":
            arch = "x86"
        elif arch == "64bit":
            arch = "x64"
    elif system == "Linux":
        # Raspberry Pi and Linux on arm projects
        if "arm" in machine:
            if arch == "32bit":
                arch = "armhf" if machine.endswith("l") else "arm"
            elif arch == "64bit":
                # Raise an exception for now; Once it gets supported by FMOD we can just modify the code here
                pyfmodex = False
                raise NotImplementedError(
                    "ARM64 not supported by FMOD.\nUse a 32bit python version."
                )
        elif arch == "32bit":
            arch = "x86"
        elif arch == "64bit":
            arch = "x86_64"
    else:
        pyfmodex = False
        raise NotImplementedError(
            "Couldn't find a correct FMOD library for your system ({system} - {arch})."
        )

    # build path and load library
    LIB_PATH = os.path.join(ROOT, "lib", "FMOD", system, arch)

    # prepare the environment for pyfmodex
    if system == "Windows":
        os.environ["PYFMODEX_DLL_PATH"] = os.path.join(LIB_PATH, "fmod.dll")
    else:
        ext = "dylib" if system == "Darwin" else "so"
        os.environ["PYFMODEX_DLL_PATH"] = os.path.join(LIB_PATH, f"libfmod.{ext}")

        # hotfix ctypes for pyfmodex for non windows
        ctypes.windll = getattr(ctypes, "windll", None)

    import pyfmodex


def extract_audioclip_samples(clip: AudioClip) -> dict:
    """extracts all the samples from an AudioClip
    :param audio: AudioClip
    :type audio: AudioClip
    :return: {filename : sample(bytes)}
    :rtype: dict
    """
    data = getattr(clip, "m_AudioData", None)
    if data:
        data = bytes(data)
    elif hasattr(clip, "m_Resource"):
        data = clip.m_Resource.resolve()

    if not data:
        # eg. StreamedResource not available
        return {}

    magic = memoryview(data)[:8]

    ext = None
    if magic[:4] == b"OggS":
        ext = "ogg"
    elif magic[:4] == b"RIFF":
        ext = "wav"
    elif magic[4:8] == b"ftyp":
        ext = "m4a"
    else:
        return dump_samples(clip, bytes(data))

    return {f"{clip.m_Name}.{ext}": data}


def dump_samples(clip: AudioClip, data: bytes):
    if pyfmodex is None:
        import_pyfmodex()
    if not pyfmodex:
        return {}
    # init system
    system = pyfmodex.System()
    system.init(clip.m_Channels, pyfmodex.flags.INIT_FLAGS.NORMAL, None)

    sound = system.create_sound(
        data,
        pyfmodex.flags.MODE.OPENMEMORY,
        exinfo=pyfmodex.structure_declarations.CREATESOUNDEXINFO(
            length=len(data),
            numchannels=clip.m_Channels,
            defaultfrequency=clip.m_Frequency,
        ),
    )

    # iterate over subsounds
    samples = {}
    for i in range(sound.num_subsounds):
        if i > 0:
            filename = "%s-%i.wav" % (clip.m_Name, i)
        else:
            filename = "%s.wav" % clip.m_Name
        subsound = sound.get_subsound(i)
        samples[filename] = subsound_to_wav(subsound)
        subsound.release()

    sound.release()
    system.release()
    return samples


def subsound_to_wav(subsound):
    # get sound settings
    length = subsound.get_length(pyfmodex.enums.TIMEUNIT.PCMBYTES)
    channels = subsound.format.channels
    bits = subsound.format.bits
    sample_rate = int(subsound.default_frequency)

    # write to buffer
    w = EndianBinaryWriter(endian="<")
    # riff chucnk
    w.write(b"RIFF")
    w.write_int(length + 36)  # sizeof(FmtChunk) + sizeof(RiffChunk) + length
    w.write(b"WAVE")
    # fmt chunck
    w.write(b"fmt ")
    w.write_int(16)  # sizeof(FmtChunk) - sizeof(RiffChunk)
    w.write_short(1)
    w.write_short(channels)
    w.write_int(sample_rate)
    w.write_int(sample_rate * channels * bits // 8)
    w.write_short(channels * bits // 8)
    w.write_short(bits)
    # data chunck
    w.write(b"data")
    w.write_int(length)
    # data
    lock = subsound.lock(0, length)
    for ptr, length in lock:
        ptr_data = ctypes.string_at(ptr, length.value)
        w.write(ptr_data)
    subsound.unlock(*lock)
    return w.bytes
