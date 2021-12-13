'''
Connect any Exports we have to Imports we may also have 
(most useful for multiple file workspaces)
'''
def analyze(vw):
    vw.connectImportsWithExports()
