import bs4
import requests
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
    sess = requests.session()

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
    funcs = [line[10:] for line in functext]
    return funcs

def parseDataLines(funcs):
    # parse each line and populate the api dict
    api = {}
    for func in funcs:
        func = func.replace("*", "* ")
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
