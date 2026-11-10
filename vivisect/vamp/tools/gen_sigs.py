#!/usr/bin/env python3
"""
VAMP Signature Generator

Load a dynamically-linked library binary (or static archive) into Vivisect,
run analysis, and generate VAMP signatures for all named functions.

Usage:
    python -m vivisect.vamp.tools.gen_sigs \
        --input libc.so.6 \
        --library glibc \
        --version 2.31 \
        --arch amd64 \
        --platform linux \
        --compiler gcc-9.4.0 \
        --output glibc_2.31_x64.json

    # Batch mode: generate sigs for multiple binaries
    python -m vivisect.vamp.tools.gen_sigs \
        --input-dir /path/to/libs/ \
        --library glibc \
        --version 2.31 \
        --output-dir vamp/data/
"""

import argparse
import hashlib
import logging
import os
import sys
import time

import vivisect
import vivisect.vamp as v_vamp

logger = logging.getLogger(__name__)


def compute_sha256(filepath):
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def generate_sigs(input_path, library, version, arch, platform_name,
                  compiler, compiled_flags='', source_url=None,
                  min_length=8, max_masked_ratio=0.50, min_confidence='low',
                  dedup=True, verbose=False):
    """
    Generate VAMP signatures from a library binary.

    Returns: a sigset dict ready for serialization.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger.info("Loading binary: %s", input_path)

    # Compute binary hash
    binary_sha256 = compute_sha256(input_path)

    # Create Vivisect workspace and load the binary
    vw = vivisect.VivWorkspace()
    vw.loadFromFile(input_path)
    vw.setMeta('Architecture', arch)

    logger.info("Analyzing binary (this may take a while)...")
    vw.analyze()

    logger.info("Analysis complete. Generating signatures...")

    # Collect all named functions
    functions = vw.getFunctions()
    logger.info("Found %d functions total", len(functions))

    signatures = []
    skipped = 0
    errors = 0

    for funcva in functions:
        # Get function name
        fname = vw.getName(funcva)
        if fname is None:
            skipped += 1
            continue

        # Skip unnamed/generated names
        if fname.startswith('sub_') or fname.startswith('loc_'):
            skipped += 1
            continue

        # Strip address suffix if present (e.g., "printf_0x1234" -> "printf")
        # but keep the full name for the sig value
        sig_name = fname

        # Prefix with library name for consistency
        if not sig_name.startswith(library + '.'):
            sig_name = '%s.%s' % (library, fname.split('.')[0] if '.' in fname else fname)

        try:
            sig_bytes, sig_mask = v_vamp.genSigAndMask(vw, funcva)
        except Exception as e:
            logger.debug("Skipping %s (0x%x): %s", fname, funcva, e)
            errors += 1
            continue

        if sig_bytes is None or len(sig_bytes) == 0:
            skipped += 1
            continue

        # Generate metadata
        meta = v_vamp.genSigMetadata(vw, funcva, sig_bytes, sig_mask)

        # Filter by quality
        if meta['first_block_size'] < min_length:
            skipped += 1
            continue
        if meta['masked_ratio'] > max_masked_ratio:
            skipped += 1
            continue

        sig_entry = {
            'name': sig_name,
            'bytes': sig_bytes.hex(),
            'mask': sig_mask.hex() if sig_mask else None,
            'func_size': meta['func_size'],
            'first_block_size': meta['first_block_size'],
            'reloc_count': meta['reloc_count'],
            'masked_ratio': meta['masked_ratio'],
            'confidence': meta['confidence'],
        }
        signatures.append(sig_entry)

    logger.info("Generated %d signatures (skipped %d, errors %d)",
                len(signatures), skipped, errors)

    # Serialize
    sigset = v_vamp.serializeSigSet(
        library=library,
        version=version,
        arch=arch,
        platform=platform_name,
        compiler=compiler,
        compiled_flags=compiled_flags,
        binary_sha256=binary_sha256,
        signatures=signatures,
        source_url=source_url,
    )

    # Deduplicate
    if dedup:
        sigset = v_vamp.dedupSigs(sigset)
        logger.info("After dedup: %d signatures", len(sigset['signatures']))
        if sigset.get('dedup_conflicts'):
            logger.info("Dedup conflicts: %d", len(sigset['dedup_conflicts']))

    return sigset


def main():
    parser = argparse.ArgumentParser(
        description='VAMP Signature Generator — generate byte/mask signatures from library binaries')
    parser.add_argument('--input', '-i', help='Input library binary (.so, .dll, .a, .dylib)')
    parser.add_argument('--input-dir', help='Directory of library binaries (batch mode)')
    parser.add_argument('--output', '-o', help='Output JSON signature file')
    parser.add_argument('--output-dir', help='Output directory for batch mode')
    parser.add_argument('--library', required=True, help='Library name (e.g., glibc, openssl)')
    parser.add_argument('--version', required=True, help='Library version (e.g., 2.31)')
    parser.add_argument('--arch', default='amd64', help='Architecture (i386, amd64, arm, aarch64)')
    parser.add_argument('--platform', default='linux', help='Platform (linux, windows, darwin, android)')
    parser.add_argument('--compiler', default='unknown', help='Compiler (e.g., gcc-9.4.0)')
    parser.add_argument('--flags', default='', help='Compilation flags (e.g., -O2 -fPIC)')
    parser.add_argument('--source-url', help='URL to the source/binary archive')
    parser.add_argument('--min-length', type=int, default=8, help='Minimum signature length in bytes')
    parser.add_argument('--max-masked', type=float, default=0.50, help='Maximum masked byte ratio (0.0-1.0)')
    parser.add_argument('--min-confidence', default='low', choices=['low', 'medium', 'high'],
                        help='Minimum confidence level')
    parser.add_argument('--no-dedup', action='store_true', help='Skip deduplication')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    if not args.input and not args.input_dir:
        parser.error("Must specify --input or --input-dir")
    if args.input and not args.output:
        parser.error("Must specify --output when using --input")
    if args.input_dir and not args.output_dir:
        parser.error("Must specify --output-dir when using --input-dir")

    if args.input:
        # Single file mode
        sigset = generate_sigs(
            input_path=args.input,
            library=args.library,
            version=args.version,
            arch=args.arch,
            platform_name=args.platform,
            compiler=args.compiler,
            compiled_flags=args.flags,
            source_url=args.source_url,
            min_length=args.min_length,
            max_masked_ratio=args.max_masked,
            min_confidence=args.min_confidence,
            dedup=not args.no_dedup,
            verbose=args.verbose,
        )
        v_vamp.saveSigSet(args.output, sigset)
        print("Wrote %d signatures to %s" % (len(sigset['signatures']), args.output))

    if args.input_dir:
        # Batch mode
        if not os.path.isdir(args.input_dir):
            parser.error("Input directory does not exist: %s" % args.input_dir)

        os.makedirs(args.output_dir, exist_ok=True)
        count = 0
        for fname in sorted(os.listdir(args.input_dir)):
            if fname.startswith('.'):
                continue
            fpath = os.path.join(args.input_dir, fname)
            if not os.path.isfile(fpath):
                continue

            # Generate output filename
            outname = '%s_%s_%s_%s.json' % (args.library, args.version, args.arch, args.platform)
            outpath = os.path.join(args.output_dir, outname)

            try:
                sigset = generate_sigs(
                    input_path=fpath,
                    library=args.library,
                    version=args.version,
                    arch=args.arch,
                    platform_name=args.platform,
                    compiler=args.compiler,
                    compiled_flags=args.flags,
                    source_url=args.source_url,
                    min_length=args.min_length,
                    max_masked_ratio=args.max_masked,
                    min_confidence=args.min_confidence,
                    dedup=not args.no_dedup,
                    verbose=args.verbose,
                )
                v_vamp.saveSigSet(outpath, sigset)
                print("Wrote %d signatures to %s" % (len(sigset['signatures']), outpath))
                count += 1
            except Exception as e:
                print("ERROR processing %s: %s" % (fname, e), file=sys.stderr)
                continue

        print("Processed %d files" % count)

        # Update index
        index = v_vamp.updateSigSetIndex(args.output_dir)
        print("Updated index: %d sig sets" % len(index.get('sig_sets', [])))


if __name__ == '__main__':
    main()