#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Contains test cases for the base.py module."""

from __future__ import unicode_literals
import unittest
import sys
import os.path
from PyQt5.QtCore import (Qt, QSize, QTimer, pyqtSlot)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QSplashScreen,
                             QGridLayout, QHBoxLayout, QVBoxLayout, QGroupBox,
                             QCheckBox, QComboBox, QToolButton, QLabel, QSpinBox,
                             QTreeView, QAction)
from PyQt5.QtGui import (QIcon, QPixmap, QStandardItemModel)

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from zippyipscanner import zippyipscanner
except ImportError as error:
    print(error)
    sys.exit(1)

 
app_defaults = {
    "pos": None,
    "size": [400, 300],
    "ipStartHistory": [],
    "ipEndHistory": [],
    "customScanHistory": [],
    "scanConfig": {"hostnameTimeout": "5", "Hostname": 2, "Manufacturer": 2, "MAC Address": 2},
    "filter": {"showAliveOnly": 2}
}


class WidgetTestCase(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])
        self.main = zippyipscanner.MainWindow()

    def tearDown(self):
        self.main.close()
        
    def test_appDefaults(self):
        r = self.main.appDefaults
        assert isinstance(r, dict)
        assert r == app_defaults
        
    def test_appPath(self):
        r = self.main.appPath
        assert isinstance(r, str)
        
    def test_config(self):
        r = self.main.config
        assert isinstance(r, dict)
        
    def test_isScanning(self):
        r = self.main.isScanning
        assert isinstance(r, bool)
        
    def test_scanParams(self):
        r = self.main.scanParams
        assert isinstance(r, dict)
        
    def test_appendIpEntry(self):
        r = self.main.appendIpEntry({"IP Address": "Bar"})
        
    def test_clearIpListItems(self):
        self.main.appendIpEntry({"IP Address": "Bar"})
        assert self.main.ipModel.rowCount() == 1
            
    def test_cleanScan(self):
        r = self.main.cleanScan()    
        
    def test_parseIpString(self):
        r = self.main.parseIpString("192.168.0.1")
        assert r == ["192.168.0.1"]
        
        
if __name__ == '__main__':
    unittest.main()
