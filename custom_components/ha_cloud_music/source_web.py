# 网页播放器
import time, datetime
from homeassistant.components import websocket_api
import voluptuous as vol

WS_TYPE_MEDIA_PLAYER = "ha_cloud_music_event"
SCHEMA_WEBSOCKET = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
    {
        "type": WS_TYPE_MEDIA_PLAYER,
        vol.Optional("data"): dict,
    }
)

class MediaPlayerWEB():

    # 初始化
    def __init__(self, config, media=None):
        # 播放器相同字段
        self.config = config
        self._media = media
        self._muted = False
        self.media_position = 0
        self.media_duration = 0
        self.media_position_updated_at = datetime.datetime.now()
        self.state = 'idle'
        self.is_tts = False
        self.is_on = True
        # 不同字段
        self.volume_level = 1
        self.is_support = True
        # 监听web播放器的更新
        if media is not None:
            # media._hass.services.register("ha_cloud_music", 'web_media_player_updated', self.update)
            self.hass = media._hass
            # 监听web播放器的更新
            self.hass.components.websocket_api.async_register_command(
                WS_TYPE_MEDIA_PLAYER,
                self.update,
                SCHEMA_WEBSOCKET
            )

    def update(self, hass, connection, msg):
        data = msg['data']
        # 音乐结束
        if self._media is not None and self.is_tts == False and self.is_on == True and data.get('is_end') == 1:
            print('执行下一曲')
            self._media.media_end_next()
        else:
            self.volume_level = data.get('volume_level')
            self._muted = data.get('is_volume_muted')
            self.media_duration = data.get('media_duration')
            self.media_position = data.get('media_position')
            self.media_position_updated_at = datetime.datetime.now()
        # 回调结果
        # self.connection = connection

    def reloadURL(self, url, position):
        # 重新加载URL
        self.load(url)
        # 先把声音设置为0，然后调整位置之后再还原
        volume_level = self.volume_level
        if volume_level > 0:
            self.set_volume_level(0)
        time.sleep(2)
        self.seek(position)
        if volume_level > 0:
            time.sleep(1)
            self.set_volume_level(volume_level)

    def load(self, url):
        # 加载URL
        self.hass.bus.fire("ha_cloud_music_event", {"type": "load", "data": url})
        # 不是TTS时才设置状态
        if self.is_tts == False:
            self.state = 'playing'

    def play(self):
        # 播放
        self.hass.bus.fire("ha_cloud_music_event", {"type": "play"})
        self.state = "playing"
    
    def pause(self):
        # 暂停
        self.hass.bus.fire("ha_cloud_music_event", {"type": "pause"})
        self.state = "paused"
    
    def seek(self, position):
        # 设置进度
        self.hass.bus.fire("ha_cloud_music_event", {"type": "media_position", "data": position})

    def mute_volume(self, mute):
        # 静音
        self.hass.bus.fire("ha_cloud_music_event", {"type": "is_volume_muted", "data": mute})

    def set_volume_level(self, volume):
        # 设置音量
        self.hass.bus.fire("ha_cloud_music_event", {"type": "volume_set", "data": volume})

    def volume_up(self):
        # 增加音量
        current_volume = self.volume_level
        if current_volume <= 100:
            self.set_volume_level(current_volume + 5)

    def volume_down(self):
        # 减少音量
        current_volume = self.volume_level
        if current_volume <= 100:
            self.set_volume_level(current_volume - 5)

    def stop(self):
        # 停止
        self.hass.bus.fire("ha_cloud_music_event", {"type": "pause"})
