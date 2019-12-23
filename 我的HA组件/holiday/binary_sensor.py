"""
功能：判断当前日期是否节假日.

配置
binary_sensor:
  - platform: holiday

"""
import logging
import time
import requests
import json
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
    
    _sensor = IsHolidaySensor(sensor_name)
    _LOGGER.info('''
    --------------------------------------------
    
    节假日传感器 安装成功
    
    今天是：'''+ _sensor.today +'''
    
    --------------------------------------------
    ''')
    add_entities(
        [_sensor],
        True,
    )

class IsHolidaySensor(BinarySensorDevice):
    """Implementation of a Workday sensor."""

    def __init__(self, name):
        """Initialize the Workday sensor."""
        self._name = name     
        self._state = False
        self._today = None
        # 忌
        self._avoid = None
        # 宜
        self._suit = None
        self._holiday_name = None
        self._week = None
        # 五行
        self._wuxing = None
        self._suici = None
        self._nongli = None
        self._gongli = None
        self._fu = None
        self._xi = None
        self._cai = None
        self._shengxiao = None
        self._xingzuo = None

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
        return {
            '忌': self._avoid,
            '宜': self._suit,
            '今日': self.today,            
            '星期': self._week,
            '农历': self._nongli,
            '公历': self._gongli,
            '生肖': self._shengxiao,
            '星座': self._xingzuo,
            '五行': self._wuxing,
            '岁次': self._suici,
            '财神方位': self._cai,
            '喜神方位': self._xi,
            '福神方位': self._fu,            
            '假日名称': self._holiday_name,
        }
    
    # 获取详细信息
    def get_details(self, _date):
        try:
            localtime = time.localtime(_date)
            
            self._week = ['一','二','三','四','五','六','日'][localtime.tm_wday]
            _a = time.strftime("%Y/%m/%Y%m%d", localtime)
            # http://www.nongli.cn/rili/api/app/god/2019/01/20190101.js
            res = requests.get('http://www.nongli.cn/rili/api/app/god/'+_a+'.js')
            r = str(res.content, encoding='utf-8')
            _r = parse('json:'+r)
            _obj = _r['html']
            self._wuxing = _obj['wuxing'].strip('"')
            # 农历
            _nongli = _obj['nongli'].strip('"').split(' ')
            self._nongli = _nongli[0]
            self._shengxiao = _nongli[1]
            # 公历
            _gongli = _obj['gongli'].strip('"').split(' ')
            self._gongli = _gongli[0]
            self._xingzuo = _gongli[1]            
            self._suici = _obj['suici'].strip('"')
            self._cai = _obj['cai'].strip('"')
            self._xi = _obj['xi'].strip('"')
            self._fu = _obj['fu'].strip('"')
            _LOGGER.info('获取当天详细信息')
        except Exception as e:
            print(e)

    # 日期格式化
    def date_format(self, _date):
        return time.mktime(time.strptime(_date,"%Y-%m-%d"))

    
    # 查询列表是否有假日
    def findHoliday(self, today, _list):
        if (len(list(filter(lambda x: x['date'] == today and x['status'] == '1', _list))) > 0):
            return True
        # 如果有状态为2的，说明这一天是双休日，但是要上班
        if (len(list(filter(lambda x: x['date'] == today and x['status'] == '2', _list))) > 0):
            return False
        return None
        
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
        # 获取宜忌
        _almanac = list(filter(lambda x: x['date'] == today, obj['almanac']))
        if len(_almanac) > 0:
            self._avoid = _almanac[0]['avoid']
            self._suit = _almanac[0]['suit']
            
        # 判断是否在我国传统假日列表里
        _list = list(filter(lambda x: x['startday'] == today, obj['holidaylist']))
        if (len(_list) > 0):
            self._holiday_name = _list[0].name
            return True
        # 判断是否在传统假日连休列表里
        if 'holiday' in obj:
            _holiday = obj['holiday']
            if isinstance(_holiday,list):
                for item in _holiday:
                    _result = self.findHoliday(today, item['list'])
                    if _result != None:
                        self._holiday_name = item['name']
                        return _result
            elif isinstance(_holiday,dict):
                _result = self.findHoliday(today, _holiday['list'])
                if _result != None:
                    self._holiday_name = _holiday['name']
                    return _result
        # 判断是否双休日
        if localtime.tm_wday == 5:
            self._holiday_name = '周六'
            return True
        if localtime.tm_wday == 6:
            self._holiday_name = '周日'
            return True
        
        return False

    async def async_update(self):
        """判断是否节假日，获取当天详细信息."""
        # if self._today != self.today:
        now = time.time()
        self.get_details(now)
        # 重置假日名称
        self._holiday_name = None
        self._state = self.is_holiday(now)            
        self._today = self.today

# --------------字符串转JSON-----------------------
def skip_ws(txt, pos):
    while pos < len(txt) and txt[pos].isspace():
        pos += 1
    return pos
 
def parse_str(txt, pos, allow_ws=False, delimiter=[',',':','}',']']):
    while pos < len(txt):
        if not allow_ws and txt[pos].isspace():
            break
        if txt[pos] in delimiter:
            break
        pos += 1
    return pos
 
def parse_obj(txt, pos):
    obj = dict()
 
    while True:
        pos = skip_ws(txt, pos+1)
        end = parse_str(txt, pos, True, [':'])
        if end >= len(txt):
            raise ValueError("unexpected end when parsing object key")
        key = txt[pos:end].strip()
        pos = skip_ws(txt, end+1)
        if pos >= len(txt):
            raise ValueError("unexpected end when parsing object value")
        if txt[pos] == '[':
            value, pos = parse_array(txt, pos)
        elif txt[pos] == '{':
            value, pos = parse_obj(txt, pos)
        else:
            end = parse_str(txt, pos, True, [',','}'])
            if end >= len(txt):
                raise ValueError("unexpected end when parsing object value")
            value = txt[pos:end].strip()
            pos = end
 
        obj[key] = value
        pos = skip_ws(txt, pos)
        if pos >= len(txt):
            raise ValueError("unexpected end when object value finish")
        if txt[pos] == '}':
            return obj, pos+1
 
def parse_array(txt, pos):
    array = list()
 
    while True:
        pos = skip_ws(txt, pos+1)
        if pos >= len(txt):
            raise ValueError("unexpected end when parsing array item")
        if txt[pos] == '[':
            value, pos = parse_array(txt, pos)
        elif txt[pos] == '{':
            value, pos = parse_obj(txt, pos)
        else:
            end = parse_str(txt, pos, True, [',',']'])
            if end >= len(txt):
                raise ValueError("unexpected end when parsing array item")
            value = txt[pos:end].strip()
            pos = end
        
        array.append(value)
        pos = skip_ws(txt, pos)
        if pos >= len(txt):
            raise ValueError("unexpected end when array item finish")
        if txt[pos] == ']':
            return array, pos+1
 
def parse(txt):
    if txt.startswith('json'):
        pos = txt.find(':')
        if pos != -1:
            pos = skip_ws(txt, pos+1)
            if txt[pos] == '{':
                obj, pos = parse_obj(txt, pos)
                return obj
            elif txt[pos] == '[':
                array, pos = parse_array(txt, pos)
                return array
    raise ValueError("format error when parsing root")