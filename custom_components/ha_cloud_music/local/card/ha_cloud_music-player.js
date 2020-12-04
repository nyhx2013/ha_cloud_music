// 状态卡
class HaCloudMusicPlayer extends HTMLElement {

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
                <ha-icon class="play_mode" icon="mdi:repeat" title="播放模式"></ha-icon>
            </div>
            <div>
                <ha-icon class="prev" icon="mdi:skip-previous" title="上一曲"></ha-icon>
            </div>
            <div>
                <img title="播放/暂停" class="action" style="height:80px;width:80px;border:1px solid silver;border-radius:50%;" src="data:image/png;base64,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" />
            </div>
            <div>
                <ha-icon class="next" icon="mdi:skip-next" title="下一曲"></ha-icon>
            </div>
            <div>
                <ha-icon class="controls-list" icon="mdi:refresh" title="重新播放"></ha-icon>
            </div>
        </div>
        <!-- 音乐进度 -->
        <div class="progress">
          <div><ha-icon class="mdi-cards-heart" icon="mdi:cards-heart" title="喜欢"></ha-icon></div>
          <div class="time-position">00:00</div>
          <div>
             <input class="ha-paper-slider" type="range" min="0" max="100" value="50" style="width:200px" title="调整播放进度" />
          </div>                 
          <div class="time-length">00:00</div>
          <div><ha-icon class="icon-music-search" icon="mdi:search-web" title="音乐搜索"></ha-icon></div>
        </div>
        <ha_cloud_music-search class="hide"></ha_cloud_music-search>
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
            .hide{display:none;}
            .controls,
            .progress{ display:flex; text-align: center; align-items: center;}
            .controls>div,
            .progress>div{width:100%;}
            .red{color:red;}
            ha-icon,
            .action{
                cursor:pointer;
            }
            .controls ha-icon{--mdc-icon-size: 30px;}
            .mdi-cards-heart{
                --mdc-icon-size: 25px;
            }
            .icon-music-search{
                --mdc-icon-size: 30px;
                color: gray;
            }

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
            ha_cloud_music.toast("上一曲")
            ha_cloud_music.callMediaPlayerService("media_previous_track")
        }
        $('.next').onclick = () => {
            ha_cloud_music.toast("下一曲")
            ha_cloud_music.callMediaPlayerService("media_next_track")
        }
        $('.action').onclick = () => {
            const { state } = this.stateObj
            ha_cloud_music.toast(state == "playing" ? '暂停音乐' : '播放音乐')
            ha_cloud_music.callMediaPlayerService("media_play_pause")
        }
        $('.controls-list').onclick = () => {
            ha_cloud_music.toast("重新开始播放")
            let { source } = this.stateObj.attributes
            if (source) ha_cloud_music.callMediaPlayerService("select_source", { source })
        }
        $('.play_mode').onclick = () => {
            let icon = $('.play_mode').getAttribute('icon')
            let obj = this.playMode.find(ele => ele.icon === icon)
            let mode = obj.value
            mode = mode >= 3 ? 0 : mode + 1
            // 设置播放模式
            ha_cloud_music.callService("ha_cloud_music.config", { play_mode: mode })

            let newMode = this.playMode[mode]
            ha_cloud_music.toast(newMode.name)
            $('.play_mode').setAttribute('icon', newMode.icon)

        }

        $('.progress .ha-paper-slider').onchange = () => {
            const { media_duration } = this.stateObj.attributes
            let seek_position = Math.floor($('.progress .ha-paper-slider').value / 100 * media_duration)
            ha_cloud_music.callMediaPlayerService("media_seek", { seek_position })
            ha_cloud_music.toast(`调整音乐进度到${seek_position}秒`)
        }

        $('.mdi-cards-heart').onclick = () => {
            $('.mdi-cards-heart').classList.add('red')
            ha_cloud_music.fetchApi({ type: 'love_set' }).then((res) => {
                ha_cloud_music.toast(res.msg)
                // 通知最爱列表更新
                ha_cloud_music.onmessage('love_set')
            })
        }
        $('.icon-music-search').onclick = () => {
            $('ha_cloud_music-search').classList.toggle('hide')
        }
    }

    // 更新界面数据
    updated() {
        let { $, _stateObj } = this
        // console.log(_stateObj)
        const { state, attributes } = _stateObj
        const { entity_picture, favourite, play_mode, media_position, media_duration } = attributes
        // 封面播放图
        const action = $('.action')
        if (entity_picture) {
            action.src = entity_picture
        }
        // 如果是在播放中，则转圈圈
        if (state == "playing") {
            if (!action.classList.contains('rotate')) action.classList.add('rotate')
        } else {
            action.classList.remove('rotate')
        }
        // 判断是否红心
        const classList = $('.mdi-cards-heart').classList
        const isFavourite = classList.contains('red')
        if (favourite) {
            if (!isFavourite) classList.add('red')
        } else {
            if (isFavourite) classList.remove('red')
        }
        // 设备模式
        let mode = this.playMode.find(ele => ele.name == play_mode)
        if (mode) {
            $('.play_mode').setAttribute('icon', mode.icon)
        }
        $('.progress .time-position').textContent = `${this.timeForamt(media_position / 60)}:${this.timeForamt(media_position % 60)}`
        $('.progress .time-length').textContent = `${this.timeForamt(media_duration / 60)}:${this.timeForamt(media_duration % 60)}`
        if (media_position <= media_duration) {
            $('.progress .ha-paper-slider').value = media_position / media_duration * 100
        }
    }

    timeForamt(num) {
        if (isNaN(num)) return '00'
        num = Math.floor(num)
        if (num < 10) return '0' + String(num)
        return String(num)
    }
}

// 定义DOM对象元素
customElements.define('ha_cloud_music-player', HaCloudMusicPlayer);