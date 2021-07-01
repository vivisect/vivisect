# Vivisect / Vdb / Vtrace

A combined disassembler/static analysis/symbolic execution/debugger framework.

## Usage

Please see the quickstart/usage docs over at our [docs page](https://vivisect.readthedocs.io/en/latest/)

## Installing

For most use cases, you should just be able to run `pip install vivisect[gui]` to get both the vivisect/vdb libraries and UI components. For other use cases, please see our [documentation](https://vivisect.readthedocs.io/en/latest/).


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
