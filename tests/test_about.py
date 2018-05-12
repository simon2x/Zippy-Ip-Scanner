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
    from zippyipscanner import about
except ImportError as error:
    print(error)
    sys.exit(1)

    
class TestAboutDialog(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])
        self.about = about.AboutDialog(testing=True)
                
    def tearDown(self):
        self.about.close()
        
    def test_key_press_event_fail(self):
        result = self.about.keyPressEvent("")
        assert result is None
        result = self.about.keyPressEvent(Qt.Key_Return)
        assert result is None
        
    def test_key_press_event_success(self):
        result = self.about.keyPressEvent(Qt.Key_Escape)
        assert result is True

    def test_homePageLink(self):
        result = self.about.homePageLink
        assert isinstance(result, str)
        
    def test_macVendorLink(self):
        result = self.about.macVendorLink
        assert isinstance(result, str)
        
    def test_macVendorPolicy(self):
        result = self.about.macVendorPolicy
        assert isinstance(result, str)
        
    def test_githubLink(self):
        result = self.about.githubLink
        assert isinstance(result, str)  

    def test_initGUI(self):
        result = self.about.initGUI()
        assert result is None
    
        
if __name__ == '__main__':
    unittest.main()
