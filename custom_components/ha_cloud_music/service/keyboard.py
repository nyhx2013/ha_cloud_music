#!/usr/bin/env python
#coding: utf-8

'''
查看输入设备列表ls /dev/input

查看输入设备的详细信息 cat /proc/bus/input/devices

安装依赖
pip install evdev

运行程序
python3 keyboard.py
'''
from evdev import InputDevice
from select import select
from requests import post
import json

# 调用服务
def call_service(domain, service, data):
    url = 'http://localhost:8123/api/services/'+ domain +'/'+ service
    headers = {
        'Authorization': 'Bearer 这里是密钥',
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
                if (event.value == 1):
                    print('按下')
                else:
                    print('放开')
                    if (event.code == 71):
                        # 7
                        call_service('light', 'toggle', { 'entity_id': 'light.xiaomi_philips_light'})
                    elif (event.code == 72):
                        # 8
                        call_service('light', 'toggle', { 'entity_id': 'light.cai_deng'})
                    elif (event.code == 73):
                        # 9
                        print('not')
                    elif (event.code == 74):
                        # -
                        call_service('media_player', 'volume_down', { 'entity_id': 'media_player.ha_cloud_music'})
                    elif (event.code == 75):
                        # 4
                        call_service('switch', 'toggle', { 'entity_id': 'switch.dian_shi'})
                    elif (event.code == 76):
                        # 5
                        call_service('switch', 'toggle', { 'entity_id': 'switch.tian_mao_he_zi'})
                    elif (event.code == 77):
                        # 6    
                        print('6')
                    elif (event.code == 78):
                        # +
                        call_service('media_player', 'volume_up', { 'entity_id': 'media_player.ha_cloud_music'})
                    elif (event.code == 79):
                        # 1
                        call_service('media_player', 'media_previous_track', { 'entity_id': 'media_player.ha_cloud_music'})
                    elif (event.code == 80):
                        # 2
                        call_service('media_player', 'media_play_pause', { 'entity_id': 'media_player.ha_cloud_music'})
                    elif (event.code == 81):
                        # 3
                        call_service('media_player', 'media_next_track', { 'entity_id': 'media_player.ha_cloud_music'})
                print(event.code, event.value)

if __name__ == '__main__':
    detectInputKey()
