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
release and all the dependencies.

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
