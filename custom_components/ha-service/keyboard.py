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
import time
import yaml
import os

# 获取yaml文件数据
current_path = os.path.abspath(".")
yaml_path = os.path.join(current_path, "config.yaml")
def getConfig():
    file = open(yaml_path, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    data = yaml.full_load(file_data)
    return data

# 调用服务
def call_service(hass_token, domain, service, data):
    try:
        url = 'http://localhost:8123/api/services/'+ domain +'/'+ service
        headers = {
            'Authorization': 'Bearer ' + hass_token,
            'content-type': 'application/json',
        }
        response = post(url, json.dumps(data), headers=headers)
        print(response.text)
    except Exception as e:
        print('Error:', e)
    
# 键码处理事件
def keyEvent(code, is_long):
    # 获取配置文件
    cfg = getConfig()
    _token = cfg['token']
    # 如果当前code定义
    if code in cfg['key']:
        _result = cfg['key'][code]
        # 如果有定义服务，则调用
        if _result != None:
            if is_long == 1:
                print('执行长按事件')
                _sv = _result['long_service'].split('.')
                _domain = _sv[0]
                _service = _sv[1]
                call_service(_token, _domain, _service, _result['long_data'])
            else:
                print('执行短按事件')
                _sv = _result['service'].split('.')
                _domain = _sv[0]
                _service = _sv[1]
                call_service(_token, _domain, _service, _result['data'])



# 判断是否按下键
is_keydown = False

# 监听键盘按键
def detectInputKey():
    input_event = '/dev/input/event3'
    print('''
    开始监听键盘设备：''' + input_event + '''
    注意：
        如果按下键没有反应，请更改对应的驱动
        把 event5 改成 对应的键盘驱动
        不知道就从0往后试验 event0、event1、event2、event3、event4、
    ''')
    dev = InputDevice(input_event)
    while True:
        select([dev], [], [])
        for event in dev.read():
            if (event.value == 1 or event.value == 0) and event.code != 0:
                code = event.code
                print('当前键码： ' + str(code))
                global is_keydown
                if (event.value == 1):
                    print('开始记录按下时间')
                    if is_keydown == False:
                        is_keydown = True
                        # 记录按下时间
                        global key_record
                        key_record = {code:  time.time()}
                else:
                    if code in key_record:
                        # 如果当前时间和按下时间，间隔1秒以上，说明长按
                        if time.time() - key_record[code] > 1:
                            print('长按')
                            keyEvent(code, 1)
                        else:
                            print('短按')
                            keyEvent(code, 0)
                    # 重置为否
                    is_keydown = False


if __name__ == '__main__':
    detectInputKey()
