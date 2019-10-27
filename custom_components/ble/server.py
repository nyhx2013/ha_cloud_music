from http.server import HTTPServer, BaseHTTPRequestHandler
import bluetooth
import select
import json
import datetime
import time
import _thread

data = "[]"
host = ('localhost', 8321)

class MyDiscoverer(bluetooth.DeviceDiscoverer):

    def pre_inquiry(self):
        self._devices = []
        self.done = False

    def device_discovered(self, address, device_class, rssi, name):
        #print("%s - %s" % (address, name))

        # get some information out of the device class and display it.
        # voodoo magic specified at:
        #
        # https://www.bluetooth.org/foundry/assignnumb/document/baseband
        major_classes = ("Miscellaneous",
                         "Computer",
                         "Phone",
                         "LAN/Network Access point",
                         "Audio/Video",
                         "Peripheral",
                         "Imaging")
        major_class = (device_class >> 8) & 0xf
        if major_class < 7:
            # 类型
            class_type = major_classes[major_class]
            #print("  %s" % major_classes[major_class])
        # else:
            #print("  Uncategorized")

        #print("  services:")
        service_classes = ((16, "positioning"),
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
            "type": str(class_type),
            "rssi": str(rssi),
            "time": str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        })

    def inquiry_complete(self):
        self.done = True

    def read_devices(self, timeout=10):
        readfiles = [self, ]

        now = datetime.datetime.now()

        while (datetime.datetime.now() - now).seconds < timeout:
            rfds = select.select(readfiles, [], [])[0]
            if self in rfds:
                self.process_event()
            if self.done:
                break

    def filter_devices(self, address):
        # 查看指定设备
        filter_list = filter(
            lambda x: x["mac"] == address.upper(), self._devices)
        devices = list(filter_list)
        if len(devices) > 0:
            return devices[0]
        return None

# 循环调用        
def loop():
    while True:
        try:
            d = MyDiscoverer()
            d.find_devices(lookup_names=True)
            # 获取所有设备
            d.read_devices()
            global data
            data = json.dumps(d._devices, ensure_ascii=False)
        except Exception as e:
            print('Error:',e)
        
_thread.start_new_thread(loop,())

class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        path = str(self.path)
        if path == "/ble":
            self.wfile.write(data.encode())
        else:
            self.wfile.write("404".encode())

if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()