# architecture registration
import vivisect.archs.arm.cpu
import vivisect.archs.i386.cpu
import vivisect.archs.amd64.cpu

# binfile parser registration
import vivisect.formats.pe.binfile
import vivisect.formats.elf.binfile
import vivisect.formats.blob.binfile
import vivisect.formats.macho.binfile

import vivisect.lib.thishost as v_thishost

if v_thishost.check(platform='windows'):
    import vivisect.runtime.windows.target

