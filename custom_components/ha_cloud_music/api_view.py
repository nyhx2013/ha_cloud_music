from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN_API, DOMAIN
from .util import trim_char

##### 网关控制
class ApiView(HomeAssistantView):
    url = DOMAIN_API
    name = DOMAIN
    requires_auth = True

    async def post(self, request):
        response = await request.json()
        hass = request.app["hass"]
        mp = hass.data[DOMAIN]
        if 'type' in response:
            _type = response['type']
            _name = trim_char(response.get('name', ''))
            if _type == 'web':
                _result = await mp.api_music.get(response['url'])
                return self.json(_result)
            elif _type == 'proxy':
                _result = await mp.api_music.proxy_get(response['url'])
                return self.json(_result)
            elif _type == 'search-ximalaya':
                _id = response.get('id')
                _page = response.get('page', 1)
                if _id is not None:
                    res = await mp.api_music.ximalaya_playlist(_id, _page)
                    _result = {
                        'list': res,
                        'total': res[0]['load']['total']
                    }
                else:
                    _result = await mp.api_music.search_ximalaya(_name)
                return self.json(_result)
            elif _type == 'search-djradio':
                _id = response.get('id')
                _page = response.get('page', 1)
                if _id is not None:
                    res = await mp.api_music.djradio_playlist(_id, int(_page) - 1, 50)
                    _result = {
                        'list': res,
                        'total': res[0]['load']['total']
                    }
                else:
                    _result = await mp.api_music.search_djradio(_name)
                return self.json(_result)
            elif _type == 'search-playlist':
                _id = response.get('id')
                if _id is not None:
                    res = await mp.api_music.music_playlist(_id)
                    _result = {
                        'list': res['list']
                    }
                else:
                    _result = await mp.api_music.search_playlist(_name)
                return self.json(_result)
            elif _type == 'search-music':
                _result = await mp.api_music.search_music(_name)
                return self.json(_result)
            elif _type == 'play_media':
                await mp.play_media('music_playlist', {
                                'index': response['index'],
                                'list': response['list']
                            })
                mp.update_entity()
                return self.json({"code": 0, "msg": "播放成功"})
            elif _type == 'love_get':
                res = mp.api_config.get_love_playlist()
                return self.json({"code": 0, "msg": "最爱列表", "data": res})
            elif _type == 'love_set':
                mp.api_config.set_love_playlist(mp)
                mp.favourite = True
                mp.update_entity()
                return self.json({"code": 0, "msg": "收藏到我的最爱"})
            elif _type == 'love_delete':
                mp.api_config.delete_love_playlist(response['id'], response.get('music_type', ''))
                return self.json({"code": 0, "msg": "删除成功"})
                
        return self.json(response)