import os
import unittest

def require(f):
    def skipit(*args, **kwargs):
        raise unittest.SkipTest('VIVBINS env var...')

    if os.getenv('VIVBINS') == None:
        return skipit

    return f
