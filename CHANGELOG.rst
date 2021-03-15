******************
Vivisect Changelog
******************


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
  (`#352 https://github.com/vivisect/vivisect/pull/352`_)
- Python 3 Cleanup (for extensions/UI fixes/unicode detection/switchtable regression/ELF Parser)
  (`#353 https://github.com/vivisect/vivisect/pull/353`_)
- More memory render fixes
  (`#355 https://github.com/vivisect/vivisect/pull/355`_)
- More python3 fixes for API consistency and packed dll name exception handling
  (`#357 https://github.com/vivisect/vivisect/pull/357`_)
- Python3.6 specific import fixes
  (`#361 https://github.com/vivisect/vivisect/pull/361`_)
- Memory rendering tweaks to not double show bytes
  (`#364 https://github.com/vivisect/vivisect/pull/364`_)
- UI fixes for arrow keys, taint value fixes to prevent some infinity recursion
  (`#365 https://github.com/vivisect/vivisect/pull/365`_)
- Symbolik View was unusable
  (`#366 https://github.com/vivisect/vivisect/pull/366`_)
- DynamicBranches wasn't populating in py, and no return improvements
  (`#367 https://github.com/vivisect/vivisect/pull/367`_)
- Logging update for vivbin/vdbbin
  (`#368 https://github.com/vivisect/vivisect/pull/368`_)

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
- New noret pass/several API refreshes/intel emulator fixes/emucode hyra function fixes
  (`#333 <https://github.com/vivisect/vivisect/pull/333>`_)
- Migrate to CircleCI for Continuous Integratoin
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
