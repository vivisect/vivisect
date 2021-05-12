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

    pip install vivisect[gui]

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
* Make sure vivisect is up to date.
* Make sure you have all the GUI requirements installed
* Make sure vivisect is in your PYTHONPATH environment variable.

And then you should just be able to run the vivisect UI using this::

    python -m viviect.vivbin

Or for convenience sake, we also register vivbin as a script name, so this should also work::

    vivbin

However, those commands merely open an empty UI, and we want to look at bytes and functions. To do that, we can run the vivbin script like so::

    vivbin /path/to/my/interesting/binary.exe

Which will kick off auto-analysis and then open the vivisect UI.


Running Bulk Analysis
=====================

If you'd prefer to run vivisect headless, or you want to save and/or share the initial workspace file, you can run vivisect in bulk analysis mode::

    vivbin -B /path/to/my/bulk/binary.exe

Which will create a ".viv" file located at `/path/to/my/bulk/binary.exe.viv`.

Running the Vdb UI
==================

Simimlarly, for vivbin, these commands also work::
    python -v vdbbin.vdbin -Q
    vdbbin -Q

