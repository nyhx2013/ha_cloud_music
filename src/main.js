// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
// import 'babel-polyfill'
// import 'assets/js/hack'
import Vue from 'vue'
import store from './store'
import router from './router'
import App from './App'
import fastclick from 'fastclick'
import mmToast from 'base/mm-toast'
import VueLazyload from 'vue-lazyload'
import { VERSION } from './config'

import '@/assets/css/index.less'

// 优化移动端300ms点击延迟
fastclick.attach(document.body)

// 弹出层
Vue.use(mmToast)

// 懒加载
Vue.use(VueLazyload, {
  preLoad: 1,
  loading: require('assets/img/default.png')
})

// 版权信息
window.mmPlayer = window.mmplayer = `欢迎使用 mmPlayer!
当前版本为：V${VERSION}
作者：茂茂
Github：https://github.com/maomao1996/Vue-mmPlayer
歌曲来源于网易云音乐 (http://music.163.com)`
//console.info(`%c${window.mmplayer}`, `color:blue`)


// 网易云音乐插件
window.clv = {
  get hass() {
    return new Promise(async (resolve, reject) => {
      let res = await top.window.hassConnection
      if (res == null) {
        setTimeout(() => {
          Vue.prototype.$mmToast("请在Home Assistant中使用")
        }, 1500)
        reject("请在Home Assistant中使用")
        return
      }
      let conn = res.conn
      // 检测是否有除本身之外的播放器
      let mp = Object.keys(conn._ent.state).filter(key => key.indexOf('media_player') == 0 && key != 'media_player.ha_cloud_music')
      if (mp.length === 0) {
        Vue.prototype.$mmToast("检测到当前HomeAssistant没有安装媒体播放器，本功能无法使用")
        reject("检测到当前HomeAssistant没有安装媒体播放器，本功能无法使用")
        return;
      }
      // 这里拦截所有请求信息，如果ID重用，则刷新页面
      conn.socket.onmessage = function ({ data }) {
        try {
          let res = JSON.parse(data)
          if (res.success == false && res.error.code == 'id_reuse') {
            //top.location.reload()
          }
        } catch (ex) {
          console.log(data)
        }
      }
      // 查找自定义播放器
      let musicEntity = Object.keys(conn._ent.state).find(key => key.indexOf('media_player.ha_cloud_music') === 0)
      //console.log(musicEntity)
      let _clv = conn._ent.state[musicEntity]
      let o = Object.create(null)
      let attr = _clv.attributes
      if (typeof attr.media_playlist === 'string') {
        attr.playlist = JSON.parse(attr.media_playlist)
      } else {
        attr.playlist = attr.media_playlist || []
      }
      attr['index'] = attr.playlist.findIndex((ele, index) =>
        attr.source == ((index + 1) + '.' + ele.song + ' - ' + ele.singer))
      o.attr = attr
      o.id = musicEntity
      o.isReady = ['playing', 'paused'].includes(_clv.state)
      o.isPlaying = _clv.state == 'playing'
      o.state = _clv.state
      o.call = (service_data, service = 'play_media', domain = 'media_player') => {
        conn.socket.send(JSON.stringify({
          id: Date.now(),
          type: "call_service",
          domain,
          service,
          service_data
        }))
      }
      resolve(o)
    })
  },
  ready() {
    this.hass.then(({ attr, isPlaying }) => {
      try {
        let ha_card = top.document.body
          .querySelector("home-assistant")
          .shadowRoot.querySelector("home-assistant-main")
          .shadowRoot.querySelector("app-drawer-layout partial-panel-resolver ha-panel-iframe")
          .shadowRoot.querySelector("iframe");
        ha_card.style.position = 'absolute'
        let url = new URLSearchParams(location.search)
        if (url.get('show_mode') === 'fullscreen') {
          ha_card.style.top = '0'
          ha_card.style.height = '100%'
        }
      } catch (ex) {
        console.log(ex)
      }

      let list = attr.playlist
      if (list.length > 0) {
        store.dispatch('setPlaylist', { list })
        store.commit('SET_CURRENTINDEX', attr.index)
        store.commit('SET_PLAYING', isPlaying)
      }
    })
  },
  exec(args) {
    Vue.loading()
    this.hass.then(({ call, id }) => {
      let media_args = {
        entity_id: id
      }
      let media_action = 'play_media'
      if (args.cmd == 'prev') {
        media_action = 'media_previous_track'
      } else if (args.cmd == 'next') {
        media_action = 'media_next_track'
      } else if (args.cmd == 'index') {
        media_args['media_content_id'] = args.index
        media_args['media_content_type'] = 'music_load'
      } else if (args.cmd == 'play') {
        media_action = 'media_play'
      } else if (args.cmd == 'pause') {
        media_action = 'media_pause'
      } else if (args.cmd == 'load') {
        media_args['media_content_id'] = JSON.stringify({
          index: args.index,
          list: args.playlist
        })
        media_args['media_content_type'] = 'music_playlist'
      } else if (args.cmd == 'volume') {
        media_action = 'volume_set'
        media_args['volume_level'] = parseFloat(args.index)
      } else if (args.cmd == 'position') {
        media_action = 'media_seek'
        media_args['seek_position'] = parseFloat(args.index)
      } else if (args.cmd == 'shuffle') {
        media_action = 'shuffle_set'
        media_args['shuffle'] = parseFloat(args.shuffle)
      }
      call(media_args, media_action, "media_player");
    })
  },
  /**
  * 防抖
  * @param {Function} fn
  * @param {Number} wait
  */
  debounce(fn, wait) {
    let _this = window.clv
    let cache = _this.debounce.prototype.cache || {}
    let fnKey = fn.toString()
    let timeout = cache[fnKey]
    if (timeout != null) clearTimeout(timeout)
    cache[fnKey] = setTimeout(() => {
      fn()
      // 清除内存占用
      if (Object.keys(cache).length === 0) {
        _this.debounce.prototype.cache = null
      } else {
        delete _this.debounce.prototype.cache[fnKey]
      }
    }, wait)
    _this.debounce.prototype.cache = cache
  },
  //设置进度
  setPosition(position) {
    this.debounce(() => {
      this.exec({
        cmd: 'position',
        index: position
      })
    }, 1000)
  },
  //设置音量
  setVolume(volume) {
    this.debounce(() => {
      this.exec({
        cmd: 'volume',
        index: volume.toFixed(1)
      })
    }, 1000)
  },
  loadlist(playList, currentIndex) {


    let pl = []
    playList.forEach((ele, index) => {
      pl.push({
        song: ele.name,
        singer: ele.singer,
        ...ele
      })
    })
    if (pl.length > 0) {
      this.exec({
        cmd: 'load',
        playlist: JSON.stringify(pl),
        index: currentIndex
      })
    }

  }
}

window.clv.ready()


import Loading from '@/base/mm-loading/mm-loading.vue'
//动态注册组件
Vue.loading = Vue.prototype.loading = function (timeout = 3) {
  let v = new Vue({
    store,
    router,
    render: h => h(Loading)
  }).$mount(document.createElement('div'))
  document.body.appendChild(v.$el)
  setTimeout(() => {
    document.body.removeChild(v.$el)
  }, timeout * 1000)
}


/* eslint-disable no-new */
new Vue({
  el: '#mmPlayer',
  store,
  router,
  render: h => h(App)
})
