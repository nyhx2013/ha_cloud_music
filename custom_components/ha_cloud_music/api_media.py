# 内置VLC播放器
from .api_vlc import VlcPlayer

class ApiMedia():

    def __init__(self, media, cfg):
        self.hass = media._hass
        self.media = media
        self.is_notify = bool(cfg['is_notify'])
        self.is_debug = bool(cfg['is_debug'])
        self._LOGGER = cfg['_LOGGER']
        # 判断是否支持VLC
        self._supported_vlc = None
    
    ###################### 内置VLC播放器相关方法 ######################
    # 判断是否支持VLC
    @property
    def supported_vlc(self):
        """判断是否支持vlc模块."""
        if self._supported_vlc != None:
            return self._supported_vlc

        try:
            # 执行引入vlc操作，如果报错，则不支持vlc
            import vlc
            instance = vlc.Instance()
            instance.media_player_new()
            instance.release()
            self._supported_vlc = True
            return True
        except Exception as e:
            self._supported_vlc = False
            return False
    
    # 初始化内置VLC播放器
    def init_vlc_player(self):
        try:
            if self.media._media == None or hasattr(self.media._media, 'ha_cloud_music') == False:
                self.media._media = VlcPlayer()
        except Exception as e:
            print("【初始化内置VLC播放器】出现错误", e)  

    # 释放vlc对象
    def release_vlc_player(self):        
        if self.media._media != None and hasattr(self.media._media, 'ha_cloud_music') == True:
            self.media._media.release()

    ###################### 内置VLC播放器相关方法 ######################

    # 通知
    def notification(self, message, type):
        if self.is_notify == True:
            self.hass.async_create_task(self.hass.services.async_call('persistent_notification', 'create', 
                {"message": message, 
                "title": "云音乐", 
                "notification_id": 
                "ha-cloud-music-" + type}))

    # 调用服务
    def call_service(self, domain, service, data):
        self.hass.async_create_task(self.hass.services.async_call(domain, service, data))

    ###################### 调试日志 ######################

    # 日志
    def log(self, *args):
        if self.is_debug == True:
            self._LOGGER.info(*args)
    
    # 调试日志
    def debug(self, *args):
        self._LOGGER.debug(*args)
    
    ###################### 调试日志 ######################
    