#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Contains test cases for the base.py module."""

from __future__ import unicode_literals
import pytest
import sys
import os.path
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

SYS_ARGS = {
    "--verbose": 0,
}


def test_sys_args():
    assert zippyipscanner.process_sys_args() == {}
    for x in SYS_ARGS:
        assert x in zippyipscanner.SYS_ARGS

def test_sys_args_dummy():
    t = ["", "--verbose=2"]
    zippyipscanner.sys.argv = t
    result = zippyipscanner.process_sys_args()
    assert result["--verbose"] == "2"

def test_set_logging_level():
    zippyipscanner.set_logging_level()
    del zippyipscanner.SYS_ARGS["--verbose"]
    zippyipscanner.set_logging_level()
    
def test_appDefaults(qtbot):
    window = zippyipscanner.MainWindow()
    qtbot.addWidget(window)

def test_isScanning(qtbot):
    window = zippyipscanner.MainWindow()
    qtbot.addWidget(window)
    r = window.isScanning
    assert isinstance(r, bool)
        
def test_scanParams(qtbot):
    window = zippyipscanner.MainWindow()
    qtbot.addWidget(window)
    r = window.scanParams
    assert isinstance(r, dict)

def test_appPath(qtbot):
    window = zippyipscanner.MainWindow()
    qtbot.addWidget(window)
    r = window.appPath
    assert isinstance(r, str)
        
def test_config(qtbot):
    window = zippyipscanner.MainWindow()
    qtbot.addWidget(window)
    r = window.config
    assert isinstance(r, dict)
        
def test_slotScanIp(qtbot):
    window = zippyipscanner.MainWindow()
    qtbot.addWidget(window)
    r = window.slotScanIp({"IP Address": "Bar"})
        
def test_clearIpListItems(qtbot):
    window = zippyipscanner.MainWindow()
    qtbot.addWidget(window)
    r = window.slotScanIp({"IP Address": "Bar"})
    assert window.ipModel.rowCount() == 1
        
def test_cleanScan(qtbot):
    window = zippyipscanner.MainWindow()
    qtbot.addWidget(window)
    r = window.cleanScan()    

def test_setScanIcons(qtbot):
    window = zippyipscanner.MainWindow()
    qtbot.addWidget(window)
    window.setScanIcons()
        
if __name__ == '__main__':
    pytest.main()
