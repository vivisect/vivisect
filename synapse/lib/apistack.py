import functools
import traceback
import collections

HOOK_NONE   = 0     # hooks that just want to watch (HOOK_NONE,None) or None
HOOK_RET    = 1     # hooks that want to answer the call (HOOK_RET,retval)
HOOK_CALL   = 2     # hooks that want to change call args (HOOK_CALL,(args,kwargs))

def stackable(f):
    f.canstack = True

    @functools.wraps(f)
    def stackcaller(self, *args, **kwargs):
        for apihook in self.apihooks.get( f.__name__ ):
            try:
                ret = apihook(self, *args, **kwargs)
                if ret == None:
                    continue

                hook,hookval = ret
                if hook == HOOK_RET:
                    return hookval

                if hook == HOOK_CALL:
                    args,kwargs = hookval

            except Exception as e:
                traceback.print_exc()

        return f(self, *args, **kwargs)

    return stackcaller

class NoSuchApi(Exception):pass
class ApiCantStack(Exception):pass

class ApiStack:
    '''
    Implements a "driver stack" style API stacking mechanism.

    Each API in the stack (in order) has an opportunity to 
    '''
    def __init__(self):
        self.apihooks = collections.defaultdict(list)

    def addApiHook(self, name, callback, idx=-1):
        '''
        Add an api hook to a stackable method.
        Example:
            def callback(apiobj, *args, **kwargs):
                print('hehe')

            o.addApiHook('doSomeWoot',callback)

        To modify the call or return value, an API hook may return
        a tuple of (hook_code,hook_val)

        NOTE:
            the callback syntax is callback(<obj>,*args,**kwargs)
            to allow hooks to get a copy of which object is being called.
        '''
        meth = getattr(self,name,None)
        if meth == None:
            raise NoSuchApi(name)
        if not getattr(meth,'canstack',False):
            raise ApiCantStack(name)
        self.apihooks[name].insert(idx,callback)

    def addApiHooks(self, obj, idx=-1):
        '''
        Add API hooks for each hookable API which is implemented by obj.
        '''
        # FIXME

def hookcall(*args,**kwargs):
    '''
    Helper function to construct a HOOK_CALL return
    '''
    return (HOOK_CALL,(args,kwargs))

def hookret(ret):
    '''
    Helper function to construct a HOOK_RET return
    '''
    return (HOOK_RET,ret)
