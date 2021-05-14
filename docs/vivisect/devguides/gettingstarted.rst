.. _parsing:

Getting Started
###############

Parsing a binary
================

Like any good reverse engineering platform, vivisect/vdb supports both the PE and ELF file formats. If you're only interested in parsing the binary file format, and not any of the auto-analysis, you can just pop parse the binary using the PE or Elf modules that vivisect brings along::

    import PE
    pe = PE.peFromFileName("/path/to/my/pe.exe")

Similarly for Elf files::

    import Elf
    elf = Elf.elfFromFileName("/path/to/nix/exe.elf")

Creating a Workspace
====================

If you want a fully populated workspace, you can run::

    import vivisect
    vw = vivisect.VivWorkspace()
    vw.loadFromFile("/path/to/a/binary/or/viv/file")
    vw.analyze()

Once the call to `analyze()` returns, auto-analysis has finished, and the `vw` variable is fully populated with the knowledge of function boundaries, locations of interest, binary structures, etc.

If you've already read a file into memory, you can instead use the `loadFromFd` method on the workspace variable::

    import vivisect
    with open("/path/to/my/binary/file", 'rb') as fd:
        vw = vivisect.VivWorkspace()
        vw.loadFromFd(fd)
        vw.analyze()

Loading a Binary
================

If you've already loaded and parsed a binary into a PE or Elf object provided by vivisect's parser modules, then all you should need to do to get it into a proper workspace is::

    import vivisect
    vw = vivisect.VivWorkspace()
    vw.loadParsedBin(binary_object)
    vw.analyze()

where `binary_object` is your PE or Elf class object.
