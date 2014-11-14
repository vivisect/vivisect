
"""
The analysis package.  Modules in this directory are responsible
for different phases of analysis on different platforms.
"""


def addAnalysisModules(vw):

    import vivisect.analysis.i386 as viv_analysis_i386

    arch = vw.getMeta('Architecture')
    fmt  = vw.getMeta('Format')
    plat = vw.getMeta('Platform')

    if fmt == 'pe':

        vw.addAnalysisModule("vivisect.analysis.pe")

        if arch == 'i386':

            vw.addImpApi('windows','i386')

            viv_analysis_i386.addEntrySigs(vw)
            vw.addStructureModule('win32', 'vstruct.defs.win32')
            vw.addStructureModule('ntdll', 'vstruct.defs.windows.win_5_1_i386.ntdll')

        elif arch == 'amd64':

            vw.addImpApi('windows','amd64')
            vw.addStructureModule('ntdll', 'vstruct.defs.windows.win_6_1_amd64.ntdll')

        vw.addConstModule('vstruct.constants.ntstatus')

        vw.addAnalysisModule("vivisect.analysis.generic.pointers")
        vw.addAnalysisModule("vivisect.analysis.generic.relocations")
        vw.addAnalysisModule("vivisect.analysis.generic.pointers")
        vw.addAnalysisModule("vivisect.analysis.generic.pointertables")

        vw.addAnalysisModule("vivisect.analysis.ms.vftables") # RELIES ON LOC_POINTER
        vw.addAnalysisModule("vivisect.analysis.generic.emucode") # RELIES ON LOC_POINTER
        # run imports after emucode
        if arch == 'i386':
            vw.addAnalysisModule("vivisect.analysis.i386.importcalls")

        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")
        vw.addFuncAnalysisModule("vivisect.analysis.ms.hotpatch")
        vw.addFuncAnalysisModule("vivisect.analysis.ms.msvc")

        # Snap in an architecture specific emulation pass
        if arch == 'i386':
            vw.addFuncAnalysisModule("vivisect.analysis.i386.calling")

        elif arch == 'amd64':
            vw.addFuncAnalysisModule("vivisect.analysis.amd64.emulation")

        # See if we got lucky and got arg/local hints from symbols
        vw.addAnalysisModule('vivisect.analysis.ms.localhints')
        # Find import thunks
        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")
        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule('vivisect.analysis.ms.msvcfunc')
        vw.addAnalysisModule("vivisect.analysis.generic.mkpointers")

    elif fmt == 'elf': # ELF ########################################################

        vw.addAnalysisModule("vivisect.analysis.elf")

        if arch == 'i386':
            viv_analysis_i386.addEntrySigs(vw)
            vw.addAnalysisModule("vivisect.analysis.i386.importcalls")

        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule("vivisect.analysis.generic.relocations")
        vw.addAnalysisModule("vivisect.analysis.generic.pointertables")
        vw.addAnalysisModule("vivisect.analysis.generic.emucode")

        # Get PLTs taken care of early
        vw.addFuncAnalysisModule("vivisect.analysis.elf.elfplt")
        # Generic code block analysis
        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")

        # Add our emulation modules
        if arch == 'i386':
            vw.addFuncAnalysisModule("vivisect.analysis.i386.calling")
        elif arch == 'amd64':
            vw.addFuncAnalysisModule("vivisect.analysis.amd64.emulation")

        # Find import thunks
        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")
        vw.addAnalysisModule("vivisect.analysis.generic.pointers")

    elif fmt == 'macho': # MACH-O ###################################################

        if arch == 'i386':
            viv_analysis_i386.addEntrySigs(vw)
            vw.addAnalysisModule("vivisect.analysis.i386.importcalls")

        # Add the one that brute force finds function entry signatures
        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule("vivisect.analysis.generic.relocations")
        vw.addAnalysisModule("vivisect.analysis.generic.pointertables")
        vw.addAnalysisModule("vivisect.analysis.generic.emucode")

        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")

        if arch == 'i386':
            vw.addFuncAnalysisModule("vivisect.analysis.i386.calling")

        elif arch == 'amd64':
            vw.addFuncAnalysisModule("vivisect.analysis.amd64.emulation")

        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")
        vw.addAnalysisModule("vivisect.analysis.generic.pointers")

    elif fmt == 'blob': # BLOB ######################################################

        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule("vivisect.analysis.generic.relocations")
        vw.addAnalysisModule("vivisect.analysis.generic.pointertables")
        vw.addAnalysisModule("vivisect.analysis.generic.emucode")

        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")

    elif fmt == 'ihex': # BLOB ######################################################

        vw.addAnalysisModule("vivisect.analysis.generic.funcentries")
        vw.addAnalysisModule("vivisect.analysis.generic.relocations")
        #vw.addAnalysisModule("vivisect.analysis.generic.pointertables")
        vw.addAnalysisModule("vivisect.analysis.generic.emucode")

        vw.addFuncAnalysisModule("vivisect.analysis.generic.codeblocks")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.impapi")
        vw.addFuncAnalysisModule("vivisect.analysis.generic.thunks")

    else:

        raise Exception('Analysis modules unknown for format: %s' % fmt)

