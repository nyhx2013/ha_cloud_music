# VLC播放器
import time, datetime

class MediaPlayerVLC():

    # 初始化
    def __init__(self, config, media=None):
        # 播放器相同字段
        self.config = config
        self._media = media
        self._muted = False
        self.media_position = 0
        self.media_duration = 0
        self.media_position_updated_at = datetime.datetime.now()
        
        try:
            import vlc
            self._instance = vlc.Instance()
            self._client = self._instance.media_player_new()
            _event_manager = self._client.event_manager()
            _event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.end)
            _event_manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.update)
            self.is_support = True
        except Exception as e:
            print(e)
            self.is_support = False

    @property
    def volume_level(self):
        return self._client.audio_get_volume() / 100
    
    def end(self, event):
        # 音乐结束
        print('执行下一曲')
        if self._media is not None:
            self._media.media_end_next()

    def update(self, event):
        # 更新
        media_duration = int(self._client.get_length() / 1000)
        media_position = int(self._client.get_position() * media_duration)
        print("当前进度：%s，总时长：%s"%(media_position, media_duration))
        self.media_position = media_position
        self.media_duration = media_duration
        self.media_position_updated_at = datetime.datetime.now()
        self._muted = (self._client.audio_get_mute() == 1)

    def load(self, url):
        # 加载URL
        self._client.set_media(self._instance.media_new(url))
        self._client.play()

    def play(self):
        # 播放
        if self._client.is_playing() == False:
            self._client.play()
    
    def pause(self):
        # 暂停
        if self._client.is_playing() == True:
            self._client.pause()
    
    def seek(self, position):
        # 设置进度
        track_length = self._client.get_length() / 1000
        self.media_position = position
        self._client.set_position(position / track_length)

    def mute_volume(self, mute):
        # 静音
        self._client.audio_set_mute(mute)
        self._muted = mute

    def set_volume_level(self, volume):
        # 设置音量
        self._client.audio_set_volume(int(volume * 100))

    def volume_up(self):
        # 增加音量
        current_volume = self._client.audio_get_volume()
        if current_volume <= 100:
            self._client.audio_set_volume(current_volume + 5)

    def volume_down(self):
        # 减少音量
        current_volume = self._client.audio_get_volume()
        if current_volume <= 100:
            self._client.audio_set_volume(current_volume - 5)

    def stop(self):
        # 停止
        self._client.release()
        self._instance.release()

'''
mm = MediaPlayerVLC({})
if mm.is_support:
    mm.load('http://music.jiluxinqing.com/mp3/2014122718214050.mp3')

while True:
    pass
'''