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


# 调用服务
def call_service(hass_token, domain, service, data):
    url = 'http://localhost:8123/api/services/'+ domain +'/'+ service
    headers = {
        'Authorization': 'Bearer ' + hass_token,
        'content-type': 'application/json',
    }
    response = post(url, json.dumps(data), headers=headers)
    print(response.text)

# 键码处理事件
def keyEvent(code, is_long):
  if is_long == 1:
    print('执行长按事件')
  else:
    print('执行短按事件')


# 判断是否按下键
is_keydown = False

# 监听键盘按键
def detectInputKey():
    input_event = '/dev/input/event5'
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
