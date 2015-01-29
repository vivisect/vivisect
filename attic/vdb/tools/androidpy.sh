#!/bin/sh
PY4APATH=/data/data/com.googlecode.pythonforandroid
PY4ADATA=${EXTERNAL_STORAGE}/com.googlecode.pythonforandroid
PYTHONPATH=${PY4ADATA}/extras/python:${PY4APATH}/files/python/lib/python2.6/lib-dynload
export PYTHONPATH
export TEMP=${PY4ADATA}/extras/python/tmp
export PYTHON_EGG_CACHE=${TEMP}
export PYTHONHOME=${PY4APATH}/files/python
export LD_LIBRARY_PATH=${PY4APATH}/files/python/lib:/system/lib
export HOME=${PY4ADATA}
${PY4APATH}/files/python/bin/python "$@"

