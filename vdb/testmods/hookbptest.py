import vtrace.breakpoints
import vdb.testmods as v_testmods

# in order for these tests to 'pass', these syms need to be in impapi and be
# called multiple times by python.
plat_syms = {
    'windows': 'ntdll.rtlencodepointer',
}


def prehook(event, trace, ret_addr, args, callconv):
    trace.setMeta('prehookhit', True)
    cur = trace.getMeta('prehook_num', 0)
    trace.setMeta('prehook_num', cur + 1)


def posthook(event, trace, saved_ret_addr, saved_args, callconv):
    trace.setMeta('posthookhit', True)
    cur = trace.getMeta('posthook_num', 0)
    trace.setMeta('posthook_num', cur+1)


def prehookThrow(event, trace, ret_addr, args, callconv):
    raise Exception('pre throw')


def posthookThrow(event, trace, saved_ret_addr, saved_args, callconv):
    raise Exception('post throw')


class HookBpTest(v_testmods.VtracePythonTest):
    '''
    Tests the direct implementation of the functionality.
    '''
    modname = 'vdb.testmods.hookbptest'

    def runTest(self):

        plat = self.trace.getMeta('Platform').lower()
        symname = plat_syms.get(plat)
        if symname is None:
            raise Exception('No symbol to test platform!')

        # if we're on 64bit, impapi won't have the sym so specify cc
        # and num args.  we should move this into another test. and specify
        # this as part of the def of plat_syms since we really want to test
        # with AND without impapi present.
        cc = None
        argc = None
        if '64' in self.trace.getMeta('Architecture'):
            cc = self.trace.getEmulator().getCallingConvention('msx64call')
            argc = 1

        bp = vtrace.breakpoints.HookBreakpoint(symname, callingconv=cc, argc=argc)
        bp.prehooks.append(prehook)
        bp.posthooks.append(posthook)
        self.trace.addBreakpoint(bp)

        self.trace.setMode('RunForever', True)
        self.trace.run()

        assert(self.trace.getMeta('ExitCode', 0) == 31)
        assert(self.trace.getMeta('prehookhit'))
        assert(self.trace.getMeta('posthookhit'))


class HookBpTest2(v_testmods.VtracePythonTest):
    '''
    Tests addHook works with both a prehook and posthook callback specified.
    '''
    modname = 'vdb.testmods.hookbptest'

    def runTest(self):

        plat = self.trace.getMeta('Platform').lower()
        symname = plat_syms.get(plat)
        if symname is None:
            raise Exception('No symbol to test platform!')

        # if we're on 64bit, impapi won't have the sym so specify cc
        # and num args.  we should move this into another test. and specify
        # this as part of the def of plat_syms since we really want to test
        # with AND without impapi present.
        cc = None
        argc = None
        if '64' in self.trace.getMeta('Architecture'):
            cc = self.trace.getEmulator().getCallingConvention('msx64call')
            argc = 1

        vtrace.breakpoints.addHook(self.trace, symname, prehook, posthook, cc=cc, argc=argc)

        self.trace.setMode('RunForever', True)
        self.trace.run()

        assert(self.trace.getMeta('ExitCode', 0) == 31)
        assert(self.trace.getMeta('prehookhit'))
        assert(self.trace.getMeta('posthookhit'))


class HookBpTest3(v_testmods.VtracePythonTest):
    '''
    Tests addHook works with only a prehook callback specified.
    '''
    modname = 'vdb.testmods.hookbptest'

    def runTest(self):

        plat = self.trace.getMeta('Platform').lower()
        symname = plat_syms.get(plat)
        if symname is None:
            raise Exception('No symbol to test platform!')

        # don't specify posthook
        vtrace.breakpoints.addHook(self.trace, symname, prehook)

        self.trace.setMode('RunForever', True)
        self.trace.run()

        assert(self.trace.getMeta('ExitCode', 0) == 31)
        assert(self.trace.getMeta('prehookhit'))


class HookBpTest4(v_testmods.VtracePythonTest):
    '''
    Tests addHook works even when a handler throws an exception (and the other
    handlers still execute)
    '''
    modname = 'vdb.testmods.hookbptest'

    def silentErrorHandler(self, cb_name, stre):
        '''
        default error handler in hookbp prints, we don't need to do that and
        makes the screen scroll.
        '''
        pass

    def runTest(self):

        vtrace.breakpoints.HookBreakpoint.defaultErrorHandler = self.silentErrorHandler
        plat = self.trace.getMeta('Platform').lower()
        symname = plat_syms.get(plat)
        if symname is None:
            raise Exception('No symbol to test platform!')

        vtrace.breakpoints.addHook(self.trace, symname, prehookThrow)
        vtrace.breakpoints.addHook(self.trace, symname, prehook)
        vtrace.breakpoints.addHook(self.trace, symname, posthookThrow)
        vtrace.breakpoints.addHook(self.trace, symname, posthook)

        self.trace.setMode('RunForever', True)
        self.trace.run()

        assert(self.trace.getMeta('ExitCode', 0) == 31)
        assert(self.trace.getMeta('prehookhit'))
        assert(self.trace.getMeta('posthookhit'))


class HookBpTest5(v_testmods.VtracePythonTest):
    modname = 'vdb.testmods.hookbptest'

    def runTest(self):

        plat = self.trace.getMeta('Platform').lower()
        symname = plat_syms.get(plat)
        if symname is None:
            raise Exception('No symbol to test platform!')

        vtrace.breakpoints.addHook(self.trace, symname, prehook)
        vtrace.breakpoints.addHook(self.trace, symname, prehook)
        vtrace.breakpoints.addHook(self.trace, symname, posthook)
        vtrace.breakpoints.addHook(self.trace, symname, posthook)

        self.trace.setMode('RunForever', True)
        self.trace.run()

        assert(self.trace.getMeta('ExitCode', 0) == 31)
        assert(self.trace.getMeta('prehook_num') > 2)
        assert(self.trace.getMeta('prehookhit'))
        assert(self.trace.getMeta('posthook_num') > 2)
        assert(self.trace.getMeta('posthookhit'))


class HookBpTest6(v_testmods.VtracePythonTest):
    '''
    Tests the failure of adding a pre bp at a location that already has another
    type of bp on it.
    '''
    modname = 'vdb.testmods.hookbptest'

    def runTest(self):

        plat = self.trace.getMeta('Platform').lower()
        symname = plat_syms.get(plat)
        if symname is None:
            raise Exception('No symbol to test platform!')

        # add a normal bp
        self.trace.addBreakByExpr(symname)

        # try to add some special breaks
        hitexception = False
        try:
            vtrace.breakpoints.addHook(self.trace, symname, prehook)
        except Exception as e:
            # if it's not the right exception, fail the test.
            # TODO: use our own exception type? :)
            assert('cannot add this hook, non-HookBreakpoint' in str(e))
            hitexception = True

        self.trace.setMode('RunForever', True)
        self.trace.run()

        assert(self.trace.getMeta('ExitCode', 0) == 31)
        assert(hitexception is True)

# TODO: add test for going through a function multiple times
# ensure the correct # of hook breakpoints are created.

# TODO: add test for a breakpoint type that already exists at the
# post hook breakpoint location

# TODO: I don't think these are run....


if __name__ == '__main__':
    import sys
    sys.exit(31)  # TODO: tests for something NOT in impapi
