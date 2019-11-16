"""判断当前日期是否节假日."""
import logging
import time
import requests
from datetime import datetime, timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, WEEKDAYS
from homeassistant.components.binary_sensor import BinarySensorDevice
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "节假日"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Workday sensor."""
    sensor_name = config.get(CONF_NAME)
    _LOGGER.info('节假日传感器 安装成功',)
    add_entities(
        [IsHolidaySensor(sensor_name)],
        True,
    )

# 查询列表是否有假日
def findHoliday(today, _list):
    if (len(list(filter(lambda x: x['date'] == today and x['status'] == '1', _list))) > 0):
        return True
    # 如果有状态为2的，说明这一天是双休日，但是要上班
    if (len(list(filter(lambda x: x['date'] == today and x['status'] == '2', _list))) > 0):
        return False
    return None

class IsHolidaySensor(BinarySensorDevice):
    """Implementation of a Workday sensor."""

    def __init__(self, name):
        """Initialize the Workday sensor."""
        self._name = name     
        self._state = False
        self._today = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the device."""
        return self._state
    
    @property
    def today(self):
        localtime = time.localtime(time.time())
        return "{}-{}-{}".format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday)

    @property
    def state_attributes(self):
        """Return the attributes of the entity."""
        # return self._attributes
        return {}
    
    # 日期格式化
    def date_format(self, _date):
        return time.mktime(time.strptime(_date,"%Y-%m-%d"))

    # 判断当天是否假日
    def is_holiday(self, _date):
        # 获取当前日期
        localtime = time.localtime(_date)
        ym = "{}年{}月".format(localtime.tm_year,localtime.tm_mon)
        today = "{}-{}-{}".format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday)
        #today = '2019-10-1'
        _LOGGER.info('获取当前日期： %s',today)
        # 获取百度日历
        res = requests.get('https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?query=' + ym 
        + '&co=&resource_id=6018&t=1573873782858&ie=utf8&oe=gbk&cb=op_aladdin_callback&format=json&tn=baidu&cb=&_=1573873715796')
        r = res.json()
        obj = r['data'][0]
        # 判断是否在我国传统假日列表里
        if (len(list(filter(lambda x: x['startday'] == today, obj['holidaylist']))) > 0):
            return True
        # 判断是否在传统假日连休列表里
        _holiday = obj['holiday']
        if isinstance(_holiday,list):
            for item in _holiday:
                _result = findHoliday(today, item['list'])
                if _result != None:
                    return _result
        elif isinstance(_holiday,dict):
            _result = findHoliday(today, _holiday['list'])
            if _result != None:
                return _result    
        # 判断是否双休日
        if localtime.tm_wday == 5 or localtime.tm_wday == 6:
            return True
        
        return False

    async def async_update(self):
        """Get date and look whether it is a holiday."""
        if self._today != self.today:
            self._state = self.is_holiday(time.time())
            self._today = self.today
