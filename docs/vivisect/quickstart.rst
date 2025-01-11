.. toctree::
   :titlesonly:

.. _quickstart:


Getting Started
###############


Installing
==========

**Vivisect** is a python 3.6 and up package, with several optional dependencies that can be installed, depending on your use case.

From the Python Package Index
-----------------------------

Packages for vivisect are built and push to the Python Package index at https://pypi.org/project/vivisect/. You can use pip to install vivisect/vdb/etc::

    pip install vivisect

Which will get you the latest vivisect for use in headless mode. If would also like a cool hacker UI to do your reverse engineering in, you can instead run::

    pip install "vivisect[gui]"

Which will also install the PyQt5 dependecies necessary for running the vivisect UI.

From Github
-----------

The code for vivisect lives at https://github.com/vivisect/vivisect/, where you can submit PRs, log issues, or clone the repo for your own personal modifications.

Installing Older Versions
-------------------------

The transition to python3 compatibility for vivisect is a relatively recent change, and a backwards incompatible one, so if you still need to run vivisect under python2, you can install a version of vivisect in the 0.2.x line, the most recent of which is 0.2.1.

Running the Vivisect UI
=======================

If you're eager to get started analyzing a binary, first:

- Make sure vivisect is up to date.

- Make sure you have all the GUI requirements installed

- Make sure vivisect is in your PYTHONPATH environment variable.

And then you should just be able to run the vivisect UI using this::

    python -m vivisect.vivbin

Or for convenience sake, we also register vivbin as a script name, so this should also work::

    vivbin

However, those commands merely open an empty UI, and we want to look at bytes and functions. To do that, we can run the vivbin script like so::

    vivbin /path/to/my/interesting/binary.exe

Which will kick off auto-analysis and then open the vivisect UI.


Running Bulk Analysis
=====================

If you'd prefer to run vivisect headless, or you want to save and/or share the initial workspace file, you can run vivisect in bulk analysis mode::

    vivbin -B /path/to/my/bulk/binary.exe

Which will create a ".viv" file located at `/path/to/my/bulk/binary.exe.viv`. The viv file is a saved version of the full workspace, so you can open it up like you would any other file::

    vivbin /path/to/my/bulk/binary.exe.viv


Collaborative Reverse Engineering
=================================

One of the most powerful aspects of Vivisect is its real-time collaboration server capabilities.  There are two ways to collaborate with others over a network.

- The first way is completely from the GUI, choosing `Share->Share Workspace` from one instance of Vivisect (vivbin), and others choosing `Share->Connect to Shared Workspace` from a separate Vivisect instance

- The other way to collaborate over a network, or using localhost, is to run a VivServer.  With a VivServer, you can share an entire directory structure of VivWorkspace files.

Because of the :ref:`event-driven <eventsystem>` Vivisect storage model, actions taken in one Vivisect window is easily redirected to the remote Server/Workspace, and other connected workspaces updated within seconds.

Running the VivServer
=====================

Running the VivServer is simple::

    vivserver /path/to/top/directory

Interacting with the VivServer
==============================

Saving a workspace to a VivServer is as simple as `File->Save to Server`
A popup lets you choose the server and the path.  A checkbox lets you set the default server.  If you access one server the majority of the time, you will find this very helpful.  If you want to access another server once or twice, don't check this box, and your default won't be affected.

The FilePath is where in the remote file repository this workspace will be stored, and its name (Be sure to add the .viv extension to the filename).

Loading a remote workspace from a VivServer is accomplished by `Share->Connect to Workspace Server`
A similar popup will allow you to select the server, and a followup dialog will list the workspaces available.  Once you choose a workspace, the current Vivisect window will close and be replaced by a new window, connected to the remote workspace.


Running the VDB UI
==================

Simimlarly, for vivbin, these commands also work::

    python -v vdbbin.vdbin -Q
    vdbbin -Q

Though vdb does not require a frontend, and it fine with operating without a frontend, so the `-Q` option is purely if you want the fanciness of a Qt UI

Attaching VDB to a Process
==========================

Fancy UI or not, Vdb is a debugger, so it requires some process to debug. If you want to attach to an already running process, you can supply it on the command line like so::

    vdbbin -p <process>

Where `<process>` is either the pid of the process you want to attach to, or some identifying substring of the process' command line

Alternatively, if you've already start vdb up::

    vdb > attach <process>

where `<process>` follows the same guidelines as above.

And if you want to start a process and attach to it from the start::

    vdbbin -c <command>

Where `<command>` is some command-line string (preferably quoted to avoid any issues) that vdb will then spawn off a subprocess for, and then attach to that child process.

And if you're already in the vdb command-line::
    vdb > exec <command>

Where `<command>` follows the same guideline as above.
