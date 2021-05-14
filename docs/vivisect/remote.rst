.. _remote:

Remote Vivisect
###############

Vivisect comes with it's own RPC mechanism called cobra. While cobra itself is designed to be a fairly general mechanism for RPC, the main usage of cobra inside vivisect is to facilitate remote collaboration. If you've got a directory full of vivisect workspace files, you can share those workspaces files via::

    python3 -m vivisect.remote.server </path/to/directory>

Which will then spawn a serverand print out the port that other users can connect to in order to pull down one (or more) of the workspaces. And as events are added, by either the server or the client, those events will populate to the other end of the pipe.
