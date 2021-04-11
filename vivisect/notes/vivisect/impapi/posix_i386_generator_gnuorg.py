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
def cache_store(name, obj):
    tmpfile = os.sep.join([tempfile.gettempdir(), ".impapi.posix."+name])
    print(repr(tmpfile))
    outfile = open(tmpfile, 'wb')
    pcklstr = pickle.dumps(obj)
    outfile.write(pcklstr)

def cache_retr(name):
    tmpfile = os.sep.join([tempfile.gettempdir(), ".impapi.posix."+name])
    try:
        outf = open(tmpfile, 'rb')
        return pickle.load(outf)
    except Exception as e:
        print(e)
    return None


def getAllFrontUrls(sess):
    cached = cache_retr('urls')
    if cached is not None:
        return cached

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

    cache_store('urls', urls)

    return urls


def getAllFuncProtos(funcs=None):
    if funcs is None:
        funcs = getRawDataLines()
    api = parseDataLines(funcs)

    return api


def getRawDataLines():
    pages = cache_retr('pages')
    if pages is not None:
        print("using cached `pages`: %s" % repr(pages)[:20])

    else:
        print("no cache, pulling pages from source...")
        sess = requests.session()

        # get all 1500+ urls and downselect them to functions 
        urls = getAllFrontUrls(sess)
        pages = [sess.get(BASE_URL + url) for url in urls]

        # store the cache in /tmp
        cache_store('pages', pages)

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
    funcs = [line[10:] for line in functext]
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
        for chunk in argchunks:
            chunk = [foo.strip() for foo in chunk if len(foo.strip())]
            if len(chunk):
                if chunk[-1].endswith(')'):
                    aname = None
                else:
                    aname = chunk.pop()

                # handle variadic args (...):
                if aname in ('...', b'\xe2\x80\xa6'.decode('utf8')):
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

        api['plt_%s' % funcname] = (rettype, None, 'cdecl', '*.%s' % funcname, tuple(argout))

    return api



def reprAllFuncProtos(funcs=None):
    api = getAllFuncProtos(funcs)
    keys = list(api.keys())
    keys.sort()

    out = ['api = {']
    for key in keys:
        data = api.get(key)
        out.append("    %r: %r," % (key, data)
                )
    out.append('}')
    return '\n'.join(out)

def writeAllFuncProtos():
    open('i386.py', 'w').write(reprAllFuncProtos())


if __name__ == '__main__':
    writeAllFuncProtos()
