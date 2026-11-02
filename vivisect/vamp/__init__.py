"""
Vamp is a function/codeblock signaturing framework which is
a subcomponent of vivisect.  These may be used to import/export
signature sets and potentially identify code reuse or static
linking...

Current signature ideas:
    function arg count
    code block count
    globals refs
    code block refs
    unusual instruction use
    odd immediates
    import calls
    other signature calls
    certianty index
    Exception handling

    There will be function characteristics and code-block
    characteristics...

NOTE: Initial signature code consists entirely of the envi
bytesig module and byte/mask sets for known function signatures.
"""

import binascii
import json
import os
import time

import envi.bytesig as e_bytesig

import vivisect.const as v_const

# Format version for JSON signature files
SIG_FORMAT_VERSION = 1

# Package-level data directory (for bundled MSVC sigs only)
_PACKAGE_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def getSigDataDirs():
    """
    Determine the VAMP signature data directories using a search order.

    VAMP_SIG_DIR may contain a colon-separated list of directories
    (PATH-style). All existing directories are returned, in order.

    Search order:
    1. VAMP_SIG_DIR environment variable (colon-separated, each dir must exist)
    2. ~/.viv/vamp-sigs/data/ (default user directory, if it exists)
    3. vivisect/vamp/data/ (package-level, always included for bundled MSVC sigs)

    Returns: list of existing directory paths. The package-level directory is
    always included as the last entry (even if empty — it may contain bundled
    sigs or just a README).
    """
    dirs = []

    # 1. Environment variable (colon-separated, PATH-style)
    env_val = os.environ.get('VAMP_SIG_DIR')
    if env_val:
        for d in env_val.split(':'):
            d = d.strip()
            if d and os.path.isdir(d) and d not in dirs:
                dirs.append(d)

    # 2. Default user directory: ~/.viv/vamp-sigs/data/
    home_dir = os.path.expanduser('~/.viv/vamp-sigs/data')
    if os.path.isdir(home_dir) and home_dir not in dirs:
        dirs.append(home_dir)

    # 3. Package-level fallback (bundled MSVC sigs) — always included
    if _PACKAGE_DATA_DIR not in dirs:
        dirs.append(_PACKAGE_DATA_DIR)

    return dirs


def getSigDataDir():
    """
    Backward-compat shim: returns the first data directory.
    Use getSigDataDirs() for multi-directory support.
    """
    dirs = getSigDataDirs()
    return dirs[0] if dirs else _PACKAGE_DATA_DIR


def genSigAndMask(vw, funcva):
    """
    Generate an envi bytesig signature and mask for the given
    function block.  This will properly mask off relocations
    if present.
    """

    fsize = 0
    if funcva not in vw.getFunctions():
        funcva = vw.getFunction(funcva)
        if funcva is None:
            raise Exception('Given funcva not a function or within a known function')
    func_blocks = [cbva for cbva, _, _ in vw.getFunctionBlocks(funcva)]
    # Figure out the size of the first linear chunk
    # in this function...
    cb = vw.getCodeBlock(funcva)
    if cb[v_const.CB_VA] not in func_blocks:
        raise Exception("funcva not in given func")
    while cb is not None:
        cbva, cbsize, cbfunc = cb
        if cbfunc != funcva:
            break
        fsize += cbsize
        cb = vw.getCodeBlock(cbva + cbsize)

    if fsize == 0:
        raise Exception("0 length function??!?1")

    bytez = vw.readMemory(funcva, fsize)

    sig = b""
    mask = b""
    i = 0
    while i < fsize:
        rtype = vw.getRelocation(funcva + i)
        if rtype is None:
            sig += bytez[i:i + 1]
            mask += b"\xff"
            i += 1
        elif rtype == v_const.RTYPE_BASERELOC:
            x = b"\x00" * vw.psize
            sig += x
            mask += x
            i += vw.psize
        else:
            raise Exception("Unhandled Reloc Type: %d" % rtype)

    return sig, mask


def genSigMetadata(vw, funcva, sig, mask):
    """
    Generate metadata about a signature for confidence scoring.

    Returns a dict with:
        func_size: total size of the function
        first_block_size: size of the first linear code block
        reloc_count: number of relocation slots masked out
        masked_ratio: fraction of bytes that are masked (0.0-1.0)
        confidence: 'high', 'medium', or 'low'
    """
    fsize = 0
    if funcva not in vw.getFunctions():
        funcva = vw.getFunction(funcva)

    # Get total function size
    for cbva, cbsize, cbfunc in vw.getFunctionBlocks(funcva):
        fsize += cbsize

    first_block_size = len(sig)
    reloc_count = sum(1 for b in mask if b == 0)
    masked_bytes = sum(1 for b in mask if b == 0)
    masked_ratio = masked_bytes / first_block_size if first_block_size > 0 else 1.0

    # Confidence scoring
    if first_block_size >= 16 and masked_ratio < 0.25:
        confidence = 'high'
    elif first_block_size >= 8 and masked_ratio < 0.50:
        confidence = 'medium'
    else:
        confidence = 'low'

    return {
        'func_size': fsize,
        'first_block_size': first_block_size,
        'reloc_count': reloc_count,
        'masked_ratio': round(masked_ratio, 4),
        'confidence': confidence,
    }


def serializeSigSet(library, version, arch, platform, compiler,
                    compiled_flags, binary_sha256, signatures,
                    source_url=None, generated_by='vamp-gen-sigs'):
    """
    Serialize a set of signatures into a JSON-serializable dict.

    Each entry in *signatures* should be a dict with keys:
        name, bytes (hex str), mask (hex str),
        func_size, first_block_size, reloc_count, confidence
    """
    return {
        'format_version': SIG_FORMAT_VERSION,
        'library': library,
        'version': version,
        'arch': arch,
        'platform': platform,
        'compiler': compiler,
        'compiled_flags': compiled_flags,
        'source_url': source_url,
        'binary_sha256': binary_sha256,
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'generated_by': generated_by,
        'signatures': signatures,
    }


def saveSigSet(filepath, sigset):
    """
    Write a signature set dict to a JSON file.
    """
    d = os.path.dirname(filepath)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(sigset, f, indent=2, sort_keys=False)
    return filepath


def loadSigSet(filepath):
    """
    Load a JSON signature file and return a populated SignatureTree
    along with the metadata dict.

    Returns: (SignatureTree, metadata_dict)
    """
    with open(filepath, 'r') as f:
        data = json.load(f)

    if data.get('format_version') != SIG_FORMAT_VERSION:
        raise ValueError(
            "Unsupported signature format version: %r (expected %d)" %
            (data.get('format_version'), SIG_FORMAT_VERSION))

    tree = e_bytesig.SignatureTree()
    for sig in data['signatures']:
        bytez = binascii.unhexlify(sig['bytes'])
        mask = binascii.unhexlify(sig['mask']) if sig.get('mask') else None
        tree.addSignature(bytez, masks=mask, val=sig['name'])

    metadata = {k: v for k, v in data.items() if k != 'signatures'}
    return tree, metadata


def loadAllSigSets(data_dir=None):
    """
    Load all JSON signature files from the data directory(ies).

    If data_dir is None, searches all directories from getSigDataDirs().
    If data_dir is a string, searches only that directory.
    If data_dir is a list, searches each directory in the list.

    Returns: list of (SignatureTree, metadata_dict, filepath) tuples
    """
    if data_dir is None:
        data_dirs = getSigDataDirs()
    elif isinstance(data_dir, str):
        data_dirs = [data_dir]
    elif isinstance(data_dir, list):
        data_dirs = data_dir
    else:
        data_dirs = [data_dir]

    results = []
    seen_files = set()
    for data_dir in data_dirs:
        if not os.path.isdir(data_dir):
            continue
        for fname in sorted(os.listdir(data_dir)):
            if not fname.endswith('.json'):
                continue
            if fname == 'index.json':
                continue
            filepath = os.path.join(data_dir, fname)
            # Skip duplicate files (same path seen in an earlier dir)
            if filepath in seen_files:
                continue
            seen_files.add(filepath)
            try:
                tree, meta = loadSigSet(filepath)
                results.append((tree, meta, filepath))
            except Exception as e:
                # Skip files that fail to load — don't crash the whole pipeline
                continue

    return results


def loadSigSetIndex(data_dir=None):
    """
    Load the master index file(s) from the data directory(ies).

    If data_dir is None, merges index.json from all directories in
    getSigDataDirs(). If data_dir is specified, loads only that directory's
    index.

    Returns: dict with 'sig_sets' list (merged from all directories),
    or empty dict if no index exists anywhere.
    """
    if data_dir is None:
        data_dirs = getSigDataDirs()
    elif isinstance(data_dir, str):
        data_dirs = [data_dir]
    elif isinstance(data_dir, list):
        data_dirs = data_dir
    else:
        data_dirs = [data_dir]

    merged = {'sig_sets': [], 'sig_set_count': 0, 'total_signatures': 0}
    seen_files = set()

    for data_dir in data_dirs:
        index_path = os.path.join(data_dir, 'index.json')
        if not os.path.isfile(index_path):
            continue
        try:
            with open(index_path, 'r') as f:
                idx = json.load(f)
        except Exception:
            continue
        for entry in idx.get('sig_sets', []):
            fname = entry.get('file', '')
            if fname in seen_files:
                continue
            seen_files.add(fname)
            merged['sig_sets'].append(entry)
        merged['sig_set_count'] = len(merged['sig_sets'])
        merged['total_signatures'] += idx.get('total_signatures', 0)

    return merged


def updateSigSetIndex(data_dir=None):
    """
    Scan the data directory for all .json sig files (excluding index.json)
    and rebuild the master index file.

    Returns: the index dict that was written.
    """
    if data_dir is None:
        data_dir = getSigDataDir()

    sig_sets = []
    if os.path.isdir(data_dir):
        for fname in sorted(os.listdir(data_dir)):
            if not fname.endswith('.json') or fname == 'index.json':
                continue
            filepath = os.path.join(data_dir, fname)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                if data.get('format_version') != SIG_FORMAT_VERSION:
                    continue
                sig_sets.append({
                    'id': '%s_%s_%s_%s_%s' % (
                        data.get('library', 'unknown'),
                        data.get('version', '0'),
                        data.get('arch', 'unknown'),
                        data.get('platform', 'unknown'),
                        data.get('compiler', 'unknown').split('-')[0],
                    ),
                    'library': data.get('library', 'unknown'),
                    'version': data.get('version', 'unknown'),
                    'arch': data.get('arch', 'unknown'),
                    'platform': data.get('platform', 'unknown'),
                    'compiler': data.get('compiler', 'unknown'),
                    'file': fname,
                    'sig_count': len(data.get('signatures', [])),
                })
            except Exception:
                continue

    index = {
        'format_version': SIG_FORMAT_VERSION,
        'updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'sig_sets': sig_sets,
    }

    os.makedirs(data_dir, exist_ok=True)
    index_path = os.path.join(data_dir, 'index.json')
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)

    return index


def filterSigs(sigset, min_length=8, max_masked_ratio=0.50,
               min_confidence='low'):
    """
    Filter signatures in a sigset dict by quality criteria.

    Args:
        sigset: a sigset dict (as produced by serializeSigSet)
        min_length: minimum first_block_size in bytes
        max_masked_ratio: maximum fraction of masked bytes allowed
        min_confidence: 'low', 'medium', or 'high' — drop anything below

    Returns: a new sigset dict with filtered signatures.
    """
    confidence_order = {'low': 0, 'medium': 1, 'high': 2}
    min_conf_val = confidence_order.get(min_confidence, 0)

    filtered = []
    for sig in sigset.get('signatures', []):
        if sig.get('first_block_size', 0) < min_length:
            continue
        if sig.get('masked_ratio', 0) > max_masked_ratio:
            continue
        if confidence_order.get(sig.get('confidence', 'low'), 0) < min_conf_val:
            continue
        filtered.append(sig)

    result = dict(sigset)
    result['signatures'] = filtered
    return result


def dedupSigs(sigset):
    """
    Remove duplicate signatures (same bytes+mask) from a sigset dict.
    If two sigs have the same bytes+mask but different names, keep the
    first occurrence and log the conflict in a 'dedup_conflicts' field.

    Returns: a new sigset dict with duplicates removed.
    """
    seen = {}
    unique = []
    conflicts = []

    for sig in sigset.get('signatures', []):
        key = sig['bytes'] + (sig.get('mask') or '')
        if key in seen:
            conflicts.append({
                'bytes': sig['bytes'],
                'name1': seen[key],
                'name2': sig['name'],
            })
            continue
        seen[key] = sig['name']
        unique.append(sig)

    result = dict(sigset)
    result['signatures'] = unique
    if conflicts:
        result['dedup_conflicts'] = conflicts
    return result