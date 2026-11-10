#!/usr/bin/env python3
"""
VAMP Signature Diff Tool

Compare two signature sets (e.g., glibc 2.27 vs 2.31) to identify
which function signatures are stable across versions and which have
changed. This helps identify:

- Stable functions: identical sig across versions (good for universal sigs)
- Changed functions: sig differs but name is the same (need per-version sigs)
- Added functions: new in the newer version
- Removed functions: gone from the newer version

Usage:
    python -m vivisect.vamp.tools.sig_diff \
        --old glibc_2.27_x64.json \
        --new glibc_2.31_x64.json \
        [--output diff_report.json]
"""

import argparse
import json
import logging
import os
import sys

import vivisect.vamp as v_vamp

logger = logging.getLogger(__name__)


def diff_sig_sets(old_path, new_path):
    """
    Compare two JSON signature files.

    Returns: diff report dict
    """
    # Load both sig sets
    with open(old_path, 'r') as f:
        old_data = json.load(f)
    with open(new_path, 'r') as f:
        new_data = json.load(f)

    old_lib = old_data.get('library', 'unknown')
    new_lib = new_data.get('library', 'unknown')
    old_ver = old_data.get('version', 'unknown')
    new_ver = new_data.get('version', 'unknown')

    logger.info("Comparing %s %s vs %s %s", old_lib, old_ver, new_lib, new_ver)

    # Build name -> sig maps
    old_sigs = {}
    for sig in old_data.get('signatures', []):
        old_sigs[sig['name']] = sig

    new_sigs = {}
    for sig in new_data.get('signatures', []):
        new_sigs[sig['name']] = sig

    old_names = set(old_sigs.keys())
    new_names = set(new_sigs.keys())

    # Categorize
    common_names = old_names & new_names
    added_names = new_names - old_names
    removed_names = old_names - new_names

    # Among common names, check if the sig is identical or changed
    stable = []      # identical bytes+mask
    changed = []     # different bytes or mask

    for name in common_names:
        old_sig = old_sigs[name]
        new_sig = new_sigs[name]

        old_bytes = old_sig.get('bytes', '')
        new_bytes = new_sig.get('bytes', '')
        old_mask = old_sig.get('mask', '') or ''
        new_mask = new_sig.get('mask', '') or ''

        if old_bytes == new_bytes and old_mask == new_mask:
            stable.append(name)
        else:
            changed.append({
                'name': name,
                'old_bytes': old_bytes,
                'new_bytes': new_bytes,
                'old_mask': old_mask,
                'new_mask': new_mask,
                'old_first_block_size': old_sig.get('first_block_size', 0),
                'new_first_block_size': new_sig.get('first_block_size', 0),
                'old_confidence': old_sig.get('confidence', 'unknown'),
                'new_confidence': new_sig.get('confidence', 'unknown'),
            })

    # Compute stability metrics
    total_common = len(common_names)
    stable_count = len(stable)
    changed_count = len(changed)
    stability_rate = stable_count / total_common if total_common > 0 else 0.0

    report = {
        'old_file': old_path,
        'new_file': new_path,
        'old_library': old_lib,
        'old_version': old_ver,
        'new_library': new_lib,
        'new_version': new_ver,
        'old_sig_count': len(old_sigs),
        'new_sig_count': len(new_sigs),
        'common_functions': total_common,
        'stable_functions': stable_count,
        'changed_functions': changed_count,
        'added_functions': len(added_names),
        'removed_functions': len(removed_names),
        'stability_rate': round(stability_rate, 4),
        'stable': sorted(stable),
        'changed': changed,
        'added': sorted(added_names),
        'removed': sorted(removed_names),
    }

    return report


def print_report(report):
    """Print a human-readable diff report."""
    print("\n" + "=" * 70)
    print("VAMP Signature Diff Report")
    print("=" * 70)
    print("Old: %s %s (%d sigs)" % (report['old_library'], report['old_version'], report['old_sig_count']))
    print("New: %s %s (%d sigs)" % (report['new_library'], report['new_version'], report['new_sig_count']))
    print("-" * 70)
    print("Common functions:   %d" % report['common_functions'])
    print("  Stable (identical): %d (%.1f%%)" % (
        report['stable_functions'],
        report['stability_rate'] * 100 if report['common_functions'] > 0 else 0))
    print("  Changed:            %d" % report['changed_functions'])
    print("Added functions:    %d" % report['added_functions'])
    print("Removed functions:  %d" % report['removed_functions'])
    print("-" * 70)
    print("Stability rate:     %.2f%%" % (report['stability_rate'] * 100))
    print("=" * 70)

    if report['changed']:
        print("\nChanged Functions (first 20):")
        for c in report['changed'][:20]:
            print("  %s" % c['name'])
            print("    old: %d bytes, %s confidence" % (c['old_first_block_size'], c['old_confidence']))
            print("    new: %d bytes, %s confidence" % (c['new_first_block_size'], c['new_confidence']))
        if len(report['changed']) > 20:
            print("  ... and %d more" % (len(report['changed']) - 20))

    if report['added']:
        print("\nAdded Functions (first 20):")
        for name in report['added'][:20]:
            print("  + %s" % name)
        if len(report['added']) > 20:
            print("  ... and %d more" % (len(report['added']) - 20))

    if report['removed']:
        print("\nRemoved Functions (first 20):")
        for name in report['removed'][:20]:
            print("  - %s" % name)
        if len(report['removed']) > 20:
            print("  ... and %d more" % (len(report['removed']) - 20))


def main():
    parser = argparse.ArgumentParser(
        description='VAMP Signature Diff — compare sig sets across versions')
    parser.add_argument('--old', '-o', required=True, help='Older version JSON sig file')
    parser.add_argument('--new', '-n', required=True, help='Newer version JSON sig file')
    parser.add_argument('--output', help='Write diff report to JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not os.path.isfile(args.old):
        parser.error("Old sig file not found: %s" % args.old)
    if not os.path.isfile(args.new):
        parser.error("New sig file not found: %s" % args.new)

    report = diff_sig_sets(args.old, args.new)
    print_report(report)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print("\nReport written to: %s" % args.output)


if __name__ == '__main__':
    main()