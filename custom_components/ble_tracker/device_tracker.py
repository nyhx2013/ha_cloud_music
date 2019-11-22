""" 

蓝牙设备追踪服务

device_tracker:
  - platform: ble_tracker

"""
import logging
import time
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.typing import HomeAssistantType

_LOGGER = logging.getLogger(__name__)

VERSION = '1.1'
DOMAIN = 'ble_tracker'
BT_PREFIX = "BLE_"

# 设置设备
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
        host_name=name,
        attributes=attributes,
        source_type='ble_tracker',
    )

# 安装扫描器
async def async_setup_scanner(
    hass: HomeAssistantType, config: dict, async_see, discovery_info=None
):
    _LOGGER.info('''
-------------------------------------------------------------------

    蓝牙设备追踪【作者QQ：635147515】

    版本：''' + VERSION + '''    

    介绍：这是一个在树莓派上使用的，与蓝牙扫描服务搭配使用的插件

    项目地址：https://github.com/shaonianzhentan/ha_cloud_music/tree/master/custom_components/ble_tracker
    
-------------------------------------------------------------------''')

    # 创建API网关
    class HAGateView(HomeAssistantView):
        url = '/' + DOMAIN + '-api'
        name = DOMAIN
        requires_auth = True
        async def post(self, request):
            """更新状态实体."""
            response = await request.json()
            await see_device(hass, async_see, response)
            return self.json(response)                
    
    # 创建HTTP服务
    hass.http.register_view(HAGateView)
    return True

    
