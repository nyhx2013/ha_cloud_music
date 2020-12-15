"""Util for Conversation."""
import re
import string
import random

########################################## 常量

########################################## 去掉前后标点符号
def trim_char(text):
    return text.strip(' 。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼')

########################################## 汉字转数字
common_used_numerals_tmp ={'零':0, '一':1, '二':2, '两':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10, '百':100, '千':1000, '万':10000, '亿':100000000}
common_used_numerals = {}
for key in common_used_numerals_tmp:
  common_used_numerals[key.encode('cp936').decode('cp936')] = common_used_numerals_tmp[key]

def chinese2digits(uchars_chinese):
    try:
        uchars_chinese = uchars_chinese.encode('cp936').decode('cp936')
        total = 0
        r = 1              #表示单位：个十百千...
        for i in range(len(uchars_chinese) - 1, -1, -1):
            val = common_used_numerals.get(uchars_chinese[i])
            if val >= 10 and i == 0:  #应对 十三 十四 十*之类
                if val > r:
                    r = val
                    total = total + val
                else:
                    r = r * val
                #total =total + r * x
            elif val >= 10:
                if val > r:
                    r = val
                else:
                    r = r * val
            else:
                total = total + r * val
        return total
    except Exception as ex:
        return None

# 判断是否数字
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def format_number(num):
    if is_number(num) == False:
        num = chinese2digits(num)
    return float(num)

########################################## (我想听|播放)(.+)的(歌|音乐)
def matcher_singer_music(text):
    matchObj = re.match(r'(我想听|播放)(.+)的(歌|音乐)', text)
    if matchObj is not None:
        return matchObj.group(2)

########################################## 播放(电台|歌单|歌曲|新闻|广播|专辑)(.*)
def matcher_play_music(text):
    matchObj = re.match(r'播放(电台|歌单|歌曲|新闻|广播|专辑)(.*)', text)
    if matchObj is not None:
        return (matchObj.group(1), matchObj.group(2))

########################################## (播放|暂停)音乐
def matcher_play_pause(text):
    matchObj = re.match(r'(播放|暂停)音乐', text)
    if matchObj is not None:
        return matchObj.group(1)

########################################## (上|下|前|后)一(曲|首)
def matcher_prev_next(text):
    matchObj = re.match(r'(上|下|前|后)一(曲|首)', text)
    if matchObj is not None:
        return matchObj.group(1)

########################################## 集数调整
def matcher_playlist_index(text):
    matchObj = re.match(r'播放第(.+)(集|首)(.*)', text)
    if matchObj is not None:
        return format_number(matchObj.group(1))

########################################## 音量调整
def matcher_volume_setting(text):
    matchObj = re.match(r'(把tts|把音乐|音乐|tts)(声音|音量)调到(.+)', text)
    if matchObj is not None:
        volume_level = matchObj.group(3)
        if volume_level == '最大':
            volume_level = 100.0
        elif volume_level == '最小':
            volume_level = 20.0
        else:
            volume_level = format_number(volume_level)
        return (matchObj.group(1), float(volume_level) / 100.0)