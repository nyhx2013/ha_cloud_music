 # 蓝牙追踪HA插件

 ## 如何使用

> 安装

 将本项目【ble_tracker文件夹】复制到HA的custom_components文件夹中

> 配置

 然后在configuration.yaml中配置以下内容

```

device_tracker:
  - platform: ble_tracker

```

> 开启服务
- 1.请将ha-service文件夹复制到树莓派中（随便放哪里）
- 2.打开config.yaml文件，配置token（请在HomeAssistant里获取永久token）
- 3.配置要监听的mac地址（必须大写）
- 4.使用python3 ble.py启动服务

```

注意：开启服务前请先安装相关依赖

安装对应依赖
sudo apt-get install bluetooth libbluetooth-dev pkg-config libboost-python-dev libboost-thread-dev libglib2.0-dev python-dev

安装python插件
sudo pip install pybluez

开启扫描服务
python3 ble.py

```

## 配置内容
```

token: 这里配置HA的token
# 要监听蓝牙MAC地址（可添加多个）
mac:
  - B4:C4:FC:66:A6:F0
  - B4:C4:FC:66:A6:F1
  - B4:C4:FC:66:A6:F2
  - B4:C4:FC:66:A6:F3

```