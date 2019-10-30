"""
百度语音外挂服务.
专门解决vlc播放器输出被截断的问题
"""
import asyncio
import logging

import aiohttp
from aiohttp.hdrs import REFERER, USER_AGENT
import async_timeout
import voluptuous as vol

from homeassistant.components.tts import CONF_LANG, PLATFORM_SCHEMA, Provider
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

GOOGLE_SPEECH_URL = "https://api.jiluxinqing.com/api/service/tts?text="

CONF_PLAYER = "player"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Optional(CONF_PLAYER, default=""): vol.string
)

async def async_get_engine(hass, config):
    """Set up Google speech component."""
    return GoogleProvider(hass,  config[CONF_PLAYER])


class GoogleProvider(Provider):
    """The Google speech API provider."""

    def __init__(self, hass, player):
        """Init Google TTS service."""
        self.hass = hass
        self._player = player
        self.name = "百度语音"

    @property
    def default_language(self):
        """Return the default language."""
        return "zh-cn"

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return "zh-cn"

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS from google."""
        websession = async_get_clientsession(self.hass)
        data = b""
        try:
            with async_timeout.timeout(10):
                # 如果播放器是vlc，则在后面加上多余的字符
                if self._player == 'vlc':
                    message = message + "。哦"

                request = await websession.get(
                    GOOGLE_SPEECH_URL + message, params=None, headers=None
                )

                if request.status != 200:
                    _LOGGER.error(
                        "Error %d on load URL %s", request.status, request.url
                    )
                    return None, None
                data += await request.read()

        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Timeout for google speech")
            return None, None

        return "mp3", data
