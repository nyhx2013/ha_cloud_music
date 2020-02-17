import os, hashlib, asyncio, threading, time, requests
from mutagen.mp3 import MP3
from urllib.request import urlopen, quote, urlretrieve
from homeassistant.helpers import template
from homeassistant.const import (STATE_IDLE, STATE_PAUSED, STATE_PLAYING, STATE_OFF, STATE_UNAVAILABLE)

session = requests.session()

from .api_const import ROOT_PATH
from .api_config import ApiConfig

class ApiTTS():
    def __init__(self, media, cfg):
        self.hass = media._hass
        self.media = media
        self.media_position = None
        self.media_url = None
        self.thread = None        
        self.tts_before_message = cfg['tts_before_message']
        self.tts_after_message = cfg['tts_after_message']
        tts_mode = cfg['tts_mode']        
        if [1, 2, 3, 4].count(tts_mode) == 0:
            tts_mode = 4            
        self.tts_mode = tts_mode
        self.api_config = ApiConfig(os.path.join(os.path.dirname(__file__), 'dist/cache'))
    
    def log(self, name,value):
        self.media.api_media.log('【文本转语音】%s：%s',name,value)

    # 异步进行TTS逻辑
    def async_tts(self, text):
        # 如果当前正在播放，则暂停当前播放，保存当前播放进度
        if self.media._media != None and self.media._state == STATE_PLAYING:
           self.media.media_pause()
           self.media_position = self.media._media_position
           self.media_url = self.media._media_url        
        # 播放当前文字内容
        self.play_url(text)
        # 恢复当前播放到保存的进度
        if self.media_url != None:
            self.log('恢复当前播放URL', self.media_url)
            self.hass.services.call('media_player', 'play_media', {
                'entity_id': 'media_player.ha_cloud_music',
                'media_content_id': self.media_url,
                'media_content_type': 'music'
            })
            time.sleep(2)
            self.log('恢复当前进度', self.media_position)
            self.hass.services.call('media_player', 'media_seek', {
                'entity_id': 'media_player.ha_cloud_music',
                'seek_position': self.media_position
            })
            # 启用自动下一曲
            self.media._timer_enable = True
            self.media_url = None

    # 获取语音URL
    def play_url(self, text):
        # 生成文件名
        f_name = self.api_config.md5(text) + ".mp3"
        # 创建目录名称
        _dir =  self.api_config.get_path('tts')
        self.api_config.mkdir(_dir)
        # 生成缓存文件名称
        ob_name = _dir + '/' + f_name
        self.log('本地文件路径', ob_name)
        # 文件不存在，则获取下载
        if os.path.isfile(ob_name) == False:
            session.get('https://ai.baidu.com/tech/speech/tts')
            res = session.post('https://ai.baidu.com/aidemo',{
                'type': 'tns',
                'spd': 5,
                'pit': 5,
                'vol': 5,
                'per': self.tts_mode,
                'tex': text
            })
            r = res.json()
            if r['errno'] == 0:
                base64_data = r['data'].replace('data:audio/x-mpeg;base64,','')
                self.api_config.base64_to_file(base64_data,  ob_name)
        else:
            # 如果没有下载，则延时1秒
            time.sleep(1)
        # 生成播放地址
        local_url = self.hass.config.api.base_url + ROOT_PATH + '/cache/tts/' + f_name        
        self.log('本地URL', local_url)
        self.hass.services.call('media_player', 'play_media', {
            'entity_id': 'media_player.ha_cloud_music',
            'media_content_id': local_url,
            'media_content_type': 'music'
        })
        # 计算当前文件时长，设置超时播放时间
        audio = MP3(ob_name)
        self.log('音频时长', audio.info.length)
        time.sleep(audio.info.length + 4)

    async def speak(self, call):
        try:
            text = call.data['message']
            # 解析模板
            tpl = template.Template(text, self.hass)
            text = self.tts_before_message + tpl.async_render(None) + self.tts_after_message
            self.log('解析后的内容', text)
            if self.thread != None:
                self.thread.join()

            self.thread = threading.Thread(target=self.async_tts, args=(text,))
            self.thread.start()            
        except Exception as ex:
            self.log('出现异常', ex)

    # 清除缓存
    async def clear(self, call):
        try:
            _path = self.api_config.get_path('tts')
            self.api_config.delete(_path)  
        except Exception as ex:
            self.log('出现异常', ex)