import qs from 'qs'
import axios from '@/utils/axios'
import { defaultLimit } from '@/config'
import { formatTopSongs } from '@/utils/song'

axios.defaults.baseURL = 'https://api.mtnhao.com'

async function proxyGet(url, data) {
  const ha = top.document.querySelector('home-assistant')
  if (!ha) {
    return axios.get(url, data)
  }
  if (data && 'params' in data) {
    url = `${url}?${qs.stringify(data.params)}`
  }
  // console.log(url)
  return ha.hass.fetchWithAuth('/ha_cloud_music-api', {
    method: 'POST',
    body: JSON.stringify({
      type: 'web',
      url
    })
  }).then(res => res.json())
}

// 排行榜列表
export function getToplistDetail() {
  return proxyGet('/toplist/detail')
}

// 推荐歌单
export function getPersonalized() {
  return proxyGet('/personalized')
}

// 歌单详情
export function getPlaylistDetail(id) {
  return new Promise((resolve, reject) => {
    proxyGet('/playlist/detail', {
      params: { id }
    })
      .then(({ playlist }) => playlist)
      .then(playlist => {
        const { trackIds, tracks } = playlist
        // 过滤完整歌单 如排行榜
        if (tracks.length === trackIds.length) {
          playlist.tracks = formatTopSongs(playlist.tracks)
          resolve(playlist)
          return
        }
        // 限制歌单详情最大 500
        const ids = trackIds
          .slice(0, 500)
          .map(v => v.id)
          .toString()
        getMusicDetail(ids).then(({ songs }) => {
          playlist.tracks = formatTopSongs(songs)
          resolve(playlist)
        })
      })
  })
}

// 搜索
export function search(keywords, page = 0, limit = defaultLimit) {
  return proxyGet('/search', {
    params: {
      offset: page * limit,
      limit: limit,
      keywords
    }
  })
}

// 热搜
export function searchHot() {
  return proxyGet('/search/hot')
}

// 获取用户歌单详情
export function getUserPlaylist(uid) {
  return proxyGet('/user/playlist', {
    params: {
      uid
    }
  })
}

// 获取歌曲详情
export function getMusicDetail(ids) {
  return proxyGet('/song/detail', {
    params: {
      ids
    }
  })
}

// 获取音乐是否可以用
export function getCheckMusic(id) {
  return proxyGet('/check/music', {
    params: {
      id
    }
  })
}

// 获取音乐地址
export function getMusicUrl(id) {
  return proxyGet('/song/url', {
    params: {
      id
    }
  })
}

// 获取歌词
export function getLyric(id) {
  const url = '/lyric'
  return proxyGet(url, {
    params: {
      id
    }
  })
}

// 获取音乐评论
export function getComment(id, page, limit = defaultLimit) {
  return proxyGet('/comment/music', {
    params: {
      offset: page * limit,
      limit: limit,
      id
    }
  })
}
