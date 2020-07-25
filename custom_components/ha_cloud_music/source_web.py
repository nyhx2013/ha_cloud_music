# 网页播放器

class MediaPlayerWEB():

    def __init__(self, config):
        self.config = config
        self.state = 0

    def load(self, url):
        # 加载URL
        self.state = 1

    def play(self):
        self.state = 1
    
    def pause(self):
        self.state = 2
        
