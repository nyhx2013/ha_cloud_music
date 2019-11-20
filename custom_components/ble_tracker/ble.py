'''
安装对应依赖
sudo apt-get install bluetooth libbluetooth-dev pkg-config libboost-python-dev libboost-thread-dev libglib2.0-dev python-dev
安装python插件
pip install pybluez
开启服务
python3 ble.py

调用URL获取扫描到的蓝牙列表
http://localhost:8321/ble
'''

from http.server import HTTPServer, BaseHTTPRequestHandler
import bluetooth
import select
import json
import os
import sys
import datetime
import time
import _thread
from requests import post
from urllib import parse

HTTP_DATA = "[]"
# 与HA通信的token
HAToken = ""
# 要过滤的设备
filter_mac = []

scan_time = datetime.datetime.now()
host = ('0.0.0.0', 8321)

# 蓝牙扫描类
class MyDiscoverer(bluetooth.DeviceDiscoverer):

    def pre_inquiry(self):
        self._devices = []
        self.done = False

    def device_discovered(self, address, device_class, rssi, name):
        print("%s - %s" % (address, str(name, encoding='utf-8')))

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

        # 设置扫描时间
        global scan_time
        scan_time = datetime.datetime.now()
        mac = str(address)
        _ble_info = {
            "name": str(name, encoding='utf-8'),
            "mac": mac,
            "services": str(services),
            "type": str(class_type),
            "rssi": str(rssi),
            "time": str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        }        
        self._devices.append(_ble_info)
        
        # 如果token不为空，当前设备存在于过滤设备中
        # 强制更新设备状态
        if HAToken != '' and len(filter_mac) > 0 and filter_mac.count(mac) > 0:            
            print("【" + str(datetime.datetime.now()) + "】执行更新服务")
            # 通信HA更新
            url = 'http://localhost:8123/ble_tracker-api'
            headers = {
                'Authorization': HAToken,
                'content-type': 'application/json',
            }
            response = post(url, json.dumps(_ble_info), headers=headers)
            print("【更新结果】" + response.text)

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
            print("【" + str(datetime.datetime.now()) + "】【扫描设备】开始扫描蓝牙设备")
            d = MyDiscoverer()
            d.find_devices(lookup_names=True)
            # 获取所有设备
            d.read_devices()
            print("【" + str(datetime.datetime.now()) + "】【扫描设备】扫描完成，当前蓝牙设备数量： ", len(d._devices))
            global HTTP_DATA
            HTTP_DATA = json.dumps(d._devices, ensure_ascii=False)
            global data_list
            data_list = d._devices
            time.sleep(12)
        except Exception as e:
            print('Error:', e)


_thread.start_new_thread(loop, ())

# 重启程序
def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

# HTTP服务
class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        # 解析URL地址
        res = parse.urlparse('http://localhost:8321' + str(self.path))
        # 参数转成字典
        query = parse.parse_qs(res.query)
        print(query)
        if res.path == "/ble":
            # 写入数据
            self.wfile.write(HTTP_DATA.encode())
            # 如果当前时间和扫描时间相差超过10分钟，则重启程序
            print("【" + str(datetime.datetime.now()) + "】【读取状态】上次扫描时间：", scan_time)
            seconds = (datetime.datetime.now() - scan_time).seconds
            print("【" + str(datetime.datetime.now()) + "】【读取状态】距上次扫描相差时间：", seconds)
            if seconds > 60:
                restart_program()
            
            # 设置与HA通信的token
            if 'token' in query:
                global HAToken
                HAToken = query['token'][0]
            # 设置过滤的mac地址
            if 'mac' in query:
                global filter_mac
                filter_mac = query['mac'][0].split(',')
        else:
            self.wfile.write("404".encode())


if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
