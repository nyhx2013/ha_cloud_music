# 配置Android应用使用
import time, datetime, requests, aiohttp
import threading

class MediaPlayerAndroid():

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
        self._status = None
        self.is_support = True
        self._muted_volume = 0
        self.volume_level = 1
        # 定时更新
        self.request('set', 'music_reset')
        self.timer = threading.Timer(2, self.update)
        self.timer.start()

    # 发送数据请求
    async def async_request(self, type, key, value = ''):
        android_host = self.config['android_host']
        url = f'http://{android_host}:8124/{type}?key={key}&value={value}'
        print(url)
        async with aiohttp.request('GET', url) as resp:
            content = await resp.json()
            print(content)
            return content

    def request(self, type, key, value = ''):
        if self._media is not None:
            self._media._hass.async_create_task(self.async_request(type, key, value))        

    def update(self):
        # 更新
        try:
            android_host = self.config['android_host']
            url = f'http://{android_host}:8124/get?key=music'
            result = requests.get(url, timeout=3)
            res = result.json()
            print(res)
            media_position = res['media_position']
            media_duration = res['media_duration']
            state = res['state']
            self.volume_level = res.get('volume_level')
            # 判断是否下一曲
            if state == 'end':
                print('执行下一曲方法')
                if self._media is not None and self.state == 'playing' and self.is_tts == False and self.is_on == True:
                    self.state = 'idle'
                    self._media.media_end_next()
                    time.sleep(3)
            else:
                # print("当前进度：%s，总时长：%s"%(media_position, media_duration))
                self.media_position = media_position
                self.media_duration = media_duration
                self.media_position_updated_at = datetime.datetime.now()
            self.is_support = True
        except Exception as e:
            self.is_support = False
            print('出现异常', e)
        
        # 递归调用自己
        self.timer = threading.Timer(4, self.update)
        self.timer.start()  

    def reloadURL(self, url, position):
        time.sleep(1)
        # 重新加载URL
        self.load(url)
        time.sleep(2)
        # 先把声音设置为0，然后调整位置之后再还原
        self.set_volume_level(0)
        time.sleep(1)
        self.seek(position)
        time.sleep(1)
        self.set_volume_level(self._media.volume_level)

    def load(self, url):
        # 加载URL
        url = url.replace("https://", "http://")
        self.request('set', 'music_url', url)
        # 不是TTS时才设置状态
        if self.is_tts == False:
            self.state = 'playing'
        
    def play(self):
        # 播放
        self.state = 'playing'
        self.request('set', 'music_play')
    
    def pause(self):
        # 暂停
        self.state = 'paused'
        self.request('set', 'music_pause')
    
    def seek(self, position):
        # 设置进度
        self.request('set', 'music_seek', position)

    def mute_volume(self, mute):
        # 静音
        if mute:
            self._muted_volume = self.volume_level
            self.set_volume_level(0)
        else:
            self.set_volume_level(self._muted_volume)
        self._muted = mute

    def set_volume_level(self, volume):
        # 设置音量
        self.request('set', 'msuic_set_volume', int(volume * 100))

    def volume_up(self):
        # 增加音量
        current_volume = self.volume_level
        if current_volume <= 100:
            self.set_volume_level(current_volume + 5)

    def volume_down(self):
        # 减少音量
        current_volume = self.volume_level
        if current_volume >= 0:
            self.set_volume_level(current_volume - 5)

    def stop(self):
        self.timer.cancel()
        self.request('set', 'music_reset')

    def log(self, msg):
        if self._media is not None:
            self._media.log(msg, 'source_android')

'''
mm = MediaPlayerAndroid({'android_host': 'localhost'})
if mm.is_support:
    mm.load('https://freetyst.nf.migu.cn/public%2Fproduct4th%2Fproduct36%2F2019%2F09%2F0614%2F2018%E5%B9%B409%E6%9C%8824%E6%97%A500%E7%82%B900%E5%88%86%E6%89%B9%E9%87%8F%E9%A1%B9%E7%9B%AE%E5%8D%8E%E7%BA%B399%E9%A6%96-16%2F%E5%85%A8%E6%9B%B2%E8%AF%95%E5%90%AC%2FMp3_64_22_16%2F6005751FH33.mp3')
'''