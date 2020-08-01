import aiohttp, asyncio, json, re, os, uuid
import http.cookiejar as HC
from .api_config import get_config_path, read_config_file, write_config_file

# 全局请求头
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
# 模拟MAC环境
COOKIES = {'os': 'osx'}

# 乐听头条配置
UID = str(uuid.uuid4()).replace('-','')
LOG_ID = '1234'

class ApiMusic():

    def __init__(self, media, cfg):
        self.hass = media._hass
        self.media = media
        self.api_url = cfg['api_url']
        self.uid = cfg['uid']
        self.user = cfg['user']
        self.password = cfg['password']

    async def login(self):
        # 如果有用户名密码，则登录
        if self.user != '' and self.password != '':
            self.log('登录操作', '开始登录')
            # 判断是否使用邮箱
            if '@' in self.user:
                # 邮箱登录
                res = await self.get('/login?email=' + self.user + '&password=' + self.password)
            else:               
                # 手机号码登录
                res = await self.get('/login/cellphone?phone=' + self.user + '&password=' + self.password)
            # 登录成功
            if res['code'] == 200:
                self.uid = str(res['account']['id'])
                write_config_file('account.json', {
                    'uid': self.uid,
                    'user': self.user,
                    'account': res['account']
                })
                self.log('登录成功')
            else:
                self.log('登录失败', res)

    def log(self, name, value = ''):
        self.media.log('【ApiMusic接口】%s：%s',name,value)

    async def get(self, url):
        link = self.api_url + url
        result = None
        try:
            global COOKIES            
            jar = aiohttp.CookieJar(unsafe=True)
            async with aiohttp.ClientSession(headers=HEADERS, cookies=COOKIES, cookie_jar=jar) as session:
                async with session.get(link) as resp:
                    # 如果是登录，则将登录状态保存起来
                    if '/login' in url:
                        _dict = {}
                        cookies = session.cookie_jar.filter_cookies(self.api_url)
                        for key, cookie in cookies.items():
                            _dict[key] = cookie.value
                            # print(key)
                            # print(cookie.value)
                        # 设置全局cookies值
                        COOKIES = _dict

                    result = await resp.json()
        except Exception as e:
            self.log('【接口出现异常】' + link, e)
        return result
    
    async def proxy_get(self, url):
        result = None
        try:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                async with session.get(url) as resp:
                    # 喜马拉雅返回的是文本内容
                    if 'https://mobile.ximalaya.com/mobile/' in url:
                        result = json.loads(await resp.text())
                    else:    
                        result = await resp.json()
        except Exception as e:
            self.log('【接口出现异常】' + url, e)
        return result

    ###################### 获取音乐播放URL ######################    
    
    # 获取音乐URL
    async def get_song_url(self, id):
        obj = await self.get("/song/url?id=" + str(id))
        return obj['data'][0]['url']

    # 获取重写向后的地址
    async def get_redirect_url(self, url):
        # 请求网页
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result_url = str(response.url)
                if result_url == 'https://music.163.com/404':
                    return None
                return result_url
        return None

    # 进行咪咕搜索，可以播放周杰伦的歌歌
    async def migu_search(self, songName, singerName):
        try:
            # 如果含有特殊字符，则直接使用名称搜索
            searchObj = re.search(r'\(|（|：|:《', songName, re.M|re.I)
            if searchObj:
                keywords = songName
            else:    
                keywords = songName + ' - '+ singerName
            
            res = await self.proxy_get("http://m.music.migu.cn/migu/remoting/scr_search_tag?rows=10&type=2&keyword=" + keywords + "&pgc=1")
            
            if 'musics' in res and len(res['musics']) > 0 and (songName in res['musics'][0]['songName'] or searchObj):
                return res['musics'][0]['mp3']
        except Exception as e:
            print("在咪咕搜索时出现错误：", e)
        return None

    ###################### 获取音乐播放URL ######################

    ###################### 获取音乐列表 ######################

    # 获取网易歌单列表
    async def music_playlist(self, id):
        obj = await self.get('/playlist/detail?id=' + str(id))
        if obj['code'] == 200:            
            trackIds = obj['playlist']['trackIds']
            _trackIds = map(lambda item: str(item['id']), trackIds)
            _obj = await self.get('/song/detail?ids=' + ','.join(_trackIds))
            _list = _obj['songs']
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
    async def djradio_playlist(self, id, offset, size):
        obj = await self.get('/dj/program?rid='+str(id)+'&limit=50&offset='+str(offset * size))
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

    # 喜马拉雅播放列表
    async def ximalaya_playlist(self, id, index, size):
        obj = await self.proxy_get('https://mobile.ximalaya.com/mobile/v1/album/track?albumId=' + str(id) + '&device=android&isAsc=true&pageId='\
            + str(index) + '&pageSize=' + str(size) +'&statEvent=pageview%2Falbum%40203355&statModule=%E6%9C%80%E5%A4%9A%E6%94%B6%E8%97%8F%E6%A6%9C&statPage=ranklist%40%E6%9C%80%E5%A4%9A%E6%94%B6%E8%97%8F%E6%A6%9C&statPosition=8')

        if obj['ret'] == 0:
            _list = obj['data']['list']
            _totalCount = obj['data']['totalCount']
            if len(_list) > 0:
                # 获取专辑名称
                _obj = await self.proxy_get('http://mobile.ximalaya.com/v1/track/baseInfo?device=android&trackId='+str(_list[0]['trackId']))
                
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

    # 播放专辑
    async def play_ximalaya(self, name):
        hass = self.hass
        obj = await self.proxy_get('https://m.ximalaya.com/revision/suggest?kw=' + name + '&paidFilter=false&scope=all')
        if obj['ret'] == 200:
            result = obj['data']['result']
            print(result)
            if result['albumResultNum'] > 0:
                id = result['albumResultList'][0]['id']
                print('获取ID：' + str(id))
                _newlist = await self.ximalaya_playlist(id, 1, 50)
                if len(_newlist) > 0:
                    # 调用服务，执行播放
                    _dict = {
                        'index': 0,
                        'list': json.dumps(list(_newlist), ensure_ascii=False)
                    }
                    await hass.services.async_call('media_player', 'play_media', {
                                        'entity_id': 'media_player.yun_yin_le',
                                        'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                        'media_content_type': 'music_playlist'
                                    })
        return None

    ###################### 获取音乐列表 ######################

    ###################### 播放音乐列表 ######################
    
    # 播放电台
    async def play_dj_hotsong(self, name):
        hass = self.hass
        obj = await self.get('/search?keywords='+ name +'&type=1009')
        if obj['code'] == 200:
            artists = obj['result']['djRadios']
            if len(artists) > 0:
                singerId = artists[0]['id']
                _newlist = await self.djradio_playlist(singerId, 0, 50)
                if len(_newlist) > 0:
                    # 调用服务，执行播放
                    _dict = {
                        'index': 0,
                        'list': json.dumps(list(_newlist), ensure_ascii=False)
                    }
                    await hass.services.async_call('media_player', 'play_media', {
                                        'entity_id': 'media_player.yun_yin_le',
                                        'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                        'media_content_type': 'music_playlist'
                                    }, blocking=True)
        else:
            return None
    
    # 播放歌手的热门歌曲
    async def play_singer_hotsong(self, name):
        hass = self.hass
        obj = await self.get('/search?keywords='+ name +'&type=100')
        if obj['code'] == 200:
            artists = obj['result']['artists']
            if len(artists) > 0:
                singerId = artists[0]['id']
                # 获取热门歌曲
                hot_obj = await self.get('/artists/top/song?id='+ str(singerId))
                if hot_obj['code'] == 200:
                    _list = hot_obj['hotSongs']
                    _newlist = map(lambda item: {
                        "id": int(item['id']),
                        "name": item['name'],
                        "album": item['al']['name'],
                        "image": ('picUrl' in item['al']) and item['al']['picUrl'] or hot_obj['artist']['picUrl'],
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
                                        'entity_id': 'media_player.yun_yin_le',
                                        'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                        'media_content_type': 'music_playlist'
                                    }, blocking=True)
        else:
            return None

    # 播放歌手的热门歌曲
    async def play_song(self, name):
        hass = self.hass
        obj = await self.get('/search?keywords='+ name)
        if obj['code'] == 200:
            songs = obj['result']['songs']
            if len(songs) > 0:
                _list = songs
                _newlist = map(lambda item: {
                    "id": int(item['id']),
                    "name": item['name'],
                    "album": item['album']['name'],
                    "image": item['album']['artist']['img1v1Url'],
                    "duration": int(item['duration']) / 1000,
                    "url": "https://music.163.com/song/media/outer/url?id=" + str(item['id']),
                    "song": item['name'],
                    "singer": len(item['artists']) > 0 and item['artists'][0]['name'] or '未知'
                    }, _list)
                # 调用服务，执行播放
                _dict = {
                    'index': 0,
                    'list': json.dumps(list(_newlist), ensure_ascii=False)
                }
                await hass.services.async_call('media_player', 'play_media', {
                                    'entity_id': 'media_player.yun_yin_le',
                                    'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                    'media_content_type': 'music_playlist'
                                }, blocking=True)
                
        else:
            return None
            

    # 播放歌单
    async def play_list_hotsong(self, name):
        hass = self.hass
        obj = await self.get('/search?keywords='+ name +'&type=1000')
        if obj['code'] == 200:
            artists = obj['result']['playlists']
            if len(artists) > 0:
                singerId = artists[0]['id']
                obj = await self.music_playlist(singerId)
                if obj != None and len(obj['list']) > 0:
                    _newlist = obj['list']
                    # 调用服务，执行播放
                    _dict = {
                        'index': 0,
                        'list': json.dumps(_newlist, ensure_ascii=False)
                    }
                    await hass.services.async_call('media_player', 'play_media', {
                                        'entity_id': 'media_player.yun_yin_le',
                                        'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                        'media_content_type': 'music_playlist'
                                    }, blocking=True)                
        else:
            return None
    
    ###################### 播放音乐列表 ######################

    ###################### 播放新闻 ######################

    # 获取新闻
    async def _get_news(self, session, leting_headers, catalog_id):
        async with session.get('https://app.leting.io/app/url/channel?catalog_id=' + catalog_id + '&size=20&distinct=1&v=v8&channel=xiaomi', headers=leting_headers) as res:
            r = await res.json()
            _list = r['data']['data']
            _newlist = map(lambda item: {
                "id": item['sid'],
                "name": item['title'],
                "album": item['catalog_name'],
                "image": item['source_icon'],
                "duration": item['duration'],
                "url": item['audio'],
                "song": item['title'],
                "singer": item['source']
                }, _list)
            return list(_newlist)
        return None

    async def play_news(self, name):
        hass = self.hass
        async with aiohttp.ClientSession() as session:
            async with session.get('https://app.leting.io/auth?uid=' + UID + '&appid=f03268abb256885da72e046b556a588c&app_secret=a595a43547ed414e2e96378a338f2f21&logid=' + LOG_ID) as res:
                r = await res.json()
                token = r['data']['token']
                leting_headers = {"uid":UID, "logid": LOG_ID, "token": token}
                _newlist = []
                # 热点
                _list = await self._get_news(session, leting_headers, 'f3f5a6d2-5557-4555-be8e-1da281f97c22')
                if _list is not None:
                    _newlist.extend(_list)
                # 社会
                _list = await self._get_news(session, leting_headers, 'd8e89746-1e66-47ad-8998-1a41ada3beee')
                if _list is not None:
                    _newlist.extend(_list)
                # 国际
                _list = await self._get_news(session, leting_headers, '4905d954-5a85-494a-bd8c-7bc3e1563299')
                if _list is not None:
                    _newlist.extend(_list)
                # 国内
                _list = await self._get_news(session, leting_headers, 'fc583bff-e803-44b6-873a-50743ce7a1e9')
                if _list is not None:
                    _newlist.extend(_list)
                # 科技
                _list = await self._get_news(session, leting_headers, 'f5cff467-2d78-4656-9b72-8e064c373874')
                if _list is not None:
                    _newlist.extend(_list)
                '''
                热点：f3f5a6d2-5557-4555-be8e-1da281f97c22
                社会：d8e89746-1e66-47ad-8998-1a41ada3beee
                国际：4905d954-5a85-494a-bd8c-7bc3e1563299
                国内：fc583bff-e803-44b6-873a-50743ce7a1e9
                体育：c7467c00-463d-4c93-b999-7bbfc86ec2d4
                娱乐：75564ed6-7b68-4922-b65b-859ea552422c
                财经：c6bc8af2-e1cc-4877-ac26-bac1e15e0aa9
                科技：f5cff467-2d78-4656-9b72-8e064c373874
                军事：ba89c581-7b16-4d25-a7ce-847a04bc9d91
                生活：40f31d9d-8af8-4b28-a773-2e8837924e2e
                教育：0dee077c-4956-41d3-878f-f2ab264dc379
                汽车：5c930af2-5c8a-4a12-9561-82c5e1c41e48
                人文：f463180f-7a49-415e-b884-c6832ba876f0
                旅游：8cae0497-4878-4de9-b3fe-30518e2b6a9f
                北京市：29d6168ed172c09fc81d2d71d4ec0686
                '''
                # 调用服务，执行播放
                _dict = {
                    'index': 0,
                    'list': json.dumps(_newlist, ensure_ascii=False)
                }
                await hass.services.async_call('media_player', 'play_media', {
                                    'entity_id': 'media_player.yun_yin_le',
                                    'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                    'media_content_type': 'music_playlist'
                                })
                    

    ###################### 播放新闻 ######################

    
    ###################### 播放广播 ######################

    async def play_fm(self, name):
        hass = self.hass
        async with aiohttp.ClientSession() as session:
            async with session.get('https://search.qingting.fm/v3/search?categoryid=0&k=' + name + '&page=1&pagesize=15&include=all') as res:
                r = await res.json()
                docs = r['data']['data']['docs']
                if isinstance(docs, list):
                    # 过滤直播
                    filter_list = list(filter(lambda item: item['type'] == 'channel_live', docs))
                    if len(filter_list) == 0:
                        return None
                    # print(filter_list)
                    # 整理格式
                    _newlist = map(lambda item: {
                        "id": item['id'],
                        "name": item['title'],
                        "album": item['category_name'],
                        "image": item['cover'],
                        "duration": 0,
                        "url": 'http://lhttp.qingting.fm/live/' + str(item['id']) + '/64k.mp3',
                        "song": item['title'],
                        "singer": '蜻蜓FM'
                    }, filter_list)
                    # 调用服务，执行播放
                    _dict = {
                        'index': 0,
                        'list': json.dumps(list(_newlist), ensure_ascii=False)
                    }
                    await hass.services.async_call('media_player', 'play_media', {
                                        'entity_id': 'media_player.yun_yin_le',
                                        'media_content_id': json.dumps(_dict, ensure_ascii=False),
                                        'media_content_type': 'music_playlist'
                                    })
    
