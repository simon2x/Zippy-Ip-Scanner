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
import platform
import re
import urllib.request
import socket
import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class LookupHostname(QtCore.QThread):

    signal = pyqtSignal(dict)

    def __init__(self, parent, address, timeout):
        super(LookupHostname, self).__init__()

        self.parent = parent
        self.timeout = timeout * 1000
        self.address = address

        self.signal.connect(self.parent.receiveHostnameResult)

    def run(self):
        hostname = "n/a"
        try:
            hostname = socket.gethostbyaddr(self.address)[0]
        except socket.herror:
            pass
        self.signal.emit({"address": self.address, "hostname": hostname})


def LookupMacAddress(address):
    """
    Finds the MAC Addresses using ARP

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

    def __init__(self, parent, addresses, scanParams):
        super(PingAddress, self).__init__()

        self.parent = parent
        self.signal.connect(self.parent.receiveScanResult)
        self.debugSignal.connect(self.parent.receiveDebugSignal)
        self.scanParams = scanParams
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

            # For each IP address in the subnet, run the ping command
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
                    self.debugSignal.emit("PingAddress->Output: %s" % output)
                    if "TTL=" in output:
                        status = "Online"
                        ttlStart = output.index("TTL=")
                        ttlEnd = output.index("\r\n\r\nPing statistics")
                        ttl = output[ttlStart + len("TTL="):ttlEnd]
                        msStart = output.index("Average = ")
                        ms = output[msStart + len(("Average = ")):].strip("\r\n")

            if platform.system() == 'Linux':
                if "ttl=" in output:
                    status = "Online"
                    ttlStart = output.index("ttl=")
                    ttlEnd = output.index(" time=")
                    ttl = output[ttlStart + len("ttl="):ttlEnd]
                    msStart = output.index("time=")
                    msEnd = output.index(" ms")
                    ms = output[msStart + len("time="):msEnd]

            self.debugSignal.emit("PingAddress->Status: %s" % status)
            if status == "Online":
                if self.scanParams["MAC Address"] == 2:
                    self.debugSignal.emit("PingAddress->MAC Address: %s" % address)
                    mac = LookupMacAddress(address)

                if self.scanParams["Manufacturer"] == 2:
                    self.debugSignal.emit("PingAddress->LookupManufacturers: %s" % mac)
                    mfn = LookupManufacturers(mac)

                # if self.scanParams["Hostname"] == 2:
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

            self.signal.emit(params)
