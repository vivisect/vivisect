'''
Vivisect parser for Volvo Binary Files (VBF) used in firmware, notably in 
the automotive industry
'''
import struct
import vivisect.const as v_const
import vivisect.parsers as v_parsers

def parseFile(vw, filename, baseaddr=None):
    fd = file(filename, 'rb')
    return loadVbfIntoWorkspace(vw, fd, filename=filename, baseaddr=baseaddr)

def parseBytes(vw, bytes, baseaddr=None):
    fd = StringIO(bytes)
    return loadVbfIntoWorkspace(vw, fd, filename=filename, baseaddr=baseaddr)

def parseFd(vw, fd, filename=None, baseaddr=None):
    fd.seek(0)
    return loadVbfIntoWorkspace(vw, fd, filename=filename, baseaddr=baseaddr)

def parseMemory(vw, memobj, baseaddr):
    raise Exception('no parseMemory for VBFs!')

def parseVBF(vbf):
    braces = 0
    for idx in range(len(vbf)):
        if vbf[idx] == '{':
            braces += 1
        elif vbf[idx] == '}':
            braces -= 1
            if not braces:
                break
    header = vbf[:idx+1]
    bindata = vbf[idx+1:]

    blocks = []
    while len(bindata):
        addr, size = struct.unpack_from('>II', bindata, 0)
        print hex(addr), hex(size)
        block = bindata[8:8+size]
        checksum = struct.unpack_from('>H', bindata, 8+size)
        blocks.append((addr, block, checksum))
        bindata = bindata[size + 10:]

    return header, bindata, blocks

def loadVbfIntoWorkspace(vw, fd, filename, baseaddr):
    vbf = fd.read()
    hdr, bdata, blocks = parseVBF(vbf)
    arch = vw.config.viv.parsers.vbf.arch
    if not arch:
        raise Exception('VBF loader *requires* arch option (-O viv.parsers.ihex.arch=\\"<archname>\\")')

    bigend = vw.config.viv.parsers.vbf.bigend
    if not bigend:
        raise Exception('VBF loader *requires* arch option (-O viv.parsers.ihex.bigend=\\"(true,false)\\")')

    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform','Unknown')
    vw.setMeta('Format','vbf')
    vw.setMeta('bigend', bigend)

    vw.setMeta('DefaultCall', v_const.archcalls.get(arch,'unknown'))

    # add memorymaps, segments, and find lowest address
    baseva = 0xffffffff
    for addr, data, checksum in blocks:
        vw.addMemoryMap(addr, 7, 'map_%x' % addr, data)
        vw.addSegment(addr, len(data), '%.8x' % addr, filename)
        if addr < baseva:
            baseva = addr
    
    fname = vw.addFile(filename, baseva, v_parsers.md5Bytes(bdata))  # use vbf?
    vw.setFileMeta(fname, 'header', hdr)
