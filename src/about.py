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
from license import __license__
import os
import wx
from wx.lib.agw import hyperlink

class AboutDialog(wx.Frame):

    def __init__(self):                    
        wx.Frame.__init__(self, None, -1, title="About Zippy Ip Scanner")
                        
        panel = wx.Panel(self)    
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbox1 = wx.StaticBox(panel, label="")
        sboxSizerInfo = wx.StaticBoxSizer(sbox1, wx.HORIZONTAL)
        grid = wx.GridSizer(cols=2)
        grid.Add(wx.StaticText(panel, label="Author:"), 0, wx.ALL, 5)
        link = hyperlink.HyperLinkCtrl(panel, label="www.sanawu.com", URL="www.sanawu.com")
        grid.Add(link, 0, wx.ALL|wx.EXPAND, 5)
        grid.Add(wx.StaticText(panel, label="Github:"), 0, wx.ALL, 5)
        g = "https://github.com/swprojects/Zippy-Ip-Scanner"
        link = hyperlink.HyperLinkCtrl(panel, label=g, URL=g)
        grid.Add(link, 1, wx.ALL|wx.EXPAND, 5)
        grid.Add(wx.StaticText(panel, label="Version:"), 0, wx.ALL, 5)
        v = __version__
        grid.Add(wx.StaticText(panel, label=v), 0, wx.ALL, 5)
        
        sboxSizerInfo.Add(grid, 1, wx.ALL|wx.EXPAND, 5)
        
        sbox = wx.StaticBox(panel, label="Mac Vendor Lookup")        
        sboxSizerMacLookup = wx.StaticBoxSizer(sbox, wx.VERTICAL)  
        lookupText = wx.StaticText(panel)
        text = ("Zippy Ip Scanner retrieves the MAC vendor name via MacVendors.co API and \n"
               +"therefore MAC vendor name retrieval is subject to MacVendors.co privacy policy.")
        lookupText.SetLabel(text)
        sboxSizerMacLookup.Add(lookupText, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        link = hyperlink.HyperLinkCtrl(panel, label="MacVendors.co Privacy Policy", URL="http://macvendors.co/kb/privacy-policy")
        sboxSizerMacLookup.Add(link, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        
        sbox2 = wx.StaticBox(panel, label="License")
        sboxSizerLicense = wx.StaticBoxSizer(sbox2, wx.VERTICAL)  
              
        style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_CENTRE
        licenseText = wx.TextCtrl(panel, style=style)
        licenseText.SetValue(__license__)
        sboxSizerLicense.Add(licenseText, 1, wx.ALL|wx.EXPAND, 5)
        
        sizer.Add(sboxSizerInfo, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sboxSizerMacLookup, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sboxSizerLicense, 1, wx.ALL|wx.EXPAND, 5)
        
        panel.SetSizerAndFit(sizer)
        
        self.Centre()
        self.Fit()
        w,h = self.GetSize()
        self.SetMinSize((w, h*1.5))        
        self.SetSize((w, h*1.5))
        self.Show()
        
        try:
            self.SetIcon(wx.Icon("icon.ico"))
        except:
            pass
        self.Bind(wx.EVT_CHAR_HOOK, self.OnChar)
        
    @property 
    def app(self):
        return wx.GetApp()
        
    def OnChar(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Close()   
            
        