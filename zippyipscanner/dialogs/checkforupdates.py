#!/usr/bin/python3
# -*- coding: utf-8 -*
'''
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
'''


import logging
from urllib import request
from version import __version__
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from forms.uicheckforupdates import Ui_CheckForUpdates

baseUrl = 'https://sourceforge.net/projects/zippy-ip-scanner/files/'
releaseURL = 'https://raw.githubusercontent.com/swprojects/Zippy-Ip-Scanner/master/RELEASES'


class CheckForUpdatesThread(QThread):

    signalCheck = pyqtSignal(dict)

    def __init__(self, parent):
        super(CheckForUpdatesThread, self).__init__()
        self.parent = parent
        self.signalCheck.connect(self.parent.slotCheck)
        self.start()

    def run(self):
        req = request.Request(releaseURL, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            result = request.urlopen(req).read().decode('utf-8')
            result = result.split('\n')
            ver, url = result[0].split(',')
            a = '<a href=\'{0}\'>{1}</a>'.format(url, ver)
        except Exception as e:
            logging.info(e)
            a = None

        self.signalCheck.emit({'result': a})


class CheckForUpdates(QDialog):

    def __init__(self, parent):
        super(CheckForUpdates, self).__init__(parent)
        self.setWindowTitle('Check For Updates')
        self.ui = Ui_CheckForUpdates()
        self.ui.setupUi(self)
        self.updateUI()
        self.show()
        CheckForUpdatesThread(self).exec()

    @pyqtSlot(dict)
    def slotCheck(self, kwargs):
        a = kwargs.get('result', 'Failed to check latest available version. Try checking manually')
        self.ui.labelLatestVersion.setText(a)

    def updateUI(self):
        logging.info('CheckForUpdates->updateUI')
        self.ui.labelCurrentVersion.setText('v{0}'.format(__version__))
        self.ui.labelCheckManual.setText('<a href=\'{0}\'>Check Releases Manually</a>'.format(baseUrl))
        self.ui.labelLatestVersion.setText('vX.X.X')
