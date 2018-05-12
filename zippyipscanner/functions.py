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

import logging
import json
import os
import re
import urllib.request
import socket
import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


def on_windows():
    return os.name == "nt"


def startupInfo():
    """Configure subprocess to hide the console window"""
    if on_windows():
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE
        return info
    return None


class LookupHostname(QtCore.QThread):

    signal = pyqtSignal(dict)

    def __init__(self, parent, address, timeout):
        super(LookupHostname, self).__init__()

        self.parent = parent
        self.timeout = timeout * 1000
        self.address = address

        if self.parent:
            self.signal.connect(self.parent.receiveHostnameResult)

    def run(self):
        hostname = "n/a"
        try:
            hostname = socket.gethostbyaddr(self.address)[0]
        except socket.herror:
            pass
        result = {"address": self.address, "hostname": hostname}
        if not self.parent:
            return result
        self.signal.emit(result)


def LookupMacAddress(address):
    """
    Finds the MAC Addresses using ARP

    NOTE: This finds mac addresses only within the subnet.
    It doesn't fetch mac addresses for routed network ips.
    """
    if on_windows():
        arp_cmd = ['arp', '-a']
    else:
        arp_cmd = ['arp', '-n']

    info = startupInfo()
    pid = subprocess.Popen(arp_cmd + [address],
                           stdin=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE, startupinfo=info)
    out = pid.communicate()[0]

    macRe = re.compile(r'(([a-f\d]{1,2}[:-]){5}[a-f\d]{1,2})')
    macFound = macRe.search(out.decode('utf-8'))
    if macFound:
        mac = macFound.group(0).replace('-', ':')
    else:
        mac = "n/a"

    logging.debug("address: %s, mac: %s" % (address, mac))
    return mac


def LookupManufacturers(mac):
    """Request to macvendors.co for manufacturer name"""
    macUrl = 'http://macvendors.co/api/{0}'.format(mac)
    req = urllib.request.Request(macUrl, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        result = urllib.request.urlopen(req).read()
        result = result.decode("utf-8")
    except Exception as e:
        logging.debug("LookupManufacturers Exception: {0}".format(e))
        return ""

    logging.debug("LookupManufacturers:Result: %s" % result)
    # logging.debug("request URL: %s" % r.text)
    result = json.loads(result)["result"]

    try:
        mfn = result["company"]
        return mfn
    except Exception as e:
        return ""


class PingAddress(QtCore.QThread):

    signal = pyqtSignal(dict)
    debugSignal = pyqtSignal(str)

    def __init__(self, parent, addresses, scanParams, start=True):
        super(PingAddress, self).__init__()

        self.parent = parent
        self.addresses = addresses
        self.scanParams = scanParams
        if self.parent:
            self.signal.connect(self.parent.receiveScanResult)
            self.debugSignal.connect(self.parent.receiveDebugSignal)
        if start is True:
            self.start()

    @property
    def checkMac(self):
        return self.scanParams["MAC Address"] == 2

    @property
    def checkManufacturer(self):
        return self.scanParams["Manufacturer"] == 2

    def extractMS(self, output):
        try:
            msStart = output.index("Average = ")
            ms = output[msStart + len("Average = "):].strip("\r\n")
        except ValueError:
            msStart = output.index("time=")
            msEnd = output.index(" ms")
            ms = output[msStart + len("time="):msEnd]
        return ms

    def extractTTL(self, output):
        try:
            ttlStart = output.index("TTL=")
            ttlEnd = output.index("\r\n\r\nPing statistics")
            ttl = output[ttlStart + len("TTL="):ttlEnd]
        except ValueError:
            ttlStart = output.index("ttl=")
            ttlEnd = output.index(" time=")
            ttl = output[ttlStart + len("ttl="):ttlEnd]
        return ttl

    def gotResponse(self, output):
        if on_windows():
            return "Reply from" in output
        else:
            return "ttl=" in output

    def outputResult(self, output):
        """Return result of output"""
        self.debugSignal.emit(output)
        result = {}
        if self.gotResponse(output):
            result["TTL"] = self.extractTTL(output)
            result["Ping"] = self.extractMS(output)
        return result

    def pingCommand(self, address):
        if on_windows():
            cmd = ['ping', '-n', '1', '-w', '500', address]
        else:
            cmd = ['ping', '-c', '1', '-w', '1', address]
        return cmd

    def returnResult(self, result):
        self.signal.emit(result)

    def runCommand(self, cmd):
        output = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE, startupinfo=startupInfo()).communicate()[0]
        output = output.decode('utf-8')
        return output

    def run(self):
        for index, address in enumerate(self.addresses):
            # For each IP address in the subnet, run the ping command
            result = {"IP Address": address, "TTL": "", "Ping": "", "Manufacturer": "", "MAC Address": ""}
            address = str(address)
            cmd = self.pingCommand(address)
            out = self.runCommand(cmd)
            result.update(self.outputResult(out))
            if result["TTL"]:
                if self.checkMac:
                    result["MAC Address"] = LookupMacAddress(address)
                if self.checkManufacturer:
                    result["Manufacturer"] = LookupManufacturers(result["MAC Address"])
            self.returnResult(result)
        self.exit()
