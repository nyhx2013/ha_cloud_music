from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN_API, DOMAIN

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
            _name = response.get('name', '')
            if _type == 'web':
                _result = await mp.api_music.get(response['url'])
                return self.json(_result)
            elif _type == 'proxy':
                _result = await mp.api_music.proxy_get(response['url'])
                return self.json(_result)
            elif _type == 'search-ximalaya':
                _result = await mp.api_music.search_ximalaya(_name)
                return self.json(_result)
            elif _type == 'search-djradio':
                _result = await mp.api_music.search_djradio(_name)
                return self.json(_result)
            elif _type == 'search-playlist':
                _result = await mp.api_music.search_playlist(_name)
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
                return self.json({"code": 0, "msg": "收藏到我的最爱"})
            elif _type == 'love_delete':
                mp.api_config.delete_love_playlist(response['id'], response.get('music_type', ''))
                return self.json({"code": 0, "msg": "删除成功"})
                
        return self.json(response)