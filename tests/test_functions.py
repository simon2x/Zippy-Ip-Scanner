#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Contains test cases for the base.py module."""

from __future__ import unicode_literals

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
    from zippyipscanner import functions
except ImportError as error:
    print(error)
    sys.exit(1)


class MockMain():
    
    # @pyqtSlot(dict)
    def receiveDebugSignal(message):
        assert isInstance(message, str)
        
    # @pyqtSlot(dict)
    def receiveHostnameResult(result):
        assert isInstance(result, str)
        
    # @pyqtSlot(dict)
    def receiveScanResult(result):
        self.pingAddressThread.exit()
        assert isInstance(result, str)
        
        
def test_lookup_hostname():
    m = MockMain()
    functions.LookupHostname(m, "000.000.0.000", 5)
    
def test_lookup_mac_address():
    m = MockMain()
    r = functions.LookupMacAddress("000.000.0.000")
    assert isinstance(r, str)
    
def test_lookup_manufacturer():
    m = MockMain()
    r = functions.LookupManufacturers("000.000.0.000")
    assert isinstance(r, str)

def test_ping_address():
    m = MockMain()
    m.pingAddressThread = functions.PingAddress(m, ["000.000.0.000"], {})

    
if __name__ == '__main__':
    unittest.main()
