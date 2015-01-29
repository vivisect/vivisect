# Vivisect MarkII

Vivisect MarkII is a next generation vivisect architecture which codifies
lessons learned from the years of organic growth of the vdb, vtrace, cobra,
envi, vstruct, and vivisect projects.

[http://visi.kenshoto.com/](http://visi.kenshoto.com/)

# MarkII Design
A number of design considerations are the foundation for the Viv MarkII
effort.

* 100% python3 ( this feature alone would require a total refactor )
* python2 compatible ( default case should be py3, with py2 fallbacks )
* unit tests unit tests unit tests ( shooting for 100% non-interface code coverage )
* portable / serializable data primitives
* async event driven architecture
* "impenetrable" abstraction layers
* "top" level APIs are RMI compatible
* more "data convention" less "data APIs" ( ie, setFooInfo("woot",10) > setFooWoot(10) )
* truly unified code ( previous vtrace + vivisect was a smash and go )
* ground-up distributed processing capability ( built in not bolt on )
* 0 cruft ( the legacy code base had grown organically )

and more I'm sure to think of later...

# Tools
Vivisect command line tools are implemented as executable python modules
which can be run using:

> python -m <toolmodule>

Vivisect tools:
* vivisect.tools.vdb    - replacement for vdbbin, the vivisect debug cli
* vivisect.tools.viv    - replacement for vivbin, the vivisect workspace cli
* vivisect.tools.bex    - binary executable dumper ( multi-format )

## vivisect.tools.viv
## vivisect.tools.vdb
## vivisect.tools.bex

