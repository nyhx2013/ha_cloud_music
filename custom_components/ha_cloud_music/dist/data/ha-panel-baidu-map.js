class HaPanelBaiduMap extends HTMLElement {
    constructor() {
        super()
        const shadow = this.attachShadow({ mode: 'open' });
        const div = document.createElement('div', { 'class': 'root' });
        div.innerHTML = `
            <app-toolbar>
            </app-toolbar>
            <div id="baidu-map"></dvi>
        `

        shadow.appendChild(div)
        // 设置样式
        const style = document.createElement('style');
        style.textContent = `
            app-header, app-toolbar {
                background-color: var(--primary-color);
                font-weight: 400;
                color: var(--text-primary-color, white);
            }
            #baidu-map{width:100%;height:calc(100vh - 64px); z-index: 0;}
        `;
        shadow.appendChild(style);
        this.shadow = shadow
    }

    ready() {
        if (window.BMap) {
            // 添加标题
            let toolbar = this.shadow.querySelector('app-toolbar')
            if (toolbar.children.length === 0) {
                // console.log(window.BMap)
                // console.log('%O',this)
                // console.log('%O',toolbar)              
                let menuButton = document.createElement('ha-menu-button')
                menuButton.hass = this.hass
                menuButton.narrow = true
                toolbar.appendChild(menuButton)

                let title = document.createElement('div')
                title.setAttribute('main-title', '')
                title.textContent = '百度地图'
                toolbar.appendChild(title)
                // 获取当前HA配置的经纬度
                let { latitude, longitude } = this.hass.config
                // 生成一个对象
                var map = new BMap.Map(this.shadow.querySelector('#baidu-map'));
                this.map = map
                //添加地图类型控件
                map.addControl(new BMap.MapTypeControl({
                    mapTypes: [
                        BMAP_NORMAL_MAP,
                        BMAP_HYBRID_MAP
                    ]
                }))
                // 启用鼠标滚轮缩放
                map.enableScrollWheelZoom();

                this.actionPanel()

                this.translate({ longitude, latitude }).then(res => {
                    // 添加圆形区域
                    let mPoint = res[0]
                    var circle = new BMap.Circle(mPoint, 100, { fillColor: "blue", strokeWeight: 1, fillOpacity: 0.3, strokeOpacity: 0.3 });
                    map.addOverlay(circle);
                    // 添加家坐标
                    this.addOverlay({ latitude: mPoint.lat, longitude: mPoint.lng, pic: 'https://api.jiluxinqing.com/api/service/cdn/home.png' }, 'zone')
                    // 中心点
                    map.centerAndZoom(mPoint, 18);
                })


                this.update()
                /*
                var top_left_control = new BMap.ScaleControl({anchor: BMAP_ANCHOR_TOP_LEFT});// 左上角，添加比例尺
                var top_left_navigation = new BMap.NavigationControl();  //左上角，添加默认缩放平移控件
                var top_right_navigation = new BMap.NavigationControl({anchor: BMAP_ANCHOR_TOP_RIGHT, type: BMAP_NAVIGATION_CONTROL_SMALL}); //右上角，仅包含平移和缩放按钮
                mp.addControl(top_left_control);        
                mp.addControl(top_left_navigation);     
                mp.addControl(top_right_navigation);    
                */
            } else {
                this.update()
            }
        }
    }

    // 设置定位
    addOverlay({ latitude, longitude, pic }, type, click) {
        let mPoint = new BMap.Point(longitude, latitude)
        let size = new BMap.Size(80, 80)
        if (type === 'zone') {
            size = new BMap.Size(32, 32)
        }

        //创建家庭图标
        var myIcon = new BMap.Icon(pic, size, {
            imageSize: size
        });
        var marker = new BMap.Marker(mPoint, { icon: myIcon });  // 创建标注        
        marker.type = type
        marker.addEventListener("click", function () {
            if (typeof click === 'function') {
                click(this)
            }
        });
        this.map.addOverlay(marker);              // 将标注添加到地图中
    }

    // 更新位置
    update() {
        let map = this.map
        // 删除所有设备
        let allOverlay = map.getOverlays();
        if (allOverlay.length > 0) {
            for (let i = 0; i < allOverlay.length - 1; i++) {
                if (allOverlay[i].type === "device") {
                    map.removeOverlay(allOverlay[i]);
                }
            }
        }

        this.debounce(async () => {
            // 这里添加设备
            let states = this.hass.states
            let keys = Object.keys(states).filter(ele => ele.indexOf('device_tracker') === 0)
            for (let key of keys) {
                let stateObj = states[key]
                let attr = stateObj.attributes
                // 如果有经纬度，并且不在家，则标记
                if ('longitude' in attr && 'latitude' in attr && stateObj.state != 'home') {
                    let pic = 'https://api.jiluxinqing.com/api/service/cdn/people.png'
                    if ('entity_picture' in attr) {
                        pic = attr.entity_picture
                    }
                    let res = await this.translate({ longitude: attr.longitude, latitude: attr.latitude })
                    let point = res[0]
                    this.addOverlay({ latitude: point.lat, longitude: point.lng, pic }, 'device', () => {
                        // this.fire("hass-notification", { message:'这是一条测试数据' });
                        this.fire('hass-more-info', { entityId: key })
                    })
                }
            }
        }, 1000)
    }

    // 坐标转换
    translate({ longitude, latitude }) {
        return new Promise((resolve, reject) => {
            var points = [new BMap.Point(longitude, latitude)]
            var convertor = new BMap.Convertor();
            convertor.translate(points, 1, 5, function (data) {
                if (data.status === 0) {
                    resolve(data.points)
                }
            })
        })
    }

    // 触发事件
    fire(type, data) {
        const event = new Event(type, {
            bubbles: true,
            cancelable: false,
            composed: true
        });
        event.detail = data;
        this.dispatchEvent(event);
    }

    // 操作面板
    actionPanel() {
        let { latitude, longitude } = this.hass.config
        // 获取所有设备
        this.deviceList = [{
            id: '',
            name: '家',
            longitude,
            latitude
        }]

        let states = this.hass.states
        let keys = Object.keys(states).filter(ele => ele.indexOf('device_tracker') === 0)
        keys.forEach(key => {
            let stateObj = states[key]
            let attr = stateObj.attributes
            if ('longitude' in attr && 'latitude' in attr) {
                this.deviceList.push({
                    id: key,
                    name: attr.friendly_name,
                    longitude: attr.longitude,
                    latitude: attr.latitude
                })
            }
        })

        const map = this.map
        // 定义一个控件类,即function
        function ZoomControl() {
            // 默认停靠位置和偏移量
            this.defaultAnchor = BMAP_ANCHOR_TOP_LEFT;
            this.defaultOffset = new BMap.Size(10, 10);
        }

        // 通过JavaScript的prototype属性继承于BMap.Control
        ZoomControl.prototype = new BMap.Control();

        // 自定义控件必须实现自己的initialize方法,并且将控件的DOM元素返回
        // 在本方法中创建个div元素作为控件的容器,并将其添加到地图容器中
        ZoomControl.prototype.initialize = (map) => {
            // 创建一个DOM元素
            var div = document.createElement("div");
            let select = document.createElement('select')
            this.deviceList.forEach(ele => {
                let option = document.createElement('option')
                option.value = ele.id
                option.text = ele.name
                select.appendChild(option)
            })
            select.onchange = () => {
                // 这里重新定位
                let { longitude, latitude } = this.deviceList[select.selectedIndex]
                this.translate({ longitude, latitude }).then(res => {
                    map.centerAndZoom(res[0], 18);
                })

            }
            // 添加文字说明
            div.appendChild(select);
            // 添加DOM元素到地图中
            map.getContainer().appendChild(div);
            // 将DOM元素返回
            return div;
        }
        // 创建控件
        var myZoomCtrl = new ZoomControl();
        // 添加到地图当中
        map.addControl(myZoomCtrl);

    }


    /**
    * 防抖
    * @param {Function} fn
    * @param {Number} wait
    */
    debounce(fn, wait) {
        let cache = this.cache || {}
        let fnKey = fn.toString()
        let timeout = cache[fnKey]
        if (timeout != null) clearTimeout(timeout)
        cache[fnKey] = setTimeout(() => {
            fn()
            // 清除内存占用
            if (Object.keys(cache).length === 0) {
                this.cache = null
            } else {
                delete this.cache[fnKey]
            }
        }, wait)
        this.cache = cache
    }


    loadScript(src) {
        return new Promise((resolve, reject) => {
            let id = btoa(src)
            let ele = document.getElementById(id)
            if (ele) {
                resolve()
                return
            }
            let script = document.createElement('script')
            script.id = id
            script.src = src
            script.onload = function () {
                resolve()
            }
            document.querySelector('head').appendChild(script)
        })
    }



    get panel() {
        return this._panel
    }

    set panel(value) {
        this._panel = value
        let ak = value.config.ak
        if (ak) {
            if (ak === 'ha_cloud_music') { ak = 'hNT4WeW0AGvh2GuzuO92OfM6hCW25HhX' }
            this.loadScript(`https://api.map.baidu.com/getscript?v=3.0&ak=${ak}`).then(res => {
                this.ready()
            })
        } else {
            alert('请配置百度AK')
        }
    }
}

customElements.define('ha-panel-baidu-map', HaPanelBaiduMap);