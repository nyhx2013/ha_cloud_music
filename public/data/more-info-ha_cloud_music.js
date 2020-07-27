class MoreInfoHaCloudMusic extends HTMLElement {

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

    throttle(callback, time) {
        let timer = null
        return () => {
            if (timer) clearTimeout(timer)
            timer = setTimeout(() => {
                callback()
                timer = null
            }, time)
        }
    }

    // 创建界面
    created(hass) {
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'more-info-ha_cloud_music'
        ha_card.innerHTML = `
        <div class="voice-panel hide">      
            <div id="inputPanel">
                <ha-icon class="input-mode" icon="mdi:microphone"></ha-icon>
                <input type="text" placeholder="请使用手机语音输入法" autofocus id="txtInput" />
                <ha-icon class="menu-open" icon="mdi:menu-open"></ha-icon>
            </div>
            <div class="list">
                <div class="left content">
                    <button>😁</button>
                    <div><span>
                    播放音乐、暂停音乐、下一曲、<br/>
                    上一曲、小点声音、大点声音
                    </span></div>
                </div>
                <div class="right content">
                    <div><span>播放新闻</span></div>
                    <button data-cmd="播放新闻">😘</button>
                </div>
                <div class="left content">
                    <button>😁</button>
                    <div><span>新闻音频资源来自😋乐听头条</span></div>
                </div>
                <div class="right content">
                    <div><span>我想听林俊杰的歌</span></div>
                    <button data-cmd="我想听林俊杰的歌">😘</button>
                </div>
                <div class="left content">
                    <button>😁</button>
                    <div><span>林俊杰👌歌手都来自网易云音乐</span></div>
                </div>
                <div class="right content">
                    <div><span>播放歌曲明天你好</span></div>
                    <button data-cmd="播放歌曲明天你好">😘</button>
                </div>
                <div class="left content">
                    <button>😁</button>
                    <div><span>明天你好😍歌曲来自网易云音乐</span></div>
                </div>
                <div class="right content">
                    <div><span>播放专辑段子来了</span></div>
                    <button data-cmd="播放专辑段子来了">😘</button>
                </div>
                <div class="left content">
                    <button>😁</button>
                    <div><span>段子来了😄来自喜马拉雅哦</span></div>
                </div>
                <div class="right content">
                    <div><span>播放电台宋宇的报刊选读</span></div>
                    <button data-cmd="播放电台宋宇的报刊选读">😘</button>
                </div>                
                <div class="left content">
                    <button>😁</button>
                    <div><span>宋宇的报刊选读😜来自网易云音乐哦</span></div>
                </div>
                <div class="right content">
                    <div><span>播放歌单私人雷达</span></div>
                    <button data-cmd="播放歌单私人雷达">😘</button>
                </div>     
                <div class="left content">
                    <button>😁</button>
                    <div><span>私人雷达😊来自网易云音乐哦</span></div>
                </div>
            </div>
        </div>
        <div class="music-panel">
            <!-- 音量控制 -->
            <div class="volume">
                <div>
                    <ha-icon class="volume-off" icon="mdi:volume-high"></ha-icon>
                </div>
                <div>
                    <ha-paper-slider min="0" max="100" />
                </div>                
                <div>
                    <ha-icon class="menu" icon="mdi:menu"></ha-icon>
                </div>
            </div>
                        
            <!-- 源播放器 -->
            <div class="source">
                <ha-paper-dropdown-menu label-float="" label="源播放器">
                    <paper-listbox slot="dropdown-content">
                    </paper-listbox>
                </ha-paper-dropdown-menu>
            </div>
            <!-- 音乐列表 -->
            <div class="music-list-panel">
                <ul>
                </ul>
            </div>
        </div>
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
         .voice-panel{}
         .music-panel{}
         .hide{display:none;}
         
         .volume{display:flex;align-items: center;text-align:center;}
         .volume div:nth-child(1),
         .volume div:nth-child(3){cursor:pointer;}
         .volume div:nth-child(2){width:100%;}
         .volume ha-paper-slider{width:100%;}
         
         .source ha-paper-dropdown-menu{width:100%;}
         
         .music-list-panel{}
         .music-list-panel ul{margin:0;padding:10px 0;list-style:none;}
         .music-list-panel ul li{padding:10px 0;display:flex;    align-items: center;}
         .music-list-panel ul li span{width:100%;display:block;}
         .music-list-panel ul li.active{color: var(--primary-color);}
         .music-list-panel ul li:last-child{display:flex;}
         .music-list-panel ul li:last-child button{flex:1;padding:10px 0;border:none;color:white;background-color:var(--primary-color);}
        
         #inputPanel{display:flex;align-items: center;text-align:center;}
         #txtInput {
            border-radius: 10px;
            outline: none;
            width:100%;
            box-sizing: border-box;
            padding: 8px 10px;
            border: 1px solid silver;
            margin: 0 10px;
        }

        .content {
            padding: 10px 0;
            display: flex;
            overflow: auto;
        }

        .content div {
            flex: 1;
        }

        .content span {
            display: inline-block;
            padding: 5px 10px 8px 10px;
        }

        .content button {
            border: none;
            font-size: 30px;
            outline: none;
            width: 55px;
            background-color: transparent;
        }

        .right {
            text-align: right;
        }

        .right span {
            background-color: purple;
            color: white;
            border-radius: 10px 10px 0px 10px;
            text-align: left;
        }

        .right button {
            float: right;

        }

        .left button {
            float: left;
        }

        .left {
            text-align: left;
        }

        .left span {
            background-color: white;
            border-radius: 10px 10px 10px 0px;
        }
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true
        /* ***************** 附加代码 ***************** */
        this.icon = {
            volume_high: 'mdi:volume-high',
            volume_off: 'mdi:volume-off',
        }
        let { $ } = this
        let _this = this
        // 静音        
        $('.volume-off').onclick = function () {
            // 是否静音
            let is_volume_muted = this.icon === _this.icon.volume_high

            _this.callService('media_player.volume_mute', {
                entity_id: _this.stateObj.entity_id,
                is_volume_muted
            })

            _this.toast(is_volume_muted ? "静音" : '启用音量')
            this.setAttribute('icon', is_volume_muted ? _this.icon.volume_off : _this.icon.volume_high)
        }
        // 调整音量
        $('.volume ha-paper-slider').onchange = function () {
            let volume_level = this.value / 100
            _this.callService('media_player.volume_set', {
                entity_id: _this.stateObj.entity_id,
                volume_level: volume_level
            })
            _this.toast(`调整音量到${this.value}`)
        }
        // 显示语音控制界面
        let inputMode = $('.input-mode')
        inputMode.onclick = () => {
            let isText = inputMode.icon == 'mdi:card-text'
            let icon = isText ? 'mdi:microphone' : 'mdi:card-text'
            inputMode.icon = icon
            this.toast(isText ? '切换到语音模式，自动发送文本' : '切换到文本模式')
        }
        $('.menu').onclick = () => {
            $('.music-panel').classList.add('hide')
            $('.voice-panel').classList.remove('hide')
        }
        $('.menu-open').onclick = () => {
            $('.voice-panel').classList.add('hide')
            $('.music-panel').classList.remove('hide')
        }
        // 选择源播放器
        $('.source paper-listbox').addEventListener('selected-changed', function () {
            let { entity_id, attributes } = _this._stateObj
            let sound_mode_list = attributes.sound_mode_list
            let sound_mode = sound_mode_list[this.selected]
            // 选择源播放器
            if (attributes.sound_mode != sound_mode) {
                _this.callService('media_player.select_sound_mode', {
                    entity_id,
                    sound_mode
                })
                _this.toast(`更换源播放器：${sound_mode}`)
            }
        })
        // 语音输入
        this.addMsg = (value) => {
            let div = document.createElement('div')
            div.className = `right content`
            div.innerHTML = `<div><span>${value}</span></div><button data-cmd="${value}">😘</button>`
            $(".list").insertBefore(div, $('.list>div'))

            this._hass.callApi('POST', 'events/ha_voice_text_event', { text: value }).then(res => {
                this.toast("命令发送成功")
            })
        }

        let txtInput = $('#txtInput')
        txtInput.oninput = this.throttle(() => {
            // 如果是文本模式，则不处理
            let isText = inputMode.icon == 'mdi:card-text'
            if (isText) return;

            let value = txtInput.value.trim()
            if (value) {
                txtInput.value = ''
                this.addMsg(value)
            }
        }, 1000)
        txtInput.onkeypress = (event) => {
            if (event.keyCode == 13) {
                let value = txtInput.value.trim()
                if (value) {
                    txtInput.value = ''
                    this.addMsg(value)
                }
            }
        }
        // 命令点击
        $('.list').addEventListener('click', (event) => {
            let ele = event.path[0]
            if ('cmd' in ele.dataset) {
                let text = ele.dataset['cmd']
                this._hass.callApi('POST', 'events/ha_voice_text_event', { text }).then(res => {
                    this.toast("命令发送成功")
                })
            }
        })
    }

    // 更新界面数据
    updated(hass) {
        let { $, _stateObj } = this
        let attr = _stateObj.attributes
        let entity_id = _stateObj.entity_id
        let sound_mode_list = attr.sound_mode_list
        let source_list = attr.source_list
        // 音量
        $('.volume .volume-off').setAttribute('icon', attr.is_volume_muted ? this.icon.volume_off : this.icon.volume_high)
        $('.volume ha-paper-slider').value = attr.volume_level * 100
            // 源播放器
            ; (() => {
                if (sound_mode_list) {
                    // 判断当前是否需要更新DOM
                    let items = $('.source').querySelectorAll('paper-item')
                    if (items && items.length == sound_mode_list.length) return;
                    // 生成节点
                    let listbox = $('.source paper-listbox')
                    listbox.innerHTML = sound_mode_list.map((ele) => {
                        return `<paper-item>${ele}</paper-item>`
                    }).join('')
                    // 选择当前默认项
                    let sound_mode_index = sound_mode_list.indexOf(attr.sound_mode)
                    listbox.selected = sound_mode_index
                }
            })();
        // 音乐列表
        if (source_list && source_list.length > 0) {
            let ul = $('.music-list-panel ul')
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
                        this.callService('media_player.select_source', {
                            entity_id,
                            source: ele
                        })
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
                    let playIndex = count - 50 + 1
                    this.toast(`播放第${playIndex}项音乐`)
                    this.callService('ha_cloud_music.load', {id, type, index: playIndex})
                }
                let btn2 = document.createElement('button')
                btn2.innerHTML = '播放下一页'
                btn2.onclick = () => {
                    let playIndex = count + 50 + 1
                    this.toast(`播放第${playIndex}项音乐`)
                    this.callService('ha_cloud_music.load', {id, type, index: playIndex})
                }
                if (index > 0) li.appendChild(btn1)
                if (count < total - 50) li.appendChild(btn2)
                fragment.appendChild(li)
            }
            ul.appendChild(fragment)
        }
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
            this.callService("media_player.media_previous_track", { entity_id: this._stateObj.entity_id })
        }
        $('.next').onclick = () => {
            this.toast("下一曲")
            this.callService("media_player.media_next_track", { entity_id: this._stateObj.entity_id })
        }
        $('.action').onclick = () => {
            this.toast(this._stateObj.state == "playing" ? '暂停音乐' : '播放音乐')
            this.callService("media_player.media_play_pause", { entity_id: this._stateObj.entity_id })
        }
        $('.controls-list').onclick = () => {
            this.toast("重新开始播放")
            let { source } = this.stateObj.attributes
            if (source) this.callService("media_player.select_source", { entity_id: this._stateObj.entity_id, source })
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
                entity_id: this._stateObj.entity_id,
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