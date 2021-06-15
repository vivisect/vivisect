.. _workspaces:

Workspaces
##########

A VivWorkspace object is the beating heart of all the analysis vivisect does. It contains the results of all the analysis modules, function boundaries, memory maps, pointers, codeblocks, and any other metadata of interest. Read the getting started guide :ref:`gettingstarted` on a quick way to populate a workspace.


Locations
=========

Locations are the generalized "points of interests" inside of a binary. These POIs can be anything from an ascii string, to an assembly instruction, import location, or just some padding bytes.

In vivisect, locations are represented as a tuple consisting of four elements. The first element is the virtual address the location of interest starts at, the second the size (in bytes) that the location spans, the third element is the location type (represented as an integer from vivisect/const.py), and a fourth info field that is type-specific information.

The most common calls concerning locations are the adder and getters::

    import vivisect.const as v_const
    va = 0x1234
    size = 5
    ltyp = v_const.LOC_OP
    tinfo = None
    vw.addLocation(va, size, ltyp, tinfo=tinf)

    loctup = vw.getLocation(va)
    assert loctup == (va, size, ltyp, tinfo)

Where `vw` is our standard variable name for our VivWorkspace instance that has been loaded with either a pre-existing workspace or a binary that was parsed and loaded in.

There are other utility functions for locations such as::

    import vivisect.const as v_const
    vw.isLocation(0x401000)
    vw.isLocType(0x401000, v_const.LOC_IMPORT)

As well as::

    for ltup in vw.getLocationRange(0x802000, 0xff):
        va, size, ltyp, tinfo = ltup
        print(va)

    prev = vw.getPrevLocation(va)

Cross References
================

When one location in a binary references another (such as when a pointer dereference is made), vivisect not only adds locations for both of them, but also as a connector tuple linking the two locations. Xrefs in vivisect are represented as tuple of four elelments. The first element in the tuple is the virtual address of the location that is doing the referring (the referer), the second element is the virtual address of the location that is being referred to (the referee), the third element is an integer representing the type of cross reference the current reference is (see vivisect/const.py), and the fourth element is a set of flags representing more information about the cross reference.

To retrieve all of the cross references in the workspace::

    vw.getXrefs()

Which also takes an optional type paramter if you're only interested in certain types of cross references::

    import vivisect.const as v_const
    vw.getXrefs(rtype=v_const.REF_CODE)

Be warned as most binaries contain a non-trivial amount of cross references, so printing them out might not be recommended.

To get all the cross references from a particular virtual address::

    vw.getXrefsFrom(0x12345678)

which also takes an optional rtype parameter::

    import vivisect.const as v_const
    vw.getXrefsFrom(0x12345678, rtype=v_const.REF_PTR)

And to get all the cross references to a particular virtual address::

    vw.getXrefsTo(0x12345678)
    
which, like the others, also takes an optional rtype parameter::

    import vivisect.const as v_const
    vw.getXrefsTo(0x12345678, rtype=v_const.REF_DATA)

and if you want to make your own cross reference::

    import vivisect.const as v_const
    referer = 0x401abcd
    referee = 0x4021234
    vw.addXref(referrer, referee, v_const.REF_CODE, rflags=0)

VA Sets
=======

While locations tend to very general (most binaries have some concept of an import mechanism/opcodes/pointers/etc), there are other groupings of virtual addresses that are more platform/architecture/format specific that deserve their own callouts. Features like a PE file's Delayed Imports, or an Elf file's usage of thunk registers, all deserve to be called out, but either don't quite fit into the location model, or are already there, and the VA set serves as a secondary information storage.

VA sets are effectively a dictionary of typed lists. You can retrieve the list of currently defined VA sets from a
workspace instance via::
    
    vw.getVaSetNames()

and retrieve all the values stored in a particular VA set via::

    vw.getVaSetRows('pe:ordinals')

Alternatively, if you're already examining a virtual address, you can check if it's in a particular VA set via::

    vw.getVaSetRow('EntryPoints', 0x401000)

and if you want to add to a particular VA set::

    vw.setVaSetRow('EntryPoints', (0x1234,))

By convention, the first value in the tuple passed to setVaSetRow is an integer (or some other virtual address), but technically there's nothing stopping you from using any other type of dictionary key.
