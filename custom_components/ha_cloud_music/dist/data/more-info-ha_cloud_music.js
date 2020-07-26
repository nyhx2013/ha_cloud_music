class MoreInfoHaCloudMusic extends HTMLElement {
    constructor() {
        super()
        this.icon = {
            volume_high: 'mdi:volume-high',
            volume_off: 'mdi:volume-off',
        }
        const shadow = this.attachShadow({ mode: 'open' });
        const div = document.createElement('div', { 'class': 'root' });
        div.innerHTML = `               
               <!-- 音量控制 -->
               <div class="volume">
                <div>
                  <ha-icon class="volume-off" icon="mdi:volume-high"></ha-icon>
                </div>
                <div>
                    <ha-paper-slider min="0" max="100" />
                </div>
               </div>
                              
               <!-- 源播放器 -->
               <div class="source">
                 
               </div>
                                             
               <div class="mask"></div>              
                              
               <!-- 音乐列表 -->
               <div class="music-list-panel">
                 <ul>
                 </ul>
               </div>
               
               <div class="loading">
                   <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin: auto;transform: translateY(100%); display: block;" width="200px" height="200px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
                    <circle cx="28" cy="75" r="11" fill="#85a2b6">
                      <animate attributeName="fill-opacity" repeatCount="indefinite" dur="1s" values="0;1;1" keyTimes="0;0.2;1" begin="0s"></animate>
                    </circle>

                    <path d="M28 47A28 28 0 0 1 56 75" fill="none" stroke="#bbcedd" stroke-width="10">
                      <animate attributeName="stroke-opacity" repeatCount="indefinite" dur="1s" values="0;1;1" keyTimes="0;0.2;1" begin="0.1s"></animate>
                    </path>
                    <path d="M28 25A50 50 0 0 1 78 75" fill="none" stroke="#dce4eb" stroke-width="10">
                      <animate attributeName="stroke-opacity" repeatCount="indefinite" dur="1s" values="0;1;1" keyTimes="0;0.2;1" begin="0.2s"></animate>
                    </path>
                    </svg>
               </div>
               <div class="toast">
                弹窗提示
               </div>
        `
        shadow.appendChild(div);
        // 绑定事件
        const _this = this
        // 静音
        div.querySelector('.volume-off').onclick = function () {
            let icon = this.getAttribute('icon')
            let is_volume_muted = false
            if (this.icon === _this.icon.volume_high) {
                this.setAttribute('icon', _this.icon.volume_off)
                _this.toast("静音")
                is_volume_muted = true
            } else {
                this.setAttribute('icon', _this.icon.volume_high)
                _this.toast("启用音量")
                is_volume_muted = false
            }
            _this.call({
                entity_id: _this.stateObj.entity_id,
                is_volume_muted: is_volume_muted
            }, 'volume_mute')
        }
        // 调整音量
        div.querySelector('.volume ha-paper-slider').onchange = function () {
            let volume_level = this.value / 100
            _this.call({
                entity_id: _this.stateObj.entity_id,
                volume_level: volume_level
            }, 'volume_set')
            _this.toast(`调整音量到${this.value}`)
        }

        // 设置样式
        const style = document.createElement('style');
        style.textContent = `
         
         .loading{
            width: 100%;height: 100vh;position: fixed;background: rgba(0,0,0,.7);top: 0;left: 0;display:none;
            z-index:1000;
         }
         .toast{background-color:black;
            color:white;
            text-align:center;
            width:100%;
            position:fixed;
            top:0;left:0;
            z-index:1001;
            display:none;
            opacity: 0;
            padding:22px 10px;
            font-weight:bold;
            font-size:14px;
            transition: opacity 0.5s;}
         
         .source ha-paper-dropdown-menu{width:100%;}
         
         .volume{display:flex;align-items: center;}
         .volume div:nth-child(1){width:40px;text-align:center;cursor:pointer;}
         .volume div:nth-child(2){width:100%;}
         .volume ha-paper-slider{width:100%;}
         
         .music-list-panel{}
         .music-list-panel ul{margin:0;padding:10px 0;list-style:none;}
         .music-list-panel ul li{padding:10px 0;display:flex;    align-items: center;}
         .music-list-panel ul li span{width:100%;display:block;}
         .music-list-panel ul li.active{color: var(--primary-color);}
         .music-list-panel ul li:last-child{display:flex;}
         .music-list-panel ul li:last-child button{flex:1;padding:10px 0;border:none;}
         
        `;
        shadow.appendChild(style);
        this.shadow = shadow

        this.info = document.createElement('div')

    }

    showMask() {
        this.shadow.querySelector('.mask').style.display = 'block'
    }

    hideMask() {
        this.shadow.querySelector('.mask').style.display = 'none'
    }

    showLoading() {
        this.loadingTime = Date.now()
        this.shadow.querySelector('.loading').style.display = 'block'
    }

    hideLoading() {
        if (Date.now() - this.loadingTime < 1000) {
            setTimeout(() => {
                this.shadow.querySelector('.loading').style.display = 'none'
            }, 1000)
        } else {
            this.shadow.querySelector('.loading').style.display = 'none'
        }
    }

    // 提示
    toast(msg) {
        let toast = this.shadow.querySelector('.toast')
        if (toast.timer != null) {
            clearTimeout(toast.timer)
        }
        toast.innerHTML = msg
        toast.style.display = 'block'
        toast.style.opacity = '1'
        toast.timer = setTimeout(() => {
            toast.style.opacity = '0'
            toast.timer = setTimeout(() => {
                toast.style.display = 'none'
                toast.timer = null
            }, 500)
        }, 3000)
    }

    // 调用接口
    async call(data, service, domain = 'media_player') {
        this.showLoading()
        // 开始执行加载中。。。
        let auth = this.hass.auth
        let authorization = ''
        if (auth._saveTokens) {
            // 过期
            if (auth.expired) {
                await auth.refreshAccessToken()
            }
            authorization = `${auth.data.token_type} ${auth.accessToken}`
        } else {
            authorization = `Bearer ${auth.data.access_token}`
        }
        // 发送查询请求
        fetch(`/api/services/${domain}/${service}`, {
            method: 'post',
            body: JSON.stringify(data),
            headers: {
                authorization
            }
        }).then(res => res.json()).then(res => {

        }).finally(() => {
            //加载结束。。。
            this.hideLoading()
        })
    }

    timeForamt(num) {
        if (num < 10) return '0' + String(num)
        return String(num)
    }

    // 自定义初始化方法
    render() {
        const _this = this
        let attr = this.stateObj.attributes
        let state = this.stateObj.state
        let entity_id = this.stateObj.entity_id
        // console.log(attr)
        // console.log(this.stateObj.entity_id)

        this.shadow.querySelector('.volume .volume-off').setAttribute('icon', attr.is_volume_muted ? this.icon.volume_off : this.icon.volume_high)
        this.shadow.querySelector('.volume ha-paper-slider').value = attr.volume_level * 100

        /************************ 音乐列表 ***************************************/
        if (attr.source_list && attr.source_list.length > 0) {
            ; (() => {
                let ul = this.shadow.querySelector('.music-list-panel ul')
                ul.innerHTML = ''
                let fragment = document.createDocumentFragment();
                attr.source_list.forEach((ele, index) => {
                    let li = document.createElement('li')
                    if (ele === attr.source) {
                        li.className = 'active'
                        li.innerHTML = `<span>${ele}</span> <ha-icon icon="mdi:music"></ha-icon>`
                    } else {
                        let span = document.createElement('span')
                        span.textContent = ele
                        li.appendChild(span)
                        let ironIcon = document.createElement('ha-icon')
                        ironIcon.setAttribute('icon', 'mdi:play-circle-outline')
                        ironIcon.onclick = () => {
                            // 这里播放音乐
                            // console.log(index,ele)
                            this.call({
                                entity_id,
                                source: ele
                            }, 'select_source')
                            this.toast(`开始播放： ${ele}`)
                        }
                        li.appendChild(ironIcon)
                    }
                    fragment.appendChild(li)
                })
                // 如果有下一页，则显示播放下一页
                let media_playlist = attr.media_playlist
                let obj = media_playlist[0]['load']
                if (obj) {
                    // 获取相关信息
                    let { id, type, index, total } = obj
                    // 当前所有页数的数据
                    let count = index * 50

                    let li = document.createElement('li')
                    let btn1 = document.createElement('button')
                    btn1.innerHTML = '播放上一页'
                    btn1.onclick = () => {
                        this.call({
                            id,
                            type,
                            index: count - 100 + 1
                        }, 'load', 'ha_cloud_music')
                    }
                    let btn2 = document.createElement('button')
                    btn2.innerHTML = '播放下一页'
                    btn2.onclick = () => {
                        this.call({
                            id,
                            type,
                            index: count + 1
                        }, 'load', 'ha_cloud_music')
                    }

                    if (count > 50) li.appendChild(btn1)
                    if (count < total - 50) li.appendChild(btn2)
                    fragment.appendChild(li)
                }

                ul.appendChild(fragment)
            })();
        }
        /************************ 源播放器 ***************************************/
        if (attr.sound_mode_list) {
            let sound_mode_list = []
            let sound_mode = attr.sound_mode_list.indexOf(attr.sound_mode)
            // 获取当前节点数据
            let items = this.shadow.querySelectorAll('.source paper-item')
            if (items && items.length == attr.sound_mode_list.length) {
                // console.log(items)
                return
            }

            attr.sound_mode_list.forEach((ele) => {
                sound_mode_list.push(`<paper-item>${ele}</paper-item>`)
            })
            this.shadow.querySelector('.source').innerHTML = `
                <ha-paper-dropdown-menu label-float="" label="源播放器">
                    <paper-listbox slot="dropdown-content" selected="${sound_mode}">
                        ${sound_mode_list.join('')}
                    </paper-listbox>
                </ha-paper-dropdown-menu>
            `
            // 读取源播放器
            this.shadow.querySelector('.source paper-listbox').addEventListener('selected-changed', function () {
                if (sound_mode != this.selected) {
                    // console.log(this.selected)
                    // console.log('%O', this)
                    sound_mode = this.selected
                    let sound_mode_name = attr.sound_mode_list[this.selected]
                    // 选择源播放器
                    _this.call({
                        entity_id,
                        sound_mode: sound_mode_name
                    }, 'select_sound_mode')
                    _this.toast(`更换源播放器：${sound_mode_name}`)
                }
            })
        }
    }

    get stateObj() {
        return this._stateObj
    }

    set stateObj(value) {
        this._stateObj = value
        this.render()
    }
}

customElements.define('more-info-ha_cloud_music', MoreInfoHaCloudMusic);

// 状态卡
class MoreInfoStateHaCloudMusic extends HTMLElement {

    constructor() {
        super()
        // 播放模式
        this.playMode = [
            {
                name: '列表循环',
                value: 0,
                icon: 'mdi:repeat'
            },
            {
                name: '顺序播放',
                value: 1,
                icon: 'mdi:shuffle-disabled'
            },
            {
                name: '随机播放',
                value: 2,
                icon: 'mdi:shuffle'
            },
            {
                name: '单曲循环',
                value: 3,
                icon: 'mdi:repeat-once'
            }
        ]
    }

    /*
     * 触发事件
     * type: 事件名称
     * data: 事件参数
     */
    fire(type, data) {
        const event = new Event(type, {
            bubbles: true,
            cancelable: false,
            composed: true
        });
        event.detail = data;
        this.dispatchEvent(event);
    }

    /*
     * 调用服务
     * service: 服务名称(例：light.toggle)
     * service_data：服务数据(例：{ entity_id: "light.xiao_mi_deng_pao" } )
     */
    callService(service_name, service_data = {}) {
        let arr = service_name.split('.')
        let domain = arr[0]
        let service = arr[1]
        this._hass.callService(domain, service, service_data)
    }

    // 通知
    toast(message) {
        this.fire("hass-notification", { message })
    }

    /*
     * 接收HA核心对象
     */
    set hass(hass) {
        this._hass = hass
        if (!this.isCreated) {
            this.created(hass)
        }
    }

    get stateObj() {
        return this._stateObj
    }

    // 接收当前状态对象
    set stateObj(value) {
        this._stateObj = value
        // console.log(value)
        if (this.isCreated) this.updated()
    }

    // 创建界面
    created(hass) {
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'more-info-state-ha_cloud_music'
        ha_card.innerHTML = `
        <div class="controls">
            <div>
                <ha-icon class="play_mode" icon="mdi:repeat"></ha-icon>
            </div>
            <div>
                <ha-icon class="prev" icon="mdi:skip-previous"></ha-icon>
            </div>
            <div>
                <img class="action" style="height:80px;width:80px;border:1px solid silver;border-radius:50%;" />
            </div>
            <div>
                <ha-icon class="next" icon="mdi:skip-next"></ha-icon>
            </div>
            <div>
                <ha-icon class="controls-list" icon="mdi:refresh"></ha-icon>
            </div>
        </div>
        <!-- 音乐进度 -->
        <div class="progress">
          <div>00:00</div>
          <div>
             <ha-paper-slider min="0" max="100" value="50" />
          </div>                 
          <div>00:00</div>
        </div>
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
            .controls,
            .progress{ display:flex; text-align: center; align-items: center;}
            .controls>div,
            .progress>div{width:100%;}
            .controls ha-icon{--mdc-icon-size: 30px;cursor:pointer;}
            .action{cursor:pointer;}

            @keyframes rotate{
                from{ transform: rotate(0deg) }
                to{ transform: rotate(359deg) }
            }
            .rotate{
                animation: rotate 5s linear infinite;
            }
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true
        /* ***************** 附加代码 ***************** */
        let { $ } = this
        $('.prev').onclick = () => {
            this.toast("上一曲")
            this.callService("media_player.media_previous_track", { entity_id: "media_player.ha_cloud_music" })
        }
        $('.next').onclick = () => {
            this.toast("下一曲")
            this.callService("media_player.media_next_track", { entity_id: "media_player.ha_cloud_music" })
        }
        $('.action').onclick = () => {
            this.toast(this._stateObj.state == "playing" ? '暂停音乐' : '播放音乐')
            this.callService("media_player.media_play_pause", { entity_id: "media_player.ha_cloud_music" })
        }
        $('.controls-list').onclick = () => {
            this.toast("重新开始播放")
            let { source } = this.stateObj.attributes
            if (source) this.callService("media_player.select_source", { entity_id: "media_player.ha_cloud_music", source })
        }
        $('.play_mode').onclick = () => {
            let icon = $('.play_mode').getAttribute('icon')
            let obj = this.playMode.find(ele => ele.icon === icon)
            let mode = obj.value
            mode = mode >= 3 ? 0 : mode + 1
            // 设置播放模式
            this.callService("ha_cloud_music.config", { play_mode: mode })

            let newMode = this.playMode[mode]
            this.toast(newMode.name)
            $('.play_mode').setAttribute('icon', newMode.icon)

        }

        $('.progress ha-paper-slider').onchange = () => {
            let attr = this.stateObj.attributes
            let seek_position = $('.progress ha-paper-slider').value / 100 * attr.media_duration
            this.callService("media_player.media_seek", {
                entity_id: "media_player.ha_cloud_music",
                seek_position
            })
            this.toast(`调整音乐进度到${seek_position}秒`)
        }
    }

    // 更新界面数据
    updated(hass) {
        let { $, _stateObj } = this
        // console.log(_stateObj)
        let action = $('.action')
        let attrs = _stateObj.attributes
        if ('entity_picture' in attrs) {
            action.src = attrs.entity_picture
        }
        // 如果是在播放中，则转圈圈
        if (_stateObj.state == "playing") {
            if (!action.classList.contains('rotate')) action.classList.add('rotate')
        } else {
            action.classList.remove('rotate')
        }
        // 设备模式
        let mode = this.playMode.find(ele => ele.name == attrs.play_mode)
        if (mode) {
            $('.play_mode').setAttribute('icon', mode.icon)
        }

        $('.progress div:nth-child(1)').textContent = `${this.timeForamt(Math.floor(attrs.media_position / 60))}:${this.timeForamt(attrs.media_position % 60)}`
        $('.progress div:nth-child(3)').textContent = `${this.timeForamt(Math.floor(attrs.media_duration / 60))}:${this.timeForamt(attrs.media_duration % 60)}`
        if (attrs.media_position <= attrs.media_duration) {
            $('.progress ha-paper-slider').value = attrs.media_position / attrs.media_duration * 100
        }
    }

    timeForamt(num) {
        if (num < 10) return '0' + String(num)
        return String(num)
    }
}
// 定义DOM对象元素
customElements.define('more-info-state-ha_cloud_music', MoreInfoStateHaCloudMusic);