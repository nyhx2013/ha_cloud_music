import os, hashlib, asyncio, threading, time
from mutagen.mp3 import MP3
from urllib.request import urlopen, quote, urlretrieve
from homeassistant.helpers import template
from homeassistant.const import (STATE_IDLE, STATE_PAUSED, STATE_PLAYING, STATE_OFF, STATE_UNAVAILABLE)
# md5加密
def md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()

from .api_const import ROOT_PATH

class ApiTTS():
    def __init__(self, media, cfg):
        self.hass = media._hass
        self.media = media
        self.media_position = None
        self.media_url = None
        self.thread = None        
        self.tts_before_message = cfg['tts_before_message']
        self.tts_after_message = cfg['tts_after_message']
    
    def log(self, name,value):
        self.media.api_media.log('【文本转语音】%s：%s',name,value)

    # 异步进行TTS逻辑
    def async_tts(self, text):
        # 如果当前正在播放，则暂停当前播放，保存当前播放进度
        if self.media._media != None and self.media._state == STATE_PLAYING:
           self.media.media_pause()
           self.media_position = self.media._media_position
           self.media_url = self.media._media_url
        
        # 下载文件到本地缓存，播放当前文字内容
        url = "https://api.jiluxinqing.com/api/service/tts?text="+ quote(text)
        f_name = md5(text) + ".mp3"
        ob_name = os.path.join(os.path.dirname(__file__), 'dist/cache/' + f_name).replace('\\','/')
        self.log('本地文件路径', ob_name)
        if os.path.isfile(ob_name) == False:
            urlretrieve(url, ob_name)
        else:
            # 如果没有下载，则延时1秒
            time.sleep(1)
        local_url = self.hass.config.api.base_url + ROOT_PATH + '/cache/' + f_name        
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
        # 恢复当前播放到保存的进度
        if self.media_url != None:
            self.log('恢复当前播放URL', self.media_position)
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