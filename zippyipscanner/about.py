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

if __name__ != "__main__":
    # this allows us import relatively
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import logging
from version import __version__
from license import __license__
import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
                             QLabel, QTextEdit, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class AboutDialog(QDialog):

    def __init__(self, parent=None, testing=False):
        super(AboutDialog, self).__init__(parent)
        self.setWindowTitle("About Zippy Ip Scanner")
        self.testing = testing
        if testing is False:
            if parent:
                self.setWindowIcon(QIcon(parent.appPath + "zippyipscanner.ico"))
            self.initGUI()
            self.show()

    @property
    def homePageLink(self):
        return "www.sanawu.com"

    @property
    def macVendorLink(self):
        return "http://macvendors.co/kb/privacy-policy"

    @property
    def macVendorPolicy(self):
        p = ("Zippy Ip Scanner retrieves the MAC vendor name via MacVendors.co API and \n"
             + "therefore MAC vendor name retrieval is subject to <a href={0}>MacVendors.co"
             + " privacy policy</a>.\n".format(self.macVendorLink)
             + "Uncheck Manufacturer checkbox to disable this feature.")
        return p

    @property
    def githubLink(self):
        return "https://github.com/swprojects/Zippy-Ip-Scanner"

    @property
    def homePageLink(self):
        return "www.sanawu.com"

    @property
    def macVendorLink(self):
        return "http://macvendors.co/kb/privacy-policy"

    @property
    def macVendorPolicy(self):
        p = ("Zippy Ip Scanner retrieves the MAC vendor name via MacVendors.co API and \n"
             + "therefore MAC vendor name retrieval is subject to <a href={0}>MacVendors.co"
             + " privacy policy</a>.\n".format(self.macVendorLink)
             + "Uncheck Manufacturer checkbox to disable this feature.")
        return p

    @property
    def githubLink(self):
        return "https://github.com/swprojects/Zippy-Ip-Scanner"

    def keyPressEvent(self, event):
        logging.info("AboutDialog->keyPressEvent")
        try:
            e = event.key()
        except AttributeError:
            e = event
        if e == Qt.Key_Escape:
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
        authorLabel = QLabel("<a href={0}>{1}</a>".format(self.homePageLink, self.homePageLink), self)
        authorLabel.setTextFormat(Qt.RichText)
        authorLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        aboutLayout.addWidget(authorLabel, 0, 2, 1, 2)
        authorLabel.setOpenExternalLinks(True)

        aboutLayout.addWidget(QLabel("Github:", self), 1, 0, 1, 2)
        g = self.githubLink
        homeLabel = QLabel("<a href={0}>{1}</a>".format(g, g), self)
        homeLabel.setTextFormat(Qt.RichText)
        homeLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
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

        policyLabel = QLabel(self.macVendorPolicy, self)
        policyLabel.setWordWrap(True)
        policyLabel.setTextFormat(Qt.RichText)
        policyLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
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
        licenseText.setAlignment(Qt.AlignCenter)
        licenseText.setText(__license__)
        gboxScanLayout.addWidget(licenseText)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AboutDialog()
    sys.exit(app.exec_())
