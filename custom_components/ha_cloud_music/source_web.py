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
        self.rate = 1
        self.media_position = 0
        self.media_duration = 0
        self.media_position_updated_at = datetime.datetime.now()
        self.state = 'idle'
        self.is_tts = False
        self.is_on = True
        # 不同字段
        self.count = 0
        self.volume_level = 1
        self.is_support = True
        # 监听web播放器的更新
        if media is not None:
            self.hass = media._hass
            # 监听web播放器的更新
            self.hass.components.websocket_api.async_register_command(
                WS_TYPE_MEDIA_PLAYER,
                self.update,
                SCHEMA_WEBSOCKET
            )

    def update(self, hass, connection, msg):
        data = msg['data']
        if self._media is not None:
            # 消息类型
            type = data.get('type', '')
            # 客户端ID
            client_id = data.get('client_id', '')
            if type == 'init':
                # 初始化连接成功
                self.hass.bus.fire("ha_cloud_music_event", {"type": "init", "data": {
                    'client_id': client_id,
                    'volume_level': self.volume_level,
                    'media_url': self._media.media_url,
                    'media_position': self.media_position
                }})
            elif type == 'update':
                media_position = data.get('media_position', 0)
                media_duration = data.get('media_duration', 0)                
                print(self.media_position)
                print(self.media_duration)
                # 更新进度
                if self.media_duration is not None and self.media_position is not None \
                    and self.media_duration > 0 and self.media_position > 0 \
                    and self.media_position + 2 >= self.media_duration \
                    and self.count > 0:
                    print('执行下一曲')
                    self.count = -10
                    self._media.media_end_next()
                # 防止通信太慢，导致进度跟不上自动下下一曲
                self.count = self.count + 1
                if self.count > 100:
                    self.count = 0
                # 更新数据
                self.volume_level = data.get('volume_level')
                self._muted = data.get('is_volume_muted')
                self.media_duration = media_duration
                self.media_position = media_position
                self.media_position_updated_at = datetime.datetime.now()        
        # 回调结果
        # self.connection = connection

    def reloadURL(self, url, position):
        # 重新加载URL
        self.load(url)
        # 先把声音设置为0，然后调整位置之后再还原
        self.set_volume_level(0)
        # 局域网资源，则优化快进规则
        if self._media.base_url in url:
            time.sleep(0.1)
            self.seek(position)
        else:
            time.sleep(1)
            self.seek(position)
            time.sleep(1)
        self.set_volume_level(self._media.volume_level)

    def load(self, url):
        # 使用TTS服务
        if self.is_tts:
            self.hass.bus.fire("ha_cloud_music_event", {"type": "tts", "data": url})
        else:
            # 加载URL
            self.hass.bus.fire("ha_cloud_music_event", {"type": "load", "data": url})
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

    def set_rate(self, rate):
        # 设置播放速度
        return 1