import os
import bs4
import pickle
import requests
import tempfile
'''
Downloads lots of pages, parses, and pulls out function declarations for impapi

(210409)
One problem: 7 functions from "Waiting with Specific Clocks" page don't have 
all their arguments fit in the <dt> tags.  Rather than rework the script that
works for 1500+ other functions, we just modified the output manually.
(https://www.gnu.org/software/libc/manual/html_node/Waiting-with-Explicit-Clocks.html)


'''

BASE_URL = "https://www.gnu.org/software/libc/manual/html_node/"
def getAllFrontUrls(sess):
    frontpage = sess.get(BASE_URL + 'Function-Index.html') 
    soup = bs4.BeautifulSoup(frontpage.text)
    urls = []
    for link in soup.find_all('a'):
        url = link.get('href') 
        uurl = url 
        if '#' in uurl: 
            uurl = url[:url.find('#')] 
 
        if url in urls:
            continue

        urls.append(uurl)

    return urls


def getAllFuncProtos(funcs=None):
    if funcs is None:
        funcs = getRawDataLines()
    api = parseDataLines(funcs)

    return api


def getRawDataLines():
    with requests.session() as sess:

        # get all 1500+ urls and downselect them to functions 
        urls = getAllFrontUrls(sess)
        pages = [sess.get(BASE_URL + url) for url in urls]

        bss = [bs4.BeautifulSoup(page.text) for page in pages]

        dts = []
        funcdts = []
        for b in bss:
            dt = b.find_all('dt')

            for item in dt:
                if 'Function:' in repr(item):
                    if item not in funcdts:
                        funcdts.append(item)

        # strip out the text and whittle each function down to a prototype line
        functext = [fdt.text for fdt in funcdts]
        funcs = [line[10:] for line in functext]  # skip first 10 chars, "Function: "
        return funcs

def parseDataLines(funcs):
    # parse each line and populate the api dict
    api = {}
    for func in funcs:
        func = func.replace("*", "* ").replace(';', '')
        print(func)
        # split at the (
        leftside, rightside = func.split('(', 1)

        # handle the left side
        parts = [x for x in leftside.split(' ') if len(x)]

        funcname = parts.pop()
        rettype = ' '.join(parts)

        # handle the args (rightside)
        rightside = rightside.replace(')','')
        args = rightside.split(',')
        argchunks = [arg.split(' ') for arg in args]

        argout = []
        if argchunks != [['void']]:     # skip "(void)" entries
            for chunk in argchunks:
                chunk = [foo.strip() for foo in chunk if len(foo.strip())]
                if len(chunk):
                    if chunk[-1].endswith(')') or len(chunk) == 1:
                        aname = None
                    else:
                        aname = chunk.pop()

                    # handle variadic args (...):
                    if len(chunk) and chunk[-1] in ('...', b'\xe2\x80\xa6'.decode('utf8')):
                        atype = 'variadic'
                        aname = ''
                    else:
                        atype = ' '.join(chunk)

                    argout.append((atype, aname))
                else:
                    input("FIXME: lost args at the end")

        if 'printf' in func:
            #import envi.interactive as ei; ei.dbg_interact(locals(), globals())
            pass


        cconv = cconvs.get(funcname, 'cdecl')
        
        api['plt_%s' % funcname] = (rettype, None, cconv, '*.%s' % funcname, tuple(argout))

    return api

cconvs = {
        'div': 'stdcall',
        'ldiv': 'stdcall',
        'lldiv': 'stdcall',
        'mallinfo': 'stdcall',
        'inet_makeaddr': 'stdcall',
        }


def reprAllFuncProtos(funcs=None):
    api = getAllFuncProtos(funcs)
    keys = list(api.keys())
    keys.sort()

    out = ['apitypes = {\n}','','api = {']
    out.append("    'plt___libc_start_main':( 'int', None, 'cdecl', '*.__libc_start_main', (('int', 'main'), ('int', 'argc'), ('int', 'argv')) ),")
    out.append("    'main':( 'int', None, 'stdcall', '*.main_entry', (('int', None), ('int', None), ('int', None)) ),")

    for key in keys:
        data = api.get(key)
        out.append("    %r: %r," % (key, data)
                )
    out.append('''    # taken from libc directly:
    'plt___libc_rpc_getport': ('int', None, 'stdcall', '*.__libc_rpc_getport', (('int', 'arg0'), ('int', 'arg1'), ('int', 'arg2'))),
    'plt___nss_services_lookup2': ('int', None, 'stdcall', '*.__nss_services_lookup2', (('int', 'arg0'),)),
    'plt___nss_passwd_lookup2': ('int', None, 'stdcall', '*.__nss_passwd_lookup2', (('int', 'arg0'),)),
    'plt__dl_addr': ('int', None, 'stdcall', '*._dl_addr', (('int', 'arg0'),)),
    'plt__dl_vsym': ('int', None, 'stdcall', None, (('int', 'arg0'),)),
    'plt___nss_group_lookup2': ('int', None, 'stdcall', '*.__nss_group_lookup2', (('int', 'arg0'),)),
    'plt___nss_hosts_lookup2': ('int', None, 'stdcall', '*.__nss_hosts_lookup2', (('int', 'arg0'),)),
    ''')
    out.append('}')
    return '\n'.join(out) + "\n"

def writeAllFuncProtos():
    open('i386.py', 'w').write(reprAllFuncProtos())


if __name__ == '__main__':
    writeAllFuncProtos()
