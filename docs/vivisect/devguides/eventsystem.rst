.. _eventsystem:

The Event System
################

Vivisect's event system is how vivisect informs itself of what's going on, what pieces of analysis should be saved, what remote calls are happening, and just generally what's going on.

More formally, the event system is comprised of a series of handler functions on the VivWorkspaceCore class in `vivisect/base.py`, as well as a firing mechanism (the `_fireEvent` method on the VivWorkspaceCore class). As the main workspace fires events, the handler registered for that event runs. So when something like `VivWorkspace.delLocation` is called, `delLocation` runs and can do whatever setup it wants, and then as a final function call, it calls `self._fireEvent` with the ID of the event it wants to fire (so in this example, `VWE_DELLOCATION`), and a tuple representing the data it wants to pass to the handler function.

On the surface, this seems like a little bit of overkill. However, this architecture buys us two useful features, along with one limitation. The first thing this buys us is our remote capabilities. Along with several other subsystems, vivisect also brings along a subproject called cobra, which is our own RPC mechanism. Vivisect uses this for enabling a client/server architecture, so that you can expose your vivisect session to a remote user and in real-time, collaborate on reverse engineering a binary, with events from both the client and the server auotmatically populating to the other side.

Secondly, the event system is how vivisect saves the workspace. Every time `_fireEvent` is called, the event type and the event info are appended are the running list of events that is a property on the VivWorkspace class.

The one limitation is that since we've married the event system and the save system, all values that are sent through the event system, for everything from setting metadata to function comments, must be serializable through both python's pickle package and msgpack. Besides that, we have not *historically* implemented custom serialization/deserialization methods on any classes/non-primitive typed objects in order to keep some basic level of backwards compatibility across vivisect and various workspace files.
