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

# Or set the VAMP_SIG_DIR environment variable
export VAMP_SIG_DIR=/path/to/vamp-sigs/data
```

## Data Directory Search Order

The VAMP analysis module searches for signature files in this order:

1. `VAMP_SIG_DIR` environment variable
2. `~/.viv/vamp-sigs/data/` (default user directory)
3. `vivisect/vamp/data/` (this directory — bundled MSVC sigs only)