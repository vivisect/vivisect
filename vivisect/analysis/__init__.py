
"""
The analysis package.  Modules in this directory are responsible
for different phases of analysis on different platforms.
"""

import logging
logger = logging.getLogger(__name__)

ARM_ARCHS = ('arm', 'thumb', 'thumb16')


def addAnalysisModules(vw):

    import vivisect
    import vivisect.analysis.i386 as viv_analysis_i386

    arch = vw.getMeta('Architecture')
    fmt = vw.getMeta('Format')

    if fmt == 'pe':

        vw.addAnalysisModule("vivisect.analysis.generic.entrypoints")
        vw.addAnalysisModule("vivisect.analysis.pe")

        if arch == 'i386':

            vw.addImpApi('windows', 'i386')
            vw.addImpApi('winkern', 'i386')

            viv_analysis_i386.addEntrySigs(vw)
            vw.addStructureModule('win32', 'vstruct.defs.win32')
            vw.addStructureModule('ntdll', 'vstruct.defs.windows.win_5_1_i386.ntdll')

        elif arch == 'amd64':

            vw.addImpApi('windows', 'amd64')
            vw.addImpApi('winkern', 'amd64')
            vw.addStructureModule('ntdll', 'vstruct.defs.windows.win_6_1_amd64.ntdll')

        elif arch in ARM_ARCHS:
            vw.addImpApi('windows','arm')
            vw.addFuncAnalysisModule('vivisect.analysis.arm.renaming')

        vw.addConstModule('vstruct.constants.ntstatus')

        vw.addAnalysisModule("vivisect.analysis.generic.relocations")

        vw.addAnalysisModule("vivisect.analysis.ms.vftables")  # RELIES ON LOC_POINTER
        vw.addAnalysisModule("vivisect.analysis.generic.emucode")  # RELIES ON LOC_POINTER

        # run imports after emucode
        if arch == 'i386':
            vw.addAnalysisModule("vivisect.analysis.i386.importcalls")
            vw.addAnalysisModule("vivisect.analysis.i386.golang")
        elif arch == 'amd64':
            vw.addAnalysisModule("vivisect.analysis.amd64.golang")

        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")
        vw.addFuncAnalysisModule("vivisect.analysis.ms.hotpatch")
        vw.addFuncAnalysisModule("vivisect.analysis.ms.msvc")

        if arch in ('i386', 'amd64'):
            # Applies to i386 and amd64, will split it up when neccessary
            vw.addFuncAnalysisModule("vivisect.analysis.i386.instrhook")

        # Snap in an architecture specific emulation pass
        if arch == 'i386':
            vw.addFuncAnalysisModule("vivisect.analysis.i386.calling")

        elif arch == 'amd64':
            vw.addFuncAnalysisModule("vivisect.analysis.amd64.emulation")

        elif arch in ARM_ARCHS:
            vw.addFuncAnalysisModule("vivisect.analysis.arm.emulation")

        # See if we got lucky and got arg/local hints from symbols
        vw.addAnalysisModule('vivisect.analysis.ms.localhints')
        # Find import thunks
        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.noret")
        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule('vivisect.analysis.ms.msvcfunc')
        vw.addAnalysisModule("vivisect.analysis.generic.thunks")

        vw.addAnalysisModule('vivisect.analysis.generic.strconst')

    elif fmt == 'elf':  # ELF ########################################################

        # elfplt wants to be run before generic.entrypoints.
        vw.addAnalysisModule("vivisect.analysis.elf.elfplt")
        vw.addAnalysisModule("vivisect.analysis.generic.entrypoints")
        vw.addAnalysisModule("vivisect.analysis.elf")

        if arch in ('i386', 'amd64', 'arm'):
            vw.addImpApi('posix', arch)

        if arch == 'i386':
            viv_analysis_i386.addEntrySigs(vw)
            vw.addAnalysisModule("vivisect.analysis.i386.importcalls")
            # add va set for tracking thunk_bx function(s)
            vw.addVaSet('thunk_bx', ( ('fva', vivisect.VASET_ADDRESS), ) )
            vw.addFuncAnalysisModule("vivisect.analysis.i386.thunk_bx")
        elif arch in ARM_ARCHS:
            vw.addVaSet('thunk_reg', ( ('fva', vivisect.VASET_ADDRESS), ('reg', vivisect.VASET_INTEGER), ))
            vw.addFuncAnalysisModule('vivisect.analysis.arm.thunk_reg')
            vw.addFuncAnalysisModule('vivisect.analysis.arm.renaming')

        vw.addAnalysisModule("vivisect.analysis.generic.relocations")
        vw.addAnalysisModule("vivisect.analysis.elf.libc_start_main")
        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule("vivisect.analysis.generic.emucode")
        vw.addAnalysisModule("vivisect.analysis.generic.pointertables")

        # Generic code block analysis
        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")

        if arch in ('i386', 'amd64'):
            # Applies to i386 and amd64, will split it up when neccessary
            vw.addFuncAnalysisModule("vivisect.analysis.i386.instrhook")

        # Add our emulation modules
        if arch == 'i386':
            vw.addFuncAnalysisModule("vivisect.analysis.i386.calling")

        elif arch == 'amd64':
            vw.addFuncAnalysisModule("vivisect.analysis.amd64.emulation")

        elif arch in ARM_ARCHS:
            vw.addFuncAnalysisModule("vivisect.analysis.arm.emulation")

        # Find import thunks
        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.noret")
        # due to inconsistencies in plt layouts, we'll keep this as a func module as well
        vw.addFuncAnalysisModule("vivisect.analysis.elf.elfplt")
        # late-analysis ELF PLT tidying up, allowing unused PLT entries to be made into functions
        vw.addAnalysisModule("vivisect.analysis.elf.elfplt_late")
        vw.addAnalysisModule("vivisect.analysis.generic.thunks")
        vw.addAnalysisModule("vivisect.analysis.generic.pointers")

    elif fmt == 'macho': # MACH-O ###################################################

        vw.addAnalysisModule("vivisect.analysis.generic.entrypoints")
        if arch == 'i386':
            viv_analysis_i386.addEntrySigs(vw)
            vw.addAnalysisModule("vivisect.analysis.i386.importcalls")

        # Add the one that brute force finds function entry signatures
        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule("vivisect.analysis.generic.relocations")
        vw.addAnalysisModule("vivisect.analysis.generic.emucode")
        vw.addAnalysisModule("vivisect.analysis.generic.pointertables")

        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")

        if arch == 'i386':
            vw.addFuncAnalysisModule("vivisect.analysis.i386.calling")

        elif arch == 'amd64':
            vw.addFuncAnalysisModule("vivisect.analysis.amd64.emulation")

        elif arch in ARM_ARCHS:
            vw.addFuncAnalysisModule("vivisect.analysis.arm.emulation")
            vw.addFuncAnalysisModule('vivisect.analysis.arm.renaming')

        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")
        vw.addAnalysisModule("vivisect.analysis.generic.pointers")

    elif fmt == 'blob': # BLOB ######################################################

        vw.addAnalysisModule("vivisect.analysis.generic.entrypoints")
        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule("vivisect.analysis.generic.relocations")
        #vw.addAnalysisModule("vivisect.analysis.generic.pointertables")
        vw.addAnalysisModule("vivisect.analysis.generic.emucode")

        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")

        if arch in ARM_ARCHS:
            vw.addFuncAnalysisModule("vivisect.analysis.arm.emulation")
            vw.addFuncAnalysisModule('vivisect.analysis.arm.renaming')

        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")

    elif fmt in ('ihex', 'srec'): # Intel HEX  or SRECORD (similar) #################

        vw.addAnalysisModule("vivisect.analysis.generic.entrypoints")
        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule("vivisect.analysis.generic.relocations")
        #vw.addAnalysisModule("vivisect.analysis.generic.pointertables")
        vw.addAnalysisModule("vivisect.analysis.generic.emucode")

        if arch in ARM_ARCHS:
            vw.addFuncAnalysisModule("vivisect.analysis.arm.emulation")
            vw.addFuncAnalysisModule('vivisect.analysis.arm.renaming')

        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")

    else:

        raise Exception('Analysis modules unknown for format: %s' % fmt)

    logger.info('Vivisect Analysis Setup Hooks Complete')
