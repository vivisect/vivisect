import mfc42
import oledlg
import ws2_32
import comctl32
import msvbvm60
import oleaut32

'''
A small module for keeping a database of ordinal to symbol
mappings for DLLs which frequently get linked without symbolic
infoz.
'''

ords = {
    'mfc42.dll': mfc42.ord_names,
    'oledlg.dll': oledlg.ord_names,
    'ws2_32.dll': ws2_32.ord_names,
    'wsock32.dll': ws2_32.ord_names,
    'msvbvm60.dll': msvbvm60.ord_names,
    'comctl32.dll': comctl32.ord_names,
    'oleaut32.dll': oleaut32.ord_names,
}

def ordLookup(libname, ord):
    '''
    Lookup a name for the given ordinal if it's in our
    database.
    '''
    names = ords.get(libname.lower())
    if names is None:
        return 'ord%d' % ord
    name = names.get(ord)
    if name is None:
        return 'ord%d' % ord
    return name
