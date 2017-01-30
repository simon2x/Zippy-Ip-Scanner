import json
import multiprocessing
from multiprocessing.pool import ThreadPool
from multiprocessing.dummy import Pool as ThreadPool 
import logging
import platform
import re
import requests
import socket
import subprocess
import time
import threading
import wx
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub

PROCESS_COUNT = multiprocessing.cpu_count() - 1
# PROCESS_COUNT = multiprocessing.cpu_count() - 1
PLATFORM = platform.system().lower()

def GetHostByAddress(address):
    # return 
    try:
        hostname = socket.gethostbyaddr(address)[0]
    except socket.herror:
        hostname = "n/a"
    
    logging.info("address: %s, host: %s" % (address,hostname))

    return hostname
    
def LookupHostnames(addresses):
    # lookup hostnames of all IP addresses
    hostnames = []
    for index, address in enumerate(addresses):
        print(index, address)
        pool = ThreadPool(100) 
        res = pool.apply_async(GetHostByAddress, args=(address,))
        try:
            hostname = res.get(0.01)  # Wait timeout seconds for func to complete.
            hostnames.append((index, hostname))
        except multiprocessing.TimeoutError:
            print("Aborting hostname lookup due to timeout")
            # pool.terminate()
            continue
    
    return hostnames
    
def LookupHostname(address):
    # lookup hostnames of all IP addresses
    pool = ThreadPool(1) 
    res = pool.apply_async(GetHostByAddress, args=(address,))    
    try:
        hostname = res.get(0.01)  # Wait timeout seconds for func to complete.       
    except multiprocessing.TimeoutError:
        print("Aborting hostname lookup due to timeout")
        # pool.terminate()
        hostname = ""

    return hostname
    
def LookupMacAddress(address):

    """ Finds the MAC Addresses using ARP

    NOTE: This finds mac addresses only within the subnet.
    It doesn't fetch mac addresses for routed network ips.
    """

    if platform.system() == 'Windows':
        arp_cmd = ['arp', '-a']
    else:
        arp_cmd = ['arp', '-n']
    
    pid = subprocess.Popen(arp_cmd + [address], stdout=subprocess.PIPE)
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
    mac_url = 'http://macvendors.co/api/%s'
    print(mac_url % mac)
    r = requests.get(mac_url % mac)
    logging.info("request URL: %s" % r.text)
    result = r.json()["result"]
    mfn = result["company"]
    
    return mfn

class PingAddress(threading.Thread):
    
    def __init__(self, addresses):
        
        threading.Thread.__init__(self)
        
        self._stop = False
        pub.subscribe(self.stop, "PingAddress.stop")
        
        self._addresses = addresses
        self.start()
        
    def stop(self, msg=None):
        self._stop = True
        logging.info("Killing thread: PingAddress")
        
    def run(self):    
        
        # Configure subprocess to hide the console window
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE
        
        for index, address in enumerate(self._addresses):
        
            if self._stop:
                return
            
            # For each IP address in the subnet, 
            # run the ping command with subprocess.popen interface
            address = str(address)
            cmd = ['ping', '-n', '1', '-w', '500', address]
            output = subprocess.Popen(cmd, stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
            output = output.decode('utf-8')
            
            # parse TTL and response time (ms)
            ttl = ""
            ms = ""
            mac = ""
            mfn = ""
            hostname = ""
            status = "Offline"
            if PLATFORM == "windows":
            
                if "Destination host unreachable" in output:
                    pass                 
                elif "Request timed out" in output:
                    mac = LookupMacAddress(address)
                    mfn = LookupManufacturers(mac)
                else:
                    status = "Online"
                    
                    ttl_start = output.index("TTL=")
                    ttl_end = output.index("\r\n\r\nPing statistics")
                    
                    ttl = output[ttl_start+len("TTL="):ttl_end]
                    
                    ms_start = output.index("Average = ")
                    ms = output[ms_start+len(("Average = ")):]
                    
                    mac = LookupMacAddress(address)
                    mfn = LookupManufacturers(mac)
                    
                    # hostname = LookupHostname(address)
                    
            params = {}
            params["index"] = index
            params["address"] = address
            params["ms"] = ms
            params["ttl"] = ttl
            params["mfn"] = mfn
            params["mac"] = mac
            params["status"] = status
            params["hostname"] = hostname
            wx.CallAfter(pub.sendMessage, "main.InsertAddress", params)

        wx.CallAfter(pub.sendMessage, "main.GetHostNames", "")
        
#end class PingAddress