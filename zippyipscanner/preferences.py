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
import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox, QListWidget, QStackedWidget,
                             QSplitter, QVBoxLayout, QCheckBox, QListWidgetItem, QDialogButtonBox,
                             QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

PREFERENCE_LIST = [
    "General",
    "Scan",
]


class PreferencesDialog(QDialog):

    def __init__(self, parent=None, config={}, testing=False):
        super(PreferencesDialog, self).__init__(parent)
        self.setWindowTitle("Zippy Ip Scanner Preferences")
        self.widgetDict = {}
        self._config = config
        self.testing = testing
        if testing is False:
            if parent:
                self.setWindowIcon(QIcon(parent.appPath + "zippyipscanner.ico"))
            self.initGUI()
            self.show()
        self.setFixedSize(800, 600)

    @property
    def config(self):
        return self._config

    def keyPressEvent(self, event):
        logging.info("PreferencesDialog->keyPressEvent")
        try:
            e = event.key()
        except AttributeError:
            e = event
        if e == Qt.Key_Escape:
            self.close()

    def onSelectionChanged(self):
        n = self.prefList.currentRow()
        self.rightWidget.setCurrentIndex(n)

    def generalUI(self):
        widget = QWidget(self)
        grid = QGridLayout()
        widget.setLayout(grid)
        grid.setColumnStretch(0, 1)
        grid.setSpacing(5)

        gboxLayout = QVBoxLayout()
        gboxResults = QGroupBox("General", self)
        gboxResults.setLayout(gboxLayout)
        self.chkShowAlive = QCheckBox("Remember Window Size", self)
        grid.addWidget(gboxResults)
        self.chkShowAlive.setTristate(False)
        gboxLayout.addWidget(self.chkShowAlive)
        return widget

    def scanUI(self):
        widget = QWidget(self)
        grid = QGridLayout()
        widget.setLayout(grid)
        grid.setColumnStretch(0, 1)
        grid.setSpacing(5)

        gboxLayout = QVBoxLayout()
        gboxResults = QGroupBox("Scan", self)
        gboxResults.setLayout(gboxLayout)
        self.chkShowAlive = QCheckBox("Remember Scan History", self)
        grid.addWidget(gboxResults)
        self.chkShowAlive.setTristate(False)
        gboxLayout.addWidget(self.chkShowAlive)
        return widget

    def initGUI(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        splitter = QSplitter(self, orientation=Qt.Horizontal)
        mainLayout.addWidget(splitter)

        prefList = QListWidget(self)
        self.rightWidget = QStackedWidget(self)
        for s in PREFERENCE_LIST:
            item = QListWidgetItem(s)
            prefList.addItem(item)
            try:
                w = getattr(self, s.lower() + "UI")()
                self.widgetDict[s] = w
                self.rightWidget.addWidget(w)
            except Exception as e:
                logging.debug(e)

        splitter.addWidget(prefList)
        prefList.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.prefList = prefList

        splitter.addWidget(self.rightWidget)
        self.rightWidget.addWidget(self.generalUI())

        qBut = QDialogButtonBox(self)
        mainLayout.addWidget(qBut)
        qBut.addButton(QDialogButtonBox.Save)
        qBut.addButton(QDialogButtonBox.Cancel)

        splitter.setSizes([150, 650])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = PreferencesDialog()
    sys.exit(app.exec_())
