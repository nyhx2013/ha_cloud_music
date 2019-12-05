import json
import os
import logging
import voluptuous as vol
import requests
import time 
import datetime
import random
import re
import urllib.parse
import uuid
import math
import base64 

# ----------邮件相关---------- #
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))
# ----------邮件相关---------- #
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import config_validation as cv, intent
from homeassistant.helpers.event import track_time_interval
from homeassistant.components import weblink
from homeassistant.components.http import HomeAssistantView
import aiohttp
from aiohttp import web
from aiohttp.web import FileResponse
from typing import Optional
from homeassistant.helpers.state import AsyncTrackStates
from urllib.request import urlopen, quote

_LOGGER = logging.getLogger(__name__)
############## 日志记录
_DEBUG = False
def _log(*arg):
    if _DEBUG:
        _LOGGER.info(*arg)

def _log_info(*arg):
    _LOGGER.info(*arg)

###################媒体播放器##########################
from homeassistant.components.media_player import (
    MediaPlayerDevice, PLATFORM_SCHEMA)
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,MEDIA_TYPE_URL, SUPPORT_PAUSE, SUPPORT_PLAY, SUPPORT_NEXT_TRACK, SUPPORT_PREVIOUS_TRACK, SUPPORT_TURN_ON, SUPPORT_TURN_OFF,
    SUPPORT_PLAY_MEDIA, SUPPORT_STOP, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET, SUPPORT_SELECT_SOURCE, SUPPORT_CLEAR_PLAYLIST, SUPPORT_STOP, 
    SUPPORT_SELECT_SOUND_MODE, SUPPORT_SHUFFLE_SET, SUPPORT_SEEK, SUPPORT_VOLUME_STEP)
from homeassistant.const import (
    CONF_NAME, STATE_IDLE, STATE_PAUSED, STATE_PLAYING, STATE_OFF, STATE_UNAVAILABLE)
import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.helpers import discovery, device_registry as dr

SUPPORT_VLC = SUPPORT_PAUSE | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | SUPPORT_STOP | SUPPORT_SELECT_SOUND_MODE | SUPPORT_TURN_ON | SUPPORT_TURN_OFF | \
    SUPPORT_PLAY_MEDIA | SUPPORT_PLAY | SUPPORT_STOP | SUPPORT_NEXT_TRACK | SUPPORT_PREVIOUS_TRACK | SUPPORT_SELECT_SOURCE | SUPPORT_CLEAR_PLAYLIST | \
    SUPPORT_SHUFFLE_SET | SUPPORT_SEEK | SUPPORT_VOLUME_STEP

# 定时器时间
TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=1)
###################媒体播放器##########################

# 全局请求头
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
# 接口请求地址
API_URL = ""
API_KEY_LIST = {}

API_KEY = str(uuid.uuid4())


VERSION = '2.1.7'
DOMAIN = 'ha_cloud_music'

HASS = None

##### 网关控制
class HassGateView(HomeAssistantView):
    """View to handle Configuration requests."""

    url = '/' + DOMAIN + '-api'
    name = DOMAIN
    requires_auth = False

    async def get(self, request):    
        _raw_path = request.rel_url.raw_path
        # _log_info(request.rel_url)
        if _raw_path == self.url:
            # 提示地址
            _tips_location = '/'+ DOMAIN + '/' + VERSION + '/dist/tips.html?msg='
            if 'key' in request.query:
                _key = request.query['key']
                global API_KEY_LIST
                if _key in API_KEY_LIST:
                    # 如果Key超过一天，则提示过期
                    if (API_KEY_LIST[_key] - datetime.datetime.now()).seconds < 3600 * 60 * 24:
                        # 这里执行删除key的操作
                        del API_KEY_LIST[_key]
                        # 这里解析服务
                        _action = urllib.parse.unquote(request.query['action'])
                        arr = _action.split('.', 1)
                        if arr[0] == 'script':
                            await HASS.services.async_call('script', str(arr[1]))
                        elif arr[0] == 'automation':
                            await HASS.services.async_call('automation', 'trigger', {'entity_id': _action})
                        return web.HTTPFound(location= _tips_location + '执行成功&id=' + _action)
                    else:
                        return web.HTTPFound(location= _tips_location + '通信密钥已过期')
                else:
                    return web.HTTPFound(location= _tips_location + '该操作【已执行】或者【已过期】')
            #a = urllib.parse.unquote(_api)

        _path = os.path.dirname(__file__) + _raw_path.replace('/'+ DOMAIN + '/' + VERSION,'')        
        return FileResponse(_path)

    async def post(self, request):
        """Update state of entity."""
        response = await request.json()
        hass = request.app["hass"]
        
        if 'key' in response:
            # 如果密钥不一致，则提示没有权限
            if response['key'] == API_KEY:
                if 'type' in response:
                    _type = response['type'] 
                    if _type == 'web':
                        _api = response['url']
                        async with aiohttp.request('GET',API_URL + _api) as r:
                            _result = await r.json(encoding="utf-8")
                            return self.json(_result)
                    elif _type == 'text':
                        # 这里进行文本解析
                        _text = response['text']
                        # 音乐控制解析
                        if '下一曲' in _text or '下一首' in _text:
                            await hass.services.async_call('media_player', 'media_next_track', {'entity_id': 'media_player.ha_cloud_music'})
                            return self.json({'code': 0, 'msg': '执行下一曲成功'})
                        elif '上一曲' in _text or '上一首' in _text:
                            await hass.services.async_call('media_player', 'media_previous_track', {'entity_id': 'media_player.ha_cloud_music'})
                            return self.json({'code': 0, 'msg': '执行上一曲成功'})
                        elif '播放' in _text:
                            await hass.services.async_call('media_player', 'media_play', {'entity_id': 'media_player.ha_cloud_music'})
                            return self.json({'code': 0, 'msg': '执行播放成功'})
                        elif '暂停' in _text or '停止' in _text:
                            await hass.services.async_call('media_player', 'media_pause', {'entity_id': 'media_player.ha_cloud_music'})
                            return self.json({'code': 0, 'msg': '执行暂停成功'})

                        # 开关控制
                        intent_type = ''
                        if '打开' in _text or '开启' in _text or '启动' in _text :
                            intent_type = 'HassTurnOn'
                        elif '关闭' in _text or '关掉' in _text  or '关上' in _text :
                            intent_type = 'HassTurnOff'

                        try:
                            if intent_type != '':
                                # 获取要操作的名称                                
                                if '打开' in _text:
                                    _name = _text.split('打开')[1]
                                elif '开启' in _text:
                                    _name = _text.split('开启')[1]
                                elif '启动' in _text:
                                    _name = _text.split('启动')[1]
                                elif '关闭' in _text:
                                    _name = _text.split('关闭')[1]
                                elif '关掉' in _text:
                                    _name = _text.split('关掉')[1]
                                elif '关上' in _text:
                                    _name = _text.split('关上')[1]

                                intent_response = await intent.async_handle(hass, DOMAIN, intent_type, {'name': {'value': _name}})
                                _log_info(intent_response.intent)
                                _log_info(intent_response.speech)
                                _log_info(intent_response.card)
                                return self.json({'code':0, 'data': intent_response.speech, 'type': 'intent'})
                            else:
                                # 调用自定义的意图                                
                                if hass.services.has_service('conversation','process'):
                                    _log_info("调用自定义的意图")
                                    await hass.services.async_call('conversation', 'process', {'text': _text})
                                    return self.json({'code': 0, 'msg': '调用自定义的意图成功'})
                                else:
                                    return self.json({'code': 0, 'msg': '对不起，没有开启自定义意图'})

                        except intent.UnknownIntent as err:
                            _LOGGER.warning('接收到未知的意图 %s', intent_type)
                        except intent.InvalidSlotInfo as err:
                            _LOGGER.error('接收到无效的插槽数据: %s', err)
                        except intent.IntentError as err:
                            _LOGGER.exception('处理请求时出错 %s', intent_type)
                            return self.json({'code': 1, 'msg': '处理请求时出错，您可能没有这个设备'})

            else:
                return self.json({"code": 401})
        return self.json(response)

        
##### 安装平台
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional("sidebar_title", default="云音乐"): cv.string,
    vol.Optional("sidebar_icon", default="mdi:music"): cv.string,
    # 网易云音乐用户ID
    vol.Optional("uid", default=""): cv.string,
    # 显示模式 全屏：fullscreen
    vol.Optional("show_mode", default="default"): cv.string,
    # 网易云音乐接口地址
    vol.Required("api_url"): cv.string,
    vol.Optional("api_key", default=''): cv.string,
    # TTS相关配置
    vol.Optional("tts_before_message", default=""): cv.string,
    vol.Optional("tts_after_message", default=""): cv.string,
    # QQ邮箱相关配置（密码为QQ邮箱授权码【不是QQ密码】）
    vol.Optional("mail_qq", default=""): cv.string,
    vol.Optional("mail_code", default=""): cv.string,
    vol.Optional("base_url", default=""): cv.string,
    # 启用百度地图
    vol.Optional("map_ak", default=""): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the vlc platform."""
  
    global HASS
    HASS = hass
    # 注册静态目录
    local = hass.config.path("custom_components/ha_cloud_music")
    if os.path.isdir(local):
        hass.http.register_static_path('/'+ DOMAIN + '/' + VERSION, local, False)
    
    hass.http.register_view(HassGateView)
    mp = MediaPlayer(hass)
    add_entities([mp])
    
    
    # 设置API地址
    global API_URL
    API_URL = config.get("api_url")

    # 验证api_key是否设置为uuid格式（为了安全，必须要这么做）
    _api_key = config.get("api_key")
    global API_KEY
    if _api_key != '' and re.match('\w{8}(-\w{4}){3}-\w{12}', _api_key):
        _log_info('使用自定义api_key：' + _api_key)
        API_KEY = _api_key

    # 判断是否支持VLC
    supported_vlc_tips = '不支持'
    _is_vlc = '0'
    if mp.supported_vlc == True:
        _is_vlc = '1'
        supported_vlc_tips = '支持'
 
    _sidebar_title = config.get("sidebar_title")
    _sidebar_icon = config.get("sidebar_icon")
    _show_mode = config.get("show_mode")
    _uid = config.get("uid")
    _map_ak = config.get("map_ak")
    mp.tts_config['before_message'] = config.get("tts_before_message")
    mp.tts_config['after_message'] = config.get("tts_after_message")
    mp.mail['qq'] = config.get("mail_qq")
    mp.mail['code'] = config.get("mail_code")
    mp.base_url = config.get("base_url")
    
    _show_mode_str = "正常模式"
    if _show_mode == 'fullscreen':
        _show_mode_str = "全屏模式"
    
    _LOGGER.info('''
-------------------------------------------------------------------
    ha_cloud_music云音乐插件【作者QQ：635147515】
    
    版本：''' + VERSION + '''    
    
    介绍：这是一个网易云音乐的HomeAssistant播放器插件
    
    项目地址：https://github.com/shaonianzhentan/ha_cloud_music
    
    配置信息：
    
        API_URL：''' + API_URL + '''            
        
        API_KEY：''' + API_KEY + '''
        
        内置VLC播放器：''' + supported_vlc_tips + '''
        
        侧边栏名称：''' + _sidebar_title + '''
        
        侧边栏图标：''' + _sidebar_icon + '''
        
        显示模式：''' + _show_mode_str + '''
        
        用户ID：''' + _uid + '''

-------------------------------------------------------------------''')      

    # 注册服务【加载歌单】
    hass.services.register(DOMAIN, 'load', mp.load_songlist)
    # 注册服务【设置播放模式】
    hass.services.register(DOMAIN, 'play_mode', mp.play_mode)
    # 注册服务【tts】
    if mp.supported_vlc == True:
        hass.services.register(DOMAIN, 'tts', mp.tts)
    # 注册服务【notify】
    if mp.mail['qq'] != '' and mp.mail['code'] != '':
        hass.services.register(DOMAIN, 'notify', mp.notify)

    # 添加状态卡片
    hass.components.frontend.add_extra_js_url(hass, '/'+ DOMAIN + '/' + VERSION + '/dist/data/more-info-ha_cloud_music.js')
    hass.components.frontend.add_extra_js_url(hass, '/'+ DOMAIN + '/' + VERSION + '/dist/data/more-info-ha_cloud_music-kodi.js')    
    # 添加到侧边栏
    coroutine = hass.components.frontend.async_register_built_in_panel(
        "iframe",
        _sidebar_title,
        _sidebar_icon,
        DOMAIN,
        {"url": "/" + DOMAIN+"/" + VERSION + "/dist/index.html?ver=" + VERSION 
        + "&show_mode=" + _show_mode
        + "&api_key=" + API_KEY
        + "&ak=" + _map_ak
        + "&uid=" + _uid
        + "&vlc=" + _is_vlc},
        require_admin=True,
    )
    try:
        if coroutine != None:
            coroutine.send(None)
    except StopIteration:
        pass

    # 添加百度地图
    if _map_ak != '':
        hass.components.frontend.add_extra_js_url(hass, '/'+ DOMAIN + '/' + VERSION + '/dist/data/ha-panel-baidu-map.js')
        hass.components.frontend.async_register_built_in_panel(
            "baidu-map",
            "百度地图",
            "mdi:map-marker-radius",
            frontend_url_path=None,
            config={"ak": _map_ak},
            require_admin=True,
        )

    # 添加语音服务
    if mp.base_url != '':
        _plaintext = '{"host": "' + mp.base_url.strip('/') + '", "key": "' + API_KEY + '"}'
        encodestr = base64.b64encode(_plaintext.encode('utf-8'))
        _encryption = str(encodestr,'utf-8')
        #_log_info('加密信息')
        #_log_info(_encryption)
        weblink.setup(hass,{'weblink': {
                'entities': [{'name': '云音乐语音服务', 'url': 'https://api.jiluxinqing.com/ha/voice.html?key=' + _encryption, 'icon': 'mdi:microphone'}]
            }
        })
    return True   
    
###################媒体播放器##########################
class MediaPlayer(MediaPlayerDevice):
    """Representation of a vlc player."""

    def __init__(self, hass):
        """Initialize the vlc device."""
        self._hass = hass
        self.music_playlist = None
        self.music_index = 0
        self._name = DOMAIN
        self._media_image_url = None
        self._media_title = None
        self._media_name = None
        self._media_artist = None
        self._media_album_name = None
        self._volume = None
        self._state = STATE_IDLE
        self._source_list = None
        self._source = None
        self._sound_mode_list = None
        self._sound_mode = None
        # 播放模式（0：列表循环，1：顺序播放，2：随机播放，3：单曲循环）
        self._play_mode = 0
        self._media_playlist = None
        self._media_position_updated_at = None
        self._media_position = 0
        self._media_duration = None
        # 错误计数
        self.error_count = 0
        self.loading = False
        # 定时器操作计数
        self.next_count = 0
        # 判断是否支持VLC
        self._supported_vlc = None
        self._media = None
        # 是否启用定时器
        self._timer_enable = True
        # 定时器
        track_time_interval(hass, self.interval, TIME_BETWEEN_UPDATES)
        self.base_url = None
        #### TTS 相关配置 ####
        self.tts_config = {
            'vlc': None,
            'play_state': None,
            'before_message': '',
            'after_message': '',
        }
        #### 邮箱 相关配置 ####
        self.mail = {
            'qq': '',
            'code': ''
        }
    
    def interval(self, now):
        # 如果当前状态是播放，则进度累加（虽然我定时的是1秒，但不知道为啥2秒执行一次）
        if self._media != None:
            # 走内置播放器的逻辑
            if self._sound_mode == "内置VLC播放器":
                
                if self._timer_enable == True:
                    # 如果内置播放器状态为off，说明播放结束了
                    if (self._source_list != None and len(self._source_list) > 0 
                        and self._media.state == STATE_OFF
                        and self.next_count > 0):
                        self.media_end_next()
                    # 计数器累加
                    self.next_count += 1
                    if self.next_count > 100:
                        self.next_count = 100

                # 获取当前进度
                self._media_position = int(self._media.attributes['media_position'])
            else:
                _log('当前时间：%s，当前进度：%s,总进度：%s', self._media_position_updated_at, self._media_position, self.media_duration)
                _log('源播放器状态 %s，云音乐状态：%s', self._media.state, self._state)
                
                  # 没有进度的，下一曲判断逻辑
                if self._timer_enable == True:
                    # 如果进度条结束了，则执行下一曲
                    # 执行下一曲之后，15秒内不能再次执行操作
                    if (self._source_list != None 
                        and len(self._source_list) > 0
                        and self.media_duration > 3 
                        and self.next_count > 0):
                        # MPD的下一曲逻辑
                        if self.player_type == "mpd":
                            _isEnd = self.media_duration - self.media_position <= 3
                            if _isEnd == True:
                                self.next_count = -15
                                # 先停止再播放
                                self._hass.services.call('media_player', 'media_stop', {"entity_id": self._sound_mode}, True)
                                _log_info('MPD播放器更新 下一曲')
                                self.media_end_next()
                        else:
                              # 如果当前总进度 - 当前进度 小于 11，则下一曲 （十一是下一次更新的时间）
                            _isEnd = self.media_duration - self.media_position <= 11
                            # 如果进度结束，则下一曲
                            if _isEnd == True:
                                self.next_count = -15
                                _log_info('播放器更新 下一曲')
                                self.media_end_next()
                    # 计数器累加
                    self.next_count += 1
                    if self.next_count > 100:
                        self.next_count = 100
                    
                    self.update()
                
                # 如果存在进度，则取源进度
                if 'media_position' in self._media.attributes:
                    # 判断是否为kodi播放器
                    if self.player_type == "kodi":
                        self._hass.services.call('homeassistant', 'update_entity', {"entity_id": self._sound_mode})
                        if 'media_position' in self._media.attributes:
                            self._media_position = int(self._media.attributes['media_position']) + 5
                    else:
                        self._media_position = int(self._media.attributes['media_position'])
                # 如果当前是播放状态，则进行进度累加。。。
                elif self._state == STATE_PLAYING and self._media_position_updated_at != None:
                    _media_position = self._media_position
                    _today = (now - self._media_position_updated_at)
                    _seconds = _today.seconds + _today.microseconds / 1000000.0
                    _log('当前相差的秒：%s', _seconds)
                    self._media_position += _seconds
            
            # 更新当前播放进度时间
            self._media_position_updated_at = now
            
    def update(self):        
        """Get the latest details from the device."""
        if self._sound_mode == None:
            self.init_sound_mode()            
            return False
        # 如果播放器列表有变化，则更新
        self.update_sound_mode_list() 
        
        # 使用内置VLC
        if self._sound_mode == "内置VLC播放器":
            self.init_vlc_player()            
        else:
            self.release_vlc_player()
            # 获取源播放器
            self._media = self._hass.states.get(self._sound_mode)
            # 如果状态不一样，则更新源播放器
            if self._state != self._media.state:
                self._hass.services.call('homeassistant', 'update_entity', {"entity_id": self._sound_mode})
                self._hass.services.call('homeassistant', 'update_entity', {"entity_id": 'media_player.'+DOMAIN})
        
        self._media_duration = self.media_duration
        self._state = self._media.state
            
        return True

    @property
    def state_attributes(self):
        """Return the state attributes."""
        attr = super().state_attributes
        attr.update({'custom_ui_more_info': 'more-info-ha_cloud_music'})
        return attr

    # 判断当前关联的播放器类型
    @property
    def player_type(self):
        if self._media != None:
            attr = self._media.attributes
            if 'supported_features' in attr:
                supported_features = attr['supported_features']
                if supported_features == 54847:
                    return "kodi"
                elif ('media_position' not in attr or 'media_duration' not in attr):
                    # 如果没有进度or没有总进度，则判断为mpd
                    return "mpd"
                
    # 判断是否内置播放器
    @property
    def is_vlc(self):
        return self._sound_mode == "内置VLC播放器"
                
    @property
    def name(self):
        """Return the name of the device."""
        return self._name
    
    @property
    def registry_name(self):
        """返回实体的friendly_name属性."""
        return '网易云音乐'
    
    @property
    def app_id(self):
        """ID of the current running app."""
        return self._name

    @property
    def app_name(self):
        """Name of the current running app."""
        return '网易云音乐'
    
    @property
    def media_image_url(self):
        """当前播放的音乐封面地址."""
        if self._media_image_url != None:            
            return self._media_image_url + "?param=500y500"
        return self._media_image_url
        
    @property
    def media_image_remotely_accessible(self) -> bool:
        """图片远程访问"""
        return True
    
    @property
    def source_list(self):
        """Return the name of the device."""
        return self._source_list   

    @property
    def source(self):
        """Return the name of the device."""
        return self._source       
        
    @property
    def sound_mode_list(self):
        """Return the name of the device."""
        return self._sound_mode_list

    @property
    def sound_mode(self):
        """Return the name of the device."""
        return self._sound_mode
    
    @property
    def media_album_name(self):
        """专辑名称."""
        return self._media_album_name
    
    @property
    def media_playlist(self):
        """当前播放列表"""
        return self._media_playlist
    
    @property
    def media_title(self):
        """歌曲名称."""
        return self._media_title
        
    @property
    def media_artist(self):
        """歌手"""
        return self._media_artist
        
    @property
    def state(self):
        """Return the state of the device."""
        # 如果状态是关，则显示idle
        if self._state == STATE_OFF or self._state == STATE_UNAVAILABLE:
            return STATE_IDLE

        return self._state

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        if self._media == None:
            return None
        
        if 'volume_level' in self._media.attributes:
            return self._media.attributes['volume_level']
            
        return 1

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        if self._media == None:
            return None
        
        if 'is_volume_muted' in self._media.attributes:
            return self._media.attributes['is_volume_muted']
            
        return False

    @property
    def shuffle(self):
        """随机播放开关."""
        return self._play_mode == 2

    @property
    def media_season(self):
        """播放模式（没有找到属性，所以使用这个）"""
        if self._play_mode == 1:
            return '顺序播放'
        elif self._play_mode == 2:
            return '随机播放'
        elif self._play_mode == 3:
            return '单曲循环'
        else:
            return '列表循环'
        
    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_VLC

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MEDIA_TYPE_MUSIC

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        if self._media == None:
            return None
        
        attr = self._media.attributes
        if 'media_duration' in attr:
            return int(attr['media_duration'])
        # 如果当前歌曲没有总长度，也没有进度，则取当前列表里的
        if ('media_duration' not in attr and 'media_position' not in attr 
            and self.music_playlist != None and len(self.music_playlist) > 0 and self.music_index >= 0):
            music_info = self.music_playlist[self.music_index]
            return int(music_info['duration'])
        
        return 0

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        if self._media == None:
            return None
            
        return self._media_position
		
    @property
    def media_position_updated_at(self):
        """When was the position of the current playing media valid."""
        if self._media == None:
            return None
        
        if 'media_position_updated_at' in self._media.attributes:
            return self._media.attributes['media_position_updated_at']
            
        return self._media_position_updated_at
        
    def set_shuffle(self, shuffle):
        """禁用/启用 随机模式."""
        if shuffle:
            self._play_mode = 2
        else:
            self._play_mode = 0

    def media_seek(self, position):
        """将媒体设置到特定位置."""
        _log_info('设置播放位置：%s', position)
        self.call('media_seek', {"position": position})        

    def mute_volume(self, mute):
        """静音."""
        self.call('volume_mute', {"is_volume_muted": mute})

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""        
        _log_info('设置音量：%s', volume)
        self.call('volume_set', {"volume": volume})

    def media_play(self):
        """Send play command."""
        self.call('media_play')
        self._state = STATE_PLAYING

    def media_pause(self):
        """Send pause command."""
        self.call('media_pause')
        self._state = STATE_PAUSED

    def media_stop(self):
        """Send stop command."""
        self.call('media_stop')
        self._state = STATE_IDLE
		
    def play_media(self, media_type, media_id, **kwargs):
        """Play media from a URL or file."""        
        #_log('类型：%s', media_type)                
        if media_type == MEDIA_TYPE_MUSIC:
            self._timer_enable = False
            url = media_id
        elif media_type == 'music_load':                    
            self.music_index = int(media_id)
            music_info = self.music_playlist[self.music_index]
            url = self.get_url(music_info)
        elif media_type == MEDIA_TYPE_URL:
            _log('加载播放列表链接：%s', media_id)
            res = requests.get(media_id)
            play_list = res.json()
            self._media_playlist = play_list
            self.music_playlist = play_list
            music_info = self.music_playlist[0]
            url = self.get_url(music_info)
            #数据源
            source_list = []
            for index in range(len(self.music_playlist)):
                music_info = self.music_playlist[index]
                source_list.append(str(index + 1) + '.' + music_info['song'] + ' - ' + music_info['singer'])
            self._source_list = source_list
            #初始化源播放器
            self.media_stop()
            _log('绑定数据源：%s', self._source_list)
        elif media_type == 'music_playlist':
            _log('初始化播放列表')
            
            # 如果是list类型，则进行操作
            if isinstance(media_id, list):            
                self._media_playlist = json.dumps(media_id)
                self.music_playlist = media_id                
            else:
                dict = json.loads(media_id)    
                self._media_playlist = dict['list']
                self.music_playlist = json.loads(self._media_playlist)
                self.music_index = dict['index']
                
            music_info = self.music_playlist[self.music_index]
            url = self.get_url(music_info)
            #数据源
            source_list = []
            for index in range(len(self.music_playlist)):
                music_info = self.music_playlist[index]
                source_list.append(str(index + 1) + '.' + music_info['song'] + ' - ' + music_info['singer'])
            self._source_list = source_list
            #初始化源播放器
            self.media_stop()
        else:
            _LOGGER.error(
                "不受支持的媒体类型 %s",media_type)
            return
        _log_info('title：%s ，play url：%s' , self._media_name, url)
        
        # 默认为music类型，如果指定视频，则替换
        play_type = "music"
        try:
            if 'media_type' in music_info and music_info['media_type'] == 'video':
                play_type = "video"
            # 如果没有url则下一曲（如果超过3个错误，则停止）
            # 如果是云音乐播放列表 并且格式不是mp3，则下一曲
            elif url == None or (media_type == 'music_load' and url.find(".mp3") < 0):
               self.notification("没有找到【" + self._media_name + "】的播放链接，自动为您跳到下一首", "load_song_url")
               self.error_count = self.error_count + 1
               if self.error_count < 3:
                 self.media_next_track()
               return
            else:
                self.notification("正在播放【" + self._media_name + "】", "load_song_url")
        except Exception as e:
            print('这是一个正常的错误：', e)
        # 重置错误计数
        self.error_count = 0
        # 重置播放进度
        self._media_position = 0
        self._media_position_updated_at = None
        #播放音乐
        self.call('play_media', {"url": url,"type": play_type})


    # 音乐结束自动下一曲
    def media_end_next(self):        
        playlist_count = len(self.music_playlist) - 1
        # 如果是顺序播放，最后一曲，则暂停
        if self._play_mode == 1 and self.music_index >= playlist_count:
            return
        # 如果是单曲循环，则索引往前移一位
        if self._play_mode == 3:
            self.music_index = self.music_index - 1
        # 如果启用了随机模式，则每次都生成随机值
        elif self._play_mode == 2:
           # 这里的索引会在下一曲后加一
           self.music_index = random.randint(0, playlist_count)           

        self.media_next_track()

    def media_next_track(self):
        self.music_index = self.music_index + 1
        _log('下一曲：%s', self.music_index)
        self.next_count = -15        
        self.music_load()

    def media_previous_track(self):
        self.music_index = self.music_index - 1
        _log('上一曲：%s', self.music_index)
        self.music_load()
    
    def select_source(self, source):
        _log('选择源：%s', source)
        #选择播放
        self._state = STATE_IDLE
        self.music_index = self._source_list.index(source)
        self.play_media('music_load', self.music_index)
        
    def select_sound_mode(self, sound_mode):        
        self._sound_mode = sound_mode
        self._state = STATE_IDLE
        self.save_sound_mode()
        _log('选择声音模式：%s', sound_mode)
    
    def clear_playlist(self):
        _log('清除播放列表')
        self.music_playlist = None
        self.music_index = 0
        self._media_title = None
        self._media_name = None
        self._source_list = None
        self._media_album_name = None
        self._source = None
        self._shuffle = False
        self._media_image_url = None
        self._media_artist = None
        self._media_playlist = None
        self._media_position_updated_at = None
        self._media_position = 0
        self._media_duration = None                
        self.media_stop()

    # 关闭播放器
    def turn_off(self):
        self.clear_playlist()
    
    def notification(self, message, type):
        self._hass.services.call('persistent_notification', 'create', {"message": message, "title": "云音乐", "notification_id": "ha-cloud-music-" + type})
    
    # 更新播放器列表
    def update_sound_mode_list(self):
        entity_list = self._hass.states.entity_ids('media_player')
        if len(entity_list) != len(self._sound_mode_list):
            self.init_sound_mode()
        
    # 保存当前选择的播放器
    def save_sound_mode(self):
        filename = os.path.dirname(__file__) + '/sound_mode.json'
        entity_value = {'state': self._sound_mode}
        with open(filename, 'w') as f_obj:
            json.dump(entity_value, f_obj)
    
    # 读取当前保存的播放器
    def init_sound_mode(self):
        filename = os.path.dirname(__file__) + '/sound_mode.json'
        sound_mode = None
        if os.path.exists(filename) == True:
            with open(filename, 'r') as f_obj:
                entity = json.load(f_obj)
                sound_mode = entity['state']
                
        # 过滤云音乐
        entity_list = self._hass.states.entity_ids('media_player')
        filter_list = filter(lambda x: x.count('media_player.' + DOMAIN) == 0, entity_list)
        _list = list(filter_list)
        if self.supported_vlc == True:
            _list.insert(0, "内置VLC播放器")
        
        self._sound_mode_list = _list
        
        # 如果保存的是【内置VLC播放器】，则直接加载
        if sound_mode == "内置VLC播放器":
           self._sound_mode = "内置VLC播放器"
           self.init_vlc_player()
           return        
        
        if len(self._sound_mode_list) > 0:
            # 判断存储的值是否为空
            if sound_mode != None and self._sound_mode_list.count(sound_mode) == 1:
                self._sound_mode = sound_mode
            elif self.supported_vlc == True:
                self._sound_mode = "内置VLC播放器"
                self.init_vlc_player()
            else:
                self._sound_mode = self._sound_mode_list[0]
        elif self.supported_vlc == True:
            self._sound_mode = "内置VLC播放器"
            self.init_vlc_player()
        #_log(self._sound_mode_list)
       
    def get_url(self, music_info):
        self._media_name = music_info['song'] + ' - ' + music_info['singer']
        self._source = str(self.music_index + 1) + '.' + self._media_name
        # 歌名
        self._media_title = music_info['song']
        # 歌手
        self._media_artist = music_info['singer']
        # 设置图片
        if 'image' in music_info:
            self._media_image_url = music_info['image']
        # 设置专辑名称
        if 'album' in music_info:
            self._media_album_name = music_info['album']
        
        # 如果有传入类型，则根据类型处理
        if 'type' in music_info:
            if music_info['type'] == 'url':
                # 如果传入的是能直接播放的音频
                return music_info['url']
            elif music_info['type'] == 'djradio':
                # 如果传入的是网易电台
                res = requests.get(API_URL + "/song/url?id=" + str(music_info['id']))
                obj = res.json()
                url = obj['data'][0]['url']
                return url
        
        url = get_redirect_url(music_info['url'])
        # 如果没有url，则去咪咕搜索
        if url == None:
            return migu_search(music_info['song'], music_info['singer'])
        return url
    
    def call(self, action, info = None):
        dict = {"entity_id": self._sound_mode}
        if info != None:
            if 'url' in info:
                dict['media_content_id'] = info['url']
            if 'type' in info:
                dict['media_content_type'] = info['type']
            if 'volume' in info:
                dict['volume_level'] = info['volume']
            if 'position' in info:
                dict['seek_position'] = info['position']
                # 如果是MPD，则直接赋值
                if self.player_type == "mpd":
                    self._media_position = info['position']
            if 'is_volume_muted' in info:
                dict['is_volume_muted'] = info['is_volume_muted']
                
        #调用服务
        _log('调用服务：%s', action)
        _log(dict)
                
        if self._sound_mode == "内置VLC播放器":
            if action == "play_media":
                self._media.load(info['url'])
            elif action == "media_pause":
                self._media.pause()
            elif action == "media_play":
                self._media.play()
            elif action == "volume_set":
                self._media.volume_set(info['volume'])
            elif action == "media_seek":
                self._media.seek(info['position'])
            elif action == "volume_mute":
                self._media.mute_volume(info['is_volume_muted'])
                
            # 执行完操作之后，强制更新当前播放器
            if action != "play_media":
                self._hass.services.call('homeassistant', 'update_entity', {"entity_id": 'media_player.'+DOMAIN})
        else:
            self._hass.services.call('media_player', action, dict)
            self._hass.services.call('homeassistant', 'update_entity', {"entity_id": self._sound_mode})
            self._hass.services.call('homeassistant', 'update_entity', {"entity_id": 'media_player.'+DOMAIN})
                    
    def music_load(self):
        if self.music_playlist == None:
           _log('结束播放，没有播放列表')
           return
        self._timer_enable = True
        playlist_count = len(self.music_playlist)
        if self.music_index >= playlist_count:
           self.music_index = 0
        elif self.music_index < 0:
           self.music_index = playlist_count - 1
        self.play_media('music_load', self.music_index)
    
    
    ######### 服务 ##############
    # 邮件通知
    def notify(self, call):
        _title = call.data['title']
        _message = call.data['message']
        # 执行命令
        if 'action' in call.data:
            _key = str(uuid.uuid4())
            if self.base_url != '':
                global API_KEY_LIST
                for item in API_KEY_LIST:
                    # 如果当前key大于24小时，则删除
                    if (API_KEY_LIST[item] - datetime.datetime.now()).seconds > 3600 * 60 * 24:
                        del API_KEY_LIST[item]
                # 把这个通知的key加入到字典中
                API_KEY_LIST.update({_key: datetime.datetime.now()})
                _message = _message + '<br/><br/><a href="' + self.base_url.strip('/') + '/'+ DOMAIN + '-api?key=' + _key + '&action=' +  call.data['action'] + '" style="background:#03a9f4;color:white;padding:15px 0;text-decoration:none;display:block;text-align:center;">执行命令</a>' 
            else:
                self.notification('【' + _title + '】没有配置base_url参数','mail')

        _user = self.mail['qq']
        # 如果没有后缀，则加上
        if '@qq.com' not in _user:
            _user = _user + '@qq.com'
        
        from_addr = _user
        password = self.mail['code']
        to_addr = _user
        smtp_server = 'smtp.qq.com'
        msg = MIMEText(_message, 'html', 'utf-8')
        msg['From'] = _format_addr('HomeAssistant <%s>' % from_addr)
        msg['To'] = _format_addr('智能家居 <%s>' % to_addr)
        msg['Subject'] = Header(_title, 'utf-8').encode()
        try:
            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()
            self.notification('【' + _title + '】邮件通知发送成功','mail')
        except Exception as e:
            self.notification('【' + _title + '】邮件通知发送失败','mail')

    # 设置播放模式
    def play_mode(self, call):
        _mode = call.data['mode']
        mode_list = [0, 1, 2, 3]
        if mode_list.count(_mode) == 0:
            _mode = 0
        self._play_mode = _mode
        _mode_name = "列表循环"
        if self._play_mode == 1:
            _mode_name = "顺序播放"
        elif self._play_mode == 2:
            _mode_name = "随机播放"
        elif self._play_mode == 3:
            _mode_name = "单曲循环"
        _log_info('设置播放模式：%s', _mode_name)

    # 加载播放列表
    def load_songlist(self, call): 
        list_index = 0
        # 如果传入了id和type，则按最新的服务逻辑来操作
        if 'id' in call.data and 'type' in call.data:
            _id = call.data['id']
            if call.data['type'] == 'playlist':
                _type = "playlist"
            elif call.data['type'] == 'djradio':
                _type = "djradio"
            elif call.data['type'] == 'ximalaya':
                _type = "ximalaya"
            else:
                self.notification("加载播放列表：type参数错误", "load_songlist")
                return "type参数错误"
        elif 'id' in call.data:
            _id = call.data['id']
            _type = "playlist"
        elif 'rid' in call.data:
            _id = call.data['rid']
            _type = "djradio"
        
        # 兼容旧的格式
        if 'list_index' in call.data:
            list_index = int(call.data['list_index']) - 1
        # 新的参数
        if 'index' in call.data:
            list_index = int(call.data['index']) - 1
        if self.loading == True:
            self.notification("正在加载歌单，请勿重复调用服务", "load_songlist")
            return
        self.loading = True

        try:
            if _type == "playlist":
                _log_info("加载歌单列表，ID：%s", _id)
                # 获取播放列表
                res = requests.get(API_URL + '/playlist/detail?id=' + str(_id))
                obj = res.json()
                if obj['code'] == 200:
                    _list = obj['playlist']['tracks']
                    _newlist = map(lambda item: {
                        "id": int(item['id']),
                        "name": item['name'],
                        "album": item['al']['name'],
                        "image": item['al']['picUrl'],
                        "duration": int(item['dt']) / 1000,
                        "url": "https://music.163.com/song/media/outer/url?id=" + str(item['id']),
                        "song": item['name'],
                        "singer": len(item['ar']) > 0 and item['ar'][0]['name'] or '未知'
                        }, _list)            
                    #_log_info(_result)
                    if list_index < 0 or list_index >= len(_list):
                        list_index = 0                      
                    self.music_index = list_index
                    self.play_media('music_playlist', list(_newlist))
                    self.notification("正在播放歌单【"+obj['playlist']['name']+"】", "load_songlist")
                else:
                    # 这里弹出提示
                    self.notification("没有找到id为【"+_id+"】的歌单信息", "load_songlist")
            elif _type == "djradio":
                _log_info("加载电台列表，ID：%s", _id)
                # 获取播放列表
                offset = 0
                if list_index >= 50:
                   offset = math.floor((list_index + 1) / 50)
                # 取余
                list_index = list_index % 50
                _list = djradio_playlist(_id, offset, 50)
                if len(_list) > 0:
                    self.music_index = list_index
                    self.play_media('music_playlist', _list)
                    self.notification("正在播放专辑【" + _list[0]['album'] + "】", "load_songlist")
                else:
                    self.notification("没有找到id为【"+_id+"】的电台信息", "load_songlist")
            elif _type == 'ximalaya':
                _log_info("加载喜马拉雅专辑列表，ID：%s", _id)
                # 取余
                list_index = list_index % 50
                
                _list = ximalaya_playlist(_id, list_index + 1, 50)    
                if len(_list) > 0:
                    self.music_index = list_index
                    self.play_media('music_playlist', _list)
                    self.notification("正在播放专辑【" + _list[0]['album'] + "】", "load_songlist")
                else:
                    self.notification("没有找到id为【"+_id+"】的专辑信息", "load_songlist")
                    
        except Exception as e:
            print(e)
            self.notification("加载歌单的时候出现了异常", "load_songlist")
        finally:
            # 这里重置    
            self.loading = False
    
    ######################内置VLC播放器相关方法################################
    @property
    def supported_vlc(self):
        """判断是否支持vlc模块."""
        if self._supported_vlc != None:
            return self._supported_vlc

        try:
            # 执行引入vlc操作，如果报错，则不支持vlc
            import vlc
            instance = vlc.Instance()
            instance.media_player_new()
            instance.release()
            self._supported_vlc = True
            return True
        except Exception as e:
            self._supported_vlc = False
            return False
    
    # 初始化内置VLC播放器
    def init_vlc_player(self):
        try:
            if self._media == None or hasattr(self._media, 'ha_cloud_music') == False:
                self._media = VlcPlayer()
        except Exception as e:
            print("【初始化内置VLC播放器】出现错误", e)            

    # 释放vlc对象
    def release_vlc_player(self):        
        if self._media != None and hasattr(self._media, 'ha_cloud_music') == True:
            self._media._vlc.release()
            self._media._instance.release()
    
    ######################文字转语音################################
    # 时间转换
    def tts_time_format(self, num):
        if num < 10:
            return '0' + str(num)
        return str(num)

    # 文字转语音
    def tts(self, call):
        # 获取message参数
        message = call.data['message']
        # 如当前正在播放音乐，则先暂停        
        if self._state == STATE_PLAYING:
            self.tts_config['play_state'] = True
            self.media_pause()
        # 特殊符号替换成时间
        localtime = time.localtime(time.time())

        message = self.tts_config['before_message'] \
            + message.replace('%Y', str(localtime.tm_year))\
                .replace('%m', str(localtime.tm_mon))\
                .replace('%d', str(localtime.tm_mday))\
                .replace('%HH', self.tts_time_format(localtime.tm_hour))\
                .replace('%H', str(localtime.tm_hour))\
                .replace('%MM', self.tts_time_format(localtime.tm_min))\
                .replace('%M', str(localtime.tm_min))\
                .replace('%S', str(localtime.tm_sec)) \
            + self.tts_config['after_message']
        _log_info('文字转语音：%s', message)
        # 开始播放语音
        import vlc
        instance = vlc.Instance()
        _vlc = instance.media_player_new()        
        _event_manager = _vlc.event_manager()
        _event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.tts_end)
        _vlc.set_media(instance.media_new("https://api.jiluxinqing.com/api/service/tts?text="+ quote(message)))
        _vlc.play()
        self.tts_config['vlc'] = instance

    # 播放结束  
    def tts_end(self, event):
        if self.tts_config['play_state'] == True:
            self.media_play()
        self.tts_config['play_state'] = False
        self.tts_config['vlc'].release()
            
###################媒体播放器##########################


###################内置VLC播放器##########################
class VlcPlayer():
    def __init__(self): 
        import vlc
        self.vlc = vlc
        self._instance = vlc.Instance()
        self._vlc = self._instance.media_player_new()
        self.state = STATE_IDLE
        self.attributes = {
            "volume_level": 1,
            "is_volume_muted": False,
            "media_duration": 0,
            "media_position_updated_at": None,
            "media_position": 0,
        }        
        self.ha_cloud_music = True
        self._event_manager = self._vlc.event_manager()
        self._event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.end)
        self._event_manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.update)
    
    def end(self, event):
        self.state = STATE_OFF
        
    def update(self, event):
        try:
            status = self._vlc.get_state()
            if status == self.vlc.State.Playing:
                self.state = STATE_PLAYING
            elif status == self.vlc.State.Paused:
                self.state = STATE_PAUSED
            else:
                self.state = STATE_IDLE
            
            media_duration = self._vlc.get_length() / 1000
            self.attributes['media_duration'] = media_duration
            self.attributes['media_position'] = self._vlc.get_position() * media_duration
            self.attributes['media_position_updated_at'] = datetime.datetime.now()
            self.attributes['volume_level'] = self._vlc.audio_get_volume() / 100
            self.attributes['is_volume_muted'] = (self._vlc.audio_get_mute() == 1)
            
            #_log_info(self.attributes)
        except Exception as e:
            print(e)

    def load(self, url):
        self._vlc.set_media(self._instance.media_new(url))
        self._vlc.play()
        self.state = STATE_PLAYING
                
    def play(self):
        if self._vlc.is_playing() == False:
            self._vlc.play()
        self.state = STATE_PLAYING
    
    def pause(self):
        if self._vlc.is_playing() == True:
            self._vlc.pause()
        self.state = STATE_PAUSED
    
    def volume_set(self, volume_level):
        self.attributes['volume_level'] = volume_level
        self._vlc.audio_set_volume(int(volume_level * 100))
    
    # 设置位置
    def seek(self, position):
        self.attributes['media_position'] = position
        track_length = self._vlc.get_length()/1000
        self._vlc.set_position(position/track_length)
    
    # 静音
    def mute_volume(self, mute):
        self.attributes['is_volume_muted'] = mute
        self._vlc.audio_set_mute(mute)

# 获取重写向后的地址
def get_redirect_url(url):
    # 请求网页
    response = requests.get(url, headers=HEADERS)
    result_url = response.url
    if result_url == 'https://music.163.com/404':
        return None
    return result_url

# 进行咪咕搜索，可以播放周杰伦的歌歌
def migu_search(songName, singerName):
    try:
        # 如果含有特殊字符，则直接使用名称搜索
        searchObj = re.search(r'\(|（|：|:《', songName, re.M|re.I)
        if searchObj:
            keywords = songName
        else:    
            keywords = songName + ' - '+ singerName
        _log_info("开始在咪咕搜索：%s", keywords)
        response = requests.get("http://m.music.migu.cn/migu/remoting/scr_search_tag?rows=10&type=2&keyword=" + keywords + "&pgc=1", headers=HEADERS)
        res = response.json()
        
        if 'musics' in res and len(res['musics']) > 0 and (songName in res['musics'][0]['songName'] or searchObj):
            return res['musics'][0]['mp3']
    except Exception as e:
        print("在咪咕搜索时出现错误：", e)
    return None

# 网易电台
def djradio_playlist(id, offset, size):
    res = requests.get(API_URL + '/dj/program?rid='+str(id)+'&limit=50&offset='+str(offset * size))
    obj = res.json()
    if obj['code'] == 200:
        _list = obj['programs']
        _newlist = map(lambda item: {
            "id": int(item['mainSong']['id']),
            "name": item['name'],
            "album": item['dj']['brand'],
            "image": item['coverUrl'],
            "duration": int(item['mainSong']['duration']) / 1000,
            "song": item['name'],
            "type": "djradio",
            "singer": item['dj']['nickname']
            }, _list)            
        return list(_newlist)
    else:
        return []
        
# 喜马拉雅播放列表
def ximalaya_playlist(id, index, size):
    res = requests.get('https://mobile.ximalaya.com/mobile/v1/album/track?albumId=' + str(id) + '&device=android&isAsc=true&pageId='\
        + str(index) + '&pageSize=' + str(size) +'&statEvent=pageview%2Falbum%40203355&statModule=%E6%9C%80%E5%A4%9A%E6%94%B6%E8%97%8F%E6%A6%9C&statPage=ranklist%40%E6%9C%80%E5%A4%9A%E6%94%B6%E8%97%8F%E6%A6%9C&statPosition=8')
    obj = res.json()
    if obj['ret'] == 0:
        _list = obj['data']['list']
        if len(_list) > 0:
            # 获取专辑名称
            _res = requests.get('http://mobile.ximalaya.com/v1/track/baseInfo?device=android&trackId='+str(_list[0]['trackId']))
            _obj = _res.json()
            # 格式化列表
            _newlist = map(lambda item: {
                "id": item['trackId'],
                "name": item['title'],
                "album": _obj['albumTitle'],
                "image": item['coverLarge'],
                "duration": item['duration'],
                "song": item['title'],
                "type": "url",
                "url": item['playUrl64'],
                "singer": item['nickname']
                }, _list)
            return list(_newlist)
    return []