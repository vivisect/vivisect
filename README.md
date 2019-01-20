# Vivisect / Vdb / Vtrace

Now all as one project! ( made sense once vivisect went public )
For more in-depth docs on various topics, see the wiki at
[http://visi.kenshoto.com/](http://visi.kenshoto.com/)

## Vdb

As in previous vdb releases, the command ```python vdbbin``` from the
checkout directory will drop you into a debugger prompt on supported
platforms. ( Windows / Linux / FreeBSD / OSX... kinda? )

Commands in vdb grow/refine quickly, so use in-line help such as:

> vdb> help

or...

> vdb> help writemem

to show available commands and options.  Additionally, for basic vdb
use, the wiki at [http://visi.kenshoto.com/](http://visi.kenshoto.com/)

## Vivisect

Fairly un-documented static analysis / emulation / symbolik analysis
framework for PE/Elf/Mach-O/Blob binary formats on various architectures.
To start with, you probably want to run a "bulk analysis" pass on a binary
using:

> python vivbin -B <binaryfile>

which will leave you with <binaryfile>.viv

Then run:

> python vivbin <binaryfile>.viv

to open the GUI and begin reverse engineering.  As with most vtoys, the ui
relies fairly heavily on right-click context menus and various memory
views.

For the binary ninjas, all APIs used during automatic analysis ( and several
that aren't ) are directly accessible for use writing your own custom
research tools...  The interface should be nearly the same when dealing with
a real process ( via vdb/vtrace ) and dealing with an emulator / viv workspace.

## UI Dependencies

The vivisect UI can be run under either PyQt4 and PyQt5

For running via PyQt4, first you'll need  to install Qt4 and Qt4-Webkit libraries. On Ubuntu, you can do this via:

```
sudo apt-get install libqt4-dev libqtwebkit-dev
```

If you're on an older version of python, you may be able to pip install PyQt4 and SIP like so:

```
pip install PyQt4 SIP
```

However, on recent (tested on 2.7.15 December 2018) versions of pip, that pip install fails. To get around this, you'll need to download the sources for both PyQt4 and SIP from Riverbank.
* SIP can be found [here](https://sourceforge.net/projects/pyqt/files/sip/sip-4.19.13/sip-4.19.13.tar.gz) 
* PyQt4 can be found [here](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12.3/PyQt4_gpl_x11-4.12.3.tar.gz)

Untar them to their respective directories and cd in the directory for SIP:

```
tar -xf sip-4.19.13.tar.gz
tar -xf PyQt4_gpl_x11-4.12.3.tar.gz
cd sip-4.19.13/
```

Then build the SIP module. Due to the recent version of SIP we're using, we have to build it as a private module like so:

```
python configure.py --sip-module PyQt4.sip
make
make install
```

Now cd back to the PyQt4 module and build that one:

```
cd ../PyQt4_gpl_x11-4.12.3/
python configure-ng.py
make -j4
make install
```

If you run into an `Error 2` status code on the `make install` line, replace that line with `sudo make install`, and things should work out fine.

And then you should be able to open up your vivisect workspace with the vivbin script.

### PyQt5

Installing PyQt5 via pip is not supported in Python 2.x. So similar steps must be followed to install PyQt5 to get the UI working that way as well.

Install qt5 and the webkit dependency:
```
sudo apt-get install qt5-default libqt5webkit5-dev
```

Install the dependencies that PyQt5 needs:
```
pip install enum34
```

The rest of the build/install steps are the same, save for changing out the version numbers from PyQt4 to PyQt5.

### Dependencies:
To enable proper networking:

```
pip install msgpack
```

To enable Posix C++ demangling:

```
pip install cxxfilter
```
## Build Status

[![Build Status](https://travis-ci.org/vivisect/vivisect.svg?branch=master)](https://travis-ci.org/vivisect/vivisect)
