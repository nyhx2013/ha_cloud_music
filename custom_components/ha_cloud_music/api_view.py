from homeassistant.components.http import HomeAssistantView

from .api_const import DOMAIN_API,DOMAIN

##### 网关控制
class ApiView(HomeAssistantView):
    """View to handle Configuration requests."""

    url = DOMAIN_API
    name = DOMAIN
    requires_auth = True

    async def post(self, request):
        response = await request.json()
        hass = request.app["hass"]
        if 'type' in response:
            _type = response['type'] 
            if _type == 'web':
                mp = hass.data[DOMAIN]
                _result = mp.api_music.get(response['url'])
                return self.json(_result)
                
        return self.json(response)