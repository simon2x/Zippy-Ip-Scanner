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

    
# class WidgetTestCase(unittest.TestCase):

    # def setUp(self):
        # self.app = QApplication([])
        # self.about = about.AboutDialog()
                
    # def tearDown(self):
        # self.about.close()
        
    # def test_key_press_event(self):
        # self.about.keyPressEvent("")
        

if __name__ == '__main__':
    unittest.main()
