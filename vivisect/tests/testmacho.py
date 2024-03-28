import logging
import unittest

import vstruct.defs.macho as vs_macho
import vstruct.defs.macho.const as vsm_const

import vivisect.tests.utils as utils
import vivisect.tests.helpers as helpers
import vivisect.parsers.macho as v_p_macho

logger = logging.getLogger(__name__)


class MachOTests(utils.VivTest):
    @classmethod
    def setUpClass(cls):
        super(MachOTests, cls).setUpClass()
        byts = helpers.getTestBytes('osx', 'amd64', 'safaridriver.bin')
        cls.safari = vs_macho.mach_o()
        cls.safari.vsParse(byts)
        # TODO: plumb a full workspace test after updating the parser

    def test_basic(self):
        header = self.safari.mach_header
        self.eq(vsm_const.MH_MAGIC_64, header.magic)
        self.eq(vsm_const.CPU_TYPE_X86_64, header.cputype)
        self.eq(0x80000003, header.cpusubtype)
        self.eq(vsm_const.MH_EXECUTE, header.filetype)
        self.eq(20, header.ncmds)
        self.eq(1640, header.sizeofcmds)
        self.eq(vsm_const.MH_PIE, header.flags & vsm_const.MH_PIE)
        self.eq(vsm_const.MH_TWOLEVEL, header.flags & vsm_const.MH_TWOLEVEL)
        self.eq(vsm_const.MH_DYLDLINK, header.flags & vsm_const.MH_DYLDLINK)
        self.eq(vsm_const.MH_NOUNDEFS, header.flags & vsm_const.MH_NOUNDEFS)

        self.len(self.safari.load_commands._vs_fields, header.ncmds)

        answers = {
            'cmd0': {
                'cmd': 25,
                'cmdsize': 72,
                'segname': '__PAGEZERO',
                'vmaddr': 0,
                'vmsize': 4294967296,
                'fileoff': 0,
                'filesize': 0,
                'maxprot': 0,
                'initprot': 0,
                'nsects': 0,
                'flags': 0,
            },
            'cmd1': {
                'cmd': 25,
                'cmdsize': 472,
                'segname': '__TEXT',
                'vmaddr': 4294967296,
                'vmsize': 4096,
                'fileoff': 0,
                'filesize': 4096,
                'maxprot': 7,
                'initprot': 5,
                'nsects': 5,
                'flags': 0,
            },
            'cmd2': {
                'cmd': 25,
                'cmdsize': 312,
                'segname': '__DATA',
                'vmaddr': 4294971392,
                'vmsize': 4096,
                'fileoff': 4096,
                'filesize': 4096,
                'maxprot': 7,
                'initprot': 3,
                'nsects': 3,
                'flags': 0,
            },
            'cmd3': {
                'cmd': 25,
                'cmdsize': 72,
                'segname': '__LINKEDIT',
                'vmaddr': 4294975488,
                'vmsize': 12288,
                'fileoff': 8192,
                'filesize': 10128,
                'maxprot': 7,
                'initprot': 1,
                'nsects': 0,
                'flags': 0,
            },
            'cmd4': {
                'cmd': 0x80000022,
                'cmdsize': 48,
                'rebase_off': 8192,
                'rebase_size': 8,
                'bind_off': 0x2008,
                'bind_size': 0x18,
                'weak_bind_off': 0,
                'weak_bind_size': 0,
                'lazy_bind_off': 0x2020,
                'lazy_bind_size': 0x20,
                'export_off': 0x2040,
                'export_size': 0x20,
            },
            'cmd5': {
                'cmd': 2,
                'cmdsize': 0x18,
                'symoff': 0x2068,
                'nsyms': 4,
                'stroff': 0x20b8,
                'strsize': 0x50,
            },
            'cmd6': {
                'cmd': 0xb,
                'cmdsize': 0x50,
                'ilocalsym': 0,
                'nlocalsym': 1,
                'iextdefsym': 1,
                'nextdefsym': 1,
                'iundefsym': 2,
                'nundefsym': 2,
                'tocoff': 0,
                'ntoc': 0,
                'modtaboff': 0,
                'nmodtab': 0,
                'extrefsymoff': 0,
                'nextrefsyms': 0,
                'indirectsymoff': 0x20a8,
                'nindirectsyms': 4,
                'extreloff': 0,
                'nextrel': 0,
                'locreloff': 0,
                'nlocrel': 0,
            },
            'cmd8': {
                'cmd': 0x1b,
                'cmdsize': 24,
                'uuid': "b'\\xbc\\xaaJ\\x0b\\xbfp:]\\xbc\\xf9r\\xf3\\x97\\x80\\xebg'",
            },
            'cmd19': {
                'cmd': 29,
                'cmdsize': 16,
                'dataoff': 8464,
                'datasize': 9856,
            }
        }

        for seg, seginfo in answers.items():
            cmd = self.safari.load_commands[seg]
            self.eq(len(cmd), cmd.cmdsize)
            for key, valu in seginfo.items():
                if type(cmd[key]._vs_value) is bytes:
                    self.eq(str(cmd[key]), valu)
                else:
                    self.eq(cmd[key], valu)

    def test_sections(self):
        answers = {
            'cmd1': [
                {
                    'sectname': '__text',
                    'segname': '__TEXT',
                    'addr': 0x100000a80,
                    'size': 0xa,
                    'offset': 0xa80,
                    'align': 0,
                    'reloff': 0,
                    'nreloc': 0,
                    'flags': 0x80000400,
                    'reserved1': 0,
                    'reserved2': 0,
                    'reserved3': 0,
                },
                {
                    'sectname': '__stubs',
                    'segname': '__TEXT',
                    'addr': 0x100000a8a,
                    'size': 0x6,
                    'offset': 0xa8a,
                    'align': 1,
                    'reloff': 0,
                    'nreloc': 0,
                    'flags': 0x80000408,
                    'reserved1': 0,
                    'reserved2': 6,
                    'reserved3': 0,
                },
                {
                    'sectname': '__stub_helper',
                    'segname': '__TEXT',
                    'addr': 0x100000a90,
                    'size': 0x1a,
                    'offset': 0xa90,
                    'align': 2,
                    'reloff': 0,
                    'nreloc': 0,
                    'flags': 0x80000400,
                    'reserved1': 0,
                    'reserved2': 0,
                    'reserved3': 0,
                },
                {
                    'sectname': '__info_plist',
                    'segname': '__TEXT',
                    'addr': 0x100000aaa,
                    'size': 0x50e,
                    'offset': 0xaaa,
                    'align': 0,
                    'reloff': 0,
                    'nreloc': 0,
                    'flags': 0,
                    'reserved1': 0,
                    'reserved2': 0,
                    'reserved3': 0,
                },
                {
                    'sectname': '__unwind_info',
                    'segname': '__TEXT',
                    'addr': 0x100000fb8,
                    'size': 0x48,
                    'offset': 0xfb8,
                    'align': 2,
                    'reloff': 0,
                    'nreloc': 0,
                    'flags': 0,
                    'reserved1': 0,
                    'reserved2': 0,
                    'reserved3': 0,
                },
            ]
        }

        for seg, sectinfo in answers.items():
            cmd = self.safari.load_commands[seg]
            for idx, section in enumerate(sectinfo):
                realsect = cmd.sections[idx]
                for name, valu in section.items():
                    if type(realsect[name]._vs_value) is bytes:
                        self.eq(valu, str(realsect[name]))
                    else:
                        self.eq(valu, realsect[name])

    def test_version_segment(self):
        for idx, lc in self.safari.load_commands:
            if lc.cmd == vsm_const.LC_SOURCE_VERSION:
                ver = lc.getVersion()
                self.eq('7605.1.33.1.4', ver)
