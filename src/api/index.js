import axios from 'axios'
import qs from 'qs'
import { URL, defaultLimit } from '@/config'

let query = new URLSearchParams(location.search)
const apiKey = query.get('api_key')
// 如果没有api_key，则开启调试模式
const isDebug = apiKey === null
axios.defaults.baseURL = isDebug ? URL : '/ha_cloud_music-api'
function handlerGet(url, data) {
  if (isDebug) {
    return axios.get(url, data)
  }
  if (data && 'params' in data && data['params']) {
    url = url + '?' + qs.stringify(data['params'])
  }
  return new Promise((resolve, reject) => {
    axios.post('', {
      type: 'web',
      key: apiKey,
      url
    }).then(res => {
      resolve(res)
    }).catch(ex => {
      reject(ex)
    })
  })
}

// 排行榜列表
export function getToplistDetail() {
  return handlerGet('/toplist/detail')
}

// 排行榜详情
export function topList(idx) {
  return handlerGet('/top/list', {
    params: {
      idx
    }
  })
}

// 推荐歌单
export function getPersonalized() {
  return handlerGet('/personalized')
}

// 歌单详情
export function getPlaylistDetail(id) {
  return handlerGet('/playlist/detail', {
    params: {
      id
    }
  })
}

// 电台 - 节目
export function getDjProgram(rid, offset, limit = 30) {
  return handlerGet('/dj/program', {
    params: {
      rid,
      offset,
      limit
    }
  })
}

// 搜索
export function search(keywords, page = 0, limit = defaultLimit) {
  return handlerGet('/search', {
    params: {
      offset: page * limit,
      limit: limit,
      keywords
    }
  })
}

// 热搜
export function searchHot() {
  return handlerGet('/search/hot')
}

// 获取用户歌单详情
export function getUserPlaylist(uid) {
  return handlerGet('/user/playlist', {
    params: {
      uid
    }
  })
}

// 获取歌曲详情
export function getMusicDetail(ids) {
  return handlerGet('/song/detail', {
    params: {
      ids
    }
  })
}

// 获取音乐是否可以用
export function getCheckMusic(id) {
  return handlerGet('/check/music', {
    params: {
      id
    }
  })
}

// 获取音乐地址
export function getMusicUrl(id) {
  return handlerGet('/song/url', {
    params: {
      id
    }
  })
}

// 获取歌词
export function getLyric(id) {
  const url = '/lyric'
  return handlerGet(url, {
    params: {
      id
    }
  })
}

// 获取音乐评论
export function getComment(id, page, limit = defaultLimit) {
  return handlerGet('/comment/music', {
    params: {
      offset: page * limit,
      limit: limit,
      id
    }
  })
}

/* -----------------------------蜻蜓FM------------------------------- */
// 获取分类
export function getCategories() {
  return new Promise((resolve, reject) => {
    let arr = []
    axios.get('https://rapi.qingting.fm/categories?type=channel').then(({ data }) => {
      if (data.Success === 'ok') {
        data.Data.forEach(ele => {
          arr.push({
            id: ele.id,
            name: ele.title,
            updateFrequency: '',
            picUrl: 'https://p2.music.126.net/WEIm9ckMQ9AmN7kKDn30VQ==/109951163686912767.jpg'
          })
        })
        resolve(arr)
      }
    })
  })
}

// 获取电台列表
export function getFmList({ id, page, size }) {
  return new Promise((resolve, reject) => {
    if (!page) page = 1
    if (!size) size = 12
    axios.get(`https://rapi.qingting.fm/categories/${id}/channels?with_total=true&page=${page}&pagesize=${size}`).then(({ data }) => {
      if (data.Success === 'ok') {
        let res = data.Data

        let arr = []
        res.items.forEach(ele => {
          arr.push({
            album: ele.categories[0].title,
            duration: ele.audience_count,
            id: ele.content_id,
            image: ele.cover,
            name: (ele.nowplaying && ele.nowplaying.title) || ele.title,
            singer: ele.title,
            type: 'url',
            url: `http://lhttp.qingting.fm/live/${ele.content_id}/64k.mp3`
          })
        })

        resolve({
          list: arr,
          total: res.total
        })
      }
    })
  })
}

/* -----------------------------网易电台------------------------------- */
// 获取电台
export function getFM163() {
  return new Promise((resolve, reject) => {
    let arr = [
      {
        id: 1008,
        name: '网易轻松一刻',
        updateFrequency: '',
        picUrl: 'https://p2.music.126.net/WpJ-eHT47MDiOaq27EUTzQ==/109951163959542449.jpg'
      },
      {
        id: 332398053,
        name: '报刊选读',
        updateFrequency: '',
        picUrl: 'https://p2.music.126.net/LGdz3aHX0v6ODAYroiYH6A==/3299634397415569.jpg'
      },
      {
        id: 331464058,
        name: '睡不着电台',
        updateFrequency: '',
        picUrl: 'https://p1.music.126.net/Hmikf7lu9uc6YwhseOIL2A==/109951163304402567.jpg'
      },
      {
        id: 618058,
        name: '蕊希电台',
        updateFrequency: '',
        picUrl: 'https://p2.music.126.net/JpGpHfy_DUAWeuIQHrjYbg==/1418370012865049.jpg'
      },
      {
        id: 339906053,
        name: '小北电台',
        updateFrequency: '',
        picUrl: 'http://p1.music.126.net/Jbno74p63uXXIgtafwMZcw==/109951163620386920.jpg'
      },
      {
        id: 101009,
        name: '程一电台',
        updateFrequency: '',
        picUrl: 'https://p2.music.126.net/YfsRFHpQZv2FyXK7RRHnQw==/109951163894320715.jpg'
      },
      {
        id: 349437249,
        name: '夜听',
        updateFrequency: '',
        picUrl: 'https://p2.music.126.net/x6lw6XTZhViVL5I4j_zj7A==/18568552371730335.jpg'
      },
      {
        id: 316038,
        name: '好姑娘对你说晚安',
        updateFrequency: '',
        picUrl: 'https://p2.music.126.net/MbnVK0CEGZNw4CBVW0P-fw==/6668538023616484.jpg'
      },
      {
        id: 332327052,
        name: '向北',
        updateFrequency: '',
        picUrl: 'https://p2.music.126.net/aAmcvKKcOHVQmoCqlT3E9g==/1412872444869584.jpg'
      }
    ]
    resolve(arr)
  })
}
