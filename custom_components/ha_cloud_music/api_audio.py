import datetime
from homeassistant.const import (STATE_IDLE, STATE_PAUSED, STATE_PLAYING, STATE_OFF, STATE_UNAVAILABLE)

###################网页版audio元素##########################
class AudioPlayer():
    def __init__(self, hass):
        self.hass = hass
        self.state = STATE_IDLE
        self.is_active = False
        self.attributes = {
            "volume_level": 1,
            "is_volume_muted": False,
            "media_duration": 0,
            "media_position_updated_at": None,
            "media_position": 0,
        }
        self.ha_web_music = True

        def handle_event(event):
            state = event.data.get('state')
            if state == "playing":
                self.state = STATE_PLAYING
            elif state == "paused":
                self.state = STATE_PAUSED
            
            self.attributes['volume_level'] = event.data.get('volume_level')
            self.attributes['is_volume_muted'] = event.data.get('is_volume_muted')
            self.attributes['media_duration'] = event.data.get('media_duration')
            self.attributes['media_position_updated_at'] = event.data.get('media_position_updated_at')
            self.attributes['media_position'] = event.data.get('media_position')

        # 监听web播放器的更新
        hass.services.register("ha_cloud_music", 'web_media_player_updated', handle_event)

    # 释放
    def release(self):
        self.is_active = False

    # 加载音乐   
    def load(self, url):
        self.is_active = True
        self.hass.bus.fire("web_media_player_changed", {"type": "load", "data": url})
        self.state = STATE_PLAYING

    # 播放            
    def play(self):
        self.hass.bus.fire("web_media_player_changed", {"type": "play"})
        self.state = STATE_PLAYING
    
    # 暂停
    def pause(self):
        self.hass.bus.fire("web_media_player_changed", {"type": "pause"})
        self.state = STATE_PAUSED
    
    # 设置音量
    def volume_set(self, volume_level):
        self.hass.bus.fire("web_media_player_changed", {"type": "volume_set", "data": volume_level})
    
    # 设置位置
    def seek(self, position):
        self.hass.bus.fire("web_media_player_changed", {"type": "media_position", "data": position})
    
    # 静音
    def mute_volume(self, mute):
        self.hass.bus.fire("web_media_player_changed", {"type": "is_volume_muted", "data": mute})