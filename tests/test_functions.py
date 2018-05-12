#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Contains test cases for the base.py module."""

from __future__ import unicode_literals
import unittest
import logging
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

class TestPingAddress(unittest.TestCase):
    
    def setUp(self):
        self.scanParams = {"MAC Address": 2, "Manufacturer": 2}
        self.thread = functions.PingAddress(None, [], self.scanParams, start=False)
        
    def tearDown(self):
        pass

    def test_checkMac(self):
        assert self.thread.checkMac is True
        self.scanParams["MAC Address"] = 0
        assert self.thread.checkMac is False
        
    def test_checkManufacturer(self):
        assert self.thread.checkManufacturer is True
        self.scanParams["Manufacturer"] = 0
        assert self.thread.checkManufacturer is False

    def test_extractMS_Windows(self):
        output = "Average = 50\r\n"
        ttl = self.thread.extractMS(output)
        assert ttl == "50"
        
    def test_extractMS_Linux(self):
        output = "time=50 ms"
        ttl = self.thread.extractMS(output)
        assert ttl == "50"
                
    def test_extractTTL_Windows(self):
        output = "TTL=50\r\n\r\nPing statistics"
        ttl = self.thread.extractTTL(output)
        assert ttl == "50"
        
    def test_extractTTL_Linux(self):
        output = "ttl=50 time="
        ttl = self.thread.extractTTL(output)
        assert ttl == "50"

    def test_gotResponse(self):
        if functions.on_windows():
            assert self.thread.gotResponse("Reply from") is True
        else:    
            assert self.thread.gotResponse("ttl=") is True
    
    def test_gotResponse2(self):
        assert self.thread.gotResponse("GARBAGE OUTPUT") is False
        
    def test_outputResult(self):
        result = self.thread.outputResult("")
        assert result == {}
        
    def test_outputResult_Linux(self):
        output = "Reply from" + "ttl=50 time=50 ms"
        result = self.thread.outputResult(output)
        assert result["TTL"] == "50"
        
    def test_pingCommand(self):
        address = "192.168.0.1"
        result = self.thread.pingCommand(address)
        assert result[-1] == address
        
    def test_returnResult(self):
        result = self.thread.returnResult({})
        assert result is None
      
    def test_runCommand(self):
        pass
        
    def test_run(self):
        pass
  
def test_startupInfo():
    info = functions.startupInfo()
    if functions.on_windows():
        assert info is not None
    else:
        assert info is None
            
def test_lookup_hostname():
    functions.LookupHostname(None, "192.168.0.1", 5)
    
def test_lookup_mac_address():
    r = functions.LookupMacAddress("192.168.0.1")
    assert isinstance(r, str)
    
def test_lookup_manufacturer():
    r = functions.LookupManufacturers("192.168.0.1")
    assert isinstance(r, str)

if __name__ == '__main__':
    unittest.main()
