# MPD播放器
'''
python3 -m pip install python-mpd2
'''
import time

class MediaPlayerMPD():

    # 初始化
    def __init__(self, config, media=None):
        self.config = config
        self._status = None
        self._muted = False
        self._muted_volume = 0
        self._media = media
        try:
            import mpd
            self._client = mpd.MPDClient()
            self._client.timeout = 30
            self._client.idletimeout = None
            # 连接MPD服务
            self._client.connect(config['host'], config.get('port', '6600'))
            if 'password' in config:
                self._client.password(config['password'])
            self.is_support = True
        except Exception as e:
            print(e)
            self.is_support = False

    @property
    def volume_level(self):
        # 获取音量
        if "volume" in self._status:
            return int(self._status["volume"]) / 100
        return None

    def update(self):
        # 更新
        self._status = self._client.status()
        position = self._status.get("time")
        media_position = 0
        media_duration = 0
        # 读取音乐时长和进度
        if isinstance(position, str) and ':' in position:
            arr = position.split(':')
            media_position = int(arr[0])
            media_duration = int(arr[1])
            # 判断是否下一曲
            if media_duration > 0:
                print('当前进度：%s，总时长：%s', media_position, media_duration)
                if media_duration - media_position <= 1:
                    print('执行下一曲方法')
                    if self._media is not None:
                        self._media.media_end_next()

        self.media_position = media_position
        self.media_duration = media_duration

    def load(self, url):
        # 加载URL
        self._client.clear()
        self._client.add(url)
        self._client.play()

    def play(self):
        # 播放
        self._client.pause(0)
    
    def pause(self):
        # 暂停
        self._client.pause(1)
    
    def seek(self, position):
        # 设置进度
        self._client.seekcur(position)

    def mute_volume(self, mute):
        # 静音
        if "volume" in self._status:
            if mute:
                self._muted_volume = self.volume_level
                self.set_volume_level(0)
            else:
                self.set_volume_level(self._muted_volume)
            self._muted = mute

    def set_volume_level(self, volume):
        # 设置音量
        if "volume" in self._status:
            self._client.setvol(int(volume * 100))

    def volume_up(self):
        # 增加音量
        if "volume" in self._status:
            current_volume = int(self._status["volume"])

            if current_volume <= 100:
                self._client.setvol(current_volume + 5)

    def volume_down(self):
        # 减少音量
        if "volume" in self._status:
            current_volume = int(self._status["volume"])

            if current_volume >= 0:
                self._client.setvol(current_volume - 5)

    def stop(self):
        # 停止
        self._client.stop()
        self._client.disconnect()

mm = MediaPlayerMPD({'host': '192.168.1.113'})
if mm.is_support:
    mm.load('http://music.jiluxinqing.com/mp3/20200328182257900.mp3')

while True:
    time.sleep(1)
    mm.update()
    pass