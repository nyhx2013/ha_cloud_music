class HaCloudMusicSetting extends HTMLElement {

    constructor() {
        super()
        this.created()
    }
    // 创建界面
    created() {
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'ha_cloud_music-setting'
        ha_card.innerHTML = `            
        <!-- 源播放器 -->
        <div class="source">
            <fieldset>
                <legend><a href="/ha_cloud_music-web/index.html?v=${Date.now()}" target="_blank" title="云音乐网页播放器" class="source-web-player">源播放器</a></legend>
                <select></select>
            </fieldset>
        </div>
        
        <div class="rate-source">
            <fieldset>
                <legend>播放速度</legend>
                <select>
                    <option value="1">正常</option>
                    <option value="1.2">1.2倍速</option>
                    <option value="1.3">1.3倍速</option>
                    <option value="1.4">1.4倍速</option>
                    <option value="1.5">1.5倍速</option>
                    <option value="2">2.0倍速</option>
                    <option value="2.5">2.5倍速</option>
                    <option value="3">3.0倍速</option>
                </select>
            </fieldset>
        </div>
        
        <!-- 音量控制 -->
        <div class="volume">
            <ha-icon class="volume-off" icon="mdi:volume-high"></ha-icon>
            <div>
                <input class="ha-paper-slider" type="range" min="0" max="100" />
            </div>
        </div>

        <!-- 音量控制 -->
        <div class="tts-volume">
            <ha-icon class="text-to-speech" icon="mdi:text-to-speech"></ha-icon>
            <div>
                <input class="ha-paper-slider" type="range" min="0" max="100" />
            </div>
        </div>

        <div class="tts-source">
            <fieldset>
                <legend>声音模式</legend>
                <select>
                    <option>标准男声</option>
                    <option>标准女声</option>
                    <option>情感男声</option>
                    <option>情感女声</option>
                </select>
            </fieldset>
        </div>
                    
        <!-- TTS输入 -->
        <div class="tts-input">
            <input type="text" placeholder="文字转语音" />
        </div>
        <!-- 缓存 --> 
        <button class="cache-button">缓存当前音乐到media目录</button>

        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
        .hide{display:none;}
        .ha_cloud_music-setting select{background:white;}
        .volume{margin-top:10px;}
         .volume,
         .tts-volume{display:flex;align-items: center;text-align:center;padding:10px 0;}
         .volume div,
         .tts-volume div{width:100%;}
         .volume .ha-paper-slider,
         .tts-volume .ha-paper-slider{width:100%;}
         
         .rate-source{margin-top: 10px;}
         .rate-source select,
         .tts-source select,
         .source select{width:100%; border:none;}
         .source-web-player{color:var(--primary-color);text-decoration:none;}
         
         .tts-input input{width: 100%;
            box-sizing: border-box;
            margin-top: 20px;
            border-radius: 10px;
            outline: none;
            border: 1px solid silver;
            padding: 8px 10px;}
         
         .cache-button{margin-top:20px; padding:10px; width:100%; border:none; cursor: pointer; color: white; background-color:var(--primary-color);}

        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        let { $ } = this
        const _this = this
        this.icon = {
            volume_high: 'mdi:volume-high',
            volume_off: 'mdi:volume-off',
        }

        // 静音        
        $('.volume-off').onclick = function () {
            // 是否静音
            let is_volume_muted = this.icon === _this.icon.volume_high

            ha_cloud_music.callService('media_player.volume_mute', {
                entity_id: _this.stateObj.entity_id,
                is_volume_muted
            })

            ha_cloud_music.toast(is_volume_muted ? "静音" : '启用音量')
            this.setAttribute('icon', is_volume_muted ? _this.icon.volume_off : _this.icon.volume_high)
        }
        // 调整音量
        $('.volume .ha-paper-slider').onchange = function () {
            let volume_level = this.value / 100
            ha_cloud_music.callService('media_player.volume_set', {
                entity_id: _this.stateObj.entity_id,
                volume_level: volume_level
            })
            ha_cloud_music.toast(`调整音量到${this.value}`)
        }
        // 选择源播放器
        $('.source select').addEventListener('change', function () {
            let { entity_id, attributes } = _this.stateObj
            let sound_mode = this.value
            console.log(sound_mode)
            // 选择源播放器
            if (attributes.sound_mode != sound_mode) {
                ha_cloud_music.callService('media_player.select_sound_mode', {
                    entity_id,
                    sound_mode
                })
                ha_cloud_music.toast(`更换源播放器：${sound_mode}`)
            }
        })
        // 选择倍速
        $('.rate-source select').addEventListener('change', function () {
            let { attributes } = _this.stateObj
            let media_rate = this.value
            console.log(media_rate)
            if (attributes.media_rate != media_rate) {
                ha_cloud_music.callService('ha_cloud_music.config', { media_rate: Number(media_rate) })
                ha_cloud_music.toast(`使用${media_rate}倍速播放`)
            }
        })
        // 调整语音转文字音量
        $('.tts-volume .ha-paper-slider').onchange = function () {
            ha_cloud_music.callService('ha_cloud_music.config', {
                tts_volume: this.value
            })
            ha_cloud_music.toast(`调整TTS音量到${this.value}`)
        }
        // 文字转语音
        let ttsInput = $('.tts-input input')
        ttsInput.onkeypress = (event) => {
            if (event.keyCode == 13) {
                let message = ttsInput.value.trim()
                if (message) {
                    ttsInput.value = ''
                    ha_cloud_music.callService('ha_cloud_music.tts', { message })
                }
            }
        }
        // 声音模式        
        $('.tts-source select').addEventListener('change', function () {
            const { selectedIndex } = this
            let { tts_mode } = _this.stateObj.attributes
            let selected = selectedIndex + 1
            if (tts_mode != selected) {
                ha_cloud_music.callService('ha_cloud_music.config', {
                    tts_mode: selected
                })
                ha_cloud_music.toast(`声音模式设置为${['度小宇', '度小美', '度逍遥', '度丫丫'][selectedIndex]}`)
            }
        })
        // 缓存音乐
        let loading = false
        $('.cache-button').onclick = () => {
            const { media_url, media_title, media_artist } = this.stateObj.attributes
            if (media_url) {
                if (this.validatorDownloadUrl(media_url)) {
                    if (loading) return ha_cloud_music.toast('你这样点，会把系统搞卡死')
                    loading = true
                    console.log(media_url)
                    ha_cloud_music.callService('ha_cloud_music.cache', {
                        name: `${media_title} - ${media_artist}`,
                        url: media_url
                    })
                    ha_cloud_music.toast('开始缓存音乐，请去【media/ha_cloud_music】目录查看')
                    setTimeout(() => {
                        loading = false
                    }, 3000)
                } else {
                    ha_cloud_music.toast('只支持网易云音乐的链接')
                }
            } else {
                ha_cloud_music.toast('当前播放链接有问题，不能缓存')
            }
        }
    }

    // 验证下载链接
    validatorDownloadUrl(media_url) {
        return ['isure.stream.qqmusic.qq.com', 'music.126.net', 'nf.migu.cn'].some(host => media_url.includes(host))
    }

    updated(stateObj) {
        let { $ } = this
        this.stateObj = stateObj
        let attr = stateObj.attributes
        let sound_mode_list = attr.sound_mode_list
        // 音量
        $('.volume .volume-off').setAttribute('icon', attr.is_volume_muted ? this.icon.volume_off : this.icon.volume_high)
        $('.volume .ha-paper-slider').value = attr.volume_level * 100
        // 设置TTS音量
        $('.tts-volume .ha-paper-slider').value = attr.tts_volume > 0 ? attr.tts_volume : attr.volume_level * 100
        // 音乐倍速
        const media_rate = $('.rate-source select').value
        if (media_rate != attr.media_rate) {
            console.log(media_rate, attr.media_rate)
            $('.rate-source select').value = Number(attr.media_rate)
        }
        // 显示缓存按钮
        const { media_url } = attr
        if (media_url) {
            // 支持咪咕音乐、QQ音乐、网易云音乐
            if (this.validatorDownloadUrl(media_url)) {
                $('.cache-button').classList.remove('hide')
            } else {
                $('.cache-button').classList.add('hide')
            }
        }
        // 源播放器
        ; (() => {
            if (sound_mode_list) {
                // 判断当前是否需要更新DOM
                let items = $('.source').querySelectorAll('option')
                if (items && items.length == sound_mode_list.length) return;
                // 生成节点
                let listbox = $('.source select')
                let sound_mode_list_str = sound_mode_list.map((ele) => {
                    return `<option value="${ele}">${ele}</option>`
                }).join('')
                // 其他播放器
                const states = ha_cloud_music.hass.states
                sound_mode_list_str += Object.keys(states).filter(ele => ele.indexOf('media_player') === 0 && !ele.includes('media_player.yun_yin_le')).map(key => {
                    let entity = states[key]
                    if (entity.state === "unavailable") return ''
                    return `<option value="${key}">${entity.attributes.friendly_name}</option>`
                })
                listbox.innerHTML = sound_mode_list_str
                // 选择当前默认项
                listbox.value = attr.sound_mode
                // 选择当前声音模式
                $('.tts-source select').selectedIndex = attr.tts_mode - 1
            }
        })();
    }
}
customElements.define('ha_cloud_music-setting', HaCloudMusicSetting);