import re

class ApiVoice():

    def __init__(self, hass, api_music):
        self.hass = hass
        self.api_music = api_music

    async def text_event(self,event):
        hass = self.hass
        _text = event.data.get('text')
        #_log_info('监听语音小助手的文本：' + _text)
        # 我想听xxx的歌
        pattern = re.compile(r"我想听(.+)的歌")
        singer = pattern.findall(_text)
        if len(singer) == 1:
            # 正在播放xxx的歌
            singerName = singer[0]
            # 开始搜索当前歌手的热门歌曲
            await self.api_music.play_singer_hotsong(singerName)
        # 播放电台 xxxx
        if _text.find('播放电台') == 0:
            _name = _text.split('播放电台')[1]
            await self.api_music.play_dj_hotsong(_name)
        # 播放歌单 xxxx
        if _text.find('播放歌单') == 0:
            _name = _text.split('播放歌单')[1]
            await self.api_music.play_list_hotsong(_name)
        # 播放歌曲 xxxx
        if _text.find('播放歌曲') == 0:
            _name = _text.split('播放歌曲')[1]
            await self.api_music.play_song(_name)
        # 播放新闻
        if _text.find('播放新闻') == 0:
            _name = _text.split('播放新闻')[1]
            await self.api_music.play_news(_name)
        # 播放专辑
        if _text.find('播放专辑') == 0:
            _name = _text.split('播放专辑')[1]
            await self.api_music.play_ximalaya(_name)

        # 音乐控制解析
        if '下一曲' == _text:
            await hass.services.async_call('media_player', 'media_next_track', {'entity_id': 'media_player.ha_cloud_music'})
        elif '上一曲' == _text:
            await hass.services.async_call('media_player', 'media_previous_track', {'entity_id': 'media_player.ha_cloud_music'})
        elif '播放音乐' == _text:
            await hass.services.async_call('media_player', 'media_play', {'entity_id': 'media_player.ha_cloud_music'})
        elif '暂停音乐' == _text:
            await hass.services.async_call('media_player', 'media_pause', {'entity_id': 'media_player.ha_cloud_music'})
        elif '声音小点' == _text or '小点声音' == _text or '小一点声音' == _text or '声音小一点' == _text:
            await hass.services.async_call('media_player', 'volume_down', {'entity_id': 'media_player.ha_cloud_music'})
        elif '声音大点' == _text or '大点声音' == _text or '大一点声音' == _text or '声音大一点' == _text:
            await hass.services.async_call('media_player', 'volume_up', {'entity_id': 'media_player.ha_cloud_music'})