'''
vivisect.debug allows portable, remote, extensible debugging of
target processes and devices.  for old skewl folks, this is the
home of the new vtrace/vdb.

- Architecture

The vivisect debug architecture is implemented in several layers
of abstraction to allow for portability and remote debugging.

** Debugger - The top of the vivisect.debug stack.  The Debugger
              allows developers to enumerate the debug target, call
              platform specific extensions, and instantiate traces.

** Trace    - Similar to vtrace.Trace, a vivisect Trace implements the
              debug functions associated with one process or target device.

** DebugTarget  - The DebugTarget layer is the layer which implements the
                  portions of the API which must actually be executed on the
                  target system.  Trace and DebugApi functions ultimately call
                  a DebugTarget instance ( either locally, or remotely ) which
                  can only be instantiated on the target platform.

'''
