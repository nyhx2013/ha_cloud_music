# 各个功能配置介绍

功能太多，按需配置

```

# 完整配置
# api_url: 接口请求地址（必填项）
# sidebar_title: 侧边栏名称
# sidebar_icon: 侧边栏图标
# show_mode: 显示模式（全屏显示: fullscreen）
# uid: 网易云音乐的用户ID
# user: 网易云音乐的账号（使用账号密码登录，则自动获取对应uid，不需要填写uid）
# password: 网易云音乐的密码（使用账号密码登录，则自动获取对应uid，不需要填写uid）
# tts_before_message: tts服务前置消息（可选）
# tts_after_message: tts服务后置消息（可选）
# tts_mode: tts发音模式（默认4）【参数：1: 标准男声、2: 标准女声、3: 情感男声、4: 情感女声】
# is_voice: 语音文字识别（默认启用）启用：true，禁用：false
# is_notify: 消息通知（默认启用）启用：true，禁用：false
# is_debug: 调试日志（默认启用）启用：true，禁用：false

media_player:
  - platform: ha_cloud_music
    api_url: 'http://localhost:3000'
    sidebar_title: 云音乐
    sidebar_icon: mdi:music
    show_mode: fullscreen
    uid: 47445304
    user: 网易云账号(邮箱或手机号)
    passwowrd: 网易云密码
    tts_before_message: '主人：'
    tts_after_message: '。我是爱你的小喵'
    tts_mode: 4
    is_voice: true
    is_notify: true
    is_debug: true

```