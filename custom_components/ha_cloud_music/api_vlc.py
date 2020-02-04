import datetime
from homeassistant.const import (STATE_IDLE, STATE_PAUSED, STATE_PLAYING, STATE_OFF, STATE_UNAVAILABLE)

###################内置VLC播放器##########################
class VlcPlayer():
    def __init__(self): 
        import vlc
        self.vlc = vlc
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
        self.ha_cloud_music = True
        self._event_manager = self._vlc.event_manager()
        self._event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.end)
        self._event_manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.update)
    
    def release(self):
        self._vlc.release()
        self._instance.release()

    def end(self, event):
        self.state = STATE_OFF
        
    def update(self, event):
        try:
            status = self._vlc.get_state()
            if status == self.vlc.State.Playing:
                self.state = STATE_PLAYING
            elif status == self.vlc.State.Paused:
                self.state = STATE_PAUSED
            else:
                self.state = STATE_IDLE
            
            media_duration = self._vlc.get_length() / 1000
            self.attributes['media_duration'] = media_duration
            self.attributes['media_position'] = self._vlc.get_position() * media_duration
            self.attributes['media_position_updated_at'] = datetime.datetime.now()
            self.attributes['volume_level'] = self._vlc.audio_get_volume() / 100
            self.attributes['is_volume_muted'] = (self._vlc.audio_get_mute() == 1)
        except Exception as e:
            print(e)

    def load(self, url):
        self._vlc.set_media(self._instance.media_new(url))
        self._vlc.play()
        self.state = STATE_PLAYING
                
    def play(self):
        if self._vlc.is_playing() == False:
            self._vlc.play()
        self.state = STATE_PLAYING
    
    def pause(self):
        if self._vlc.is_playing() == True:
            self._vlc.pause()
        self.state = STATE_PAUSED
    
    def volume_set(self, volume_level):
        self.attributes['volume_level'] = volume_level
        self._vlc.audio_set_volume(int(volume_level * 100))
    
    # 设置位置
    def seek(self, position):
        self.attributes['media_position'] = position
        track_length = self._vlc.get_length()/1000
        self._vlc.set_position(position/track_length)
    
    # 静音
    def mute_volume(self, mute):
        self.attributes['is_volume_muted'] = mute
        self._vlc.audio_set_mute(mute)