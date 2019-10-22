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
class MyDiscoverer(bluetooth.DeviceDiscoverer):
    
    def pre_inquiry(self):
        self._devices = []
        self.done = False
    
    def device_discovered(self, address, device_class, rssi, name):
        # print("%s - %s" % (address, name))
        
        # get some information out of the device class and display it.
        # voodoo magic specified at:
        #
        # https://www.bluetooth.org/foundry/assignnumb/document/baseband
        major_classes = ( "Miscellaneous", 
                          "Computer", 
                          "Phone", 
                          "LAN/Network Access point", 
                          "Audio/Video", 
                          "Peripheral", 
                          "Imaging" )
        major_class = (device_class >> 8) & 0xf
        if major_class < 7:
            # 类型
            type = major_classes[major_class]
            # print("  %s" % major_classes[major_class])
        else:
            print("  Uncategorized")

        # print("  services:")
        service_classes = ( (16, "positioning"), 
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
        
        self._devices.append({
            "name": name,
            "mac": address,            
            "services": services,
            "type": type,
            "rssi": rssi,
            "mi": pow(10, (abs(rssi) - self._a)/(10 * self._n))
        })

    def inquiry_complete(self):
        self.done = True
        
    def read_devices(self, timeout = 10):
        readfiles = [ self, ]

        now = datetime.datetime.now()

        while (datetime.datetime.now() - now).seconds < timeout:
            rfds = select.select( readfiles, [], [] )[0]
            if self in rfds:
                self.process_event()
            if self.done: break
    
    def filter_devices(self, address):
        # 查看指定设备
        filter_list = filter(lambda x: x["mac"] == address.upper(), self._devices)
        devices = list(filter_list)
        if len(devices) > 0:
            return devices[0]
        return None
        
discoverer = MyDiscoverer()

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
    """发现蓝牙设备.
    result = bluetooth.discover_devices(
        duration=8,
        lookup_names=True,
        flush_cache=True,
        lookup_class=False,
        device_id=device_id,
    )
    """
    #_LOGGER.info("发现蓝牙设备 = %d", len(result))    
    #_LOGGER.info(filter_mac)
    #_LOGGER.info(result)    
    #_LOGGER.info("获取所有设备")    
    # 获取所有设备
    global discoverer
    discoverer = MyDiscoverer()
    discoverer._a = 59 # 发射端和接收端相隔1米时的信号强度
    discoverer._n = 2.0 # 环境衰减因子
    discoverer.find_devices(lookup_names = True)
    discoverer.read_devices(12)
    filter_list = filter(lambda x: filter_mac.count(x["mac"]) == 1, discoverer._devices)
    return list(filter_list)


async def see_device(
    hass: HomeAssistantType, async_see, mac: str
) -> None:
    """将设备标记为可见."""
    result = discoverer.filter_devices(mac)
    if result == None:
        return None
    
    attributes = {
        "name": result['name'],
        "services": result['services'],
        "rssi": result['rssi'],
        "type": result['type'],
        "mi": result['mi']
    }
    
    await async_see(
        mac=f"{BT_PREFIX}{mac}",
        host_name=result['mac'],
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
                # 判断mac值是否存在
                mac = item['mac']
                if mac not in devices_to_track and mac not in devices_to_not_track:
                    devices_to_track.add(mac)
            
            # 遍历所有已知设备
            for mac in devices_to_track:
                # 添加设备
                tasks.append(see_device(hass, async_see, mac))

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
