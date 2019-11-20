"""
安装对应依赖
sudo apt-get install bluetooth libbluetooth-dev pkg-config libboost-python-dev libboost-thread-dev libglib2.0-dev python-dev
安装python插件
pip install pybluez
启用扫描服务
python3 ble.py

配置蓝牙设备的跟踪.
    mac: 要配置的mac地址，必须大写，多个以逗号分隔
    
device_tracker:
  - platform: ha_cloud_music  
    mac: 'B4:C4:FC:66:A6:F0'

"""
import asyncio
import logging
from typing import List, Set, Tuple, Optional

# pylint: disable=import-error

import bluetooth
import select
import datetime
import time
import voluptuous as vol
import requests
import uuid
import aiohttp
from aiohttp import web
from aiohttp.web import FileResponse
from homeassistant.components.http import HomeAssistantView

from homeassistant.components.device_tracker import PLATFORM_SCHEMA
from homeassistant.components.device_tracker.const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_TRACK_NEW,    
    SCAN_INTERVAL,
    SOURCE_TYPE_BLUETOOTH,
)
from homeassistant.components.device_tracker.legacy import (
    YAML_DEVICES,
    async_load_config,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import HomeAssistantType

###########################发现设备################################


_LOGGER = logging.getLogger(__name__)


DOMAIN = 'ble_tracker'
BT_PREFIX = "BT_"
CONF_FILTER_MAC = "mac"
API_KEY = str(uuid.uuid4())


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_FILTER_MAC): cv.ensure_list_csv,
    }
)


def is_bluetooth_device(device) -> bool:
    """通过mac检查设备是否是蓝牙设备."""
    return device.mac and device.mac[:3].upper() == BT_PREFIX


def discover_devices(filter_mac):
    try:
        r = requests.get("http://localhost:8321/ble?mac=" + (','.join(filter_mac)) +"&token=" + API_KEY, timeout=5)
        ble = r.json()
        # _LOGGER.info(ble)
        filter_list = filter(lambda x: filter_mac.count(x["mac"]) == 1, ble)
        return list(filter_list)
    except Exception as e:
        print(e)
        _LOGGER.error("蓝牙监听服务未开启。。。http://localhost:8321")
        return []

async def see_device(
    hass: HomeAssistantType, async_see, result
) -> None:
    mac = result['mac']
    name = result['name']
    attributes = {
        "device_name": name,
        "services": result['services'],
        "rssi": result['rssi'],
        "type": result['type'],
        "scan_time": result['time'],
        "update_time": str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    }
    await async_see(
        mac=f"{BT_PREFIX}{mac}",
        host_name=mac,
        attributes=attributes,
        source_type=SOURCE_TYPE_BLUETOOTH,
    )


async def async_setup_scanner(
    hass: HomeAssistantType, config: dict, async_see, discovery_info=None
):
    # 设置扫描时间
    interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    # 获取要过滤的蓝牙
    filter_mac = config.get(CONF_FILTER_MAC, [])
    
    

    update_bluetooth_lock = asyncio.Lock()

    async def perform_bluetooth_update():
        """发现蓝牙设备并更新状态."""

        # _LOGGER.info("执行蓝牙设备发现和更新")
        tasks = []

        try:
            # 获取所有设备
            devices = await hass.async_add_executor_job(discover_devices, filter_mac)
            # 遍历所有设备
            for item in devices:
                tasks.append(see_device(hass, async_see, item))

            if tasks:
                await asyncio.wait(tasks)

        except bluetooth.BluetoothError:
            _LOGGER.exception("Error looking up Bluetooth device")

    async def update_bluetooth(now=None):
        """Lookup Bluetooth devices and update status."""

        # 如果更新正在进行，我们什么也不做
        if update_bluetooth_lock.locked():
            _LOGGER.info(
                "上次执行更新的时间比预定的更新间隔长 %s",
                interval,
            )
            return

        async with update_bluetooth_lock:
            await perform_bluetooth_update()

    hass.async_create_task(update_bluetooth())
    async_track_time_interval(hass, update_bluetooth, interval)
    
    
    # 创建API网关
    class HassGateView(HomeAssistantView):
        url = '/' + DOMAIN + '-api'
        name = DOMAIN
        requires_auth = False
        async def post(self, request):
            """更新状态实体."""
            _LOGGER.info("更新实体状态")
            _LOGGER.info(request.headers['Authorization'])
            # 如果密钥一致，则更新状态
            if request.headers['Authorization'] == API_KEY:
                response = await request.json()
                await see_device(hass, async_see, response)
                
            return self.json(response)                
    
    # 创建HTTP服务
    hass.http.register_view(HassGateView)
    return True

    
