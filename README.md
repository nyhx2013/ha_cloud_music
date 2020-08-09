# 4.0系列正在测试中（不支持自定义播放器，请勿直接升级使用）

# 网易云音乐HA插件

基于第三方UI修改，配合自定义的media插件实现的后台播放功能；

> custom_components：对应的HomeAssistant自定义插件目录

> 这个前端的播放器由 [maomao1996](https://github.com/maomao1996) 开发，我只是基础上进行了修改

## 免责声明
本站音频文件来自各网站接口，本站不会修改任何音频文件

音频版权来自各网站，本站只提供数据查询服务，不提供任何音频存储和贩卖服务

本项目仅为自己测试项目，请勿用作商业用途，请勿通过本项目下载盗版歌曲资源，否则后果自负！

## 使用注意

> 4.0版本以上目前只支持指定播放器（VLC播放器、MPD播放器、网页播放器）

> 3.3版本支持所有播放器

## 如何使用

> 安装

1.使用[HACS安装](https://github.com/custom-components/hacs)

在HACS里输入：https://github.com/shaonianzhentan/ha_cloud_music 即可安装成功（类型选择Integration）

2.自定义安装

将本项目custom_components里的内容，放到HA的custom_components文件夹中

> 后台插件配置

然后在configuration.yaml中配置以下内容
```
media_player:
  - platform: ha_cloud_music
    api_url: 接口请求地址
    mpd_host: MPD播放器host（如果你有的话）

```

[完整配置文档](./docs/ "完整配置文档")

# 请一定要在HomeAssistant里使用，不然没啥用，关于界面相关，请查看原作者的项目，我要减少这个库的大小，所以把图片都删了

## License

[MIT](https://github.com/maomao1996/Vue-mmPlayer/blob/master/LICENSE)
