# VAMP Signature Generation

VAMP (Vivisect's Automated Matching Process) is a function identification
subsystem that matches known library functions in static-compiled, stripped
binaries — analogous to IDA Pro's FLIRT technology.

This directory contains JSON signature databases and the tools to generate
new ones quickly.

## Quick Start: Generate Sigs for a New Library

### From an ELF shared library (.so)

```bash
# One-liner: generate sigs from any .so file
python3 -m vivisect.vamp.tools.gen_elf_sigs \
    --input /path/to/libfoo.so \
    --library libfoo \
    --version 1.2.3 \
    --arch amd64 \
    --platform linux \
    --compiler gcc-13 \
    --output vivisect/vamp/data/libfoo_1_2_3_amd64_linux.json
```

This takes **seconds** — no full vivisect analysis needed. The tool reads
the ELF symbol table directly and extracts byte/mask signatures with
relocation masking.

### From a Windows DLL (.dll)

Use the full vivisect-based generator (slower, runs complete analysis):

```bash
python3 -m vivisect.vamp.tools.gen_sigs \
    --input C:\path\to\libfoo.dll \
    --library libfoo \
    --version 1.2.3 \
    --arch amd64 \
    --platform windows \
    --compiler msvc-2022 \
    --output vivisect/vamp/data/libfoo_1_2_3_amd64_windows.json
```

### From a package (.deb / .rpm / .pkg)

Extract the package first, then run the ELF generator on the .so inside:

```bash
# Debian/Ubuntu .deb
dpkg-deb -x libfoo_1.2.3_amd64.deb /tmp/libfoo-extract/
python3 -m vivisect.vamp.tools.gen_elf_sigs \
    --input /tmp/libfoo-extract/usr/lib/x86_64-linux-gnu/libfoo.so.1.2.3 \
    --library libfoo \
    --version 1.2.3 \
    --arch amd64 \
    --output vivisect/vamp/data/libfoo_1_2_3_amd64_linux.json

# RPM
rpm2cpio libfoo-1.2.3.rpm | cpio -idmv
python3 -m vivisect.vamp.tools.gen_elf_sigs \
    --input ./usr/lib64/libfoo.so.1.2.3 \
    --library libfoo \
    --version 1.2.3 \
    --arch amd64 \
    --output vivisect/vamp/data/libfoo_1_2_3_amd64_linux.json
```

### During an Offline RE Session (CTF / Proprietary Library)

Found a stripped binary that statically links a known library? Generate
sigs from the **original unstripped library** and match against the target:

```bash
# 1. Find the original library (from the target system, a dev package,
#    or a package archive)
#    e.g., the target was built on Ubuntu 22.04 with glibc 2.35
apt download libc6  # or: curl the .deb from archive.ubuntu.com
dpkg-deb -x libc6_2.35-0ubuntu3.14_amd64.deb /tmp/libc/
python3 -m vivisect.vamp.tools.gen_elf_sigs \
    --input /tmp/libc/lib/x86_64-linux-gnu/libc.so.6 \
    --library glibc \
    --version 2.35 \
    --arch amd64 \
    --output /tmp/glibc_2_35_amd64.json

# 2. Load the sigs in vivisect CLI
vivisect> vampload /tmp/glibc_2_35_amd64.json
Loaded 2100 signatures for glibc 2.35 (amd64/linux)

# 3. List loaded sig sets
vivisect> vamplist
Loaded VAMP signature sets:
  [0] glibc 2.35 (amd64/linux) — 2100 signatures

# 4. Match a specific function
vivisect> vampmatch 0x401000
Match in set [0] glibc 2.35: glibc.printf

# 5. Or let auto-analysis do it — add the generic vamp module:
vivisect> addFuncAnalysisModule vivisect.analysis.generic.vamp
```

### For a Proprietary / Custom Library

If you're reversing a binary that statically links a proprietary or custom
library, and you have access to the original .so or .a:

```bash
# Generate sigs from the original unstripped library
python3 -m vivisect.vamp.tools.gen_elf_sigs \
    --input /opt/vendor/lib/libproprietary.so \
    --library libproprietary \
    --version 3.7.2 \
    --arch amd64 \
    --output vivisect/vamp/data/libproprietary_3_7_2_amd64_linux.json

# Then use them against the stripped target binary
python3 -m vivisect.vamp.tools.validate_sigs \
    --sigs vivisect/vamp/data/libproprietary_3_7_2_amd64_linux.json \
    --test-binary /path/to/stripped_target \
    --verbose
```

## Signature File Format

Each JSON sig file contains:

```json
{
  "format_version": 1,
  "library": "glibc",
  "version": "2.39",
  "arch": "amd64",
  "platform": "linux",
  "compiler": "gcc-13",
  "compiled_flags": "-O2",
  "binary_sha256": "...",
  "generated_at": "2026-08-09T...",
  "signatures": [
    {
      "name": "glibc.printf",
      "bytes": "f30f1efa554889e5...",
      "mask": "ffffffffffffffff...",
      "func_size": 142,
      "first_block_size": 256,
      "reloc_count": 0,
      "masked_ratio": 0.0,
      "confidence": "high"
    }
  ]
}
```

- **bytes/mask**: Hex-encoded byte sequence with mask (`\xff` = compare,
  `\x00` = wildcard for relocatable addresses)
- **confidence**: `high` (≥16 bytes, <25% masked), `medium` (≥8 bytes,
  <50% masked), `low` (everything else — usually filtered out)
- **func_size**: Total function size from the symbol table
- **first_block_size**: Size of the first linear code block (capped at 256)

## Available Tools

| Tool | Purpose | Speed |
|------|---------|-------|
| `gen_elf_sigs.py` | Fast ELF sig generator (symbol table + raw bytes) | Seconds |
| `gen_sigs.py` | Full vivisect-based generator (runs complete analysis) | Minutes |
| `validate_sigs.py` | Test sigs against a binary, report TP/FP/FN | Seconds |
| `sig_diff.py` | Compare sig sets across versions for stability | Instant |

## Available Signature Databases

Run `python3 -c "import vivisect.vamp as v; idx = v.loadSigSetIndex(); print(idx)"`
or:

```bash
vivisect> vamplist
```

See `data/index.json` for the full catalog.

## Adding New Signature Databases

1. Generate the sig file using one of the tools above
2. Save it to `vivisect/vamp/data/` with naming convention:
   `LIBRARY_VERSION_ARCH_PLATFORM.json`
3. Regenerate the index:
   ```python
   import vivisect.vamp as v
   v.updateSigSetIndex()
   ```
4. The generic analysis module (`vivisect.analysis.generic.vamp`)
   auto-loads all matching sig sets during analysis based on the
   workspace's architecture and platform.

## CLI Commands

| Command | Description |
|---------|-------------|
| `vampsig <va>` | Generate a sig for a specific function VA |
| `vampload <file>` | Load a JSON sig set into the workspace |
| `vamplist` | List loaded sig sets and available data files |
| `vampmatch <va>` | Check a function against all loaded sig sets |

## TODO

- [ ] Weekly automated scans for newer versions of major Windows and Linux
      libraries (glibc, musl, OpenSSL, zlib, etc.), automated download and
      sig generation, and a new PR submitted to
      https://github.com/vivisect/vivisect with the updated sig databases
- [ ] Bionic (Android) libc sigs — requires Android NDK download
- [ ] Windows UCRT/MSVC CRT sigs — requires Windows SDK binaries
- [ ] Additional crypto libraries: mbedTLS, wolfSSL, libsodium, BoringSSL
- [ ] Additional compression: libpng, libtiff, libjpeg
- [ ] Cross-version stability analysis using `sig_diff.py`