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

# Directory containing JSON signature databases
_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


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
    Load all JSON signature files from the data directory.

    Returns: list of (SignatureTree, metadata_dict, filepath) tuples
    """
    if data_dir is None:
        data_dir = _DATA_DIR

    results = []
    if not os.path.isdir(data_dir):
        return results

    for fname in sorted(os.listdir(data_dir)):
        if not fname.endswith('.json'):
            continue
        if fname == 'index.json':
            continue
        filepath = os.path.join(data_dir, fname)
        try:
            tree, meta = loadSigSet(filepath)
            results.append((tree, meta, filepath))
        except Exception as e:
            # Skip files that fail to load — don't crash the whole pipeline
            continue

    return results


def loadSigSetIndex(data_dir=None):
    """
    Load the master index file (data/index.json) if it exists.

    Returns: dict with 'sig_sets' list, or empty dict if no index exists.
    """
    if data_dir is None:
        data_dir = _DATA_DIR

    index_path = os.path.join(data_dir, 'index.json')
    if not os.path.isfile(index_path):
        return {}

    with open(index_path, 'r') as f:
        return json.load(f)


def updateSigSetIndex(data_dir=None):
    """
    Scan the data directory for all .json sig files (excluding index.json)
    and rebuild the master index file.

    Returns: the index dict that was written.
    """
    if data_dir is None:
        data_dir = _DATA_DIR

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