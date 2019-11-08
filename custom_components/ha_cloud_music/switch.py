'''
将当前状态保存到本地


#开关
switch:
  - platform: ha_cloud_music
    name: 电视
    turn_on_service: 这里是脚本服务或自动化服务（参考下面插座配置）
    turn_off_service: 这里是脚本服务或自动化服务（参考下面插座配置）
  - platform: ha_cloud_music
    name: 插座
    turn_on_service: script.123456789
    turn_off_service: automation.123456789

'''
import asyncio
from functools import partial
import logging
import os
import json

import voluptuous as vol

from homeassistant.components.switch import (
    DOMAIN, PLATFORM_SCHEMA, SwitchDevice)
from homeassistant.const import (
    ATTR_ENTITY_ID, CONF_HOST, CONF_NAME, CONF_TOKEN)
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = '开关'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional('turn_on_service'): cv.string,
    vol.Optional('turn_off_service'): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the switch from config."""

    name = config.get(CONF_NAME)

    devices = []
    unique_id = None

    device = XiaomiPlugGenericSwitch(name, unique_id, hass, config)
    devices.append(device)

    async_add_entities(devices, update_before_add=True)


class XiaomiPlugGenericSwitch(SwitchDevice):
    """Representation of a Xiaomi Plug Generic."""

    def __init__(self, name, unique_id, hass, config):
        """Initialize the plug switch."""
        self._name = name
        self._unique_id = unique_id
        self._hass = hass
        self._cfg = config
        self._icon = 'mdi:power-socket'
        self._available = False
        self._state = None
        self._state_attrs = {
            # ATTR_TEMPERATURE: None,
        }
        self._skip_update = False

    @property
    def should_poll(self):
        """Poll the plug."""
        return True

    @property
    def unique_id(self):
        """Return an unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return self._icon

    @property
    def available(self):
        """Return true when state is known."""
        return self._available

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    # 调用服务    
    async def async_call_service(self, service):
        if service != None:
            arr = service.split('.', 1)
            if arr[0] == 'script':            
                await self._hass.services.async_call('script', str(arr[1]))
            elif arr[0] == 'automation':
                await self._hass.services.async_call('automation', 'trigger', {'entity_id': service})

    async def async_turn_on(self, **kwargs):
        """Turn the plug on."""
        if self.is_on == False:
            await self.async_call_service(self._cfg.get('turn_on_service'))            
        self._state = True

    async def async_turn_off(self, **kwargs):
        """Turn the plug off."""
        if self.is_on == True:
            await self.async_call_service(self._cfg.get('turn_off_service'))
        self._state = False

    async def async_update(self):
        filename = os.path.dirname(__file__) + '/_state-switch-' + self._name + '.json'
        """Fetch state from the device."""
        if self._available == False:
            self._available = True
            # 初始化的情况下读取存储数据            
            try:
                with open(filename, 'r') as f_obj:
                    entity = json.load(f_obj)
                self._state = entity['state']
                # self._state_attrs[ATTR_TEMPERATURE] = entity['temperature']
            except:
              print('初始化数据')
            return
        
        if self._state == None:
            self._state = False
        # 更新数据
        entity_value = {'state': self._state}
        with open(filename, 'w') as f_obj:
            json.dump(entity_value, f_obj)
   
            ###
    async def async_set_wifi_led_on(self):
        """Turn the wifi led on."""
        return

    async def async_set_wifi_led_off(self):
        """Turn the wifi led on."""
        return

    async def async_set_power_price(self, price: int):
        """Set the power price."""
        return