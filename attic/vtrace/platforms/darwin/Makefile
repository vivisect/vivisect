SRCS=machhelper.c excServer.c excUser.c
DYLIB=machhelper.dylib

# mig /usr/include/mach/exc.defs
# edit all catch_exception_* references to vtrace_catch_exception_*
# then our exc_server doesn't try to locate those functions in the
# main exe.... #fuckingwinning

all:
	gcc -dynamiclib -arch i386 -arch x86_64 ${SRCS} -o ${DYLIB}

clean:
	rm -rf ${DYLIB}
