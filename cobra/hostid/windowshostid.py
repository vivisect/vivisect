import os
import ctypes

def getHostId():
    sysdrive = os.getenv('SystemDrive') + '\\'
    buf = ctypes.create_string_buffer(64)
    if not ctypes.windll.kernel32.GetVolumeNameForVolumeMountPointA(sysdrive, buf, ctypes.c_uint32(64)):
        return None
    return buf.value

