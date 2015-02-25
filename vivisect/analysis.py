'''
API for the global registration of vivisect analysis modules
'''

class VivAnalysis:

analyzers = {}

def addVivAnalyzer(name,callback):

