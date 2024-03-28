import sys
import struct
import traceback

import vdb.testmods
import vdb.testmods.hookbptest as v_t_hookbptest
import vdb.testmods.callingconventions as v_t_callingconventions

tests = [
]

tests32 = [
    v_t_callingconventions.i386StdCallCallingConventionTest(0),
    v_t_callingconventions.i386CdeclCallingConventionTest(0),
    v_t_callingconventions.i386ThisCallCallingConventionTest(0),
    v_t_callingconventions.i386MsFastCallCallingConventionTest(0),
    v_t_callingconventions.i386BFastCallCallingConventionTest(0),

    v_t_callingconventions.i386StdCallCallingConventionTest(1),
    v_t_callingconventions.i386CdeclCallingConventionTest(1),
    v_t_callingconventions.i386ThisCallCallingConventionTest(1),
    v_t_callingconventions.i386MsFastCallCallingConventionTest(1),
    v_t_callingconventions.i386BFastCallCallingConventionTest(1),

    v_t_callingconventions.i386StdCallCallingConventionTest(3),
    v_t_callingconventions.i386CdeclCallingConventionTest(3),
    v_t_callingconventions.i386ThisCallCallingConventionTest(3),
    v_t_callingconventions.i386MsFastCallCallingConventionTest(3),
    v_t_callingconventions.i386BFastCallCallingConventionTest(3),

    v_t_callingconventions.i386StdCallCallingConventionTest(10),
    v_t_callingconventions.i386CdeclCallingConventionTest(10),
    v_t_callingconventions.i386ThisCallCallingConventionTest(10),
    v_t_callingconventions.i386MsFastCallCallingConventionTest(10),
    v_t_callingconventions.i386BFastCallCallingConventionTest(10),
]

tests64 = [
    v_t_callingconventions.x64MSx64CallCallingConventionTest(0),
    v_t_callingconventions.x64MSx64CallCallingConventionTest(1),
    v_t_callingconventions.x64MSx64CallCallingConventionTest(3),
    v_t_callingconventions.x64MSx64CallCallingConventionTest(10),

    v_t_callingconventions.SysVAmd64CallCallingConventionTest(0),
    v_t_callingconventions.SysVAmd64CallCallingConventionTest(1),
    v_t_callingconventions.SysVAmd64CallCallingConventionTest(3),
    v_t_callingconventions.SysVAmd64CallCallingConventionTest(10),

    v_t_callingconventions.SysVAmd64SystemCallCallingConventionTest(0),
    v_t_callingconventions.SysVAmd64SystemCallCallingConventionTest(1),
    v_t_callingconventions.SysVAmd64SystemCallCallingConventionTest(3),
    v_t_callingconventions.SysVAmd64SystemCallCallingConventionTest(10),
]

windows = [
    v_t_hookbptest.HookBpTest(),
    v_t_hookbptest.HookBpTest2(),
    v_t_hookbptest.HookBpTest3(),
    v_t_hookbptest.HookBpTest4(),
    v_t_hookbptest.HookBpTest5(),
    v_t_hookbptest.HookBpTest6(),
]

def runTests(tests):

    for test in tests:
        testname = test.__class__.__name__
        try:
            stage = 'prep'
            test.prepTest()
            stage = 'run'
            test.runTest()
            stage = 'clean'
            test.cleanTest()
            print('Test Success: %s' % test.__class__.__name__)
        except vdb.testmods.SkipTest as e:
            print('Test Skipped: %s (in %s) %s' % (testname, stage, e))
        except Exception as e:
            traceback.print_exc()
            print('Test Failure: %s (in %s) %s' % (testname, stage, e))

def main():

    print('running bare minimum vtrace tests')
    runTests(tests)
    print('')
    print('running architecture specific tests')
    if struct.calcsize('P') == 4:
        runTests(tests32)
    elif struct.calcsize('P') == 8:
        runTests(tests64)
    else:
        raise Exception('unsupported bitness')
    print('')

    print('running platform specific tests')
    if 'win' in sys.platform.lower():
        runTests(windows)


if __name__ == '__main__':
    sys.exit(main())
