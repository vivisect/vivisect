# Vivisect / Vdb / Vtrace

A combined disassembler/static analysis/symbolic execution/debugger
framework. More documentation is in the works :)

## Vdb

As in previous releases, the command ```python -m vdb.vdbbin``` from the
checkout directory will drop you into a debugger prompt on supported
platforms. ( Windows / Linux / FreeBSD / OSX... kinda? )

Commands in vdb grow/refine quickly, so use in-line help such as:

> vdb> help

or...

> vdb> help writemem

to show available commands and options.

## Vivisect

Fairly un-documented static analysis / emulation / symbolik analysis
framework for PE/Elf/Mach-O/Blob binary formats on various architectures.
To start with, you probably want to run a "bulk analysis" pass on a binary
using:

```
python3 -m vivisect.vivbin -B <binaryfile>
```

which will leave you with <binaryfile>.viv

Then run:

```
python3 -m vivisect.vivbin <binaryfile>.viv
```

to open the GUI and begin reverse engineering. Or, if you're impatient,
you can just run:

```
python3 -m vivisect.vivbin <binaryfile>
```

to do both simultaneously. You will have to hit <Ctrl-S> to manually save
the workspace file though.

As with most vtoys, the ui relies fairly heavily on right-click context menus
and various memory views.

For the binary ninjas, all APIs used during automatic analysis (and several
that aren't) are directly accessible for use writing your own custom
research tools. The interface should be nearly the same when dealing with
a real process (via vdb/vtrace) and dealing with an emulator / viv workspace.

## Installing

Unlike previous releases, version v1.x.x and up of vivisect/vdb should be entirely
pip installable, so just running `pip install vivisect` should get you the latest
release and all of the baseline dependencies in order to run vivisect in a headless
mode.

However, should you also desire a GUI, you can run `pip install vivisect[gui]` to
also install the pyqt5 based gui dependencies.

For convenience, setup.py for vivisect installs the main user facing scripts of
vivbin and vdbbin to the local path, so instead of having to run:

```
python3 -m vivisect.vivbin <binaryfile>
python3 -m vdb.vdbbin
```

You should just be able to run

```
vivbin -B <binaryfile>
vdbbin
```

and have things work as normal.

## Versioning

All releases prior to v1.0.0 are python2 only. As of v1.0.0, vivisect/vdb/vstruct
are all python3 compatible. Please report any bugs/issues to the [issue tracker](https://github.com/vivisect/vivisect/issues)
or hit us up in the #vivisect room in the [synapse slack](http://slackinvite.vertex.link/)

Please see v0.x.x-support branch for the current python2 version, or pip install
the v.0.2.x version of vivisect.

## Upgrading

Due to fun pickle shenanigans, old python2 vivisect workspaces are not typically
compatible with python3. In what will be one of (if not, the) final release of the
python2 compatible vivisect, v0.2.1 will include a conversion script that can migrate
the basicfile-based vivisect workspaces files to the msgpack-back ones, which should
be loadable in python3 vivisect.

## Build Status

[![CircleCI](https://circleci.com/gh/vivisect/vivisect/tree/master.svg?style=svg)](https://circleci.com/gh/vivisect/vivisect/tree/master)
[![Build Status](https://travis-ci.org/vivisect/vivisect.svg?branch=master)](https://travis-ci.org/vivisect/vivisect)

## Extending Vivisect / Vdb

Vivisect allows you to extend it's functionality through the use of Vivisect 
Extensions.  Extensions are loaded with the GUI, and they give nearly complete
access to the entire Vivisect Workspace and GUI.

Extensions are Python modules loaded from directories contained in the 
`VIV_EXT_PATH` environment variable.  Like DOS or Unix paths, this is a set
of directories separated by the OS-specific separator (Windows=';', Unix=':').

Like all Python modules, they can be either a `<modulename>.py` file or a 
directory with a `__init__.py` file inside it.  Each module will be loaded into
the namespace and the `vivExtension(vw, vwgui)` function executed (for Vdb, the
`vdbExtension(vdb, vdbgui)` function will be executed).  It is up to the module
to make any modifications (adding menu entries or toolbars, hooking the context
menu, etc) within this function.  Submodules may be included in the directory-
version of the extensions, and may be accessed with `from . import <blah>`.

In addition to your private zero-day finding extensions, outside plugins may
be wrapped into Vivisect by simply copying/symlinking them into one of your
extension directories (listed in the `VIV_EXT_PATH`).

If no `VIV_EXT_PATH` environment variable has been defined, Vivisect will
look for extensions in `$HOME/.viv/plugins/` if it exists.  If `VIV_EXT_PATH`
is defined, you much choose to add `$HOME/.viv/plugins/` to it or not.  It will
not be checked unless it is explicitly listed in `VIV_EXT_PATH`.

For examples of using this powerful capability, look at the example file at:
`vivisect/extensions/example_gui_extension.py`

## The Power of Scripts with Vivisect

You can script up menial tasks or powerful techniques using simple Python
scripts from either the command-line or the GUI.  

Scripts are loaded and run as any python code is run from the command line.  
The key diffenece is that Vivisect places a VivWorkspace object in the global
namespace with the name `vw`.  The GUI, if one exists (Vivisect can be run 
headless), can be accessed using `vw.getVivGui()`.  

From the CommandLine, analysis modules can be run in the following fashion:
`$ vivbin -M attackmodule.py targetbin.viv`
If your module makes any changes to the VivWorkspace, be sure it saves:
`vw.saveWorkspace()`

To run a script from the GUI, the command bar at the bottom of the screen is
used. Simply enter:
`script attackmodule.py <args>`
This method does not need to save to the workspace, as you can choose to do 
that through standard GUI methods (Ctrl-S or File->Save).
This method has the added benefit of being able to provide arguments, which
are placed in the namespace as `argv`.  
