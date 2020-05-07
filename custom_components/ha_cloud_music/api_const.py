import os, json

DOMAIN = 'ha_cloud_music'
VERSION = '2.4.1'
DOMAIN_API = '/' + DOMAIN + '-api'
ROOT_PATH = '/' + DOMAIN + '-local/' + VERSION

def TrueOrFalse(val, trueStr, falseStr):
    if val:
        return trueStr
    return falseStr

# 获取配置路径
def get_config_path(name):
    return os.path.join(os.path.dirname(__file__), 'dist/cache/' + name).replace('\\','/')

# 读取配置
def read_config_file(name):
    fn = get_config_path(name)
    if os.path.isfile(fn):
        with open(fn,'r',encoding='utf-8') as f:
            content = json.load(f)
            return content
    return None

# 写入配置
def write_config_file(name, obj):
    with open(get_config_path(name),'w',encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False)