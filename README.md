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

## 测试环境

### 树莓派3B+
- 使用了HAChina的镜像安装，[镜像地址](https://www.hachina.io/docs/8536.html "镜像地址")
- 系统安装了vlc播放器
- HA版本：0.113.0
- 使用vlc播放器【测试通过】
- 使用MPD播放器【测试通过】
- 使用DLNA播放器【暂不支持】
- 使用Kodi播放器【暂不支持】

### Windows10
- 使用pip安装的homeassistant
- 系统安装了vlc播放器
- HA版本：0.113.0
- 使用vlc播放器【测试通过】
- 使用MPD播放器【测试通过】
- 使用DLNA播放器【暂不支持】
- 使用Kodi播放器【暂不支持】

# 请一定要在HomeAssistant里使用，不然没啥用

## 功能

- 播放器
- 快捷键操作
- 歌词滚动
- 正在播放
- 排行榜
- 歌单详情
- 搜索
- 播放历史
- 查看评论
- 同步网易云歌单

## 界面欣赏

PC端界面自我感觉还行， 就是移动端界面总觉得怪怪的，奈何审美有限，所以又去整了高仿网易云的 React 版本（如果小哥哥、小姐姐们有好看的界面，欢迎交流哈）

### HomeAssistant界面
#### 服务页面
![服务页面](./screenshots/微信截图_20191027172903.png)
#### 播放组件
![播放组件](./screenshots/微信截图_20191027173028.png)
#### 播放更多信息
![播放更多信息](./screenshots/微信截图_20191027173501.png)
#### 选择媒体插件
![选择媒体插件](./screenshots/select_mode.png)

### PC
#### 正在播放
![正在播放](./screenshots/1.jpg)
#### 排行榜
![排行榜](./screenshots/2.jpg)
#### 搜索
![搜索](./screenshots/3.jpg)
#### 我的歌单
![我的歌单](./screenshots/4.jpg)
#### 我听过的
![我听过的](./screenshots/5.jpg)
#### 歌曲评论
![歌曲评论](./screenshots/6.jpg)

### 移动端

![移动端一](./screenshots/7.jpg)
![移动端二](./screenshots/8.jpg)

## 其他说明

- 并没有全面测试，所以可能有BUG
- 如有问题请直接在 Issues 中提，或者您发现问题并有非常好的解决方案，欢迎 PR

## License

[MIT](https://github.com/maomao1996/Vue-mmPlayer/blob/master/LICENSE)
