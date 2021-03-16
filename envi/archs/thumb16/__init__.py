from envi.archs.arm import *

from . import disasm as th_disasm


class Thumb16Module(ThumbModule):
    def __init__(self):
        ThumbModule.__init__(self, name='thumb16')
