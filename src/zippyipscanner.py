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

import csv
import functions
import json
import logging
import ipaddress
import multiprocessing
import platform
import queue
import os
import sys
import subprocess
import threading
import time
import wx

# wx modules
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub

queue = queue.Queue()

# python 2 to 3 compatibility
try:
    range
except:
    range = xrange    

#----- logging -----#

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create file handler which logs even debug messages
# fh = logging.FileHandler('wxpietool.log')
# fh.setLevel(logging.DEBUG)
# # create console handler with a higher log level
# ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
# # create formatter and add it to the handlers
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# # formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# ch.setFormatter(formatter)
# # add the handlers to the logger
# logger.addHandler(fh)
# logger.addHandler(ch)

PROCESS_COUNT = multiprocessing.cpu_count() - 1
PLATFORM = platform.system().lower()

# logging.

class ConfirmDialog(wx.Dialog):

    def __init__(self, parent, message):
        wx.Dialog.__init__(self, parent)
        
        self.SetTitle("Delete items")
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(60)
        label_message = wx.StaticText(self, label=message)
        sizer.Add(label_message, 1, wx.ALL|wx.ALIGN_CENTRE, 2)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Yes","No"]:
            btn = wx.Button(self, label=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            hsizer.Add(btn, 0, wx.ALL|wx.ALIGN_RIGHT, 2)
        sizer.Add(hsizer, 0, wx.ALL|wx.ALIGN_RIGHT, 2)
        
        self.SetSizer(sizer) 
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        
        if label == "Yes":
            self.EndModal(wx.ID_YES)
        else:
            self.EndModal(wx.ID_NO)
            
# inherited list class
class BaseList(wx.ListCtrl, ListCtrlAutoWidthMixin):
    
    def __init__(self, parent):
        
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
        ListCtrlAutoWidthMixin.__init__(self)
        
        # self.setResizeColumn(1)
        
    def DeselectAll(self):
        selected = self.GetFirstSelected()
        while selected != -1:
            self.Select(selected, on=0)
            selected = self.GetNextSelected(selected)
    
    def ScrollToBottom(self):
        self.EnsureVisible(self.GetItemCount() - 1)
    
    def GetSelected(self):
        selections = []
        selected = self.GetFirstSelected()        
        while selected != -1:
            selections.append(selected)
            selected = self.GetNextSelected(selected)
        
        return selections 
        
#end ScrollToBottom def
                
    def DeleteSelected(self):
        selected = self.GetFirstSelected()
        if selected == -1:
            return
        selected_items = []        
        while selected != -1:
            selected_items.append(selected)
            selected = self.GetNextSelected(selected)
            
        for item in reversed(selected_items):
            logging.info("Deleted image from list: %s" % str(item))
            self.DeleteItem(item)

class Main(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self,
                          None,
                          wx.ID_ANY,
                          title='Zippy IP Scanner 2017')
                
        self._menus = {}
        self._btns = {}
        self._data = {}
        self._sortby = None
        self._hostname_cache = {}
        #
        self._makes = []
        self._models = []
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbox = wx.StaticBox(panel, label="Scan Configuration")
        
        sboxsizer_toolbar = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        self.start_ip = wx.TextCtrl(panel, value="192.168.0.0")
        self.end_ip = wx.TextCtrl(panel, value="192.168.0.25")
        sboxsizer_toolbar.Add(self.start_ip, 0, wx.ALL|wx.EXPAND, 2)
        sboxsizer_toolbar.Add(self.end_ip, 0, wx.ALL|wx.EXPAND, 2)
        
        btn = wx.Button(panel, label="Scan")                    
        btn.Bind(wx.EVT_BUTTON, self.OnScan)
        sboxsizer_toolbar.Add(btn, 0, wx.ALL|wx.EXPAND, 2)        
        
        sbox = wx.StaticBox(panel, label="Results")
        sboxsizer_results = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        
        hsizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        btn_reset = wx.Button(panel, label="Reset Filters")
        btn_reset.Bind(wx.EVT_BUTTON, self.OnButton)
        self.cbox_makes = wx.ComboBox(panel, name="makes", choices=["All Makes"], 
                                        size=(200,-1), style=wx.CB_READONLY)
        self.cbox_models = wx.ComboBox(panel, name="models", choices=["All Models"],
                                                size=(200,-1), style=wx.CB_READONLY)
        self.cbox_makes.Bind(wx.EVT_COMBOBOX, self.OnFilter)
        self.cbox_models.Bind(wx.EVT_COMBOBOX, self.OnFilter)
        self.cbox_makes.SetSelection(0)
        self.cbox_models.SetSelection(0)
        hsizer_controls.Add(self.cbox_makes, 0, wx.ALL|wx.EXPAND, 2)
        hsizer_controls.Add(self.cbox_models, 0, wx.ALL|wx.EXPAND, 2)
        
        label_latlon = wx.StaticText(panel, label="Alive/Dead:")
        hsizer_controls.Add(label_latlon, 0, wx.ALL|wx.ALIGN_CENTRE, 2)
        self.chk_latlon = {}
        for label in ["N","S","W","E"]:        
            self.chk_latlon[label] = wx.CheckBox(panel, label=label)
            self.chk_latlon[label].SetValue(True)
            self.chk_latlon[label].Bind(wx.EVT_CHECKBOX, self.OnFilter)
            hsizer_controls.Add(self.chk_latlon[label], 0, wx.ALL|wx.EXPAND, 2)
                        
        hsizer_controls.AddStretchSpacer()
        hsizer_controls.Add(btn_reset, 0, wx.ALL|wx.EXPAND, 2)
        
        
        self.ip_list = BaseList(panel)
        self.ip_headers = ["IP Address","Hostname","Ping","TTL","Manufacturer","MAC Address"]
        for col, header in enumerate(self.ip_headers):
            self.ip_list.InsertColumn(col, header)
        self.ip_list.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumn)
                
        sboxsizer_results.Add(hsizer_controls, 0, wx.ALL|wx.EXPAND, 5)
        sboxsizer_results.Add(self.ip_list, 3, wx.ALL|wx.EXPAND, 5)
        
        sizer.Add(sboxsizer_toolbar, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sboxsizer_results, 1, wx.ALL|wx.EXPAND, 5)
        
        panel.SetSizer(sizer)
        self.SetSize((800, 600))
        self.Show()
        
        panel.SetSizer(sizer)
        self.Bind(wx.EVT_CLOSE,  self.OnClose)
        
        pub.subscribe(self.InsertAddress, "main.InsertAddress")
        pub.subscribe(self.GetHostNames, "main.GetHostNames")
        
        # try to load settings
        try:
            with open("settings.json", "r") as loadfile:
                data = json.load(loadfile)
                loadfile.close()
                
                makes = []
                models = []
                for key in sorted(data.keys()):
                    value = data[key]
                    self._data[int(key)] = value
                    self.ip_list.Append(value)
                    
                    #extra: add to filter
                    make = value[3]
                    model = value[4] 
                    if make not in makes:
                        makes.append(make)
                    if model not in models:
                        models.append(model)
                 
                 
                self._makes = sorted(makes)  
                self._models = sorted(models)   
                
                for make in self._makes:
                    self.cbox_makes.Append(make)
                for model in self._models:
                    self.cbox_models.Append(model)
                    
            # self.cbox_models.Append(self._models)                
        except:
            print("Could not load settings file")
        
        self._hosts = {} 
        # self.timer_lookup = wx.Timer(self)
        # self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer_lookup)
     
    def GetHostNames(self, msg):
        hostnames = functions.LookupHostnames(self._addresses)
        logging.info(hostnames)
        for index, hostname in hostnames:
            self.ip_list.SetItem(index, 1, hostname)
            
    def OnComboBox(self, event):
        e = event.GetEventObject()
        name = e.GetName()
        if name == "makes":
            pass
        elif name == "models":
            pass
     
    def OnFilter(self, event):
        filters = []
        for label, chk in self.chk_latlon.items():
            if chk.GetValue():
                filters.append(label)
                filters.append(label.lower())
        
        self.ip_list.DeleteAllItems()
        for x in range(0, len(self._data.keys())):
            value = self._data[x]
            print(value[6], value[8], filters)
            
            make = self.cbox_makes.GetSelection()
            model = self.cbox_models.GetSelection()
            if str(value[6]) in filters and str(value[8]) in filters:
                if (make, model) == (0, 0):
                    self.ip_list.Append(value)
                    continue
                make = self.cbox_makes.GetStringSelection()
                model = self.cbox_models.GetStringSelection()
                
                if value[3] == make:
                    self.ip_list.Append(value)
                elif value[4] == model:
                    self.ip_list.Append(value)
    
    def InsertAddress(self, msg):
        msg = msg.data
        index = msg["index"]
        address = msg["address"]
        ttl = msg["ttl"]
        ms = msg["ms"]
        mac = msg["mac"]
        mfn = msg["mfn"]
        status = msg["status"]
        hostname = msg["hostname"]
        
        item = [address, hostname, ms, ttl, mfn, mac]
        logging.info("Inserting item %s" % str(item))
                        
        self._data[index] = {"address":address,
                             "status":status, 
                             "hostname":hostname,
                             "ms":ms,
                             "status":status,
                             "ttl":ttl,
                             "mac":mac,
                             "mfn":mfn,
                             "manufacturer":""}
        self.ip_list.Append(item)
        
    def OnScan(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        
        if label == "Stop":
            pub.sendMessage("PingAddress.stop", "")
            e.SetLabel("Scan")
            return
        
        self.ip_list.DeleteAllItems()
        e.SetLabel("Stop")
        
        start_ip = self.start_ip.GetValue()
        end_ip = self.end_ip.GetValue()
            
        if not start_ip and not end_ip:
            logging.info("No valid IP range defined")
            return
        if not end_ip:
            pass
            
        start = list(map(int, start_ip.split(".")))
        end = list(map(int, end_ip.split(".")))

        # is end IP before start IP?  
        for i in range(4):
            if start[i] > end[i]:
                start, end = end, start
                break

        logging.info("Populate IP range list from %s - %s" % (start, end))
        
        temp = start
        addresses = []
        addresses.append(start_ip)
        
        # def generate_ip_list(ip):
        #increment address until it reaches the end ip
        while temp != end:
            start[3] += 1
            
            if temp[i] == 256:
                temp[i] = 0
                temp[i-1] += 1
            
            ip = ".".join(map(str, temp))
            addresses.append(ip)
                    
        functions.PingAddress(addresses)
        
        self._addresses = addresses
            
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        
        if label == "Start Scan":
            self.OnScan()
            
        if label == "Reset Filters":
            self.cbox_makes.SetSelection(0)
            self.cbox_models.SetSelection(0)
            for chk in self.chk_latlon.values():
                chk.SetValue(True)
            
            # re add all items
            self.ip_list.DeleteAllItems()
            for x in range(0, len(self._data.keys())):
                value = self._data[x]
                self.ip_list.Append(value)
                
        elif label == "Clear List":
            count = str(len(self._data.keys()))
            message = "Delete all %s items?" % count
            dlg = ConfirmDialog(self, message)
            ret = dlg.ShowModal()
            
            if ret == wx.ID_YES:
                self.ip_list.DeleteAllItems()                
                self._data = {}
    
    def OnColumn(self, event):
        """ here we sort items by the column clicked """
        e = event.GetEventObject()
        index = event.GetColumn()
        
        items = []
        for row in range(self.ip_list.GetItemCount()):
            item = []
            for col in range(self.ip_list.GetColumnCount()):
                text = self.ip_list.GetItem(row, col).GetText()
                item.append(text)
            items.append(item)    
            
        self.ip_list.DeleteAllItems()
                
        if self._sortby == index:
            # already sorted, this time reverse order
            sorted_x = sorted(items, key=lambda x: x[index].lower())
            sorted_x = reversed(sorted_x)
        else:
            sorted_x = sorted(items, key=lambda x: x[index].lower())            
            self._sortby = index
            
        # print(sorted_x)
        self.ip_list.DeleteAllItems()
        for x in sorted_x:
            self.ip_list.Append(x)
                    
        
#end OnButton def

    def OnClose(self, event):
        """ save settings before quitting """
        with open("settings.json", "w") as savefile:
            json.dump(self._data, savefile, sort_keys=True, indent=1)
        
        event.Skip()
        
#end OnClose def
 
#end Main class

if __name__ == "__main__":
    app = wx.App()
    frame = Main()
    app.MainLoop()