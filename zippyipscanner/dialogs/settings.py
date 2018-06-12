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
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from forms.uisettingsdialog import Ui_SettingsDialog

PREFERENCE_LIST = [
    "General",
    "Scan",
]


class SettingsDialog(QDialog):

    def __init__(self, parent, config={}):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Zippy Ip Scanner Preferences")
        self.parent = parent
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.widgets = {}
        self._config = config
        self.setWindowIcon(QIcon(parent.appPath + "zippyipscanner.ico"))
        self.updateUI()
        self.show()

    @property
    def config(self):
        return self._config

    def onButton(self, button):
        logging.info('SettingsDialog->apply')
        if button.text() == 'Cancel':
            return
        # save settings
        self.config['showSplash'] = self.ui.checkBoxSplashScreen.isChecked()
        if not self.ui.checkBoxSplashScreen.isChecked():
            self.parent.clearScanHistory()
        self.config['rememberScanHistory'] = self.ui.checkBoxScanHistory.isChecked()
        self.parent.config.update(self.config)
        self.parent.saveConfig()

    def keyPressEvent(self, event):
        logging.info('PreferencesDialog->keyPressEvent')
        try:
            e = event.key()
        except AttributeError:
            e = event
        if e == Qt.Key_Escape:
            self.close()

    def updateUI(self):
        logging.info('SettingsDialog->updateUI')
        self.ui.checkBoxSplashScreen.setChecked(self.config['showSplash'])
        self.ui.checkBoxScanHistory.setChecked(self.config['rememberScanHistory'])
