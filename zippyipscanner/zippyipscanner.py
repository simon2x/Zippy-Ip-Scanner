#!/usr/bin/python3
# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>
Copyright (c) 2018 by Simon Wu <Zippy Ip Scanner>
Released subject to the GNU Public License
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import os
import sys

if __name__ != "__main__":
    # this allows avoid changing relative imports
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import csv
import base
import functions
import json
import logging
import platform
import queue
import subprocess
import threading
import time
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from version import __version__
from collections import OrderedDict
from about import AboutDialog
from updatechecker import CheckForUpdates
from splashscreen import SplashScreen
from portable import resource_path

#----- logging -----#
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainFrame(wx.Frame):

    def __init__(self, portable=False):
        if portable:
            title = 'Zippy IP Scanner v{0} - Portable'.format(__version__)
        else:
            title = 'Zippy IP Scanner v{0}'.format(__version__)

        wx.Frame.__init__(self, None, title=title)
        self.CreateStatusBar()
        self.CreateMenu()

        self._aboutFrame = None
        self._checkUpdateDialog = None

        self._menus = {}
        self._btns = {}
        self._bitmaps = {}
        self.SetupBitmaps()
        self._icons = {}
        self._data = {}
        self._sortBy = 0
        self._hostnameCache = {}
        self._addressResults = []
        self._addressDict = {}
        self._hostnameCheck = []
        self.scanTotalCount = 0
        self.pingThread = None
        self.ipHeaders = ["IP Address","Hostname","Ping","TTL","Manufacturer","MAC Address"]
        self.currentIpList = None
        self.clipBoard = wx.Clipboard()

        # this is passed to the PingAddress thread so we know
        # when to end and/or user intervenes to stop early
        self._stopThread = []

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # ranged scan static box
        sbox = wx.StaticBox(panel, label="Scan Range")
        sboxSizerScanRange = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        self.startIp = wx.ComboBox(panel)
        self.endIp = wx.ComboBox(panel)
        sboxSizerScanRange.Add(self.startIp, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        sboxSizerScanRange.Add(self.endIp, 1, wx.ALL|wx.ALIGN_CENTRE, 5)

        # restore previous values
        for item in self.app.config["ipStartHistory"]:
            self.startIp.Append(item)
        for item in self.app.config["ipEndHistory"]:
            self.endIp.Append(item)

        if self.app.config["ipStartHistory"] == []:
            self.startIp.SetValue("192.168.0.0")
        else:
            self.startIp.SetSelection(0)

        if self.app.config["ipEndHistory"] == []:
            self.endIp.SetValue("192.168.0.256")
        else:
            self.endIp.SetSelection(0)

        self.btnScan = wx.Button(panel, label="Scan", name="", style=wx.BU_NOTEXT)
        self.btnScan.SetBitmap(self.bitmaps["start"])
        self.btnScan.Bind(wx.EVT_BUTTON, self.OnScan)
        sboxSizerScanRange.Add(self.btnScan, 0, wx.ALL, 5)
        sizer.Add(sboxSizerScanRange, 0, wx.ALL|wx.EXPAND, 5)

        # custom scan static box
        sbox = wx.StaticBox(panel, label="Custom Scan")
        sboxSizerCustomScan = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        self.stringIp = wx.ComboBox(panel, value="192.168.0.0-100")
        sboxSizerCustomScan.Add(self.stringIp, 1, wx.ALL|wx.ALIGN_CENTRE, 5)

        self.btnCustomScan = wx.Button(panel, label="Scan", name="", style=wx.BU_NOTEXT)
        self.btnCustomScan.SetBitmap(self.bitmaps["start"])
        self.btnCustomScan.Bind(wx.EVT_BUTTON, self.OnCustomScan)
        sboxSizerCustomScan.Add(self.btnCustomScan, 0, wx.ALL, 5)
        sboxSizerCustomScan.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
        sizer.Add(sboxSizerCustomScan, 0, wx.ALL|wx.EXPAND, 5)

        # restore previous values
        for item in self.app.config["customScanHistory"]:
            self.stringIp.Append(item)
        if self.app.config["customScanHistory"] == []:
            self.stringIp.SetValue("192.168.0.1-256")
        else:
            self.stringIp.SetSelection(0)

        # custom scan static box
        sbox = wx.StaticBox(panel, label="Scan Configuration")
        sboxSizerScanConfig = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        hostTimeoutLabel = wx.StaticText(panel, label="Hostname Timeout [-1=5s] (s):")
        self.spinHostTimeout = wx.SpinCtrl(panel, min=-1, max=90, value="-1")
        self.spinHostTimeout.SetValue(self.app.config["scanConfig"]["hostnameTimeout"])
        sboxSizerScanConfig.Add(hostTimeoutLabel, 0, wx.ALL|wx.CENTRE, 5)
        sboxSizerScanConfig.Add(self.spinHostTimeout, 0, wx.ALL, 5)
        self.scanConfig = {}
        for label in ["Hostname", "MAC Address", "Manufacturer"]:
            self.scanConfig[label] = wx.CheckBox(panel, label=label)
            self.scanConfig[label].Bind(wx.EVT_CHECKBOX, self.OnScanCheckBox)
            self.scanConfig[label].SetValue(self.app.config["scanConfig"][label])
            sboxSizerScanConfig.Add(self.scanConfig[label], 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sboxSizerScanConfig, 0, wx.ALL|wx.EXPAND, 5)

        # results box
        sbox = wx.StaticBox(panel, label="Results")
        sboxSizerResults = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        hSizerFilter = wx.BoxSizer(wx.HORIZONTAL)
        self.chkShowAlive = wx.CheckBox(panel, label="Show Alive Only")
        self.chkShowAlive.Bind(wx.EVT_CHECKBOX, self.OnFilterCheckBox)
        self.chkShowAlive.SetValue(self.app.config["filter"]["showAliveOnly"])
        hSizerFilter.Add(self.chkShowAlive, 0, wx.ALL|wx.EXPAND, 5)
        sboxSizerResults.Add(hSizerFilter, 0, wx.ALL|wx.EXPAND, 5)

        self.ipList = base.BaseList(panel)
        for col, header in enumerate(self.ipHeaders):
            self.ipList.InsertColumn(col, header)
        self.ipList.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumn)
        self.ipList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnIpListRightClick)
        self.ipList.Hide()

        self.ipListFilter = base.BaseList(panel)
        for col, header in enumerate(self.ipHeaders):
            self.ipListFilter.InsertColumn(col, header)
        self.ipListFilter.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumn)
        self.ipListFilter.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnIpListRightClick)
        sboxSizerResults.Add(self.ipListFilter, 3, wx.ALL|wx.EXPAND, 5)


        self.OnFilterCheckBox()
        sizer.Add(sboxSizerResults, 1, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)

        self.SetMinSize(sizer.Fit(self))
        self.Show()

        panel.SetSizer(sizer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self._hosts = {}
        self.timerCheck = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimerCheck, self.timerCheck)

        self.timerHostTimeout = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimerHostTimeout, self.timerHostTimeout)
        self.timerHostTimeout.Start(1000)

        try:
            self.SetIcon(wx.Icon(resource_path("zippyipscanner.ico")))
        except:
            pass

    @property
    def app(self):
        return wx.GetApp()

    @property
    def statusBar(self):
        return self.GetStatusText()

    @statusBar.setter
    def statusBar(self, value):
        return self.SetStatusText(str(value))

    @property
    def bitmaps(self):
        return self._bitmaps

    @property
    def scanParams(self):
        params = {}
        for label, chkBox in self.scanConfig.items():
            params[label] = chkBox.GetValue()
        del params["Hostname"]
        return params

    def CleanScan(self):
        self._stopThread = []
        self._addressResults = []

        self._addressDict = {}
        self._hostnameCheck = []
        self.pingThread = None

        self.btnScan.SetBitmap(self.bitmaps["start"])
        self.btnCustomScan.SetBitmap(self.bitmaps["start"])

        self.btnScan.SetName("")
        self.btnCustomScan.SetName("")

    def CreateMenu(self):
        menubar = wx.MenuBar()

        menuFile = wx.Menu()
        fileMenus = [("Exit", "Exit Program", wx.ID_EXIT)]
        for item, helpStr, wxId in fileMenus:
            item = menuFile.Append(wxId, item, helpStr)
            self.Bind(wx.EVT_MENU, self.OnMenu, item)
        menubar.Append(menuFile, "&File")

        menuHelp = wx.Menu()
        helpMenus = [("Check for updates", "Check for updates", wx.ID_SETUP),
                     ("About\tCtrl+F1", "Import Images From Folder", wx.ID_ABOUT)]
        for item, helpStr, wxId in helpMenus:
            item = menuHelp.Append(wxId, item, helpStr)
            self.Bind(wx.EVT_MENU, self.OnMenu, item)

        menubar.Append(menuHelp, "&Help")
        self.menubar = menubar
        self.SetMenuBar(menubar)

    def GetHostNames(self, msg):
        hostnames = functions.LookupHostnames(self._addresses)
        logging.info(hostnames)
        for index, hostname in hostnames:
            self.ipList.SetItem(index, 1, hostname)

    def ParseIpString(self, ip):
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
            print(e)

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
            print(e)

        return addresses

    def OnFilterCheckBox(self, event=None):
        self.OnColumn()

    def OnListContextMenu(self, event):
        try:
            e = event.GetEventObject()
            name = e.GetName()
        except:
            id = event.GetId()
            name = e.GetLabel(id)

        selection = self.currentIpList.GetFirstSelected()
        content = []
        if name == "All":
            while selection != -1:
                c = []
                for n,s in enumerate(self.ipHeaders):
                    c.append(s+"="+self.currentIpList.GetItemText(selection, col=n))
                content.append(",".join(c))
                selection = self.currentIpList.GetNextSelected(selection)
            content = "\n".join(content)
        else:
            while selection != -1:
                iColumn = self.ipHeaders.index(name)
                content.append(self.currentIpList.GetItemText(selection, col=iColumn))
                selection = self.currentIpList.GetNextSelected(selection)
            content = ",".join(content)

        if self.clipBoard.Open():
            self.clipBoard.SetData(wx.TextDataObject(content))
            # keeps data on exit, X11 not supported
            self.clipBoard.Flush()
            self.clipBoard.Close()

    def OnIpListRightClick(self, event):
        """ handle both ip list and ip filtered list item context menu here"""
        ipList = event.GetEventObject()
        self.currentIpList = ipList
        selection = ipList.GetFirstSelected()
        if selection == -1:
            return

        menu = wx.Menu()
        copyMenu = wx.Menu()
        menu.AppendSubMenu(copyMenu, "Copy")
        for label in ["All","IP Address","Hostname","Manufacturer","MAC Address"]:
            if not label:
                menu.AppendSeparator()
                continue
            item = copyMenu.Append(wx.ID_ANY, label)

        menu.Bind(wx.EVT_MENU, self.OnListContextMenu)
        self.PopupMenu(menu)

    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()

    def OnClose(self, event):
        """ save settings before quitting """
        for label, chkBox in self.scanConfig.items():
            self.app.config["scanConfig"][label] = chkBox.GetValue()
        self.app.config["scanConfig"]["hostnameTimeout"] = self.spinHostTimeout.GetValue()
        self.app.config["filter"]["showAliveOnly"] = self.chkShowAlive.GetValue()

        self.app.SaveConfig()
        event.Skip()

    def OnColumn(self, event=None):
        """ here we sort items by the column clicked """
        items = []
        for row in range(self.ipList.GetItemCount()):
            item = []
            if self.chkShowAlive.GetValue() and not self.ipList.GetItem(row, 2).GetText():
                continue
            for col in range(self.ipList.GetColumnCount()):
                text = self.ipList.GetItem(row, col).GetText()
                item.append(text)
            items.append(item)

        if not event:
            index = self._sortBy
            sorted_x = sorted(items, key=lambda x: x[index].lower())
        else:
            index = event.GetColumn()

            if self._sortBy == index:
                # already sorted, this time reverse order
                sorted_x = sorted(items, key=lambda x: x[index].lower())
                sorted_x = reversed(sorted_x)
            else:
                sorted_x = sorted(items, key=lambda x: x[index].lower())
                self._sortBy = index

        self.ipListFilter.DeleteAllItems()
        for x in sorted_x:
            self.ipListFilter.Append(x)

    def OnCustomScan(self, event):
        e = event.GetEventObject()
        name = e.GetName()

        if name == "Stop":
            self.StopScan()
            return

        self.statusBar = "Scanning ..."
        self.ipList.DeleteAllItems()
        self.ipListFilter.DeleteAllItems()

        self.btnScan.SetName("Stop")
        self.btnCustomScan.SetName("Stop")
        self.btnScan.SetBitmap(self.bitmaps["stop"])
        self.btnCustomScan.SetBitmap(self.bitmaps["stop"])

        stringIp = self.stringIp.GetValue()
        if not stringIp:
            self.StopScan()
            return

        self.UpdateScanHistory()
        addresses = []
        stringIp = stringIp.split(",")
        for ip in stringIp:
            res = self.ParseIpString(ip)
            for add in res:
                if add in addresses:
                    continue
                addresses.append(add)

        self._addresses = addresses
        for addr in self._addresses:
            self._addressDict[addr] = {"index": self.ipList.Append([addr])}

        self.pingThread = functions.PingAddress(addresses, self._addressResults, self._stopThread, self.scanParams)

        self.scanTotalCount = len(addresses)
        self.StartTimerCheck()

    def OnMenu(self, event):
        e = event.GetEventObject()
        id = event.GetId()

        if id == wx.ID_ABOUT:
            if self._aboutFrame:
                self._aboutFrame.Raise()
            else:
                self._aboutFrame = AboutDialog()

        elif id == wx.ID_EXIT:
            self.Close()

        elif id == wx.ID_SETUP:
            if self._checkUpdateDialog:
                self._checkUpdateDialog.Raise()
            else:
                self._checkUpdateDialog = CheckForUpdates()

    def OnScan(self, event):
        e = event.GetEventObject()
        name = e.GetName()

        if name == "Stop":
            self.StopScan()
            return

        self.statusBar = "Scanning ..."
        self.ipList.DeleteAllItems()
        self.ipListFilter.DeleteAllItems()

        self.btnScan.SetName("Stop")
        self.btnCustomScan.SetName("Stop")
        self.btnScan.SetBitmap(self.bitmaps["stop"])
        self.btnCustomScan.SetBitmap(self.bitmaps["stop"])

        startIp = self.startIp.GetValue()
        endIp = self.endIp.GetValue()

        if not startIp and not endIp:
            logging.info("No valid IP range defined")
            e.SetLabel("Start")
            return
        if not endIp:
            pass

        self.UpdateScanHistory()

        start = [int(x) for x in startIp.split(".")]
        end = [int(x) for x in endIp.split(".")]
        if start[0:2] != end[0:2]:
            self.StopScan()
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
        print(temp,end)
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
        for addr in self._addresses:
            self._addressDict[addr] = {"index": self.ipList.Append([addr])}

        self.pingThread = functions.PingAddress(addresses, self._addressResults, self._stopThread, self.scanParams)

        self.scanTotalCount = len(addresses)
        self.StartTimerCheck()

    def OnScanCheckBox(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        value = e.GetValue()
        if label == "MAC Address" and value is False:
            self.scanConfig["Manufacturer"].SetValue(value)
        elif label == "Manufacturer" and value is True:
            self.scanConfig["MAC Address"].SetValue(value)

    def OnTimerCheck(self, event):
        if self.addressResultsCount < len(self._addressResults):
            result = self._addressResults[self.addressResultsCount]
            index = self._addressDict[result["IP Address"]]["index"]
            self.addressResultsCount += 1

            if self.scanConfig["Hostname"].GetValue() is True and result["Ping"]:
                timeout = self.spinHostTimeout.GetValue()
                if timeout == -1:
                    timeout = 5
                buffer = []
                thread = functions.LookupHostname(result["IP Address"], buffer, timeout)
                self._hostnameCheck.append((index, thread, buffer))
            for k, v in result.items():
                try:
                    self.ipList.SetItem(index, self.ipHeaders.index(k), v)
                except Exception as e:
                    print(e)

            self.OnColumn()

        msg = "Scanning: Addresses Pinged = {0}/{1}".format(self.addressResultsCount, self.scanTotalCount)
        msg += ", Hostname Checks Remaining = {0}".format(len(self._hostnameCheck))
        self.statusBar = msg

        if self._hostnameCheck:
            for x in [4,3,2,1,0]: # max no. of running checks
                try:
                    index, thread, buffer = self._hostnameCheck[x]
                    if not thread.beginCheck:
                        thread.beginCheck = True
                    elif thread.finished:
                        print(index, self.ipHeaders.index("Hostname"), str(buffer))
                        self.ipList.SetItem(index, self.ipHeaders.index("Hostname"), str(buffer[-1]))
                        ipAdd = self.ipList.GetItemText(index)
                        for filterIndex in range(self.ipListFilter.GetItemCount()):
                            if self.ipListFilter.GetItemText(filterIndex) == ipAdd:
                                self.ipListFilter.SetItem(filterIndex, self.ipHeaders.index("Hostname"), str(buffer[-1]))
                        del self._hostnameCheck[x]
                except:
                    continue

        elif True in self._stopThread:
            self.addressResultsCount = 0
            while self.pingThread.is_alive():
                continue
            self.StopScan()
            self.btnScan.SetLabel("Scan")
            self.timerCheck.Stop()

    def OnTimerHostTimeout(self, event):
        for h in self._hostnameCheck:
            index, thread, buffer = h
            if thread.beginCheck:
                thread.timeout -= 1

    def SetupBitmaps(self):
        for label in ["start", "stop"]:
            image = wx.Image(resource_path("images/{0}.png".format(label)))
            image.Rescale(24,24)
            self._bitmaps[label] = wx.Bitmap(image)

    def StartTimerCheck(self):
        self.addressResultsCount = 0
        self.timerCheck.Start(100)

    def StopScan(self):
        self._stopThread.append(True)
        self.addressResultsCount = 0
        self.timerCheck.Stop()
        if self.pingThread:
            while self.pingThread.is_alive():
                continue
        self.CleanScan()
        self.statusBar = "Scan Finished: Addresses Checked = {0}".format(self.scanTotalCount)

    def UpdateScanHistory(self):
        for cbox, dictKey in [(self.startIp, "ipStartHistory"),
                              (self.endIp, "ipEndHistory"),
                              (self.stringIp, "customScanHistory")]:
            count = cbox.GetCount()
            items = [cbox.GetString(x) for x in range(count)]
            value = cbox.GetValue()
            if value in items:
                index = items.index(value)
                del items[index]
            items.insert(0, value)

            cbox.Clear()
            for item in items:
                cbox.Append(item)
            cbox.SetValue(value)

            try:
                items = items[:10]
            except:
                pass
            self.app.config[dictKey] = items

class Main(wx.App):

    def __init__(self, portable=False):
        wx.App.__init__(self)

        self._portable = portable
        self._config = self.appDefaults
        self.LoadConfig()
        SplashScreen(800)
        frame = MainFrame(portable=portable)

    @property
    def appDefaults(self):
        return {
            "pos": None,
            "size": None,
            "ipStartHistory": [],
            "ipEndHistory": [],
            "customScanHistory": [],
            "scanConfig": {"hostnameTimeout":"5", "Hostname":True, "Manufacturer":False, "MAC Address": True},
            "filter": {"showAliveOnly": True}
        }

    @property
    def config(self):
        return self._config

    @property
    def configPath(self):
        if not self._portable:
            sp = wx.StandardPaths.Get()
            path = sp.GetUserConfigDir()
            dirPath = os.path.join(path, "Zippy IP Scanner")
            path = os.path.join(dirPath, "config.json")
            if not os.path.exists(os.path.join(dirPath)):
                os.makedirs(dirPath)
        else:
            path = "config.json"
        return path

    def LoadConfig(self):
        # try to load settings
        try:
            with open(self.configPath, "r") as file:
                data = json.load(file)
                file.close()
                self.config.update(data)
        except Exception as e:
            print("Could not load settings file:", e)
            self.SaveConfig()

    def SaveConfig(self):
        with open(self.configPath, "w") as file:
            json.dump(self.config, file, sort_keys=True, indent=2)
        print(self.config)

        
def main():
    app = Main(portable=False)
    app.MainLoop()
        
if __name__ == "__main__":
    main()