# VAMP Signature Data

This directory contains the **bundled MSVC signature set** for backward
compatibility with the original `vivisect.analysis.ms.msvc` module.

## Full Signature Database

The complete VAMP signature database (57 sig sets, 195,366 signatures
covering glibc, musl, OpenSSL, libstdc++, zlib, and many more libraries
across amd64/i386/arm/aarch64) is too large to include in the main
vivisect repository. It lives in a separate repository:

**https://github.com/atlas0fd00m/vamp-sigs**

## Installation

```bash
# Clone into the default user directory
git clone https://github.com/atlas0fd00m/vamp-sigs.git ~/.viv/vamp-sigs

# Or set the VAMP_SIG_DIR environment variable (single or multiple dirs)
export VAMP_SIG_DIR=/path/to/vamp-sigs/data

# Multiple directories (colon-separated, PATH-style — all are searched)
export VAMP_SIG_DIR=/opt/custom-sigs:/path/to/vamp-sigs/data:/opt/extra-sigs
```

## Data Directory Search Order

The VAMP analysis module searches for signature files across all
configured directories, merging signatures from every source:

1. `VAMP_SIG_DIR` environment variable (colon-separated list, each must exist)
2. `~/.viv/vamp-sigs/data/` (default user directory, if it exists)
3. `vivisect/vamp/data/` (this directory — bundled MSVC sigs, always included)

All directories in the search path are searched — signatures are merged
from every source. Earlier directories take priority for MSVC compat files
(`msvc_x86.json`, `msvc_x64.json`) where only the first match is loaded;
all other sig files from all directories are loaded (duplicates by filepath
are skipped).