******************
Vivisect Changelog
******************

v0.2.0 - 2021-01-12
===================
Features
--------
- More IMAGE_FILE defs and honoring NXCOMPAT in older PE files
  (`#319 https://github.com/vivisect/vivisect/pull/319`)
- Msgpack backed storage module
  (`#321 https://github.com/vivisect/vivisect/pull/321`)
- Substring location accesses
  (`#327 https://github.com/vivisect/vivisect/pull/327`)
- Parse and return the delay import table
  (`#331 https://github.com/vivisect/vivisect/pull/331`)
- New noret pass/several API refreshes/intel emulator fixes/emucode hyra function fixes
  (`#333 https://github.com/vivisect/vivisect/pull/333`)

Fixes
-----
- Import emulator to handle dynamic branches (switchcases) using only xrefs
  (`#314 https://github.com/vivisect/vivisect/pull/314`)
- ARM Register access tweaks
  (`#315 https://github.com/vivisect/vivisect/pull/315`)
- Normlize the return value of i386's getOperAddr
  (`#316 https://github.com/vivisect/vivisect/pull/316`)
- Bugfix for handling deleted codeblocks
  (`#317 https://github.com/vivisect/vivisect/pull/317`)
- Syntax error fixes
  (`#318 https://github.com/vivisect/vivisect/pull/318`)
- PE carving fix/makePointer call in makeOpcode fix
  (`#320 https://github.com/vivisect/vivisect/pull/320`)
- More intel nop decodings
  (`#326 https://github.com/vivisect/vivisect/pull/326`)
- More intel decodings/Codeflow fixes/Enable ARM for PE/Address infinite loop/Metadata
  (`#329 https://github.com/vivisect/vivisect/pull/329`)
- Cobra: not configuring logging for everyone upon import
  (`#330 https://github.com/vivisect/vivisect/pull/330`)
- Speedup for symbolik's setSymKid and intel decoding fixes
  (`#332 https://github.com/vivisect/vivisect/pull/332`)
- Don't configure logging in vivisect module
  (`#334 https://github.com/vivisect/vivisect/pull/334`)

v0.1.0 - 2020-09-08
===================
Features
--------
- ELF tweaks for ARM binaries.
  (`#290 <https://github.com/vivisect/vivisect/pull/290>`)
- Codebase cleanup in preparation to move to python 3.
  (`#293 <https://github.com/vivisect/vivisect/pull/293>`)
- More opcode mappings for intel.
  (`#299 <https://github.com/vivisect/vivisect/pull/299>`)
- Upgrade cxxfilt.
  (`#302 <https://github.com/vivisect/vivisect/pull/302>`)
- Expand unittest coverage.
  (`#303 <https://github.com/vivisect/vivisect/pull/303>`)
- Support for integrating with revsync.
  (`#304 <https://github.com/vivisect/vivisect/pull/304>`)
- Symbolik Reduction Speedup.
  (`#309 <https://github.com/vivisect/vivisect/pull/309>`)

Fixes
-----
- PyPI fix for vtrace.
  (`#300 <https://github.com/vivisect/vivisect/pull/300>`)
- Calling convention fixes
  (`#301 <https://github.com/vivisect/vivisect/pull/301>`)
- ARM disassembly and emulation bugfixes.
  (`#305 <https://github.com/vivisect/vivisect/pull/305>`)
- Msgpack strict_map_key bugfix.
  (`#307 <https://github.com/vivisect/vivisect/pull/307>`)
- Make creation of $HOME/.viv directory user configurable.
  (`#310 <https://github.com/vivisect/vivisect/pull/310>`)


v0.1.0rc1 - 2020-07-30
======================
- Initial Pypi Release
