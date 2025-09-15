import logging

import vivisect.tests.utils as v_t_utils
import vivisect.tests.helpers as v_t_helpers

logger = logging.getLogger(__name__)

class DwarfTest(v_t_utils.VivTest):
    @classmethod
    def setUpClass(cls):
        cls.vw = v_t_helpers.getTestWorkspace('linux', 'i386', 'chgrp.llvm')

    def test_dwarf_functions(self):
        vw = self.vw
        realfuncs = set(self.vw.getFunctions())
        self.len(vw.debuginfo.functions, 200)
        self.len([x.start for x in vw.debuginfo.functions if x.start is not None], 199)

        missing = [x for x in vw.debuginfo.functions if x.start is None]
        self.len(missing, 1)
        self.eq(missing[0].name, 'stpcpy')

        dbgfuncs = set([x.start for x in self.vw.debuginfo.functions if x.start is not None])

        missing = dbgfuncs - realfuncs
        self.len(missing, 0)

        # structs
        self.len(vw.debuginfo.structs, 68)
        names = [x.name for x in vw.debuginfo.structs]
        self.isin('quoting_options', names)
        self.isin('dev_ino', names)
        self.isin('timespec', names)

        # we end up with two copies since it's defined twice (even dwarfdump lists in twice total)
        structs = [x for x in vw.debuginfo.structs if x.name == 'Chown_option']
        self.len(structs, 2)
        mnames = [m.name for m in structs[0].members]
        self.eq(mnames, [
            'verbosity',
            'recurse',
            'root_dev_info',
            'affect_symlink_referent',
            'force_silent',
            'user_name',
            'group_name'
        ])
