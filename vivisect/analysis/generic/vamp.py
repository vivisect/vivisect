"""
Generic VAMP signature analysis module.

This module checks each function against all loaded VAMP signature sets
(not just MSVC) and marks matches as thunks with the signature name.

Unlike vivisect.analysis.ms.msvc which only checks MSVC sigs, this module
auto-loads all JSON sig sets from vamp/data/ that match the workspace's
architecture and platform.

Matching uses multi-factor scoring:
  1. Most unmasked bytes (most specific match wins)
  2. Confidence level (high > medium > low)
  3. Function size match (bonus if sig func_size matches target)

Alias resolution: functions with identical masked byte sequences (e.g.,
__new_pclose = pclose) are all returned as potential matches.
"""

import logging
import os
import binascii
import json

import envi.bytesig as e_bytesig

import vivisect.vamp as v_vamp

logger = logging.getLogger(__name__)

# Cache: (arch, platform) -> (SignatureTree, sig_metadata_list)
_sigtree_cache = {}

# Confidence ranking for scoring
_CONF_RANK = {'high': 3, 'medium': 2, 'low': 1}


def _arch_matches(sig_arch, vw_arch):
    """Check if a signature set's architecture matches the workspace's."""
    if not sig_arch or not vw_arch:
        return True  # Be permissive if either is unknown

    # Normalize architecture names
    arch_aliases = {
        'i386': {'i386', 'x86', 'ia32', 'i486', 'i586', 'i686'},
        'amd64': {'amd64', 'x64', 'x86_64', 'x86-64'},
        'arm': {'arm', 'arm32', 'aarch32'},
        'aarch64': {'aarch64', 'arm64'},
    }

    sig_arch_lower = sig_arch.lower()
    vw_arch_lower = vw_arch.lower()

    if sig_arch_lower == vw_arch_lower:
        return True

    for canonical, aliases in arch_aliases.items():
        if sig_arch_lower in aliases and vw_arch_lower in aliases:
            return True

    return False


def _get_sigtree(arch, platform):
    """
    Load and cache all matching sig sets for the given arch/platform.

    Returns a tuple of (SignatureTree, sig_metadata_dict) where
    sig_metadata_dict maps sig_name -> {confidence, func_size, masked_ratio,
    unmasked_count, library}.
    """
    cache_key = (arch, platform)
    if cache_key in _sigtree_cache:
        return _sigtree_cache[cache_key]

    tree = e_bytesig.SignatureTree()
    sig_meta = {}  # name -> metadata dict
    loaded = 0

    data_dir = os.path.join(os.path.dirname(v_vamp.__file__), 'data')
    if os.path.isdir(data_dir):
        for fname in sorted(os.listdir(data_dir)):
            if not fname.endswith('.json') or fname == 'index.json':
                continue
            filepath = os.path.join(data_dir, fname)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                sig_arch = data.get('arch', '')
                sig_platform = data.get('platform', '')
                if not _arch_matches(sig_arch, arch):
                    continue
                if platform and sig_platform and sig_platform != platform:
                    continue

                library = data.get('library', '')
                for sig in data.get('signatures', []):
                    bytez = binascii.unhexlify(sig['bytes'])
                    mask_str = sig.get('mask')
                    if mask_str:
                        mask = binascii.unhexlify(mask_str)
                    else:
                        mask = None

                    name = sig['name']
                    unmasked_count = sum(1 for b in (mask or b'\xff' * len(bytez)) if b != 0)

                    tree.addSignature(bytez, masks=mask, val=name)

                    sig_meta[name] = {
                        'confidence': sig.get('confidence', 'low'),
                        'func_size': sig.get('func_size', 0),
                        'masked_ratio': sig.get('masked_ratio', 1.0),
                        'unmasked_count': unmasked_count,
                        'library': library,
                    }
                loaded += 1
            except Exception:
                continue

    logger.debug("Loaded %d sig sets for arch=%s platform=%s", loaded, arch, platform)
    result = (tree, sig_meta)
    _sigtree_cache[cache_key] = result
    return result


def _get_all_matches(tree, bytes_data, offset):
    """
    Get ALL matching signatures from the tree, not just the first one.

    Returns a list of (sig_name, sig_bytes, sig_masks) tuples.
    """
    matches = []
    node = tree.basenode
    while True:
        depth, sigs, choices, term = node
        matches.extend(term)
        if len(sigs) == 1:
            sbytes, smasks, sobj = sigs[0]
            is_match = True
            for i in range(depth, len(sbytes)):
                realoff = offset + i
                if realoff >= len(bytes_data):
                    is_match = False
                    break
                masked = bytes_data[realoff] & smasks[i]
                if masked != sbytes[i]:
                    is_match = False
                    break
            if is_match:
                matches.append(sigs[0])
            break

        node = None
        for sig in sigs:
            sbytes, smasks, sobj = sig
            if offset + depth >= len(bytes_data):
                continue
            masked = bytes_data[offset + depth] & smasks[depth]
            if sbytes[depth] == masked:
                node = choices[masked]
                break

        if node is None:
            break

    return matches


def _score_match(sig_name, sig_meta, func_size):
    """
    Score a match by: unmasked bytes (desc), confidence (desc), func_size match.

    Returns a tuple suitable for sorting (higher = better).
    """
    meta = sig_meta.get(sig_name, {})
    unmasked = meta.get('unmasked_count', 0)
    conf = _CONF_RANK.get(meta.get('confidence', 'low'), 1)
    sig_fsize = meta.get('func_size', 0)
    size_bonus = 1 if (func_size > 0 and sig_fsize > 0 and sig_fsize == func_size) else 0
    return (unmasked, conf, size_bonus)


def analyzeFunction(vw, funcva):
    """
    Check a function against all loaded VAMP signature sets.
    If a match is found, mark the function as a thunk and name it.

    Uses multi-factor scoring to pick the best match when multiple
    sigs match the same function.
    """
    arch = vw.getMeta('Architecture', '')
    platform = vw.getMeta('Platform', '')

    tree, sig_meta = _get_sigtree(arch, platform)
    if not tree.sigs:
        return

    # Get function size for scoring
    func_size = 0
    try:
        func_size = vw.getFunctionSize(funcva)
    except Exception:
        pass

    offset, bytes_data = vw.getByteDef(funcva)

    # Get ALL matches (not just first)
    matches = _get_all_matches(tree, bytes_data, offset)
    if not matches:
        return

    # Score each match and pick the best
    best_match = None
    best_score = (-1, -1, -1)
    for sbytes, smasks, sobj in matches:
        score = _score_match(sobj, sig_meta, func_size)
        if score > best_score:
            best_score = score
            best_match = sobj

    if best_match is not None:
        fname = best_match.split(".")[-1]
        vw.makeName(funcva, "%s_%.8x" % (fname, funcva), filelocal=True)
        vw.makeFunctionThunk(funcva, best_match)


def analyze(vw):
    """
    Workspace-level analysis entry point.
    Called during the analysis pass to initialize the VAMP sig module.
    """
    arch = vw.getMeta('Architecture', '')
    platform = vw.getMeta('Platform', '')
    logger.info("VAMP generic analysis: loading sigs for arch=%s platform=%s", arch, platform)
    # Pre-load the sig tree
    tree, sig_meta = _get_sigtree(arch, platform)
    logger.info("VAMP generic analysis: %d signatures loaded", len(tree.sigs))