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

import os
import sys
import json
import logging
from functools import partial
from PyQt5.QtCore import (Qt, QSize, QTimer, pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplashScreen)
from PyQt5.QtGui import (QIcon, QPixmap, QStandardItemModel)
from base.filteredmodel import FilteredModel


appPath = ''
if __name__ != '__main__':
    # this allows us to import relatively
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    appPath = os.path.dirname(os.path.realpath(__file__)) + '/'


if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


import functions
from about import AboutDialog
from dialogs.settings import SettingsDialog
from version import __version__
from forms.uimainwindow import Ui_MainWindow

SYS_ARGS = {
    "--verbose": 0,
}
# verbosity
LOG_LEVELS = {
    "1": 20,  # Info
    "2": 10,  # Debug
    "3": 30,  # Warning
    "4": 40,  # Error
    "5": 50,  # Critical
}

STOP_ICON = appPath + "images/stop.png"
START_ICON = appPath + "images/start.png"
MAX_HOSTNAME_CHECKS = 5
TIMER_CHECK_MS = 100
SPLASH_TIMEOUT = 1200


class MainWindow(QMainWindow):

    signalAddPing = pyqtSignal(dict)
    signalScanParams = pyqtSignal(dict)
    signalStopScanning = pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()

        self._isScanning = False
        self._bitmaps = {}
        self._sortBy = 0
        self._addressResults = []
        self.addressResultsCount = 0
        self._addressDict = {}
        self._hostnameCheck = {}
        self._hostnameCheckThreads = {}
        self.scanTotalCount = 0
        self.pingThread = functions.PingAddress(self)
        self.signalAddPing.connect(self.pingThread.slotAddPing)
        self.signalScanParams.connect(self.pingThread.slotScanParams)
        self.signalStopScanning.connect(self.pingThread.slotStopScanning)
        self.parseIpthread = None
        self.ipHeaders = ["IP Address", "Hostname", "Ping", "TTL", "Manufacturer", "MAC Address"]
        self.currentIpList = None

        self.setWindowTitle("Zippy IP Scanner v{0}".format(__version__))
        self.setWindowIcon(QIcon(appPath + "zippyipscanner.ico"))

        self._config = self.appDefaults
        self.loadConfig()
        self.createMenuBar()
        self.statusBar()

        self.initGUI()
        self.initTimers()
        self.restoreConfigState()
        self.initSplash()
        self.show()

    @property
    def appDefaults(self):
        return {
            "pos": None,
            "size": [400, 300],
            "ipStartHistory": [],
            "ipEndHistory": [],
            "customScanHistory": [],
            "scanConfig": {"hostnameTimeout": "5", "Hostname": 2, "Manufacturer": 2, "MAC Address": 2},
            "filter": {"showAliveOnly": 2}
        }

    @property
    def appPath(self):
        return appPath

    @property
    def config(self):
        return self._config

    @property
    def configPath(self):
        if sys.platform == "linux":
            from os.path import expanduser, join
            from os import system
            home = expanduser("~")
            base = "{0}/.local/share/zippyipscanner/".format(home)
            system("mkdir -p {0}".format(base))
            path = join(base, "config.json")
        else:
            path = "config.json"
        return path

    @property
    def isScanning(self):
        return self._isScanning

    @isScanning.setter
    def isScanning(self, value):
        self._isScanning = value

    @pyqtSlot(str)
    def slotDebug(self, str):
        logging.debug(str)

    @pyqtSlot(str)
    def slotLookupTimeout(self, address):
        logging.info(address)
        del self._hostnameCheck[address]
        self.addressResultsCount += 1

    @pyqtSlot(dict)
    def slotHostnameResult(self, result):
        """
        Receive a single hostname scan result

        :param dict result: the result of a hostname scan
        :returns: None
        :raises KeyError: raises an exception

        """
        logging.debug("MainWindow->slotHostnameResult %s" % str(result))

        if self.isScanning is False:
            return

        try:
            index = self._addressDict[result["address"]]["index"]
            self.ipModel.setData(self.ipModel.index(index, self.ipHeaders.index("Hostname")), result["hostname"])
            del self._hostnameCheck[result["address"]]
            del self._hostnameCheckThreads[result["address"]]
            self.addressResultsCount += 1
        except KeyError:
            logging.debug(KeyError)

    @pyqtSlot(dict)
    def slotScanIp(self, data):
        """
        Append new scan entry to ip list and add to pingThread

        :param dict data: contains IP address
        :returns: None
        :raises Exception: raises an exception

        """
        self.ipModel.insertRow(self.ipModel.rowCount())
        for col, header in enumerate(self.ipHeaders):
            try:
                index = self.ipModel.rowCount() - 1
                self.ipModel.setData(self.ipModel.index(index, col), data[header])
                address = data["IP Address"]
                self._addressDict[address] = {"index": index}
                self.startScan(index, address)
            except Exception as e:
                logging.debug("MainWindow->slotScanIp: %s" % e)

    @pyqtSlot(dict)
    def slotScanResult(self, result):
        """
        Receive and handle scan result

        :param dict result: dict of ip scan result
        :returns: None
        :raises Error: if ipModel fails to setData

        """
        logging.debug(result)
        if self.isScanning is False:
            return
        try:
            index = self._addressDict[result["IP Address"]]["index"]
        except KeyError:
            # Sometimes we receive a result even after stopping
            self.stopScan()
            return
        if self.scanConfig["Hostname"].checkState() == 2 and result["Ping"]:
            timeout = self.spinHostTimeout.value()
            if timeout == -1:
                timeout = 5
            self._hostnameCheck[result["IP Address"]] = functions.LookupHostname(self, result["IP Address"], timeout)
        else:
            self.addressResultsCount += 1
        for k, v in result.items():
            try:
                self.ipModel.setData(self.ipModel.index(index, self.ipHeaders.index(k)), v)
            except Exception as e:
                logging.info("onTimerCheck::Exception: %s, k=%s, v=%s" % e, k, v)

    @property
    def scanParams(self):
        """Returns current user selected scan parameters"""
        params = {}
        for label, chkBox in self.scanConfig.items():
            params[label] = chkBox.checkState()
        del params["Hostname"]
        return params

    def clearIpListItems(self):
        self.ipModel.removeRows(0, self.ipModel.rowCount())

    def cleanScan(self):
        self._addressResults = []
        self._addressDict = {}
        self._addresses = {}
        self._hostnameCheck = {}
        self._hostnameCheckThreads = {}
        self.setScanIcons(start=True)

    def closeEvent(self, event):
        self.stopScan()
        self.saveConfig()
        if self.splash:
            self.splash.close()
        event.accept()

    def createMenuBar(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        settingsMenu = mainMenu.addMenu('&Settings')
        scanMenu = settingsMenu.addMenu('&Clear Scan History')
        helpMenu = mainMenu.addMenu('&Help')
        menuItem = namedtuple("MenuItem", ["name", "shortcut", "tip", "event"])
        items = [
            (menuItem("&Exit", "Ctrl+Q", "Exit application...", self.close), fileMenu),
            (menuItem("&Preferences", "Ctrl+P", "Open preferences...", self.showPreferences), settingsMenu),
            (menuItem("&About", "Ctrl+F1", "About", self.showAbout), helpMenu),
            (menuItem("&All", "", "Clears and resets scan history", self.showAbout), scanMenu),
            (menuItem("&Range Scan", "", "Clears and resets range scan History", self.showAbout), scanMenu),
            (menuItem("&Custom IP Scan", "", "Clears and resets custom scan history", self.showAbout), scanMenu),
        ]
        for item, menu in items:
            m = QAction(item.name, self)
            m.setShortcut(item.shortcut)
            m.setStatusTip(item.tip)
            m.triggered.connect(item.event)
            menu.addAction(m)

    def createIpModel(self, parent):
        model = QStandardItemModel(0, 6, parent)
        for col, header in enumerate(self.ipHeaders):
            logging.info("Adding column %s" % str(header))
            model.setHeaderData(col, Qt.Horizontal, header)
        return model

    def initGUI(self):
        row = 0
        widget = QWidget()
        self.setCentralWidget(widget)
        self.grid = QGridLayout()
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        # self.grid.setColumnStretch(4, 1)
        self.grid.setSpacing(5)
        widget.setLayout(self.grid)

        # scan range
        gboxScanLayout = QHBoxLayout()
        gboxScan = QGroupBox("Scan Range", self)
        gboxScan.setLayout(gboxScanLayout)
        self.grid.addWidget(gboxScan, row, 0, 1, 2)

        self.startIp = QComboBox(self)
        self.startIp.setEditable(True)
        self.endIp = QComboBox(self)
        self.endIp.setEditable(True)
        gboxScanLayout.addWidget(self.startIp)
        gboxScanLayout.addWidget(self.endIp)

        self.btnScan = QToolButton(self)
        self.btnScan.clicked.connect(self.onScan)
        self.btnScan.setIcon(QIcon(START_ICON))
        self.btnScan.setIconSize(QSize(48, 32))
        gboxScanLayout.addWidget(self.btnScan)

        # custom scan
        row += 1
        gboxCustomScanLayout = QHBoxLayout()
        gboxCustomScan = QGroupBox("Custom Scan Range", self)
        gboxCustomScan.setLayout(gboxCustomScanLayout)
        self.grid.addWidget(gboxCustomScan, row, 0, 1, 2)
        self.stringIp = QComboBox(self)
        self.stringIp.setEditable(True)
        gboxCustomScanLayout.addWidget(self.stringIp)
        self.btnCustomScan = QToolButton(self)
        self.btnCustomScan.setIcon(QIcon(START_ICON))
        self.btnCustomScan.setIconSize(QSize(48, 32))
        self.btnCustomScan.clicked.connect(self.onScanCustom)
        gboxCustomScanLayout.addWidget(self.btnCustomScan)

        # scan configuration
        row += 1
        scanConfBox = QHBoxLayout()
        gboxScanConfig = QGroupBox("Scan Configurations", self)
        gboxScanConfig.setLayout(scanConfBox)
        timeoutLabel = QLabel(self)
        timeoutLabel.setText("Hostname Timeout [-1=5s]")
        self.spinHostTimeout = QSpinBox(self)
        self.spinHostTimeout.setMinimum(-1)
        self.spinHostTimeout.setMaximum(99)
        self.spinHostTimeout.setValue(int(self.config["scanConfig"]["hostnameTimeout"]))
        self.spinHostTimeout.valueChanged.connect(self.saveConfig)
        scanConfBox.addWidget(timeoutLabel)
        scanConfBox.addWidget(self.spinHostTimeout)
        self.scanConfig = {}
        for label in ["Hostname", "MAC Address", "Manufacturer"]:
            self.scanConfig[label] = QCheckBox(label, self)
            self.scanConfig[label].setCheckState(self.config["scanConfig"][label])
            self.scanConfig[label].stateChanged.connect(partial(self.onScanCheckBox, label))
            scanConfBox.addWidget(self.scanConfig[label])
        self.grid.addWidget(gboxScanConfig, row, 0)

        # results
        row += 1
        self.grid.setRowStretch(row, 1)
        gboxLayout = QVBoxLayout()
        gboxResults = QGroupBox("Results", self)
        gboxResults.setLayout(gboxLayout)
        self.chkShowAlive = QCheckBox("Show Alive Only", self)
        self.chkShowAlive.setCheckState(self.config["filter"]["showAliveOnly"])
        self.chkShowAlive.stateChanged.connect(self.onFilterCheckBox)
        self.chkShowAlive.setTristate(False)
        gboxLayout.addWidget(self.chkShowAlive)
        self.ipList = QTreeView()
        self.ipList.setRootIsDecorated(False)
        self.ipList.setAlternatingRowColors(True)
        self.ipModel = self.createIpModel(self.ipList)
        self.ipList.setModel(self.ipModel)
        gboxLayout.addWidget(self.ipList)
        self.grid.addWidget(gboxResults, row, 0, -1, -1)

    def initSplash(self):
        self.splash = QSplashScreen(QPixmap(appPath + "splash.png"), Qt.WindowStaysOnTopHint)
        self.splash.show()
        QTimer.singleShot(SPLASH_TIMEOUT, lambda: self.splash.close())

    def initTimers(self):
        logging.debug("MainWindow->initTimers")
        self.timerCheck = QTimer()
        self.timerCheck.timeout.connect(self.onTimerCheck)

    def loadConfig(self):
        """Try to load settings or create/overwrite config file"""
        logging.info("MainWindow->loadConfig")
        try:
            with open(self.configPath, "r") as file:
                data = json.load(file)
                file.close()
                self.config.update(data)
        except Exception as e:
            logging.info("Could Not Load Settings File:", e)
            self.saveConfig()

    def onFilterCheckBox(self, state):
        self.saveConfig()

    def onScan(self, event):
        """Scan range"""
        logging.info("MainWindow->onScan")
        if self.isScanning is True:
            self.stopScan()
            return
        self.prepareScan()

        start = self.startIp.currentText()
        end = self.endIp.currentText()
        if not start or not end:
            logging.info("Invalid IP range defined. Start and/or end range empty.")
            self.stopScan()
            return
        self.updateScanHistory()

        ipRange = start + "-" + end
        self.parseIpthread = functions.ParseIpRange(self, ipRange)

    def onScanCheckBox(self, label):
        logging.info("MainWindow->onScanCheckBox %s" % label)
        value = self.scanConfig[label].checkState()
        self.config["scanConfig"][label] = value
        if label == "MAC Address" and value is 0:
            self.scanConfig["Manufacturer"].setCheckState(2)
        elif label == "Manufacturer" and value is 2:
            self.scanConfig["MAC Address"].setCheckState(0)

    def onScanCustom(self):
        logging.info("MainWindow->onScanCustom")
        if self.isScanning is True:
            self.stopScan()
            return
        self.prepareScan()

        stringIp = self.stringIp.currentText()
        if not stringIp:
            self.stopScan()
            return

        self.updateScanHistory()
        stringIp = stringIp.split(",")
        for ipRange in stringIp:
            self.parseIpthread = functions.ParseIpRange(self, ipRange)

    def onTimerCheck(self):
        """Check if we have received any scan results"""
        logging.debug("MainWindow->onTimerCheck")
        logging.debug("_hostnameCheck: {0}".format(self._hostnameCheck))

        msg = "Scanning: Addresses Pinged = {0}/{1}, ".format(self.addressResultsCount, self.ipModel.rowCount())
        msg += "Checking Hostname(s) = {0}".format(len(self._hostnameCheck))
        if self.addressResultsCount == self.ipModel.rowCount() and not self._hostnameCheck:
            self.setStatusBar("Finished " + msg)
            self.stopScan()
            return
        self.setStatusBar(msg)

        rm = []
        for address, thread in self._hostnameCheckThreads.items():
            thread.timeout -= TIMER_CHECK_MS
            if thread.timeout < 0:
                rm.append(address)

        for addr in rm:
            try:
                self._hostnameCheck[addr].terminate()
            except Exception as e:
                logging.debug("MainWindow->onTimerCheck: %s" % e)

            del self._hostnameCheck[addr]
            del self._hostnameCheckThreads[addr]

        if len(self._hostnameCheckThreads.keys()) > MAX_HOSTNAME_CHECKS:
            return
        elif self._hostnameCheck:
            for address, thread in self._hostnameCheck.items():
                if address in self._hostnameCheckThreads:
                    continue
                self._hostnameCheckThreads[address] = thread
                self._hostnameCheckThreads[address].start()
                return

    def prepareScan(self):
        self.isScanning = True
        self.setStatusBar("Scanning ...")
        self.setScanIcons(start=False)
        self.clearIpListItems()

    def restoreConfigState(self):
        """Restore application state from config"""
        logging.info("Menubar->Help->restoreConfigState")
        self.restoreScanHistory()

        try:
            w, h = self.config["size"]
            w, h = int(w), int(h)
            self.resize(w, h)
        except Exception as e:
            logging.debug("restoreConfigState Exception: %s" % e)

    def restoreScanHistory(self):
        self.startIp.addItems(self.config["ipStartHistory"])
        self.endIp.addItems(self.config["ipEndHistory"])

        if self.config["ipStartHistory"] == []:
            self.startIp.addItem("192.168.0.0")

        if self.config["ipEndHistory"] == []:
            self.endIp.addItem("192.168.0.255")

        self.stringIp.addItems(self.config["customScanHistory"])
        if self.config["customScanHistory"] == []:
            self.stringIp.addItem("192.168.0.1-255")

    def saveConfig(self):
        logging.info("Menubar->Help->saveConfig")

        try:
            self.config["scanConfig"]["hostnameTimeout"] = self.spinHostTimeout.value()
            self.config["filter"]["showAliveOnly"] = self.chkShowAlive.checkState()
            self.config["size"] = [self.frameGeometry().width(),
                                   self.frameGeometry().height()]
            for label in ["Hostname", "MAC Address", "Manufacturer"]:
                self.config["scanConfig"][label] = self.scanConfig[label].checkState()
        except Exception as e:
            logging.debug(e)

        try:
            with open(self.configPath, "w") as file:
                json.dump(self.config, file, sort_keys=True, indent=2)
        except PermissionError:
            logging.info("PermissionError: you do not permission to save config")
        logging.debug(self.config)

    def setScanIcons(self, start=True):
        if start:
            icon = START_ICON
        else:
            icon = STOP_ICON
        self.btnScan.setIcon(QIcon(icon))
        self.btnCustomScan.setIcon(QIcon(icon))

    def setStatusBar(self, message, timeout=0):
        logging.debug("MainWindow->setStatusBar")
        self.statusBar().showMessage(message, timeout)

    def showAbout(self):
        """Show the About wndow"""
        logging.info("Menubar->Help->showAbout")
        AboutDialog(self)

    def showPreferences(self):
        """Show the About wndow"""
        logging.info("Menubar->Settings->showPreferences")
        PreferencesDialog(self, config=self.config)

    def sendScanParams(self):
        # we cannot get Manufacturer if user disables MAC
        params = self.scanParams
        if params["MAC Address"] == 0:
            params["Manufacturer"] = 0
        self.signalScanParams.emit(params)

    def startScan(self, index, address):
        self.sendScanParams()
        self.signalAddPing.emit({"index": index, "address": address})
        self.startTimerCheck()

    def startTimerCheck(self):
        logging.info("MainWindow->startTimerCheck")
        self.timerCheck.start(TIMER_CHECK_MS)

    def stopHostnameChecks(self):
        for t in self._hostnameCheckThreads.values():
            t.terminate()

    def stopParseIpThread(self):
        if self.parseIpthread:
            self.parseIpthread.terminate()
            self.parseIpthread = None

    def stopPingThread(self):
        self.signalStopScanning.emit()

    def stopTimerCheck(self):
        self.timerCheck.stop()

    def stopScan(self):
        logging.info("MainWindow->stopScan")
        self.setStatusBar("Scan Finished: Addresses Checked = {0}".format(self.addressResultsCount))
        self.isScanning = False
        self.addressResultsCount = 0
        self.stopTimerCheck()
        self.stopPingThread()
        self.stopParseIpThread()
        self.stopHostnameChecks()
        self.cleanScan()

    def updateScanHistory(self):
        """Save scan history to config"""
        logging.info("MainWindow->updateScanHistory")
        for cbox, dictKey in [(self.startIp, "ipStartHistory"),
                              (self.endIp, "ipEndHistory"),
                              (self.stringIp, "customScanHistory")]:
            items = [cbox.itemText(x) for x in range(cbox.count())]
            value = cbox.currentText()
            if value in items:
                index = items.index(value)
                del items[index]
            items.insert(0, value)

            cbox.clear()
            for item in items:
                cbox.addItem(item)

            items = items[:10]
            self.config[dictKey] = items

        self.saveConfig()


def process_sys_args():
    res = {}
    for arg in sys.argv[1:]:
        if "=" not in arg:
            continue
        key, value = arg.split("=")[:2]
        res[key.lower()] = value.lower()
    return res


def set_logging_level():
    # Logging Configuration
    try:
        v = LOG_LEVELS[SYS_ARGS["--verbose"]]
        logging.basicConfig(level=v)
    except KeyError:
        pass


def main():
    SYS_ARGS.update(process_sys_args())
    set_logging_level()
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
