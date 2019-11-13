"""
自定义的灯

#灯的实体
light:
  - platform: ha_cloud_music
    name: 彩灯
    turn_on_service: 这里是脚本服务或自动化服务
    turn_off_service: 这里是脚本服务或自动化服务
    
"""
import asyncio
import datetime
from datetime import timedelta
from functools import partial
import logging
import os
from math import ceil

import voluptuous as vol
import json

from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_HS_COLOR, ATTR_COLOR_TEMP, ATTR_ENTITY_ID, DOMAIN,
    PLATFORM_SCHEMA, SUPPORT_BRIGHTNESS, SUPPORT_COLOR, SUPPORT_COLOR_TEMP,
    Light)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.util import color, dt

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = '彩灯'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional('turn_on_service'): cv.string,
    vol.Optional('turn_off_service'): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the light from config."""

    name = config.get(CONF_NAME)

    devices = []
    secondary_device = HALight(name, hass, config)
    devices.append(secondary_device)

    async_add_entities(devices, update_before_add=True)

# 所有灯的基类


class HALight(Light):
    """Representation of a Abstract Xiaomi Philips Light."""

    def __init__(self, name, hass, config):
        """Initialize the light device."""
        self._name = name
        self._hass = hass
        self._cfg = config
        self._unique_id = None
        self._brightness = None
        self._available = False
        self._state = None
        self._state_attrs = {
        }

    @property
    def should_poll(self):
        """Poll the light."""
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
    def available(self):
        """Return true when state is known."""
        return self._available

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def supported_features(self):
        """Return the supported features."""
        return SUPPORT_BRIGHTNESS

    # 调用服务
    async def async_call_service(self, service):
        if service != None:
            arr = service.split('.', 1)
            if arr[0] == 'script':
                await self._hass.services.async_call('script', str(arr[1]))
            elif arr[0] == 'automation':
                await self._hass.services.async_call('automation', 'trigger', {'entity_id': service})

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
            #_LOGGER.info('亮度：%s', self._brightness)

        # 如果是初始化打开，则亮度为255
        if self.is_on == None:
            self._brightness = 255

        if self.is_on == None or self.is_on == False:
            await self.async_call_service(self._cfg.get('turn_on_service'))
        self._state = True

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        if self.is_on == True:
            await self.async_call_service(self._cfg.get('turn_off_service'))
        self._state = False

    async def async_update(self):
        filename = os.path.dirname(__file__) + \
            '/_state-light-' + self._name + '.json'
        """Fetch state from the device."""
        if self._available == False:
            self._available = True
            # 初始化的情况下读取存储数据
            try:
                with open(filename, 'r') as f_obj:
                    entity = json.load(f_obj)
                self._state = entity['state']
                self._brightness = entity['brightness']
            except:
                print('初始化数据')
            return

        # 更新数据
        entity_value = {'state': self._state, 'brightness': self._brightness}
        with open(filename, 'w') as f_obj:
            json.dump(entity_value, f_obj)