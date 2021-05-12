.. _analysismodules:

Overview
========

Vivisect's analysis modules are starting points of the majority of how vivisect discovers interesting features of a binary. 

Organization
============

Internally, vivisect organizes analysis modules by OS type and processor architecture. For example, an analysis module that deals strictly with 32-bit intel would live in `vivisect/analysis/i386/`, while an analysis module that deals with any elf file would live in `vivisect/analysis/elf/`. For analysis modules that operate on just the workspace, and don't contain any code that deals with a specific architecture, those typically live in `vivisect/analysis/generic`.

Now, that's not to say an analysis modules has to live in there. Analysis modules 

Individual modules are loaded on demand by the `_snapInAnalysisModules` workspace method.


Workspace Level Modules
=======================


Function Level Modules
======================


