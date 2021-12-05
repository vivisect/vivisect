.. _gettingstarted:

Getting Started
###############

Vivisect has a rich environment for reverse-engineering / vulnerability research, and it was originally designed to remain quite modular.  For example, the ENVI subsystem (disassembly and rudimentary emulation) can exist without Vivisect proper (all the code in vivisect/).  Many other subsystems have been left modular as well, such as the individual file parsers (PE and Elf and Macho), Vstructs, and the Visgraph subsystems.  The core libraries which make up Vivisect are::

    * ENVI (envi/) - Core disassembly/emulation code

    * PE (PE/) - Generic PE parsing library
    
    * ELF (Elf/) - Generic Elf parsing library
    
    * Cobra (cobra/) - Networking abstraction library, including remote-code-pulling and clustering facilities
    
    * VQT (vqt/) - Core Vivisect QT windowing libraries (great for extending Vivisect or writing your own code)
    
    * VTrace (vtrace/) - Platform-agnostic low-level debugging/tracing library
    
    * VDB (vdb/) - Higher level Vulnerability Debugger code (depends on VTrace)
    
    * VStruct (vstruct/) - Easy-to-use Structure builder/manipulation library
    
    * VisGraph (visgraph/) - Graph and Path libraries used to represent virtually anything with nodes and edges with properties
    
    * Vivisect (vivisect/) - Rich multi-architecture, cross-platform binary analysis framework, depending on most of the other libraries

    * Symboliks (vivisect/symboliks/) - Symbolic analysis framework based on Vivisect


While there are many fully featured tools/libraries, most of the functionality is provided from the Vivisect Workspace (vivisect.VivWorkspace).  Unless you only want to use a particular library mentioned above, most exploration is best done there.

Because so much of Vivisect's power is in its flexibility, sometimes the options can seem confusing at first.  For instance, Vivisect can load from a binary file (a PE, Elf, IHEX, SREC, or blob), it can load from a File Descriptor (say, you already have the file open), or can be loaded from a Memory Object.  So don't be intimidated that the following three examples all load a VivWorkspace differently.  All are valid, but you'll get to use the one that suits your needs best.  


Parsing a binary
================

Like any good reverse engineering platform, vivisect/vdb supports both the PE and ELF file formats. If you're only interested in parsing the binary file format, and not any of the auto-analysis/disassembly/emulation you get with a VivWorkspace, you can just parse the binary using the PE or Elf modules included with Vivisect::

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

Loading a Binary From Its Parser
================================

If you've already loaded and parsed a binary into a PE or Elf object provided by vivisect's parser modules, then all you should need to do to get it into a proper workspace is::

    # First we end up loading a binary
    import Elf
    binary_object = Elf.Elf(open("/path/to/binary", "rb"))

    # Now we create a VivWorkspace and load in the binary
    import vivisect
    vw = vivisect.VivWorkspace()
    vw.loadParsedBin(binary_object)
    vw.analyze()

where `binary_object` is your PE or Elf class object.


My Comfort-Zone
===============

When I'm writing tools, my most common path to getting spun up looks like this::

    # Loading a binary file (not a saved workspace)
    import vivisect
    vw = vivisect.VivWorkspace()
    vw.loadFromFile('/path/to/file.bin')

    # If what I'm doing requires analysis (most things)
    vw.analyze()


    # Alternately: Loading a saved VivWorkspace
    import vivisect
    vw = vivisect.VivWorkspace()
    vw.loadWorkspace('/path/to/file.viv')


Changing Configuration Items
============================
Sometimes when working with a workspace, you may wish to programmatically change configuration options (much like the command line option `-O` as in `vivbin -O viv.parsers.srec.arch=arm`.  Changing the configuration is typically desirable before loading any files into the workspace, as the parsers often make use of the configuration more than anything other subsystem.

First create a workspace::

    import vivisect
    vw = vivisect.VivWorkspace()

Next you can interact with the workspace's config module::

    In [11]: vw.config                                                                                                                 
    Out[11]: <envi.config.EnviConfig at 0x7fe9d167ceb0>

    In [12]: print(vw.config.reprConfigPaths())                                                                                        
    Valid Config Entries:
        remote.server = 10.42.120.72
        vdb.BreakOnEntry = False
        vdb.BreakOnMain = False
        vdb.SymbolCacheActive = True
        ...
        viv.parsers.srec.arch = rxv2
        viv.parsers.srec.offset = 192
        ...

    In [13]: vw.config.viv.parsers.srec.arch                                                                                           
    Out[13]: 'rxv2'

    In [14]: vw.config.viv.parsers.srec.arch = 'msp430'
    
    In [15]: vw.config.viv.parsers.srec.arch                                                                                           
    Out[15]: 'msp430'

    In [16]: vw.config.viv.parsers.ihex.arch                                                                                           
    Out[16]: 'cc8051'

    In [17]: vw.config.viv.parsers.ihex
    Out[17]: <envi.config.EnviConfig at 0x7fe9d2760070>

    In [18]: print(vw.config.viv.parsers.ihex.reprConfigPaths())
    Valid Config Entries:
        .arch = cc8051
        .offset = 0
        .bigend = False

    Valid Config Paths:
    

    In [19]: vw.config.viv.parsers.ihex.arch='arm'


Once you have configured the necessary items, load your file::

    In [31]: vw.loadFromFile('/home/atlas/work/firmware.hex')                                      

    In [32]: vw.getMeta('Architecture')                                                                                                
    Out[32]: 'arm'

    In [32]: vw.analyze()

When you're happy with your workspace, be sure to save it::

    In [33]: vw.saveWorkspace(fullsave=True)

To save a workspace, `vw.saveWorkspace()` is used.  The "fullsave=True" means to write a complete file, instead of saving incrementally.  For the first time save, this is important, as it places the header on the workspace file which tells Viv what kind of file it is.

No filename is given, but the filename to be written is stored in the workspace metadata.  The default name is the last file loaded into the workspace + ".viv".  You can see and modify this filename like so::

    In [36]: vw.getMeta('StorageName')                                                                                                 
    Out[36]: '/home/atlas/work/firmware.hex.viv'

    In [37]: vw.setMeta('StorageName', '/home/atlas/work/firmware.hex-clean-211205.viv')

    In [38]: vw.saveWorkspace(fullsave=True)                                                                                           


Loading an ELF and Working With Functions
=========================================

Getting started working with files is really quite easy.  Cherry-picking from the illustrations above::

    import vivisect
    vw = vivisect.VivWorkspace()
    vw.loadFromFile('/bin/chown')
    vw.analyze()
    vw.setMeta('StorageName', '/home/atlas/work/chown-new.viv')
    vw.saveWorkspace(True)

or:
    In [62]: vw = vivisect.VivWorkspace()                                                                                              

    In [63]: vw.loadFromFile('/bin/chown')                                                                                             
    Out[63]: 'chown'

    In [64]: vw.getMeta('StorageName')                                                                                                 
    Out[64]: '/bin/chown.viv'

    In [65]: vw.analyze() 

    In [66]: vw.setMeta('StorageName', '/home/atlas/work/chown-new.viv') 

    In [67]: vw.saveWorkspace(True) 

`VivWorkspace.getFunctions()` returns a list of Virtual Addresses (va's) for the beginning of each function::

    In [67]: vw.getFunctions()                                                                                                         
    Out[67]: 
    [0x20024a0,
     0x2002000,
     0x200b5c4,
     0x2002f10,
     0x2002480,
     0x2002e60,
    ...]

Let's get more information about a function.  For our purpose, we'll play with 0x200b530::

    fva = 0x200b530

    In [89]: fva = 0x200b530                                                                                                           
    
    In [90]: vw.getName(fva)                                                                                                           
    Out[90]: 'sub_0200b530'
    
    In [91]: vw.getFunctionApi(fva)                                                                                                    
    Out[91]: 
    ('int',
     None,
     'sysvamd64call',
     None,
     [('int', 'rdi'), ('int', 'rsi'), ('int', 'rdx')])
    
    In [92]: vw.getFunctionArgs(fva)                                                                                                   
    Out[92]: [('int', 'rdi'), ('int', 'rsi'), ('int', 'rdx')]
    
    In [93]: vw.getFunctionBlocks(fva)                                                                                                 
    Out[93]: 
    [(0x200b530, 0x37, 0x200b530),
     (0x200b567, 0x9, 0x200b530),
     (0x200b570, 0x16, 0x200b530),
     (0x200b586, 0xf, 0x200b530)]
    
    In [95]: vw.getFunctionLocals(fva)                                                                                                 
    Out[95]: []
    
    In [96]: vw.getFunctionMetaDict(fva)                                                                                               
    Out[96]: 
    {'CallsFrom': [0x2002000],
     'Size': 0x65,
     'BlockCount': 0x4,
     'InstructionCount': 0x22,
     'MnemDist': {'nop': 0x2,
      'push': 0x6,
      'lea': 0x2,
      'mov': 0x6,
      'sub': 0x2,
      'call': 0x2,
      'sar': 0x1,
      'jz': 0x1,
      'xor': 0x1,
      'add': 0x2,
      'cmp': 0x1,
      'jnz': 0x1,
      'pop': 0x6,
      'ret': 0x1},
     'api': ('int',
      None,
      'sysvamd64call',
      None,
      [('int', 'rdi'), ('int', 'rsi'), ('int', 'rdx')])}

And a fun one to work with, the Mnemonic Distribution for a function.  ie. what opcodes and how many of them::
    In [97]: vw.getFunctionMeta(fva, 'MnemDist')                                                                                       
    Out[97]: 
    {'nop': 0x2,
     'push': 0x6,
     'lea': 0x2,
     'mov': 0x6,
     'sub': 0x2,
     'call': 0x2,
     'sar': 0x1,
     'jz': 0x1,
     'xor': 0x1,
     'add': 0x2,
     'cmp': 0x1,
     'jnz': 0x1,
     'pop': 0x6,
     'ret': 0x1}

And one of the best features::

    In [101]: graph = vw.getFunctionGraph(fva)                                                                                         

    In [102]: graph.getNodes()
    Out[102]: 
    [(0x200b530,
      {'cbva': 0x200b530,
       'valist': (0x200b530,
        0x200b534,
        0x200b536,
        0x200b53d,
        0x200b53f,
    ...
    ]

    In [104]: graph.getEdges()                                                                                                         
    Out[104]: 
    [('d7e5e271cdffa91979a7975869f1b480',
      0x200b530,
      0x200b586,
      {'va1': 0x200b565, 'va2': 0x200b586, 'codeflow': (0x200b565, 0x200b586)}),
     ('afa8ae92b22bc8991d795494a98d9f55',
      0x200b530,
      0x200b567,
      {'va1': 0x200b565, 'va2': 0x200b567, 'codeflow': (0x200b565, 0x200b567)}),
     ('e9d715e9af6ed8b341af5d2d06da3acb',
      0x200b567,
      0x200b570,
      {'va1': 0x200b569, 'va2': 0x200b570, 'codeflow': (0x200b569, 0x200b570)}),
     ('d9b145f311c69a982d4f72707972d70e',
      0x200b567,
      0x200b570,
      {'va1': 0x200b584, 'va2': 0x200b570, 'codeflow': (0x200b584, 0x200b570)}),
     ('e705a3d616747893990567e06257be59',
      0x200b570,
      0x200b586,
      {'va1': 0x200b584, 'va2': 0x200b586, 'codeflow': (0x200b584, 0x200b586)})]
    

Loading a PE and Listing Its Exports
====================================

Having More Fun
===============

Vivisect maintains a list of Segments (in some cases, aka "sections"), which you can review like so::

    In [39]: vw.getSegments()                                                                                                          
    Out[39]: [(0x20000000, 0x100000, '20000000', 'firmware')]

Often more importantly, you can inspect the workspace's Memory Maps::

    In [45]: vw.getMemoryMaps()                                                                                                        
    Out[45]: [(0x20000000, 0x100000, 0x7, 'firmware')]


