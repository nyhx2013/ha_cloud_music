/* eslint-disable */

import Vue from 'vue'
import store from '../store/index'
import { setVolume } from '@/utils/storage'

// 音频对象
let audio = {
    volume: 0,
    currentTime: 0,
    media_position: 0
}

export default class {
    constructor() {
        this.loading = false
        this.isReady = false
        this.ready()
    }

    static get isSupport() {
        return !!top.document.querySelector('home-assistant')
    }

    get hass() {
        return top.document.querySelector('home-assistant').hass
    }

    get entity_id() {
        return 'media_player.yun_yin_le'
    }

    // 实体
    get entity() {
        return this.hass.states[this.entity_id]
    }

    // 实体属性
    get attributes() {
        return this.entity.attributes
    }

    // 当前播放索引
    get index() {
        const { media_playlist, source } = this.attributes
        const playlist = media_playlist || []
        return playlist.findIndex((ele, index) => source == ((index + 1) + '.' + ele.song + ' - ' + ele.singer))
    }

    // 请求接口
    fetchApi(url, data) {
        const loading = Vue.loading()
        this.loading = true
        return this.hass.fetchWithAuth(url, {
            method: 'POST',
            body: JSON.stringify(data)
        }).then(res => res.json()).finally(() => {
            this.loading = false
            loading.close()
        })
    }

    // 调用服务
    callService(service, data) {
        const arr = service.split('.')
        return this.fetchApi(`/api/services/${arr[0]}/${arr[1]}`, data)
    }

    // 调用服务
    callMediaPlayerService(service, data) {
        return this.callService(`media_player.${service}`, {
            entity_id: this.entity_id,
            ...data
        })
    }

    ready() {
        // 获取播放器的状态与属性
        const { state, attributes } = this.entity
        const isReady = ['playing', 'paused'].includes(state)
        this.isReady = isReady
        const playlist = attributes.media_playlist || []
        // 设置音量
        setVolume(attributes.volume_level)
        // 根据HA播放器，设置对应的状态
        const { index } = this
        if (index >= 0) store.commit('SET_CURRENTINDEX', index)
        store.commit('SET_PLAYING', isReady)
        // 根据HA播放器，设置对应的播放模式（0、1、2、3）
        store.commit('SET_PLAYMODE', this.playMode[attributes.play_mode] || 0)
        // 设置列表
        store.dispatch('setPlaylist', { list: playlist })
        console.log(`播放状态：${isReady}, 模式：${attributes.play_mode}，索引：${index}`)
        // 显示模式
        this.showMode()
        // 开始执行定时更新
        this.update()
    }

    showMode() {
        // 设置全屏模式
        try {
            let haPanelIframe = top.document.body
                .querySelector("home-assistant")
                .shadowRoot.querySelector("home-assistant-main")
                .shadowRoot.querySelector("app-drawer-layout partial-panel-resolver ha-panel-iframe").shadowRoot
            let ha_card = haPanelIframe.querySelector("iframe");
            ha_card.style.position = 'absolute'
            if (this.query('show_mode') === 'fullscreen') {
                haPanelIframe.querySelector('app-toolbar').style.display = 'none'
                ha_card.style.top = '0'
                ha_card.style.height = '100%'
            }
        } catch (ex) {
            this.log(ex)
        }
    }

    /**
     * 当前播放源
     */
    get src() {
        return audio.src
    }
    set src(value) {
        if (value === audio.src) {
            return
        }
        audio.currentTime = 0
        audio.src = value
        store.commit('SET_PLAYING', true)
        /**
         * 如果当前播放的歌曲，和HA播放器里一致，则不进行操作
         */
        let { currentIndex, playlist } = store.state

        if (playlist.length > 0) {
            // 格式化当前播放列表
            const list = []
            playlist.forEach((ele, index) => {
                list.push({
                    song: ele.name,
                    ...ele
                })
            })
            //播放歌单
            const { media_title, media_artist } = this.attributes
            // 获取当前播放的音乐
            let { song, singer } = list[currentIndex]
            // 如果歌名、歌手、当前索引不一样，则播放
            if (song != media_title || singer != media_artist || this.index != currentIndex) {
                this.fetchApi('/ha_cloud_music-api', {
                    type: 'play_media',
                    index: currentIndex,
                    list
                })
            }
        }
    }
    /**
     * 当前进度
     */
    get currentTime() {
        return audio.currentTime
    }

    set currentTime(value) {
        this.debounce(() => {
            this.log('调整进度', value)
            this.callMediaPlayerService('media_seek', { seek_position: value }).finally(() => {
                audio.currentTime = value
            })
        }, 1000)
    }
    // 当前声音
    get volume() {
        return audio.volume
    }

    set volume(value) {
        if (Number.isNaN(value)) return
        this.debounce(() => {
            const { volume_level } = this.attributes
            this.log('调整音量：%s, HA音乐：%s', value, volume_level)
            if (volume_level != value) {
                this.callMediaPlayerService('volume_set', { volume_level: value }).finally(() => {
                    audio.volume = value
                })
            }
        }, 1000)
    }

    // 播放
    play() {
        this.callMediaPlayerService('media_play').finally(() => {
            // 触发播放事件
            if (typeof this.onplay === 'function') {
                this.onplay()
            }
        })
    }

    // 暂停
    pause() {
        this.callMediaPlayerService('media_pause')
    }

    // 设置播放模式
    get playMode() {
        return {
            '列表循环': 0,
            '顺序播放': 1,
            '随机播放': 2,
            '单曲循环': 3
        }
    }

    set playMode(mode) {
        let arr = Object.entries(this.playMode)
        let obj = arr.find(ele => ele[1] === mode)
        Vue.prototype.$mmToast(obj[0])
        this.callService('ha_cloud_music.config', {
            play_mode: mode
        })
    }

    // 定时更新
    update() {
        setInterval(async () => {
            // 操作中的时候，不执行更新操作
            if (this.loading === false) {
                const { state, attributes } = this.entity
                const isPlaying = state == 'playing'
                let { media_position, play_mode, media_title, media_artist, volume_level } = attributes
                const PLAYMODE = this.playMode[play_mode] || 0
                // 设置音量
                audio.volume = volume_level

                if (isPlaying) {
                    if (audio.media_position !== media_position) {
                        this.log('【校准进度】当前进度：%s HA进度：%s 上一次更新进度：%s', audio.currentTime, media_position, audio.media_position)
                        audio.currentTime = audio.media_position = media_position
                    } else {
                        audio.currentTime += 1
                    }
                }
                store.commit('SET_PLAYING', isPlaying)
                const { index } = this
                if (this.isEqual({ media_title, media_artist, index }) === false) {
                    store.commit('SET_PLAYMODE', PLAYMODE)
                    if (index >= 0) store.commit('SET_CURRENTINDEX', index)
                }
            }
            // 更新进度条
            if (typeof this.ontimeupdate === 'function') {
                this.ontimeupdate()
            }
        }, 1000)
    }


    /* ******************************自定义服务****************************** */
    log() {
        // console.log(...arguments)
    }

    // 判断当前播放音乐，是否与HA一致
    isEqual({ media_title, media_artist, index }) {
        let { currentIndex, playlist } = store.state
        let { name, singer } = playlist[currentIndex]
        if (name != media_title || singer != media_artist || index != currentIndex) {
            return false
        }
        return true
    }

    query(name) {
        let url = new URLSearchParams(location.search)
        return url.get(name)
    }

    /**
    * 防抖
    * @param {Function} fn
    * @param {Number} wait
    */
    debounce(fn, wait) {
        let cache = this.debounce.prototype.cache || {}
        let fnKey = fn.toString()
        let timeout = cache[fnKey]
        if (timeout != null) clearTimeout(timeout)
        cache[fnKey] = setTimeout(() => {
            fn()
            // 清除内存占用
            if (Object.keys(cache).length === 0) {
                this.debounce.prototype.cache = null
            } else {
                delete this.debounce.prototype.cache[fnKey]
            }
        }, wait)
        this.debounce.prototype.cache = cache
    }
}