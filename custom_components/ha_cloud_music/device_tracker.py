""" 

这个插件会把HA搞的卡死，千万别用
这个插件会把HA搞的卡死，千万别用
这个插件会把HA搞的卡死，千万别用

安装对应依赖
sudo apt-get install bluetooth libbluetooth-dev pkg-config libboost-python-dev libboost-thread-dev libglib2.0-dev python-dev
安装python插件
pip install pybluez


蓝牙设备追踪服务

device_tracker:
  - platform: ha_cloud_music
    mac: B4:C4:FC:66:A6:F0

"""
import logging
import time
import bluetooth
import voluptuous as vol
from homeassistant.components.device_tracker import PLATFORM_SCHEMA
from homeassistant.helpers.typing import HomeAssistantType
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.device_tracker.const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_TRACK_NEW,
    SCAN_INTERVAL,
    SOURCE_TYPE_BLUETOOTH,
)

_LOGGER = logging.getLogger(__name__)

VERSION = '1.2'
DOMAIN = 'ha_cloud_music'
BT_PREFIX = "HA_BT_"
CONF_MAC = 'mac'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_MAC): cv.string,
    }
)

def now_format_time():
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

# 安装扫描器
async def async_setup_scanner(
    hass: HomeAssistantType, config: dict, async_see, discovery_info=None
):
    # 设置扫描时间
    interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    # 获取扫描mac地址
    mac = config.get(CONF_MAC)
    # 定义扫描器    
    async def scanner(now=None):
        _LOGGER.debug('开始扫描：'+ now_format_time())
        name = bluetooth.lookup_name(mac.upper())
        _LOGGER.debug('扫描完成：'+ now_format_time())
        _LOGGER.debug(name)
        if name != None:
            attributes = {
                "mac": mac,
                "device_name": name,
                "scan_time": now_format_time()
            }
            await async_see(
                mac=f"{BT_PREFIX}{mac}",
                host_name=name,
                attributes=attributes,
                source_type='ha_cloud_music',
            )
    # 设置定时器
    hass.async_create_task(scanner())
    async_track_time_interval(hass, scanner, interval)

    # 项目信息
    _LOGGER.info('''
-------------------------------------------------------------------

    蓝牙设备追踪【作者QQ：635147515】

    版本：''' + VERSION + '''    

    介绍：这是一个在树莓派上使用的蓝牙扫描器

    项目地址：https://github.com/shaonianzhentan/ha_cloud_music
    
-------------------------------------------------------------------''')
    return True
