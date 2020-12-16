import json, os, shutil, hashlib, base64

from .const import DOMAIN, VERSION, DOMAIN_API, WEB_PATH, ROOT_PATH

class ApiConfig():

    def __init__(self, _dir):        
        if os.path.exists(_dir) == False:           
            self.mkdir(_dir)
        self.dir = _dir

    def get_tts(self):
        return self.read('tts.json')

    def set_tts(self, mode, volume):
        content = {
            'mode': mode,
            'volume': volume
        }
        self.write('tts.json', content)

    ''' 【设置/获取】最爱列表 '''
    def get_love_playlist(self):
        res = self.read('love.json')
        if res is None:
            return []
        return res

    # 当前是否喜欢
    def is_love_playlist(self, id, type):
        res = self.get_love_playlist()
        length = len(list(filter(lambda m: m['id'] == id and m.get('type', '') == type, res)))
        return length > 0

    def set_love_playlist(self, media):
        res = self.get_love_playlist()
        playlist = media.music_playlist
        index = media.music_index
        # 判断当前播放音乐是否存在
        music_info = playlist[index]
        length = len(list(filter(lambda m: m['id'] == music_info['id'] and m.get('type', '') == music_info.get('type', ''), res)))
        if length == 0:
            res.insert(0, music_info)
        self.write('love.json', res)
    
    # 删除收藏
    def delete_love_playlist(self, id, type):
        res = self.get_love_playlist()
        index = -1
        for i, item in enumerate(res):
            print(item)
            print(i)
            if item['id'] == id and item.get('type', '') == type:
                index = i
        if index >= 0:
            res.pop(index)
            self.write('love.json', res)

    ''' 【设置/获取】播放列表 '''
    def get_playlist(self):
        return self.read('playlist.json')

    def set_playlist(self, media):
        volume_level = media.volume_level
        playlist = media.music_playlist
        index = media.music_index
        content = {
            'volume_level': volume_level,
            'index': index,
            'playlist': playlist
        }
        self.write('playlist.json', content)
        # 缓存当前播放列表
        music_info = playlist[index]
        if 'load' in music_info:
            obj = music_info['load']
            self.write(obj['type'] + '-' + str(obj['id']) + '.json', content)

    # 缓存文件
    def get_cache_playlist(self, type, id):
        return self.read(type + '-' + str(id) + '.json')

    ''' 【设置/获取】播放器 '''
    def get_sound_mode(self):
        return self.read('sound_mode.json')

    def set_sound_mode(self, sound_mode):
        self.write('sound_mode.json', {'state': sound_mode})

    # 加密
    def md5(self, data):
        return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()

    # 创建文件夹
    def mkdir(self, path):
        folders = []
        while not os.path.isdir(path):
            path, suffix = os.path.split(path)
            folders.append(suffix)
        for folder in folders[::-1]:
            path = os.path.join(path, folder)
            os.mkdir(path)

    # 获取目录列表
    def get_dirs(self, _path):
        file_name = os.listdir(_path)
        _list = []
        for file in file_name:
            abs_path = os.path.join(_path, file)
            if os.path.isdir(abs_path):
                fileinfo = os.stat(abs_path)
                _list.append({
                    'name': file,
                    'path': abs_path,
                    'size': fileinfo.st_size,
                    'size_name': self.format_byte(fileinfo.st_size),
                    'edit_time': fileinfo.st_mtime,
                })
        return _list

    # 获取文件列表
    def get_files(self, _path):
        file_name = os.listdir(_path)
        _list = []
        for file in file_name:
            abs_path = os.path.join(_path, file)
            if os.path.isfile(abs_path):
                fileinfo = os.stat(abs_path)
                _list.append({
                    'name': file,
                    'path': abs_path,
                    'size': fileinfo.st_size,
                    'size_name': self.format_byte(fileinfo.st_size),
                    'edit_time': fileinfo.st_mtime,
                })
        return _list

    # 格式化文件大小的函数
    def format_byte(self, number):
        for (scale, label) in [(1024*1024*1024, "GB"), (1024*1024,"MB"), (1024,"KB")]:
            if number >= scale:
                return "%.2f %s" %(number*1.0/scale,lable)
            elif number == 1:
                return "1字节"
            else:  #小于1字节
                byte = "%.2f" % (number or 0)
                return ((byte[:-3]) if byte.endswith(".00") else byte) + "字节"

    # 获取路径
    def get_path(self, name):
        return self.dir + '/' + name

    # 读取文件内容
    def read(self, name):
        fn = self.get_path(name)
        if os.path.isfile(fn):
            with open(fn,'r', encoding='utf-8') as f:
                content = json.load(f)
                return content
        return None

    # 写入文件内容
    def write(self, name, obj):
        with open(self.get_path(name), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)

    # 删除文件
    def delete(self, _path):
        if os.path.exists(_path):
            if os.path.isfile(_path):
                # 删除文件
                os.remove(_path)
            elif os.path.isdir(_path):
                # 删除目录
                shutil.rmtree(_path, ignore_errors=True)

    # base64数据生成文件
    def base64_to_file(self, base64_data, file):
        ori_image_data = base64.b64decode(base64_data)
        fout = open(file, 'wb')
        fout.write(ori_image_data)
        fout.close()