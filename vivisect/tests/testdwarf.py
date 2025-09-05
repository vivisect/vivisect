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
        #found = realfuncs - dbgfuncs

        missing = dbgfuncs - realfuncs
        self.len(missing, 0)
