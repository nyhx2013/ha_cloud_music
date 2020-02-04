/* eslint-disable */

import Vue from 'vue'
import axios from 'axios'
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
    // 操作中。。。
    this.loading = false
    this.isReady = false
    this.ver = ""
    // 初始化播放模式
    this.ready()
  }

  get hass() {
    return new Promise(async (resolve, reject) => {
      let res = await top.window.hassConnection
      if (res == null) {
        Vue.prototype.$mmToast("请在Home Assistant中使用")
        reject("请在Home Assistant中使用")
        return
      }
      // 如果过期，则刷新令牌
      if (res.auth.expired) {
        res.auth.refreshAccessToken()
      }
      let conn = res.conn
      // 检测是否有除本身之外的播放器
      let mp = Object.keys(conn._ent.state).filter(key => key.indexOf('media_player') == 0 && key != 'media_player.ha_cloud_music')
      if (mp.length === 0) {
        Vue.prototype.$mmToast("检测到当前HomeAssistant没有安装媒体播放器，本功能无法使用")
        reject("检测到当前HomeAssistant没有安装媒体播放器，本功能无法使用")
        return;
      }
      // 查找自定义播放器
      let entity_id = Object.keys(conn._ent.state).find(key => key.indexOf('media_player.ha_cloud_music') === 0)
      // 获取当前播放器对象
      let ha_cloud_music = conn._ent.state[entity_id]
      // 获取播放器的状态与属性
      let { state, attributes } = ha_cloud_music
      // 修复属性
      if (typeof attributes.media_playlist === 'string') {
        attributes.playlist = JSON.parse(attributes.media_playlist)
      } else {
        attributes.playlist = attributes.media_playlist || []
      }
      attributes['index'] = attributes.playlist.findIndex((ele, index) => attributes.source == ((index + 1) + '.' + ele.song + ' - ' + ele.singer))

      // 生成对象
      let o = Object.create(null)
      o.attr = attributes
      o.entity_id = entity_id
      o.isReady = ['playing', 'paused'].includes(state)
      o.isPlaying = state == 'playing'
      o.state = state
      o.call = (service_data, service = 'play_media', domain = 'media_player') => {
        let { hassUrl, token_type } = res.auth.data
        let accessToken = res.auth.accessToken
        axios.post(`${hassUrl}/api/services/${domain}/${service}`, service_data, {
          headers: {
            Authorization: `${token_type} ${accessToken}`
          }
        }).then(res => {
          let arr = res.data
          if (Array.isArray(arr) && arr.length === 1) {
            let { attributes } = arr[0]
            if (service === 'media_seek') {
              audio.currentTime = attributes.media_position
            }
          }
          // this.log()
        })
      }
      resolve(o)
    })
  }

  ready() {
    this.hass.then(({ attr, isReady }) => {
      // this.log(store.state.playlist)
      this.isReady = isReady
      this.log(attr)
      let { index, volume_level, playlist } = attr
      // 设置音量
      setVolume(volume_level)
      // 根据HA播放器，设置对应的状态
      store.commit('SET_CURRENTINDEX', index)
      store.commit('SET_PLAYING', isReady)
      // 根据HA播放器，设置对应的播放模式（0、1、2、3）
      store.commit('SET_PLAYMODE', this.playMode[attr.media_season] || 0)
      // 设置列表
      store.dispatch('setPlaylist', { list: playlist })
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
      // 初始化版本
      this.ver = this.query('ver')
      // 初始化用户ID
      let uid = this.query('uid')
      if (uid) {
        store.dispatch('setUid', uid)
      }
      // 开始执行定时更新
      this.update()
    })
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
      let pl = []
      playlist.forEach((ele, index) => {
        pl.push({
          song: ele.name,
          singer: ele.singer,
          ...ele
        })
      })
      //播放歌单
      this.hass.then(({ attr, call, entity_id }) => {
        // 获取当前播放的音乐
        let { song, singer } = pl[currentIndex]
        let { media_title, media_artist, index } = attr
        // 如果歌名、歌手、当前索引不一样，则播放
        if (song != media_title || singer != media_artist || index != currentIndex) {
          call({
            entity_id,
            media_content_id: JSON.stringify({
              index: currentIndex,
              list: JSON.stringify(pl)
            }),
            media_content_type: 'music_playlist'
          }, 'play_media')
        }
      })
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
      this.load().then(() => {
        this.hass.then(({ call, entity_id }) => {
          call({
            entity_id,
            seek_position: value
          }, 'media_seek')
        })
      }).finally(() => {
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
      this.load().then(() => {
        this.hass.then(({ call, entity_id, attr }) => {
          let { volume_level } = attr
          this.log('调整音量：%s, HA音乐：%s', value, volume_level)
          if (volume_level != value) {
            call({
              entity_id,
              volume_level: value
            }, 'volume_set')
          }
        })
      }).finally(() => {
        audio.volume = value
      })
    }, 1000)
  }

  // 播放
  play() {
    this.load().then(() => {
      this.hass.then(({ call, entity_id }) => {
        call({
          entity_id,
        }, 'media_play')
      }).catch(ex => {
        audio.play()
      }).finally(() => {
        // 触发播放事件
        if (typeof this.onplay === 'function') {
          this.onplay()
        }
      })
    })
  }

  // 暂停
  pause() {
    this.load().then(() => {
      this.hass.then(({ call, entity_id }) => {
        call({
          entity_id,
        }, 'media_pause')
      }).catch(ex => {
        audio.pause()
      })
    })
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
    this.load().then(() => {
      let arr = Object.entries(this.playMode)
      let obj = arr.find(ele => ele[1] === mode)
      Vue.prototype.$mmToast(obj[0])
      this.hass.then(({ call }) => {
        call({
          play_mode: mode
        }, 'config', 'ha_cloud_music')
      })
    })
  }

  load(time = 3000) {
    Vue.prototype.loading()
    if (this.load.prototype.timer) {
      clearTimeout(this.load.prototype.timer)
    }
    this.loading = true
    return new Promise((resolve) => {
      this.load.prototype.timer = setTimeout(() => {
        this.loading = false
        this.load.prototype.timer = null
      }, time)
      resolve()
    })
  }



  // 定时更新
  update() {
    setInterval(async () => {
      try {
        // 操作中的时候，不执行更新操作
        if (this.loading === false) {
          let { attr, isPlaying } = await this.hass
          let { media_position, media_season, media_title, media_artist, index, volume_level } = attr

          audio.volume = volume_level

          if (isPlaying) {
            if (audio.media_position !== media_position) {
              this.log('【校准进度】当前进度：%s HA进度：%s 上一次更新进度：%s', audio.currentTime, media_position, audio.media_position)
              audio.currentTime = audio.media_position = media_position
            } else {
              audio.currentTime += 1
            }
          }
          if (this.isEqual({ media_title, media_artist, index }) === false) {
            store.commit('SET_PLAYMODE', this.playMode[media_season] || 0)
            store.commit('SET_CURRENTINDEX', index)
          }
        }
      } catch (ex) {

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

  /**
  * 生成UUID
  *
  */
  get uuid() {
    var s = []
    var hexDigits = '0123456789abcdef'
    for (var i = 0; i < 36; i++) {
      s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1)
    }
    s[14] = '4' // bits 12-15 of the time_hi_and_version field to 0010
    s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1) // bits 6-7 of the clock_seq_hi_and_reserved to 01
    s[8] = s[13] = s[18] = s[23] = '-'

    var uuid = s.join('')
    return uuid
  }

}
