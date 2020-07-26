# 内置VLC播放器

class ApiMedia():

    def __init__(self, media, cfg):
        self.hass = media._hass
        self.media = media
        self.is_notify = bool(cfg['is_notify'])
        self.is_debug = bool(cfg['is_debug'])
        self._LOGGER = cfg['_LOGGER']
   
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
    