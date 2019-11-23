# 一些服务

## 蓝牙扫描服务 ble.py

## 键盘监听服务 keyboard.py

### 配置文件 config.yaml

```

token: 这里配置HA的token
# 要监听蓝牙MAC地址
mac:
  - B4:C4:FC:66:A6:F0
  - B4:C4:FC:66:A6:F1
# 监听按键
key:
  # 键码
  71:
    # 短按事件
    service: light.toggle
    data:
      entity_id: light.xiaomi_philips_light
    # 长按事件
    long_service: light.toggle
    long_data:
      entity_id: light.cai_deng        
  72:
    service: light.toggle
    data:
      entity_id: light.cai_deng
      
```

## 更新记录

### 2019-11-23
- 支持长按事件