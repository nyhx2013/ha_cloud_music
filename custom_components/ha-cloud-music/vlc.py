import datetime

STATE_IDLE = 'idle'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'

class VlcPlayer():
    def __init__(self):
        import vlc        
        self._instance = vlc.Instance()
        self._vlc = self._instance.media_player_new()
        self.state = STATE_IDLE
        self.attributes = {
            "volume_level": 1,
            "is_volume_muted": False,
            "media_duration": 0,
            "media_position_updated_at": None,
            "media_position": 0,
        }
        event_manager = self._vlc.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.update)

    def update(self):
        import vlc        
        status = self._vlc.getstate()
        if status == vlc.State.Playing:
            self.state = STATE_PLAYING
        elif status == vlc.State.Paused:
            self.state = STATE_PAUSED
        else:
            self.state = STATE_IDLE

        self.attributes['media_duration'] = self._vlc.get_length() / 1000
        self.attributes['media_position'] = self._vlc.get_position() * self._media_duration
        self.attributes['media_position_updated_at'] = datetime.datetime.now()
        self.attributes['volume_level'] = self._vlc.audio_get_volume() / 100
        self.attributes['is_volume_muted'] = (self._vlc.audio_get_mute() == 1)

    def play(self, url):
        self._vlc.set_media(self._instance.media_new(url))
        self._vlc.play()
        self.state = STATE_PLAYING


try:
   vlcPlayer = VlcPlayer()
except Exception as e:
    print(e)
