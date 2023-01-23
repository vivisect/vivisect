.. _scripting:

The Power of Scripts with Vivisect
##################################

You can script up menial tasks or powerful techniques using simple Python scripts from either the command-line or the GUI.  

Scripts are loaded and run as any python code is run from the command line.  The key diffenece is that Vivisect places a VivWorkspace object in the global namespace with the name `vw`.  The GUI, if one exists (Vivisect can be run headless), can be accessed using `vw.getVivGui()`.  

From the CommandLine, analysis modules can be run in the following fashion:
`$ vivbin -M attackmodule.py targetbin.viv`
If your module makes any changes to the VivWorkspace, be sure it saves:
`vw.saveWorkspace()`

To run a script from the GUI, the command bar at the bottom of the screen is used. Simply enter:
`script attackmodule.py <args>`
This method does not need to save to the workspace, as you can choose to do that through standard GUI methods (Ctrl-S or File->Save).  This method has the added benefit of being able to provide arguments, which are placed in the namespace as `argv`.  
