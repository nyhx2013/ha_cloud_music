#!/usr/bin/env python
#coding: utf-8

'''
查看输入设备列表ls /dev/input

查看输入设备的详细信息 cat /proc/bus/input/devices

安装依赖
pip install evdev
pip install pyyaml
pip install requests

运行程序
python3 keyboard.py
'''
from evdev import InputDevice
from select import select
from requests import post
import json
import yaml
import os

# 获取yaml文件数据
current_path = os.path.abspath(".")
yaml_path = os.path.join(current_path, "keyboard.yaml")
def getConfig():
    file = open(yaml_path, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    data = yaml.full_load(file_data)
    return data

# 调用服务
def call_service(hass_token, domain, service, data):
    url = 'http://localhost:8123/api/services/'+ domain +'/'+ service
    headers = {
        'Authorization': 'Bearer ' + hass_token,
        'content-type': 'application/json',
    }
    response = post(url, json.dumps(data), headers=headers)
    print(response.text)

def detectInputKey():
    # event1是usb对应的键盘
    dev = InputDevice('/dev/input/event7')
    while True:
        select([dev], [], [])
        for event in dev.read():
            if (event.value == 1 or event.value == 0) and event.code != 0:
                print(event.code, event.value)
                if (event.value == 1):
                    print('按下')
                else:
                    print('放开')
                    # 获取配置文件
                    cfg = getConfig()
                    _token = cfg['token']
                    _code = event.code
                    # 如果当前code定义
                    if _code in cfg['key']:
                        _result = cfg['key'][_code]
                        # 如果有定义服务，则调用
                        if _result != None:
                            _sv = _result['service'].split('.')
                            _domain = _sv[0]
                            _service = _sv[1]
                            call_service(_token, _domain, _service, _result['data'])
                    else:
                        print('当前未定义处理事件')

if __name__ == '__main__':
    detectInputKey()
