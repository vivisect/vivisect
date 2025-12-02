import logging

import envi
import envi.exc as e_exc
import envi.archs.aarch64.emu as e_aarch64
from envi.archs.aarch64.regs import *

import vivisect.exc as v_exc
import vivisect.impemu.emulator as v_i_emulator

import visgraph.pathcore as vg_path

logger = logging.getLogger(__name__)


class A64WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_aarch64.A64Emulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_aarch64.A64Emulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)
        self.setMemArchitecture(envi.ARCH_A64)

