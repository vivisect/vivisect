# Migrating to Python3

So vivisect recently went from python2 to python3. Luckily, most APIs have stayed
relatively the same. There are a couple APIs (such as read/write memory) where the
inputs/outputs have changed, but for the most part, the APIs have very similar
structure to what they had before. Beyond that though, perhaps the biggest hurdle
for upgrading from python2 to python3 are any pre-existing workspaces.

## Existing workspaces

Workspaces saved via the basicfile format won't migrate cleanly. Basicfile is backed
by python's pickle, so having it work across python2 and python3 is...tricky. Not
impossible, but in order to maintain backwards compatibility, while still providing
an upgrade path, there's another storage module (vivisect.storage.mpfile) that is 
msgpack based which, and works across python versions. To further help with migration,
there's the `vivisect.storage.tools.convert` module that can convert from one storage
format to the other. The conversion module exists in both the latest python2 release
(0.2.1) as well as the upcoming 1.0.1 release, in case another major need of it arises.

But to convert a single workspace from basicfile to mpfile:
```
python2 -m vivisect.storage.tools.convert <basicfile_workspace>
```
Which will then produce a `<workspace>.mpviv` file that should be loadable in python2 and python3.

The opposite also works, so you can run:
```
python2 -m vivisect.storage.tools.convert <mpfile_workspace>
```
To produce a basicfile-based workspace.

Please note that since we don't want to accidentally overwrite any files, the `.viv`
or `.mpviv` extensions that the conversion tool do not replace any other extensions,
so if you run the conversion tool on `foo.viv`, you'll end up with `foo.viv.mpviv`.
If this is not the behavior you want, you can supply the `--name` parameter to the tool
to specify the name for the new workspace like so:
```
python2 -m vivisect.storage.tools.convert <workspace> --name <my_new_worksapce_name>
```
