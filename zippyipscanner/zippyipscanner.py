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

import os
import sys

if __name__ != "__main__":
    # this allows avoid changing relative imports
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import functions
import json
import logging
from functools import partial

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, 
                          Qt, QTime, QSize, QTimer, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from about import AboutDialog
# from updatechecker import CheckForUpdates

from version import __version__

#----- logging -----#
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STOP_ICON = 'images/stop.png'
START_ICON = 'images/start.png'
MAX_HOSTNAME_CHECKS = 5
TIMER_CHECK_MS = 100
SPLASH_TIMEOUT = 1200

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        logging.debug("MainWindow ")
                
        self._isScanning = False
        self._bitmaps = {}
        # self.SetupBitmaps()
        self._sortBy = 0
        self._addressResults = []
        self.addressResultsCount = 0
        self._addressDict = {}
        self._hostnameCheck = {}
        self._hostnameCheckThreads = {}
        self.scanTotalCount = 0
        self.pingThread = None
        self.ipHeaders = ["IP Address","Hostname","Ping","TTL","Manufacturer","MAC Address"]
        self.currentIpList = None
        
        self.setWindowTitle('Zippy IP Scanner v{0}'.format(__version__))
        self.setWindowIcon(QtGui.QIcon('zippyipscanner.ico'))
        
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
            "scanConfig": {"hostnameTimeout":"5", "Hostname":2, "Manufacturer":2, "MAC Address": 2},
            "filter": {"showAliveOnly": 2}
        }

    @property
    def config(self):
        return self._config
        
    @property
    def configPath(self):
        path = "config.json"
        return path
        
    @property
    def isScanning(self):
        return self._isScanning
        
    @isScanning.setter
    def isScanning(self, value):
        self._isScanning = value 
           
    @pyqtSlot(str)
    def lookupTimedOut(self, address):
        logging.info(address)
        del self._hostnameCheck[address]
        
    @pyqtSlot(str)
    def receiveDebugSignal(self, str):
        logging.debug(str)  
        
    @pyqtSlot(dict)
    def receiveHostnameResult(self, result):
        logging.debug(result)
           
        if not self.isScanning:
            return
            
        try:
            index = self._addressDict[result["address"]]["index"] 
            self.ipModel.setData(self.ipModel.index(index, self.ipHeaders.index("Hostname")), result["hostname"])
            del self._hostnameCheck[result["address"]]
            del self._hostnameCheckThreads[result["address"]]
        except KeyError: 
            logging.debug(KeyError)
        
    @pyqtSlot(dict)
    def receiveScanResult(self, result):
        logging.debug(result)
        
        if not self.isScanning:
            return
        
        index = self._addressDict[result["IP Address"]]["index"]        
        if self.scanConfig["Hostname"].checkState() == 2 and result["Ping"]:            
            timeout = self.spinHostTimeout.value()
            if timeout == -1:
                timeout = 5
            self._hostnameCheck[result["IP Address"]] = functions.LookupHostname(self, result["IP Address"], timeout)
        self.addressResultsCount += 1
        for k, v in result.items():            
            try:
                self.ipModel.setData(self.ipModel.index(index, self.ipHeaders.index(k)), v)                
            except Exception as e:
                logging.info("onTimerCheck::Exception: %s, k=%s, v=%s" % e, k, v)
        
    @property
    def scanParams(self):
        params = {}
        for label, chkBox in self.scanConfig.items():
            params[label] = chkBox.checkState()
        del params["Hostname"]
        return params
        
    def appendIpEntry(self, data):
        self.ipModel.insertRow(self.ipModel.rowCount())
        for col, header in enumerate(self.ipHeaders):
            try:
                self.ipModel.setData(self.ipModel.index(self.ipModel.rowCount()-1, col), data[header])
            except:
                pass
           
    def closeEvent(self, event):
        self.stopScan()
        self.saveConfig()
        if self.splash:
            self.splash.close()
        event.accept()
        
    def clearIpListItems(self):
        self.ipModel.removeRows(0, self.ipModel.rowCount())
    
    def cleanScan(self):        
        self._addressResults = []
        self._addressDict = {}
        self._addresses = {}
        self._hostnameCheck = {}
        self._hostnameCheckThreads = {}
        self.pingThread = None
        
        self.btnScan.setIcon(QtGui.QIcon(START_ICON))
        self.btnCustomScan.setIcon(QtGui.QIcon(START_ICON))
        self.isScanning = False
        
    def createMenuBar(self):
        exitAction = QAction("&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip('Exit application...')
        # exitAction.triggered.connect(QtCore.QCoreApplication.instance().quit)
        exitAction.triggered.connect(self.close)
        
        aboutAction = QAction("&About", self)
        aboutAction.setShortcut("Ctrl+F1")
        aboutAction.setStatusTip('About')
        aboutAction.triggered.connect(self.showAbout)
        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        helpMenu = mainMenu.addMenu('&Help')
        helpMenu.addAction(aboutAction)
        
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
        self.btnScan.setIcon(QtGui.QIcon(START_ICON))
        self.btnScan.setIconSize(QSize(48,32))
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
        self.btnCustomScan.setIcon(QtGui.QIcon(START_ICON))
        self.btnCustomScan.setIconSize(QSize(48,32))
        self.btnCustomScan.clicked.connect(self.onCustomScan)
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
        self.grid.addWidget(gboxScanConfig, row, 0)#, 1, 2)

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
        self.splash = QSplashScreen(QPixmap("splash.png"), QtCore.Qt.WindowStaysOnTopHint)
        self.splash.show()
        
        QtCore.QTimer.singleShot(SPLASH_TIMEOUT, lambda: self.splash.close())
        
    def initTimers(self):
        logging.debug("MainWindow->initTimers")
        self.timerCheck = QTimer()
        self.timerCheck.timeout.connect(self.onTimerCheck)
    
    def loadConfig(self):
        """ try to load settings or create/overwrite config file"""
        logging.info("MainWindow->loadConfig")
        try:
            with open(self.configPath, "r") as file:
                data = json.load(file)
                file.close()
                self.config.update(data)
        except Exception as e:
            logging.info("Could Not Load Settings File:", e)
            self.saveConfig()
    
    def onCustomScan(self):
        logging.info("MainWindow->onCustomScan")
        
        if self.isScanning is True:
            self.stopScan()
            return
        self.isScanning = True
        self.setStatusBarText("Scanning ...")
        self.btnScan.setIcon(QtGui.QIcon(STOP_ICON))
        self.btnCustomScan.setIcon(QtGui.QIcon(STOP_ICON))
        self.clearIpListItems()
        
        stringIp = self.stringIp.currentText()
        if not stringIp:
            self.stopScan()
            return
        
        self.updateScanHistory()
        addresses = []
        stringIp = stringIp.split(",")
        for ip in stringIp:
            res = self.parseIpString(ip)
            for add in res:
                if add in addresses:
                    continue
                addresses.append(add)
        
        self._addresses = addresses
        self.startScan()
        
    def onFilterCheckBox(self, state):
        self.saveConfig()
            
    def onScan(self, event):
        """Scan range"""
        logging.info("MainWindow->onScan")
        if self.isScanning is True:
            self.stopScan()
            return
        self.isScanning = True
        self.setStatusBarText("Scanning ...")
        self.btnScan.setIcon(QtGui.QIcon(STOP_ICON))
        self.btnCustomScan.setIcon(QtGui.QIcon(STOP_ICON))
        self.clearIpListItems()

        startIp = self.startIp.currentText()
        endIp = self.endIp.currentText()
        if not startIp and not endIp:
            logging.info("No valid IP range defined")
            self.stopScan()
            return
        if not endIp:
            pass

        self.updateScanHistory()

        start = [int(x) for x in startIp.split(".")]
        end = [int(x) for x in endIp.split(".")]
        if start[0:2] != end[0:2]:
            self.stopScan()
            return

        # is end IP before start IP?
        for i in range(4):
            if start[i] > end[i]:
                start, end = end, start
                break

        logging.info("Populate IP range list from %s - %s" % (start, end))
        temp = start
        addresses = []
        addresses.append(startIp)

        #increment address until it reaches the end ip
        logging.debug("{0}, {1}".format(temp, end))
        while temp != end:
            start[3] += 1
            ip = ".".join([str(x) for x in temp])
            addresses.append(ip)

            if temp == end:
                break
            if temp[3] >= 256:
                temp[3] = 0
                temp[2] += 1

        self._addresses = addresses
        self.startScan()
        
    def onScanCheckBox(self, label):
        logging.info("MainWindow->onScanCheckBox %s" % label)
        value = self.scanConfig[label].checkState()
        if label == "MAC Address" and value is 0:
            self.scanConfig["Manufacturer"].setCheckState(2)
        elif label == "Manufacturer" and value is 2:
            self.scanConfig["MAC Address"].setCheckState(0)
            
    def onTimerCheck(self):
        """Check if we have received any scan results"""
        logging.debug("MainWindow->onTimerCheck")        
        logging.debug("_hostnameCheck: {0}".format(self._hostnameCheck))
        
        msg = "Scanning: Addresses Pinged = {0}/{1}, ".format(self.addressResultsCount, len(self._addresses))
        msg += "Checking Hostname(s) = {0}".format(len(self._hostnameCheck))
        if self.addressResultsCount == len(self._addresses) and not self._hostnameCheck:
            self.setStatusBarText("Finished "+msg)
            self.stopScan()
            return
        self.setStatusBarText(msg)
        
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
                                
    def parseIpString(self, ip):
        addresses = []
        # range?
        try:
            ipStart, ipEnd = ip.split("-")
            ipBase = ipStart.split(".")[:-1]
            ipEnd = ".".join(ipBase) + "." + ipEnd
            ipStart = [int(x) for x in ipStart.split(".")]
            if len(ipStart) != 4:
                return []
            ipEnd = [int(x) for x in ipEnd.split(".")]

            if ipStart[3] > 256:
                ipStart[3] == 256
            if ipEnd[3] > 256:
                ipEnd[3] == 256

            # is end IP before start IP?
            if ipStart[3] > ipEnd[3]:
                ipStart, ipEnd = ipEnd, ipStart
            elif ipStart[3] == ipEnd[3]:
                return [".".join([str(x) for x in ipStart])]

            logging.info("Populate IP range list from %s - %s" % (ipStart, ipEnd))

            temp = ipStart
            addresses.append(".".join([str(x) for x in temp]))
            #increment address until it reaches the end ip
            i = ipStart[3]
            while temp != ipEnd:
                ipStart[3] += 1
                ip = ".".join([str(x) for x in temp])
                addresses.append(ip)
            return addresses

        except Exception as e:
            logging.debug(e)

        # single ip?
        try:
            ipAdd = [int(x) for x in ip.split(".")]
            if len(ipAdd) != 4:
                return []
            if ipAdd[3] > 256:
                return []
            addresses.append(ip)
            return addresses

        except Exception as e:
            logging.debug(e)

        return addresses
    
    def restoreConfigState(self):
        """Restore application state from config"""
        logging.info("Menubar->Help->restoreConfigState")
        for item in self.config["ipStartHistory"]:
            self.startIp.addItem(item)
        for item in self.config["ipEndHistory"]:
            self.endIp.addItem(item)
            
        if self.config["ipStartHistory"] == []:
            self.startIp.addItem("192.168.0.0")

        if self.config["ipEndHistory"] == []:
            self.endIp.addItem("192.168.0.255")
            
        # restore previous values
        for item in self.config["customScanHistory"]:
            self.stringIp.addItem(item)
        if self.config["customScanHistory"] == []:
            self.stringIp.addItem("192.168.0.1-255")
        try:    
            w, h = self.config["size"]
            w, h = int(w), int(h)
            self.resize(w, h)
        except:
            pass
            
    def saveConfig(self):
        logging.info("Menubar->Help->saveConfig")
        
        self.config["scanConfig"]["hostnameTimeout"] = self.spinHostTimeout.value()
        self.config["filter"]["showAliveOnly"] = self.chkShowAlive.checkState()
        self.config["size"] = [self.frameGeometry().width(),
                               self.frameGeometry().height()]
        
        with open(self.configPath, "w") as file:
            json.dump(self.config, file, sort_keys=True, indent=2)
        logging.debug(self.config)
        
    def setStatusBarText(self, message, timeout=0):
        logging.debug("MainWindow->setStatusBarText")
        self.statusBar().showMessage(message, timeout)
    
    def showAbout(self):
        """Show the About wndow"""
        logging.info("Menubar->Help->showAbout")
        AboutDialog(self)
        
    def startScan(self):
        logging.info("startScan: addresses={0}".format(len(self._addresses)))
        addresses = self._addresses
        self.scanTotalCount = len(addresses) 
        for addr in self._addresses:
            self._addressDict[addr] = {"index": self.ipModel.rowCount()}
            self.appendIpEntry({"IP Address": addr})

        self.pingThread = functions.PingAddress(self, addresses, self.scanParams)
        self.timerCheck.start(TIMER_CHECK_MS)
    
    def startTimerCheck(self):
        logging.info("MainWindow->startTimerCheck")
        self.timerCheck.start(TIMER_CHECK_MS)
        
    def stopScan(self):
        logging.info("MainWindow->stopScan")
        self.addressResultsCount = 0
        self.timerCheck.stop()
        if self.pingThread:
            self.pingThread.terminate()
        for t in self._hostnameCheckThreads.values():
            t.terminate()
        self.cleanScan()
        self.setStatusBarText("Scan Finished: Addresses Checked = {0}".format(self.scanTotalCount))
        
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
            try:
                items = items[:10]
            except:
                pass
            self.config[dictKey] = items
            
        self.saveConfig()

def main():    
    app = QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()