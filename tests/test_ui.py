#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Contains test cases for the base.py module."""

from __future__ import unicode_literals

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))


try:
    import wx
    from unittest import mock

    from zippyipscanner.base import (
        BaseList
    )
except ImportError as error:
    print(error)
    sys.exit(1)


class TestBaseList(unittest.TestCase):

    """Test cases for the BaseList widget."""

    def setUp(self):
        self.app = wx.App()

        self.frame = wx.Frame(None)
        self.baseList = BaseList(self.frame)

    def tearDown(self):
        self.frame.Destroy()
        
    def test_add_columns(self):
        self.baseList.InsertColumn(0, "column0")
    
    def test_append(self):
        self.baseList.InsertColumn(0, "column0")
        self.baseList.Append(["item0"])
        self.assertEqual(self.baseList.GetItemText(0, col=0), "item0")

if __name__ == '__main__':
    unittest.main()
