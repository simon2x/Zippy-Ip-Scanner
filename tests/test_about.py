#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Contains test cases for the base.py module."""

from __future__ import unicode_literals
import pytest
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


def test_key_press_event(qtbot):
    dialog = about.AboutDialog()
    qtbot.addWidget(dialog)
    qtbot.keyPress(dialog, Qt.Key_Return)
    
def test_homePageLink(qtbot):
    dialog = about.AboutDialog()
    qtbot.addWidget(dialog)
    result = dialog.homePageLink
    assert isinstance(result, str)

def test_macVendorLink(qtbot):
    dialog = about.AboutDialog()
    qtbot.addWidget(dialog)
    result = dialog.macVendorLink
    assert isinstance(result, str)

def test_macVendorPolicy(qtbot):
    dialog = about.AboutDialog()
    qtbot.addWidget(dialog)
    result = dialog.macVendorPolicy
    assert isinstance(result, str)

def test_githubLink(qtbot):
    dialog = about.AboutDialog()
    qtbot.addWidget(dialog)
    result = dialog.githubLink
    assert isinstance(result, str)
