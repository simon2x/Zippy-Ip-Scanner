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

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

class BaseList(wx.ListCtrl, ListCtrlAutoWidthMixin):
    
    def __init__(self, parent):
        
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
        ListCtrlAutoWidthMixin.__init__(self)
        
        # self.setResizeColumn(1)
        # self.setResizeColumn(2)
        
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