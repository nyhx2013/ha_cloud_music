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
import asyncio

################### 接口定义 ###################
# 常量
from .api_const import DOMAIN, VERSION, ROOT_PATH, TrueOrFalse, write_config_file, read_config_file
# 网易云接口
from .api_music import ApiMusic
# 网关视图
from .api_view import ApiView
# 媒体接口
from .api_media import ApiMedia
# 语音接口
from .api_voice import ApiVoice
# TTS接口
from .api_tts import ApiTTS
################### 接口定义 ###################
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import config_validation as cv, intent
from homeassistant.helpers.event import track_time_interval, async_call_later
from homeassistant.components.weblink import Link
from homeassistant.components.http import HomeAssistantView
import aiohttp
from aiohttp import web
from aiohttp.web import FileResponse
from typing import Optional
from homeassistant.helpers.state import AsyncTrackStates
from urllib.request import urlopen, quote
from homeassistant.core import Event
from homeassistant.components.media_player import (
    MediaPlayerDevice)
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,MEDIA_TYPE_URL, SUPPORT_PAUSE, SUPPORT_PLAY, SUPPORT_NEXT_TRACK, SUPPORT_PREVIOUS_TRACK, SUPPORT_TURN_ON, SUPPORT_TURN_OFF,
    SUPPORT_PLAY_MEDIA, SUPPORT_STOP, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET, SUPPORT_SELECT_SOURCE, SUPPORT_CLEAR_PLAYLIST, SUPPORT_STOP, 
    SUPPORT_SELECT_SOUND_MODE, SUPPORT_SHUFFLE_SET, SUPPORT_SEEK, SUPPORT_VOLUME_STEP)
from homeassistant.const import (
    CONF_NAME, STATE_IDLE, STATE_PAUSED, STATE_PLAYING, STATE_OFF, STATE_UNAVAILABLE, EVENT_HOMEASSISTANT_STOP)
import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.helpers import discovery, device_registry as dr

_LOGGER = logging.getLogger(__name__)
###################媒体播放器##########################

SUPPORT_VLC = SUPPORT_PAUSE | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | SUPPORT_STOP | SUPPORT_SELECT_SOUND_MODE | SUPPORT_TURN_ON | SUPPORT_TURN_OFF | \
    SUPPORT_PLAY_MEDIA | SUPPORT_PLAY | SUPPORT_STOP | SUPPORT_NEXT_TRACK | SUPPORT_PREVIOUS_TRACK | SUPPORT_SELECT_SOURCE | SUPPORT_CLEAR_PLAYLIST | \
    SUPPORT_SHUFFLE_SET | SUPPORT_SEEK | SUPPORT_VOLUME_STEP

# 定时器时间
TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=1)
###################媒体播放器##########################




def setup_platform(hass, config, add_entities, discovery_info=None):

    ################### 系统配置 ###################

    # 名称与图标
    sidebar_title = config.get("sidebar_title", "云音乐")
    sidebar_icon = config.get("sidebar_icon","mdi:music")
    # 网易云音乐用户ID
    uid = str(config.get("uid", ''))
    # 用户名和密码
    user = str(config.get("user", ''))
    password = str(config.get("password", ''))
    # 显示模式 全屏：fullscreen
    show_mode = config.get("show_mode", "default")
    # 网易云音乐接口地址
    api_url = str(config.get("api_url", '')).strip('/')
    # TTS相关配置
    tts_before_message = config.get("tts_before_message", '')
    tts_after_message = config.get("tts_after_message", '')
    tts_mode = config.get("tts_mode", 4)

    #### （启用/禁用）配置 #### 

    # 是否开启语音文字处理程序（默认启用）
    is_voice = config.get('is_voice', True)
    # 是否启用通知（默认启用）
    is_notify = config.get('is_notify', True)
    # 是否调试模式（默认启用）
    is_debug = config.get('is_debug', True)

    # 检测配置
    if api_url == '':
        _LOGGER.error("检测到未配置api_url参数！")
        return
    ################### 系统配置 ###################

    ################### 定义实体类 ###################
    # 播放器实例
    mp = MediaPlayer(hass)    
    mp.api_media = ApiMedia(mp, {
        # 是否通知
        'is_notify': is_notify,
        # 是否调试
        'is_debug': is_debug,
        '_LOGGER': _LOGGER
    })
    mp.api_tts = ApiTTS(mp,{
        'tts_before_message': tts_before_message,
        'tts_after_message': tts_after_message,
        'tts_mode': tts_mode
    })    
    mp.api_music = ApiMusic(mp, {
        'api_url': api_url, 
        'uid': uid, 
        'user': user, 
        'password': password
    })
    # 开始登录
    mp.api_music.login()
    hass.data[DOMAIN] = mp
    # 添加实体
    add_entities([mp])

    ################### 定义实体类 ###################

    ################### 注册静态目录与接口网关 ###################    
    local = hass.config.path("custom_components/ha_cloud_music/dist")
    if os.path.isdir(local):
        # 注册静态目录
        hass.http.register_static_path(ROOT_PATH, local, False)
        # 注册网关接口
        hass.http.register_view(ApiView)
        # 添加状态卡片
        hass.components.frontend.add_extra_js_url(hass, ROOT_PATH + '/data/more-info-ha_cloud_music.js')
        # 注册菜单栏
        hass.components.frontend.async_register_built_in_panel(
            "iframe",
            sidebar_title,
            sidebar_icon,
            DOMAIN,
            {"url": ROOT_PATH + "/index.html?ver=" + VERSION 
            + "&show_mode=" + show_mode
            + "&uid=" + mp.api_music.uid},
            require_admin=True
        )
    ################### 注册静态目录与接口网关 ###################

    ################### 注册服务 ################### 
    # 注册服务【加载歌单】
    hass.services.register(DOMAIN, 'load', mp.load_songlist)

    # 注册服务【配置】
    hass.services.register(DOMAIN, 'config', mp.config)

    # 注册服务【tts】
    hass.services.register(DOMAIN, 'tts', mp.api_tts.speak)
    hass.services.register(DOMAIN, 'tts_clear', mp.api_tts.clear)

    # 监听语音小助手的文本
    if is_voice == True:
        _ApiVoice = ApiVoice(hass, mp.api_music)
        hass.bus.listen('ha_voice_text_event', _ApiVoice.text_event)

    ################### 注册服务 ################### 

    # 显示插件信息
    _LOGGER.info('''
-------------------------------------------------------------------
    ha_cloud_music云音乐插件【作者QQ：635147515】
    
    版本：''' + VERSION + '''    
    
    介绍：这是一个网易云音乐的HomeAssistant播放器插件
    
    项目地址：https://github.com/shaonianzhentan/ha_cloud_music
    
    配置信息：
    
        API_URL：''' + api_url + '''
        
        内置VLC播放器：''' + TrueOrFalse(mp.api_media.supported_vlc, '支持', '不支持') + '''
        
        侧边栏名称：''' + sidebar_title + '''
        
        侧边栏图标：''' + sidebar_icon + '''
        
        显示模式：''' + TrueOrFalse(show_mode == 'fullscreen', '全局模式', '默认模式') + '''
        
        用户ID：''' + mp.api_music.uid + '''

-------------------------------------------------------------------''')
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
        self._media_url = None
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
        self._media = None
        # 是否启用定时器
        self._timer_enable = True
        self._notify = True
        # 定时器
        track_time_interval(hass, self.interval, TIME_BETWEEN_UPDATES)
        # 读取配置文件
        music_playlist = read_config_file('music_playlist.cfg')
        if music_playlist != None:
            self._media_playlist = json.dumps(music_playlist)
            self.music_playlist = music_playlist
        
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
                        self.next_count = -15
                        self.media_end_next()
                    # 计数器累加
                    self.next_count += 1
                    if self.next_count > 100:
                        self.next_count = 100

                # 获取当前进度
                self._media_position = int(self._media.attributes['media_position'])
            else:
                self.api_media.debug('当前时间：%s，当前进度：%s,总进度：%s', self._media_position_updated_at, self._media_position, self.media_duration)
                self.api_media.debug('源播放器状态 %s，云音乐状态：%s', self._media.state, self._state)
                
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
                                self.api_media.log('MPD播放器更新 下一曲')
                                self.media_end_next()
                        else:
                              # 如果当前总进度 - 当前进度 小于 11，则下一曲 （十一是下一次更新的时间）
                            _isEnd = self.media_duration - self.media_position <= 11
                            # 如果进度结束，则下一曲
                            if _isEnd == True:
                                self.next_count = -15
                                self.api_media.log('播放器更新 下一曲')
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
                    self.api_media.debug('当前相差的秒：%s', _seconds)
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
            self.api_media.init_vlc_player()            
        else:
            self.api_media.release_vlc_player()
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
        self.api_media.log('【设置播放位置】：%s', position)
        self.call('media_seek', {"position": position})        

    def mute_volume(self, mute):
        """静音."""
        self.call('volume_mute', {"is_volume_muted": mute})

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        self.api_media.log('【设置音量】：%s', volume)
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
        self.api_media.log('【播放列表类型】：%s', media_type)
        if media_type == MEDIA_TYPE_MUSIC:
            self._timer_enable = False
            url = media_id
        elif media_type == 'music_load':                    
            self.music_index = int(media_id)
            music_info = self.music_playlist[self.music_index]
            url = self.get_url(music_info)
        elif media_type == MEDIA_TYPE_URL:
            self.api_media.log('加载播放列表链接：%s', media_id)
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
            self.api_media.log('绑定数据源：%s', self._source_list)
        elif media_type == 'music_playlist':
            self.api_media.log('初始化播放列表')
            
            # 如果是list类型，则进行操作
            if isinstance(media_id, list):            
                self._media_playlist = json.dumps(media_id)
                self.music_playlist = media_id
            else:
                dict = json.loads(media_id)    
                self._media_playlist = dict['list']
                self.music_playlist = json.loads(self._media_playlist)
                self.music_index = dict['index']
            
            # 保存音乐播放列表到本地
            write_config_file('music_playlist.cfg', self.music_playlist)
            
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
            # 防止进行自动下一曲的操作
            self.next_count = -15
            self._timer_enable = True
        else:
            _LOGGER.error(
                "不受支持的媒体类型 %s",media_type)
            return
        self.api_media.log('【当前播放音乐】【%s】:【%s】' , self._media_name, url)
        
        # 默认为music类型，如果指定视频，则替换
        play_type = "music"
        try:
            if 'media_type' in music_info and music_info['media_type'] == 'video':
                play_type = "video"
            # 如果没有url则下一曲（如果超过3个错误，则停止）
            # 如果是云音乐播放列表 并且格式不是mp3不是m4a，则下一曲
            elif url == None or (media_type == 'music_load' and url.find(".mp3") < 0 and url.find('.m4a') < 0):
               self.api_media.notification("没有找到【" + self._media_name + "】的播放链接，自动为您跳到下一首", "load_song_url")
               self.error_count = self.error_count + 1
               if self.error_count < 3:
                 self.media_next_track()
               return
            else:
                self.api_media.notification("正在播放【" + self._media_name + "】", "load_song_url")
        except Exception as e:
            print('这是一个正常的错误：', e)
        # 重置错误计数
        self.error_count = 0
        # 重置播放进度
        self._media_position = 0
        self._media_position_updated_at = None
        #播放音乐
        self._media_url = url
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
        self.api_media.log('【下一曲】：%s', self.music_index)
        self.next_count = -15
        self.music_load()

    def media_previous_track(self):
        self.music_index = self.music_index - 1
        self.api_media.log('【上一曲】：%s', self.music_index)
        self.music_load()
    
    def select_source(self, source):
        self.api_media.log('【选择音乐】：%s', source)
        #选择播放
        self._state = STATE_IDLE
        self.music_index = self._source_list.index(source)
        self.play_media('music_load', self.music_index)
        
    def select_sound_mode(self, sound_mode):        
        self._sound_mode = sound_mode
        self._state = STATE_IDLE        
        write_config_file('sound_mode.json', {'state': self._sound_mode})
        self.api_media.log('【选择源播放器】：%s', sound_mode)
    
    def clear_playlist(self):
        self.api_media.log('【重置播放器】')
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
    
    # 更新播放器列表
    def update_sound_mode_list(self):
        entity_list = self._hass.states.entity_ids('media_player')
        if len(entity_list) != len(self._sound_mode_list):
            self.init_sound_mode()
    
    # 读取当前保存的播放器
    def init_sound_mode(self):
        sound_mode = None
        res =  read_config_file('sound_mode.json')
        if res is not None:
            sound_mode = res['state']

        # 过滤云音乐
        entity_list = self._hass.states.entity_ids('media_player')
        filter_list = filter(lambda x: x.count('media_player.' + DOMAIN) == 0, entity_list)
        _list = list(filter_list)
        if self.api_media.supported_vlc == True:
            _list.insert(0, "内置VLC播放器")
        
        self._sound_mode_list = _list
        
        # 如果保存的是【内置VLC播放器】，则直接加载
        if sound_mode == "内置VLC播放器":
           self._sound_mode = "内置VLC播放器"
           self.api_media.init_vlc_player()
           return        
        
        if len(self._sound_mode_list) > 0:
            # 判断存储的值是否为空
            if sound_mode != None and self._sound_mode_list.count(sound_mode) == 1:
                self._sound_mode = sound_mode
            elif self.api_media.supported_vlc == True:
                self._sound_mode = "内置VLC播放器"
                self.api_media.init_vlc_player()
            else:
                self._sound_mode = self._sound_mode_list[0]
        elif self.api_media.supported_vlc == True:
            self._sound_mode = "内置VLC播放器"
            self.api_media.init_vlc_player()
        #self.api_media.log(self._sound_mode_list)
       
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
            elif music_info['type'] == 'djradio' or music_info['type'] == 'cloud':                
                # 如果传入的是网易电台
                return self.api_music.get_song_url(music_info['id'])
        
        url = self.api_music.get_redirect_url(music_info['url'])
        # 如果没有url，则去咪咕搜索
        if url == None:
            return self.api_music.migu_search(music_info['song'], music_info['singer'])
        return url
    
    def call(self, action, info = None):
        _dict = {"entity_id": self._sound_mode}
        if info != None:
            if 'url' in info:
                _dict['media_content_id'] = info['url']
            if 'type' in info:
                _dict['media_content_type'] = info['type']
            if 'volume' in info:
                _dict['volume_level'] = info['volume']
            if 'position' in info:
                _dict['seek_position'] = info['position']
                # 如果是MPD，则直接赋值
                if self.player_type == "mpd":
                    self._media_position = info['position']
            if 'is_volume_muted' in info:
                _dict['is_volume_muted'] = info['is_volume_muted']
                
        #调用服务
        self.api_media.log('【调用服务[' + str(self._sound_mode) + ']】%s：%s', action, _dict)
                
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
            self._hass.services.call('media_player', action, _dict)
            self._hass.services.call('homeassistant', 'update_entity', {"entity_id": self._sound_mode})
            self._hass.services.call('homeassistant', 'update_entity', {"entity_id": 'media_player.'+DOMAIN})
                    
    def music_load(self):
        if self.music_playlist == None:
           self.api_media.log('【结束播放，没有播放列表】')
           return
        self._timer_enable = True
        playlist_count = len(self.music_playlist)
        if self.music_index >= playlist_count:
           self.music_index = 0
        elif self.music_index < 0:
           self.music_index = playlist_count - 1
        self.play_media('music_load', self.music_index)
    
    
    # 设置播放模式
    def set_play_mode(self, _mode):
        mode_names = ['列表循环', '顺序播放', '随机播放', '单曲循环']
        mode_list = [0, 1, 2, 3]
        if mode_list.count(_mode) == 0:
            _mode = 0
        self._play_mode = _mode
        self.api_media.log('【设置播放模式】：%s', mode_names[_mode])

    ######### 服务 ##############
    def config(self, call):
        _obj = call.data
        # 设置播放模式
        if 'play_mode' in _obj:
            self.set_play_mode(_obj['play_mode'])
        # （禁用/启用）通知
        if 'is_notify' in _obj:
            self.api_media.is_notify = bool(_obj['is_notify'])
        # （禁用/启用）日志
        if 'is_debug' in _obj:
            self.api_media.is_debug = bool(_obj['is_debug'])

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
                self.api_media.notification("加载播放列表：type参数错误", "load_songlist")
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
            self.api_media.notification("正在加载歌单，请勿重复调用服务", "load_songlist")
            return
        self.loading = True

        try:
            if _type == "playlist":
                self.api_media.log("【加载歌单列表】，ID：%s", _id)
                # 获取播放列表
                obj = self.api_music.music_playlist(_id)      
                if obj != None and len(obj['list']) > 0:
                    _newlist = obj['list']
                    if list_index < 0 or list_index >= len(_newlist):
                        list_index = 0
                    self.music_index = list_index
                    self.play_media('music_playlist', _newlist)
                    self.api_media.notification("正在播放歌单【"+obj['name']+"】", "load_songlist")
                else:
                    # 这里弹出提示
                    self.api_media.notification("没有找到id为【"+_id+"】的歌单信息", "load_songlist")
            elif _type == "djradio":
                self.api_media.log("【加载电台列表】，ID：%s", _id)
                # 获取播放列表
                offset = 0
                if list_index >= 50:
                   offset = math.floor((list_index + 1) / 50)
                # 取余
                list_index = list_index % 50
                _list = self.api_music.djradio_playlist(_id, offset, 50)
                if len(_list) > 0:
                    self.music_index = list_index
                    self.play_media('music_playlist', _list)
                    self.api_media.notification("正在播放专辑【" + _list[0]['album'] + "】", "load_songlist")
                else:
                    self.api_media.notification("没有找到id为【"+_id+"】的电台信息", "load_songlist")
            elif _type == 'ximalaya':
                self.api_media.log("【加载喜马拉雅专辑列表】，ID：%s", _id)
                # 播放第几条音乐
                music_index = list_index % 50
                # 获取第几页
                list_index =  math.floor(list_index / 50) + 1
                _list = self.api_music.ximalaya_playlist(_id, list_index, 50)
                if len(_list) > 0:
                    self.music_index = music_index
                    self.play_media('music_playlist', _list)
                    self.api_media.notification("正在播放专辑【" + _list[0]['album'] + "】", "load_songlist")
                else:
                    self.api_media.notification("没有找到id为【"+_id+"】的专辑信息", "load_songlist")
                    
        except Exception as e:
            self.api_media.log(e)
            self.api_media.notification("加载歌单的时候出现了异常", "load_songlist")
        finally:
            # 这里重置    
            self.loading = False
                    
###################媒体播放器##########################