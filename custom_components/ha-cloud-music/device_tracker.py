"""
蓝牙设备的跟踪.

device_tracker:
  - platform: ha-cloud-music
    filter_mac: 'B4:C4:FC:66:A6:F0'

"""
import asyncio
import logging
from typing import List, Set, Tuple, Optional

# pylint: disable=import-error

import bluetooth
import select
import datetime
import voluptuous as vol
import requests

from homeassistant.components.device_tracker import PLATFORM_SCHEMA
from homeassistant.components.device_tracker.const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_TRACK_NEW,
    DOMAIN,
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

BT_PREFIX = "BT_"


CONF_DEVICE_ID = "device_id"
CONF_FILTER_MAC = "filter_mac"

DEFAULT_DEVICE_ID = -1

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_FILTER_MAC): cv.ensure_list_csv,
        vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): vol.All(
            vol.Coerce(int), vol.Range(min=-1)
        ),
    }
)


def is_bluetooth_device(device) -> bool:
    """通过mac检查设备是否是蓝牙设备."""
    return device.mac and device.mac[:3].upper() == BT_PREFIX


def discover_devices(device_id: int, filter_mac):    
    r = requests.get("http://localhost:8321/ble")
    ble = r.json()
    _LOGGER.info(ble)
    filter_list = filter(lambda x: filter_mac.count(x["mac"]) == 1, ble)
    return list(filter_list)


async def see_device(
    hass: HomeAssistantType, async_see, result
) -> None:
    mac = result['mac']
    name = result['name']
    attributes = {
        "name": name,
        "services": result['services'],
        "rssi": result['rssi'],
        "type": result['type'],
        "mi": result['mi']
    }    
    await async_see(
        mac=f"{BT_PREFIX}{mac}",
        host_name=name,
        attributes=attributes,
        source_type=SOURCE_TYPE_BLUETOOTH,
    )

async def get_tracking_devices(hass: HomeAssistantType) -> Tuple[Set[str], Set[str]]:
    """
    加载所有已知设备.
    我们只需要这些设备，所以请将“家庭和家庭范围”设置为
    """
    yaml_path: str = hass.config.path(YAML_DEVICES)

    devices = await async_load_config(yaml_path, hass, 0)
    bluetooth_devices = [device for device in devices if is_bluetooth_device(device)]

    devices_to_track: Set[str] = {
        device.mac[3:] for device in bluetooth_devices if device.track
    }
    devices_to_not_track: Set[str] = {
        device.mac[3:] for device in bluetooth_devices if not device.track
    }

    return devices_to_track, devices_to_not_track
    
async def async_setup_scanner(
    hass: HomeAssistantType, config: dict, async_see, discovery_info=None
):
    """设置蓝牙扫描仪."""
    device_id: int = config.get(CONF_DEVICE_ID)
    # 设置扫描时间
    interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    # 获取要过滤的蓝牙
    filter_mac = config.get(CONF_FILTER_MAC, [])
        
    update_bluetooth_lock = asyncio.Lock()

    devices_to_track, devices_to_not_track = await get_tracking_devices(hass)

    async def perform_bluetooth_update():
        """发现蓝牙设备并更新状态."""

        #_LOGGER.info("执行蓝牙设备发现和更新")
        tasks = []

        try:            
            # 获取所有设备
            devices = await hass.async_add_executor_job(discover_devices, device_id, filter_mac)
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

    return True
