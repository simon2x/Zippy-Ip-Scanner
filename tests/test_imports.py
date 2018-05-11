#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Contains test cases for the base.py module."""

from __future__ import unicode_literals

import sys
import os.path

try:
    pass
except ImportError as error:
    print(error)
    sys.exit(1)

def test_version():
    from zippyipscanner.version import __version__
    v = __version__
    v2 = v.split(".")
    for x in v2:
        int(x)
    
def test_license():
    from zippyipscanner.license import __license__
    assert isinstance(__license__, str)

def test_import_portable():
    from zippyipscanner.portable import resource_path
        
def test_resource_path():
    from zippyipscanner.portable import resource_path
    r = resource_path("")
    assert isinstance(r, str)

    
if __name__ == '__main__':
    unittest.main()
