import aiohttp, asyncio, json, re, os, uuid, math, urllib, threading, re
import http.cookiejar as HC
from homeassistant.helpers.network import get_url

# 全局请求头
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
# 模拟MAC环境
COOKIES = {'os': 'osx'}

# 乐听头条配置
UID = str(uuid.uuid4()).replace('-','')
LOG_ID = '1234'

class ApiMusic():

    def __init__(self, media, config):
        self.hass = media._hass
        self.media = media
        # 网易云音乐接口地址
        self.api_url = config.get("api_url", '').strip('/')
        self.qq_api_url = config.get('qq_api_url', '').strip('/')
        self.xmly_api_url = config.get('xmly_api_url', '').strip('/')
        # 网易云音乐用户ID
        self.uid = str(config.get("uid", ''))
        # 用户名和密码        
        self.user = str(config.get("user", ''))
        self.password = str(config.get("password", ''))

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
            if res is not None and res['code'] == 200:
                self.uid = str(res['account']['id'])
                self.log('登录成功')
            else:
                self.media.notify("网易云登录失败，请检查账号密码是否错误。如果确定没错，请检查接口是否正常。", "error")
                self.log('登录失败', res)

    def log(self, name, value = ''):
        self.media.log('【ApiMusic接口】%s：%s',name,value)

    async def get(self, url):
        link = self.api_url + url
        # 不是登录请求，则显示出来（这里保护登录信息）
        if '/login' not in url:
            print(link)
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
        print(url)
        result = None
        try:
            headers = {'Referer': url}
            headers.update(HEADERS)
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    # 喜马拉雅返回的是文本内容
                    if 'https://mobile.ximalaya.com/mobile/' in url:
                        result = json.loads(await resp.text())
                    else:    
                        result = await resp.json()
        except Exception as e:
            self.log('【接口出现异常】' + url, e)
        return result

    # QQ音乐
    async def qq_get(self, url):
        if self.qq_api_url != '':
            res = await self.proxy_get(self.qq_api_url + url)
            if res is not None and res['response']["code"] == 0:
                return res['response']

    ###################### 获取音乐播放URL ######################    
    async def get_http_code(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return response.status

    # 获取音乐URL
    async def get_song_url(self, id):
        obj = await self.get("/song/url?id=" + str(id))
        return obj['data'][0]['url']

    # 获取QQ音乐URL
    async def get_qq_song_url(self, id):
        res = await self.qq_get("/getMusicVKey?songmid=" + str(id))
        if res is not None and len(res['playLists']) > 0:
            url = res['playLists'][0]
            http_code = await self.get_http_code(url)
            if http_code == 403:
                # 如果没有权限，说明这个只有尊贵的QQ音乐绿砖会员才能收听
                # 我木有钱，只想白嫖，所以调用这位老哥的开放接口
                vip_url = 'https://api.qq.jsososo.com/song/url?id=' + str(id)
                print(f"使用白嫖接口：{vip_url}")
                res = await self.proxy_get(vip_url)
                return res['data']
            return url

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
            
            res = await self.proxy_get("http://m.music.migu.cn/migu/remoting/scr_search_tag?rows=10&type=2&keyword=" + urllib.parse.quote(keywords) + "&pgc=1")
            
            if 'musics' in res and len(res['musics']) > 0 and (songName in res['musics'][0]['songName'] or searchObj):
                return res['musics'][0]['mp3']
        except Exception as e:
            print("在咪咕搜索时出现错误：", e)
        return None

    ###################### 获取音乐播放URL ######################

    ###################### 搜索音乐列表 ######################    
    # 音乐搜索
    async def search_music(self, name):
        _list = []
        # 搜索网易云音乐
        obj = await self.get('/search?keywords='+ name)
        if obj['code'] == 200:
            songs = obj['result']['songs']
            if len(songs) > 0:
                _newlist = map(lambda item: {
                    "search_source": "网易云音乐",
                    "id": int(item['id']),
                    "name": item['name'],
                    "album": item['album']['name'],
                    "image": item['album']['artist']['img1v1Url']+"?param=300y300",
                    "duration": int(item['duration']) / 1000,
                    "url": "https://music.163.com/song/media/outer/url?id=" + str(item['id']),
                    "song": item['name'],
                    "singer": len(item['artists']) > 0 and item['artists'][0]['name'] or '未知'
                    }, songs)
                _list.extend(list(_newlist))
        # 搜索QQ音乐
        res = await self.qq_get('/getSmartbox?key=' + name)
        if res is not None:
            songs = res['data']['song']
            if songs['count'] > 0:
                _newlist = map(lambda item: {
                    "search_source": "QQ音乐",
                    "id": int(item['id']),
                    "mid": item['mid'],
                    "name": item['name'],
                    "album": "QQ音乐",
                    "image": "http://p3.music.126.net/3TTjFNIrtcUzoMlB1D1fDA==/109951164969055590.jpg?param=300y300",
                    "duration": 0,
                    "type": "qq",
                    "song": item['name'],
                    "singer": item['singer']
                    }, songs['itemlist'])
                _list.extend(list(_newlist))
        # 搜索咪咕音乐
        res = await self.proxy_get("http://m.music.migu.cn/migu/remoting/scr_search_tag?rows=10&type=2&keyword=" + urllib.parse.quote(name) + "&pgc=1")
        if res is not None:
            songs = res['musics']
            if res['pgt'] > 0:
                _newlist = map(lambda item: {
                    "search_source": "咪咕音乐",
                    "id": int(item['id']),
                    "name": item['songName'],
                    "album": item['albumName'],
                    "image": item['cover'] != 'null' and item['cover'] or 'https://m.music.migu.cn/migu/fs/media/p/149/163/5129/image/20171120/1332871.jpg',
                    "duration": 0,
                    "url": item['mp3'],
                    "song": item['songName'],
                    "singer": item['singerName']
                    }, songs)
                _list.extend(list(_newlist))
        return _list

    async def search_ximalaya(self, name):
        _newlist = []
        url = f'https://m.ximalaya.com/m-revision/page/search?kw={name}&core=all&page=1&rows=20'
        obj = await self.proxy_get(url)
        if obj['ret'] == 0:
            artists = obj['data']['albumViews']['albums']
            _newlist = list(map(lambda item: {
                "id": item['albumInfo']['id'],
                "name": item['albumInfo']['title'],
                "cover": item['albumInfo'].get('cover_path', 'https://imagev2.xmcdn.com/group79/M02/77/6C/wKgPEF6masWTCICAAAA7qPQDtNY545.jpg!strip=1&quality=7&magick=webp&op_type=5&upload_type=cover&name=web_large&device_type=ios'),
                "intro": item['albumInfo']['intro'],
                "creator": item['albumInfo']['nickname']
            }, artists))
        return _newlist
    
    async def search_djradio(self, name):
        _newlist = []
        obj = await self.get('/search?keywords='+ name +'&type=1009')
        if obj['code'] == 200:
            artists = obj['result']['djRadios']
            _newlist = list(map(lambda item: {
                "id": item['id'],
                "name": item['name'],
                "cover": item['picUrl'],
                "intro": item['dj']['signature'],
                "creator": item['dj']['nickname']
            }, artists))
        return _newlist
    
    async def search_playlist(self, name):
        _newlist = []
        obj = await self.get('/search?keywords='+ name +'&type=1000')
        if obj['code'] == 200:
            artists = obj['result']['playlists']
            _newlist = list(map(lambda item: {
                "id": item['id'],
                "name": item['name'],
                "cover": item['coverImgUrl'],
                "intro": item['description'],
                "creator": item['creator']['nickname']
            }, artists))
        return _newlist

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
                    'index': offset + 1,
                    'total': _totalCount
                },
                "type": "djradio",
                "singer": item['dj']['nickname']
                }, _list)            
            return list(_newlist)
        else:
            return []

    # 喜马拉雅播放列表
    async def ximalaya_playlist(self, id, index, size=50):
        url = 'https://mobile.ximalaya.com/mobile/v1/album/track?albumId=' + str(id) + '&device=android&isAsc=true&pageId=' + str(index) + '&pageSize=' + str(size) +'&statEvent=pageview%2Falbum%40203355&statModule=%E6%9C%80%E5%A4%9A%E6%94%B6%E8%97%8F%E6%A6%9C&statPage=ranklist%40%E6%9C%80%E5%A4%9A%E6%94%B6%E8%97%8F%E6%A6%9C&statPosition=8'
        obj = await self.proxy_get(url)
        if obj['ret'] == 0:
            _list = obj['data']['list']
            _totalCount = obj['data']['totalCount']
            if len(_list) > 0:
                # 获取专辑名称
                url = 'http://mobile.ximalaya.com/v1/track/baseInfo?device=android&trackId='+str(_list[0]['trackId'])
                _obj = await self.proxy_get(url)
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
                    "type": "xmly",
                    "url": item['playUrl64'],
                    "singer": item['nickname']
                    }, _list)
                return list(_newlist)
        return []

    # 播放专辑
    async def play_ximalaya(self, name, number=1):
        hass = self.hass
        url = 'https://m.ximalaya.com/m-revision/page/search?kw=' + name + '&core=all&page=1&rows=5'
        obj = await self.proxy_get(url)
        if obj['ret'] == 0:
            result = obj['data']['albumViews']
            # print(result)
            if result['total'] > 0:
                albumInfo = result['albums'][0]['albumInfo']
                id = albumInfo['id']
                print('获取ID：' + str(id))
                # 优先获取本地数据
                if number == -1:
                    # 读取本地数据
                    res = self.media.api_config.get_cache_playlist('ximalaya', id)
                    if res is not None:
                        await self.media.play_media('music_playlist', {
                                'index': res['index'],
                                'list': res['playlist']
                            })
                        return None
                    number = 1
                
                _newlist = await self.ximalaya_playlist(id, math.ceil(number / 50), 50)
                index = number % 50 - 1
                if index < 0:
                    index = 49
                # 调用服务，执行播放
                if len(_newlist) > 0:
                    await self.media.play_media('music_playlist', {
                        'index': index,
                        'list': _newlist
                    })
        return None

    # 获取VIP音频链接
    async def get_ximalaya_vip_audio_url(self, id):
        if self.xmly_api_url != '':
            obj = await self.proxy_get(self.xmly_api_url + "/?id=" + str(id))
            if obj is not None and obj['code'] == 0:
                return obj['data']

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
                    await self.media.play_media('music_playlist', list(_newlist))
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
                    await self.media.play_media('music_playlist', list(_newlist))
        else:
            return None

    # 播放音乐
    async def play_song(self, name):
        _list = await self.search_music(name)
        # 调用服务，执行播放
        if len(_list) > 0:
            await self.media.play_media('music_playlist', _list)

    # 播放歌单
    async def play_list_hotsong(self, name):
        obj = await self.get('/search?keywords='+ name +'&type=1000')
        if obj['code'] == 200:
            artists = obj['result']['playlists']
            if len(artists) > 0:
                singerId = artists[0]['id']
                obj = await self.music_playlist(singerId)
                if obj != None and len(obj['list']) > 0:
                    _newlist = obj['list']
                    # 调用服务，执行播放
                    await self.media.play_media('music_playlist', _newlist)
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
                await self.media.play_media('music_playlist', _newlist)

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
                    await self.media.play_media('music_playlist', list(_newlist))
    
    ###################### 缓存到本地音乐库 ######################

    async def cache_file(self, url, file_name):
        hass = self.hass
        path = hass.config.path("media/ha_cloud_music")
        # 替换文件名特殊字符为下划线
        rstr = r"[\/\\\:\*\?\"\<\>\|]"
        name = re.sub(rstr, "_", file_name)

        file_path = os.path.join(path, name + '.mp3')
        print('【缓存文件】' + file_path)
        thread = threading.Thread(target=urllib.request.urlretrieve, args=(url, file_path))
        thread.start()

    ###################### 获取本地音乐库 ######################

    def get_local_media_list(self, search_type):        
        file_path = ''
        singer = "默认列表"
        if search_type != 'library_music':
            file_path = search_type.replace('library_', '')
            singer = file_path

        hass = self.hass
        children = []
        base_url = get_url(hass).strip('/')
        path = hass.config.path("media/ha_cloud_music")
        file_path = file_path.replace('library_', '')
        # 获取所有文件
        file_dir = os.path.join(path, file_path)
        for filename in os.listdir(file_dir):
            if os.path.isfile(os.path.join(file_dir, filename)) and '.mp3' in filename:
                songid = f"{base_url}/media-local/"
                if file_path != '':
                    songid += urllib.parse.quote(f"{file_path}/{filename}")
                else:
                    songid += urllib.parse.quote(filename)
                song = filename.replace('.mp3', '')
                children.append({
                    "name": song,
                    "song": song,
                    "singer": singer,
                    "album": "媒体库",
                    "image": f"{base_url}/static/icons/favicon-192x192.png",
                    "type": "url",
                    "url": songid
                })
        return children
