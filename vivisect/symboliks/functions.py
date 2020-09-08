'''
'''
import inspect

import vstruct
import vivisect.symboliks

from vivisect.symboliks.common import *

class CallingConventionProxy:

    def __init__(self, cconv, argv, funcsym):
        self.argv = argv # viv style (type,name) tuple list
        self.cconv = cconv
        self.funcsym = funcsym

    def __call__(self, emu):

        # Get and update the symbolik args
        args = self.cconv.getSymbolikArgs(emu, self.argv)
        args = [ arg.update(emu) for arg in args ]

        # If callFunction returns something, snap it back in.
        # Otherwise, snap in a Call symbol.
        ret = self.callFunction(emu, *args)
        if ret is None:
            ret = Call(self.funcsym, emu.__width__, args)

        # Set the return value into the symbolik state
        self.cconv.setSymbolikReturn(emu, ret, self.argv)

    def getSymbolikArgs(self, emu):
        return self.cconv.getSymbolikArgs(emu, self.argv)

    def callFunction(emu, *args):
        # Each calling convention proxy must implement this to do
        # the actual call hook...
        return None


class ImportCallProxy(CallingConventionProxy):
    '''
    A calling convention proxy allows the definition of
    a pythonic function which may then be called by an emulator
    during symbolik effect processing.
    '''

    def __init__(self, func, cconv):

        # Do crazy introspection shit to make calling convention
        # map function args to names / vstruct types.
        aspec = inspect.getargspec(func)
        argn = aspec.args[1:]
        argt = aspec.defaults

        argv = [ (argt[i],argn[i]) for i in range(len(argn)) ]

        modlast = func.__module__.split('.')[-1]
        funcsym = Var('%s.%s' % (modlast, func.__name__))

        CallingConventionProxy.__init__(self, cconv, argv, funcsym)

        self.func = func

    def callFunction(self, emu, *args):
        return self.func(emu, *args)
