import aiohttp, asyncio, json, requests, re

# 全局请求头
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

class ApiMusic():

    def __init__(self, hass, _api_url, _uid, _user, _password):
        self.hass = hass
        self._api_url = _api_url
        self._uid = _uid
        self._user = _user
        self._password = _password

    async def get(self, url):
        async with aiohttp.request('GET',self._api_url + url) as r:
          return await r.json(encoding="utf-8")

    # 获取重写向后的地址
    def get_redirect_url(self, url):
        # 请求网页    
        response = requests.get(url, headers=HEADERS)
        result_url = response.url
        if result_url == 'https://music.163.com/404':
            return None
        return result_url

    # 进行咪咕搜索，可以播放周杰伦的歌歌
    def migu_search(self, songName, singerName):
        try:
            # 如果含有特殊字符，则直接使用名称搜索
            searchObj = re.search(r'\(|（|：|:《', songName, re.M|re.I)
            if searchObj:
                keywords = songName
            else:    
                keywords = songName + ' - '+ singerName
            response = requests.get("http://m.music.migu.cn/migu/remoting/scr_search_tag?rows=10&type=2&keyword=" + keywords + "&pgc=1", headers=HEADERS)
            res = response.json()
            
            if 'musics' in res and len(res['musics']) > 0 and (songName in res['musics'][0]['songName'] or searchObj):
                return res['musics'][0]['mp3']
        except Exception as e:
            print("在咪咕搜索时出现错误：", e)
        return None

    # 获取网易歌单列表
    def music_playlist(self, id):
        res = requests.get(self._api_url + '/playlist/detail?id=' + str(id))
        obj = res.json()
        if obj['code'] == 200:
            _list = obj['playlist']['tracks']
            _newlist = map(lambda item: {
                "id": int(item['id']),
                "name": item['name'],
                "album": item['al']['name'],
                "image": item['al']['picUrl'],
                "duration": int(item['dt']) / 1000,
                "url": "https://music.163.com/song/media/outer/url?id=" + str(item['id']),
                "song": item['name'],
                "singer": len(item['ar']) > 0 and item['ar'][0]['name'] or '未知'
                }, _list)
            return {
                'name': obj['playlist']['name'],
                'list': list(_newlist)
            }
        else:
            return None

    # 获取网易电台列表
    def djradio_playlist(self, id, offset, size):
        res = requests.get(self._api_url + '/dj/program?rid='+str(id)+'&limit=50&offset='+str(offset * size))
        obj = res.json()
        if obj['code'] == 200:
            _list = obj['programs']
            _totalCount = obj['count']
            _newlist = map(lambda item: {
                "id": int(item['mainSong']['id']),
                "name": item['name'],
                "album": item['dj']['brand'],
                "image": item['coverUrl'],
                "duration": int(item['mainSong']['duration']) / 1000,
                "song": item['name'],
                "load":{
                    'id': id,
                    'type': 'djradio',
                    'index': offset,
                    'total': _totalCount
                },
                "type": "djradio",
                "singer": item['dj']['nickname']
                }, _list)            
            return list(_newlist)
        else:
            return []



    # 播放电台
    async def play_dj_hotsong(self, djName):
        hass = self.hass
        res = requests.get(self._api_url + '/search?keywords='+ djName +'&type=1009')
        obj = res.json()
        if obj['code'] == 200:
            artists = obj['result']['djRadios']
            if len(artists) > 0:
                singerId = artists[0]['id']
                _newlist = self.djradio_playlist(singerId, 0, 50)
                if len(_newlist) > 0:
                    # 调用服务，执行播放
                    _dict = {
                        'index': 0,
                        'list': json.dumps(list(_newlist), ensure_ascii=False)
                    }
                    await hass.services.async_call('media_player', 'play_media', {
                                        'entity_id': 'media_player.ha_cloud_music',
                                        'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                        'media_content_type': 'music_playlist'
                                    }, blocking=True)
                
        else:
            return None
    
    # 播放歌手的热门歌曲
    async def play_singer_hotsong(self, singerName):
        hass = self.hass
        res = requests.get(self._api_url + '/search?keywords='+ singerName +'&type=100')
        obj = res.json()
        if obj['code'] == 200:
            artists = obj['result']['artists']
            if len(artists) > 0:
                singerId = artists[0]['id']
                # 获取热门歌曲
                hot_res = requests.get(self._api_url + '/artists/top/song?id='+ str(singerId))
                hot_obj = hot_res.json()
                if hot_obj['code'] == 200:
                    _list = hot_obj['hotSongs']
                    _newlist = map(lambda item: {
                        "id": int(item['id']),
                        "name": item['name'],
                        "album": item['al']['name'],
                        "image": item['al']['picUrl'],
                        "duration": int(item['dt']) / 1000,
                        "url": "https://music.163.com/song/media/outer/url?id=" + str(item['id']),
                        "song": item['name'],
                        "singer": len(item['ar']) > 0 and item['ar'][0]['name'] or '未知'
                        }, _list)
                    # 调用服务，执行播放
                    _dict = {
                        'index': 0,
                        'list': json.dumps(list(_newlist), ensure_ascii=False)
                    }
                    await hass.services.async_call('media_player', 'play_media', {
                                        'entity_id': 'media_player.ha_cloud_music',
                                        'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                        'media_content_type': 'music_playlist'
                                    }, blocking=True)
                
        else:
            return None

    # 播放歌单
    async def play_list_hotsong(self, djName):
        hass = self.hass
        res = requests.get(self._api_url + '/search?keywords='+ djName +'&type=1000')
        obj = res.json()
        if obj['code'] == 200:
            artists = obj['result']['playlists']
            if len(artists) > 0:
                singerId = artists[0]['id']
                obj = self.music_playlist(singerId)
                if obj != None and len(obj['list']) > 0:
                    _newlist = obj['list']
                    # 调用服务，执行播放
                    _dict = {
                        'index': 0,
                        'list': json.dumps(_newlist, ensure_ascii=False)
                    }
                    await hass.services.async_call('media_player', 'play_media', {
                                        'entity_id': 'media_player.ha_cloud_music',
                                        'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                        'media_content_type': 'music_playlist'
                                    }, blocking=True)
                
        else:
            return None

    # 喜马拉雅播放列表
    def ximalaya_playlist(self, id, index, size):
        res = requests.get('https://mobile.ximalaya.com/mobile/v1/album/track?albumId=' + str(id) + '&device=android&isAsc=true&pageId='\
            + str(index) + '&pageSize=' + str(size) +'&statEvent=pageview%2Falbum%40203355&statModule=%E6%9C%80%E5%A4%9A%E6%94%B6%E8%97%8F%E6%A6%9C&statPage=ranklist%40%E6%9C%80%E5%A4%9A%E6%94%B6%E8%97%8F%E6%A6%9C&statPosition=8')
        obj = res.json()
        if obj['ret'] == 0:
            _list = obj['data']['list']
            _totalCount = obj['data']['totalCount']
            if len(_list) > 0:
                # 获取专辑名称
                _res = requests.get('http://mobile.ximalaya.com/v1/track/baseInfo?device=android&trackId='+str(_list[0]['trackId']))
                _obj = _res.json()
                # 格式化列表
                _newlist = map(lambda item: {
                    "id": item['trackId'],
                    "name": item['title'],
                    "album": _obj['albumTitle'],
                    "image": item['coverLarge'],
                    "duration": item['duration'],
                    "song": item['title'],
                    "load":{
                        'id': id,
                        'type': 'ximalaya',
                        'index': index,
                        'total': _totalCount
                    },
                    "type": "url",
                    "url": item['playUrl64'],
                    "singer": item['nickname']
                    }, _list)
                return list(_newlist)
        return []