.. _analysismodules:

Analysis Modules
################

Vivisect's analysis modules are starting points of the majority of how vivisect discovers interesting features of a binary. 

Organization
============

Internally, vivisect organizes analysis modules by OS type and processor architecture. For example, an analysis module that deals strictly with 32-bit intel would live in `vivisect/analysis/i386/`, while an analysis module that deals with any elf file would live in `vivisect/analysis/elf/`. For analysis modules that operate on just the workspace, and don't contain any code that deals with a specific architecture, those typically live in `vivisect/analysis/generic`. Not all of the analysis modules living in all the subdirectories of `vivisect/analysis` will be loaded by default. Which modules are loaded are a function of the exe format and the exe architecture. For more details on which modules are loaded under what cases, see `vivisect/analysis/__init__.py`.

Further, that's not to say an analysis modules has to live in any of those subdirectories. A custom analysis modules can be loaded using the `addAnalysisModule` or the `addFuncAnalysisModule`, depending on the type of analysis module you have.

Keep in mind that the order of analysis modules matters, so where your analysis modules runs relative to other modules matters. A general rule of thumb (but by no means a hard and fast rule) is that more specific analysis modules should run before more general modules. Specific and general in this case can be a bit of nebulous term, but typically general means something like the `vivisect/analysis/generic/pointers.py` analysis module, which is a bit of a shotgun atttempt to marshall anything that looks like a pointer into being a pointer location. Since it's a very broad sweeping analysis pass, it runs last in the cycle, so that we don't accidentally make a pointer out of something that should be an instruction (for example). On the opposite end of the spectrum, we have something like the `vivisect/analysis/i386/instrhook.py` analysis module, which only deals with very specific instructions in attempt to discover very specific pointers. It's relatively targeted, dealing with data we've already confident about, Which is why it can run relatively early in the analysis process.


Beyond the nebulous concepts of general vs specific analysis modules, there is one concrete difference in the analysis modules, and that's the difference between function level analysis modules and workspace level analysis modules.


Workspace Level Modules
=======================

While both workspace level analysis modules and function level modules have access to modifying the full workspace (due to API usage), workspace level modules are typically father reaching analysis modules. They are run only once, in the order that they are added by `VivWorkspace.addAnalysisModule`.

Workspace level modules all share the function type signature of `analyze(vw)`. `addAnalysisModule` adds the module via the python import path, so when we call `addAnalysisModule`, it's typically with something like `vivisect.analysis.generic.emucode`, and inside `vivisect/analysis/generic/emucode.py`, there is a function called `analyze` that takes the vivisect workspace as the first (and only) parameter.


Function Level Modules
======================

In contrast to a workspace level module, function level analysis modules are typically run many, many times. On every call to `VivWorkspace.makeFunction`, once codeflow finishes, each function level module is run on the newly discovered, in the order that they were added via `VivWorkspace.addFuncAnalysisModule`, so each function module runs once for each discovered function in a binary. 

Similar to workspace modules, each function modules shares a function signature  of `analyzeFunction(vw, fva)`.
`addFuncAnalysisModule` adds each function module by python import path, so when `addFuncAnalysisModule` is called, it's typically with something like `vivisect.analysis.generic.codeblocks`, and inside the corresponding `vivisect/analysis/generic/codeblocks.py`, there should be a function called `analyzeFunction` function, that takes two parameters, the first of which is the vivisect workspace object, and the second representing the starting virtual address of the function that is currently being created/analyzed.
