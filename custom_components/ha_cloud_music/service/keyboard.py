#!/usr/bin/env python
#coding: utf-8

'''
安装依赖
pip install evdev

运行程序
python3 keyboard.py
'''
from evdev import InputDevice
from select import select

def detectInputKey():
    # event1是usb对应的键盘
    dev = InputDevice('/dev/input/event1')
    while True:
        select([dev], [], [])
        for event in dev.read():
            if (event.value == 1 or event.value == 0) and event.code != 0:
               print(event.code, event.value)

if __name__ == '__main__':
    detectInputKey()
