import envi
import envi.archs.ppc as e_ppc
import vivisect.impemu.emulator as v_i_emulator


import logging
logger = logging.getLogger(__name__)


class PpcWorkspaceEmulator(v_i_emulator.WorkspaceEmulator):

    taintregs = [x for x in range(13)] + [e_ppc.REG_LR]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)

        # If there is a PpcVleMaps Meta defined, update the emulator now.
        # This has to be checked here because the workspace emulators are
        # created after the metadata events are parsed
        maps = vw.getMeta('PpcVleMaps')
        if maps is not None:
            self.setVleMaps(maps)


class Ppc64EmbeddedWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc64EmbeddedEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc64EmbeddedEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)


class Ppc32EmbeddedWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc32EmbeddedEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc32EmbeddedEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)


class PpcVleWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.PpcVleEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.PpcVleEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)


class Ppc64ServerWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc64ServerEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc64ServerEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)


class Ppc32ServerWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc32ServerEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc32ServerEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)
