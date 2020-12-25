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
        self.state = 'idle'
        self.is_tts = False
        self.is_on = True

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

    @property
    def rate(self):
        return round(self._client.get_rate(), 1)

    def end(self, event):
        # 音乐结束
        if self._media is not None and self.is_tts == False and self.is_on == True:
            print('执行下一曲')
            self._media.media_end_next()

    def update(self, event):
        # 如果是TTS中，则不更新进度
        if self.is_tts == False:
            media_duration = int(self._client.get_length() / 1000)
            media_position = int(self._client.get_position() * media_duration)
            # print("当前进度：%s，总时长：%s"%(media_position, media_duration))
            self.media_position = media_position
            self.media_duration = media_duration
            self.media_position_updated_at = datetime.datetime.now()
            self._muted = (self._client.audio_get_mute() == 1)

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
        # 加载URL
        url = url.replace("https://", "http://")
        self._client.set_media(self._instance.media_new(url))
        self._client.play()
        # 不是TTS时才设置状态
        if self.is_tts == False:
            self.state = 'playing'

    def play(self):
        self.state = 'playing'
        # 播放
        if self._client.is_playing() == False:
            self._client.play()
    
    def pause(self):
        self.state = 'paused'
        # 暂停
        if self._client.is_playing() == True:
            self._client.pause()
    
    def seek(self, position):
        # 设置进度
        track_length = self._client.get_length() / 1000
        if track_length > 0:
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

    def set_rate(self, rate):
        # 设置播放速度
        return self._client.set_rate(rate)

'''
mm = MediaPlayerVLC({})
if mm.is_support:
    mm.load('https://m701.music.126.net/20201225165051/fd7f6db013996a3316a31bce123d9399/jdymusic/obj/wo3DlMOGwrbDjj7DisKw/5258591663/61bf/33cf/e6a5/da47602351f7f71aea8c1e88de587411.mp3')
    mm.set_rate(1)

while True:
    pass
'''