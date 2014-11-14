from ctypes import *
from ctypes import util
 
iokit = cdll.LoadLibrary(util.find_library('IOKit'))
cf = cdll.LoadLibrary(util.find_library('CoreFoundation'))
 
cf.CFStringCreateWithCString.argtypes = [c_void_p, c_char_p, c_int32]
cf.CFStringCreateWithCString.restype = c_void_p
cf.CFStringGetCStringPtr.argtypes = [c_void_p, c_uint32]
cf.CFStringGetCStringPtr.restype = c_char_p
 
kCFAllocatorDefault = c_void_p.in_dll(cf, "kCFAllocatorDefault")
kCFStringEncodingMacRoman = 0
 
kIOMasterPortDefault = c_void_p.in_dll(iokit, "kIOMasterPortDefault")
kIOPlatformSerialNumberKey = "IOPlatformSerialNumber".encode("mac_roman")
kIOPlatformUUIDKey = "IOPlatformUUID".encode("mac_roman")

iokit.IOServiceMatching.restype = c_void_p
iokit.IOServiceGetMatchingService.argtypes = [c_void_p, c_void_p]
iokit.IOServiceGetMatchingService.restype = c_void_p
iokit.IORegistryEntryCreateCFProperty.argtypes = [c_void_p, c_void_p, c_void_p, c_uint32]
iokit.IORegistryEntryCreateCFProperty.restype = c_void_p
iokit.IOObjectRelease.argtypes = [c_void_p]
 
 
def getHostId():
    platformExpert = iokit.IOServiceGetMatchingService(kIOMasterPortDefault,
                                                       iokit.IOServiceMatching("IOPlatformExpertDevice"))
    if platformExpert:
        #key = cf.CFStringCreateWithCString(kCFAllocatorDefault, kIOPlatformSerialNumberKey, kCFStringEncodingMacRoman)
        key = cf.CFStringCreateWithCString(kCFAllocatorDefault, kIOPlatformUUIDKey, kCFStringEncodingMacRoman)
        serialNumberAsCFString = \
            iokit.IORegistryEntryCreateCFProperty(platformExpert,
                                                  key,
                                                  kCFAllocatorDefault, 0);
        if serialNumberAsCFString:
            SERIAL = cf.CFStringGetCStringPtr(serialNumberAsCFString, 0)
       
        iokit.IOObjectRelease(platformExpert)
   
    return SERIAL
