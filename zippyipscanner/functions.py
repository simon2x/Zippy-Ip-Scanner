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

import time
import mathfunctions as mf
import logging
import json
import os
import re
import urllib.request
import socket
import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot


def on_windows():
    return os.name == "nt"


def startup_info():
    """Configure subprocess to hide the console window"""
    if on_windows():
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE
        return info
    return None


def valid_ip4(address):
    """
    Is a valid 4-byte address? If not, try to return the
    next best valid address

    Some leniency allowed on the first byte (8 LSB's). Every
    other byte must be 0 - 255.
    """
    logging.debug("functions->valid_ip4 (address=%s)" % address)
    if not isinstance(address, list):
        return False
    if len(address) == 3:
        address.append(0)
    elif len(address) != 4:
        return False
    result = [0, 0, 0, 0]
    try:
        for n, x in enumerate(address):
            if x > 255 and n == 3:
                result[n] = 255
            elif x > 255 or x < 0:
                return False
            else:
                result[n] = x
    except ValueError:
        return False
    return result


class ParseIpRange(QtCore.QThread):

    signalScanIp = pyqtSignal(dict)

    def __init__(self, parent, spec):
        super(ParseIpRange, self).__init__()

        self.parent = parent
        self.spec = spec
        self.signalScanIp.connect(self.parent.slotScanIp)
        self.start()

    def run(self):
        self.parseIpRange(self.spec)

    def parseIpRange(self, spec):
        """Is spec string a range a IP addresses?"""
        logging.debug("functions->parseIpRange")
        addresses = []
        try:
            ipStart, ipEnd = spec.split("-")[:2]

            # Check start IP
            ipStart = [int(x) for x in ipStart.split(".")]
            start = valid_ip4(ipStart)
            if start is False:
                return

            # Check end IP
            ipEnd = [int(x) for x in ipEnd.split(".")]
            if len(ipEnd) == 1:
                ipEnd = start[:3] + ipEnd
            end = valid_ip4(ipEnd)
            if end is False:
                return

            if start == end:
                ip = ".".join([str(x) for x in start])
                self.signalScanIp.emit({"IP Address": ip})
                return addresses

            startDec = mf.byte_list_to_decimal(start)
            endDec = mf.byte_list_to_decimal(end) + 1
            if endDec < startDec:
                startDec, endDec = endDec, startDec
            logging.debug("functions->parseIpRange addresses=%s" % str((startDec, endDec)))

            for _ in range(startDec, endDec):
                temp = mf.decimal_to_byte_list(startDec, retbytes=4)
                ip = ".".join([str(x) for x in temp])
                self.signalScanIp.emit({"IP Address": ip})
                startDec += 1
                time.sleep(0.05)

            logging.debug("functions->parseIpRange addresses=%s" % addresses)

        except Exception as e:
            logging.debug("functions->parseIpRange: %s" % e)
            return


class LookupHostname(QtCore.QThread):

    signalHostnameResult = pyqtSignal(dict)

    def __init__(self, parent, address, timeout):
        super(LookupHostname, self).__init__()

        self.parent = parent
        self.timeout = timeout * 1000
        self.address = address

        if self.parent:
            self.signalHostnameResult.connect(self.parent.slotHostnameResult)

    def run(self):
        hostname = "n/a"
        try:
            hostname = socket.gethostbyaddr(self.address)[0]
        except socket.herror:
            pass
        result = {"address": self.address, "hostname": hostname}
        if not self.parent:
            return result
        self.signalHostnameResult.emit(result)


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

    info = startup_info()
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

    signalScanResult = pyqtSignal(dict)
    signalDebug = pyqtSignal(str)

    def __init__(self, parent, scanParams={}):
        super(PingAddress, self).__init__()

        self.parent = parent
        self.addresses = []
        self.scanParams = scanParams
        if self.parent:
            self.signalScanResult.connect(self.parent.slotScanResult)
            self.signalDebug.connect(self.parent.slotDebug)
            self.start()

    @pyqtSlot(dict)
    def slotAddPing(self, item):
        index = item["index"]
        address = item["address"]
        self.addresses.append((index, address))

    @pyqtSlot(dict)
    def slotScanParams(self, params):
        self.scanParams = params

    @pyqtSlot()
    def slotStopScanning(self):
        self.addresses = []

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
        self.signalDebug.emit(output)
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

    def emitResult(self, result):
        self.signalScanResult.emit(result)

    def runCommand(self, cmd):
        output = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE, startupinfo=startup_info()).communicate()[0]
        output = output.decode('utf-8')
        return output

    def run(self):
        while True:
            if not self.addresses:
                time.sleep(0.5)
                continue
            index, address = self.addresses[0]
            # For each IP address in the subnet, run the ping command
            result = {
                "IP Address": address,
                "TTL": "",
                "Ping": "",
                "Manufacturer": "",
                "MAC Address": ""
            }
            address = str(address)
            cmd = self.pingCommand(address)
            out = self.runCommand(cmd)
            result.update(self.outputResult(out))
            if result["TTL"]:
                if self.checkMac:
                    result["MAC Address"] = LookupMacAddress(address)
                if self.checkManufacturer:
                    result["Manufacturer"] = LookupManufacturers(result["MAC Address"])
            self.emitResult(result)
            try:
                del self.addresses[0]
            except IndexError:
                pass
