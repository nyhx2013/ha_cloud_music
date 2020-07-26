# 其他播放器

class MediaPlayerOther():

    # 初始化
    def __init__(self, config, media=None):
        self.config = config
        self._muted = False
        self._media = media
        self.volume_level = 0
        self.is_support = True
        def handle_event(event):
            state = event.data.get('state')
            if state == "playing":
                self.state = "playing"
            elif state == "paused":
                self.state = "paused"
            
            self.volume_level = event.data.get('volume_level')
            self._muted = event.data.get('is_volume_muted')
            self.media_duration = event.data.get('media_duration')
            self.media_position = event.data.get('media_position')
            self.media_position_updated_at = datetime.datetime.now()

        # 监听web播放器的更新
        if 'hass' in media:
            self.hass = media.hass
            media.hass.services.register("ha_cloud_music", 'web_media_player_updated', handle_event)

    def load(self, url):
        # 加载URL
        self.hass.bus.fire("web_media_player_changed", {"type": "load", "data": url})

    def play(self):
        # 播放
        self.hass.bus.fire("web_media_player_changed", {"type": "play"})
    
    def pause(self):
        # 暂停
        self.hass.bus.fire("web_media_player_changed", {"type": "pause"})
    
    def seek(self, position):
        # 设置进度
        self.hass.bus.fire("web_media_player_changed", {"type": "media_position", "data": position})

    def mute_volume(self, mute):
        # 静音
        self.hass.bus.fire("web_media_player_changed", {"type": "is_volume_muted", "data": mute})

    def set_volume_level(self, volume):
        # 设置音量
        self.hass.bus.fire("web_media_player_changed", {"type": "volume_set", "data": volume})

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
        self.hass.bus.fire("web_media_player_changed", {"type": "pause"})
