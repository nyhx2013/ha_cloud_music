class MoreInfoHaCloudMusic extends HTMLElement {
    constructor() {
        super()
        this.icon = {
            play: 'mdi:play-circle-outline',
            pause: 'mdi:pause-circle-outline',
            shuffle_disabled: 'mdi:shuffle-disabled', //列表播放
            repeat: 'mdi:repeat', //列表循环
            repeat_once: 'mdi:repeat-once', //单曲循环
            shuffle: 'mdi:shuffle', //随机播放
            volume_high: 'mdi:volume-high',
            volume_off: 'mdi:volume-off',
        }
        // 播放模式
        this.playMode = [
            {
                name: '列表循环',
                value: 0,
                icon: this.icon.repeat
            },
            {
                name: '顺序播放',
                value: 1,
                icon: this.icon.shuffle_disabled
            },
            {
                name: '随机播放',
                value: 2,
                icon: this.icon.shuffle
            },
            {
                name: '单曲循环',
                value: 3,
                icon: this.icon.repeat_once
            }
        ]
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
               
               <!-- 音乐面板 -->
               <div class="music-panel">
                 <div class="music-lyric">
                    暂无歌词
                    <br/>
                    这个不重要，有时间再开发
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
               
               <!-- 音乐控制 -->
               <div class="controls">
                   <div>
                    <ha-icon class="play_mode" icon="mdi:repeat"></ha-icon>
                   </div>
                   <div>
                   <ha-icon class="prev" icon="mdi:skip-previous-outline"></ha-icon>
                   </div>
                   <div>
                   <ha-icon class="action" icon="mdi:play-circle-outline"></ha-icon>
                   </div>
                   <div>
                   <ha-icon class="next" icon="mdi:skip-next-outline"></ha-icon>
                   </div>
                   <div>
                   <ha-icon class="controls-list" icon="mdi:playlist-music-outline"></ha-icon>
                   </div>
               </div>
               
               <div class="mask"></div>              
                              
               <!-- 音乐列表 -->
               <div class="music-list-panel">
                 <div class="music-list-panel-title">
                    <div class="list-play-mode">
                    </div>
                    <div>
                        <ha-icon class="close-panel" icon="mdi:close"></ha-icon>
                    </div>
                 </div>
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
        div.querySelector('.action').onclick = function () {
            let icon = this.getAttribute('icon')
            if (icon === _this.icon.play) {
                this.setAttribute('icon', _this.icon.pause)
                // 调用播放服务
                _this.call({ entity_id: _this.stateObj.entity_id }, 'media_play')
                _this.toast("播放音乐")
            } else {
                this.setAttribute('icon', _this.icon.play)
                // 调用暂停服务
                _this.call({ entity_id: _this.stateObj.entity_id }, 'media_pause')
                _this.toast("暂停音乐")
            }
        }
        // 设置播放模式
        div.querySelector('.play_mode').onclick = function () {
            let icon = this.getAttribute('icon')
            let obj = _this.playMode.find(ele => ele.icon === icon)
            let mode = obj.value
            mode = mode >= 3 ? 0 : mode + 1
            // 设置播放模式
            _this.call({ play_mode: mode }, 'config', 'ha_cloud_music')
            this.setAttribute('icon', _this.playMode[mode].icon)
            _this.toast(_this.playMode[mode].name)
        }
        div.querySelector('.prev').onclick = function () {
            // 上一曲
            _this.call({ entity_id: _this.stateObj.entity_id }, 'media_previous_track')
            _this.toast("播放上一首")
        }
        div.querySelector('.next').onclick = function () {
            // 下一曲
            _this.call({ entity_id: _this.stateObj.entity_id }, 'media_next_track')
            _this.toast("播放下一首")
        }
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
        // 调整进度
        div.querySelector('.progress ha-paper-slider').onchange = function () {
            let attr = _this.stateObj.attributes
            let seek_position = this.value / 100 * attr.media_duration

            _this.call({
                entity_id: _this.stateObj.entity_id,
                seek_position: seek_position
            }, 'media_seek')

            _this.toast(`调整音乐进度到${seek_position}秒`)
        }
        // 显示音乐列表
        div.querySelector('.controls-list').onclick = () => {
            this.showMask()
            div.querySelector('.music-list-panel').style.display = 'block'
        }
        // 隐藏音乐列表
        div.querySelector('.close-panel').onclick = () => {
            div.querySelector('.music-list-panel').style.display = 'none'
            this.hideMask()
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
         
         .progress{display:flex;align-items: center;}
         .progress div{width:40px;}
         .progress div:nth-child(2){width:100%;}
         .progress ha-paper-slider{width:100%;}
            
         .controls{display:flex;text-align:center;align-items: center;}
         .controls div{width:100%;}
         .controls div:nth-child(3) ha-icon{width:40px;height:40px;}
         
         .music-panel{background-size:cover; overflow:auto;}
         .music-panel .music-lyric{width:100%;height:100%;background:rgba(0,0,0,.7);color:white;overflow:auto;text-align:center;padding:20px 10px;
            line-height:30px;    
            box-sizing: border-box;}
            
         .music-list-panel{background:#fafafa;display:none;}
         .music-list-panel .music-list-panel-title{display:flex;border-bottom:1px solid #eee;padding:10px;align-items: flex-end;}
         .music-list-panel ul{margin:0;padding:10px 0;list-style:none;
            overflow: auto;
            height: calc(100% - 70px);
         }
         .music-list-panel ul li{padding:10px;display:flex;    align-items: center;}
         .music-list-panel ul li span{width:100%;display:block;}
         .music-list-panel ul li ha-icon{width:30px;}
         .music-list-panel ul li.active{color: var(--primary-color);}
         .music-list-panel ul li:last-child{display:flex;}
         .music-list-panel ul li:last-child button{flex:1;padding:10px 0;border:none;}
         .music-list-panel-title div{width:100%;}
         .music-list-panel-title div:nth-child(2){text-align:right;}
         
         @media (min-width: 451px){
            .music-panel{height:300px;}
            .music-list-panel{
                height:420px;
                position: absolute;
                margin-top: -424px;
                width: 320px;
            }
         }
         @media (max-width: 450px){
             .mask{width: 100%;height: 100vh;position: fixed;background: rgba(0,0,0,.5);top: 0;left: 0;display:none;}             
            .music-panel{
                height:calc(100vh - 400px);
            }
            .music-list-panel{
                position: fixed;
                width: 100%;
                bottom: 0;
                left:0;
                height: 50vh;
                border-radius: 10px 10px 0 0;
            }
         }
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
            // console.log(res)
            if (service === 'media_seek') {
                let attr = res[0].attributes
                this.shadow.querySelector('.progress ha-paper-slider').value = data.seek_position / attr.media_duration * 100
            }
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

        this.shadow.querySelector('.controls .action').setAttribute('icon', state === 'playing' ? this.icon.pause : this.icon.play)
        let playMode = this.playMode.find(ele => ele.name === attr.play_mode)
        this.shadow.querySelector('.controls .play_mode').setAttribute('icon', playMode.icon)


        this.shadow.querySelector('.volume .volume-off').setAttribute('icon', attr.is_volume_muted ? this.icon.volume_off : this.icon.volume_high)
        this.shadow.querySelector('.volume ha-paper-slider').value = attr.volume_level * 100



        if (attr['entity_picture']) {
            this.shadow.querySelector('.music-panel').style.backgroundImage = `url(${attr.entity_picture})`
        }

        /************************ 音乐列表 ***************************************/
        if (attr.source_list && attr.source_list.length > 0) {
            // 设置进度
            this.shadow.querySelector('.music-panel').style.display = 'block'
            this.shadow.querySelector('.controls').style.display = 'flex'
            this.shadow.querySelector('.progress').style.display = 'flex'
            this.shadow.querySelector('.progress div:nth-child(1)').textContent = `${this.timeForamt(Math.floor(attr.media_position / 60))}:${this.timeForamt(attr.media_position % 60)}`
            this.shadow.querySelector('.progress div:nth-child(3)').textContent = `${this.timeForamt(Math.floor(attr.media_duration / 60))}:${this.timeForamt(attr.media_duration % 60)}`
            if (attr.media_position <= attr.media_duration) {
                this.shadow.querySelector('.progress ha-paper-slider').value = attr.media_position / attr.media_duration * 100
            }
            // 显示模式与数量
            this.shadow.querySelector('.list-play-mode').innerHTML = `
                <ha-icon icon="${playMode.icon}"></ha-icon>
                ${attr.play_mode} (${attr.source_list.length})
            `
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
					let media_playlist = JSON.parse(attr.media_playlist)
					let obj = media_playlist[0]['load']
					if(obj){
						// 获取相关信息
						let {id, type, index, total} = obj
						// 当前所有页数的数据
						let count = index * 50
						
						let li = document.createElement('li')
						let btn1 = document.createElement('button')
						btn1.innerHTML = '播放上一页'
						btn1.onclick = () => {
							// console.log('上一页', media_playlist)
							this.call({
								id,
								type,
								index: count - 100 + 1
							}, 'load', 'ha_cloud_music')
						}
						let btn2 = document.createElement('button')
						btn2.innerHTML = '播放下一页'
						btn2.onclick = () => {
							// console.log('上一页', media_playlist)
							this.call({
								id,
								type,
								index: count + 1
							}, 'load', 'ha_cloud_music')
						}
						
						if(count > 50) li.appendChild(btn1)
						if(count < total - 50) li.appendChild(btn2)
						fragment.appendChild(li)	
					}
                   
                    ul.appendChild(fragment)
                })();
        } else {
            this.shadow.querySelector('.music-panel').style.display = 'none'
            this.shadow.querySelector('.controls').style.display = 'none'
            this.shadow.querySelector('.progress').style.display = 'none'
        }

        /************************ 源播放器 ***************************************/
        if (attr.sound_mode_list) {
            let sound_mode_list = []
            let sound_mode = attr.sound_mode_list.indexOf(attr.sound_mode)
            // 获取当前节点数据
            let items = this.shadow.querySelectorAll('.source paper-item')
            if(items && items.length == attr.sound_mode_list.length){                
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
                    console.log(this.selected)
                    console.log('%O', this)
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

    /* --------------------生命周期回调函数-------------------------------- */

    // 当 custom element首次被插入文档DOM时，被调用。
    connectedCallback() {

    }

    // 当 custom element从文档DOM中删除时，被调用。
    disconnectedCallback() {
        // console.log('当 custom element从文档DOM中删除时，被调用。')
    }

    // 当 custom element被移动到新的文档时，被调用。
    adoptedCallback() {
        console.log('当 custom element被移动到新的文档时，被调用。')
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