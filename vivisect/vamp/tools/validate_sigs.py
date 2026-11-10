#!/usr/bin/env python3
"""
VAMP Signature Validator

Load a signature set and test it against a binary that is known to
statically link that library. Reports true positives, false positives,
and missed functions.

Usage:
    python -m vivisect.vamp.tools.validate_sigs \
        --sigs glibc_2.31_x64.json \
        --test-binary ./test_binary \
        [--ground-truth symbols.txt]
"""

import argparse
import json
import logging
import os
import sys
from collections import defaultdict

import vivisect
import vivisect.vamp as v_vamp

logger = logging.getLogger(__name__)


def validate_sigs(sig_filepath, test_binary, ground_truth=None, verbose=False):
    """
    Validate a signature set against a test binary.

    Args:
        sig_filepath: path to JSON sig file
        test_binary: path to the binary to test against
        ground_truth: optional dict mapping funcva -> name (if the binary has symbols)
        verbose: enable debug logging

    Returns: validation report dict
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Load the signature set
    logger.info("Loading signatures from: %s", sig_filepath)
    tree, meta = v_vamp.loadSigSet(sig_filepath)
    sig_count = len(meta.get('signatures', []))
    # Actually count from the tree via the sigs dict
    sig_count = len(tree.sigs)
    logger.info("Loaded %d signatures for %s %s (%s/%s)",
                sig_count, meta.get('library'), meta.get('version'),
                meta.get('arch'), meta.get('platform'))

    # Load the test binary into Vivisect
    logger.info("Loading test binary: %s", test_binary)
    vw = vivisect.VivWorkspace()
    vw.loadFromFile(test_binary)
    logger.info("Analyzing test binary...")
    vw.analyze()

    functions = vw.getFunctions()
    logger.info("Test binary has %d functions", len(functions))

    # Match each function against the signature tree
    true_positives = []    # matched correctly
    false_positives = []   # matched but wrong name
    false_negatives = []   # not matched but should have been
    matches = defaultdict(list)  # sig_name -> [funcva, ...]

    for funcva in functions:
        try:
            offset, bytes_data = vw.getByteDef(funcva)
            match = tree.getSignature(bytes_data, offset=offset)
        except Exception:
            match = None

        if match is not None:
            matches[match].append(funcva)

            if ground_truth is not None:
                real_name = ground_truth.get(funcva)
                if real_name is not None:
                    # Check if the match is correct
                    # The sig name is like "glibc.printf" — extract the function part
                    match_func = match.split('.')[-1] if '.' in match else match
                    if real_name == match_func or real_name == match:
                        true_positives.append((funcva, match, real_name))
                    else:
                        false_positives.append((funcva, match, real_name))
                else:
                    # No ground truth for this function — it's an unverified match
                    true_positives.append((funcva, match, None))
            else:
                # No ground truth at all — all matches are unverified
                true_positives.append((funcva, match, None))
        else:
            if ground_truth is not None:
                real_name = ground_truth.get(funcva)
                if real_name is not None:
                    false_negatives.append((funcva, real_name))

    # Calculate metrics
    total_matches = len(true_positives) + len(false_positives)
    precision = len(true_positives) / total_matches if total_matches > 0 else 0.0
    recall = len(true_positives) / (len(true_positives) + len(false_negatives)) \
        if (len(true_positives) + len(false_negatives)) > 0 else 0.0

    report = {
        'sig_file': sig_filepath,
        'test_binary': test_binary,
        'library': meta.get('library'),
        'version': meta.get('version'),
        'arch': meta.get('arch'),
        'platform': meta.get('platform'),
        'total_functions': len(functions),
        'total_sigs': sig_count,
        'total_matches': total_matches,
        'true_positives': len(true_positives),
        'false_positives': len(false_positives),
        'false_negatives': len(false_negatives),
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'matches': {
            name: [hex(va) for va in vas]
            for name, vas in matches.items()
        },
        'false_positive_details': [
            {'va': hex(va), 'matched': m, 'actual': r}
            for va, m, r in false_positives
        ],
        'false_negative_details': [
            {'va': hex(va), 'expected': r}
            for va, r in false_negatives
        ],
    }

    return report


def load_ground_truth_from_symbols(vw):
    """
    Build a ground truth dict from a Vivisect workspace that has symbols.
    Returns: {funcva: name}
    """
    gt = {}
    for funcva in vw.getFunctions():
        name = vw.getName(funcva)
        if name and not name.startswith('sub_') and not name.startswith('loc_'):
            # Strip address suffix
            if '_' in name:
                parts = name.rsplit('_', 1)
                if parts[-1].startswith('0x') or parts[-1].isdigit():
                    name = parts[0]
            gt[funcva] = name
    return gt


def main():
    parser = argparse.ArgumentParser(
        description='VAMP Signature Validator — test sig sets against binaries')
    parser.add_argument('--sigs', '-s', required=True, help='JSON signature file to validate')
    parser.add_argument('--test-binary', '-t', required=True, help='Binary to test against')
    parser.add_argument('--ground-truth', '-g', help='Optional file with ground truth symbols (funcva:name per line)')
    parser.add_argument('--use-symbols', action='store_true',
                        help='Use symbols from the test binary as ground truth (for non-stripped test binaries)')
    parser.add_argument('--output', '-o', help='Write validation report to JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    ground_truth = None

    if args.ground_truth:
        ground_truth = {}
        with open(args.ground_truth, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(':', 1)
                if len(parts) == 2:
                    va = int(parts[0], 0)
                    ground_truth[va] = parts[1]

    elif args.use_symbols:
        # Load the binary with symbols to get ground truth, then
        # we'd need to re-load it stripped. For now, just use the symbols.
        logger.info("Loading test binary with symbols for ground truth...")
        vw = vivisect.VivWorkspace()
        vw.loadFromFile(args.test_binary)
        vw.analyze()
        ground_truth = load_ground_truth_from_symbols(vw)

    report = validate_sigs(
        sig_filepath=args.sigs,
        test_binary=args.test_binary,
        ground_truth=ground_truth,
        verbose=args.verbose,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("VAMP Signature Validation Report")
    print("=" * 60)
    print("Signature file:    %s" % report['sig_file'])
    print("Test binary:       %s" % report['test_binary'])
    print("Library:           %s %s" % (report['library'], report['version']))
    print("Arch/Platform:     %s / %s" % (report['arch'], report['platform']))
    print("-" * 60)
    print("Total functions:   %d" % report['total_functions'])
    print("Total sigs:        %d" % report['total_sigs'])
    print("Total matches:     %d" % report['total_matches'])
    print("True positives:    %d" % report['true_positives'])
    print("False positives:   %d" % report['false_positives'])
    print("False negatives:   %d" % report['false_negatives'])
    print("-" * 60)
    print("Precision:         %.2f%%" % (report['precision'] * 100))
    print("Recall:            %.2f%%" % (report['recall'] * 100))
    print("=" * 60)

    if report['false_positive_details']:
        print("\nFalse Positives:")
        for fp in report['false_positive_details'][:20]:
            print("  %s: matched=%s, actual=%s" % (fp['va'], fp['matched'], fp['actual']))
        if len(report['false_positive_details']) > 20:
            print("  ... and %d more" % (len(report['false_positive_details']) - 20))

    if report['false_negative_details']:
        print("\nFalse Negatives (missed functions):")
        for fn in report['false_negative_details'][:20]:
            print("  %s: expected=%s" % (fn['va'], fn['expected']))
        if len(report['false_negative_details']) > 20:
            print("  ... and %d more" % (len(report['false_negative_details']) - 20))

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print("\nReport written to: %s" % args.output)


if __name__ == '__main__':
    main()