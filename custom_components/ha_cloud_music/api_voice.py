import re

class ApiVoice():

    def __init__(self, hass, api_music):
        self.hass = hass
        self.api_music = api_music

    async def text_event(self, event):
        hass = self.hass
        _text = event.data.get('text', '').strip(' 。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼')
        #_log_info('监听语音小助手的文本：' + _text)
        # 我想听xxx的歌
        pattern = re.compile(r"^我想听(.+)的歌$")
        singer = pattern.findall(_text)
        if len(singer) == 1:
            # 正在播放xxx的歌
            singerName = singer[0]
            # 开始搜索当前歌手的热门歌曲
            await self.api_music.play_singer_hotsong(singerName)
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        # 播放第几集
        pattern = re.compile(r"^播放第(.+)[集|首]$")
        NO = pattern.findall(_text)
        if len(NO) == 1:
            index = NO[0]
            if is_number(index) == False:
                index = t(index)
            music_playlist = self.api_music.media.music_playlist
            if music_playlist is not None and len(music_playlist) > 0:
                music_info = music_playlist[0]
                # 获取加载数据
                if 'load' in music_info:
                    load = music_info['load']
                    print(load)
                    # 播放推荐音乐
                    await hass.services.async_call('ha_cloud_music', 'load', {
                            'id': load['id'], 
                            'type': load['type'], 
                            'index': index
                        })
                    # 触发语音事件
                    hass.bus.fire("ha_cloud_music_voice_event", {})
        # 重新加载专辑
        if _text == '重新加载专辑':
            music_playlist = self.api_music.media.music_playlist
            if music_playlist is not None and len(music_playlist) > 0:
                music_info = music_playlist[0]
                # 获取加载数据
                if 'load' in music_info:
                    load = music_info['load']
                    _newlist = await self.api_music.ximalaya_playlist(load['id'], load['index'])
                    if len(_newlist) > 0:
                        await self.api_music.media.play_media('music_playlist', {
                            'index': self.api_music.media.music_index,
                            'list': _newlist
                        })
                        print('重新加载专辑成功')

        # 播放电台 xxxx
        if _text.find('播放电台') == 0:
            _name = _text.split('播放电台')[1]
            await self.api_music.play_dj_hotsong(_name)
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        # 播放歌单 xxxx
        if _text.find('播放歌单') == 0:
            _name = _text.split('播放歌单')[1]
            await self.api_music.play_list_hotsong(_name)
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        # 播放歌曲 xxxx
        if _text.find('播放歌曲') == 0:
            _name = _text.split('播放歌曲')[1]
            await self.api_music.play_song(_name)
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        # 播放新闻
        if _text.find('播放新闻') == 0:
            _name = _text.split('播放新闻')[1]
            await self.api_music.play_news(_name)
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        # 播放专辑
        if _text.find('播放专辑') == 0:
            _name = _text.split('播放专辑')[1]
            # 这里配置是否还有指定集数
            pattern = re.compile(r"(.+)第(.+)[集|首]$")
            NO = pattern.findall(_name)
            if len(NO) == 1:
                _name = NO[0][0]
                index = NO[0][1]
                if is_number(index) == False:
                    index = t(index)
                print(_name, index)
                await self.api_music.play_ximalaya(_name, int(index))
            else:
                # 优先读取本地数据
                await self.api_music.play_ximalaya(_name, -1)
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        # 播放广播
        if _text.find('播放广播') == 0:
            _name = _text.split('播放广播')[1]
            await self.api_music.play_fm(_name)
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})

        # 音乐控制解析
        if '下一曲' == _text:
            self.api_music.media.media_next_track()
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        elif '上一曲' == _text:
            self.api_music.media.media_previous_track()
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        elif '播放音乐' == _text:
            self.api_music.media.media_play()
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        elif '暂停音乐' == _text:
            self.api_music.media.media_pause()
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        elif '声音小点' == _text or '小点声音' == _text or '小一点声音' == _text or '声音小一点' == _text:
            await hass.services.async_call('media_player', 'volume_down', {'entity_id': 'media_player.yun_yin_le'})
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
        elif '声音大点' == _text or '大点声音' == _text or '大一点声音' == _text or '声音大一点' == _text:
            await hass.services.async_call('media_player', 'volume_up', {'entity_id': 'media_player.yun_yin_le'})
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})

# 判断是否数字
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

# 汉字转数字
def t(str):
    zhong={'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
    danwei={'十':10,'百':100,'千':1000,'万':10000}
    num=0
    if len(str)==0:
        return 0
    if len(str)==1:
        if str == '十':
            return 10
        num=zhong[str]
        return num
    temp=0
    if str[0] == '十':
        num=10
    for i in str:
        if i == '零':
            temp=zhong[i]
        elif i == '一':
            temp=zhong[i]
        elif i == '二':
            temp=zhong[i]
        elif i == '三':
            temp=zhong[i]
        elif i == '四':
            temp=zhong[i]
        elif i == '五':
            temp=zhong[i]
        elif i == '六':
            temp=zhong[i]
        elif i == '七':
            temp=zhong[i]
        elif i == '八':
            temp=zhong[i]
        elif i == '九':
            temp=zhong[i]
        if i == '十':
            temp=temp*danwei[i]
            num+=temp
        elif i == '百':
            temp=temp*danwei[i]
            num+=temp
        elif i == '千':
            temp=temp*danwei[i]
            num+=temp
        elif i == '万':
            temp=temp*danwei[i]
            num+=temp
    if str[len(str)-1] != '十'and str[len(str)-1] != '百'and str[len(str)-1] != '千'and str[len(str)-1] != '万':
        num+=temp
    return num