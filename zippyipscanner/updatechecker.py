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

from version import __version__
import urllib.request
import wx
from wx.lib.agw import hyperlink
from threading import Thread
from portable import resource_path

baseUrl = "https://sourceforge.net/projects/zippy-ip-scanner/files/"

class CheckForUpdates(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="Check For Updates")
        
        self.version = __version__
        self.latestVersion = []
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        
        g = "https://sourceforge.net/projects/zippy-ip-scanner/files/"
        link = hyperlink.HyperLinkCtrl(panel, label="Check Releases Manually", URL=g)
        sboxSizer.Add(link, 0, wx.ALL|wx.EXPAND, 5)
        v = "v" + self.version
        versionLabel = wx.StaticText(panel, label="Current Version: %s" % v)
        sboxSizer.Add(versionLabel, 0, wx.ALL|wx.EXPAND, 5)
        
        hSizerLink = wx.BoxSizer(wx.HORIZONTAL)
        self.latestVersionLabel = wx.StaticText(panel, label="Latest Version:")
        self.link = hyperlink.HyperLinkCtrl(panel, label="", URL=g)
        hSizerLink.Add(self.latestVersionLabel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        hSizerLink.Add(self.link, 0, wx.ALL|wx.EXPAND, 5)
        sboxSizer.Add(hSizerLink, 1, wx.ALL|wx.EXPAND, 5)
        
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        self.btnCheck = wx.Button(panel, label="Check")
        self.btnCheck.SetFocus()
        # self.btnUpdate = wx.Button(panel, label="Update")
        # self.btnUpdate.Disable()
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.btnCheck.Bind(wx.EVT_BUTTON, self.OnCheck)
        # self.btnUpdate.Bind(wx.EVT_BUTTON, self.OnUpdate)
        
        hSizer.Add(self.btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hSizer.AddStretchSpacer()
        hSizer.Add(self.btnCheck, 0, wx.ALL|wx.EXPAND, 5)
        # hSizer.Add(self.btnUpdate, 0, wx.ALL|wx.EXPAND, 5)
        
        #add to main sizer
        sizer.Add(sboxSizer, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hSizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)
        w, h = sizer.Fit(self)
        self.SetMinSize((w*1.5, h))
        self.SetSize((w*1.5, h))
        self.Show()
        self.Center()        
        
        try:
            self.SetIcon(wx.Icon(resource_path("zippyipscanner.ico")))
        except:
            pass
        self.Bind(wx.EVT_CHAR_HOOK, self.OnChar)
        
    def OnCancel(self, event):
        self.Close()
    
    def OnChar(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Close()   
            
    def OnCheck(self, event):
        self.latestVersion = []
        self.latestVersionLabel.SetLabel("Latest Version:")
        self.link.SetLabel("")
        self.link.SetURL("")
        self.btnCheck.SetLabel("Checking...")
        
        u = "https://raw.githubusercontent.com/swprojects/Zippy-Ip-Scanner/master/RELEASES"
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            result = urllib.request.urlopen(req).read().decode("utf-8")
            result = result.split("\n")
            ver, url = result[0].split(",")
            print(ver, url)
            self.link.SetLabel(ver)
            self.link.SetURL(url)
        except Exception as e:
            pass   
            
        self.btnCheck.SetLabel("Check")