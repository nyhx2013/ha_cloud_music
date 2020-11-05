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
                                'list': response['playlist']
                            })
                
        return self.json(response)