#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
import pytest
PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from zippyipscanner import mathfunctions as mf
except ImportError as error:
    sys.exit(1)


  
def test_decimal_to_byte_list():
    b = 256
    res = mf.decimal_to_byte_list(b, retbytes=4)
    assert res == [0, 0, 1, 0]
    
def test_byte_list_to_decimal():
    b = [0, 0, 1, 0] 
    res = mf.byte_list_to_decimal(b)
    assert res == 256


if __name__ == '__main__':
    pytest.main()
