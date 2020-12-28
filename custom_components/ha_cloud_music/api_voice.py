import re
from .util import format_number, matcher_singer_music, matcher_playlist_index, \
    matcher_play_pause, matcher_prev_next, matcher_play_music, matcher_volume_setting

class ApiVoice():

    def __init__(self, hass, api_music):
        self.hass = hass
        self.api_music = api_music

    async def call_service(self, action, data = {}):
        data.update({ 'entity_id': 'media_player.yun_yin_le' })
        await self.hass.services.async_call('media_player', action, data)

    async def text_event(self, event):
        hass = self.hass
        text = event.data.get('text', '').strip(' 。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼')
        # 精准匹配
        if ['声音小点', '小点声音', '小一点声音', '声音小一点'].count(text) == 1:
            await self.call_service('volume_down')
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
            return
        elif ['声音大点', '大点声音', '大一点声音', '声音大一点'].count(text) == 1:
            await self.call_service('volume_up')
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
            return
        elif text == '重新加载专辑':
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
                        return
        
        # (播放|暂停)音乐
        result = matcher_play_pause(text)
        if result is not None:
            if result == '播放':
                self.api_music.media.media_play()
            else:
                self.api_music.media.media_pause()
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
            return
        
        # 上一曲、下一曲
        result = matcher_prev_next(text)
        if result is not None:
            if ['上','前'].count(result) == 1:
                self.api_music.media.media_previous_track()
            else:
                self.api_music.media.media_next_track()
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
            return

        # 播放歌手的音乐
        result = matcher_singer_music(text)
        if result is not None:
            # 开始搜索当前歌手的热门歌曲
            await self.api_music.play_singer_hotsong(result)            
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
            return
        
        # 播放第几集
        result = matcher_playlist_index(text)
        if result is not None:
            music_playlist = self.api_music.media.music_playlist
            if music_playlist is not None and len(music_playlist) > 0:
                music_info = music_playlist[0]
                # 获取加载数据
                if 'load' in music_info:
                    load = music_info['load']
                    # 播放推荐音乐
                    await hass.services.async_call('ha_cloud_music', 'load', {
                            'id': load['id'], 
                            'type': load['type'], 
                            'index': result
                        })
                    # 触发语音事件
                    hass.bus.fire("ha_cloud_music_voice_event", {})
                    return

        # 播放(电台|歌单|歌曲|新闻|广播|专辑)(.*)
        result = matcher_play_music(text)
        if result is not None:
            action = result[0]
            _name = result[1]
            if action == '电台':
                await self.api_music.play_dj_hotsong(_name)
            elif action == '歌单':
                await self.api_music.play_list_hotsong(_name)
            elif action == '歌曲':
                await self.api_music.play_song(_name)
            elif action == '新闻':
                await self.api_music.play_news(_name)
            elif action == '广播':
                await self.api_music.play_fm(_name)
            elif action == '专辑':
                # 这里配置是否还有指定集数
                pattern = re.compile(r"(.+)第(.+)[集|首]$")
                NO = pattern.findall(_name)
                if len(NO) == 1:
                    _name = NO[0][0]
                    index = format_number(NO[0][1])
                    print(_name, index)
                    await self.api_music.play_ximalaya(_name, int(index))
                else:
                    # 优先读取本地数据
                    await self.api_music.play_ximalaya(_name, -1)            
            hass.bus.fire("ha_cloud_music_voice_event", {})
            return

        # 音量调整
        result = matcher_volume_setting(text)
        if result is not None:            
            await self.call_service('volume_set', { 'volume_level': result[1] })
            # 触发语音事件
            hass.bus.fire("ha_cloud_music_voice_event", {})
            return