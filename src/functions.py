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

import json
import logging
import os
import platform
import re
import urllib.request
import socket
import subprocess
import time
import threading

def GetHostByAddress(address, hostname):
    try:
        hostname.append(socket.gethostbyaddr(address)[0])
    except socket.herror:
        hostname.append("n/a")
    
class LookupHostname(threading.Thread):
    
    def __init__(self, address, buffer, timeout):
        threading.Thread.__init__(self)
        
        self._finished = None
        self._beginCheck = None
        self._timeout = timeout
        # lookup hostnames of IP address
        self.address = address
        self.hostname = buffer
        self.daemon = True
        # self.start()
        # n = 0
        # while n < timeout:
            # if hostname:
                # return hostname[0]
            # n += 0.1
            # time.sleep(0.1)
        
        # return ""
        
    @property
    def beginCheck(self):
        return self._beginCheck
        
    @beginCheck.setter
    def beginCheck(self, value):
        if value is True:
            self._beginCheck = True
            self.start()
            
    @property
    def timeout(self):
        return self._timeout
        
    @timeout.setter
    def timeout(self, value):
        timeout = value
        if value <= 0:
            self.finished = True    
            
    @property
    def finished(self):
        if self.hostname == []:
            self.hostname.append("t/o")
        return self._finished
        
    @finished.setter
    def finished(self, value):
        self._finished = value   
        
    def run(self):
        try:
            self.hostname.append(socket.gethostbyaddr(self.address)[0])
        except socket.herror:
            self.hostname.append("n/a")
        
        self._finished = True
    
def LookupMacAddress(address):

    """ Finds the MAC Addresses using ARP

    NOTE: This finds mac addresses only within the subnet.
    It doesn't fetch mac addresses for routed network ips.
    """

    if platform.system() == 'Windows':
        arp_cmd = ['arp', '-a']
    else:
        arp_cmd = ['arp', '-n']
        
    info = None
    # Configure subprocess to hide the console window
    if os.name == 'nt':
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE
            
    pid = subprocess.Popen(arp_cmd + [address], 
                           stdin=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE, startupinfo=info)
    out = pid.communicate()[0]
    
    MAC_RE = re.compile(r'(([a-f\d]{1,2}[:-]){5}[a-f\d]{1,2})')
    mac_found = MAC_RE.search(out.decode('utf-8'))
    
    if mac_found:
        mac = mac_found.group(0).replace('-', ':')
    else:
        mac = "n/a"
        
    logging.info("address: %s, mac: %s" % (address, mac))    
    
    return mac
    
def LookupManufacturers(mac):
    """ request from macvendors.co """
    macUrl = 'http://macvendors.co/api/{0}'.format(mac)    
    req = urllib.request.Request(macUrl, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        result = urllib.request.urlopen(req).read()
        result = result.decode("utf-8")
    except Exception as e:
        print(e)
        return ""
    
    print(result)
    # logging.info("request URL: %s" % r.text)
    result = json.loads(result)["result"]
    
    print(result)
    try:
        mfn = result["company"]
        return mfn
    except:
        return ""
        
class PingAddress(threading.Thread):
    
    def __init__(self, addresses, addressResults, stopThread, scanParams):
        
        threading.Thread.__init__(self)
        
        self.scanParams = scanParams
        self._stopThread = stopThread
        self._addressResults = addressResults
        
        self._addresses = addresses
        self.start()
        
    def run(self):    
        
        info = None
        # Configure subprocess to hide the console window
        if os.name == 'nt':
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE
        
        for index, address in enumerate(self._addresses):
        
            if self._stopThread == [True]:
                return
            
            # For each IP address in the subnet, 
            # run the ping command with subprocess.popen interface
            address = str(address)
            if platform.system() == 'Windows':
                cmd = ['ping', '-n', '1', '-w', '500', address]
            elif platform.system() == 'Linux':
                cmd = ['ping', '-c', '1', '-w', '1', address]
    
            output = subprocess.Popen(cmd, 
                                      stdin=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      startupinfo=info).communicate()[0]
            output = output.decode('utf-8')
            
            # parse TTL and response time (ms)
            ttl = ""
            ms = ""
            mac = ""
            mfn = ""
            hostname = ""
            status = "Offline"
            if platform.system() == 'Windows':
                if "Destination host unreachable" in output:
                    pass                 
                elif "Request timed out" in output:
                    if self.scanParams["MAC Address"] is True:
                        mac = LookupMacAddress(address)
                        
                    if self.scanParams["Manufacturer"] is True:
                        mfn = LookupManufacturers(mac)
                elif "General failure" in output: 
                    pass
                else:
                    status = "Online"
                    ttlStart = output.index("TTL=")
                    ttlEnd = output.index("\r\n\r\nPing statistics")
                    ttl = output[ttlStart+len("TTL="):ttlEnd]
                    msStart = output.index("Average = ")
                    ms = output[msStart+len(("Average = ")):]
                    
            if platform.system() == 'Linux':   
                if "ttl=" in output:
                    status = "Online"
                    ttlStart = output.index("ttl=")
                    ttlEnd = output.index(" time=")
                    ttl = output[ttlStart+len("ttl="):ttlEnd]
                    msStart = output.index("time=")
                    msEnd = output.index(" ms") 
                    ms = output[msStart+len("time="):msEnd]
           
            if status == "Online":
                if self.scanParams["MAC Address"] is True:
                    mac = LookupMacAddress(address)
                
                if self.scanParams["Manufacturer"] is True:
                    mfn = LookupManufacturers(mac)
                
                # if self.scanParams["Hostname"] is True:
                    # hostname = LookupHostname(address, self.scanParams["hostnameTimeout"])
                    
            params = {}
            # params["index"] = index
            params["IP Address"] = address
            params["Ping"] = ms
            params["TTL"] = ttl
            params["Manufacturer"] = mfn
            params["MAC Address"] = mac
            # params["status"] = status
            # params["Hostname"] = hostname
            self._addressResults.append(params)
            
        self._stopThread.append(True)
        
#end class PingAddress