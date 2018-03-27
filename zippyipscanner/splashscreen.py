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

import wx.adv
from portable import resource_path

class SplashScreen(wx.adv.SplashScreen):
        
    def __init__(self, timeout=800):  
        splash_style = wx.adv.SPLASH_CENTRE_ON_SCREEN|wx.adv.SPLASH_TIMEOUT
        try:
            bmp = wx.Bitmap(resource_path("splash.png"))
        except:
            return
        
        wx.adv.SplashScreen.__init__(self, bmp, splash_style, timeout, None)   