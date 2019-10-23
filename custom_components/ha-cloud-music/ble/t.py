# file: asynchronous-inquiry.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: demonstration of how to do asynchronous device discovery by subclassing
#       the DeviceDiscoverer class
# $Id: asynchronous-inquiry.py 405 2006-05-06 00:39:50Z albert $
#
# XXX Linux only (5/5/2006)

import bluetooth
import select
import json
import datetime

class MyDiscoverer(bluetooth.DeviceDiscoverer):
    
    def pre_inquiry(self):
        self._devices = []
        self._type = None
        self._services = None
        self._rssi = None
        self._address = None
        self._name = None
        self.done = False
    
    def device_discovered(self, address, device_class, rssi, name):
        #print("%s - %s" % (address, name))
        
        # get some information out of the device class and display it.
        # voodoo magic specified at:
        #
        # https://www.bluetooth.org/foundry/assignnumb/document/baseband
        major_classes = ( "Miscellaneous", 
                          "Computer", 
                          "Phone", 
                          "LAN/Network Access point", 
                          "Audio/Video", 
                          "Peripheral", 
                          "Imaging" )
        major_class = (device_class >> 8) & 0xf
        if major_class < 7:
            # 类型
            type = major_classes[major_class]
            #print("  %s" % major_classes[major_class])
        #else:
            #print("  Uncategorized")

        #print("  services:")
        service_classes = ( (16, "positioning"), 
                            (17, "networking"), 
                            (18, "rendering"), 
                            (19, "capturing"),
                            (20, "object transfer"), 
                            (21, "audio"), 
                            (22, "telephony"), 
                            (23, "information"))
        services = []
        for bitpos, classname in service_classes:
            if device_class & (1 << (bitpos-1)):
                services.append(classname)
                #print("    %s" % classname)
        #print("  RSSI: " + str(rssi))
        
        self._devices.append({
            "name": str(name, encoding='utf-8'),
            "mac": str(address),
            "services": str(services),
            "type": str(type),
            "rssi": str(rssi),
            "mi": str(pow(10, (abs(rssi) - self._a)/(10 * self._n)))
        })

    def inquiry_complete(self):
        self.done = True
        
    def read_devices(self, timeout = 10):
        readfiles = [ self, ]

        now = datetime.datetime.now()

        while (datetime.datetime.now() - now).seconds < timeout:
            rfds = select.select( readfiles, [], [] )[0]
            if self in rfds:
                self.process_event()
            if self.done: break
    
    def filter_devices(self, address):
        # 查看指定设备
        filter_list = filter(lambda x: x["mac"] == address.upper(), self._devices)
        devices = list(filter_list)
        if len(devices) > 0:
            return devices[0]
        return None
        
d = MyDiscoverer()
d._a = 59
d._n = 2.0
d.find_devices(lookup_names = True)
# 获取所有设备
d.read_devices()

print(json.dumps(d._devices, ensure_ascii=False))

# EC:01:EE:3C:A6:55