DOMAIN = 'ha_cloud_music'
VERSION = '2.3.1'
DOMAIN_API = '/' + DOMAIN + '-api'
ROOT_PATH = '/' + DOMAIN + '-local/' + VERSION

def TrueOrFalse(val, trueStr, falseStr):
    if val:
        return trueStr
    return falseStr