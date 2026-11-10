#!/usr/bin/env python3
"""
VAMP Weekly Sig Scanner

Scans Ubuntu package archives for newer versions of tracked libraries,
downloads them, generates VAMP signatures, and pushes updates to the
vamp-sigs repository (https://github.com/atlas0fd00m/vamp-sigs).

This script is designed to run as a weekly cron job. It:
1. Checks the Ubuntu package archive for new versions of tracked libraries
2. Downloads any new/updated .deb packages
3. Generates VAMP sigs using gen_elf_sigs.py
4. Commits changes to a new branch on the fork (aragorn-1337/vamp-sigs)
5. Pushes the branch (PR link printed for manual creation)

Usage:
    python3 vivisect/vamp/tools/vamp_scan_weekly.py [--dry-run]
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

# --- Configuration ---

# Repos — sigs live in the separate vamp-sigs repo, not vivisect
SIGS_FORK_REPO = 'git@github.com:aragorn-1337/vamp-sigs.git'
SIGS_UPSTREAM_REPO = 'https://github.com/atlas0fd00m/vamp-sigs.git'
BRANCH_PREFIX = 'vamp-sig-update'

# Package archive URLs
SECURITY_URL = 'http://security.ubuntu.com/ubuntu/pool/main'
ARCHIVE_URL = 'http://archive.ubuntu.com/ubuntu/pool/main'
PORTS_URL = 'http://ports.ubuntu.com/ubuntu-ports/pool/main'

# Libraries to track: (source_dir, pkg_pattern, deb_arch, vamp_arch, platform, library_name, base_url)
TRACKED_LIBS = [
    # glibc x64
    ('g/glibc', 'libc6', 'amd64', 'amd64', 'linux', 'glibc', SECURITY_URL),
    # glibc i386 (libc6-i386 is a multiarch package on amd64)
    ('g/glibc', 'libc6-i386', 'amd64', 'i386', 'linux', 'glibc', SECURITY_URL),
    # glibc arm64
    ('g/glibc', 'libc6', 'arm64', 'aarch64', 'linux', 'glibc', PORTS_URL),
    # glibc armhf
    ('g/glibc', 'libc6', 'armhf', 'arm', 'linux', 'glibc', PORTS_URL),
    # musl x64
    ('m/musl', 'musl', 'amd64', 'amd64', 'linux', 'musl', ARCHIVE_URL),
    # OpenSSL x64 (try libssl3t64 for 24.04, fallback to libssl3)
    ('o/openssl', 'libssl3t64', 'amd64', 'amd64', 'linux', 'openssl', SECURITY_URL),
    ('o/openssl', 'libssl3', 'amd64', 'amd64', 'linux', 'openssl', SECURITY_URL),
    # OpenSSL arm64
    ('o/openssl', 'libssl3t64', 'arm64', 'aarch64', 'linux', 'openssl', PORTS_URL),
    # zlib
    ('z/zlib', 'zlib1g', 'amd64', 'amd64', 'linux', 'zlib', SECURITY_URL),
    # zstd
    ('z/zstd', 'libzstd1', 'amd64', 'amd64', 'linux', 'zstd', SECURITY_URL),
    # SQLite
    ('s/sqlite3', 'libsqlite3-0', 'amd64', 'amd64', 'linux', 'sqlite', SECURITY_URL),
    # libcurl
    ('c/curl', 'libcurl4', 'amd64', 'amd64', 'linux', 'libcurl', SECURITY_URL),
    # liblzma
    ('x/xz-utils', 'liblzma5', 'amd64', 'amd64', 'linux', 'liblzma', SECURITY_URL),
    # libbz2
    ('b/bzip2', 'libbz2-1.0', 'amd64', 'amd64', 'linux', 'libbz2', SECURITY_URL),
    # liblz4
    ('l/lz4', 'liblz4-1', 'amd64', 'amd64', 'linux', 'liblz4', SECURITY_URL),
    # snappy
    ('s/snappy', 'libsnappy1v5', 'amd64', 'amd64', 'linux', 'snappy', ARCHIVE_URL),
]

# Paths (computed relative to this file)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# vivisect/vamp/tools/ -> vivisect/vamp/data (bundled MSVC sigs only)
VAMP_DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
# vivisect/vamp/tools/ -> vivisect repo root
VIVISECT_REPO_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..')

# vamp-sigs repo clone (for pushing sig updates)
# Use a stable working clone alongside the vivisect repo
SIGS_REPO_DIR = os.path.expanduser('~/.viv/vamp-sigs')

# Working directory for downloads
WORK_DIR = tempfile.mkdtemp(prefix='vamp-scan-')


def fetch_package_listings(source_dir, base_url):
    """Fetch available .deb files from a package directory."""
    url = f'{base_url}/{source_dir}/'
    try:
        req = urllib.request.urlopen(url, timeout=30)
        html = req.read().decode('utf-8', errors='ignore')
        debs = re.findall(r'href="([^"]+\.deb)"', html)
        return debs
    except Exception as e:
        print(f'  ERROR fetching {url}: {e}')
        return []


def find_latest_version(debs, pkg_pattern, arch):
    """Find the latest version .deb for a given package pattern and arch."""
    matching = [d for d in debs if pkg_pattern in d and arch in d and 'dbg' not in d and 'dev' not in d]
    if not matching:
        return None
    # Sort by filename — later versions sort last
    return sorted(matching)[-1]


def download_deb(url, dest_dir):
    """Download a .deb file."""
    fname = os.path.basename(url)
    dest_path = os.path.join(dest_dir, fname)
    try:
        urllib.request.urlretrieve(url, dest_path)
        return dest_path
    except Exception as e:
        print(f'  ERROR downloading {url}: {e}')
        return None


def extract_deb(deb_path, dest_dir):
    """Extract a .deb package and find .so files."""
    os.makedirs(dest_dir, exist_ok=True)
    subprocess.run(['dpkg-deb', '-x', deb_path, dest_dir],
                   capture_output=True, timeout=60)
    so_files = []
    for root, dirs, files in os.walk(dest_dir):
        for f in files:
            if f.startswith('lib') and '.so' in f:
                so_files.append(os.path.join(root, f))
    return so_files


def generate_sigs(so_path, library, version, arch, platform, output_path):
    """Generate VAMP sigs from a .so file using gen_elf_sigs.py."""
    cmd = [
        sys.executable,
        os.path.join(SCRIPT_DIR, 'gen_elf_sigs.py'),
        '--input', so_path,
        '--library', library,
        '--version', version,
        '--arch', arch,
        '--platform', platform,
        '--output', output_path,
    ]
    # Set PYTHONPATH to repo root so gen_elf_sigs.py imports the repo-local
    # vivisect/vamp instead of any stale editable install (e.g. from /tmp).
    env = os.environ.copy()
    repo_root = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
    env['PYTHONPATH'] = repo_root + os.pathsep + env.get('PYTHONPATH', '')
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
    if result.returncode != 0:
        print(f'  gen_elf_sigs FAILED: {result.stderr[:300]}')
        return False
    return True


def get_version_from_deb_name(deb_name):
    """Extract version string from .deb filename."""
    # e.g., libc6_2.39-0ubuntu8.8_amd64.deb -> 2.39
    parts = deb_name.split('_')
    if len(parts) >= 2:
        version = parts[1].split('-')[0].split('~')[0].split('+')[0]
        return version
    return 'unknown'


def main():
    dry_run = '--dry-run' in sys.argv

    print('VAMP Weekly Sig Scanner')
    print(f'Work dir: {WORK_DIR}')
    print(f'Vivisect repo: {os.path.abspath(VIVISECT_REPO_DIR)}')
    print(f'Sigs repo: {SIGS_REPO_DIR}')
    print(f'Dry run: {dry_run}')
    print()

    # Ensure the vamp-sigs repo is cloned and up to date
    sigs_data_dir = os.path.join(SIGS_REPO_DIR, 'data')
    if not os.path.isdir(SIGS_REPO_DIR):
        print(f'Cloning vamp-sigs repo to {SIGS_REPO_DIR}...')
        clone_result = subprocess.run(
            ['git', 'clone', SIGS_FORK_REPO, SIGS_REPO_DIR],
            capture_output=True, text=True,
            env={**os.environ, 'GIT_SSH_COMMAND': 'ssh -i ~/.ssh/id_ed25519_github -o StrictHostKeyChecking=no'})
        if clone_result.returncode != 0:
            print(f'  CLONE FAILED: {clone_result.stderr[:300]}')
            return
        # Add upstream remote
        subprocess.run(['git', 'remote', 'add', 'upstream', SIGS_UPSTREAM_REPO],
                       cwd=SIGS_REPO_DIR, capture_output=True, text=True)
    else:
        # Fetch latest from upstream and update main
        print('Updating vamp-sigs repo...')
        subprocess.run(['git', 'fetch', 'upstream'], cwd=SIGS_REPO_DIR,
                       capture_output=True, text=True,
                       env={**os.environ, 'GIT_SSH_COMMAND': 'ssh -i ~/.ssh/id_ed25519_github -o StrictHostKeyChecking=no'})
        subprocess.run(['git', 'checkout', 'main'], cwd=SIGS_REPO_DIR,
                       capture_output=True, text=True)
        subprocess.run(['git', 'merge', 'upstream/main'], cwd=SIGS_REPO_DIR,
                       capture_output=True, text=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=SIGS_REPO_DIR,
                       capture_output=True, text=True,
                       env={**os.environ, 'GIT_SSH_COMMAND': 'ssh -i ~/.ssh/id_ed25519_github -o StrictHostKeyChecking=no'})

    # Load current index to see what we already have
    index_path = os.path.join(sigs_data_dir, 'index.json')
    current_versions = {}
    if os.path.exists(index_path):
        with open(index_path) as f:
            idx = json.load(f)
        for s in idx.get('sig_sets', []):
            key = (s['library'], s['arch'], s['platform'])
            current_versions[key] = s['version']

    updates = []
    seen_keys = set()

    for source_dir, pkg_pattern, deb_arch, vamp_arch, platform, library, base_url in TRACKED_LIBS:
        key = (library, vamp_arch, platform)
        if key in seen_keys:
            # Already checked a higher-priority source for this lib/arch
            continue
        print(f'Checking {library} ({pkg_pattern} {deb_arch} -> {vamp_arch}/{platform})...')
        debs = fetch_package_listings(source_dir, base_url)
        if not debs:
            continue

        latest = find_latest_version(debs, pkg_pattern, deb_arch)
        if not latest:
            print(f'  No package found for {pkg_pattern} {deb_arch}')
            continue

        version = get_version_from_deb_name(latest)

        # Check if we already have this version
        current = current_versions.get(key)
        if current and current == version:
            print(f'  Already have {library} {version} ({vamp_arch}) — skipping')
            seen_keys.add(key)
            continue

        print(f'  NEW: {library} {version} ({vamp_arch}) — was {current or "none"}')
        updates.append((library, version, vamp_arch, platform, latest, source_dir, base_url, pkg_pattern, deb_arch))
        seen_keys.add(key)

    if not updates:
        print('\nNo updates found. All sig databases are current.')
        return

    print(f'\n{len(updates)} libraries to update:')
    for lib, ver, arch, plat, deb, _, _, _, _ in updates:
        print(f'  {lib} {ver} {arch}/{plat}')

    if dry_run:
        print('\nDry run — not downloading or generating sigs.')
        return

    # Download and generate sigs
    new_sigs = []
    for library, version, vamp_arch, platform, deb_name, source_dir, base_url, pkg_pattern, deb_arch in updates:
        print(f'\nProcessing {library} {version} ({vamp_arch})...')
        deb_url = f'{base_url}/{source_dir}/{deb_name}'
        deb_path = download_deb(deb_url, WORK_DIR)
        if not deb_path:
            continue

        extract_dir = os.path.join(WORK_DIR, f'extract-{library}-{version}-{vamp_arch}')
        so_files = extract_deb(deb_path, extract_dir)
        if not so_files:
            print(f'  No .so files found in package')
            continue

        # Generate sigs for relevant .so files
        for so_path in so_files:
            so_base = os.path.basename(so_path)

            # Filter: only process the main library .so, skip unrelated
            if 'crypto' in so_base:
                lib_name = 'openssl'
                out_name = f'openssl_{version.replace(".", "_")}_{vamp_arch}_{platform}_crypto.json'
            elif 'libssl' in so_base:
                lib_name = 'openssl-ssl'
                out_name = f'openssl-ssl_{version.replace(".", "_")}_{vamp_arch}_{platform}.json'
            else:
                lib_name = library
                out_name = f'{library}_{version.replace(".", "_")}_{vamp_arch}_{platform}.json'

            out_path = os.path.join(sigs_data_dir, out_name)
            print(f'  Generating sigs from {so_base}...')
            if generate_sigs(so_path, lib_name, version, vamp_arch, platform, out_path):
                new_sigs.append(out_path)
                print(f'  OK: {out_name}')

    # Update index
    if new_sigs:
        print('\nUpdating index...')
        sys.path.insert(0, os.path.abspath(VIVISECT_REPO_DIR))
        import vivisect.vamp as v_vamp
        idx = v_vamp.updateSigSetIndex(sigs_data_dir)
        print(f'Index updated: {len(idx["sig_sets"])} sig sets')

        # Commit and push to vamp-sigs repo
        print('\nCommitting changes to vamp-sigs repo...')
        branch_name = f'{BRANCH_PREFIX}-{hashlib.md5(str(sorted(new_sigs)).encode()).hexdigest()[:8]}'

        git_env = {**os.environ, 'GIT_SSH_COMMAND': 'ssh -i ~/.ssh/id_ed25519_github -o StrictHostKeyChecking=no'}

        subprocess.run(['git', 'checkout', 'main'], cwd=SIGS_REPO_DIR,
                       capture_output=True, text=True)
        subprocess.run(['git', 'pull', 'origin', 'main'], cwd=SIGS_REPO_DIR,
                       capture_output=True, text=True, env=git_env)
        subprocess.run(['git', 'checkout', '-b', branch_name], cwd=SIGS_REPO_DIR,
                       capture_output=True, text=True)
        subprocess.run(['git', 'add', 'data/'], cwd=SIGS_REPO_DIR,
                       capture_output=True, text=True)
        commit_msg = (f'VAMP sig update: {len(new_sigs)} new/updated sig sets\n\n'
                      f'Auto-generated by weekly VAMP sig scanner.\n'
                      f'Updated: {", ".join(os.path.basename(s) for s in new_sigs)}')
        subprocess.run(['git', 'commit', '-m', commit_msg],
                       cwd=SIGS_REPO_DIR, capture_output=True, text=True)
        push_result = subprocess.run(['git', 'push', 'origin', branch_name],
                                     cwd=SIGS_REPO_DIR, capture_output=True, text=True,
                                     env=git_env)
        if push_result.returncode != 0:
            print(f'  PUSH FAILED: {push_result.stderr[:300]}')
        else:
            print(f'\nPushed branch: {branch_name}')

            # Create PR via GitHub API
            token_file = os.path.expanduser('~/.hermes/.secrets/github.env')
            gh_token = None
            if os.path.exists(token_file):
                with open(token_file) as tf:
                    for line in tf:
                        if line.startswith('GITHUB_TOKEN='):
                            gh_token = line.split('=', 1)[1].strip()
                            break

            if gh_token:
                import urllib.request as ur
                pr_body = (f'Auto-generated by weekly VAMP sig scanner.\n\n'
                           f'Updated: {", ".join(os.path.basename(s) for s in new_sigs)}')
                pr_data = json.dumps({
                    'title': commit_msg.split('\n')[0],
                    'head': f'aragorn-1337:{branch_name}',
                    'base': 'main',
                    'body': pr_body,
                }).encode('utf-8')
                req = ur.Request(
                    'https://api.github.com/repos/atlas0fd00m/vamp-sigs/pulls',
                    data=pr_data,
                    headers={
                        'Authorization': f'token {gh_token}',
                        'Content-Type': 'application/json',
                    },
                )
                try:
                    resp = ur.urlopen(req, timeout=30)
                    pr = json.loads(resp.read().decode('utf-8'))
                    print(f'PR #{pr["number"]} created: {pr["html_url"]}')
                except Exception as e:
                    print(f'  PR creation failed: {e}')
                    print(f'  Manual link: https://github.com/atlas0fd00m/vamp-sigs/pull/new/{branch_name}')
            else:
                print(f'  No GitHub token found — manual link: https://github.com/atlas0fd00m/vamp-sigs/pull/new/{branch_name}')

    print(f'\nDone. {len(new_sigs)} sig files updated.')


if __name__ == '__main__':
    main()