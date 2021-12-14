STYPE_NONE = 0
STYPE_IPYTHON = 1
STYPE_IPYTHON_NEW = 2
STYPE_CODE_INTERACT = 3


class DummyNamespace:
    __spec__ = None
    __name__ = "Dummy"


def dbg_interact(lcls, gbls):
    intro = "Let's interact!"
    shelltype = STYPE_NONE

    try:
        from IPython import embed
        # Using IPython.embed() allows ipython to load the user's normal 
        # configuration file.  But the global namespace is not expected to be a 
        # dictionary so we have to do some silly things to make this work
        # namespace
        global_ns = DummyNamespace()
        global_ns.__dict__ = gbls

        # because we are calling embed() instead of creating a shell that we 
        # call the interact() function of later we have to set custom 
        # configuration values no
        config = {
            'autocall': 2,
        }

        print(intro)
        shelltype = STYPE_IPYTHON_NEW

    except ImportError as e:
        try:
            import IPython.Shell
            ipsh = IPython.Shell.IPShell(argv=[''], user_ns=lcls, user_global_ns=gbls)
            print(intro)
            shelltype = STYPE_IPYTHON

        except ImportError as e:
            try:
                from IPython.terminal.interactiveshell import TerminalInteractiveShell
                ipsh = TerminalInteractiveShell()
                ipsh.user_global_ns.update(gbls)
                ipsh.user_global_ns.update(lcls)
                ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!
                shelltype = STYPE_IPYTHON
                print(intro)

            except ImportError as e:
                try:
                    from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell
                    ipsh = TerminalInteractiveShell()
                    ipsh.user_global_ns.update(gbls)
                    ipsh.user_global_ns.update(lcls)
                    ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!
                    shelltype = STYPE_IPYTHON

                    print(intro)
                except ImportError as e:
                    print(e)
                    shell = code.InteractiveConsole(gbls)
                    shelltype = STYPE_IPYTHON
                    print(intro)

    if shelltype == STYPE_IPYTHON_NEW:
        embed(using='', user_module=global_ns, user_ns=lcls, **config)

    elif shelltype == STYPE_IPYTHON:
        ipsh.mainloop()

    elif shelltype == STYPE_CODE_INTERACT:
        shell.interact()

    else:
        print("SORRY, NO INTERACTIVE OPTIONS AVAILABLE!!  wtfo?")

