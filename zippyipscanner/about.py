#!/usr/bin/python3
# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>
Copyright (c) 2018 by Simon Wu <Zippy Ip Scanner>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>
"""

import logging
from version import __version__
from license import __license__
import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from portable import resource_path

class AboutDialog(QDialog):

    def __init__(self, parent=None):                    
        super(AboutDialog, self).__init__(parent)
        
        self.setWindowTitle("About Zippy Ip Scanner")
        self.setWindowIcon(QtGui.QIcon('zippyipscanner.ico'))
        self.initGUI()
        self.show()
        
    def keyPressEvent(self, event):
        logging.info("AboutDialog->keyPressEvent")
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Escape:
                self.close()
            
    def initGUI(self):
        row = 0
        self.grid = QGridLayout()
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.grid.setSpacing(5)
        self.setLayout(self.grid)
        
        # About
        aboutLayout = QGridLayout()  
        gboxScan = QGroupBox("About", self) 
        gboxScan.setLayout(aboutLayout)
        self.grid.addWidget(gboxScan, row, 0, 1, 2)
        
        aboutLayout.addWidget(QLabel("Author:", self), 0, 0, 1, 2)
        authorLabel = QLabel("<a href=www.sanawu.com>www.sanawu.com</a>", self)
        authorLabel.setTextFormat(QtCore.Qt.RichText);
        authorLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        aboutLayout.addWidget(authorLabel, 0, 2, 1, 2)
        authorLabel.setOpenExternalLinks(True)
        
        aboutLayout.addWidget(QLabel("Github:", self), 1, 0, 1, 2)     
        g = "https://github.com/swprojects/Zippy-Ip-Scanner"
        homeLabel = QLabel ("<a href={0}>{1}</a>".format(g, g), self)
        homeLabel.setTextFormat(QtCore.Qt.RichText);
        homeLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        homeLabel.setOpenExternalLinks(True)
        aboutLayout.addWidget(homeLabel, 1, 2, 1, 1)
        
        aboutLayout.addWidget(QLabel("Version:", self), 2, 0, 1, 2)
        aboutLayout.addWidget(QLabel(str(__version__), self), 2, 2, 1, 2)
        
        
        # Mac Vender Lookup
        row += 1
        policyLayout = QHBoxLayout()
        gboxPolicy = QGroupBox("Mac Vender Lookup", self) 
        gboxPolicy.setLayout(policyLayout)
        self.grid.addWidget(gboxPolicy, row, 0, 1, 2)
        
        pLink = "http://macvendors.co/kb/privacy-policy"
        p = ("Zippy Ip Scanner retrieves the MAC vendor name via MacVendors.co API and \n"
            +"therefore MAC vendor name retrieval is subject to <a href={0}>MacVendors.co privacy policy</a>.\n".format(pLink)
            +"Uncheck Manufacturer checkbox to disable this feature.")
        policyLabel = QLabel(p, self)
        policyLabel.setWordWrap(True)
        policyLabel.setTextFormat(QtCore.Qt.RichText)
        policyLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        policyLabel.setOpenExternalLinks(True)
        policyLayout.addWidget(policyLabel)
                
        # License
        row += 1
        self.grid.setRowStretch(row, 1)
        gboxScanLayout = QHBoxLayout()  
        gboxScan = QGroupBox("License", self) 
        gboxScan.setLayout(gboxScanLayout)
        self.grid.addWidget(gboxScan, row, 0, 1, 2)
        licenseText = QTextEdit()
        licenseText.setReadOnly(True)
        licenseText.setAlignment(QtCore.Qt.AlignCenter)
        licenseText.setText(__license__)
        gboxScanLayout.addWidget(licenseText)
      
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AboutDialog()
    sys.exit(app.exec_())