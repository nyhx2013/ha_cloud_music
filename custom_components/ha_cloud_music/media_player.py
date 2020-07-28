import json, os, logging, time, datetime, random, re, uuid, math, base64, asyncio, aiohttp
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,MEDIA_TYPE_URL, SUPPORT_PAUSE, SUPPORT_PLAY, 
    SUPPORT_NEXT_TRACK, SUPPORT_PREVIOUS_TRACK, SUPPORT_TURN_ON, SUPPORT_TURN_OFF, SUPPORT_STOP,
    SUPPORT_PLAY_MEDIA, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET, SUPPORT_SELECT_SOURCE, SUPPORT_CLEAR_PLAYLIST, 
    SUPPORT_SELECT_SOUND_MODE, SUPPORT_SEEK, SUPPORT_VOLUME_STEP)
from homeassistant.const import (STATE_IDLE, STATE_PAUSED, STATE_PLAYING, STATE_OFF, STATE_UNAVAILABLE)

SUPPORT_FEATURES = SUPPORT_PAUSE | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | SUPPORT_SELECT_SOUND_MODE | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_PLAY_MEDIA | SUPPORT_PLAY | SUPPORT_NEXT_TRACK | \
    SUPPORT_PREVIOUS_TRACK | SUPPORT_SELECT_SOURCE | SUPPORT_CLEAR_PLAYLIST | SUPPORT_SEEK | SUPPORT_VOLUME_STEP

_LOGGER = logging.getLogger(__name__)
################### 接口定义 ###################
# 常量
from .api_config import DOMAIN, VERSION, ROOT_PATH, TrueOrFalse, write_config_file, read_config_file
# 网易云接口
from .api_music import ApiMusic
# 网关视图
from .api_view import ApiView
# 语音接口
from .api_voice import ApiVoice
# TTS接口
from .api_tts import ApiTTS
# 播放器
from .source_web import MediaPlayerWEB
from .source_vlc import MediaPlayerVLC
from .source_mpd import MediaPlayerMPD

def setup_platform(hass, config, add_entities, discovery_info=None):

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

    # 检测配置
    if api_url == '':
        _LOGGER.error("检测到未配置api_url参数！")
        return
    ################### 系统配置 ###################

    ################### 定义实体类 ###################
    # 播放器实例
    mp = MediaPlayer(hass, config)
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
    hass.async_create_task(mp.api_music.login())
    
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
        # 添加状态卡片
        hass.components.frontend.add_extra_js_url(hass, ROOT_PATH + '/data/more-info-ha_cloud_music.js')
    ################### 注册静态目录与接口网关 ###################

    ################### 注册服务 ################### 
    # 注册服务【加载歌单】
    hass.services.register(DOMAIN, 'load', mp.load_songlist)

    # 注册服务【点歌】
    hass.services.register(DOMAIN, 'pick', mp.pick_song)

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
                
        侧边栏名称：''' + sidebar_title + '''
        
        侧边栏图标：''' + sidebar_icon + '''
        
        显示模式：''' + TrueOrFalse(show_mode == 'fullscreen', '全局模式', '默认模式') + '''
        
        用户ID：''' + mp.api_music.uid + '''

-------------------------------------------------------------------''')
    return True   
    
###################媒体播放器##########################
class MediaPlayer(MediaPlayerEntity):

    def __init__(self, hass, config):
        self._config = config

        self._hass = hass
        self.music_playlist = None
        self.music_index = 0
        self.media_url = None
        self._media_image_url = None
        self._media_title = None
        self._media_name = ''
        self._media_artist = None
        self._media_album_name = None
        # 媒体播放器
        self._media_player = None
        self._volume = None
        self._source_list = None
        self._source = None
        # 播放模式（0：列表循环，1：顺序播放，2：随机播放，3：单曲循环）
        self._play_mode = 0
        self._media_position_updated_at = None
        self._media_position = 0
        self._media_duration = None
        
        # 错误计数
        self.error_count = 0
        self.loading = False
        # 是否启用定时器
        self._timer_enable = True
        self._notify = True

        _sound_mode_list = ['网页播放器']
        # 如果是Docker环境，则不显示VLC播放器
        if os.path.isfile("/.dockerenv") == True and config['mpd_host'] is not None:
            _sound_mode_list.append('MPD播放器')
        else:
            _sound_mode_list.append('VLC播放器')
        self._sound_mode_list = _sound_mode_list
        self._sound_mode = None
        # 读取播放器配置
        res =  read_config_file('sound_mode.json')
        if res is not None:
            self.select_sound_mode(res['state'])

        # 读取音乐列表
        music_playlist = read_config_file('music_playlist.json')
        if music_playlist != None:
            self.music_playlist = music_playlist
            source_list = []
            for index in range(len(self.music_playlist)):
                music_info = self.music_playlist[index]
                source_list.append(str(index + 1) + '.' + music_info['song'] + ' - ' + music_info['singer'])
            self._source_list = source_list

    def update(self):
        # 数据更新
        return True

    @property
    def name(self):
        # 设备的名称
        return "云音乐"

    @property
    def supported_features(self):
        return SUPPORT_FEATURES

    @property
    def media_content_type(self):
        return MEDIA_TYPE_MUSIC

    @property
    def state_attributes(self):
        # 当前媒体状态属性
        attr = super().state_attributes
        play_mode_list = ['列表循环','顺序播放','随机播放','单曲循环']
        attr.update({'custom_ui_more_info': 'more-info-ha_cloud_music', 
            'custom_ui_state_card': 'more-info-state-ha_cloud_music', 
            'tts_volume': self.api_tts.tts_volume,
            'tts_mode': self.api_tts.tts_mode,
            'play_mode': play_mode_list[self._play_mode]})
        return attr

    @property
    def media_image_url(self):
        # 当前播放的音乐封面地址.
        if self._media_image_url != None:            
            return self._media_image_url + "?param=500y500"
        return self._media_image_url
        
    @property
    def media_image_remotely_accessible(self) -> bool:
        # 图片远程访问
        return True
    
    @property
    def source_list(self):
        # 音乐列表 
        return self._source_list   

    @property
    def source(self):
        # 当前播放音乐
        return self._source       
        
    @property
    def sound_mode_list(self):
        # 播放器列表
        return self._sound_mode_list

    @property
    def sound_mode(self):
        # 当前播放器
        return self._sound_mode
    
    @property
    def media_album_name(self):
        """专辑名称."""
        return self._media_album_name
    
    @property
    def media_playlist(self):
        """当前播放列表"""
        return self.music_playlist
    
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
        # 返回当前播放器状态
        if self._media_player == None:
            return STATE_IDLE
        if self._media_player.state == 'playing':
            return STATE_PLAYING
        elif self._media_player.state == 'paused':
            return STATE_PAUSED

    @property
    def volume_level(self):
        if self._media_player == None:
            return None
        return self._media_player.volume_level

    @property
    def is_volume_muted(self):
        if self._media_player == None:
            return None
        return self._media_player._muted

    @property
    def media_duration(self):
        if self._media_player == None:
            return None
        return self._media_player.media_duration


    @property
    def media_position(self):
        if self._media_player == None:
            return None
        return self._media_player.media_position
		
    @property
    def media_position_updated_at(self):
        if self._media_player == None:
            return None
        return self._media_player.media_position_updated_at

    def turn_off(self):
        print("关闭设备")
        if self._media_player == None:
            return None
        self._media_player.is_on = False

    def turn_on(self):
        print("打开设备")
        if self._media_player == None:
            return None
        self._media_player.is_on = True

    def media_seek(self, position):
        """将媒体设置到特定位置."""
        if self._media_player == None:
            return None
        self.log('【设置播放位置】：%s', position)
        self._media_player.seek(position)
        self.update_entity()

    def mute_volume(self, mute):
        """静音."""
        if self._media_player == None:
            return None
        self._media_player.mute_volume(mute)
        self.update_entity()

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        if self._media_player == None:
            return None
        self.log('【设置音量】：%s', volume)
        self._media_player.set_volume_level(volume)
        self.update_entity()

    def media_play(self):
        """Send play command."""
        if self._media_player == None:
            return None
        self._media_player.play()
        self.update_entity()

    def media_pause(self):
        """Send pause command."""
        if self._media_player == None:
            return None
        self._media_player.pause()
        self.update_entity()

    def media_stop(self):
        """Send stop command."""
        if self._media_player == None:
            return None
        self._media_player.pause()
		
    async def play_media(self, media_type, media_id, **kwargs):
        # 播放媒体URL文件
        self.log('【播放列表类型】：%s', media_type)
        if media_type == MEDIA_TYPE_MUSIC:
            url = media_id
        elif media_type == 'music_load':                    
            self.music_index = int(media_id)
            music_info = self.music_playlist[self.music_index]            
            url = await self.get_url(music_info)
        elif media_type == MEDIA_TYPE_URL:
            self.log('加载播放列表链接：%s', media_id)
            play_list = await self.api_music.proxy_get(media_id)
            self.music_playlist = play_list
            music_info = self.music_playlist[0]
            url = await self.get_url(music_info)
            #数据源
            source_list = []
            for index in range(len(self.music_playlist)):
                music_info = self.music_playlist[index]
                source_list.append(str(index + 1) + '.' + music_info['song'] + ' - ' + music_info['singer'])
            self._source_list = source_list
            self.log('绑定数据源：%s', self._source_list)
        elif media_type == 'music_playlist':
            self.log('初始化播放列表')
            # 如果是list类型，则进行操作
            if isinstance(media_id, list):
                self.music_playlist = media_id
            else:
                dict = json.loads(media_id)
                self.music_playlist = json.loads(dict['list'])
                self.music_index = dict['index']
            
            # 保存音乐播放列表到本地
            write_config_file('music_playlist.json', self.music_playlist)
            
            music_info = self.music_playlist[self.music_index]
            url = await self.get_url(music_info)
            #数据源
            source_list = []
            for index in range(len(self.music_playlist)):
                music_info = self.music_playlist[index]
                source_list.append(str(index + 1) + '.' + music_info['song'] + ' - ' + music_info['singer'])
            self._source_list = source_list
        else:
            _LOGGER.error(
                "不受支持的媒体类型 %s",media_type)
            return
        self.log('【当前播放音乐】【%s】:【%s】'%(self._media_name, url))

        try:
            # 如果没有url则下一曲（如果超过3个错误，则停止）
            # 如果是云音乐播放列表 并且格式不是mp3不是m4a，则下一曲
            if url == None or (media_type == 'music_load' and url.find(".mp3") < 0 and url.find('.m4a') < 0):
               self.notify("没有找到【" + self._media_name + "】的播放链接，自动为您跳到下一首", "load_song_url")
               self.error_count = self.error_count + 1
               if self.error_count < 3:
                 self.media_next_track()
               return
            else:
                self.notify("正在播放【" + self._media_name + "】", "load_song_url")
        except Exception as e:
            print('这是一个正常的错误：', e)

        # 加载音乐
        if self._media_player is None:
            self.notify("请重新选择源播放器", "play_media")
        else:
            self.media_url = url
            self._media_player.load(url)

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
        # 下一曲
        self.music_index = self.music_index + 1
        self.log('【下一曲】：%s', self.music_index)
        self.music_load()

    def media_previous_track(self):
        # 上一曲
        self.music_index = self.music_index - 1
        self.log('【上一曲】：%s', self.music_index)
        self.music_load()
    
    def select_source(self, source):
        # 选择音乐
        self.log('【选择音乐】：%s', source)
        self.music_index = self._source_list.index(source)
        self.music_load()
        self.update_entity()
        
    def select_sound_mode(self, sound_mode):
        print(sound_mode)
        # 相同不做处理
        if self._sound_mode == sound_mode:
            return None
        
        # 选择播放器
        if self._media_player is not None:
            try:
                self._media_player.stop()
                time.sleep(1)
            except Exception as ex:
                print(ex)
                self._media_player = None
                self.notify(self._sound_mode + "连接异常", "select_sound_mode")

        if sound_mode == '网页播放器':
            self._media_player = MediaPlayerWEB(self._config, self)
        elif sound_mode == 'MPD播放器':
            # 判断是否配置mpd_host
            if 'mpd_host' not in self._config:
                self.notify("MPD播放器需要配置mpd_host", "select_sound_mode")
                self._media_player = None
            self._media_player = MediaPlayerMPD(self._config, self)
            if self._media_player.is_support == False:
                self.notify("不支持MPD播放器，请确定是否正确配置", "select_sound_mode")
                self._media_player = None
        elif sound_mode == 'VLC播放器':
            self._media_player = MediaPlayerVLC(self._config, self)
            if self._media_player.is_support == False:
                self.notify("当前系统不支持VLC播放器", "select_sound_mode")
                self._media_player = None
        else:
            self._media_player = None

        if self._media_player is not None:
            self._sound_mode = sound_mode
            write_config_file('sound_mode.json', {'state': self._sound_mode})

            self.log('【选择源播放器】：%s', sound_mode)

    ###################  自定义方法  ##########################

    async def get_url(self, music_info):
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
                url = await self.api_music.get_song_url(music_info['id'])
                return url
        
        url = await self.api_music.get_redirect_url(music_info['url'])
        # 如果没有url，则去咪咕搜索
        if url == None:
            url = await self.api_music.migu_search(music_info['song'], music_info['singer'])
        return url
                            
    def music_load(self):
        if self.music_playlist == None:
           self.log('【结束播放，没有播放列表】')
           return
        playlist_count = len(self.music_playlist)
        if self.music_index >= playlist_count:
           self.music_index = 0
        elif self.music_index < 0:
           self.music_index = playlist_count - 1
        self._hass.async_create_task(self.play_media('music_load', self.music_index))

    # 设置播放模式
    def set_play_mode(self, _mode):
        mode_names = ['列表循环', '顺序播放', '随机播放', '单曲循环']
        mode_list = [0, 1, 2, 3]
        if mode_list.count(_mode) == 0:
            _mode = 0
        self._play_mode = _mode
        self.log('【设置播放模式】：%s', mode_names[_mode])

    ######### 服务 ##############
    def config(self, call):
        _obj = call.data
        self.log('【调用内置服务】 %s', _obj)
        # 设置播放模式
        if 'play_mode' in _obj:
            self.set_play_mode(_obj['play_mode'])
        # 设置TTS声音模式
        if 'tts_mode' in _obj:
            mode_list = [1, 2, 3, 4]
            _mode = _obj['tts_mode']
            if mode_list.count(_mode) == 0:
                _mode = 4
            self.api_tts.tts_mode = _mode
            self.notify('设置TTS声音模式：' + str(_mode), 'config')
        # 设置TTS音量
        if 'tts_volume' in _obj:
            tts_volume = int(_obj['tts_volume'])
            if 1 <= tts_volume <= 100:
                self.api_tts.tts_volume = tts_volume
                self.notify('设置TTS音量到' + str(tts_volume), 'config')
        # （禁用/启用）通知
        if 'is_notify' in _obj:
            is_notify = bool(_obj['is_notify'])
            _str = TrueOrFalse(is_notify, '启用通知', '禁用通知')
            # 如果没有启用通知，则现在启用
            if self.is_notify == False:
                self.is_notify = True
            self.notify(_str, 'config')
            self.is_notify = is_notify
        
        self.update_entity()

    # 加载播放列表
    async def load_songlist(self, call): 
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
                self.notify("加载播放列表：type参数错误", "load_songlist")
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
            self.notify("正在加载歌单，请勿重复调用服务", "load_songlist")
            return
        self.loading = True

        try:
            if _type == "playlist":
                self.log("【加载歌单列表】，ID：%s", _id)
                # 获取播放列表
                obj = await self.api_music.music_playlist(_id)      
                if obj != None and len(obj['list']) > 0:
                    _newlist = obj['list']
                    if list_index < 0 or list_index >= len(_newlist):
                        list_index = 0
                    self.music_index = list_index
                    await self.play_media('music_playlist', _newlist)
                    self.notify("正在播放歌单【"+obj['name']+"】", "load_songlist")
                else:
                    # 这里弹出提示
                    self.notify("没有找到id为【"+_id+"】的歌单信息", "load_songlist")
            elif _type == "djradio":
                self.log("【加载电台列表】，ID：%s", _id)
                # 获取播放列表
                offset = 0
                if list_index >= 50:
                   offset = math.floor((list_index + 1) / 50)
                # 取余
                list_index = list_index % 50
                _list = await self.api_music.djradio_playlist(_id, offset, 50)
                if len(_list) > 0:
                    self.music_index = list_index
                    await self.play_media('music_playlist', _list)
                    self.notify("正在播放专辑【" + _list[0]['album'] + "】", "load_songlist")
                else:
                    self.notify("没有找到id为【"+_id+"】的电台信息", "load_songlist")
            elif _type == 'ximalaya':
                self.log("【加载喜马拉雅专辑列表】，ID：%s", _id)
                # 播放第几条音乐
                music_index = list_index % 50
                # 获取第几页
                list_index =  math.floor(list_index / 50) + 1
                _list = await self.api_music.ximalaya_playlist(_id, list_index, 50)
                if len(_list) > 0:
                    self.music_index = music_index
                    await self.play_media('music_playlist', _list)
                    self.notify("正在播放专辑【" + _list[0]['album'] + "】", "load_songlist")
                else:
                    self.notify("没有找到id为【"+_id+"】的专辑信息", "load_songlist")
                    
        except Exception as e:
            self.log(e)
            self.notify("加载歌单的时候出现了异常", "load_songlist")
        finally:
            # 这里重置    
            self.loading = False

    # 单曲点歌
    async def pick_song(self, call): 
        if 'name' in call.data:
            _name = call.data['name']
            self.log("【单曲点歌】，歌名：%s", _name)
            await self.api_music.play_song(_name)

    ###################  系统服务  ##########################
    # 调用服务
    def call_service(self, domain, service, data):
        self._hass.async_create_task(self._hass.services.async_call(domain, service, data))

    # 日志
    def log(self, *args):
        _LOGGER.info(*args)
    
    # 更新实体
    def update_entity(self):
        time.sleep(1)
        self.call_service('homeassistant', 'update_entity', {'entity_id': 'media_player.yun_yin_le'})

    # 通知
    def notify(self, message, type):
        self.call_service('persistent_notification', 'create', {"message": message, "title": "云音乐", "notification_id": "ha-cloud-music-" + type})