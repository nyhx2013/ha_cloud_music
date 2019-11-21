'''
安装对应依赖
sudo apt-get install bluetooth libbluetooth-dev pkg-config libboost-python-dev libboost-thread-dev libglib2.0-dev python-dev
安装python插件
pip install pybluez
开启扫描服务
python3 ble.py
'''

import bluetooth
import select
import json
import os
import yaml
import sys
import datetime
import time
import _thread
from requests import post

# 扫描时间
scan_time = datetime.datetime.now()
# 要过滤的设备
filter_mac = []
# 与HA通信的token
HAToken = ""

# 获取yaml文件数据
current_path = os.path.abspath(".")
yaml_path = os.path.join(current_path, "config.yaml")


def getConfig():
    file = open(yaml_path, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    data = yaml.full_load(file_data)
    return data


# 重启程序
def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

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
            # print("  %s" % major_classes[major_class])
        # else:
            # print("  Uncategorized")

        # print("  services:")
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
                # print("    %s" % classname)
        # print("  RSSI: " + str(rssi))

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
                'Authorization': 'Bearer ' + HAToken,
                'content-type': 'application/json',
            }
            try:
                response = post(url, json.dumps(_ble_info), headers=headers)
                print("【更新结果】" + response.text)
            except Exception as e:
                print("【出现异常】HomeAssistant没有响应")

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

                
# 循环调用
while True:
    try:
        # 读取配置
        cfg = getConfig()
        HAToken = cfg['token']
        filter_mac = cfg['mac']
        # 开始扫描设备
        print("【" + str(datetime.datetime.now()) + "】【扫描设备】开始扫描蓝牙设备")
        d = MyDiscoverer()
        d.find_devices(lookup_names=True)
        # 获取所有设备
        d.read_devices()
        print("【" + str(datetime.datetime.now()) + "】【扫描设备】扫描完成，当前蓝牙设备数量： ", len(d._devices))
        time.sleep(12)
    except Exception as e:
        print('Error:', e)