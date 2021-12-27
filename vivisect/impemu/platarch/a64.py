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
    pass
