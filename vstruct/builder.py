'''

VStruct builder!  Used to serialize structure definitions etc...

'''

import copy
import types
import inspect
import vstruct
import vstruct.primitives as vs_prim

prim_types = [ None, 
               vs_prim.v_uint8,
               vs_prim.v_uint16,
               None,
               vs_prim.v_uint32,
               None, None, None,
               vs_prim.v_uint64
             ]

# VStruct Field Flags
VSFF_POINTER = 1

class VStructConstructor:
    def __init__(self, builder, vsname):
        self.builder = builder
        self.vsname = vsname

    def __call__(self, *args, **kwargs):
        return self.builder.buildVStruct(self.vsname)

class VStructBuilder:

    def __init__(self, defs=(), enums=()):
        self._vs_defs = {}
        self._vs_ctors = {}
        self._vs_enums = {}
        self._vs_namespaces = {}
        for vsdef in defs:
            self.addVStructDef(vsdef)
        for enum in enums:
            self.addVStructEnumeration(enum)

    def __getattr__(self, name):
        ns = self._vs_namespaces.get(name)
        if ns != None:
            return ns

        # Check if we have an added constructor
        ctor = self._vs_ctors.get(name)
        if ctor:
            return ctor

        vsdef = self._vs_defs.get(name)
        if vsdef != None:
            return VStructConstructor(self, name)

        raise AttributeError, name

    def getVStructCtorNames(self):
        return self._vs_ctors.keys()

    def addVStructCtor(self, sname, ctor):
        self._vs_ctors[ sname ] = ctor

    def delVStructCtor(self, sname):
        return self._vs_ctors.pop( sname , None)

    def addVStructEnumeration(self, enum):
        self._vs_enums[enum[0]] = enum

    def addVStructNamespace(self, name, builder):
        self._vs_namespaces[name] = builder

    def getVStructNamespaces(self):
        return self._vs_namespaces.items()

    def getVStructNamespaceNames(self):
        return self._vs_namespaces.keys()

    def hasVStructNamespace(self, namespace):
        return self._vs_namespaces.get(namespace, None) != None

    def getVStructNames(self, namespace=None):
        if namespace == None:
            return self._vs_defs.keys() + self._vs_ctors.keys()

        nsmod = self._vs_namespaces.get(namespace)
        if isinstance(nsmod, VStructBuilder):
            return nsmod.getVStructNames()

        ret = []
        for name in dir(nsmod):
            nobj = getattr(nsmod, name)
            if not inspect.isclass(nobj):
                continue
            if issubclass(nobj, vstruct.VStruct):
                ret.append(name)
        return ret

    def addVStructDef(self, vsdef):
        vsname = vsdef[0]
        self._vs_defs[vsname] = vsdef

    def _buildVsType(self, tname, tsize, tflags):

        if tflags & VSFF_POINTER:
            if tsize == 4:
                return vs_prim.v_ptr32()

            elif tsize == 8:
                return vs_prim.v_ptr64()

            else:
                raise Exception('Invalid Pointer Width: %d' % tsize)

        if tname != None:
            return self.buildVStruct(tname)

        if tsize not in [1,2,4,8]:
            return v_bytes(size=tsize)

        return prim_types[tsize]()

    def buildVStruct(self, vsname):
        # Check for a namespace
        parts = vsname.split('.', 1)
        if len(parts) == 2:
            ns = self._vs_namespaces.get(parts[0])
            if ns == None:
                raise Exception('Namespace %s is not present! (need symbols?)' % parts[0])

            # If a module gets added as a namespace, assume it has a class def...
            if isinstance(ns, types.ModuleType):
                cls = getattr(ns, parts[1])
                if cls == None:
                    raise Exception('Unknown VStruct Definition: %s' % vsname)
                return cls()

            return ns.buildVStruct(parts[1])

        ctor = self._vs_ctors.get(vsname)
        if ctor != None:
            return ctor()

        vsdef = self._vs_defs.get(vsname)

        # If we still dont have a def, lets ask our namespaces
        if vsdef == None:
            for ns in self._vs_namespaces.values():

                if isinstance(ns, types.ModuleType):
                    cls = getattr(ns, vsname, None)
                    if cls != None:
                       return cls()

                else:

                    vsdef = ns._vs_defs.get(vsname)
                    if vsdef != None:
                        break

        if vsdef == None:
            return None

        vsname, vssize, vskids = vsdef

        vs = vstruct.VStruct()
        vs._vs_name = vsname
    

        for fname, foffset, fsize, ftypename, fflags, fcount in vskids:

            fieldval = self._buildVsType(ftypename, fsize, fflags)

            if fcount != None:
                afields = [copy.deepcopy(fieldval) for i in xrange(fcount) ]
                fieldval = vstruct.VArray(afields)

            cursize = len(vs)
            if foffset < cursize:
                continue

            if foffset > cursize:
                setattr(vs, '_pad%.4x' % foffset, vs_prim.v_bytes(size=(foffset-cursize)))

            setattr(vs, fname, fieldval)

        final_len = len(vs)
        if final_len < vssize:
            setattr(vs, '_pad%.4x' % vssize, vs_prim.v_bytes(size=(vssize-final_len)))

        return vs

    def _genTypeConstructor(self, tname, tsize, tflags):
        if tflags & VSFF_POINTER:
            if tsize == 4:
                return 'v_ptr32()'
            elif tsize == 8:
                return 'v_ptr64()'
            else:
                return 'v_bytes(size=%d)' % tsize

        if tname != None:
            return '%s()' % tname

        # It's a base numeric type!
        if tsize == 1:
            return 'v_uint8()'
        elif tsize == 2:
            return 'v_uint16()'
        elif tsize == 4:
            return 'v_uint32()'
        elif tsize == 8:
            return 'v_uint64()'
        else:
            return 'v_bytes(size=%d)' % tsize

    def genVStructPyCode(self):
        ret = 'import vstruct\n'
        ret += 'from vstruct.primitives import *'
        ret += '\n\n'

        for ename, esize, ekids in self._vs_enums.values():
            ret += '%s = v_enum()\n' % ename
            for kname, kval in ekids:
                ret += '%s.%s = %d\n' % (ename,kname,kval)
            ret += '\n\n'


        for vsname, vsize, vskids in self._vs_defs.values():
            ret += 'class %s(vstruct.VStruct):\n' % vsname
            ret += '    def __init__(self):\n'
            ret += '        vstruct.VStruct.__init__(self)\n'
            offset = 0
            for fname, foffset, fsize, ftypename, fflags, fcount in vskids:

                # Skip overlapped fields
                if foffset < offset:
                    continue

                # Add pad if needed to reach next offset
                if foffset > offset:
                    ret += '        self._pad%.4x = v_bytes(size=%d)\n' % (foffset, foffset-offset)
                    offset += (foffset - offset)

                fconst = self._genTypeConstructor(ftypename, fsize, fflags)

                # If fcount != None, we're an array!
                if fcount != None:
                    fconst = 'vstruct.VArray([ %s for i in xrange(%d) ])' % (fconst, fcount)
                    fsize *= fcount

                ret += '        self.%s = %s\n' % (fname, fconst)
                offset += fsize
            # Check if we need to do final pading
            if offset < vsize:
                psize = vsize - offset
                ret += '        self._pad%.4x = v_bytes(size=%d)\n' % (vsize, psize)
            ret += '\n\n'

        return ret

if __name__ == '__main__':
    # Parse windows structures from dll symbols...
    import os
    import sys
    import platform

    from pprint import pprint

    import PE
    import vtrace.platforms.win32 as vt_win32

    p = PE.PE(file(sys.argv[1], 'rb'))
    baseaddr = p.IMAGE_NT_HEADERS.OptionalHeader.ImageBase
    osmajor = p.IMAGE_NT_HEADERS.OptionalHeader.MajorOperatingSystemVersion
    osminor = p.IMAGE_NT_HEADERS.OptionalHeader.MinorOperatingSystemVersion
    machine = p.IMAGE_NT_HEADERS.FileHeader.Machine

    vsver = p.getVS_VERSIONINFO()

    archname = PE.machine_names.get(machine)

    parser = vt_win32.Win32SymbolParser(0xffffffff, sys.argv[1], baseaddr)
    parser.parse()

    t = parser._sym_types.values()
    e = parser._sym_enums.values()
    builder = VStructBuilder(defs=t, enums=e)

    print '# Version: %d.%d' % (osmajor, osminor)
    print '# Architecture: %s' % archname
    if vsver != None:
        keys = vsver.getVersionKeys()
        keys.sort()
        for k in keys:
            val = vsver.getVersionValue(k)
            if type(val) == unicode:
                val = val.encode('ascii','ignore')
            print '# %s: %s' % (k,val)
    print builder.genVStructPyCode()

