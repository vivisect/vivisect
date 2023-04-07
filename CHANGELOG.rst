******************
Vivisect Changelog
******************

V1.1.1 - 2023-04-07
===================
Features
--------
- More test resiliency for our remote server tests.
  (`#584 https://github.com/vivisect/vivisect/pull/584`_)
- Document ``getBranches`` API.
  (`#589 https://github.com/vivisect/vivisect/pull/589`_)
- Add "stepo" functionality as an option for "stepi" in VDB.
  (`#591 https://github.com/vivisect/vivisect/pull/591`_)
- Migrate away from some deprecated functions.
  (`#593 https://github.com/vivisect/vivisect/pull/593`_)
- GUI scroll improvements.
  (`#599 https://github.com/vivisect/vivisect/pull/599`_)
- Envi config get by string.
  (`#604 https://github.com/vivisect/vivisect/pull/604`_)

Fixes
-----
- Fix 64-bit emulation of intel's ``div`` instruction.
  (`#575 <https://github.com/vivisect/vivisect/pull/575>`_)
- Do dynamic imports in our envi module via importlib.import_module.
  (`#587 <https://github.com/vivisect/vivisect/pull/587>`_)
- Make our ELF module more resilient to failures.
  (`#592 <https://github.com/vivisect/vivisect/pull/592>`_)
- Fix a regex that uses an invalid escape sequence.
  (`#596 <https://github.com/vivisect/vivisect/pull/596>`_)
- Fix PE parser config option usage.
  (`#605 <https://github.com/vivisect/vivisect/pull/605>`_)
- Fix ``envi.interactive`` flag.
  (`#606 <https://github.com/vivisect/vivisect/pull/606>`_)


V1.1.0 - 2023-02-18
===================
Features
--------
- Update VDB's handling of x64 systems.
  (`#56 <https://github.com/vivisect/vivisect/pull/56>`_)
- Symbolic switchcase analysis.
  (`#112 <https://github.com/vivisect/vivisect/pull/112>`_)
- Make Vivisect loader more elegantly handle multiple files.
  (`#472 <https://github.com/vivisect/vivisect/pull/472>`_)
- Funcgraph enhancements: AutoRefresh, FollowTheLeader, Xrefs Window, and Window Renaming.
  (`#488 <https://github.com/vivisect/vivisect/pull/488>`_)
- update impapi to cover msvcr100.dll
  (`#522 <https://github.com/vivisect/vivisect/pull/522>`_)
- Add a SaveToServer dialog.
  (`#527 <https://github.com/vivisect/vivisect/pull/527>`_)
- Update imphook names in the platarch emulators.
  (`#530 <https://github.com/vivisect/vivisect/pull/530>`_)
- Relocatable ELF Support.
  (`#531 <https://github.com/vivisect/vivisect/pull/531>`_)
- Check before making new location types in the UI.
  (`#533 <https://github.com/vivisect/vivisect/pull/533>`_)
- Turn register groups from a tuple to a dictionary.
  (`#542 <https://github.com/vivisect/vivisect/pull/542>`_)
- Store a file's original name in the meta info.
  (`#543 <https://github.com/vivisect/vivisect/pull/543>`_)
- Add API entry for __read_chk on posix.
  (`#545 <https://github.com/vivisect/vivisect/pull/545>`_)
- Add option to WorkspaceEmulator to disable shared caching.
  (`#547 <https://github.com/vivisect/vivisect/pull/547>`_)
- Enabling POSIX Library Load notifications.
  (`#550 <https://github.com/vivisect/vivisect/pull/550>`_)
- Add i386 opcode vpcext.
  (`#556 <https://github.com/vivisect/vivisect/pull/556>`_)
- Update vamp signatures.
  (`#566 <https://github.com/vivisect/vivisect/pull/566>`_)
- Making architecture names/numbers in envi for impending architectures.
  (`#567 <https://github.com/vivisect/vivisect/pull/567>`_)
- Refactoring Windows library APIs.
  (`#572 <https://github.com/vivisect/vivisect/pull/572>`_)
- Sort context menu options and add "this window" option.
  (`#577 <https://github.com/vivisect/vivisect/pull/577>`_)

Fixes
-----
- Various fixes to improve ARM analysis.
  (`#473 <https://github.com/vivisect/vivisect/pull/473>`_)
- Fix an issue in the remote server.
  (`#523 <https://github.com/vivisect/vivisect/pull/523>`_)
- Fix some remote gui bugs.
  (`#525 <https://github.com/vivisect/vivisect/pull/525>`_)
- Documentation build fixes.
  (`#535 <https://github.com/vivisect/vivisect/pull/535>`_)
- More documentation build fixes.
  (`#537 <https://github.com/vivisect/vivisect/pull/537>`_)
- Bump QT Versions to address hanging.
  (`#541 <https://github.com/vivisect/vivisect/pull/541>`_)
- Fix VivWorkspace opcache key creation.
  (`#544 <https://github.com/vivisect/vivisect/pull/544>`_)
- More ARM bugfixes.
  (`#546 <https://github.com/vivisect/vivisect/pull/546>`_)
- Fix and extend Windows API hooking.
  (`#548 <https://github.com/vivisect/vivisect/pull/548>`_)
- VTrace posix missing import.
  (`#549 <https://github.com/vivisect/vivisect/pull/549>`_)
- minor bugfixes: VDB RegisterView widget
  (`#552 <https://github.com/vivisect/vivisect/pull/552>`_)
- Fix i386's vtrace archGetBackTrace results.
  (`#553 <https://github.com/vivisect/vivisect/pull/553>`_)
- Linux i386 syscall fixes.
  (`#555 <https://github.com/vivisect/vivisect/pull/555>`_)
- Pull back in some fixes that got lost in merges.
  (`#564 <https://github.com/vivisect/vivisect/pull/564>`_)
- Make MiniDump log to a named logger.
  (`#565 <https://github.com/vivisect/vivisect/pull/565>`_)
- Make BasicFile storage write the header when used from the UI.
  (`#570 <https://github.com/vivisect/vivisect/pull/570>`_)
- Arch Const Handling refactoring.
  (`#571 <https://github.com/vivisect/vivisect/pull/571>`_)
- Architecture loading emergency bugfix.
  (`#578 <https://github.com/vivisect/vivisect/pull/578>`_)

V1.0.8 - 2022-04-28
===================

Features
--------
- Improved Save-As capabilities when connected to a remote server and better struct making from the UI. 
  (`#501 <https://github.com/vivisect/vivisect/pull/501>`_)
- Improve output for the UI's ``names`` command.
  (`#516 <https://github.com/vivisect/vivisect/pull/516>`_)

Fixes
-----
- Fix issue in the proxy case where we forgot to snap in the analysis modules.
  (`#498 <https://github.com/vivisect/vivisect/pull/498>`_)
- Fix string naming.
  (`#502 <https://github.com/vivisect/vivisect/pull/502>`_)
- Fix a bug in ELFPLT analysis where certain dynamic tables were missing.
  (`#503 <https://github.com/vivisect/vivisect/pull/503>`_)
- Fix an issue where ELF parsing of STT_FUNCs was based on too many bits.
  (`#505 <https://github.com/vivisect/vivisect/pull/505>`_)
- Fix an missing name issue in Save-As.
  (`#507 <https://github.com/vivisect/vivisect/pull/507>`_)
- Improve thread safety for client workspaces.
  (`#508 <https://github.com/vivisect/vivisect/pull/508>`_)
- Fix the i386 Emulator's handling of rep(n)z.
  (`#513 <https://github.com/vivisect/vivisect/pull/513>`_)
- Fix issue when dealing with invalid PE section names.
  (`#514 <https://github.com/vivisect/vivisect/pull/514>`_)
- Fix an incorrect import name in vivbin.
  (`#518 <https://github.com/vivisect/vivisect/pull/518>`_)
- Fix a debug logging message in the ``libc_start_main`` analysis pass that would cause that analysis pass to exception out.
  (`#519 <https://github.com/vivisect/vivisect/pull/519>`_)

V1.0.7 - 2022-01-13
===================

Features
--------
- More Mach-O structure definitions and parsing support.
  (`#495 <https://github.com/vivisect/vivisect/pull/495>`_)

Fixes
-----
- Tweak how i386 analysis detections calling conventions.
  (`#493 <https://github.com/vivisect/vivisect/pull/493>`_)
- Use OptionalHeader.Magic for determining PE32/PE32+.
  (`#494 <https://github.com/vivisect/vivisect/pull/494>`_)

V1.0.6 - 2022-01-03
===================

Features
--------
- Cohesive Memory Maps.
  (`#450 <https://github.com/vivisect/vivisect/pull/450>`_)
- Add changelog to the docs build.
  (`#462 <https://github.com/vivisect/vivisect/pull/462>`_)
- Add test for unknown workspace events.
  (`#463 <https://github.com/vivisect/vivisect/pull/463>`_)
- Flesh out Delete Relocation Event and add Test Helpers.
  (`#471 <https://github.com/vivisect/vivisect/pull/471>`_)
- Update docs with developer intro info.
  (`#475 <https://github.com/vivisect/vivisect/pull/475>`_)
- Update IPython integration module.
  (`#487 <https://github.com/vivisect/vivisect/pull/487>`_)
- Improve Emulation Taint Comments.
  (`#490 <https://github.com/vivisect/vivisect/pull/490>`_)

Fixes
-----
- Fix PE carving.
  (`#464 <https://github.com/vivisect/vivisect/pull/464>`_)
- Update intel emulator repetition options.
  (`#465 <https://github.com/vivisect/vivisect/pull/465>`_)
- Update VDB's UI class inheritance to deal with display crashes.
  (`#466 <https://github.com/vivisect/vivisect/pull/466>`_)
- Update the various CLIs and VAMP interfaces.
  (`#467 <https://github.com/vivisect/vivisect/pull/467>`_)
- Fix ARM's Vivisect/VDB bridges.
  (`#469 <https://github.com/vivisect/vivisect/pull/469>`_)
- A grab bag of fixes for function thunking, ELF PLT analysis, ARM emulation, and no return display.
  (`#470 <https://github.com/vivisect/vivisect/pull/470>`_)
- Fix special character rending in the UI.
  (`#474 <https://github.com/vivisect/vivisect/pull/474>`_)
- Fix the intel emulator's idiv instruction.
  (`#476 <https://github.com/vivisect/vivisect/pull/476>`_)
- Make MACH-O parsing work.
  (`#486 <https://github.com/vivisect/vivisect/pull/486>`_)


V1.0.5 - 2021-09-10
===================

Fixes
-----
- Fix ascii string size when the string terminates at the end of a memory map.
  (`#437 <https://github.com/vivisect/vivisect/pull/437>`_)
- Better handle PE delay imports that use VA pointers instead of RVA pointers.
  (`#439 <https://github.com/vivisect/vivisect/pull/439>`_)
- envi.IMemory.readMemValue: return None on truncated read.
  (`#444 <https://github.com/vivisect/vivisect/pull/444>`_)
- Only apply the rep prefix on string instructions in intel emulation.
  (`#447 <https://github.com/vivisect/vivisect/pull/447>`_)
- Fix a pair of regressions in ELF analysis.
  (`#448 <https://github.com/vivisect/vivisect/pull/448>`_)
- Align ELF memory maps to page.
  (`#451 <https://github.com/vivisect/vivisect/pull/451>`_)
- Integer division for struct array count in ELF.
  (`#455 <https://github.com/vivisect/vivisect/pull/455>`_)
- Safe harness for addRelocation method on the workspace.
  (`#456 <https://github.com/vivisect/vivisect/pull/456>`_)
- Log to appropriate logger in elfplt late module.
  (`#458 <https://github.com/vivisect/vivisect/pull/458>`_)
- Allow duplicate init and fini functions in ELF files.
  (`#459 <https://github.com/vivisect/vivisect/pull/459>`_)
- Add Vtrace Symbol test.
  (`#460 <https://github.com/vivisect/vivisect/pull/460>`_)

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
- Initial PyPI Release
