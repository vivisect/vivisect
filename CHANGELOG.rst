******************
Vivisect Changelog
******************

V1.0.5 - 2021-09-10
===================

Fixes
-----
- Fix ascii string size when the string terminates at the end of a memory map
  (`#437 <https://github.com/vivisect/vivisect/pull/437>`_)
- Better handle PE delay imports that use VA pointers instead of RVA pointers
  (`#439 <https://github.com/vivisect/vivisect/pull/439>`_)
- envi.IMemory.readMemValue: return None on truncated read
  (`#444 <https://github.com/vivisect/vivisect/pull/444>`_)
- Only apply the rep prefix on string instructions in intel emulation
  (`#447 <https://github.com/vivisect/vivisect/pull/447>`_)
- Fix a pair of regressions in ELF analysis
  (`#448 <https://github.com/vivisect/vivisect/pull/448>`_)
- Align ELF memory maps to page
  (`#451 <https://github.com/vivisect/vivisect/pull/451>`_)
- Integer division for struct array count in ELF
  (`#455 <https://github.com/vivisect/vivisect/pull/455>`_)
- Safe harness for addRelocation method on the workspace
  (`#456 <https://github.com/vivisect/vivisect/pull/456>`_)
- Log to appropriate logger in elfplt late module
  (`#458 <https://github.com/vivisect/vivisect/pull/458>`_)
- Allow duplicate init and fini functions in ELF files
  (`#459 <https://github.com/vivisect/vivisect/pull/459>`_)

v1.0.4 - 2021-08-22
===================

Features
--------
- Add structures to UI and a compressed version of the file to the meta events.
  (`#396 <https://github.com/vivisect/vivisect/pull/396>`_)
- Actual documentation!
  (`#400 <https://github.com/vivisect/vivisect/pull/400>`_)
- Massive ELFPLT overhaul.
  (`#401 <https://github.com/vivisect/vivisect/pull/401>`_)
- Speed tweaks for the pointers pass and the workspace emulator.
  (`#402 <https://github.com/vivisect/vivisect/pull/402>`_)

Fixes
-----
- RTD didn't like python 3.9, so go with 3.8.
  (`#400 <https://github.com/vivisect/vivisect/pull/400>`_)
- Have ud2 on amd64 halt codeflow and fix a MACH-O bug.
  (`#403 <https://github.com/vivisect/vivisect/pull/403>`_)
- Fix issues in vtrace's windows, vivisect/reports, PE/carve, and others.
  (`#404 <https://github.com/vivisect/vivisect/pull/404>`_)
- Tons of i386 emulator fixes.
  (`#405 <https://github.com/vivisect/vivisect/pull/405>`_)
- Safeguard mnemonic counting in codeblocks.py.
  (`#408 <https://github.com/vivisect/vivisect/pull/408>`_)
- Fix funcgraph issues with line highlighting.
  (`#409 <https://github.com/vivisect/vivisect/pull/409>`_)
- Fix issues in i386 decoding, a new thunk pass, new ELF relocations support, and more.
  (`#411 <https://github.com/vivisect/vivisect/pull/411>`_)
- Fix vstruct signed number issue.
  (`#412 <https://github.com/vivisect/vivisect/pull/412>`_)
- Change AMD64 symboliks class declaration to get the right dealloc method.
  (`#413 <https://github.com/vivisect/vivisect/pull/413>`_)
- Remove wintypes import for vtrace to avoid a python bug.
  (`#416 <https://github.com/vivisect/vivisect/pull/416>`_)
- Raise specific exception on invalid architecture.
  (`#418 <https://github.com/vivisect/vivisect/pull/418>`_)
- Raise specific exception on invalid section alignment.
  (`#420 <https://github.com/vivisect/vivisect/pull/420>`_)
- Raise specific exception on corrupt file.
  (`#422 <https://github.com/vivisect/vivisect/pull/422>`_)
- Better handle invalid exported filename in PE files.
  (`#426 <https://github.com/vivisect/vivisect/pull/426>`_)
- Fix struct.unpack issue and float issue on corrupt files.
  (`#428 <https://github.com/vivisect/vivisect/pull/428>`_)
- ARM impapi files.
  (`#431 <https://github.com/vivisect/vivisect/pull/431>`_)
- Fix python 3.8 compatibility issues (and add to CI) and fix platformDetach.
  (`#432 <https://github.com/vivisect/vivisect/pull/432>`_)
- Alignment and padding of PE sections.
  (`#436 <https://github.com/vivisect/vivisect/pull/436>`_)
- Better handle invalid import name.
  (`#441 <https://github.com/vivisect/vivisect/pull/441>`_)

v1.0.3 - 2021-05-02
===================

Features
--------
- Loosen requirements and bring setup and requirements.txt in line with each other
  (`#399 <https://github.com/vivisect/vivisect/pull/399>`_)

Fixes
-----
- N/A

v1.0.2 - 2021-05-02
===================

Features
--------
- Refactor and update the posix impapi
  (`#390 <https://github.com/vivisect/vivisect/pull/390>`_)

Fixes
-----
- Ancient visgraph bug
  (`#387 <https://github.com/vivisect/vivisect/pull/387>`_)
- Easier version engineering
  (`#388 <https://github.com/vivisect/vivisect/pull/388>`_)
- Remove Travis CI config and fully cut over to Circle CI
  (`#389 <https://github.com/vivisect/vivisect/pull/389>`_)
- Add check to prevent divide by zero in print stats
  (`#392 <https://github.com/vivisect/vivisect/pull/392>`_)
- Fix SaveToWorkspaceServer
  (`#393 <https://github.com/vivisect/vivisect/pull/393>`_)
- Intel emulator bug fixes
  (`#394 <https://github.com/vivisect/vivisect/pull/394>`_)
- Tests for intel emulator and more fixes
  (`#395 <https://github.com/vivisect/vivisect/pull/395>`_)


v1.0.1 - 2021-04-05
===================

Features
--------
- Dynamic dialog box/Extension docs
  (`#376 <https://github.com/vivisect/vivisect/pull/376>`_)
- ELF Checksec and metadata additions
  (`#379 <https://github.com/vivisect/vivisect/pull/379>`_)
- ARM Fixes/CLI Fixes/GUI Helpers
  (`#380 <https://github.com/vivisect/vivisect/pull/380>`_)

Fixes
-----
- Callgraph/PE/vtrace fixes and pip installation update
  (`#372 <https://github.com/vivisect/vivisect/pull/373>`_)
- Extensions improvements
  (`#374 <https://github.com/vivisect/vivisect/pull/374>`_)
- Migration Doc and script/Cobra fixes/Data pointer improvement/Remote fixes
  (`#377 <https://github.com/vivisect/vivisect/pull/377>`_)
- Intel addrsize prefix fix/decoding fixes/emulator and symboliks updates/vdb fixes
  (`#384 <https://github.com/vivisect/vivisect/pull/384>`_)
- Cobra cluster updates/ARM analysis fixes/Elf parser fix
  (`#385 <https://github.com/vivisect/vivisect/pull/385>`_)
- v1.0.1 release/Intel decoding update/vtrace linux ps fix
  (`#386 <https://github.com/vivisect/vivisect/pull/386>`_)


v1.0.0 - 2021-02-23
===================

Features
--------
- Full Python 3 cutover
  (`#328 <https://github.com/vivisect/vivisect/pull/328>`_)

Fixes
-----
- Make envi.codeflow stable when analyzing function
  (Wrapped in as part of #328)
- Fixing some issues with memory view rendering
  (`#352 <https://github.com/vivisect/vivisect/pull/352>`_)
- Python 3 Cleanup (for extensions/UI fixes/unicode detection/switchtable regression/ELF Parser)
  (`#353 <https://github.com/vivisect/vivisect/pull/353>`_)
- More memory render fixes
  (`#355 <https://github.com/vivisect/vivisect/pull/355>`_)
- More python3 fixes for API consistency and packed dll name exception handling
  (`#357 <https://github.com/vivisect/vivisect/pull/357>`_)
- Python3.6 specific import fixes
  (`#361 <https://github.com/vivisect/vivisect/pull/361>`_)
- Memory rendering tweaks to not double show bytes
  (`#364 <https://github.com/vivisect/vivisect/pull/364>`_)
- UI fixes for arrow keys, taint value fixes to prevent some infinity recursion
  (`#365 <https://github.com/vivisect/vivisect/pull/365>`_)
- Symbolik View was unusable
  (`#366 <https://github.com/vivisect/vivisect/pull/366>`_)
- DynamicBranches wasn't populating in py, and no return improvements
  (`#367 <https://github.com/vivisect/vivisect/pull/367>`_)
- Logging update for vivbin/vdbbin
  (`#368 <https://github.com/vivisect/vivisect/pull/368>`_)

v0.2.0 - 2021-02-01
===================

Features
--------
- More IMAGE_FILE defs and honoring NXCOMPAT in older PE files
  (`#319 <https://github.com/vivisect/vivisect/pull/319>`_)
- Msgpack backed storage module
  (`#321 <https://github.com/vivisect/vivisect/pull/321>`_)
- Substring location accesses
  (`#327 <https://github.com/vivisect/vivisect/pull/327>`_)
- Parse and return the delay import table
  (`#331 <https://github.com/vivisect/vivisect/pull/331>`_)
- New noret pass/several API refreshes/intel emulator fixes/emucode hydra function fixes
  (`#333 <https://github.com/vivisect/vivisect/pull/333>`_)
- Migrate to CircleCI for Continuous Integration
  (`#336 <https://github.com/vivisect/vivisect/pull/336>`_)
- Enhance UI extensions
  (`#341 <https://github.com/vivisect/vivisect/pull/341>`_)
- SREC file parsing support
  (`#343 <https://github.com/vivisect/vivisect/pull/343>`_)


Fixes
-----
- Import emulator to handle dynamic branches (switchcases) using only xrefs
  (`#314 <https://github.com/vivisect/vivisect/pull/314>`_)
- ARM Register access tweaks
  (`#315 <https://github.com/vivisect/vivisect/pull/315>`_)
- Normlize the return value/usage of i386's getOperAddr
  (`#316 <https://github.com/vivisect/vivisect/pull/316>`_)
- Bugfix for handling deleted codeblocks
  (`#317 <https://github.com/vivisect/vivisect/pull/317>`_)
- Syntax error fixes
  (`#318 <https://github.com/vivisect/vivisect/pull/318>`_)
- PE carving fix/makePointer call in makeOpcode fix
  (`#320 <https://github.com/vivisect/vivisect/pull/320>`_)
- More intel nop instruction decodings
  (`#326 <https://github.com/vivisect/vivisect/pull/326>`_)
- More intel decodings/Codeflow fixes/Enable ARM for PE/Address infinite loop/Metadata
  (`#329 <https://github.com/vivisect/vivisect/pull/329>`_)
- Cobra: not configuring logging for everyone upon import
  (`#330 <https://github.com/vivisect/vivisect/pull/330>`_)
- Speedup for symbolik's setSymKid and more intel decoding fixes
  (`#332 <https://github.com/vivisect/vivisect/pull/332>`_)
- Don't configure logging in vivisect module
  (`#334 <https://github.com/vivisect/vivisect/pull/334>`_)
- Slight ARM fixes for bx flags and IHEX fixes for meta info
  (`#337 <https://github.com/vivisect/vivisect/pull/337>`_)
- PE fixes for reading at high relative offsets
  (`#338 <https://github.com/vivisect/vivisect/pull/338>`_)
- Streamline ELF tests to reduce memory footprint
  (`#340 <https://github.com/vivisect/vivisect/pull/340>`_)
- Streamline Symboliks Tests to reduce memory footprint
  (`#342 <https://github.com/vivisect/vivisect/pull/342>`_)
- Remove unused cobra imports
  (`#344 <https://github.com/vivisect/vivisect/pull/344>`_)
- More robust location handling for corrupt PE files
  (`#347 <https://github.com/vivisect/vivisect/pull/347>`_)


v0.1.0 - 2020-09-08
===================

Features
--------
- ELF tweaks for ARM binaries.
  (`#290 <https://github.com/vivisect/vivisect/pull/290>`_)
- Codebase cleanup in preparation to move to python 3.
  (`#293 <https://github.com/vivisect/vivisect/pull/293>`_)
- More opcode mappings for intel.
  (`#299 <https://github.com/vivisect/vivisect/pull/299>`_)
- Upgrade cxxfilt.
  (`#302 <https://github.com/vivisect/vivisect/pull/302>`_)
- Expand unittest coverage.
  (`#303 <https://github.com/vivisect/vivisect/pull/303>`_)
- Support for integrating with revsync.
  (`#304 <https://github.com/vivisect/vivisect/pull/304>`_)
- Symbolik Reduction Speedup.
  (`#309 <https://github.com/vivisect/vivisect/pull/309>`_)

Fixes
-----
- PyPI fix for vtrace.
  (`#300 <https://github.com/vivisect/vivisect/pull/300>`_)
- Calling convention fixes
  (`#301 <https://github.com/vivisect/vivisect/pull/301>`_)
- ARM disassembly and emulation bugfixes.
  (`#305 <https://github.com/vivisect/vivisect/pull/305>`_)
- Msgpack strict_map_key bugfix.
  (`#307 <https://github.com/vivisect/vivisect/pull/307>`_)
- Make creation of $HOME/.viv directory user configurable.
  (`#310 <https://github.com/vivisect/vivisect/pull/310>`_)


v0.1.0rc1 - 2020-07-30
======================
- Initial Pypi Release
