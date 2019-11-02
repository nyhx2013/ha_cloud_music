import axios from 'axios'
import { URL, defaultLimit } from '@/config'

axios.defaults.baseURL = URL

// 排行榜列表
export function getToplistDetail() {
  return axios.get('/toplist/detail')
}

// 排行榜详情
export function topList(idx) {
  return axios.get('/top/list', {
    params: {
      idx
    }
  })
}

// 推荐歌单
export function getPersonalized() {
  return axios.get('/personalized')
}

// 歌单详情
export function getPlaylistDetail(id) {
  return axios.get('/playlist/detail', {
    params: {
      id
    }
  })
}

// 搜索
export function search(keywords, page = 0, limit = defaultLimit) {
  return axios.get('/search', {
    params: {
      offset: page * limit,
      limit: limit,
      keywords
    }
  })
}

// 热搜
export function searchHot() {
  return axios.get('/search/hot')
}

// 获取用户歌单详情
export function getUserPlaylist(uid) {
  return axios.get('/user/playlist', {
    params: {
      uid
    }
  })
}

// 获取歌曲详情
export function getMusicDetail(ids) {
  return axios.get('/song/detail', {
    params: {
      ids
    }
  })
}

// 获取音乐是否可以用
export function getCheckMusic(id) {
  return axios.get('/check/music', {
    params: {
      id
    }
  })
}

// 获取音乐地址
export function getMusicUrl(id) {
  return axios.get('/song/url', {
    params: {
      id
    }
  })
}

// 获取歌词
export function getLyric(id) {
  const url = '/lyric'
  return axios.get(url, {
    params: {
      id
    }
  })
}

// 获取音乐评论
export function getComment(id, page, limit = defaultLimit) {
  return axios.get('/comment/music', {
    params: {
      offset: page * limit,
      limit: limit,
      id
    }
  })
}

// 获取分类
export function getCategories() {
  return new Promise((resolve, reject) => {
    let arr = []
    axios.get('https://rapi.qingting.fm/categories?type=channel').then(({ data }) => {
      if (data.Success == 'ok') {
        data.Data.forEach(ele => {
          arr.push({
            id: ele.id,
            name: ele.title,
            picUrl: 'https://p2.music.126.net/WEIm9ckMQ9AmN7kKDn30VQ==/109951163686912767.jpg?param=180y180'
          })
        })
        resolve(arr)
      }
    })
  })
}

//获取电台列表
export function getFmList({ id, page, size }) {
  return new Promise((resolve, reject) => {
    if (!page) page = 1
    if (!size) size = 12
    axios.get(`https://rapi.qingting.fm/categories/${id}/channels?with_total=true&page=${page}&pagesize=${size}`).then(({ data }) => {
      if (data.Success == 'ok') {
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
            clv_url: `http://lhttp.qingting.fm/live/${ele.content_id}/64k.mp3`
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


//获取视频列表
export function getVideoList() {
  return new Promise((resolve, reject) => {
    fetch('./data/tv.json')
      .then((res) => res.json())
      .then(data => {
        let obj = data
        let arr = []
        Object.keys(obj).forEach(key => {
          let name = key
          let picUrl = 'http://p4.music.126.net/3DCZrxJ4svHIobxLcg_KyQ==/109951164240032297.jpg?param=180y180'
          if (key == 'radio') return
          if (key == 'cctv') {
            name = 'CCTV'
            picUrl = 'http://p2.music.126.net/kkmHDFjiuTtNn5eCBjIROg==/109951164396161803.jpg?param=180y180'
          }
          if (key == 'local') {
            name = '本地电视台'
            picUrl = 'http://p1.music.126.net/21aO_ib-TzcdrWfSUZVqDg==/18829136627850148.jpg?param=180y180'
          }
          if (key == 'other') {
            name = '其它电视'
            picUrl = 'http://p1.music.126.net/QAjQi911eIc7EtMwIuXLww==/18755469348422762.jpg?param=180y180'
          }

          obj[key].map(item => {
            return item['name'] = item.title
          })
          arr.push({
            type: 'tv',
            album: '电视',
            name: name,
            source: obj[key],
            picUrl: picUrl
          })
        })
        resolve(arr)
      })
  })
}

//获取视频列表
export function searchVideoList({ keywords }) {
  return new Promise((resolve, reject) => {
    axios.get(`https://api.jiluxinqing.com/api/service/vipvideo/video?url=${keywords}`).then((res) => {
      let { code, data, msg } = res.data
      if (code === 0) {
        let arr = []
        if (data.type == 'movie' || data.type == 'tv') {
          data.data.forEach(ele => {
            arr.push({
              type: 'movie',
              album: '电影',
              name: ele.name,
              source: ele.source.eps,
              picUrl: 'http://p4.music.126.net/3DCZrxJ4svHIobxLcg_KyQ==/109951164240032297.jpg?param=180y180'
            })
          })
        }
        resolve(arr)
      }
    })
  })
}